import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

TIMEOUT = httpx.Timeout(15.0, connect=5.0)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4), retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)))
async def get_json(url: str, *, headers: dict | None = None, params: dict | list[tuple[str, str]] | None = None) -> dict:
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError(f"Expected JSON object from {url}")
        return payload
