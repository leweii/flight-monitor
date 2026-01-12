# src/fetchers/aggregator.py
import asyncio
import logging
from datetime import date
from typing import List, Optional
from src.fetchers.base import BaseFetcher
from src.models import FlightOffer

logger = logging.getLogger(__name__)

class PriceAggregator:
    """Aggregates results from multiple flight data sources."""

    def __init__(self, fetchers: List[BaseFetcher]):
        self.fetchers = [f for f in fetchers if f.is_available()]
        logger.info(f"Aggregator initialized with {len(self.fetchers)} active fetchers")

    async def fetch_all(
        self,
        origin: str,
        destination: str,
        date_start: date,
        date_end: date
    ) -> List[FlightOffer]:
        """Fetch from all sources concurrently and combine results."""
        tasks = [
            f.fetch(origin, destination, date_start, date_end)
            for f in self.fetchers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_offers = []
        for fetcher, result in zip(self.fetchers, results):
            if isinstance(result, Exception):
                logger.error(f"{fetcher.source_name} error: {result}")
            else:
                all_offers.extend(result)
                logger.info(f"{fetcher.source_name}: {len(result)} offers")

        return all_offers

    def get_best_price(self, offers: List[FlightOffer]) -> Optional[FlightOffer]:
        """Return the offer with lowest price."""
        if not offers:
            return None
        return min(offers, key=lambda x: x.price)
