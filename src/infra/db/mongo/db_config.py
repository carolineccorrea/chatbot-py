# src/db/mongo/db_config.py
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# carrega variáveis do .env
load_dotenv()

# lê URI e nome do DB
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME   = os.getenv("MONGODB_DB_NAME")

# conecta ao MongoDB Atlas
client   = AsyncIOMotorClient(MONGO_URI)
mongo_db = client[DB_NAME]
