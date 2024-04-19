import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv("dbconfig.env")

def connect_db():
    try:
        client = AsyncIOMotorClient(os.environ.get("ATLAS_URI"))
        if client:
            return client
    except Exception as e:
        print(e)