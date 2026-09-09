# Market Monitor

Production-oriented Indian equity market intelligence terminal.

`providers -> ingestion -> PostgreSQL -> analytics -> FastAPI -> Next.js`

## Implemented

- Real BharatStock Indian equity/EOD/FII-DII integration
- Optional Twelve Data global quotes
- Optional NewsAPI news ingestion
- Optional OpenAI fact-grounded commentary
- Real Zerodha Kite Connect authentication + live quote endpoint
- PostgreSQL persistence with explicit source timestamps
- 20/50/200 SMA breadth
- Advance/decline and new highs/lows
- 20%/30% five-day movers
- 4% + relative-volume scanner
- Sector performance endpoint
- Deterministic Risk-On / Neutral / Risk-Off engine
- FastAPI health/status endpoints
- Next.js dashboard
- Docker Compose local stack
- GitHub Actions CI
- Analytics tests

The application does not contain seeded fake market prices. If a provider is not configured, its data is unavailable rather than fabricated.

## Real provider references

BharatStock exposes Indian stock prices, index prices and FII/DII data through its documented API. Kite Connect provides historical market data and live WebSocket/quote APIs; the application keeps Kite credentials server-side. urlBharatStock API referencehttps://bharatstockapi.com/reference urlKite Connect API docshttps://kite.trade/docs/connect/v3/

## Fastest local setup

```bash
cp .env.example .env
# Put your real provider keys in .env
docker compose up --build
```

Then:

- Dashboard: `http://localhost:3000`
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

The `ingest` container runs the historical/EOD/news/global ingestion job once. Re-run it whenever you want a fresh backfill:

```bash
docker compose run --rm ingest
```

## Provider configuration

At minimum for Indian market data:

```env
BHARATSTOCK_API_KEY=your_real_key
```

For global cues/news/AI commentary:

```env
TWELVEDATA_API_KEY=your_real_key
NEWSAPI_KEY=your_real_key
OPENAI_API_KEY=your_real_key
```

## Live Zerodha quotes

Kite Connect requires a server-side API key/secret and login redirect. The application exposes:

```text
GET /api/broker/kite/login
GET /api/broker/kite/callback?request_token=...
GET /api/market/live
```

1. Configure `KITE_API_KEY`, `KITE_API_SECRET` and `KITE_REDIRECT_URL`.
2. Open `/api/broker/kite/login` and follow the returned login URL.
3. Kite redirects to the configured callback.
4. The callback stores the access token in PostgreSQL; it is not exposed in the dashboard.
5. `/api/market/live` then returns current quotes from Kite.

Kite access tokens are broker-session credentials and expire according to Kite's authentication rules, so re-authentication may be required.

## Manual development

API:

```bash
cd apps/api
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Web:

```bash
cd apps/web
npm install
npm run dev
```

## Tests

```bash
cd apps/api
pytest -q
```

CI also runs Python compilation and the analytics test suite on pushes and pull requests.

## Important production rule

"Live" is not the same thing as "every metric is tick-by-tick." Kite can provide live quotes, while breadth, SMA percentages, FII/DII and many scanner metrics are calculated from the appropriate EOD/intraday datasets. The UI should always display the provider timestamp/freshness rather than pretending stale data is live.
