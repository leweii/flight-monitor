# src/fetchers/kiwi.py
import httpx
import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import List
from src.fetchers.base import BaseFetcher
from src.models import FlightOffer

logger = logging.getLogger(__name__)

class KiwiFetcher(BaseFetcher):
    """Kiwi.com flight data fetcher."""

    BASE_URL = "https://api.tequila.kiwi.com/v2/search"

    def __init__(self, api_key: str):
        self.api_key = api_key

    @property
    def source_name(self) -> str:
        return "kiwi"

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
        headers = {"apikey": self.api_key}

        async with httpx.AsyncClient() as client:
            try:
                params = {
                    "fly_from": origin,
                    "fly_to": destination,
                    "date_from": date_start.strftime("%d/%m/%Y"),
                    "date_to": date_end.strftime("%d/%m/%Y"),
                    "curr": "CNY",
                    "limit": 50,
                    "one_for_city": 0,
                }

                response = await client.get(
                    self.BASE_URL,
                    params=params,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                offers = self._parse_response(data, date_start)

            except Exception as e:
                logger.error(f"Kiwi API error: {e}")

        return offers

    def _parse_response(self, data: dict, departure_date: date) -> List[FlightOffer]:
        offers = []

        for item in data.get("data", []):
            try:
                dep_date = item.get("local_departure", "")[:10]
                offer = FlightOffer(
                    origin=item.get("flyFrom", ""),
                    destination=item.get("flyTo", ""),
                    departure_date=date.fromisoformat(dep_date) if dep_date else departure_date,
                    price=Decimal(str(item.get("price", 0))),
                    currency="CNY",
                    airline=",".join(item.get("airlines", [])),
                    flight_number=item.get("route", [{}])[0].get("flight_no", ""),
                    stops=len(item.get("route", [])) - 1,
                    source=self.source_name
                )
                offers.append(offer)
            except Exception as e:
                logger.warning(f"Failed to parse Kiwi offer: {e}")

        return offers
