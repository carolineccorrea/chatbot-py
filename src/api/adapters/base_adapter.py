# src/interfaces/adapters/base_adapter.py
from abc import ABC, abstractmethod
from src.domain.models.models import Message

class BaseAdapter(ABC):
    @abstractmethod
    async def parse_request(self, payload: dict) -> Message:
        ...

    @abstractmethod
    async def send_response(self, message: Message, reply_text: str) -> None:
        ...
