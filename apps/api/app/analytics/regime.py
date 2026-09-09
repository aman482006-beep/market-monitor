from datetime import datetime, timezone


def calculate_regime(b: dict) -> dict:
    components: list[tuple[float, float, str]] = []

    breadth_inputs = [
        ("above_20_sma", 0.25, "Short-term breadth"),
        ("above_50_sma", 0.25, "Medium-term breadth"),
        ("above_200_sma", 0.20, "Long-term breadth"),
    ]
    for key, weight, label in breadth_inputs:
        value = b.get(key)
        if value is not None:
            components.append((max(0.0, min(100.0, float(value))), weight, label))

    eligible = int(b.get("eligible") or 0)
    if eligible:
        ad_ratio = (float(b.get("advances", 0)) / eligible) * 100.0
        components.append((max(0.0, min(100.0, ad_ratio)), 0.10, "Advance/decline"))
        high = float(b.get("new_highs", 0))
        low = float(b.get("new_lows", 0))
        components.append((50.0 if high + low == 0 else 100.0 * high / (high + low), 0.20, "New highs/lows"))

    if not components:
        raise RuntimeError("Insufficient data for regime calculation")

    total_weight = sum(weight for _, weight, _ in components)
    score = sum(value * weight for value, weight, _ in components) / total_weight
    regime = "RISK_ON" if score >= 60 else "NEUTRAL" if score >= 40 else "RISK_OFF"
    drivers = [f"{label}: {value:.1f}/100" for value, _, label in components if (regime == "RISK_OFF" and value < 40) or (regime == "RISK_ON" and value >= 60)]
    agreement = sum((value < 40 if regime == "RISK_OFF" else value >= 60) for value, _, _ in components)
    confidence = min(100.0, 50.0 + 50.0 * agreement / len(components))
    return {
        "regime": regime,
        "score": round(score, 2),
        "confidence": round(confidence, 2),
        "drivers": drivers or ["Signals are mixed; regime remains neutral."],
        "calculated_at": datetime.now(timezone.utc),
    }
