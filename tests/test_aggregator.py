# tests/test_aggregator.py
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock
from src.fetchers.aggregator import PriceAggregator
from src.fetchers.base import BaseFetcher
from src.models import FlightOffer

class MockFetcher(BaseFetcher):
    def __init__(self, name: str, offers: list, available: bool = True):
        self._name = name
        self._offers = offers
        self._available = available

    @property
    def source_name(self) -> str:
        return self._name

    async def fetch(self, origin, destination, date_start, date_end):
        return self._offers

    def is_available(self) -> bool:
        return self._available

@pytest.mark.asyncio
async def test_aggregator_combines_results():
    offer1 = FlightOffer("XMN", "SIN", date(2026, 2, 15), Decimal("800"), "CNY", "", "", 0, "mock1")
    offer2 = FlightOffer("XMN", "SIN", date(2026, 2, 15), Decimal("750"), "CNY", "", "", 0, "mock2")

    fetcher1 = MockFetcher("mock1", [offer1])
    fetcher2 = MockFetcher("mock2", [offer2])

    aggregator = PriceAggregator([fetcher1, fetcher2])
    results = await aggregator.fetch_all("XMN", "SIN", date(2026, 2, 15), date(2026, 2, 15))

    assert len(results) == 2

@pytest.mark.asyncio
async def test_aggregator_skips_unavailable():
    offer1 = FlightOffer("XMN", "SIN", date(2026, 2, 15), Decimal("800"), "CNY", "", "", 0, "mock1")

    fetcher1 = MockFetcher("mock1", [offer1])
    fetcher2 = MockFetcher("mock2", [], available=False)

    aggregator = PriceAggregator([fetcher1, fetcher2])
    results = await aggregator.fetch_all("XMN", "SIN", date(2026, 2, 15), date(2026, 2, 15))

    assert len(results) == 1

def test_aggregator_get_best_price():
    offer1 = FlightOffer("XMN", "SIN", date(2026, 2, 15), Decimal("800"), "CNY", "", "", 0, "mock1")
    offer2 = FlightOffer("XMN", "SIN", date(2026, 2, 15), Decimal("750"), "CNY", "", "", 0, "mock2")

    aggregator = PriceAggregator([])
    best = aggregator.get_best_price([offer1, offer2])

    assert best.price == Decimal("750")
