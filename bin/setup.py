from dotenv import load_dotenv
import os
import psycopg2

load_dotenv() # Load dotenv to use .env file
TOKEN = os.environ.get('DEV_TOKEN') if os.environ.get('ENV') == 'DEV' else os.environ.get('TOKEN') # Get token from .env file
USERNAME = os.environ.get('DEV_USERNAME') if os.environ.get('ENV') == 'DEV' else os.environ.get('USERNAME')
PASSWORD = os.environ.get('DEV_PASSWORD') if os.environ.get('ENV') == 'DEV' else os.environ.get('PASSWORD')
DATABASE_URL = os.environ.get('DEV_DATABASE_URL') if os.environ.get('ENV') == 'DEV' else os.environ.get('DATABASE_URL')

def setup_database():
  database = psycopg2.connect(DATABASE_URL)
  return database