from datetime import datetime
from app.models.models import ChatRequest, ChatResponse, Message
from app.repositories.chat_repository import (
    create_session,
    add_message,
    get_session_messages
)
from app.rag.rag_pipeline import ask_with_context

MAX_MESSAGES_PER_SESSION = 5  # ou outro limite que você queira

class ChatService:
    async def create_session(self, session_id: str):
        await create_session(session_id)

    async def process_chat(self, req: ChatRequest) -> ChatResponse:
        await self.create_session(req.session_id)

        messages = await get_session_messages(req.session_id)
        user_messages = [m for m in messages if m["sender"] == "user"]

        # Encerra caso tenha ultrapassado o número de interações
        if len(user_messages) >= MAX_MESSAGES_PER_SESSION:
            closing_message = Message(
                sender="bot",
                text="Seu tempo limite de uso do bot foi atingido. Até mais!",
                timestamp=datetime.utcnow()
            )

            # Só adiciona a mensagem final se ainda não estiver no histórico
            if not any("tempo limite" in m["text"].lower() for m in messages if m["sender"] == "bot"):
                await add_message(req.session_id, "bot", closing_message.text)

            updated = await get_session_messages(req.session_id)
            return ChatResponse(
                session_id=req.session_id,
                messages=[Message(**m) for m in updated]
            )

        await add_message(req.session_id, "user", req.message)

        try:
            rag_result = ask_with_context(req.message, req.session_id)
            bot_response = rag_result["answer"]
        except Exception as e:
            print("❌ Erro com LangChain:", e)
            bot_response = "Desculpe, ocorreu um erro ao consultar a base de conhecimento."

        await add_message(req.session_id, "bot", bot_response)

        updated_history = await get_session_messages(req.session_id)
        return ChatResponse(
            session_id=req.session_id,
            messages=[Message(**m) for m in updated_history]
        )
