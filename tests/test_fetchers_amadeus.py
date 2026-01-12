# tests/test_fetchers_amadeus.py
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, patch, MagicMock
from src.fetchers.amadeus import AmadeusFetcher


def test_amadeus_fetcher_source_name():
    fetcher = AmadeusFetcher(client_id="test_id", client_secret="test_secret")
    assert fetcher.source_name == "amadeus"


def test_amadeus_fetcher_is_available():
    fetcher = AmadeusFetcher(client_id="test_id", client_secret="test_secret")
    assert fetcher.is_available() is True


def test_amadeus_fetcher_not_available_without_credentials():
    fetcher = AmadeusFetcher(client_id="", client_secret="")
    assert fetcher.is_available() is False

    fetcher = AmadeusFetcher(client_id="test_id", client_secret="")
    assert fetcher.is_available() is False


def test_amadeus_fetcher_parse_response():
    fetcher = AmadeusFetcher(client_id="test_id", client_secret="test_secret")

    mock_response = {
        "data": [{
            "price": {
                "total": "1299.00",
                "currency": "CNY"
            },
            "itineraries": [{
                "segments": [
                    {
                        "departure": {
                            "iataCode": "XMN",
                            "at": "2026-02-15T08:30:00"
                        },
                        "arrival": {
                            "iataCode": "SIN",
                            "at": "2026-02-15T13:00:00"
                        },
                        "carrierCode": "MF",
                        "number": "851"
                    }
                ]
            }]
        }]
    }

    offers = fetcher._parse_response(mock_response, date(2026, 2, 15))
    assert len(offers) == 1
    assert offers[0].origin == "XMN"
    assert offers[0].destination == "SIN"
    assert offers[0].price == Decimal("1299.00")
    assert offers[0].currency == "CNY"
    assert offers[0].airline == "MF"
    assert offers[0].flight_number == "MF851"
    assert offers[0].stops == 0
    assert offers[0].source == "amadeus"


def test_amadeus_fetcher_parse_connecting_flight():
    fetcher = AmadeusFetcher(client_id="test_id", client_secret="test_secret")

    mock_response = {
        "data": [{
            "price": {"total": "999.00", "currency": "CNY"},
            "itineraries": [{
                "segments": [
                    {
                        "departure": {"iataCode": "XMN", "at": "2026-02-15T08:30:00"},
                        "arrival": {"iataCode": "HKG", "at": "2026-02-15T10:00:00"},
                        "carrierCode": "CX",
                        "number": "123"
                    },
                    {
                        "departure": {"iataCode": "HKG", "at": "2026-02-15T12:00:00"},
                        "arrival": {"iataCode": "SIN", "at": "2026-02-15T15:30:00"},
                        "carrierCode": "CX",
                        "number": "456"
                    }
                ]
            }]
        }]
    }

    offers = fetcher._parse_response(mock_response, date(2026, 2, 15))
    assert len(offers) == 1
    assert offers[0].stops == 1
    assert offers[0].origin == "XMN"
    assert offers[0].destination == "SIN"


def test_amadeus_fetcher_get_sample_dates():
    fetcher = AmadeusFetcher(client_id="test_id", client_secret="test_secret")

    dates = fetcher._get_sample_dates(date(2026, 2, 1), date(2026, 2, 28))
    assert len(dates) <= 10
    assert dates[0] == date(2026, 2, 1)
    # Every 3 days
    assert dates[1] == date(2026, 2, 4)


@pytest.mark.asyncio
async def test_amadeus_fetcher_returns_empty_without_credentials():
    fetcher = AmadeusFetcher(client_id="", client_secret="")
    offers = await fetcher.fetch(
        origin="XMN",
        destination="SIN",
        date_start=date(2026, 2, 1),
        date_end=date(2026, 2, 28)
    )
    assert offers == []
