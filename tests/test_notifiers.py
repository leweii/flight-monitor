# tests/test_notifiers.py
import pytest
from datetime import date
from decimal import Decimal
from src.notifiers.base import BaseNotifier
from src.notifiers.console import ConsoleNotifier
from src.notifiers.wechat import WechatNotifier
from src.notifiers.manager import NotifierManager
from src.models import AlertMessage

@pytest.fixture
def sample_message():
    return AlertMessage(
        route_name="厦门-新加坡",
        origin="XMN",
        destination="SIN",
        departure_date="2026-02-15",
        price=Decimal("750"),
        currency="CNY",
        airline="Xiamen Air",
        rule_type="threshold",
        rule_message="价格 750 <= 阈值 800",
        source="kiwi"
    )

def test_console_notifier_is_enabled():
    notifier = ConsoleNotifier(level="INFO")
    assert notifier.is_enabled() is True
    assert notifier.name == "console"

@pytest.mark.asyncio
async def test_console_notifier_send(sample_message, capsys):
    notifier = ConsoleNotifier(level="INFO")
    result = await notifier.send(sample_message)

    assert result is True


# WeChat Notifier Tests
def test_wechat_notifier_properties():
    notifier = WechatNotifier(push_key="test_key")
    assert notifier.name == "wechat"
    assert notifier.is_enabled() is True


def test_wechat_notifier_disabled_without_key():
    notifier = WechatNotifier(push_key="")
    assert notifier.is_enabled() is False


# NotifierManager Tests
@pytest.mark.asyncio
async def test_notifier_manager_sends_to_all(sample_message):
    console = ConsoleNotifier()

    manager = NotifierManager([console])
    success = await manager.notify_all(sample_message)

    assert "console" in success


@pytest.mark.asyncio
async def test_notifier_manager_skips_disabled(sample_message):
    console = ConsoleNotifier()
    wechat = WechatNotifier(push_key="")  # Disabled

    manager = NotifierManager([console, wechat])
    success = await manager.notify_all(sample_message)

    assert "console" in success
    assert "wechat" not in success
