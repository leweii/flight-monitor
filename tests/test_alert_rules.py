# tests/test_alert_rules.py
import pytest
from datetime import date
from decimal import Decimal
from src.analyzers.alert_rules import BaseAlertRule, ThresholdRule, DropPercentRule, HistoricalLowRule
from src.models import FlightOffer

@pytest.fixture
def sample_offer():
    return FlightOffer(
        origin="XMN",
        destination="SIN",
        departure_date=date(2026, 2, 15),
        price=Decimal("750"),
        currency="CNY",
        airline="MF",
        flight_number="MF851",
        stops=0,
        source="kiwi"
    )

@pytest.mark.asyncio
async def test_threshold_rule_triggers(sample_offer):
    rule = ThresholdRule(max_price=Decimal("800"))
    result = await rule.evaluate(sample_offer, None)

    assert result.triggered is True
    assert result.rule_type == "threshold"

@pytest.mark.asyncio
async def test_threshold_rule_not_triggers():
    offer = FlightOffer("XMN", "SIN", date(2026, 2, 15), Decimal("900"), "CNY", "", "", 0, "kiwi")
    rule = ThresholdRule(max_price=Decimal("800"))
    result = await rule.evaluate(offer, None)

    assert result.triggered is False

@pytest.mark.asyncio
async def test_drop_percent_rule_triggers():
    offer = FlightOffer("XMN", "SIN", date(2026, 2, 15), Decimal("800"), "CNY", "", "", 0, "kiwi")
    rule = DropPercentRule(percent=15, last_price=Decimal("1000"))
    result = await rule.evaluate(offer, None)

    assert result.triggered is True  # 20% drop > 15%
    assert "20.0%" in result.message

@pytest.mark.asyncio
async def test_drop_percent_rule_not_triggers():
    offer = FlightOffer("XMN", "SIN", date(2026, 2, 15), Decimal("900"), "CNY", "", "", 0, "kiwi")
    rule = DropPercentRule(percent=15, last_price=Decimal("1000"))
    result = await rule.evaluate(offer, None)

    assert result.triggered is False  # 10% drop < 15%

@pytest.mark.asyncio
async def test_historical_low_rule_triggers():
    offer = FlightOffer("XMN", "SIN", date(2026, 2, 15), Decimal("700"), "CNY", "", "", 0, "kiwi")
    rule = HistoricalLowRule(lookback_days=7, historical_low=Decimal("750"))
    result = await rule.evaluate(offer, None)

    assert result.triggered is True

@pytest.mark.asyncio
async def test_historical_low_rule_not_triggers():
    offer = FlightOffer("XMN", "SIN", date(2026, 2, 15), Decimal("800"), "CNY", "", "", 0, "kiwi")
    rule = HistoricalLowRule(lookback_days=7, historical_low=Decimal("750"))
    result = await rule.evaluate(offer, None)

    assert result.triggered is False
