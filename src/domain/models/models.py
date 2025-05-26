from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime

class Message(BaseModel):
    channel: str                    # ex: "telegram", "whatsapp", "webchat"
    user_id: str                    # identificador único do usuário no canal
    sender: str                     # "user" ou "bot"
    text: str
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC de quando a mensagem foi criada"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dados extras específicos do canal"
    )

class ChatRequest(BaseModel):
    company_id: str                 # identificador da empresa/tenant
    session_id: str
    message: Message

class ChatResponse(BaseModel):
    company_id: str                 # ecoa o mesmo company_id do request
    session_id: str
    messages: List[Message]
