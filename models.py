from sqlalchemy import Column, Integer, String, Float, Date, Text, DateTime, Enum
from sqlalchemy.sql import func
from database import Base
import enum

class DirectionEnum(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    name = Column(String)
    direction = Column(Enum(DirectionEnum), nullable=False)
    quantity = Column(Float)
    price = Column(Float)
    date = Column(Date)
    thesis = Column(Text)
    created_at = Column(DateTime, default=func.now())

class DailySnapshot(Base):
    __tablename__ = "daily_snapshots"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    portfolio_value = Column(Float)
    benchmark_value = Column(Float)
