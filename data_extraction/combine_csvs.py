import csv
import sys
from pathlib import Path
import argparse
from functools import partial

# DATA_PATH = Path('../real_data')

def main(folder_name):
    global DATA_PATH
    DATA_PATH = Path('../' + folder_name)

def combine_csvs(sla_ids_to_combine, base_name, out_name, data_path):
    first = True

    with open(data_path / out_name, 'w', newline='') as f_out:
        writer = csv.writer(f_out)

        for sla_id in sla_ids_to_combine:
            file_name = data_path / f'{base_name}{sla_id}.csv'

            with open(file_name, 'r', newline='') as f_in:
                reader = csv.reader(f_in)


                header = next(reader)

                # Write header only once
                if first:
                    writer.writerow(header)
                    first = False

                # Write the data rows
                for row in reader:
                    writer.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder_name', type=str, default='real_data', help='Only the name of the data folder')
    args, unknown = parser.parse_known_args()
    main(args.folder_name)

    # if len(sys.argv) < 3:
    base_name = 'attempt_success_prediction_final_mi_'
    out_name = 'attempt_success_prediction_final_mi.csv'
    # else:
    #     base_name = sys.argv[1]
    #     out_name = sys.argv[2]

    # list all files in the directory
    files = [file.name for file in DATA_PATH.iterdir() if file.is_file() and file.name.startswith(base_name)]
    # collect unique UUIDs
    uuids = [file.replace(base_name, '').replace('.csv', '') for file in files]

    combine_csvs(uuids, base_name, out_name, DATA_PATH)