from os import environ

from dotenv import load_dotenv

load_dotenv('.env')
environ['POSTGRES_HOST'] = 'localhost'
