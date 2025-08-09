from ds_shared.tzutil import get_timezone_at
from ds_shared.service_level import lp_sla_time_in_minutes
import datetime


def calculate_sla_due_by(row):
    if row['serviceLevel'] == 'Same Day':
        # Find the local timezone for the given lat and lon
        local_timezone = get_timezone_at(row['fromLat'], row['fromLon'])

        # Convert deliveryStarted to local time
        local_time = row['deliveryStartedAt'].tz_convert(local_timezone)

        # Calculate midnight on that day in local time
        midnight = local_time.replace(hour=0, minute=0, second=0, microsecond=0)

        # Add 'endOfDay' minutes to it
        sla_due_by = midnight + datetime.timedelta(minutes=row['endOfDay'])

        # Convert back to UTC before returning
        return sla_due_by.tz_convert('UTC')
    else:
        return row['deliveryStartedAt'] + datetime.timedelta(minutes=row['dropOffMinutes'])


def calculate_same_day_miss(row):
    # Find the local timezone for the given lat and lon
    local_timezone = get_timezone_at(row['fromLat'], row['fromLon'])

    # Convert deliveryStarted to local time
    started_at_local_time = row['deliveryStartedAt'].tz_convert(local_timezone)
    completed_at_local_time = row['deliveryCompletedAt'] .tz_convert(local_timezone)

    return True if started_at_local_time.date() != completed_at_local_time.date() else False


def create_sla_columns(df):
    df['slaDueBy'] = df.apply(calculate_sla_due_by, axis=1)

    # now create our binary label
    df['late'] = df['deliveryCompletedAt'] > df['slaDueBy']
    df['onTime'] = ~df['late']
    df['late'] = df['late'].astype(int)
    df['onTime'] = df['onTime'].astype(int)

    df['sameDayMiss'] = df.apply(calculate_same_day_miss, axis=1)

    return df


def create_attempt_columns(df):
    # add the time remaining in the SLA at the start time of the attempt that delivered the package
    df['slaTimeRemainingAtLastAttempt'] = df['slaDueBy'] - df['finalAttemptStartedAt']
    df['slaMinutesRemainingAtLastAttempt'] = df['slaTimeRemainingAtLastAttempt'].dt.total_seconds() / 60

    # add the total time spent on the last attempt
    df['finalAttemptDuration'] = df['deliveryCompletedAt'] - df['finalAttemptStartedAt']
    df['finalAttemptDurationMinutes'] = df['finalAttemptDuration'].dt.total_seconds() / 60

    if 'driverAssignedAt' in df.columns:
        # add the time spent from the time the attempt was started, to the time a driver as assigned
        df['driverAssignedLagTime'] = df['driverAssignedAt'] - df['finalAttemptStartedAt']
        df['driverAssignedLagTimeMinutes'] = df['driverAssignedLagTime'].dt.total_seconds() / 60

        # add the time spent from the time the driver was assigned, to the time the driver picked up the package
        df['driverPickUpLagTime'] = df['pickedUpAt'] - df['driverAssignedAt']
        df['driverPickUpLagTimeMinutes'] = df['driverPickUpLagTime'].dt.total_seconds() / 60

    return df


def create_ontime_columns(df):
    df['lspOnTime'] = df['finalAttemptDurationMinutes'] < df['serviceLevel'].map(lp_sla_time_in_minutes).astype(int)
    df['lspOnTime'] = df['lspOnTime'].astype(int)

    return df
