# create_index.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
client = MongoClient(os.environ["MONGODB_URI"])
db = client.get_default_database()
db.users.create_index("email", unique=True)
print("created index on users.email")
