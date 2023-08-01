from datetime import datetime


def get_day_from_datetime(datetime):
    datetime_string = str(datetime)
    date_format = "%Y-%m-%d %H:%M:%S.%f%z"
    date = datetime.strptime(datetime_string, date_format)

    # Get the day name from the datetime object
    day_name = date.strftime("%A")

    return day_name


def get_day_name(day_number):
    days_of_week = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }

    mapped_day_number = day_number % 7  # Map day numbers greater than 6 to their corresponding day numbers
    if mapped_day_number in days_of_week:
        return days_of_week[mapped_day_number]
    else:
        return 'Invalid day number'