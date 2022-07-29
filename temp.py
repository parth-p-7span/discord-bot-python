import asyncio
import json
import os
import interactions
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

bot = interactions.Client(token=os.getenv('TOKEN'))

with open('messages.json', 'r') as f:
    messages = json.load(f)


@bot.command(
    name="test",
    description="testing slash command",
    dm_permission=True
)
async def test(ctx: interactions.CommandContext):
    if ctx.channel.type != discord.ChannelType.private:
        await ctx.send("DM kar ne bhai")
        return
    await ctx.send("hey there")


@bot.command(
    name="summary",
    description="To get monthly clickup summary",
    dm_permission=True,
    options=[
        interactions.Option(
            name="month",
            description="Enter Month",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def summary(ctx: interactions.CommandContext, month: str):
    try:
        if ctx.channel.type != discord.ChannelType.private:
            await ctx.send(messages['dm_kar_bhai'])
            return
    except:
        now = datetime.now(tz_IN)
        if month == "":
            month = str(now.month)

        start_of_day = datetime(now.year, int(month), 1, 0, 0, 0)
        month_range = calendar.monthrange(now.year, int(month))
        end_of_day = datetime(now.year, int(month), month_range[1], 23, 59, 59)
        s_timestamp = str(round(time.mktime(start_of_day.timetuple())) * 1000)
        e_timestamp = str(round(time.mktime(end_of_day.timetuple())) * 1000)

        hours, mins = clickup.get_monthly_hours(s_timestamp, e_timestamp, func.find_click_id(ctx.user.id))
        my_data = [["From", f'{start_of_day.day}-{start_of_day.month}-{start_of_day.year}'],
                   ["To", f'{end_of_day.day}-{end_of_day.month}-{end_of_day.year}'], ["Hours", hours], ["Minutes", mins]]

        table = tt.to_string(
            my_data,
            style=tt.styles.rounded_thick,
            padding=(0, 3),
        )

        string = f"{Template(messages['summary_msg']).substitute(month=func.get_month_name(month))}\n`{table}`"

        await ctx.send(string)

#
# @bot.command(
#     name="register",
#     description="Register to Seven Bot",
#     dm_permission=True,
#
#     options=[
#         interactions.Option(
#             name="email",
#             description="Enter your 7Span email address",
#             type=interactions.OptionType.STRING,
#             required=True
#         )
#     ]
# )
# async def register(ctx: interactions.CommandContext, email: str):
#     try:
#         if ctx.channel.type != discord.ChannelType.private:
#             await ctx.send(messages['dm_kar_bhai'])
#     except:
#         discord_id = str(ctx.user.id)
#         result = clickup.register(email, discord_id)
#         if result == constants.STATUS_NO_CONTENT:
#             await ctx.send(messages['err_no_user_found'])
#         elif result == constants.STATUS_BAD_REQUEST:
#             await ctx.send(messages['err_while_entering_record'])
#         elif result == constants.STATUS_OK:
#             print("OK===")
#             await ctx.send(messages['registered_successfully'])
#             clickup.create_json()
#         else:
#             await ctx.send(messages['something_went_wrong'])


@bot.command(
    name="meme",
    description="To get the meme",
    dm_permission=True,
    options=[
        interactions.Option(
            name="category",
            description="Enter any meme category",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def meme(ctx: interactions.CommandContext, category: str):
    response = requests.get(constants.meme_url + category)
    soup = BeautifulSoup(response.content, 'lxml')
    divs = soup.find_all('div', class_='item-aux-container')
    imgs = []
    for div in divs:
        img = div.find('img')['src']
        if img.startswith('http') and img.endswith('jpeg'):
            imgs.append(img)
    meme = random.choice(imgs)
    urllib.request.urlretrieve(meme, "meme.jpg")
    await ctx.send("LOL")
    embed = discord.Embed(title="MEME", url=meme, color=discord.Color.red(), description="This is testing embed")
    await ctx.channel.send(embeds=embed)
    os.remove('meme.jpg')


@bot.command(
    name="fact",
    description="To get the random fact",
    dm_permission=True
)
async def fact(ctx: interactions.CommandContext):
    try:
        res = requests.get(constants.facts_url, headers={'X-Api-Key': constants.facts_api_key})
        text = res.json()[0]['fact']
        await ctx.send(text)
    except Exception as e:
        print(e)
        await ctx.send(messages['default_quote'])


bot.start()
