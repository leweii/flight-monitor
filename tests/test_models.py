# tests/test_models.py
import pytest
from datetime import date
from decimal import Decimal
from src.models import FlightOffer

def test_flight_offer_creation():
    offer = FlightOffer(
        origin="XMN",
        destination="SIN",
        departure_date=date(2026, 2, 15),
        price=Decimal("799.00"),
        currency="CNY",
        airline="Xiamen Air",
        flight_number="MF851",
        stops=0,
        source="amadeus"
    )
    assert offer.origin == "XMN"
    assert offer.price == Decimal("799.00")

def test_flight_offer_comparison():
    offer1 = FlightOffer(
        origin="XMN", destination="SIN", departure_date=date(2026, 2, 15),
        price=Decimal("799.00"), currency="CNY", airline="", flight_number="", stops=0, source="amadeus"
    )
    offer2 = FlightOffer(
        origin="XMN", destination="SIN", departure_date=date(2026, 2, 15),
        price=Decimal("899.00"), currency="CNY", airline="", flight_number="", stops=0, source="kiwi"
    )
    assert min([offer1, offer2], key=lambda x: x.price) == offer1
