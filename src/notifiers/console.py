# src/notifiers/console.py
import logging
from colorama import Fore, Style, init
from src.notifiers.base import BaseNotifier
from src.models import AlertMessage

init()  # Initialize colorama

class ConsoleNotifier(BaseNotifier):
    """Console/logging notification channel."""

    def __init__(self, level: str = "INFO"):
        self.level = level
        self.logger = logging.getLogger("flight-alert")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(getattr(logging, level.upper()))
        self._enabled = True

    @property
    def name(self) -> str:
        return "console"

    def is_enabled(self) -> bool:
        return self._enabled

    async def send(self, msg: AlertMessage) -> bool:
        output = f"""
{Fore.GREEN}{'='*50}
✈️  机票提醒 - {msg.route_name}
{'='*50}{Style.RESET_ALL}
航线: {msg.origin} → {msg.destination}
日期: {msg.departure_date}
价格: {Fore.YELLOW}{msg.price} {msg.currency}{Style.RESET_ALL}
航司: {msg.airline}
来源: {msg.source}
触发: {msg.rule_type} - {msg.rule_message}
{'='*50}
"""
        self.logger.info(output)
        return True
