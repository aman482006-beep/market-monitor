from datetime import datetime, timezone
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.market import DailyPrice, GlobalPrice, FiiDiiFlow, NewsArticle
from app.schemas.market import Health, Breadth, Regime, GlobalQuote, Flow
from app.analytics.breadth import compute_breadth
from app.analytics.regime import calculate_regime
from app.services.ai import explain_market

router = APIRouter(prefix="/api")

@router.get("/health", response_model=Health)
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return Health(status="ok" if db_ok else "degraded", providers={
        "database": db_ok,
        "bharatstock": bool(settings.bharatstock_api_key),
        "twelvedata": bool(settings.twelvedata_api_key),
        "newsapi": bool(settings.newsapi_key),
        "openai": bool(settings.openai_api_key),
        "kite": bool(settings.kite_api_key and settings.kite_access_token),
    })

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
    rows = db.execute(select(GlobalPrice).order_by(GlobalPrice.observed_at.desc())).scalars().all()
    latest = {}
    for row in rows:
        latest.setdefault(row.symbol, row)
    return [GlobalQuote(symbol=r.symbol, price=r.price, change_pct=r.change_pct, observed_at=r.observed_at, source=r.source) for r in latest.values()]

@router.get("/market/flows", response_model=list[Flow])
def flows(db: Session = Depends(get_db)):
    rows = db.execute(select(FiiDiiFlow).order_by(FiiDiiFlow.trade_date.desc()).limit(30)).scalars().all()
    return [Flow(date=r.trade_date, fii_net=r.fii_net, dii_net=r.dii_net, fii_buy=r.fii_buy, fii_sell=r.fii_sell, dii_buy=r.dii_buy, dii_sell=r.dii_sell, source=r.source) for r in rows]

@router.get("/news")
def news(db: Session = Depends(get_db), limit: int = 50):
    rows = db.execute(select(NewsArticle).order_by(NewsArticle.published_at.desc()).limit(min(limit, 100))).scalars().all()
    return [{"title": r.title, "description": r.description, "content": r.content, "url": r.url, "source": r.source, "published_at": r.published_at, "category": r.category, "importance_score": r.importance_score, "sentiment_score": r.sentiment_score, "market_impact_score": r.market_impact_score} for r in rows]

@router.get("/market/overview")
def overview(db: Session = Depends(get_db)):
    b = breadth(db)
    r = regime(db)
    g = global_quotes(db)
    f = flows(db)
    return {"breadth": b.model_dump(), "regime": r.model_dump(), "global": [x.model_dump() for x in g], "flows": [x.model_dump() for x in f[:5]], "generated_at": datetime.now(timezone.utc)}

@router.get("/market/brief")
async def brief(db: Session = Depends(get_db)):
    data = overview(db)
    try:
        commentary = await explain_market(data)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"facts": data, "commentary": commentary}
