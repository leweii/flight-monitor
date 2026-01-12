# tests/test_alert_engine.py
import pytest
from datetime import date
from decimal import Decimal
from src.analyzers.engine import AlertEngine
from src.analyzers.alert_rules import ThresholdRule, DropPercentRule
from src.models import FlightOffer

@pytest.fixture
def sample_offer():
    return FlightOffer("XMN", "SIN", date(2026, 2, 15), Decimal("750"), "CNY", "", "", 0, "kiwi")

@pytest.mark.asyncio
async def test_engine_returns_triggered_alerts(sample_offer):
    rules = [
        ThresholdRule(max_price=Decimal("800")),  # Will trigger
        ThresholdRule(max_price=Decimal("700")),  # Won't trigger
    ]

    engine = AlertEngine(rules)
    results = await engine.check(sample_offer, None)

    assert len(results) == 1
    assert results[0].rule_type == "threshold"

@pytest.mark.asyncio
async def test_engine_multiple_triggers(sample_offer):
    rules = [
        ThresholdRule(max_price=Decimal("800")),
        DropPercentRule(percent=10, last_price=Decimal("1000")),  # 25% drop
    ]

    engine = AlertEngine(rules)
    results = await engine.check(sample_offer, None)

    assert len(results) == 2
