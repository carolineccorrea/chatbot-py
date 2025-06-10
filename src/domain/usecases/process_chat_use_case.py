from datetime import datetime
from typing import List
from src.domain.models.models import Message
from src.domain.repositories.session_repository import SessionRepository
from src.infra.rag.rag_pipeline import ask_with_context

MAX_USER_MESSAGES_PER_SESSION = 10

class ProcessChatUseCase:
    def __init__(self, repository: SessionRepository):
        self.repository = repository

    async def execute(
        self,
        company_id: str,
        session_id: str,
        incoming: Message
    ) -> List[Message]:
        history = await self.repository.get_messages(company_id, session_id)

        user_msgs = [m for m in history if m.sender == "user"]
        if len(user_msgs) >= MAX_USER_MESSAGES_PER_SESSION:
            fallback = Message(
                channel=incoming.channel,
                user_id=incoming.user_id,
                sender="bot",
                text="Você atingiu o número máximo de interações nesta sessão.",
                timestamp=datetime.utcnow(),
                metadata={}
            )
            await self.repository.add_message(company_id, session_id, fallback)
            return await self.repository.get_messages(company_id, session_id)

        await self.repository.add_message(company_id, session_id, incoming)

        try:
            result = ask_with_context(incoming.text, session_id)
            reply_text = result.get("answer", "")
        except Exception:
            reply_text = "Desculpe, ocorreu um erro ao processar sua solicitação."

        bot_msg = Message(
            channel=incoming.channel,
            user_id=incoming.user_id,
            sender="bot",
            text=reply_text,
            timestamp=datetime.utcnow(),
            metadata={}
        )

        await self.repository.add_message(company_id, session_id, bot_msg)

        return await self.repository.get_messages(company_id, session_id)
