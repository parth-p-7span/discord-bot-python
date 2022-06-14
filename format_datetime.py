from datetime import datetime
import pytz


tz_IN = pytz.timezone('Asia/Kolkata')


def get_time(timestamp):
    timestamp = int(timestamp)//1000
    dt = datetime.fromtimestamp(timestamp, tz=tz_IN).strftime('%I:%M %p')
    return dt


def get_date(timestamp):
    timestamp = int(timestamp)//1000
    dt = datetime.fromtimestamp(timestamp, tz=tz_IN).strftime('%m-%d')
    return dt


def convert(seconds):
    seconds = seconds // 1000
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    # return f'{hour}h {minutes}m'
    return hour, minutes


def get_total_row(tasks, hours):
    mins = 0
    for hour in hours:
        stems = hour.split(" ")
        temp_h = int(stems[0].replace('h', ''))
        temp_m = int(stems[1].replace('m', ''))
        mins += temp_h*60
        mins += temp_m
    final_hours = mins // 60
    final_mins = mins % 60
    total = f"{final_hours}h {final_mins}m"
    tasks.append(["Total", total, "", ""])
    return tasks
