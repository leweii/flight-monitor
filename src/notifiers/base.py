# src/notifiers/base.py
from abc import ABC, abstractmethod
from src.models import AlertMessage

class BaseNotifier(ABC):
    """Base class for notification channels."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def send(self, message: AlertMessage) -> bool:
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        pass
