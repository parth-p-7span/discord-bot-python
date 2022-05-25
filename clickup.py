import json
import requests
import constants
import format_datetime
import func
from datetime import datetime


# def reloadUserTasksJson():
#     request = requests.get(
#         url=constants.listUrl,
#         headers=constants.header
#     )
#     json_object = json.dumps(request.json(), indent=4)
#     with open('user_tasks.json', 'w') as f:
#         f.write(json_object)
#
# reloadUserTasksJson()

# def getTeamDetails():
#     users = []
#     request = requests.request(
#         method='GET',
#         url=getTeam,
#         headers=header
#     )
#     data = request.json()
#     team_members = data['teams'][0]['members']
#     for member in team_members:
#         user_dict = member['user']
#         users.append(dictToUser(user_dict))
#     return users


def getTaskById(taskId):
    request = requests.get(
        url=constants.getTask + '/' + taskId,
        headers=constants.header
    )
    return request.json()


def getUserTaskId(email):
    request = requests.get(
        url=constants.listUrl,
        headers=constants.header
    )

    tasks = request.json()['tasks']
    for task in tasks:
        try:
            if task['custom_fields'][4]['value'] == email:
                return task['id']
        except:
            pass

    return constants.STATUS_NO_CONTENT


def insertDiscordId(taskId, discordId):
    payload = {
        "value": str(discordId)
    }
    request = requests.post(
        url=constants.getTask + '/' + str(taskId) + '/field/' + constants.discord_id_field,
        headers=constants.header,
        data=json.dumps(payload)
    )
    return request


def insertClickUpId(taskId, clickUpId):
    payload = {
        "value": str(clickUpId)
    }
    request = requests.post(
        url=constants.getTask + '/' + str(taskId) + '/field/' + constants.clickup_id_field,
        headers=constants.header,
        data=json.dumps(payload)
    )
    return request


# def reloadTeamMembersJson():
#     request = requests.request(
#         method='GET',
#         url=getTeam,
#         headers=header
#     )
#     data = request.json()
#     team_members = data['teams'][0]['members']
#     json_object = json.dumps(team_members, indent=4)
#     with open('team_members.json', 'w') as f:
#         f.write(json_object)


def getClickUpId(email):
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


def register(email, discordId):
    taskId = getUserTaskId(email)
    clickUpId = getClickUpId(email)
    print("-->", clickUpId)
    if taskId == constants.STATUS_NO_CONTENT or clickUpId == constants.STATUS_NO_CONTENT:
        return constants.STATUS_NO_CONTENT
    cResponse = insertClickUpId(taskId, clickUpId)
    dResponse = insertDiscordId(taskId, discordId)
    if cResponse.status_code != constants.STATUS_OK or dResponse.status_code != constants.STATUS_OK:
        return constants.STATUS_BAD_REQUEST
    return constants.STATUS_OK


def createJson():
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
        except:
            email = ''
        try:
            clickUpId = task['custom_fields'][17]['value']
            discordId = task['custom_fields'][18]['value']
        except:
            clickUpId = ''
            discordId = ''
        users.append({'name': name, 'email': email, 'clickUpId': clickUpId, 'discordId': discordId})

    with open('users.json', 'w') as f:
        f.write(json.dumps(users))


def getTasks(startDate, endDate, discordId):
    assignee = func.findClickId(discordId)
    tasks = []
    hours = []
    request = requests.get(
        url=constants.getTeam + '/604747/time_entries?start_date=' + str(startDate) + '&end_date=' + str(
            endDate) + '&assignee=' + assignee,
        headers=constants.header
    )
    for task in request.json()['data']:
        tName = task['task']['name']
        tDuration = task['duration']
        tStart = task['start']
        tEnd = task['end']
        h, m = format_datetime.convert(int(tDuration))
        tasks.append([tName, f'{h}h {m}m', format_datetime.get_time(tStart), format_datetime.get_time(tEnd)])
        hours.append(f'{h}h {m}m')
    final_data = format_datetime.get_total_row(tasks, hours)
    return final_data


def getAssignees():
    assignees = ""
    with open('users.json', 'r') as f:
        users = json.load(f)
    for user in users:
        if user['clickUpId'] != "":
            assignees += user['clickUpId'] + ","
    return assignees


def getTasksForAllMembers(startDate, endDate):
    assignees = getAssignees()
    request = requests.get(
        url=constants.getTeam + '/604747/time_entries?start_date=' + str(startDate) + '&end_date=' + str(
            endDate) + '&assignee=' + assignees[:-1],
        headers=constants.header
    )
    return request.json()['data']


def checkForDay():
    today = datetime.now().strftime('%m-%d')
    # today = datetime(2022,4,8).strftime('%m-%d')
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
        except:
            pass
    return birthday_guys, work_anniversary_guys

# print(checkForDay())
