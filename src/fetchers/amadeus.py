# src/fetchers/amadeus.py
import httpx
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from src.fetchers.base import BaseFetcher
from src.models import FlightOffer

logger = logging.getLogger(__name__)


class AmadeusFetcher(BaseFetcher):
    """Amadeus flight data fetcher with real pricing data."""

    AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
    SEARCH_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None

    @property
    def source_name(self) -> str:
        return "amadeus"

    def is_available(self) -> bool:
        return bool(self.client_id and self.client_secret)

    async def _get_access_token(self, client: httpx.AsyncClient) -> Optional[str]:
        """Get OAuth2 access token from Amadeus."""
        # Return cached token if still valid
        if self._access_token and self._token_expires:
            if datetime.now() < self._token_expires - timedelta(minutes=1):
                return self._access_token

        try:
            response = await client.post(
                self.AUTH_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            self._access_token = data.get("access_token")
            expires_in = data.get("expires_in", 1799)
            self._token_expires = datetime.now() + timedelta(seconds=expires_in)

            logger.debug("Amadeus access token obtained")
            return self._access_token

        except Exception as e:
            logger.error(f"Amadeus auth error: {e}")
            return None

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
            token = await self._get_access_token(client)
            if not token:
                return []

            headers = {"Authorization": f"Bearer {token}"}

            # Amadeus requires specific departure date, so we search day by day
            # But to reduce API calls, we search a few sample dates
            sample_dates = self._get_sample_dates(date_start, date_end)

            for dep_date in sample_dates:
                try:
                    params = {
                        "originLocationCode": origin,
                        "destinationLocationCode": destination,
                        "departureDate": dep_date.isoformat(),
                        "adults": 1,
                        "currencyCode": "CNY",
                        "max": 10,
                    }

                    response = await client.get(
                        self.SEARCH_URL,
                        params=params,
                        headers=headers,
                        timeout=30.0
                    )

                    if response.status_code == 200:
                        data = response.json()
                        day_offers = self._parse_response(data, dep_date)
                        offers.extend(day_offers)
                        logger.info(f"Amadeus found {len(day_offers)} offers for {dep_date}")
                    else:
                        error_data = response.json() if response.content else {}
                        error_msg = error_data.get("error_description", response.status_code)
                        logger.warning(f"Amadeus API error for {dep_date}: {error_msg}")

                except Exception as e:
                    logger.error(f"Amadeus fetch error for {dep_date}: {e}")

        logger.info(f"Amadeus total: {len(offers)} offers from {origin} to {destination}")
        return offers

    def _get_sample_dates(self, date_start: date, date_end: date) -> List[date]:
        """Get sample dates to search (to reduce API calls)."""
        dates = []
        current = date_start
        # Search every 3 days to balance coverage and API limits
        while current <= date_end:
            dates.append(current)
            current += timedelta(days=3)
        return dates[:10]  # Max 10 dates to avoid rate limits

    def _parse_response(self, data: dict, departure_date: date) -> List[FlightOffer]:
        offers = []

        for item in data.get("data", []):
            try:
                price_info = item.get("price", {})
                price = Decimal(str(price_info.get("total", 0)))
                currency = price_info.get("currency", "CNY")

                # Get first segment info
                itineraries = item.get("itineraries", [])
                if not itineraries:
                    continue

                segments = itineraries[0].get("segments", [])
                if not segments:
                    continue

                first_segment = segments[0]
                last_segment = segments[-1]

                # Parse departure date
                dep_str = first_segment.get("departure", {}).get("at", "")[:10]
                dep_date = date.fromisoformat(dep_str) if dep_str else departure_date

                # Get airline and flight info
                carrier = first_segment.get("carrierCode", "")
                flight_num = first_segment.get("number", "")

                offer = FlightOffer(
                    origin=first_segment.get("departure", {}).get("iataCode", ""),
                    destination=last_segment.get("arrival", {}).get("iataCode", ""),
                    departure_date=dep_date,
                    price=price,
                    currency=currency,
                    airline=carrier,
                    flight_number=f"{carrier}{flight_num}",
                    stops=len(segments) - 1,
                    source=self.source_name
                )
                offers.append(offer)

            except Exception as e:
                logger.warning(f"Failed to parse Amadeus offer: {e}")

        return offers
