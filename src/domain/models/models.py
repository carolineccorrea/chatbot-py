from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, date

class Message(BaseModel):
    channel: str                    # ex: "telegram", "whatsapp", "webchat"
    user_id: str                    # identificador único do usuário no canal
    sender: str                     # "user" ou "bot"
    text: str
    phone_number: Optional[str] = Field(
        default=None,
        description="Número de telefone do usuário, se compartilhado"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC de quando a mensagem foi criada"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dados extras específicos do canal"
    )

class ChatRequest(BaseModel):
    company_id: str
    session_id: str
    session_date: date = Field(
        default_factory=lambda: datetime.utcnow().date(),
        description="Data UTC da sessão (reset diário)"
    )
    message: Message

class ChatResponse(BaseModel):
    company_id: str
    session_id: str
    messages: List[Message]
