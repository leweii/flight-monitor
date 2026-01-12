# tests/test_fetchers_kiwi.py
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, patch
from src.fetchers.kiwi import KiwiFetcher

def test_kiwi_fetcher_source_name():
    fetcher = KiwiFetcher(api_key="test_key")
    assert fetcher.source_name == "kiwi"

def test_kiwi_fetcher_is_available():
    fetcher = KiwiFetcher(api_key="test_key")
    assert fetcher.is_available() is True

def test_kiwi_fetcher_not_available_without_key():
    fetcher = KiwiFetcher(api_key="")
    assert fetcher.is_available() is False

@pytest.mark.asyncio
async def test_kiwi_fetcher_parse_response():
    fetcher = KiwiFetcher(api_key="test_key")

    mock_response = {
        "data": [{
            "flyFrom": "XMN",
            "flyTo": "SIN",
            "local_departure": "2026-02-15T10:00:00.000Z",
            "price": 799,
            "airlines": ["MF"],
            "route": [{"flight_no": "MF851"}],
        }]
    }

    offers = fetcher._parse_response(mock_response, date(2026, 2, 15))
    assert len(offers) == 1
    assert offers[0].price == Decimal("799")
    assert offers[0].source == "kiwi"
