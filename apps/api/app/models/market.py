from datetime import date, datetime
from sqlalchemy import Date, DateTime, Float, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class Stock(Base):
    __tablename__ = "stocks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255))
    exchange: Mapped[str] = mapped_column(String(20), default="NSE", index=True)
    isin: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    sector: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

class DailyPrice(Base):
    __tablename__ = "daily_prices"
    __table_args__ = (UniqueConstraint("symbol", "trade_date", name="uq_daily_symbol_date"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(40), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    adjusted_close: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(80))
    source_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class IndexPrice(Base):
    __tablename__ = "index_prices"
    __table_args__ = (UniqueConstraint("symbol", "trade_date", name="uq_index_symbol_date"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(80), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(80))
    source_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class GlobalPrice(Base):
    __tablename__ = "global_prices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(80), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    price: Mapped[float] = mapped_column(Float)
    change_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(80))

class FiiDiiFlow(Base):
    __tablename__ = "fii_dii_flows"
    __table_args__ = (UniqueConstraint("trade_date", name="uq_flow_date"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    fii_buy: Mapped[float] = mapped_column(Float)
    fii_sell: Mapped[float] = mapped_column(Float)
    fii_net: Mapped[float] = mapped_column(Float)
    dii_buy: Mapped[float] = mapped_column(Float)
    dii_sell: Mapped[float] = mapped_column(Float)
    dii_net: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(80))
    source_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class NewsArticle(Base):
    __tablename__ = "news_articles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(1000))
    description: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    content: Mapped[str | None] = mapped_column(String(10000), nullable=True)
    url: Mapped[str] = mapped_column(String(2000), unique=True)
    source: Mapped[str] = mapped_column(String(255))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    importance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    market_impact_score: Mapped[float | None] = mapped_column(Float, nullable=True)
