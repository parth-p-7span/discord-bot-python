import json
import requests
import constants
import format_datetime
import func
from datetime import datetime
import pytz


tz_IN = pytz.timezone('Asia/Kolkata')


def get_task_by_id(task_id):
    request = requests.get(
        url=constants.getTask + '/' + task_id,
        headers=constants.header
    )
    return request.json()


def get_user_task_id(email):
    page = 0
    request = requests.get(
        url=constants.listUrl + "?page=" + str(page),
        headers=constants.header
    )

    tasks = request.json()['tasks']
    count = len(tasks)
    while count == 100:
        page += 1
        request = requests.get(
            url=constants.listUrl + "?page=" + str(page),
            headers=constants.header
        )
        tasks = tasks + request.json()['tasks']
        count = len(request.json()['tasks'])

    for index, task in enumerate(tasks):
        try:
            if task['custom_fields'][4]['value'] == email:
                return task['id']
        except Exception as e:
            print("[GET_USER_TASK_ID EXCEPTION] : ", str(e))
            pass

    return constants.STATUS_NO_CONTENT


def insert_discord_id(task_id, discord_id):
    payload = {
        "value": str(discord_id)
    }
    request = requests.post(
        url=constants.getTask + '/' + str(task_id) + '/field/' + constants.discord_id_field,
        headers=constants.header,
        data=json.dumps(payload)
    )
    return request


def insert_clickup_id(task_id, clickup_id):
    payload = {
        "value": str(clickup_id)
    }
    request = requests.post(
        url=constants.getTask + '/' + str(task_id) + '/field/' + constants.clickup_id_field,
        headers=constants.header,
        data=json.dumps(payload)
    )
    return request


def get_clickup_id(email):
    request = requests.request(
        method='GET',
        url=constants.getTeam,
        headers=constants.header
    )
    users = request.json()['teams'][0]['members']
    for user in users:
        if user['user']['email'] == email:
            return user['user']['id']
    return constants.STATUS_NO_CONTENT


def register(email, discord_id):
    task_id = get_user_task_id(email)
    click_up_id = get_clickup_id(email)
    print("-->", click_up_id)
    if task_id == constants.STATUS_NO_CONTENT or click_up_id == constants.STATUS_NO_CONTENT:
        return constants.STATUS_NO_CONTENT
    c_response = insert_clickup_id(task_id, click_up_id)
    d_response = insert_discord_id(task_id, discord_id)
    if c_response.status_code != constants.STATUS_OK or d_response.status_code != constants.STATUS_OK:
        return constants.STATUS_BAD_REQUEST
    return constants.STATUS_OK


def create_json():
    users = []
    request = requests.get(
        url=constants.listUrl,
        headers=constants.header
    )
    tasks = request.json()['tasks']
    for task in tasks:
        name = task['name']
        try:
            email = task['custom_fields'][4]['value']
        except Exception as e:
            email = ''
        try:
            click_up_id = task['custom_fields'][16]['value']
            discord_id = task['custom_fields'][17]['value']
        except Exception as e:
            print("[CREATE_JSON EXCEPTION] : ", str(e))
            click_up_id = ''
            discord_id = ''
        users.append({'name': name, 'email': email, 'click_up_id': click_up_id, 'discord_id': discord_id})

    with open('users.json', 'w') as f:
        f.write(json.dumps(users))


def get_tasks(start_date, end_date, discord_id):
    assignee = func.find_click_id(discord_id)
    tasks = []
    hours = []
    request = requests.get(
        url=constants.getTeam + '/604747/time_entries?start_date=' + str(start_date) + '&end_date=' + str(
            end_date) + '&assignee=' + assignee,
        headers=constants.header
    )
    for task in request.json()['data']:
        t_name = task['task']['name']
        t_duration = task['duration']
        t_start = task['start']
        t_end = task['end']
        h, m = format_datetime.convert(int(t_duration))
        tasks.append([t_name, f'{h}h {m}m', format_datetime.get_time(t_start), format_datetime.get_time(t_end)])
        hours.append(f'{h}h {m}m')
    final_data = format_datetime.get_total_row(tasks, hours)
    return final_data


def get_assignees():
    assignees = ""
    with open('users.json', 'r') as f:
        users = json.load(f)
    for user in users:
        if user['click_up_id'] != "":
            assignees += user['click_up_id'] + ","
    return assignees


def get_tasks_for_all_members(start_date, end_date):
    assignees = get_assignees()
    request = requests.get(
        url=constants.getTeam + '/604747/time_entries?start_date=' + str(start_date) + '&end_date=' + str(
            end_date) + '&assignee=' + assignees[:-1],
        headers=constants.header
    )
    return request.json()['data']


def check_for_day():
    today = datetime.now(tz_IN).strftime('%m-%d')
    birthday_guys = []
    work_anniversary_guys = []
    request = requests.get(
        url=constants.listUrl,
        headers=constants.header
    )
    tasks = request.json()['tasks']
    for user in tasks:
        try:
            joining_day_field = user['custom_fields'][7]
            birthday_field = user['custom_fields'][8]
            join_date = format_datetime.get_date(joining_day_field['value'])
            birth_date = format_datetime.get_date(birthday_field['value'])
            if birth_date == today:
                birthday_guys.append([user['name'], user['custom_fields'][18]['value'], birth_date])
            if join_date == today:
                work_anniversary_guys.append([user['name'], user['custom_fields'][18]['value'], join_date])
        except Exception as e:
            print("[WISH_DAY EXCEPTION] : ", str(e))
    return birthday_guys, work_anniversary_guys

