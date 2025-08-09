import datetime
import pytz

import timezonefinder
tf = timezonefinder.TimezoneFinder()


def get_local_datetime_from_utc_datetime_string(utc_iso_dt_string, lat, lon):
    # Timezone finder library to get timezone string
    timezone_str = tf.timezone_at(lat=lat, lng=lon)

    if timezone_str is None:
        print("Could not determine the time zone")
        return None
    else:
        # Parse the input date string into a datetime object
        dt_naive = datetime.datetime.fromisoformat(utc_iso_dt_string)

        # Localize the datetime to UTC (or source timezone if different)
        dt_utc = pytz.utc.localize(dt_naive)

        # Convert the datetime to the target timezone
        timezone = pytz.timezone(timezone_str)
        dt_local = dt_utc.astimezone(timezone)

        return dt_local


def get_timezone_at(lat, lon):
    return tf.timezone_at(lat=lat, lng=lon)


def get_offset_date(d, lat, lon):
    # The input string or datetime MUST already be time in UTC
    timezone_str = tf.timezone_at(lat=lat, lng=lon)

    if timezone_str is None:
        print("Could not determine the time zone")
        return None

    # Parse the input to a datetime object
    if isinstance(d, str):
        d = datetime.datetime.fromisoformat(d)
    elif not isinstance(d, datetime.datetime):
        raise ValueError("Input 'd' must be a datetime object or ISO 8601 string")

    # Assume input is in UTC if it doesn't have timezone information
    if d.tzinfo is None:
        d = d.replace(tzinfo=pytz.utc)
    else:
        d = d.astimezone(pytz.utc)

    # Convert to the target timezone
    local_timezone = pytz.timezone(timezone_str)
    local_time = d.astimezone(local_timezone)

    return local_time


def getweekday(d, lat, lon):
    return datetime.datetime.isoweekday(get_offset_date(d, lat, lon))


def gethour(d, lat, lon):
    return get_offset_date(d, lat, lon).hour


def getmonth(d, lat, lon):
    return get_offset_date(d, lat, lon).month


def getweek(d, lat, lon):
    return get_offset_date(d, lat, lon).isocalendar().week


def get_local_time_components(d, lat, lon):
    off_date = get_offset_date(d, lat, lon)
    return {
        "localWeekday": datetime.datetime.isoweekday(off_date),
        "localHour": off_date.hour,
        "localMonth": off_date.month,
        "localWeekNumber": off_date.isocalendar().week
    }