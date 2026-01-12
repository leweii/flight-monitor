# src/database.py
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, create_engine
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class PriceRecord(Base):
    __tablename__ = 'price_records'

    id = Column(Integer, primary_key=True)
    origin = Column(String(3), nullable=False)
    destination = Column(String(3), nullable=False)
    departure_date = Column(Date, nullable=False)
    source = Column(String(20), nullable=False)
    airline = Column(String(50))
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='CNY')
    flight_number = Column(String(20))
    stops = Column(Integer, default=0)
    fetched_at = Column(DateTime, default=datetime.utcnow)

class AlertLog(Base):
    __tablename__ = 'alert_logs'

    id = Column(Integer, primary_key=True)
    route_name = Column(String(100))
    origin = Column(String(3))
    destination = Column(String(3))
    departure_date = Column(Date)
    trigger_type = Column(String(20))
    trigger_condition = Column(String)
    price = Column(Numeric(10, 2))
    notified_via = Column(ARRAY(String))
    created_at = Column(DateTime, default=datetime.utcnow)

def get_database_url(config: dict, async_mode: bool = True) -> str:
    """Build database URL from config."""
    db = config['database']
    driver = 'postgresql+asyncpg' if async_mode else 'postgresql'
    return f"{driver}://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['name']}"

async def init_database(config: dict):
    """Initialize async database engine and session."""
    url = get_database_url(config, async_mode=True)
    engine = create_async_engine(url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine, async_session
