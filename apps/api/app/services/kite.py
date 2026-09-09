from datetime import datetime, timezone
from kiteconnect import KiteConnect
from app.core.config import settings
from app.models.market import BrokerSession

class KiteMarketService:
    def __init__(self, db=None):
        if not settings.kite_api_key:
            raise RuntimeError("Kite API key is not configured")
        access_token = settings.kite_access_token
        if db is not None:
            session = db.query(BrokerSession).filter(BrokerSession.broker == "kite").one_or_none()
            if session and session.access_token:
                access_token = session.access_token
        if not access_token:
            raise RuntimeError("Kite is not authenticated. Open /api/broker/kite/login first")
        self.kite = KiteConnect(api_key=settings.kite_api_key)
        self.kite.set_access_token(access_token)

    def quotes(self, symbols: list[str]) -> list[dict]:
        payload = self.kite.quote(symbols) if symbols else {}
        observed_at = datetime.now(timezone.utc)
        return [{"symbol": symbol, "instrument_token": quote.get("instrument_token"), "last_price": quote.get("last_price"), "ohlc": quote.get("ohlc"), "volume": quote.get("volume"), "average_price": quote.get("average_price"), "buy_quantity": quote.get("buy_quantity"), "sell_quantity": quote.get("sell_quantity"), "timestamp": quote.get("timestamp") or observed_at, "observed_at": observed_at, "source": "kite_connect"} for symbol, quote in payload.items()]

    def instruments(self, exchange="NSE"):
        return self.kite.instruments(exchange)

    @staticmethod
    def login_url():
        if not settings.kite_api_key:
            raise RuntimeError("Kite API key is not configured")
        return KiteConnect(api_key=settings.kite_api_key).login_url()

    @staticmethod
    def create_session(request_token: str):
        if not settings.kite_api_secret:
            raise RuntimeError("Kite API secret is not configured")
        return KiteConnect(api_key=settings.kite_api_key).generate_session(request_token, api_secret=settings.kite_api_secret)
