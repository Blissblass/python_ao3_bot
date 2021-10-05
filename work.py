import AO3
from discord import user
import psycopg2
import discord
from discord.ext import commands, tasks
import DiscordUtils
from dotenv import load_dotenv
import os
from itertools import cycle

# -- SETUP --

load_dotenv() # Load dotenv to use .env file
TOKEN = os.environ.get('TOKEN') # Get token from .env file
USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
DATABASE_URL = os.environ.get('DATABASE_URL')
# database = psycopg2.connect(f"dbname=ao3_bot user={USERNAME} password={PASSWORD}")
database = psycopg2.connect(DATABASE_URL)

allowed_mentions = discord.AllowedMentions(everyone = True) # Allows the bot to mention people

def split(str):
  return [char for char in str]

def exists(workId):
  try:
    cur = database.cursor()
    cur.execute(f'SELECT WORK_ID FROM WORKS WHERE WORK_ID = { workId }')
    result = cur.fetchone()
    cur.close()
    return result != None
  except:
    database.rollback() 
    return False  


def has_update(workId):
  cur = database.cursor()
  cur.execute(f'SELECT chapters FROM WORKS WHERE WORK_ID = { workId }')
  savedWork = cur.fetchone()

  saved_nchapters = savedWork[0]
  newWork_nchapters = AO3.Work(workId).nchapters
  cur.close()
  return saved_nchapters < newWork_nchapters

async def check_all_for_update():
  cur = database.cursor()
  cur.execute('SELECT WORK_ID, CHANNEL_ID, USER_ID FROM WORKS')
  work_req = cur.fetchall()

  if len(work_req) <= 0:
    return print("Database empty...")
    

  for work in work_req:
    work_id = work[0]
    channel_id = work[1]
    user_id = work[2]
    if has_update(work_id):
      print('Update found!')
      channel = client.get_channel(channel_id)
      work = AO3.Work(work_id)
      cur = database.cursor()
      cur.execute(f'UPDATE WORKS SET CHAPTERS={work.nchapters} WHERE WORK_ID={work_id}')
      database.commit()
      latest_chapter = work.chapters[work.nchapters - 1]
      text = latest_chapter.text
      summary = ' '.join(text.split(" ")[:100])

      embed = discord.Embed(color=discord.Colour.from_rgb(153, 0, 0), title=f"Update found for {work.title}!")
      embed.add_field(name=f"{latest_chapter.title}:", value=f"{summary}...", inline=False)
      embed.add_field(name="URL:", value=f"Read this fic over at https://archiveofourown.org/works/{work_id}/chapters/{latest_chapter.id}", inline=False)
      embed.set_thumbnail(url="https://i.imgur.com/q0MqhAe.jpg")

      await channel.send(content=f'<@{user_id}>, update found for { work.title }!', embed = embed)
      cur.close()
    else:
      print(f'No update available for { work_id }...')  
 
# AO3 setup 

# url = "https://archiveofourown.org/works/32593318/chapters/80849710" # Get sample work URL
# workid = AO3.utils.workid_from_url(url) # Extract Work ID
# work = AO3.Work(workid) # Initiate a new Work class with the Work ID

# -----------------------------------------------

# Discord setup
client = commands.Bot(command_prefix='^', help_command=None)
status = cycle([
  'Keeping fandoms alive 24/7', 
  'Use !help to see all available commands!',
  'We promise to keep it SFW (we wont)',  
  'Use !help to see all available commands!', 
  'Your secrets are safe with us!'
  'Use !help to see all available commands!'
  'Use !help to see all available commands!',
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
  await ctx.send(f'Pong! ({ctx.guild.id} | {type(ctx.guild.id)}, {ctx.channel.id} | {type(ctx.channel.id)}, {ctx.author.id} | {type(ctx.author.id)})')

@client.command()
async def add_work(ctx, workID):
  await ctx.channel.trigger_typing()
  try:
   work = AO3.Work(int(workID))
   if exists(workID):
     await ctx.send(f'Work named {work.title} already exists!')  
   else:
     cur = database.cursor()
     cur.execute(f'INSERT INTO WORKS(WORK_ID, CHAPTERS, SERVER_ID, CHANNEL_ID, USER_ID) VALUES ({workID}, {work.nchapters}, {ctx.guild.id}, {ctx.channel.id}, {ctx.author.id})')
     database.commit()
     await ctx.send(f'Work named {work.title} has been saved!')
     cur.close()
  except:
    database.rollback()
    await ctx.send(content=f"<@{ctx.author.id}>, {workID} is not a valid ID! :( Please try again!", allowed_mentions = allowed_mentions)    

@client.command()
async def fetch_work(ctx, work_id):
  await ctx.channel.trigger_typing()
  if type(int(work_id)) is int and len(work_id) > 0:
    work = AO3.Work(work_id)
    await ctx.channel.trigger_typing()
    cur_embed = discord.Embed(color=discord.Colour.from_rgb(153, 0, 0), title=work.title)
    cur_embed.add_field(name="Summary:", value=work.summary, inline=False)
    cur_embed.add_field(name="Details:", inline=False, value=f"**ID:** {work_id}, **Chapters:** {work.nchapters}")
    cur_embed.add_field(name="URL:", value=f"Read this fic at: https://archiveofourown.org/works/{work.id}/", inline=False)
    cur_embed.set_thumbnail(url="https://i.imgur.com/q0MqhAe.jpg")
    await ctx.send(f"<@{ctx.author.id}>, here's the work you requested!", embed=cur_embed)
  else:
    await ctx.send(f"<@{ctx.author.id}>, Please enter only numbers for the Work ID!")

@client.command()
async def extract_id(ctx, url):
  await ctx.channel.trigger_typing()
  work_id = AO3.utils.workid_from_url(url)
  await ctx.send(f"<@{ctx.author.id}>, Your extracted work_id is: {work_id}")    

@client.command()
async def remove_work(ctx, work_id):
  if exists(work_id):
   cur = database.cursor()
   cur.execute(f"DELETE FROM WORKS WHERE work_id={work_id}")
   database.commit()
   await ctx.channel.trigger_typing()
   work = AO3.Work(work_id)
   return await ctx.send(f"Removed work titled {work.title}!")
  
  await ctx.send(f"<@{ctx.author.id}>, {work_id} is not saved to the database and therefore cannot be removed! Please try again :(")

@client.command()
async def change_notif_channel(ctx, workId=None):
  if workId == None:
     cur = database.cursor()
     cur.execute(f"UPDATE WORKS SET channel_id = {ctx.channel.id} WHERE user_id = {ctx.author.id}")
     database.commit()
     cur.close()
     await ctx.send(f"All works updated for <@{ctx.author.id}>! Now all updates for you will be pinged in <#{ctx.channel.id}>!")
  else:
    cur = database.cursor()
    cur.execute(f"UPDATE WORKS SET channel_id = {ctx.channel.id} WHERE work_id = {workId}")
    database.commit()
    cur.close()
    work = AO3.Work(workId)
    await ctx.send(f"<@{ctx.author.id}>, work titled {work.title} has been updated to ping in <#{ctx.channel.id}>!")

@client.command()
async def get_all_works(ctx):
  cur = database.cursor()
  cur.execute(f'SELECT * FROM WORKS WHERE user_id = {ctx.author.id}')
  cl_req = cur.fetchall()
  cur.close()    
  if len(cl_req) <= 0:
    return await ctx.send(f"<@{ctx.author.id}>, you haven't saved any works yet!") 
  embeds = []
  paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
  paginator.add_reaction('⏮️', "first")
  paginator.add_reaction('⏪', "back")
  paginator.add_reaction('⏩', "next")
  paginator.add_reaction('⏭️', "last")

  await ctx.channel.trigger_typing()
  for row in cl_req:
    work = AO3.Work(row[1])
    cur_embed = discord.Embed(color=discord.Colour.from_rgb(153, 0, 0), title=work.title)
    cur_embed.add_field(name="Summary:", value=work.summary, inline=False)
    cur_embed.add_field(name="Details:", inline=False, value=f"**ID:** {row[1]}, **Chapters:** {row[2]}" + (f' **Channel**: <#{row[4]}>\n' if client.get_channel(row[4]) != None else ' **Channel:** <:x:894298558814109788>\n'))
    cur_embed.add_field(name="URL:", value=f"Read this fic at: https://archiveofourown.org/works/{row[1]}/", inline=False)
    cur_embed.set_thumbnail(url="https://i.imgur.com/q0MqhAe.jpg")
    embeds.append(cur_embed)
  
  await ctx.send(f"<@{ctx.author.id}>, here's all of your saved works!")
  await paginator.run(embeds)  
 
# Help command with descriptions
@client.command()
async def help(ctx):
  embed = discord.Embed(title='Commands!', color=discord.Colour.from_rgb(153, 0, 0), description='')

  embed.add_field(name='get_all_works', value='Gets all the works you previously saved!\n', inline=False)
  embed.add_field(name='fetch_work <work id>', value='Fetches work directly from AO3, meaning you can also check a work without saving it!\n', inline=False)
  embed.add_field(name='add_work <work id>', value='Saves work so it can be checked for updates! (Use extract_id to get your work id!)\n', inline=False)
  embed.add_field(name='remove_work <work id>', value='Unsaves your work, meaning it won\'t get checked for updates!\n', inline=False)
  embed.add_field(name='extract_id <url>', value='Extracts id from an AO3 url!\n', inline=False)
  embed.add_field(name="change_notif_channel <work id *optional*>", value="Changes the notif channel for a specific work || Changes the notification channel for all of your works if an id isn't given!")
  await ctx.send(embed=embed)


@tasks.loop(minutes=5)
async def change_status():
  await client.change_presence(activity=discord.Game(next(status)))   

@tasks.loop(minutes=5)
async def check_update():
  await check_all_for_update()




client.run(TOKEN)

# ----------------------------------------------------------------------------


