# Market Monitor

Production-oriented Indian equity market intelligence terminal.

## Architecture

`providers -> ingestion -> PostgreSQL -> analytics -> FastAPI -> Next.js`

## V1 scope

- Indian stock master + EOD OHLC
- NIFTY/SENSEX/NIFTY Smallcap 100 index data
- Global cues
- FII/DII flows
- News ingestion
- 20/50/200 SMA breadth
- Advance/decline
- New highs/lows
- 20%/30% 5-day movers
- 4% + relative-volume movers
- Deterministic market regime
- Basic scanner
- Source + timestamp + freshness status
- OpenAI commentary only from backend facts
- Optional Zerodha Kite Connect adapter

## Real providers

The application uses real external provider adapters. It does not ship fake market values.

### BharatStock
Used for Indian stock metadata, EOD prices, indexes, FII/DII and screening. See `apps/api/app/services/providers/bharatstock.py`.

### Twelve Data
Optional global quote adapter. See `apps/api/app/services/providers/twelvedata.py`.

### NewsAPI
Optional live news discovery. See `apps/api/app/services/providers/newsapi.py`.

### OpenAI
Optional commentary layer. The model receives structured backend facts and must not invent market statistics.

### Zerodha Kite Connect
Optional broker/portfolio adapter. Broker credentials remain server-side.

## Local development

```bash
cp .env.example .env
docker compose up -d postgres redis

cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another shell:

```bash
cd apps/web
npm install
npm run dev
```

API: http://localhost:8000/docs  
Web: http://localhost:3000

## Required configuration

```env
DATABASE_URL=postgresql+psycopg://market:market@localhost:5432/market_monitor
REDIS_URL=redis://localhost:6379/0
BHARATSTOCK_API_KEY=
TWELVEDATA_API_KEY=
NEWSAPI_KEY=
OPENAI_API_KEY=
```

Optional:

```env
KITE_API_KEY=
KITE_API_SECRET=
KITE_ACCESS_TOKEN=
```

## Ingestion

The data pipeline is deliberately separate from the UI.

```bash
python -m app.workers.ingest_cli
python -m app.workers.run_jobs
```

No UI data is generated until the corresponding provider returns real data.
