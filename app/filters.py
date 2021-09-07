from datetime import datetime, timedelta

def to_cst(datetime):
    """Convert a datetime in UTC to CT."""
    new_date_time = datetime - timedelta(hours=5)
    return new_date_time

def format_datetime(datetime, format=None, timedelta_hours=None):
    """Formats a datetime."""
    if timedelta_hours is not None:
        datetime += timedelta(hours=timedelta_hours)
    return datetime.strftime(format)

def timediference(start_datetime, end_datetime):
    """Formats a datetime."""
    td = end_datetime - start_datetime
    hours = td.seconds // 3600
    seconds = (td.seconds//60)%60
    return "{}H:{}M".format(hours, seconds)
