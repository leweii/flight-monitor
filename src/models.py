# src/models.py
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

@dataclass
class FlightOffer:
    origin: str
    destination: str
    departure_date: date
    price: Decimal
    currency: str
    airline: str
    flight_number: str
    stops: int
    source: str

@dataclass
class AlertMessage:
    route_name: str
    origin: str
    destination: str
    departure_date: str
    price: Decimal
    currency: str
    airline: str
    rule_type: str
    rule_message: str
    source: str

@dataclass
class AlertResult:
    triggered: bool
    rule_type: str
    message: str
    current_price: Decimal
    threshold_value: Optional[Decimal] = None
