import asyncio
import json

from discord.ext import commands, tasks
from discord.utils import get
from discord.ext import commands, tasks
import discord
from datetime import datetime, timedelta, time
import time
import calendar
import pytz

import io
import aiohttp
import termtables as tt

import constants
import clickup
import func

tz_IN = pytz.timezone('Asia/Kolkata')

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
client = commands.Bot(command_prefix='/', help_command=None, intents=intents)
# client = commands.AutoShardedBot(command_prefix='/', help_command=None, intents=intents)

with open('messages.json', 'r') as f:
    messages = json.load(f)


@client.event
async def on_ready():
    client.loop.create_task(backgroundJob())
    print(f'{client.user} has Awoken!')


@client.command(name="test")
async def test(ctx):
    print('-------', ctx.channel, '---', type(ctx.channel))
    await ctx.send(f'Tested!')


@client.command()
async def register(ctx, email):
    if email != '':
        discordId = str(ctx.message.author.id)
        result = clickup.register(email, discordId)
        if result == constants.STATUS_NO_CONTENT:
            await ctx.send(messages['err_no_user_found'])
        elif result == constants.STATUS_BAD_REQUEST:
            await ctx.send(messages['err_while_entering_record'])
        elif result == constants.STATUS_OK:
            clickup.createJson()
            await ctx.send(messages['registered_successfully'])
        else:
            await ctx.send(messages['something_went_wrong'])
    else:
        await ctx.send('Please provide your email address!')


@client.command(aliases=['clear-cache'])
async def clearCache(ctx):
    result = func.clearCache()
    if result:
        await ctx.send('All daily report cache has been cleared!')
    else:
        await ctx.send('Something went wrong!')


@client.command()
async def eod(ctx, date=''):
    if ctx.channel.type == discord.ChannelType.private:
        if date == '':
            dt = datetime.now(tz_IN)
        else:
            try:
                dt = datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                dt = datetime.strptime(date, '%d-%m-%Y')

        discordId = str(ctx.message.author.id)

        start_of_day = datetime(dt.year, dt.month, dt.day, 0, 0, 0, tzinfo=tz_IN)
        end_of_day = datetime(dt.year, dt.month, dt.day, 23, 59, 59, tzinfo=tz_IN)
        sTimestamp = str(round(time.mktime(start_of_day.timetuple())) * 1000)
        eTimestamp = str(round(time.mktime(end_of_day.timetuple())) * 1000)
        tasks = clickup.getTasks(sTimestamp, eTimestamp, discordId)
        # func.createImage(tasks)
        if len(tasks) > 1:
            string = tt.to_string(
                tasks,
                style=tt.styles.rounded_thick,
                header=["Task Name", "Hours", "Start", "End"],
                padding=(0, 1),
                alignment="lccc"
            )
            string = "`" + string + "`"
            # file_path = "temp/test.png"
            # await ctx.send(file=discord.File(file_path))
            await ctx.send(string)


        else:
            string = messages['msg_no_log_hours']
            await ctx.send(string)

    else:
        await ctx.send(f'Please send personal message to <@{constants.BOT_DISCORD}> for this command to execute.')


@client.command()
async def help(ctx):
    helps = [
        [messages['command_1'], messages['command_1_msg']],
        [messages['command_2'], messages['command_2_msg']],
        [messages['command_3'], messages['command_3_msg']],
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
    clickup.createJson()
    await ctx.send(messages['data_refreshed'])

@client.command()
async def purge(ctx, count):
    discordId = ctx.message.author.id
    if discordId == constants.HARSH_DISCORD:
        print("===> PURGING MESSAGES")
        await ctx.channel.purge(limit=count)
    else:
        print("===> ", discordId, " PURGE ACCESS DENIED")

async def sendEveningMessage():
    print("===> SEND EVENING MESSAGE")
    ids = func.getDiscordIds()
    # ids = [927786642721341490]
    for uid in ids:
        user = client.get_user(uid)
        await user.send(messages['evening_clickup_msg'])
        await asyncio.sleep(1)


async def sendEverydayReportToHR():
    print("===> SEND REPORT TO HR")
    yesterday = datetime.today() - timedelta(1)

    start_of_day = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    end_of_day = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
    sTimestamp = str(round(time.mktime(start_of_day.timetuple())) * 1000)
    eTimestamp = str(round(time.mktime(end_of_day.timetuple())) * 1000)

    formated_date = datetime.strftime(yesterday, '%Y-%m-%d')

    allTasks = clickup.getTasksForAllMembers(sTimestamp, eTimestamp)
    file_path = func.generateReport(allTasks, formated_date)

    user = client.get_user(constants.CHARMI_DISCORD)
    await user.send(f"Here's daily report of {formated_date}", file=discord.File(file_path))


async def sendMorningMessage():
    print("===> SEND MORNING MESSAGE")

    yesterday = datetime.today() - timedelta(1)
    sTimestamp, eTimestamp = func.getTimestamps(yesterday)

    allTasks = clickup.getTasksForAllMembers(sTimestamp, eTimestamp)
    sortedData = func.sortData(allTasks)
    userIds = func.getUserIds()
    reducedData, hours = func.reduceData(sortedData, userIds, getHours=True)

    for record in hours:
        if record[1] >= 10:
            discordId = func.getDiscordId(record[0])
            user = client.get_user(int(discordId))
            await user.send(messages['morning_clickup_msg'])
            await asyncio.sleep(1)


async def wishDay():
    print("===> WISH DAY")

    celebration_channel = client.get_channel(constants.CELEBRATION_CHANNEL)
    birthdays, work_anniversary = clickup.checkForDay()
    # birthdays, work_anniversary = [['Parth Panchal', '927786642721341490', '04-08'],['Parth Panchal', '927786642721341490', '04-08'],['Parth Panchal', '927786642721341490', '04-08']], [['Parth Panchal', '927786642721341490', '04-08'],['Parth Panchal', '927786642721341490', '04-08']]

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


async def testMessage():
    print("===> called")
    channel = client.get_channel(constants.CELEBRATION_CHANNEL)
    await channel.send('Test message')


async def sendMonthEndMessage():
    print("===> SEND MONTH END MESSAGE")
    ids = func.getDiscordIds()
    for i in ids:
        user = client.get_user(int(i))
        await user.send(messages['monthend_message'])


async def createThread(date, channel_id, is_morning):
    print("===> CREATE THREAD")
    channel = client.get_channel(channel_id)
    if is_morning:
        name = "🌞 " + date
    else:
        name = "🌚 " + date
    thread = await channel.create_thread(name=name, type=discord.ChannelType.public_thread)
    await thread.send("Please enter updates of " + date)


async def backgroundJob():
    while True:
        now = datetime.now(tz_IN)
        monthend = calendar.monthrange(now.year, now.month)[1]

        # send morning message to those whose yesterday clickup hours is > 10
        if now.hour == constants.MORNING_TIME[0] and now.minute == constants.MORNING_TIME[1] and now.weekday() <= 4:
            await sendMorningMessage()

        # send evening clickup message to all everyday.
        if now.hour == constants.EVENING_TIME[0] and now.minute == constants.EVENING_TIME[1] and now.weekday() <= 4:
            await sendEveningMessage()

        # send everyday report to HR
        if now.hour == constants.REPORTING_TIME[0] and now.minute == constants.REPORTING_TIME[1] and now.weekday() <= 4:
            await sendEverydayReportToHR()

        # send wishing message in celebration channel
        if now.hour == constants.CELEBRATE_TIME[0] and now.minute == constants.CELEBRATE_TIME[1]:
            await wishDay()

        # send month-end clickup warning message
        if now.day == monthend or now.day == monthend - 1:
            await sendMonthEndMessage()

        # create morning thread
        if now.hour == constants.MORNING_THREAD_TIME[0] and now.minute == constants.MORNING_THREAD_TIME[1] and now.weekday() <= 4:
            date = now.strftime('%d.%m.%Y')
            await createThread(date, constants.LARAVEL_CHANNEL, True)
            await createThread(date, constants.JAVA_CHANNEL, True)
            await createThread(date, constants.DESIGN_CHANNEL, True)
            await createThread(date, constants.CMS_CHANNEL, True)

        # create evening thread
        if now.hour == constants.EVENING_THREAD_TIME[0] and now.minute == constants.EVENING_THREAD_TIME[1] and now.weekday() <= 4:
            date = now.strftime('%d.%m.%Y')
            await createThread(date, constants.LARAVEL_CHANNEL, False)
            await createThread(date, constants.JAVA_CHANNEL, False)
            await createThread(date, constants.DESIGN_CHANNEL, False)
            await createThread(date, constants.CMS_CHANNEL, False)

        await asyncio.sleep(60)

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f"Hi {member.name},\nwelcome to 7Span's Discord server, enter `\\help` command for more information."
    )
    user = client.get_user(constants.HARSH_DISCORD)
    await user.send(f"{member.mention} joined 7Span's Discord server.")


if __name__ == "__main__":
    client.run(constants.TOKEN)


print("testing----")
