# src/domain/repositories/session_repository.py

from abc import ABC, abstractmethod
from typing import List
from datetime import date

from src.domain.models.models import Message

class SessionRepository(ABC):
    @abstractmethod
    async def create_session(self, company_id: str, session_id: str) -> None:
        """
        Cria um novo registro de sessão se não existir.
        """
        ...

    @abstractmethod
    async def add_message(
        self,
        company_id: str,
        session_id: str,
        message: Message
    ) -> None:
        """
        Adiciona uma mensagem à sessão especificada.
        """
        ...

    @abstractmethod
    async def get_messages(
        self,
        company_id: str,
        session_id: str,
        session_date: date
    ) -> List[Message]:
        """
        Retorna todas as mensagens da sessão para a data informada.
        """
        ...
