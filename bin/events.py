from bin.setup import client
from bin.events import change_status, check_update

@client.event
async def on_ready():
  print('Logged in as {0.user}'.format(client))
  change_status.start()
  check_update.start()