# tests/test_fetchers_aviationstack.py
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, patch
from src.fetchers.aviationstack import AviationStackFetcher


def test_aviationstack_fetcher_source_name():
    fetcher = AviationStackFetcher(api_key="test_key")
    assert fetcher.source_name == "aviationstack"


def test_aviationstack_fetcher_is_available():
    fetcher = AviationStackFetcher(api_key="test_key")
    assert fetcher.is_available() is True


def test_aviationstack_fetcher_not_available_without_key():
    fetcher = AviationStackFetcher(api_key="")
    assert fetcher.is_available() is False


@pytest.mark.asyncio
async def test_aviationstack_fetcher_parse_response():
    fetcher = AviationStackFetcher(api_key="test_key")

    mock_response = {
        "data": [{
            "flight": {"number": "851", "iata": "MF851"},
            "airline": {"name": "Xiamen Airlines", "iata": "MF"},
            "departure": {
                "iata": "XMN",
                "scheduled": "2026-02-15T10:30:00+00:00"
            },
            "arrival": {
                "iata": "SIN",
                "scheduled": "2026-02-15T14:30:00+00:00"
            },
            "flight_status": "scheduled"
        }]
    }

    offers = fetcher._parse_response(
        mock_response,
        date_start=date(2026, 2, 1),
        date_end=date(2026, 2, 28)
    )

    assert len(offers) == 1
    assert offers[0].origin == "XMN"
    assert offers[0].destination == "SIN"
    assert offers[0].departure_date == date(2026, 2, 15)
    assert offers[0].airline == "Xiamen Airlines"
    assert offers[0].flight_number == "851"
    assert offers[0].source == "aviationstack"
    # AviationStack doesn't provide pricing
    assert offers[0].price == Decimal("0")


@pytest.mark.asyncio
async def test_aviationstack_fetcher_parse_filters_by_date():
    fetcher = AviationStackFetcher(api_key="test_key")

    mock_response = {
        "data": [
            {
                "flight": {"number": "851"},
                "airline": {"name": "Airline A"},
                "departure": {"iata": "XMN", "scheduled": "2026-02-15T10:30:00+00:00"},
                "arrival": {"iata": "SIN", "scheduled": "2026-02-15T14:30:00+00:00"},
            },
            {
                "flight": {"number": "852"},
                "airline": {"name": "Airline B"},
                "departure": {"iata": "XMN", "scheduled": "2026-03-15T10:30:00+00:00"},
                "arrival": {"iata": "SIN", "scheduled": "2026-03-15T14:30:00+00:00"},
            },
        ]
    }

    offers = fetcher._parse_response(
        mock_response,
        date_start=date(2026, 2, 1),
        date_end=date(2026, 2, 28)
    )

    # Only the first flight should be included (within date range)
    assert len(offers) == 1
    assert offers[0].flight_number == "851"


@pytest.mark.asyncio
async def test_aviationstack_fetcher_returns_empty_without_key():
    fetcher = AviationStackFetcher(api_key="")
    offers = await fetcher.fetch(
        origin="XMN",
        destination="SIN",
        date_start=date(2026, 2, 1),
        date_end=date(2026, 2, 28)
    )
    assert offers == []


@pytest.mark.asyncio
async def test_aviationstack_fetcher_handles_api_error():
    fetcher = AviationStackFetcher(api_key="test_key")

    mock_response = {
        "error": {
            "code": "invalid_access_key",
            "message": "Invalid API key"
        }
    }

    # Mock the HTTP client
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        mock_http_response = AsyncMock()
        mock_http_response.raise_for_status = AsyncMock()
        mock_http_response.json.return_value = mock_response
        mock_instance.get.return_value = mock_http_response

        offers = await fetcher.fetch(
            origin="XMN",
            destination="SIN",
            date_start=date(2026, 2, 1),
            date_end=date(2026, 2, 28)
        )

        assert offers == []
