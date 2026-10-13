# Market Data Quality and Interpretation

This project combines market data from providers with derived analytics. Treat data freshness and provenance as part of the result—not as optional UI decoration.

## Before interpreting a dashboard metric

1. **Check the source timestamp.** A successful API response can still contain stale observations.
2. **Check the market session.** Indian equities have weekends and exchange holidays; an older timestamp is not automatically a provider failure.
3. **Separate observed from derived data.** A last-traded price is an observation; moving averages, breadth, advance/decline, and scanners are calculations over a defined input window.
4. **Confirm the input window.** A 20-day moving average is only meaningful when the underlying series contains the intended 20 trading observations.
5. **Treat missing data as missing.** Do not replace unavailable provider values with zero or invented prices.
6. **Keep units explicit.** Distinguish percentage returns from percentage-point changes, and record the currency and timestamp where relevant.

## Suggested freshness fields

For every market-data response, preserve:

- Provider/source name
- Observation timestamp supplied by the provider
- Retrieval timestamp
- Instrument or index identifier
- Currency and unit, where applicable
- Whether the value is observed or derived

If a provider does not supply a trustworthy observation timestamp, label that limitation rather than implying real-time freshness.

## Practical review checklist

- [ ] Are prices and timestamps from the same instrument and market session?
- [ ] Are missing values represented explicitly?
- [ ] Are calculations tested for empty, short, and malformed input series?
- [ ] Are percentage values and decimal returns clearly distinguished?
- [ ] Does the interface avoid describing end-of-day metrics as tick-by-tick live data?

## Automated checks

The scheduled GitHub Actions workflow runs Python compilation and the API analytics test suite every day, and can also be triggered manually. It checks code health; it does **not** verify provider uptime or guarantee that live market data is current.
