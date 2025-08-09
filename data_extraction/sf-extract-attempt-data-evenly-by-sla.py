import csv
import os
import sys
from pathlib import Path
import uuid
import yaml
# import mysql.connector
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from multiprocessing import Pool
import snowflake.connector
import shutil
import argparse
from functools import partial
# from data_extraction.combine_csvs import DATA_PATH
# print('start of the run')
# collect data from the past X days

def main(capture_days, folder_name, sample_rate):
    global TIME_RANGE_START, TIME_RANGE_END, LIMIT, DATA_PATH, SAMPLE_RATE
    # CAPTURE_DAYS = 125
    LIMIT = int((capture_days + 1) * 24 * 60)
    now_utc = datetime.now(timezone.utc)
    start_day_utc = now_utc - timedelta(days=capture_days)

    TIME_RANGE_START = start_day_utc.strftime('%Y-%m-%d %H:%M:%S')
    TIME_RANGE_END = now_utc.strftime('%Y-%m-%d %H:%M:%S')

    DATA_PATH = Path('../'+folder_name)
    DATA_PATH.mkdir(parents=True, exist_ok=True)

    SAMPLE_RATE = int(sample_rate)


def db_connect():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        # password=os.getenv("SNOWFLAKE_PASSWORD"),  # If authenticating with password
        # authenticator="externalbrowser",  # If authenticating with SSO Browser
        authenticator='SNOWFLAKE_JWT',
        private_key_file=os.path.expanduser(os.getenv('PRIVATE_KEY_FILE')),
        private_key_file_pwd=os.getenv('PRIVATE_KEY_FILE_PWD'),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("PROD_SNOWFLAKE_DATABASE")
    )


# This function will be run in each child process
def worker(task, data_path, time_range_start, time_range_end, limit, sample_rate):
    sla_id, worker_template = task

    worker_conn = db_connect()

    with open(data_path / f'attempt_success_prediction_final_mi_{sla_id}.csv', 'w', newline='') as f:
        writer = csv.writer(f)

        # print('Working on {sla_id}...'.format(sla_id=sla_id))
        filled_query = worker_template.replace('%%scsla.id%%', str(sla_id))
        filled_query = filled_query.replace('%%da.createdAt.start%%', time_range_start)
        filled_query = filled_query.replace('%%da.createdAt.end%%', time_range_end)
        filled_query = filled_query.replace('%%da.limit%%', str(limit))
        filled_query = filled_query.replace('%%sample_rate%%', str(sample_rate))

        # print(f'Pulling {RANGE_STEP} mins for {sla_id} at {range_start}')

        cursor = None
        try:
            cursor = worker_conn.cursor()
            cursor.execute("USE DATABASE PROD_DB_V2;")
            cursor.execute("USE SCHEMA REPORTING_DATA;")
            cursor.execute(filled_query)

            writer.writerow([i[0] for i in cursor.description])

            for row in cursor.fetchall():
                writer.writerow(row)

        except Exception as e:
            print(f'Handling exception: {str(e)}')

        finally:
            # Close the cursor
            if cursor:
                cursor.close()
                first = False

    worker_conn.close()


def remove_completed_slas(slas, data_path):
    # collect downloaded files
    files = [file.name for file in data_path.iterdir() if
             file.is_file() and file.name.startswith('attempt_success_prediction_final_mi_')]

    # collect unique UUIDs
    uuids = [file.replace('attempt_success_prediction_final_mi_', '').replace('.csv', '') for file in files]

    # filter from the sla list the sla ids that match
    return [item for item in slas if item not in uuids]

def is_valid_uuid(s):
    try:
        uuid.UUID(s, version=4)
        return True
    except ValueError:
        return False

def clean_real_data(data_path):
    # Ensure folder exists
    if data_path.exists() and data_path.is_dir():
        for item in data_path.iterdir():
            if item.is_file() or item.is_symlink():
                item.unlink()  # Delete file or symlink
            elif item.is_dir():
                shutil.rmtree(item)

if __name__ == '__main__':
    # Ensure folder exists but is empty before any new extraction!!!
    parser = argparse.ArgumentParser()
    parser.add_argument('--capture_days', type=int, default=155, help='Number of days to capture')
    parser.add_argument('--folder_name', type=str, default='real_data', help='Only the name of the data folder')
    parser.add_argument('--sample_rate', type=int, default=10, help='Maximum number of samples to capture for each sla per minute')
    args, unknown = parser.parse_known_args()

    main(args.capture_days, args.folder_name, args.sample_rate)

    print("THE PATH IS {}".format(DATA_PATH))
    clean_real_data(DATA_PATH)

    with open(DATA_PATH / 'capture_metadata.yaml', 'w', newline='') as metadata_file:
        metadata = {
            'time_range_start': TIME_RANGE_START,
            'time_range_end': TIME_RANGE_END
        }

        yaml.dump(metadata, metadata_file, default_flow_style=False)

    load_dotenv()

    # Fetch all SLA IDs
    conn = db_connect()
    script_dir = Path(__file__).resolve().parent
    query_path = script_dir / 'helper_sql' / 'aspm-sf-get-sla-ids.sql'

    # with open('helper_sql/pp-sf-get-sla-ids.sql', 'r') as get_sla_file:
    with open(query_path, 'r') as get_sla_file:
        query = get_sla_file.read()
        query = query.replace('%%da.createdAt.start%%', TIME_RANGE_START)
        query = query.replace('%%da.createdAt.end%%', TIME_RANGE_END)

    cursor = conn.cursor()
    cursor.execute("USE DATABASE PROD_DB_V2;")
    cursor.execute("USE SCHEMA CURATED_DATA;")
    cursor.execute("SELECT CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA();")
    print(cursor.fetchone())

    get_sla_id_cursor = conn.cursor()
    get_sla_id_cursor.execute(query)
    sla_ids = [row[0] for row in get_sla_id_cursor.fetchall()]
    get_sla_id_cursor.close()
    conn.close()

    script_dir = Path(__file__).resolve().parent
    query_path = script_dir / 'helper_sql' / 'aspm-sf-data-template.sql'
    # Read SQL template
    # with open('helper_sql/pp-sf-data-template.sql', 'r') as template_file:
    with open(query_path, 'r') as template_file:
        template = template_file.read()

    # if len(sys.argv) > 1:
    #     arg = sys.argv[1]
    #
    #     if arg == 'diff':
    #         print('Performing differential pull')
    #         # remove any SLAs that we have files for already
    #         sla_ids = remove_completed_slas(sla_ids, DATA_PATH)
    #     elif is_valid_uuid(arg):
    #         worker((arg, template))
    #         exit(0)
    #     else:
    #         print(f'Invalid argument {arg}')

    # Prepare tasks
    tasks = [(sla_id, template) for sla_id in sla_ids]

    # Run the tasks in parallel using multiprocessing
    MAX_TASKS = 100
    partial_worker = partial(worker,
                             data_path=DATA_PATH,
                             time_range_start=TIME_RANGE_START,
                             time_range_end=TIME_RANGE_END,
                             limit=LIMIT, sample_rate=SAMPLE_RATE)

    with Pool(MAX_TASKS) as pool:
        pool.map(partial_worker, tasks)

    print('completed the execution')