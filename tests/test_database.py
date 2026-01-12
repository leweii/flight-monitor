# tests/test_database.py
import pytest
from datetime import date
from decimal import Decimal
from src.database import PriceRecord, AlertLog, Base

def test_price_record_model():
    record = PriceRecord(
        origin="XMN",
        destination="SIN",
        departure_date=date(2026, 2, 15),
        source="amadeus",
        airline="Xiamen Air",
        price=Decimal("799.00"),
        currency="CNY",
        flight_number="MF851",
        stops=0
    )
    assert record.origin == "XMN"
    assert record.price == Decimal("799.00")

def test_alert_log_model():
    log = AlertLog(
        route_name="厦门-新加坡",
        origin="XMN",
        destination="SIN",
        departure_date=date(2026, 2, 15),
        trigger_type="threshold",
        trigger_condition="price <= 800",
        price=Decimal("799.00"),
        notified_via=["console", "wechat"]
    )
    assert log.trigger_type == "threshold"
