from src.db.mongo.db_config import mongo_db
from datetime import datetime

async def create_session(session_id: str):
    existing = await mongo_db["sessions"].find_one({"_id": session_id})
    if not existing:
        await mongo_db["sessions"].insert_one({
            "_id": session_id,
            "created_at": datetime.utcnow(),
            "messages": []
        })

async def add_message(session_id: str, sender: str, text: str):
    message = {
        "sender": sender,
        "text": text,
        "timestamp": datetime.utcnow()
    }
    await mongo_db["sessions"].update_one(
        {"_id": session_id},
        {"$push": {"messages": message}}
    )

async def get_session_messages(session_id: str):
    session = await mongo_db["sessions"].find_one({"_id": session_id})
    return session.get("messages", []) if session else []
