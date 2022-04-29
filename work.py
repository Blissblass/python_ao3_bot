from bin.setup import *
from bin.commands import *
from bin.events import *
from bin.tasks import *

# -- SETUP --

database = get_database()
client = get_client()

client.run(TOKEN)

# -----------


