# src/notifiers/manager.py
import asyncio
import logging
from typing import List
from src.notifiers.base import BaseNotifier
from src.models import AlertMessage

logger = logging.getLogger(__name__)


class NotifierManager:
    """Manages multiple notification channels."""

    def __init__(self, notifiers: List[BaseNotifier]):
        self.notifiers = [n for n in notifiers if n.is_enabled()]
        logger.info(f"NotifierManager initialized with {len(self.notifiers)} channels")

    async def notify_all(self, message: AlertMessage) -> List[str]:
        """Send notification to all enabled channels, return successful channel names."""
        success = []

        tasks = [n.send(message) for n in self.notifiers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for notifier, result in zip(self.notifiers, results):
            if result is True:
                success.append(notifier.name)
            elif isinstance(result, Exception):
                logger.error(f"{notifier.name} failed: {result}")
            else:
                logger.warning(f"{notifier.name} returned: {result}")

        return success
