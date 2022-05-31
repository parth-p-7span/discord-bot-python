import json
import os

import format_datetime
import pandas as pd
from datetime import datetime, timedelta
import time

import dataframe_image as dfi


def sortData(data):
    newData = []
    for task in data:
        newData.append({
            "id": str(task['user']['id']),
            "name": task['user']['username'],
            "duration": task['duration']
        })
    return newData


def getUserIds():
    ids = []
    with open('users.json', 'r') as f:
        users = json.load(f)
    for user in users:
        if user["clickUpId"] != "":
            ids.append(user["clickUpId"])
    return ids


def reduceData(data, userIds, getHours=False):
    reducedData = []
    hours = []
    for id in userIds:
        user_hours = 0
        user_name = ""
        for record in data:
            if record['id'] == str(id):
                user_hours += int(record['duration'])
                user_name = record['name']
        h, m = format_datetime.convert(user_hours)
        reducedData.append([id, user_name, f'{h}h {m}m'])
        hours.append([id, h])
    if getHours:
        return reducedData, hours
    return reducedData


def generateReport(data, date):
    excelData = []
    sortedData = sortData(data)
    userIds = getUserIds()
    reducedData = reduceData(sortedData, userIds)
    file_name = 'daily_reports/' + str(date) + '.xlsx'

    for uid, name, hour in reducedData:
        excelData.append([name, hour])
    df = pd.DataFrame(excelData, columns=['Name', 'Hours'])
    df = df.sort_values(by=["Name"])
    df.to_excel(file_name, index=False)
    return file_name


def getDiscordIds():
    ids = []
    with open('users.json', 'r') as f:
        users = json.load(f)
    for user in users:
        if user["discordId"] != "":
            ids.append(int(user["discordId"]))
    return ids


def getTimestamps(yesterday):
    start_of_day = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    end_of_day = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
    sTimestamp = str(round(time.mktime(start_of_day.timetuple())) * 1000)
    eTimestamp = str(round(time.mktime(end_of_day.timetuple())) * 1000)
    return sTimestamp, eTimestamp


def findClickId(discordId):
    with open('users.json', 'r') as f:
        users = json.load(f)

    for user in users:
        if user['discordId'] == str(discordId):
            return user['clickUpId']


def getDiscordId(clickUpId):
    with open('users.json', 'r') as f:
        users = json.load(f)

    for user in users:
        if user['clickUpId'] == clickUpId:
            return user['discordId']


def clearCache():
    try:
        for f in os.listdir('daily_reports'):
            os.remove(os.path.join('daily_reports', f))
        return True
    except Exception as e:
        print('CLEAR CACHE ERROR => ', e)
        return False


def createImage(tasks):
    df = pd.DataFrame(tasks, columns=['Task Name', 'Hours', 'Start', 'End'])
    df1 = df.style.set_table_styles([dict(selector='th', props=[('text-align', 'center')])])
    df1.set_properties(**{'text-align': 'center'}).hide(axis='index')
    dfi.export(df1, 'temp/test.png', )
