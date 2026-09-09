from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.services.http import get_json

class NewsApiProvider:
    name = "newsapi"
    base = "https://newsapi.org/v2"

    async def search(self, q: str, page_size: int = 50):
        if not settings.newsapi_key:
            raise RuntimeError("NEWSAPI_KEY is not configured")
        now = datetime.now(timezone.utc)
        frm = now - timedelta(hours=24)
        return await get_json(
            f"{self.base}/everything",
            headers={"X-Api-Key": settings.newsapi_key},
            params={"q": q, "from": frm.isoformat(), "to": now.isoformat(), "language": "en", "sortBy": "publishedAt", "pageSize": min(page_size, 100)},
        )
