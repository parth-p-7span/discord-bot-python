import json
import os

import format_datetime
import pandas as pd
from datetime import datetime
import time

# import dataframe_image as dfi


def sort_data(data):
    new_data = []
    for task in data:
        new_data.append({
            "id": str(task['user']['id']),
            "name": task['user']['username'],
            "duration": task['duration']
        })
    return new_data


def get_user_ids():
    ids = []
    with open('users.json', 'r') as f:
        users = json.load(f)
    for user in users:
        if user["click_up_id"] != "":
            ids.append(user["click_up_id"])
    return ids


def reduce_data(data, user_ids, get_hours=False):
    reduced_data = []
    hours = []
    for user_id in user_ids:
        user_hours = 0
        user_name = ""
        for record in data:
            if record['id'] == str(user_id):
                user_hours += int(record['duration'])
                user_name = record['name']
        h, m = format_datetime.convert(user_hours)
        if h != 0:
            reduced_data.append([user_id, user_name, f'{h}h {m}m'])
            hours.append([user_id, h])
    if get_hours:
        return reduced_data, hours
    return reduced_data


def generate_report(data, date):
    excel_data = []
    sorted_data = sort_data(data)
    user_ids = get_user_ids()
    reduced_data = reduce_data(sorted_data, user_ids)
    file_name = 'daily_reports/' + str(date) + '.xlsx'

    for uid, name, hour in reduced_data:
        excel_data.append([name, hour])
    df = pd.DataFrame(excel_data, columns=['Name', 'Hours'])
    df = df.sort_values(by=["Name"])
    df.to_excel(file_name, index=False)
    return file_name


def get_discord_ids():
    ids = []
    with open('users.json', 'r') as f:
        users = json.load(f)
    for user in users:
        if user["discord_id"] != "":
            ids.append(int(user["discord_id"]))
    return ids


def get_timestamps(yesterday):
    start_of_day = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    end_of_day = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
    s_timestamp = str(round(time.mktime(start_of_day.timetuple())) * 1000)
    e_timestamp = str(round(time.mktime(end_of_day.timetuple())) * 1000)
    return s_timestamp, e_timestamp


def find_click_id(discord_id):
    with open('users.json', 'r') as f:
        users = json.load(f)

    for user in users:
        if user['discord_id'] == str(discord_id):
            return user['click_up_id']


def get_discord_id(clickup_id):
    with open('users.json', 'r') as f:
        users = json.load(f)

    for user in users:
        if user['click_up_id'] == clickup_id:
            return user['discord_id']


def clear_cache():
    try:
        for f in os.listdir('daily_reports'):
            os.remove(os.path.join('daily_reports', f))
        return True
    except Exception as e:
        print('CLEAR CACHE ERROR => ', e)
        return False

#
# def create_image(tasks):
#     df = pd.DataFrame(tasks, columns=['Task Name', 'Hours', 'Start', 'End'])
#     df1 = df.style.set_table_styles([dict(selector='th', props=[('text-align', 'center')])])
#     df1.set_properties(**{'text-align': 'center'}).hide(axis='index')
#     dfi.export(df1, 'temp/test.png', )


def get_month_name(month):
    with open('months.json', 'r') as f:
        data = json.loads(f.read())
    for k, d in data.items():
        if d == int(month):
            return k
