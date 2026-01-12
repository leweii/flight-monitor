# src/main.py
import asyncio
import logging
from src.config import load_config
from src.scheduler import FlightMonitorScheduler

logger = logging.getLogger(__name__)

async def main(config_path: str = 'config.yaml'):
    config = load_config(config_path)

    scheduler = FlightMonitorScheduler(config)
    scheduler.setup_jobs()
    scheduler.start()

    logger.info("🛫 Flight monitor started")

    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        scheduler.stop()
        logger.info("Monitor stopped")

async def check_route_once(origin: str, destination: str, config_path: str = 'config.yaml'):
    from datetime import date, timedelta
    from src.fetchers import PriceAggregator, KiwiFetcher, AviationStackFetcher, AmadeusFetcher

    config = load_config(config_path)
    sources = config.get('sources', {})

    fetchers = []
    if sources.get('amadeus', {}).get('enabled'):
        fetchers.append(AmadeusFetcher(
            client_id=sources['amadeus'].get('client_id', ''),
            client_secret=sources['amadeus'].get('client_secret', '')
        ))

    if sources.get('kiwi', {}).get('enabled'):
        fetchers.append(KiwiFetcher(api_key=sources['kiwi'].get('api_key', '')))

    if sources.get('aviationstack', {}).get('enabled'):
        fetchers.append(AviationStackFetcher(api_key=sources['aviationstack'].get('api_key', '')))

    aggregator = PriceAggregator(fetchers)

    today = date.today()
    offers = await aggregator.fetch_all(origin, destination, today, today + timedelta(days=30))

    if offers:
        best = aggregator.get_best_price(offers)
        print(f"\nBest price: {best.price} {best.currency}")
        print(f"Airline: {best.airline}")
        print(f"Date: {best.departure_date}")
        print(f"Source: {best.source}")
    else:
        print("No flights found")

if __name__ == '__main__':
    asyncio.run(main())
