from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import flask


uri = ""
webhook = os.getenv("MAIN_WEBHOOK")
txidWebhook = os.getenv("TXID_WEBHOOK")
dbClient = MongoClient(uri, server_api=ServerApi('1'))
db=dbClient["users"]
collection=db["127.0.0.1:8000"]
cur=dict(collection.find({})[0])
print(cur)
dbClient.close()