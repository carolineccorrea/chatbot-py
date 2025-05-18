# src/services/chat_service.py

from datetime import datetime
from src.models.models import ChatRequest, ChatResponse, Message
from src.repositories.chat_repository import create_session, add_message, get_session_messages
from src.rag.rag_pipeline import ask_with_context

# Número máximo de mensagens enviadas pelo usuário por sessão
MAX_USER_MESSAGES_PER_SESSION = 10

class ChatService:
    async def create_session(self, session_id: str):
        """
        Cria uma nova sessão no repositório.
        Deve ser chamado apenas em /start-session.
        """
        await create_session(session_id)

    async def process_chat(self, req: ChatRequest, client_ip: str) -> ChatResponse:
        """
        Processa uma mensagem de chat:
         1. Log da recepção
         2. Busca histórico no banco
         3. Conta apenas mensagens de 'user'
         4. Se >= limite, loga e retorna fallback NO FINAL do histórico
         5. Senão, registra a mensagem, chama LLMChain via prompt, registra resposta e retorna histórico atualizado
        """
        # 1) Log de recepção
        print(f"📥 [{client_ip}] -> {req.message}")

        # 2) Recupera todo o histórico salvo
        history = await get_session_messages(req.session_id)

        # 3) Filtra apenas as mensagens do usuário
        user_messages = [m for m in history if m["sender"] == "user"]

        # 4) Se atingiu o limite, loga e retorna fallback ao final
        if len(user_messages) >= MAX_USER_MESSAGES_PER_SESSION:
            print(
                f"⚠️ [{client_ip}] atingiu o limite de "
                f"{MAX_USER_MESSAGES_PER_SESSION} mensagens de usuário na sessão {req.session_id}"
            )
            return ChatResponse(
                session_id=req.session_id,
                messages=[
                    *[Message(**m) for m in history],
                    Message(
                        sender="bot",
                        text="Você atingiu o número máximo de interações nesta sessão.",
                        timestamp=datetime.utcnow()
                    )
                ]
            )

        # 5) Registra a nova mensagem do usuário
        await add_message(req.session_id, "user", req.message)

        # 6) Gera a resposta via prompt + LLMChain
        try:
            rag_result = ask_with_context(req.message, req.session_id)
            bot_response = rag_result["answer"]
        except Exception as e:
            print("❌ Erro LLMChain:", e)
            bot_response = "Desculpe, ocorreu um erro ao processar sua solicitação."

        # 7) Registra a resposta do bot
        await add_message(req.session_id, "bot", bot_response)

        # 8) Recupera o histórico completo atualizado e retorna
        updated_history = await get_session_messages(req.session_id)
        return ChatResponse(
            session_id=req.session_id,
            messages=[Message(**m) for m in updated_history]
        )

    async def process_webhook(self, body: dict):
        """
        Se precisar de webhook, trate aqui.
        """
        return {"status": "ok", "received": body}
