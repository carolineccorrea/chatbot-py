from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings

mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
mongo_db = mongo_client[settings.DB_NAME]
