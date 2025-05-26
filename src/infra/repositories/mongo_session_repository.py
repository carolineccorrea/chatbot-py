# src/infrastructure/repositories/mongo_session_repository.py
from datetime import datetime
from typing import List
from src.domain.models.models import Message
from src.domain.repositories.session_repository import SessionRepository
from src.infra.db.mongo.db_config import mongo_db

class MongoSessionRepository(SessionRepository):
    async def create_session(self, company_id: str, session_id: str) -> None:
        filter_doc = {"company_id": company_id, "_id": session_id}
        exists = await mongo_db["sessions"].find_one(filter_doc)
        if not exists:
            await mongo_db["sessions"].insert_one({
                **filter_doc,
                "created_at": datetime.utcnow(),
                "messages": []
            })

    async def add_message(
        self, company_id: str, session_id: str, message: Message
    ) -> None:
        doc = message.dict()
        await mongo_db["sessions"].update_one(
            {"company_id": company_id, "_id": session_id},
            {"$push": {"messages": doc}}
        )

    async def get_messages(
        self, company_id: str, session_id: str
    ) -> List[Message]:
        session = await mongo_db["sessions"].find_one(
            {"company_id": company_id, "_id": session_id},
            projection={"messages": 1, "_id": 0}
        )
        raw = session.get("messages", []) if session else []
        return [Message(**m) for m in raw]