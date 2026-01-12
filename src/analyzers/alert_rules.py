# src/analyzers/alert_rules.py
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, Any
from src.models import FlightOffer, AlertResult

class BaseAlertRule(ABC):
    """Base class for alert rules."""

    @property
    @abstractmethod
    def rule_type(self) -> str:
        pass

    @abstractmethod
    async def evaluate(self, offer: FlightOffer, db_session: Any) -> AlertResult:
        pass


class ThresholdRule(BaseAlertRule):
    """Triggers when price is below a fixed threshold."""

    def __init__(self, max_price: Decimal, currency: str = "CNY"):
        self.max_price = max_price
        self.currency = currency

    @property
    def rule_type(self) -> str:
        return "threshold"

    async def evaluate(self, offer: FlightOffer, db_session: Any) -> AlertResult:
        triggered = offer.price <= self.max_price
        return AlertResult(
            triggered=triggered,
            rule_type=self.rule_type,
            message=f"价格 {offer.price} {'<=' if triggered else '>'} 阈值 {self.max_price}",
            current_price=offer.price,
            threshold_value=self.max_price
        )


class DropPercentRule(BaseAlertRule):
    """Triggers when price drops by more than X% from last check."""

    def __init__(self, percent: float, last_price: Optional[Decimal] = None):
        self.percent = percent
        self.last_price = last_price  # Injected or fetched from DB

    @property
    def rule_type(self) -> str:
        return "drop_percent"

    async def evaluate(self, offer: FlightOffer, db_session: Any) -> AlertResult:
        if self.last_price is None:
            return AlertResult(
                triggered=False,
                rule_type=self.rule_type,
                message="无历史数据",
                current_price=offer.price
            )

        drop = (self.last_price - offer.price) / self.last_price * 100
        triggered = drop >= self.percent

        return AlertResult(
            triggered=triggered,
            rule_type=self.rule_type,
            message=f"降价 {drop:.1f}%（{self.last_price} → {offer.price}）",
            current_price=offer.price,
            threshold_value=self.last_price * (1 - Decimal(str(self.percent)) / 100)
        )


class HistoricalLowRule(BaseAlertRule):
    """Triggers when price is lower than historical low in lookback period."""

    def __init__(self, lookback_days: int = 7, historical_low: Optional[Decimal] = None):
        self.lookback_days = lookback_days
        self.historical_low = historical_low  # Injected or fetched from DB

    @property
    def rule_type(self) -> str:
        return "historical_low"

    async def evaluate(self, offer: FlightOffer, db_session: Any) -> AlertResult:
        if self.historical_low is None:
            return AlertResult(
                triggered=False,
                rule_type=self.rule_type,
                message="无历史数据",
                current_price=offer.price
            )

        triggered = offer.price < self.historical_low

        return AlertResult(
            triggered=triggered,
            rule_type=self.rule_type,
            message=f"{'新低价！' if triggered else ''}当前 {offer.price} {'<' if triggered else '>='} 历史最低 {self.historical_low}",
            current_price=offer.price,
            threshold_value=self.historical_low
        )
