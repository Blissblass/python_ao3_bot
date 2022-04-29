import asyncio
import time
import AO3
import discord
from bin.setup import database, client

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


def has_update(workId, work):
  cur = database.cursor()
  cur.execute(f'SELECT chapters FROM WORKS WHERE WORK_ID = { workId }')
  savedWork = cur.fetchone()

  saved_nchapters = savedWork[0]
  newWork_nchapters = work.nchapters
  cur.close()
  return saved_nchapters < newWork_nchapters

async def load_works(work_req):
  threads = []
  works = []

  print(f"Loading {len(work_req)} works...")
  start = time.time()
  for req_work in work_req:
    try:
      work_id = req_work[0]
      work = AO3.Work(work_id, load=False, load_chapters=False)
      work.channel_id = req_work[1]
      work.user_id = req_work[2]
      works.append(work)
      threads.append(work.reload(threaded=True))
    except Exception as e:
      print(e)
      print(f"Exception caught while loading {work_id}... Adding it to the end of the list")
      work_req.append(req_work)
      await asyncio.sleep(10)

  for thread in threads:
    thread.join()

  print(f"Loaded {len(works)} works in {round(time.time() - start, 1)} seconds")
  return works

async def check_all_for_update():
  cur = database.cursor()
  cur.execute('SELECT WORK_ID, CHANNEL_ID, USER_ID FROM WORKS')
  work_req = cur.fetchall()


  if len(work_req) <= 0:
    return print("Database empty...")
    
  works = await asyncio.gather(load_works(work_req))

  for work in works[0]:
    work_id = work.id
    channel_id = work.channel_id
    user_id = work.user_id

    try:
      if has_update(work_id, work):
        print(f'Update found for {work_id}!')
        channel = client.get_channel(channel_id)
        cur = database.cursor()
        cur.execute(f'UPDATE WORKS SET CHAPTERS={work.nchapters} WHERE WORK_ID={work_id}')
        database.commit()
        latest_chapter = work.chapters[work.nchapters - 1]
        text = latest_chapter.text
        summary = ' '.join(text.split(" ")[:100])
        embed = discord.Embed(color=discord.Colour.from_rgb(153, 0, 0), title=f"Update found for {work.title}!")
        embed.add_field(name=f"Sumarry:", value=f"{summary}...", inline=False)
        embed.add_field(name="URL:", value=f"Read this fic over at https://archiveofourown.org/works/{work_id}/chapters/{latest_chapter.id}", inline=False)
        embed.set_thumbnail(url="https://i.imgur.com/q0MqhAe.jpg")
        await channel.send(content=f'<@{user_id}>, update found for { work.title }!', embed = embed)
        cur.close()
      else:
        print(f'No update available for { work_id }...')
    except Exception as e:
      print(f"Exception caught for {work_id}... Adding it to the end of the list.")
      print(e)
      work_req.append(work)
      await asyncio.sleep(10)
      continue

def run_loop():
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)

  loop.run_until_complete(check_all_for_update())
  loop.close()
  
    

  print("Iterated through all works!")