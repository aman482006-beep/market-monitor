from app.core.config import settings
from app.services.http import get_json

BASE = "https://bharatstockapi.com/v1"

class BharatStockProvider:
    name = "bharatstock"

    def _headers(self):
        if not settings.bharatstock_api_key:
            raise RuntimeError("BHARATSTOCK_API_KEY is not configured")
        return {"X-API-Key": settings.bharatstock_api_key}

    async def status(self):
        return await get_json(f"{BASE}/status")

    async def stocks(self, page=1, page_size=200):
        return await get_json(f"{BASE}/stocks", headers=self._headers(), params={"page": page, "page_size": page_size, "active_only": "true"})

    async def prices(self, symbol: str, from_date: str | None = None, to_date: str | None = None, page=1, page_size=200):
        params = {"page": page, "page_size": page_size}
        if from_date: params["from"] = from_date
        if to_date: params["to"] = to_date
        return await get_json(f"{BASE}/stocks/{symbol}/prices", headers=self._headers(), params=params)

    async def quotes(self, symbols: list[str]):
        return await get_json(f"{BASE}/stocks/quotes", headers=self._headers(), params={"symbols": ",".join(symbols)})

    async def index_prices(self, index_name: str, from_date: str | None = None):
        params = {"from": from_date} if from_date else {}
        return await get_json(f"{BASE}/indices/{index_name}/prices", headers=self._headers(), params=params)

    async def fii_dii(self, latest: bool = False, from_date: str | None = None, to_date: str | None = None):
        params = {"latest": str(latest).lower()}
        if from_date: params["from"] = from_date
        if to_date: params["to"] = to_date
        return await get_json(f"{BASE}/market/fii-dii", headers=self._headers(), params=params)
