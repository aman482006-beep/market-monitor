from datetime import date, datetime
from pydantic import BaseModel

class Health(BaseModel):
    status: str
    providers: dict[str, bool]

class Breadth(BaseModel):
    date: date | None
    universe: str
    eligible: int
    above_20_sma: float | None
    above_50_sma: float | None
    above_200_sma: float | None
    advances: int
    declines: int
    ad: int
    new_highs: int
    new_lows: int
    movers_up_20_5d: int
    movers_up_30_5d: int
    up_4_volume: int
    down_4_volume: int

class Regime(BaseModel):
    regime: str
    score: float
    confidence: float
    drivers: list[str]
    calculated_at: datetime

class GlobalQuote(BaseModel):
    symbol: str
    price: float
    change_pct: float | None
    observed_at: datetime
    source: str

class Flow(BaseModel):
    date: date
    fii_net: float
    dii_net: float
    fii_buy: float
    fii_sell: float
    dii_buy: float
    dii_sell: float
    source: str
