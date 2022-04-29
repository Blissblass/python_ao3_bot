import AO3
from discord import user
import discord
from discord.ext import commands, tasks
from itertools import cycle
from bin.helper_methods import check_all_for_update
from bin.setup import *
from bin.commands import *

# -- SETUP --

database = get_database()
client = get_client()

# Discord setup
status = cycle([
  'Keeping fandoms alive 24/7!', 
  'Use ^help to see all available commands!',
  'We promise to keep it SFW!',  
  'Use ^help to see all available commands!', 
  'Your secrets are safe with us!',
  'Use ^help to see all available commands!',
  'Use ^help to see all available commands!',
])


# -- EVENTS --

@client.event
async def on_ready():
  print('Logged in as {0.user}'.format(client))
  change_status.start()
  check_update.start()

# -- COMMANDS -- 

@tasks.loop(minutes=5)
async def change_status():
  await client.change_presence(activity=discord.Game(next(status)))   

@tasks.loop(minutes=30)
async def check_update():
  await check_all_for_update()




client.run(TOKEN)

# ----------------------------------------------------------------------------


