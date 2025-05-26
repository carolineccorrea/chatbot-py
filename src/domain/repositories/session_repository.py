# src/domain/repositories/session_repository.py
from abc import ABC, abstractmethod
from typing import List
from src.domain.models.models import Message

class SessionRepository(ABC):
    @abstractmethod
    async def create_session(self, company_id: str, session_id: str) -> None:
        ...

    @abstractmethod
    async def add_message(self, company_id: str, session_id: str, message: Message) -> None:
        ...

    @abstractmethod
    async def get_messages(self, company_id: str, session_id: str) -> List[Message]:
        ...
