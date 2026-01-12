# src/fetchers/base.py
from abc import ABC, abstractmethod
from datetime import date
from typing import List
from src.models import FlightOffer

class BaseFetcher(ABC):
    """Base class for flight data source adapters."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the name of this data source."""
        pass

    @abstractmethod
    async def fetch(
        self,
        origin: str,
        destination: str,
        date_start: date,
        date_end: date
    ) -> List[FlightOffer]:
        """Fetch flight offers for given route and date range."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this fetcher is properly configured and available."""
        pass
