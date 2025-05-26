# src/infra/repositories/mongo_session_repository.py

from datetime import datetime
from typing import List, Dict, Any
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
            print(f"🗄️  Nova sessão criada: {filter_doc}")
        else:
            print(f"ℹ️  Sessão já existe: {filter_doc}")

    async def add_message(
        self,
        company_id: str,
        session_id: str,
        message: Message
    ) -> None:
        filter_doc = {"company_id": company_id, "_id": session_id}
        update_doc = {"$push": {"messages": message.dict()}}
        result = await mongo_db["sessions"].update_one(
            filter_doc,
            update_doc,
            upsert=True
        )
        print(
            f"🔄 add_message filtro={filter_doc} matched={result.matched_count} "
            f"modified={result.modified_count} upserted_id={result.upserted_id}"
        )

    async def get_messages(
        self,
        company_id: str,
        session_id: str
    ) -> List[Message]:
        filter_doc = {"company_id": company_id, "_id": session_id}
        session = await mongo_db["sessions"].find_one(
            filter_doc,
            projection={"messages": 1, "_id": 0}
        )
        raw = session.get("messages", []) if session else []
        return [Message(**m) for m in raw]
