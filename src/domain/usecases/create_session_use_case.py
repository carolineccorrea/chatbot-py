# src/application/use_cases/create_session_use_case.py
from src.domain.repositories.session_repository import SessionRepository

class CreateSessionUseCase:
    def __init__(self, repository: SessionRepository):
        self.repository = repository

    async def execute(self, company_id: str, session_id: str) -> None:
        """
        Cria uma sessão se não existir.
        """
        await self.repository.create_session(company_id, session_id)
