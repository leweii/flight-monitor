# tests/test_integration.py
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from src.scheduler import FlightMonitorScheduler
from src.models import FlightOffer

@pytest.fixture
def sample_config():
    return {
        'database': {'host': 'localhost', 'port': 5432, 'name': 'test', 'user': 'test', 'password': 'test'},
        'sources': {
            'kiwi': {'enabled': True, 'api_key': 'test_key'}
        },
        'notifiers': {
            'console': {'enabled': True, 'level': 'INFO'}
        },
        'routes': [
            {
                'name': '测试航线',
                'origin': 'XMN',
                'destination': 'SIN',
                'check_interval': '1h',
                'date_range': {'start': '2026-02-01', 'end': '2026-02-28'},
                'alerts': [{'type': 'threshold', 'max_price': 800}]
            }
        ]
    }

def test_scheduler_init(sample_config):
    scheduler = FlightMonitorScheduler(sample_config)
    assert scheduler.aggregator is not None
    assert scheduler.notifier_manager is not None

def test_scheduler_setup_jobs(sample_config):
    scheduler = FlightMonitorScheduler(sample_config)
    scheduler.setup_jobs()

    jobs = scheduler.scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0].name == '测试航线'

@pytest.mark.asyncio
async def test_full_check_flow(sample_config):
    scheduler = FlightMonitorScheduler(sample_config)

    mock_offer = FlightOffer(
        origin="XMN", destination="SIN",
        departure_date=date(2026, 2, 15),
        price=Decimal("750"), currency="CNY",
        airline="Test Air", flight_number="TA123",
        stops=0, source="mock"
    )

    with patch.object(scheduler.aggregator, 'fetch_all', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = [mock_offer]

        route = sample_config['routes'][0]
        await scheduler._check_route(route)

        mock_fetch.assert_called_once()
