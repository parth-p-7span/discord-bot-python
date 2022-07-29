import asyncio
import json
import os

from discord.ext import commands
import discord
from datetime import datetime, timedelta, time
import time
import calendar
import pytz
import requests
from bs4 import BeautifulSoup
import random
import urllib.request
from string import Template

import termtables as tt
from dotenv import load_dotenv

import constants
import clickup
import func

tz_IN = pytz.timezone('Asia/Kolkata')

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
client = commands.Bot(command_prefix='/', help_command=None, intents=intents)

with open('messages.json', 'r') as f:
    messages = json.load(f)


@client.event
async def on_ready():
    client.loop.create_task(background_job())
    print(f'{client.user} has Awoken!')


@client.command(name="test")
async def test(ctx):
    if ctx.channel.type != discord.ChannelType.private:
        await ctx.send(messages['dm_kar_bhai'])
        return
    print('-------', ctx.channel, '---', type(ctx.channel))
    await ctx.send(f'Tested!')


@client.command()
async def summary(ctx, month=''):
    if ctx.channel.type != discord.ChannelType.private:
        await ctx.send(messages['dm_kar_bhai'])
        return
    now = datetime.now(tz_IN)
    if month == "":
        month = str(now.month)

    start_of_day = datetime(now.year, int(month), 1, 0, 0, 0)
    month_range = calendar.monthrange(now.year, int(month))
    end_of_day = datetime(now.year, int(month), month_range[1], 23, 59, 59)
    s_timestamp = str(round(time.mktime(start_of_day.timetuple())) * 1000)
    e_timestamp = str(round(time.mktime(end_of_day.timetuple())) * 1000)

    hours, mins = clickup.get_monthly_hours(s_timestamp, e_timestamp, func.find_click_id(ctx.message.author.id))
    my_data = [["From", f'{start_of_day.day}-{start_of_day.month}-{start_of_day.year}'], ["To", f'{end_of_day.day}-{end_of_day.month}-{end_of_day.year}'], ["Hours", hours], ["Minutes", mins]]

    table = tt.to_string(
        my_data,
        style=tt.styles.rounded_thick,
        padding=(0, 3),
    )

    string = f"{Template(messages['summary_msg']).substitute(month=func.get_month_name(month))}\n`{table}`"

    await ctx.send(string)


@client.command()
async def register(ctx, email):
    if ctx.channel.type != discord.ChannelType.private:
        await ctx.send(messages['dm_kar_bhai'])
        return
    if email != '':
        discord_id = str(ctx.message.author.id)
        result = clickup.register(email, discord_id)
        if result == constants.STATUS_NO_CONTENT:
            await ctx.send(messages['err_no_user_found'])
        elif result == constants.STATUS_BAD_REQUEST:
            await ctx.send(messages['err_while_entering_record'])
        elif result == constants.STATUS_OK:
            clickup.create_json()
            await ctx.send(messages['registered_successfully'])
        else:
            await ctx.send(messages['something_went_wrong'])
    else:
        await ctx.send(messages['provide_email'])


@client.command(aliases=['clear-cache'])
async def clear_cache(ctx):
    if ctx.channel.type != discord.ChannelType.private:
        await ctx.send(messages['dm_kar_bhai'])
        return
    result = func.clear_cache()
    if result:
        await ctx.send(messages['cached_data_cleared_msg'])
    else:
        await ctx.send(messages['something_went_wrong'])


@client.command()
async def meme(ctx, tag="programming"):
    response = requests.get(constants.meme_url + tag)
    soup = BeautifulSoup(response.content, 'lxml')
    divs = soup.find_all('div', class_='item-aux-container')
    imgs = []
    for div in divs:
        img = div.find('img')['src']
        if img.startswith('http') and img.endswith('jpeg'):
            imgs.append(img)
    meme = random.choice(imgs)
    urllib.request.urlretrieve(meme, "meme.jpg")
    await ctx.send(file=discord.File('meme.jpg'))
    os.remove('meme.jpg')


@client.command()
async def fact(ctx):
    try:
        res = requests.get(constants.facts_url, headers={'X-Api-Key': constants.facts_api_key})
        text = res.json()[0]['fact']
        await ctx.send(text)
    except Exception as e:
        print(e)
        await ctx.send(messages['default_quote'])


@client.command()
async def broadcast(ctx, message):
    discord_id = ctx.message.author.id
    if discord_id not in [constants.CHARMI_DISCORD, constants.HARSH_DISCORD, constants.PARTH_DISCORD]:
        await ctx.send(messages['permission_denied_msg'])
        return
    members = client.get_all_members()
    for m in members:
        if m.id != constants.BOT_DISCORD and m.bot == False:
            await m.send(message)
            print("BROADCAST SENT TO => ", m.name)
            await asyncio.sleep(0.5)


@client.command()
async def compare(ctx):
    await ctx.send(Template(messages['compare_fun_msg']).substitute(id=str(constants.BOT_DISCORD)))


@client.command()
async def eod(ctx, date=''):
    if ctx.channel.type != discord.ChannelType.private:
        await ctx.send(messages['dm_kar_bhai'])
        return
    if date == '':
        dt = datetime.now(tz_IN)
    else:
        try:
            dt = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            dt = datetime.strptime(date, '%d-%m-%Y')

    discord_id = str(ctx.message.author.id)

    start_of_day = datetime(dt.year, dt.month, dt.day, 0, 0, 0, tzinfo=tz_IN)
    end_of_day = datetime(dt.year, dt.month, dt.day, 23, 59, 59, tzinfo=tz_IN)
    s_timestamp = str(round(time.mktime(start_of_day.timetuple())) * 1000)
    e_timestamp = str(round(time.mktime(end_of_day.timetuple())) * 1000)
    my_tasks = clickup.get_tasks(s_timestamp, e_timestamp, discord_id)
    # func.createImage(my_tasks)
    if len(my_tasks) > 1:
        print(len(my_tasks))
        if len(my_tasks) > 5:
            string1 = tt.to_string(
                my_tasks[:5],
                style=tt.styles.rounded_thick,
                header=["Task Name", "Hours", "Start", "End"],
                padding=(0, 1),
                alignment="lccc"
            )
            string1 = "`" + string1 + "`"

            string2 = tt.to_string(
                my_tasks[5:],
                style=tt.styles.rounded_thick,
                padding=(0, 1),
                alignment="lccc"
            )
            string2 = "`" + string2 + "`"

            await ctx.send(string1)
            await ctx.send(string2)

        else:
            string = tt.to_string(
                my_tasks,
                style=tt.styles.rounded_thick,
                header=["Task Name", "Hours", "Start", "End"],
                padding=(0, 1),
                alignment="lccc"
            )
            string = "`" + string + "`"
            await ctx.send(string)

    else:
        string = messages['msg_no_log_hours']
        await ctx.send(string)


@client.command()
async def help(ctx):
    helps = [
        [messages['command_1'], messages['command_1_msg']],
        [messages['command_2'], messages['command_2_msg']],
        [messages['command_3'], messages['command_3_msg']],
        [messages['command_4'], messages['command_4_msg']],
        [messages['command_5'], messages['command_5_msg']],
        [messages['command_6'], messages['command_6_msg']],
    ]
    message = tt.to_string(
        helps,
        style=tt.styles.rounded_thick,
        header=["Command", "Description"],
        padding=(0, 3),
        alignment="lc"
    )
    message = "`" + message + "`"
    await ctx.send(message)


@client.command(aliases=['refresh-data'])
async def refresh(ctx):
    clickup.create_json()
    await ctx.send(messages['data_refreshed'])

@client.command()
async def temp(ctx):
    channel = client.get_channel(constants.CELEBRATION_CHANNEL)
    await channel.send("aaj Friday nahi Thursday hai <@879986324415873054>")


@client.command()
async def purge(ctx, count):
    discord_id = ctx.message.author.id
    if discord_id == constants.HARSH_DISCORD:
        print("===> PURGING MESSAGES")
        await ctx.channel.purge(limit=count)
    else:
        print("===> ", discord_id, " PURGE ACCESS DENIED")


async def send_evening_message():
    print("===> SEND EVENING MESSAGE")
    ids = func.get_discord_ids()
    # ids = [927786642721341490]
    for uid in ids:
        user = client.get_user(uid)
        await user.send(messages['evening_clickup_msg'])
        await asyncio.sleep(1)


async def send_everyday_report_to_hr(is_monday):
    print("===> SEND REPORT TO HR")
    if is_monday:
        yesterday = datetime.today() - timedelta(3)
    else:
        yesterday = datetime.today() - timedelta(1)

    start_of_day = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    end_of_day = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
    s_timestamp = str(round(time.mktime(start_of_day.timetuple())) * 1000)
    e_timestamp = str(round(time.mktime(end_of_day.timetuple())) * 1000)

    formatted_date = datetime.strftime(yesterday, '%Y-%m-%d')

    all_tasks = clickup.get_tasks_for_all_members(s_timestamp, e_timestamp)
    file_path = func.generate_report(all_tasks, formatted_date)

    user = client.get_user(constants.CHARMI_DISCORD)
    await user.send(f"Here's daily report of {formatted_date}", file=discord.File(file_path))
    func.clear_cache()


async def send_morning_message():
    print("===> SEND MORNING MESSAGE")

    yesterday = datetime.today() - timedelta(1)
    s_timestamp, e_timestamp = func.get_timestamps(yesterday)

    all_tasks = clickup.get_tasks_for_all_members(s_timestamp, e_timestamp)
    sorted_data = func.sort_data(all_tasks)
    user_ids = func.get_user_ids()
    reduced_data, hours = func.reduce_data(sorted_data, user_ids, get_hours=True)

    for record in hours:
        if record[1] >= 10:
            discord_id = func.get_discord_id(record[0])
            user = client.get_user(int(discord_id))
            await user.send(messages['morning_clickup_msg'])
            await asyncio.sleep(1)


async def wish_day():
    print("===> WISH DAY")

    celebration_channel = client.get_channel(constants.CELEBRATION_CHANNEL)
    birthdays, work_anniversary = clickup.check_for_day()

    print(birthdays, work_anniversary)

    if len(birthdays) > 0:
        string = 'Happy birthday '
        for i in birthdays:
            string += f'<@{i[1]}>  '

        await celebration_channel.send(string)

    if len(work_anniversary) > 0:
        message = 'Happy work anniversary '
        for i in work_anniversary:
            message += f'<@{i[1]}>  '

        await celebration_channel.send(message)


async def send_month_end_message():
    print("===> SEND MONTH END MESSAGE")
    ids = func.get_discord_ids()
    for i in ids:
        user = client.get_user(int(i))
        await user.send(messages['monthend_message'])


async def create_thread(date, channel_id, is_morning, channel_name, is_java_update=False):
    channel = client.get_channel(channel_id)
    if is_morning:
        name = "🌞 " + date
    else:
        name = "🌚 " + date
    thread = await channel.create_thread(name=name, type=discord.ChannelType.public_thread)
    if is_java_update:
        await thread.send(messages['java_daily_updates_msg'])
    else:
        await thread.send(Template(messages['thread_msg']).substitute(date=date))
    print(f"===> {channel_name} THREAD CREATED")


async def background_job():
    while True:
        now = datetime.now(tz_IN)
        monthend = calendar.monthrange(now.year, now.month)[1]

        # send morning message to those whose yesterday clickup hours is > 10
        if now.hour == constants.MORNING_TIME[0] and now.minute == constants.MORNING_TIME[1] and now.weekday() <= 4:
            await send_morning_message()

        # send evening clickup message to all everyday.
        if now.hour == constants.EVENING_TIME[0] and now.minute == constants.EVENING_TIME[1] and now.weekday() <= 4:
            await send_evening_message()

        # send everyday report to HR
        if now.hour == constants.REPORTING_TIME[0] and now.minute == constants.REPORTING_TIME[1] and now.weekday() <= 4:
            await send_everyday_report_to_hr(now.weekday() == 0)

        # send wishing message in celebration channel
        if now.hour == constants.CELEBRATE_TIME[0] and now.minute == constants.CELEBRATE_TIME[1]:
            await wish_day()

        # send month-end clickup warning message
        if (now.day == monthend or now.day == monthend - 1) and now.hour == constants.MORNING_THREAD_TIME[
            0] and now.minute == constants.MORNING_THREAD_TIME[1]:
            await send_month_end_message()

        # create morning thread
        if now.hour == constants.MORNING_THREAD_TIME[0] and now.minute == constants.MORNING_THREAD_TIME[
            1] and now.weekday() <= 4:
            date = now.strftime('%d.%m.%Y')
            await create_thread(date, constants.LARAVEL_CHANNEL, True, "LARAVEL")
            await create_thread(date, constants.DESIGN_CHANNEL, True, "DESIGN")
            await create_thread(date, constants.CMS_CHANNEL, True, "CMS")
            await create_thread(date, constants.JAVA_UPDATES_CHANNEL, True, "JAVA_UPDATES", is_java_update=True)
            await create_thread(date, constants.JAVASCRIPT_CHANNEL, True, "JAVASCRIPT_CHANNEL")
            await create_thread(date, constants.SALES_CHANNEL, True, "SALES_CHANNEL")
            # await create_thread(date, constants.MOBILE_CHANNEL, True, "MOBILE_CHANNEL")

        # create evening thread
        if now.hour == constants.EVENING_THREAD_TIME[0] and now.minute == constants.EVENING_THREAD_TIME[
            1] and now.weekday() <= 4:
            date = now.strftime('%d.%m.%Y')
            await create_thread(date, constants.LARAVEL_CHANNEL, False, "LARAVEL")
            await create_thread(date, constants.DESIGN_CHANNEL, False, "DESIGN")
            await create_thread(date, constants.CMS_CHANNEL, False, "CMS")
            await create_thread(date, constants.JAVA_UPDATES_CHANNEL, False, "JAVA_UPDATES", is_java_update=True)
            await create_thread(date, constants.JAVASCRIPT_CHANNEL, False, "JAVASCRIPT_CHANNEL")
            await create_thread(date, constants.SALES_CHANNEL, False, "SALES_CHANNEL")
            # await create_thread(date, constants.MOBILE_CHANNEL, False, "MOBILE_CHANNEL")

        await asyncio.sleep(60)


@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        Template(messages['welcome_to_server_msg']).substitute(name=str(member.name))
    )
    user = client.get_user(constants.HARSH_DISCORD)
    await user.send(Template(messages['user_has_joined_server_msg']).substitute(id=str(member.id)))

if __name__ == "__main__":
    client.run(os.getenv('TOKEN'))
