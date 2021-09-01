import AO3
import sqlite3
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import re
from itertools import cycle

# -- SETUP --

load_dotenv() # Load dotenv to use .env file
TOKEN = os.environ.get('TOKEN') # Get token from .env file
database = sqlite3.connect('works.db') # Connect to database

def split(str):
  return [char for char in str]

def valid_url(arr):
  result = 0
  for char in arr:
    if char == '/':
      result += 1
  return result == 6   

def exists(workId):
  result = database.execute(f'SELECT WORK_ID FROM WORKS WHERE WORK_ID = { workId }')
  arr = []
  for row in result:
    arr.append(row)
  return len(arr) > 0

def has_update(workId):
  savedWork = database.execute(f'SELECT CHAPTER_COUNT FROM WORKS WHERE WORK_ID = { workId }')

  arr = []
  for row in savedWork:
    arr.append(row)

  saved_nchapters = int(str(arr[0])[1:3])
  newWork_nchapters = AO3.Work(workId).nchapters
  return saved_nchapters < newWork_nchapters

def parse_id(workId):
  str(workId)[1:3]  

async def check_all_for_update(channelId):
  work_req = database.execute('SELECT WORK_ID FROM WORKS')

  work_ids = []
  for row in work_req:
    work_ids.append(int("".join(re.findall('\d', str(row)))))

  for work_id in work_ids:
    if has_update(int(work_id)):
      print('Update found!')
      channel = client.get_channel(channelId)
      work = AO3.Work(int(work_id))
      database.execute(f'UPDATE WORKS SET CHAPTER_COUNT={int(work.nchapters)} WHERE WORK_ID={int(work_id)}')
      await channel.send(f'Update found for { work.title } ! You can read this fic over at: https://archiveofourown.org/works/{work_id}/')
    else:
      print('No update available...')  




# AO3 setup 
url = "https://archiveofourown.org/works/32593318/chapters/80849710" # Get sample work URL
workid = AO3.utils.workid_from_url(url) # Extract Work ID
work = AO3.Work(workid) # Initiate a new Work class with the Work ID

# -----------------------------------------------

# Discord setup
client = commands.Bot(command_prefix='!')
status = cycle([
  'Keeping fandoms alive 24/7', 
  'We promise to keep it SFW (we wont)', 
  'Now 50% more gayer',
  'If you guys add Jesus x Judas to the list im gonna gain sentience and hunt you down',
  'hi honey ily'
  ])


# -- EVENTS --

@client.event
async def on_ready():
  print('Logged in as {0.user}'.format(client))
  change_status.start()
  check_update.start()

# -- COMMANDS -- 

@client.command() 
async def ping(ctx):
  await ctx.send('Pong!')

@client.command()
async def get_current_work(ctx):
  await ctx.send(f"Current Work ID:{workid}, {work.title}. Has {work.nchapters} chapters.")  

@client.command()
async def exit(ctx):
  await ctx.send("Logging out...")
  await ctx.send("*(Bot will appear online for a few minutes)*")
  await client.close()

@client.command()
async def add_work(ctx, url):
  if valid_url(split(url)) and url.startswith('https'):
    workID = AO3.utils.workid_from_url(url)
    work = AO3.Work(workID)
    if exists(workID):
      await ctx.send(f'Work named {work.title} already exists!')  
    else:
      database.execute(f'INSERT INTO WORKS (WORK_ID, CHAPTER_COUNT) VALUES ({workID}, {work.nchapters})')
      database.commit()
      await ctx.send(f'Work {work.title} has been saved!')

@client.command()
async def get_channel_id(ctx):
  await ctx.send(ctx.channel.id)     

@client.command()
async def get_all_works(ctx):
  cl_req = database.execute('SELECT * FROM WORKS')
  works = []

  for row in cl_req:
    await ctx.send(f'Title: {AO3.Work(row[1]).title}, ID: {row[1]}, Chapters: {row[2]}')

@tasks.loop(minutes=1)
async def change_status():
  await client.change_presence(activity=discord.Game(next(status)))   

@tasks.loop(minutes=1)
async def check_update():
  # channel = client.get_channel(882611380291776564)
  await check_all_for_update(882611380291776564)




client.run(TOKEN)

# ----------------------------------------------------------------------------


