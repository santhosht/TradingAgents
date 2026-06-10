# AMD Analysis Summary
**Run:** AMD_20260605_131722 | **Mode:** Deep | **Date:** 2026-06-05

| Parameter     | Value |
|---------------|-------|
| Signal        | BUY (two-tranche limit) |
| Rating        | Overweight |
| Entry         | T1: $499–510 (1.0%); T2: $480–490 (0.5%, only if AMD closes <$499) |
| Secondary entry| $480–490 (0.5%, only if AMD closes below $499) |
| Breakout entry| $549–555 on close >$546 vol >35M (cancel both limits if triggered) |
| Stop Loss     | $456 (hard intraday — all tranches) |
| Target 1      | $620 (3 months — Q2 beat + EPS reacceleration) |
| Target 2      | $665 (6 months — MI300X ramp + EPYC + analyst upgrades) |
| R:R           | 2.35:1 (T1) / 4.66:1 (T2) |
| Position Size | 1.5% total (max 2.0%) |
| Confidence    | Medium |
| Mode          | Deep |
| Report dir    | reports/AMD_20260605_131722/ |

## Files
| File | Agent |
|------|-------|
| 1_analysts/market.md | Technicals — RSI 67, MACD near zero, EMA 10 at $503, 2-day pullback |
| 1_analysts/sentiment.md | Mixed 4.8/10 — Jobs strong confirmed, Barrons bearish, 6:5 bull/bear |
| 1_analysts/news.md | AMD upgrade positive; chip selloff 2nd day + Barrons double-headline negative |
| 1_analysts/fundamentals.md | FCF $2.566B record; hawkish rates compress 40× P/E; >$100M insider selling |
| 2_research/bull.md | Limit filling = trade working; TSMC demand intact; MU HBM sold out |
| 2_research/bear.md | Rate math: 35× on $13.01 = $455; Barrons institutional effect 2-3 days |
| 2_research/manager.md | Bear won more decisively; two-tranche entry added; $480-490 secondary |
| 3_trading/trader.md | T1 $499-510 (1.0%), T2 $480-490 (0.5%), stop $456, targets $620/$665 |
| 4_risk/aggressive.md | Supports two-tranche; wants 0.75% secondary (overruled) |
| 4_risk/conservative.md | 0.5% secondary correct; 60-min Monday wait; stop-gap risk flagged |
| 4_risk/neutral.md | Conservative wins sizing; 30-min Monday wait; EMA 10 close as gate |
| 5_portfolio/decision.md | Final — Overweight, two-tranche confirmed, Monday protocol added |

## Key Watch
- **Monday open:** Wait 30 minutes — Barrons institutional effect peaks at open. Check EMA 10 ($503.63): close above = T1 only; close below = activate T2
- **Tranche 2 gate:** Only activate $480–490 if AMD closes below $499 (EMA 10 breaks)
- **Q2'26 earnings (~July 2026):** Revenue must exceed $10.76B; EPS must reaccelerate from $0.84; flat/decline = exit
- **Dead zone:** $510–546 — no entry under any circumstance
- **Breakout:** $549–555 only on close >$546 with volume >35M; cancel both limit tranches simultaneously

## What To Do — Plain English

**Step 1 — Place the primary limit order tonight (set and forget)**
In Robinhood, set a limit buy order for AMD at **$510** (range: $499–510).
Set as GTC, valid 5 trading days. Fills automatically — no watching needed.

**Step 2 — Monday morning rule**
Do NOT check or act on AMD for the first 30 minutes after 9:30am Monday.
The Barrons weekend articles create a selling rush at open. Let it clear.
After 10:00am, check where AMD is trading.

**Step 3 — EMA 10 gate (check Monday close at 4pm)**
- AMD closes above $503 → your primary limit at $499–510 stays active, nothing else to do
- AMD closes below $499 → place a second smaller limit order at **$485** (range $480–490) for half the size of your first order

**Step 4 — Set the stop loss after any fill**
Both tranches use the same stop: **$456**. Hard stop, no exceptions.
Set it immediately after each fill. Do not wait.

**Step 5 — Set profit targets**
- Sell half at **$620** (3-month target)
- Sell the other half at **$665** (6-month target)

**Step 6 — Breakout watch (only if AMD never pulls back)**
On any day AMD is near $546: check Robinhood at 3:30pm.
Volume >28M + price above $546 → watch 4pm close.
Closes above $546 with volume >35M → buy $549–555 next morning.
Cancel both limit orders at the same time.

**Step 7 — Q2 earnings check (~July 2026)**
Revenue must be above **$10.76B** and EPS above **$0.84**.
Both growing → hold. Either flat or down → exit fully.

**What to ignore:**
Daily moves between $456–$546, news noise, urge to move stop down.
