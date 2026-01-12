# src/scheduler.py
import re
import logging
from datetime import date
from decimal import Decimal
from typing import List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.config import load_config
from src.models import FlightOffer, AlertMessage, AlertResult
from src.fetchers import PriceAggregator, KiwiFetcher, AviationStackFetcher, AmadeusFetcher
from src.analyzers import AlertEngine, ThresholdRule, DropPercentRule, HistoricalLowRule
from src.notifiers import NotifierManager, ConsoleNotifier, WechatNotifier

logger = logging.getLogger(__name__)

class FlightMonitorScheduler:
    """Main scheduler for flight monitoring tasks."""

    def __init__(self, config: dict):
        self.config = config
        self.scheduler = AsyncIOScheduler()
        self.aggregator = self._init_aggregator()
        self.notifier_manager = self._init_notifiers()

    def _init_aggregator(self) -> PriceAggregator:
        fetchers = []
        sources = self.config.get('sources', {})

        if sources.get('amadeus', {}).get('enabled'):
            fetchers.append(AmadeusFetcher(
                client_id=sources['amadeus'].get('client_id', ''),
                client_secret=sources['amadeus'].get('client_secret', '')
            ))

        if sources.get('kiwi', {}).get('enabled'):
            fetchers.append(KiwiFetcher(
                api_key=sources['kiwi'].get('api_key', '')
            ))

        if sources.get('aviationstack', {}).get('enabled'):
            fetchers.append(AviationStackFetcher(
                api_key=sources['aviationstack'].get('api_key', '')
            ))

        return PriceAggregator(fetchers)

    def _init_notifiers(self) -> NotifierManager:
        notifiers = []
        cfg = self.config.get('notifiers', {})

        if cfg.get('console', {}).get('enabled', True):
            notifiers.append(ConsoleNotifier(
                level=cfg.get('console', {}).get('level', 'INFO')
            ))

        if cfg.get('wechat', {}).get('enabled'):
            notifiers.append(WechatNotifier(
                push_key=cfg['wechat'].get('push_key', '')
            ))

        return NotifierManager(notifiers)

    def _parse_interval(self, interval_str: str) -> dict:
        match = re.match(r'(\d+)([hm])', interval_str)
        if not match:
            return {'hours': 1}

        value = int(match.group(1))
        unit = match.group(2)

        if unit == 'h':
            return {'hours': value}
        return {'minutes': value}

    def _build_rules(self, alert_configs: List[dict]) -> List:
        rules = []
        for cfg in alert_configs:
            alert_type = cfg.get('type')
            if alert_type == 'threshold':
                rules.append(ThresholdRule(
                    max_price=Decimal(str(cfg.get('max_price', 0)))
                ))
            elif alert_type == 'drop_percent':
                rules.append(DropPercentRule(
                    percent=cfg.get('percent', 10)
                ))
            elif alert_type == 'historical_low':
                rules.append(HistoricalLowRule(
                    lookback_days=cfg.get('lookback_days', 7)
                ))
        return rules

    def setup_jobs(self):
        for route in self.config.get('routes', []):
            interval = self._parse_interval(route.get('check_interval', '1h'))

            self.scheduler.add_job(
                self._check_route,
                trigger=IntervalTrigger(**interval),
                args=[route],
                id=f"route_{route['origin']}_{route['destination']}",
                name=route['name'],
                replace_existing=True
            )
            logger.info(f"Added job: {route['name']} (every {route.get('check_interval', '1h')})")

    async def _check_route(self, route: dict):
        logger.info(f"Checking: {route['name']}")

        date_range = route.get('date_range', {})
        date_start = date.fromisoformat(date_range.get('start', date.today().isoformat()))
        date_end = date.fromisoformat(date_range.get('end', date_start.isoformat()))

        offers = await self.aggregator.fetch_all(
            route['origin'],
            route['destination'],
            date_start,
            date_end
        )

        if not offers:
            logger.warning(f"{route['name']}: No flight data")
            return

        best = self.aggregator.get_best_price(offers)
        logger.info(f"{route['name']}: Best price {best.price} from {best.source}")

        rules = self._build_rules(route.get('alerts', []))
        engine = AlertEngine(rules)
        alerts = await engine.check(best, None)

        if alerts:
            message = AlertMessage(
                route_name=route['name'],
                origin=best.origin,
                destination=best.destination,
                departure_date=str(best.departure_date),
                price=best.price,
                currency=best.currency,
                airline=best.airline,
                rule_type=alerts[0].rule_type,
                rule_message=alerts[0].message,
                source=best.source
            )
            channels = await self.notifier_manager.notify_all(message)
            logger.info(f"Notified via: {channels}")

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()
