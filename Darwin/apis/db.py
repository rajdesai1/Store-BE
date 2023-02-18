from pymongo import MongoClient, server_api
from django.conf import settings
import urllib.parse
import certifi

MANGO_JWT_SETTINGS = settings.MANGO_JWT_SETTINGS

password = urllib.parse.quote(MANGO_JWT_SETTINGS['db_pass'])
username = urllib.parse.quote(MANGO_JWT_SETTINGS['db_user'])
db_name = MANGO_JWT_SETTINGS['db_name']
db_host = MANGO_JWT_SETTINGS.get('db_host')

if 'localhost' in db_host:
    mongo_uri = db_host
    client = MongoClient(mongo_uri)
elif 'mongodb+srv' in db_host:
    mongo_uri = db_host
    client = MongoClient(mongo_uri, server_api=server_api.ServerApi('1'), connect=False, tlsCAFile=certifi.where())



database = client[db_name]

auth_collection = MANGO_JWT_SETTINGS['auth_collection'] if 'auth_collection' in MANGO_JWT_SETTINGS else "user_profile"

fields = MANGO_JWT_SETTINGS['fields'] if 'fields' in MANGO_JWT_SETTINGS else ()

jwt_secret = MANGO_JWT_SETTINGS['jwt_secret'] if 'jwt_secret' in MANGO_JWT_SETTINGS else 'secret'

jwt_life = MANGO_JWT_SETTINGS['jwt_life'] if 'jwt_life' in MANGO_JWT_SETTINGS else 7

# secondary_username_field = MANGO_JWT_SETTINGS['secondary_username_field'] if 'secondary_username_field' in MANGO_JWT_SETTINGS and MANGO_JWT_SETTINGS['secondary_username_field'] != 'email' else None

