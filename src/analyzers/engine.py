# src/analyzers/engine.py
from typing import List, Any
from src.analyzers.alert_rules import BaseAlertRule
from src.models import FlightOffer, AlertResult

class AlertEngine:
    """Evaluates multiple alert rules against flight offers."""

    def __init__(self, rules: List[BaseAlertRule]):
        self.rules = rules

    async def check(self, offer: FlightOffer, db_session: Any) -> List[AlertResult]:
        """Check all rules and return triggered alerts."""
        triggered = []

        for rule in self.rules:
            result = await rule.evaluate(offer, db_session)
            if result.triggered:
                triggered.append(result)

        return triggered
