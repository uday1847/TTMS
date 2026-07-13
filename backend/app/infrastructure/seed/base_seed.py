from abc import ABC, abstractmethod
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.settings import Settings

logger = logging.getLogger("ttms.seed")


class SeedContext:
    """
    Context container holding runtime dependencies and configuration shared
    among all seeding operations.
    """
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings


class BaseSeed(ABC):
    """
    Abstract Base Class for modular database seeding scripts in the application.
    All domain seeds must extend this class and implement the `run` method.
    """
    def __init__(self, context: SeedContext) -> None:
        self.context = context
        self.logger = logger

    @abstractmethod
    async def run(self) -> None:
        """
        Executes the seeding logic. Must be overridden by subclasses.
        """
        pass
