# src/api/repositories/mongo_session_repository.py

from datetime import datetime, date
from typing import List

from src.domain.models.models import Message
from src.domain.repositories.session_repository import SessionRepository
from src.infra.db.mongo.db_config import mongo_db

class MongoSessionRepository(SessionRepository):
    async def create_session(self, company_id: str, session_id: str) -> None:
        now = datetime.utcnow()
        session_date_iso = now.date().isoformat()
        filter_doc = {"company_id": company_id, "_id": session_id}
        exists = await mongo_db["sessions"].find_one(filter_doc)
        if not exists:
            await mongo_db["sessions"].insert_one({
                **filter_doc,
                "created_at": now,
                "session_date": session_date_iso,
                "messages": []
            })
            print(f"🗄️  Nova sessão criada: {filter_doc} com session_date={session_date_iso}")
        else:
            print(f"ℹ️  Sessão já existe: {filter_doc}")

    async def add_message(
        self,
        company_id: str,
        session_id: str,
        message: Message
    ) -> None:
        filter_doc = {"company_id": company_id, "_id": session_id}
        msg_doc = message.dict(exclude_none=True)
        update_ops = {"$push": {"messages": msg_doc}}
        result = await mongo_db["sessions"].update_one(
            filter_doc,
            update_ops,
            upsert=True
        )
        print(
            f"🔄 add_message filtro={filter_doc} "
            f"matched={result.matched_count} modified={result.modified_count}"
        )

    async def get_messages(
        self,
        company_id: str,
        session_id: str,
        session_date: date
    ) -> List[Message]:
        filter_doc = {"company_id": company_id, "_id": session_id}
        session = await mongo_db["sessions"].find_one(
            filter_doc,
            projection={"messages": 1, "session_date": 1, "_id": 0}
        )
        if not session:
            return []

        session_date_iso = session["session_date"]
        raw = session.get("messages", [])

        todays = [
            m for m in raw
            if isinstance(m.get("timestamp"), datetime)
               and m["timestamp"].date().isoformat() == session_date_iso
        ]
        todays.sort(key=lambda m: m["timestamp"])
        return [Message(**m) for m in todays]
