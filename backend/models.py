from sqlalchemy import Column, Float, Integer, String, ForeignKey, DateTime
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)


class Watchlist(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    # ticker = Column(String, index=True)         # short symbol, e.g. "eth"
    coingecko_id = Column(String, index=True)   # full ID, e.g. "ethereum"


class CryptoPrice(Base):
    __tablename__ = "crypto_prices"
    coin = Column(String, primary_key=True, nullable=False)   # CoinGecko ID (e.g. "ethereum")
    timestamp = Column(DateTime, primary_key=True, nullable=False, default=datetime.utcnow)
    price = Column(Float, nullable=False)
