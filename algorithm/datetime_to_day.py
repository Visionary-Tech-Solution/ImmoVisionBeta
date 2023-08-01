from datetime import datetime


def get_day_from_datetime(datetime):
    datetime_string = str(datetime)
    date_format = "%Y-%m-%d %H:%M:%S.%f%z"
    date = datetime.strptime(datetime_string, date_format)

    # Get the day name from the datetime object
    day_name = date.strftime("%A")

    return day_name


def get_day_name( day):
    days_of_week = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
    }
    return days_of_week[day]