# Stock Screening

**Purpose:** Build a shortlist of candidates worth running through the full analysis pipeline. This file produces a list — not decisions. The user picks which tickers to analyze.

---

## Where to Find Candidates

| Source | What to Look For |
|--------|-----------------|
| **Finviz screener** | Price >$10, avg volume >1M, RSI 40–60, positive EPS growth |
| **TradingView screener** | Price near 50 SMA, recent pullback from highs |
| **StockAnalysis.com** | Revenue growing YoY, positive FCF, P/E below sector avg |
| **Sector rotation** | Which sectors are leading this week? Find laggards in that sector |
| **Earnings calendar** | Stocks reporting in next 2–4 weeks with strong recent momentum |
| **News / analyst upgrades** | Stocks with upgrades, beat-and-raised, or macro tailwind |

---

## Quick Pre-Filter (rule out obvious no-gos)

Before adding a ticker to the list, check:

- [ ] Price above $10 and avg volume above 1M (liquidity)
- [ ] Not in free-fall or blow-off top (chart is readable)
- [ ] Company is real — positive revenue, not a shell or micro-cap gamble
- [ ] There is a reason to look at it now (catalyst, sector move, technical setup, watchlist)

Fails any check → skip it. Don't add it to the list.

---

## Shortlist

When ready to analyze a ticker, run: `fetch_data.py TICKER` and follow `ANALYSIS_PROCESS.md`

| Ticker | Date Added | Industry | Why |
|--------|------------|----------|-----|
| ADBE | 2026-06-11 | Software | Earnings today after close; down 30% YTD on AI fears; options pricing 9% move — beat could trigger sharp bounce from oversold levels |
| MU | 2026-06-11 | Semiconductors | Analyst target raised to $1,100 (currently ~$892, -4.7% today); pullback on strong day = potential entry window |
| MRVL | 2026-06-11 | Semiconductors | AI infrastructure semi, down -5.3% today alongside sector; if pullback is macro-driven not fundamental, entry opportunity |
| AVGO | 2026-06-11 | Semiconductors | Analyst upgrades on hyperscaler design wins; revenue catalyst hitting in H2 2026 — strong fundamental story with sector tailwind |
| META | 2026-06-11 | Social Media / Ad Tech | Multiple analyst upgrades; heavy capex year absorbed without margin damage; quality name pulling back with market |
| PLTR | 2026-06-11 | AI / Enterprise Software | High volatility, predictable mean-reversion swings; AI enterprise/gov story intact; good swing setup when RSI resets |
| NVDA | 2026-06-11 | Semiconductors / AI | ⚠️ Already tracked — entry conditions $203–$208; current price ~$200 is below range; re-check if it reclaims $203 |

---

## Notes

- Keep the list short — 5 to 10 tickers max
- One line per ticker is enough; the pipeline does the deep work
- Remove tickers after analysis is run or after they go stale (>1 week without running)
