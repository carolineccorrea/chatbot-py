import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Carrega variáveis definidas no arquivo .env
load_dotenv()

# Lê URI e nome do banco a partir das variáveis de ambiente
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME")

client = AsyncIOMotorClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000  # timeout de 5 segundos
)

mongo_db = client[DB_NAME]