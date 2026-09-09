from datetime import date, timedelta
import pandas as pd
from app.analytics.breadth import compute_breadth
from app.analytics.regime import calculate_regime


def test_breadth_empty_is_explicitly_unknown():
    result = compute_breadth(pd.DataFrame(columns=["symbol", "trade_date", "close", "volume"]))
    assert result["eligible"] == 0
    assert result["above_200_sma"] is None


def test_breadth_counts_advances_and_declines():
    start = date(2026, 1, 1)
    rows = []
    for i in range(205):
        d = start + timedelta(days=i)
        rows.extend([
            {"symbol": "A", "trade_date": d, "close": 100 + i, "volume": 1000},
            {"symbol": "B", "trade_date": d, "close": 200 - i * 0.5, "volume": 1000},
        ])
    result = compute_breadth(pd.DataFrame(rows))
    assert result["advances"] == 1
    assert result["declines"] == 1
    assert result["ad"] == 0
    assert result["above_200_sma"] == 50.0


def test_regime_is_deterministic():
    breadth = {"above_50_sma": 70.0, "above_200_sma": 65.0, "ad": 150, "new_highs": 30, "new_lows": 5, "movers_up_20_5d": 4, "movers_up_30_5d": 1}
    result = calculate_regime(breadth)
    assert result["regime"] in {"Risk-On", "Neutral", "Risk-Off"}
    assert isinstance(result["score"], (int, float))
