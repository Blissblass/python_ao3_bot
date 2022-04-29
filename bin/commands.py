from bin.setup import client
from bin.setup import database
from bin.helper_methods import exists, load_works
import DiscordUtils
import discord
import AO3
import time

allowed_mentions = discord.AllowedMentions(everyone = True) # Allows the bot to mention people


@client.command() 
async def ping(ctx):
  await ctx.send(f'Pong! ({ctx.guild.id} | {type(ctx.guild.id)}, {ctx.channel.id} | {type(ctx.channel.id)}, {ctx.author.id} | {type(ctx.author.id)})')

@client.command()
async def get_id(ctx, url):
  workID = AO3.utils.workid_from_url(url)
  await ctx.send(f"<@{ctx.author.id}>, here's the id you requested! **{workID}**")

@client.command()
async def add_work(ctx, workData):
  await ctx.channel.trigger_typing()
  if workData.startswith("https"):
    workID = AO3.utils.workid_from_url(workData)
  else:
    workID = workData

  try:
   work = AO3.Work(int(workID))
   if exists(workID):
     await ctx.send(f'<@{ctx.author.id}>, work named {work.title} already exists!')  
   else:
     cur = database.cursor()
     cur.execute(f'INSERT INTO WORKS(WORK_ID, CHAPTERS, SERVER_ID, CHANNEL_ID, USER_ID) VALUES ({workID}, {work.nchapters}, {ctx.guild.id}, {ctx.channel.id}, {ctx.author.id})')
     database.commit()
     await ctx.send(f'<@{ctx.author.id}>, work named {work.title} has been saved!')
     cur.close()
  except Exception as e:
    print(e)
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
async def remove_work(ctx, work_id):
  if exists(work_id):
   cur = database.cursor()
   cur.execute(f"DELETE FROM WORKS WHERE work_id={work_id}")
   database.commit()
   await ctx.channel.trigger_typing()
   work = AO3.Work(work_id)
   return await ctx.send(f"<@{ctx.author.id}>, Removed work titled {work.title}!")
  
  await ctx.send(f"<@{ctx.author.id}>, {work_id} is not saved to the database and therefore cannot be removed!")

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
async def get_works(ctx, page=None):
  cur = database.cursor()
  if page:
    limit_start = f"{int(page) - 1}0" # If page is 1, we get first 10, if page is 2, we get first 20
    limit_end = f"{page}0" # If start was 10, we end at 20
    cur.execute(f"SELECT  WORK_ID, CHANNEL_ID, USER_ID FROM WORKS WHERE user_id = {ctx.author.id} LIMIT {limit_end} OFFSET {limit_start}")
  else:
    cur.execute(f'SELECT  WORK_ID, CHANNEL_ID, USER_ID FROM WORKS WHERE user_id = {ctx.author.id}')
  cl_req = cur.fetchall()
  cur.close()

  if len(cl_req) <= 0:
    if page:
      return await ctx.send(f"<@{ctx.author.id}>, this page is empty!")
    else:
      return await ctx.send(f"<@{ctx.author.id}>, you haven't saved any works yet!")
  if len(cl_req) > 10:
    return await ctx.send(f"<@{ctx.author.id}>, it looks like you have a lot of saved works, please choose a page!")
  
  await ctx.channel.trigger_typing()
  works = await load_works(cl_req)

  embeds = []
  paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
  paginator.add_reaction('⏮️', "first")
  paginator.add_reaction('⏪', "back")
  paginator.add_reaction('⏩', "next")
  paginator.add_reaction('⏭️', "last")

  try:
    for work in works:
      work_id = work.id
      channel_id = work.channel_id

      cur_embed = discord.Embed(color=discord.Colour.from_rgb(153, 0, 0), title=work.title)
      cur_embed.add_field(name="Summary:", value=work.summary, inline=False)
      cur_embed.add_field(name="Details:", inline=False, value=f"**ID:** {work_id}, **Chapters:** {work.nchapters}" + (f' **Channel**: <#{channel_id}>\n' if client.get_channel(channel_id) != None else ' **Channel:** <:x:894298558814109788>\n'))
      cur_embed.add_field(name="URL:", value=f"Read this fic at: https://archiveofourown.org/works/{work_id}/", inline=False)
      cur_embed.set_thumbnail(url="https://i.imgur.com/q0MqhAe.jpg")
      embeds.append(cur_embed)
  except Exception as e:
    print(e)
    return await ctx.send(f"<@{ctx.author.id}>, Something went wrong while fetching your works :(")
  
  await ctx.send(f"<@{ctx.author.id}>, here's your saved works!")
  await paginator.run(embeds)  
 
# Help command with descriptions
@client.command()
async def help(ctx):
  embed = discord.Embed(title='Commands!', color=discord.Colour.from_rgb(153, 0, 0), description='')

  embed.add_field(name='get_works <page *optional*>', value='Gets all the works you previously saved! || Splits your saved works into pages of 10 works per page.\n', inline=False)
  embed.add_field(name="get_id <url>", value="Extracts work id from a url!")
  embed.add_field(name='fetch_work <work id>', value='Fetches work directly from AO3, meaning you can also check a work without saving it!\n', inline=False)
  embed.add_field(name='add_work <work id | URL>', value='Saves work so it can be checked for updates! (Use extract_id to get your work id!)\n', inline=False)
  embed.add_field(name='remove_work <work id>', value='Removes your work, meaning it won\'t get checked for updates!\n', inline=False)
  embed.add_field(name="change_notif_channel <work id *optional*>", value="Changes the notification channel for all of your works if an id isn't given! || Changes the notif channel for a specific work")
  await ctx.send(embed=embed)