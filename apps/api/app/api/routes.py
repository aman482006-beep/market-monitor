from datetime import datetime, timezone
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.market import BrokerSession, DailyPrice, GlobalPrice, FiiDiiFlow, NewsArticle, Stock
from app.schemas.market import Health, Breadth, Regime, GlobalQuote, Flow
from app.analytics.breadth import compute_breadth
from app.analytics.regime import calculate_regime
from app.services.ai import explain_market
from app.services.kite import KiteMarketService

router = APIRouter(prefix="/api")

@router.get("/health", response_model=Health)
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1")); db_ok = True
    except Exception:
        db_ok = False
    kite_authenticated = bool(settings.kite_access_token) or db.query(BrokerSession).filter(BrokerSession.broker == "kite").first() is not None
    return Health(status="ok" if db_ok else "degraded", providers={"database": db_ok, "bharatstock": bool(settings.bharatstock_api_key), "twelvedata": bool(settings.twelvedata_api_key), "newsapi": bool(settings.newsapi_key), "openai": bool(settings.openai_api_key), "kite": bool(settings.kite_api_key and kite_authenticated)})

@router.get("/broker/kite/login")
def kite_login():
    try:
        return {"provider": "kite", "login_url": KiteMarketService.login_url()}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

@router.get("/broker/kite/callback")
def kite_callback(request_token: str, db: Session = Depends(get_db)):
    try:
        session = KiteMarketService.create_session(request_token)
        row = db.query(BrokerSession).filter(BrokerSession.broker == "kite").one_or_none()
        values = {"user_id": session.get("user_id"), "access_token": session["access_token"], "created_at": datetime.now(timezone.utc)}
        if row is None:
            db.add(BrokerSession(broker="kite", **values))
        else:
            for key, value in values.items(): setattr(row, key, value)
        db.commit()
        return RedirectResponse(url="/docs#tag/default/operation/live_quotes", status_code=303)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Kite authentication failed: {exc}")

def _breadth_dataframe(db: Session):
    rows = db.execute(select(DailyPrice)).scalars().all()
    return pd.DataFrame([{k: getattr(r, k) for k in ["symbol", "trade_date", "close", "volume"]} for r in rows])

@router.get("/market/breadth", response_model=Breadth)
def breadth(db: Session = Depends(get_db)):
    return Breadth(universe=settings.default_universe, **compute_breadth(_breadth_dataframe(db)))

@router.get("/market/regime", response_model=Regime)
def regime(db: Session = Depends(get_db)):
    return Regime(**calculate_regime(compute_breadth(_breadth_dataframe(db))))

@router.get("/market/global", response_model=list[GlobalQuote])
def global_quotes(db: Session = Depends(get_db)):
    rows = db.execute(select(GlobalPrice).order_by(GlobalPrice.observed_at.desc())).scalars().all(); latest = {}
    for row in rows: latest.setdefault(row.symbol, row)
    return [GlobalQuote(symbol=r.symbol, price=r.price, change_pct=r.change_pct, observed_at=r.observed_at, source=r.source) for r in latest.values()]

@router.get("/market/flows", response_model=list[Flow])
def flows(db: Session = Depends(get_db)):
    rows = db.execute(select(FiiDiiFlow).order_by(FiiDiiFlow.trade_date.desc()).limit(30)).scalars().all()
    return [Flow(date=r.trade_date, fii_net=r.fii_net, dii_net=r.dii_net, fii_buy=r.fii_buy, fii_sell=r.fii_sell, dii_buy=r.dii_buy, dii_sell=r.dii_sell, source=r.source) for r in rows]

@router.get("/market/live")
def live_quotes(symbols: str | None = Query(default=None, description="Comma-separated Kite instruments, e.g. NSE:RELIANCE,NSE:INFY"), db: Session = Depends(get_db)):
    requested = [x.strip() for x in (symbols or settings.kite_symbols).split(",") if x.strip()]
    try:
        return {"status": "LIVE", "data": KiteMarketService(db).quotes(requested), "generated_at": datetime.now(timezone.utc)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))

@router.get("/market/scanners/movers")
def movers(db: Session = Depends(get_db), threshold: float = Query(0.20, ge=0.01, le=2.0), limit: int = Query(25, ge=1, le=100)):
    df = _breadth_dataframe(db)
    if df.empty: return {"date": None, "items": []}
    df = df.sort_values(["symbol", "trade_date"]); df["ret5"] = df.groupby("symbol")["close"].pct_change(5); last_date = df.trade_date.max()
    latest = df[df.trade_date == last_date].dropna(subset=["ret5"]).sort_values("ret5", ascending=False)
    return {"date": last_date, "threshold": threshold, "items": latest[latest.ret5 >= threshold].head(limit)[["symbol", "close", "ret5", "volume"]].to_dict("records")}

@router.get("/market/scanners/volume")
def volume_scanner(db: Session = Depends(get_db), move_pct: float = Query(0.04, ge=0.01, le=1), limit: int = Query(50, ge=1, le=100)):
    df = _breadth_dataframe(db)
    if df.empty: return {"date": None, "items": []}
    df = df.sort_values(["symbol", "trade_date"]); g = df.groupby("symbol"); df["prev_close"] = g.close.shift(1); df["vol20"] = g.volume.transform(lambda s: s.rolling(20, min_periods=20).mean()); df["move"] = df.close / df.prev_close - 1
    last = df[df.trade_date == df.trade_date.max()].copy(); last = last[(last.move.abs() >= move_pct) & (last.volume > last.vol20)].sort_values("move", ascending=False)
    return {"date": df.trade_date.max(), "move_pct": move_pct, "items": last.head(limit)[["symbol", "close", "move", "volume", "vol20"]].to_dict("records")}

@router.get("/market/sectors")
def sectors(db: Session = Depends(get_db)):
    prices = _breadth_dataframe(db); stocks = pd.DataFrame([{"symbol": r.symbol, "sector": r.sector or "Unclassified"} for r in db.execute(select(Stock)).scalars().all()])
    if prices.empty or stocks.empty: return []
    prices = prices.sort_values(["symbol", "trade_date"]); prices["ret1d"] = prices.groupby("symbol").close.pct_change(); latest = prices[prices.trade_date == prices.trade_date.max()].merge(stocks, on="symbol", how="left")
    return latest.groupby("sector", dropna=False).agg(stocks=("symbol", "count"), avg_1d=("ret1d", "mean"), up=("ret1d", lambda s: int((s > 0).sum())), down=("ret1d", lambda s: int((s < 0).sum()))).reset_index().sort_values("avg_1d", ascending=False).to_dict("records")

@router.get("/news")
def news(db: Session = Depends(get_db), limit: int = 50):
    rows = db.execute(select(NewsArticle).order_by(NewsArticle.published_at.desc()).limit(min(limit, 100))).scalars().all()
    return [{"title": r.title, "description": r.description, "content": r.content, "url": r.url, "source": r.source, "published_at": r.published_at, "category": r.category, "importance_score": r.importance_score, "sentiment_score": r.sentiment_score, "market_impact_score": r.market_impact_score} for r in rows]

@router.get("/market/overview")
def overview(db: Session = Depends(get_db)):
    b = breadth(db); r = regime(db); g = global_quotes(db); f = flows(db)
    return {"breadth": b.model_dump(), "regime": r.model_dump(), "global": [x.model_dump() for x in g], "flows": [x.model_dump() for x in f[:5]], "generated_at": datetime.now(timezone.utc)}

@router.get("/market/brief")
async def brief(db: Session = Depends(get_db)):
    data = overview(db)
    try: commentary = await explain_market(data)
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc))
    return {"facts": data, "commentary": commentary}
