import asyncio
from datetime import date, timedelta
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.ingest import ingest_stock_master, ingest_prices, ingest_global, ingest_flows, ingest_news

async def main():
    db = SessionLocal()
    try:
        if settings.bharatstock_api_key:
            await ingest_stock_master(db)
            start = (date.today() - timedelta(days=390)).isoformat()
            await ingest_prices(db, from_date=start, to_date=date.today().isoformat())
            await ingest_flows(db)
        if settings.twelvedata_api_key:
            await ingest_global(db)
        if settings.newsapi_key:
            await ingest_news(db)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
