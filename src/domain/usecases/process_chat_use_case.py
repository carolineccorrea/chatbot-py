# src/application/use_cases/process_chat_use_case.py
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
        # 1) Recupera histórico
        history = await self.repository.get_messages(company_id, session_id)

        # 2) Limite de mensagens do usuário
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
            return [*history, fallback]

        # 3) Persiste mensagem do usuário
        await self.repository.add_message(company_id, session_id, incoming)

        # 4) Gera resposta via RAG/LLM
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
        # 5) Persiste resposta do bot
        await self.repository.add_message(company_id, session_id, bot_msg)

        # 6) Retorna histórico atualizado
        return await self.repository.get_messages(company_id, session_id)