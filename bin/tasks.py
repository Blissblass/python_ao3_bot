from cProfile import run
from itertools import cycle
from discord.ext import tasks
import discord
from bin.setup import client
from bin.helper_methods import run_loop
import threading

STATUS = cycle([
  'Keeping fandoms alive 24/7!', 
  'Use ^help to see all available commands!',
  'We promise to keep it SFW!',  
  'Use ^help to see all available commands!', 
  'Your secrets are safe with us!',
  'Use ^help to see all available commands!',
  'Use ^help to see all available commands!',
])

@tasks.loop(minutes=5)
async def change_status():
  await client.change_presence(activity=discord.Game(next(STATUS)))   

@tasks.loop(minutes=30)
async def check_update():
  thread = threading.Thread(target=run_loop, args=())
  thread.daemon = True
  thread.start()