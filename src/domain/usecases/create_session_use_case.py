# src/application/use_cases/create_session_use_case.py

import logging
from src.domain.repositories.session_repository import SessionRepository

logger = logging.getLogger(__name__)

class CreateSessionUseCase:
    def __init__(self, repository: SessionRepository):
        """
        :param repository: instância de SessionRepository (por exemplo, MongoSessionRepository)
        """
        self.repository = repository

    async def execute(self, company_id: str, session_id: str) -> None:
        """
        Cria uma sessão se ela ainda não existir no repositório.
        É idempotente: não lança erro se a sessão já existir.
        """
        try:
            await self.repository.create_session(company_id, session_id)
            logger.debug(f"Sessão garantida: company_id={company_id}, session_id={session_id}")
        except AttributeError:
            logger.warning(
                "CreateSessionUseCase: repositório não implementa create_session(), ignorando criação de sessão."
            )
        except Exception:
            logger.exception(
                f"Erro ao criar sessão: company_id={company_id}, session_id={session_id}"
            )
            raise
