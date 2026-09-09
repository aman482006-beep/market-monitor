import pandas as pd


def compute_breadth(df: pd.DataFrame) -> dict:
    required = {"symbol", "trade_date", "close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df.empty:
        return {"date": None, "eligible": 0, "above_20_sma": None, "above_50_sma": None, "above_200_sma": None, "advances": 0, "declines": 0, "ad": 0, "new_highs": 0, "new_lows": 0, "movers_up_20_5d": 0, "movers_up_30_5d": 0, "up_4_volume": 0, "down_4_volume": 0}
    work = df.copy().sort_values(["symbol", "trade_date"])
    g = work.groupby("symbol", group_keys=False)
    for n in (20, 50, 200):
        work[f"sma{n}"] = g["close"].transform(lambda s, n=n: s.rolling(n, min_periods=n).mean())
    work["prev_close"] = g["close"].shift(1)
    work["ret5"] = g["close"].pct_change(5)
    if "volume" in work.columns:
        work["vol20"] = g["volume"].transform(lambda s: s.rolling(20, min_periods=20).mean())
    else:
        work["volume"] = pd.NA
        work["vol20"] = pd.NA
    last_date = work["trade_date"].max()
    latest = work[work["trade_date"] == last_date].copy()
    eligible = len(latest)

    def pct(mask):
        valid = mask.dropna() if hasattr(mask, "dropna") else mask
        denom = int(valid.shape[0]) if hasattr(valid, "shape") else eligible
        return round(float(mask.sum() / eligible * 100), 2) if eligible else None

    highs = lows = 0
    for _, h in work.groupby("symbol"):
        h = h.sort_values("trade_date")
        if len(h) >= 253:
            previous = h.iloc[-253:-1]
            highs += int(h.iloc[-1].close >= previous.close.max())
            lows += int(h.iloc[-1].close <= previous.close.min())

    up_volume = (latest["close"] / latest["prev_close"] - 1 >= 0.04) & (latest["volume"].fillna(0) > latest["vol20"].fillna(float("inf")))
    down_volume = (latest["close"] / latest["prev_close"] - 1 <= -0.04) & (latest["volume"].fillna(0) > latest["vol20"].fillna(float("inf")))
    advances = int((latest["close"] > latest["prev_close"]).sum())
    declines = int((latest["close"] < latest["prev_close"]).sum())
    return {
        "date": last_date,
        "eligible": eligible,
        "above_20_sma": round(float((latest["close"] > latest["sma20"]).sum() / eligible * 100), 2) if eligible else None,
        "above_50_sma": round(float((latest["close"] > latest["sma50"]).sum() / eligible * 100), 2) if eligible else None,
        "above_200_sma": round(float((latest["close"] > latest["sma200"]).sum() / eligible * 100), 2) if eligible else None,
        "advances": advances,
        "declines": declines,
        "ad": advances - declines,
        "new_highs": highs,
        "new_lows": lows,
        "movers_up_20_5d": int((latest["ret5"] >= 0.20).sum()),
        "movers_up_30_5d": int((latest["ret5"] >= 0.30).sum()),
        "up_4_volume": int(up_volume.sum()),
        "down_4_volume": int(down_volume.sum()),
    }
