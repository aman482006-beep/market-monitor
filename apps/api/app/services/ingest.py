from datetime import datetime, timezone, date
from sqlalchemy import select
from app.core.config import settings
from app.models.market import DailyPrice, GlobalPrice, FiiDiiFlow, NewsArticle, Stock
from app.services.providers.bharatstock import BharatStockProvider
from app.services.providers.twelvedata import TwelveDataProvider
from app.services.providers.newsapi import NewsApiProvider

async def ingest_stock_master(db):
    p = BharatStockProvider()
    page = 1
    while True:
        payload = await p.stocks(page=page, page_size=200)
        for item in payload.get("data", []):
            symbol = item.get("symbol")
            if not symbol:
                continue
            row = db.execute(select(Stock).where(Stock.symbol == symbol)).scalar_one_or_none()
            values = dict(company_name=item.get("company_name") or symbol, exchange=item.get("exchange") or "NSE", isin=item.get("isin"), sector=item.get("sector"), is_active=bool(item.get("is_active", True)))
            if row is None:
                db.add(Stock(symbol=symbol, **values))
            else:
                for k, v in values.items(): setattr(row, k, v)
        db.commit()
        pagination = payload.get("pagination") or {}
        if page >= int(pagination.get("total_pages", page)):
            break
        page += 1

async def ingest_prices(db, symbols: list[str] | None = None, from_date: str | None = None, to_date: str | None = None):
    p = BharatStockProvider()
    if symbols is None:
        symbols = [r[0] for r in db.query(Stock.symbol).filter(Stock.exchange == "NSE", Stock.is_active.is_(True)).all()]
    for symbol in symbols:
        payload = await p.prices(symbol, from_date, to_date, page_size=200)
        now = datetime.now(timezone.utc)
        for item in payload.get("data", []):
            trade_date = date.fromisoformat(item["trade_date"])
            existing = db.execute(select(DailyPrice).where(DailyPrice.symbol == symbol, DailyPrice.trade_date == trade_date)).scalar_one_or_none()
            values = dict(open=float(item["open"]), high=float(item["high"]), low=float(item["low"]), close=float(item["close"]), adjusted_close=float(item["adjusted_close"]) if item.get("adjusted_close") is not None else None, volume=float(item["volume"]) if item.get("volume") is not None else None, source=p.name, source_timestamp=now)
            if existing is None:
                db.add(DailyPrice(symbol=symbol, trade_date=trade_date, **values))
            else:
                for k, v in values.items(): setattr(existing, k, v)
        db.commit()

async def ingest_global(db):
    p = TwelveDataProvider()
    for symbol in filter(None, [s.strip() for s in settings.global_symbols.split(",")]):
        payload = await p.quote(symbol)
        if not payload.get("price"):
            continue
        db.add(GlobalPrice(symbol=symbol, price=float(payload["price"]), change_pct=float(payload["percent_change"]) if payload.get("percent_change") else None, observed_at=datetime.now(timezone.utc), source=p.name))
    db.commit()

async def ingest_flows(db):
    p = BharatStockProvider()
    payload = await p.fii_dii(latest=False)
    for item in payload.get("data", []):
        trade_date = date.fromisoformat(item["date"])
        existing = db.execute(select(FiiDiiFlow).where(FiiDiiFlow.trade_date == trade_date)).scalar_one_or_none()
        values = dict(fii_buy=float(item["fii_buy"]), fii_sell=float(item["fii_sell"]), fii_net=float(item["fii_net"]), dii_buy=float(item["dii_buy"]), dii_sell=float(item["dii_sell"]), dii_net=float(item["dii_net"]), source=p.name, source_timestamp=datetime.now(timezone.utc))
        if existing is None: db.add(FiiDiiFlow(trade_date=trade_date, **values))
        else:
            for k, v in values.items(): setattr(existing, k, v)
    db.commit()

async def ingest_news(db):
    p = NewsApiProvider()
    payload = await p.search(settings.news_query)
    for item in payload.get("articles", []):
        url = item.get("url")
        published_at = item.get("publishedAt")
        if not url or not published_at:
            continue
        existing = db.execute(select(NewsArticle).where(NewsArticle.url == url)).scalar_one_or_none()
        values = dict(title=item.get("title") or "", description=item.get("description"), content=item.get("content"), source=(item.get("source") or {}).get("name") or "Unknown", published_at=datetime.fromisoformat(published_at.replace("Z", "+00:00")))
        if existing is None: db.add(NewsArticle(url=url, **values))
        else:
            for k, v in values.items(): setattr(existing, k, v)
    db.commit()
