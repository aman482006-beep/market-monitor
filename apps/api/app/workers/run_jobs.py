import asyncio
from datetime import date, timedelta
from app.db.session import SessionLocal
from app.services.ingest import ingest_stock_master, ingest_prices, ingest_global, ingest_flows, ingest_news

async def main():
    db = SessionLocal()
    try:
        await ingest_stock_master(db)
        start = (date.today() - timedelta(days=390)).isoformat()
        await ingest_prices(db, from_date=start, to_date=date.today().isoformat())
        if __import__("app.core.config", fromlist=["settings"]).settings.twelvedata_api_key:
            await ingest_global(db)
        if __import__("app.core.config", fromlist=["settings"]).settings.bharatstock_api_key:
            await ingest_flows(db)
        if __import__("app.core.config", fromlist=["settings"]).settings.newsapi_key:
            await ingest_news(db)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
