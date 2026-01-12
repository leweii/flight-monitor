# src/fetchers/aviationstack.py
import httpx
import logging
from datetime import date
from decimal import Decimal
from typing import List
from src.fetchers.base import BaseFetcher
from src.models import FlightOffer

logger = logging.getLogger(__name__)


class AviationStackFetcher(BaseFetcher):
    """AviationStack flight data fetcher.

    Note: AviationStack is primarily a flight tracking API, not a pricing API.
    This fetcher provides flight schedule/availability data. Price information
    may not be available or may be estimated.
    """

    BASE_URL = "http://api.aviationstack.com/v1/flights"

    def __init__(self, api_key: str):
        self.api_key = api_key

    @property
    def source_name(self) -> str:
        return "aviationstack"

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def fetch(
        self,
        origin: str,
        destination: str,
        date_start: date,
        date_end: date
    ) -> List[FlightOffer]:
        if not self.is_available():
            return []

        offers = []

        async with httpx.AsyncClient() as client:
            try:
                # AviationStack uses IATA codes for departure/arrival airports
                params = {
                    "access_key": self.api_key,
                    "dep_iata": origin,
                    "arr_iata": destination,
                    "flight_status": "scheduled",
                    "limit": 100,
                }

                response = await client.get(
                    self.BASE_URL,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                # Check for API errors
                if "error" in data:
                    error_info = data.get("error", {})
                    error_msg = error_info.get("message", "Unknown error")
                    logger.error(f"AviationStack API error: {error_msg}")
                    return []

                offers = self._parse_response(data, date_start, date_end)
                logger.info(f"AviationStack found {len(offers)} flights from {origin} to {destination}")

            except httpx.HTTPStatusError as e:
                logger.error(f"AviationStack HTTP error: {e.response.status_code}")
            except Exception as e:
                logger.error(f"AviationStack API error: {e}")

        return offers

    def _parse_response(
        self,
        data: dict,
        date_start: date,
        date_end: date
    ) -> List[FlightOffer]:
        offers = []

        for item in data.get("data", []):
            try:
                # Extract departure date
                departure_info = item.get("departure", {})
                dep_scheduled = departure_info.get("scheduled", "")

                if not dep_scheduled:
                    continue

                # Parse date from ISO format (e.g., "2026-02-15T10:30:00+00:00")
                dep_date_str = dep_scheduled[:10]
                dep_date = date.fromisoformat(dep_date_str)

                # Filter by date range
                if dep_date < date_start or dep_date > date_end:
                    continue

                # Extract flight info
                flight_info = item.get("flight", {})
                airline_info = item.get("airline", {})
                arrival_info = item.get("arrival", {})

                # AviationStack doesn't provide pricing, so we set price to 0
                # to indicate "price not available from this source"
                offer = FlightOffer(
                    origin=departure_info.get("iata", ""),
                    destination=arrival_info.get("iata", ""),
                    departure_date=dep_date,
                    price=Decimal("0"),  # Price not available from AviationStack
                    currency="CNY",
                    airline=airline_info.get("name", airline_info.get("iata", "")),
                    flight_number=flight_info.get("number", flight_info.get("iata", "")),
                    stops=0,  # AviationStack shows direct flights in this endpoint
                    source=self.source_name
                )
                offers.append(offer)

            except Exception as e:
                logger.warning(f"Failed to parse AviationStack offer: {e}")

        return offers
