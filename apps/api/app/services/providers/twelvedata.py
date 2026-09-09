from app.core.config import settings
from app.services.http import get_json

class TwelveDataProvider:
    name = "twelvedata"
    base = "https://api.twelvedata.com"

    async def quote(self, symbol: str):
        if not settings.twelvedata_api_key:
            raise RuntimeError("TWELVEDATA_API_KEY is not configured")
        return await get_json(f"{self.base}/quote", params={"symbol": symbol, "apikey": settings.twelvedata_api_key})
