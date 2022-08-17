import discord
from discord.ext import commands
import os
from Athena import Queries
from config import token
import boto3


intents = discord.Intents.all()
discord.member = True
client = commands.Bot(command_prefix = '!',intents = intents)


#Setup basic client
#Need to learn how to make another file in python and import files from another function later.

@client.event
async def on_ready() -> int:
    print('We have logged in as {0.user}'.format(client));

@client.event
async def on_member_join(member):
    Queries('INSERT INTO yeniry\nVALUES (\'{}\',\'{}\')'.format(member.id,'100'))
    await member.send('Welcome! UwU')


#client cogs to connect other classes from other files and allow them to use discord events.
@client.command()
async def load(ctx,extension):
    client.load_extension(f'cogs.{extension}');

@client.command()
async def unload(ctx,extension):
    client.unload_extension(f'cogs.{extension}');

for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}');


client.run(token);