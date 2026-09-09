from datetime import datetime, timezone
from kiteconnect import KiteConnect
from app.core.config import settings

class KiteMarketService:
    def __init__(self):
        if not settings.kite_api_key or not settings.kite_access_token:
            raise RuntimeError("Kite live market data is not configured")
        self.kite = KiteConnect(api_key=settings.kite_api_key)
        self.kite.set_access_token(settings.kite_access_token)

    def quotes(self, symbols: list[str]) -> list[dict]:
        if not symbols:
            return []
        payload = self.kite.quote(symbols)
        observed_at = datetime.now(timezone.utc)
        result = []
        for symbol, quote in payload.items():
            result.append({
                "symbol": symbol,
                "instrument_token": quote.get("instrument_token"),
                "last_price": quote.get("last_price"),
                "ohlc": quote.get("ohlc"),
                "volume": quote.get("volume"),
                "average_price": quote.get("average_price"),
                "buy_quantity": quote.get("buy_quantity"),
                "sell_quantity": quote.get("sell_quantity"),
                "timestamp": quote.get("timestamp") or observed_at,
                "observed_at": observed_at,
                "source": "kite_connect",
            })
        return result

    def instruments(self):
        return self.kite.instruments("NSE")
