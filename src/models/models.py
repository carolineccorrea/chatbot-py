from pydantic import BaseModel
from typing import List
from datetime import datetime

class Message(BaseModel):
    sender: str  # "user" ou "bot"
    text: str
    timestamp: datetime = None
class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    messages: List[Message]
