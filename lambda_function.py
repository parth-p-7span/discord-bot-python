from discord.ext import commands, tasks
import discord
import constants

import json

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

client = commands.AutoShardedBot(command_prefix='/', help_command=None, intents=intents, shard_count=5)


@client.event
async def on_ready():
    print(f'{client.user} has Awoken!')


@client.command(name="test")
async def test(ctx):
    print('-------', ctx.channel, '---', type(ctx.channel))
    await ctx.send(f'Tested!')


def lambda_handler(event, context):
    print('Parth Panchal')
    client.run(constants.TOKEN)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }