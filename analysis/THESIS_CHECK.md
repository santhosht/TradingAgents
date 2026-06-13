# Thesis Check Process

**Trigger:** User says "thesis check SYMBOL"

**Purpose:** Deep dive on a specific symbol before acting on a flag from daily scan. Reads the existing report, fetches fresh price and deep news, evaluates if thesis is still intact, and gives one clear action recommendation per state (open / orders placed / pending).

**Key rules:**
- Always covers all states for the symbol — open, orders placed, and pending in one output
- Stale analysis is highlighted in output but never blocks — always complete the check
- If LAST_DAILY_SCAN.md was run today → reuse prices and news from it (no duplicate fetch)
- If running standalone (no daily scan today) → fetch own prices and news
- Report age = trading days only (Mon–Fri), skip weekends
- Latest report = highest timestamp folder in `analysis/data/reports/SYMBOL_*/`
- Entry report = "Based on" field in POSITIONS.md
- Always write output to `analysis/data/checks/thesis/SYMBOL.md`

---

## Step 1 — Read POSITIONS.md for this symbol

Extract all states for the symbol:

**Open entries:** entry price, stop, size, targets (T1, T2), thesis-break rule, report folder ("Based on" field), any action flags (e.g. "trim flagged")

**Orders placed:** limit price, GTC expiry, stop on fill, targets

**Pending:** entry range, breakout alt (trigger + volume), stop on fill, stale-after date, special status (e.g. "WATCH AND WAIT")

If symbol appears in none of the three sections → tell user: "SYMBOL not found in POSITIONS.md — is this a new trade? Run full analysis first."

---

## Step 2 — Check LAST_DAILY_SCAN.md

Check if `analysis/data/checks/LAST_DAILY_SCAN.md` exists and was written today:

**If today's daily scan exists:**
→ Read the Structured Data section (Layer 3) for this symbol
→ Extract: price, flags, news already fetched, report path
→ Skip standalone price/news fetch in Step 3 — reuse this data instead
→ Note: still fetch a fresh live price in Step 3a (prices change fast)

**If no daily scan today (standalone mode):**
→ Proceed to Step 3 and fetch everything fresh

---

## Step 3 — Fetch fresh live price

Always fetch a fresh price regardless of daily scan — prices change throughout the day:

```bash
python3 analysis/fetch_live_data.py SYMBOL
```

Outputs: current price, day change %, volume, RSI, MACD, VWMA20, Bollinger, EMA10, ATR, last 5 days candles.

**If standalone mode** (no daily scan today), also fetch Finviz in parallel:

```
WebFetch: https://finviz.com/quote.ashx?t=SYMBOL
Extract: analyst price target, recent news headlines (top 3–5), any PT changes or downgrades
```

---

## Step 4 — Find and read reports

### Step 4a — Check analysis age

Find latest report: scan `analysis/data/reports/SYMBOL_*`, pick highest timestamp folder.
Calculate age in trading days (Mon–Fri only):

**If no report exists at all:**
→ Note in output: "⚠ No analysis on file — consider running full analysis before acting"
→ Continue with live data only (Steps 3, 5) — do not block

**If report exists but stale (>5 trading days):**
→ Note in output: "⚠ Analysis is [X] trading days old — consider running full analysis before acting"
→ Continue regardless — never block or ask

**If report is fresh (≤5 trading days):**
→ Proceed normally

### Step 4b — Ask report depth (only if report exists)

```
"How much detail for SYMBOL?
 A) Standard — decision.md + manager.md + news.md (recommended)
 B) Full — complete_report.md (⚠ heavy operation, slow)"
```

Default to A if no answer within one exchange.

### Step 4c — Read entry report

From "Based on" field in POSITIONS.md, read all three in parallel:
- `analysis/data/reports/SYMBOL_YYYYMMDD_HHMMSS/5_portfolio/decision.md`
- `analysis/data/reports/SYMBOL_YYYYMMDD_HHMMSS/2_research/manager.md`
- `analysis/data/reports/SYMBOL_YYYYMMDD_HHMMSS/1_analysts/news.md`

### Step 4d — Read latest report

Find latest report folder (highest timestamp in `analysis/data/reports/SYMBOL_*`):
- If same as entry report → skip, already read
- If different → read all three files in parallel, note what changed vs entry report

---

## Step 5 — Deep news fetch

Go deeper on news than daily scan:

**Always fetch:**
```
WebSearch: "[SYMBOL] [company name] news site:finance.yahoo.com OR site:reuters.com OR site:bloomberg.com"
(last 48–72 hours)
```

**Go deeper proactively when:**
- A named catalyst in the report is within 3 days (earnings, regulatory event, product launch) → targeted search: "SYMBOL [catalyst keyword] [month year]"
- Finviz shows a PT cut or downgrade → search for the full analyst note context
- A macro risk named in report (export controls, tariffs, rate decision) has a live headline → fetch the specific article
- Any headline mentions a competitor that maps to a risk in the report → search for more detail

**Depth rule:** Up to 3 extra fetches — surface the most important gap, go deep on that one.

If standalone mode: cross-reference all headlines against catalysts and risks named in news.md from the report.

---

## Step 6 — Evaluate thesis

Using report + live data + news, evaluate:

**Thesis status:**
- **Intact** — core thesis still holds, no major catalysts missed, technicals supportive
- **Impaired** — thesis partially holds but one or more risks have materialized
- **Broken** — core thesis no longer valid, exit conditions triggered

**For open entries — technicals:**
- RSI: overbought >70 / neutral 45–55 / oversold <40
- MACD: bullish crossover / bearish crossover / neutral
- vs VWMA20: above / below
- Bollinger: near upper / mid / near lower

**For pending entries — calm day analysis (last 5 days from candle data):**
- Count consecutive calm days inside zone (calm = volume < 25M AND price move < 1×ATR)
- Is price holding the zone or just touching and bouncing?
- Volume trend: shrinking or growing?
- RSI: cooling toward 45–55 or still elevated?
- Any big red candles breaking below the zone?

Confidence rating for pending:
```
HIGH   — 3+ calm days, volume shrinking, RSI cooling, price holding
MEDIUM — 2 calm days but volume still elevated
LOW    — price in zone but RSI high / volume not shrinking
NONE   — price touched zone but not holding
MISSED — price moved above zone top
BROKEN — price dropped below zone bottom
```

**For latest report vs entry report (if different):**
- Note any changes in price targets, thesis direction, key risks
- Flag if latest report contradicts entry report thesis

---

## Step 7 — Write output

Write to `analysis/data/checks/thesis/SYMBOL.md` — overwrite on every run.

```
Thesis Check — SYMBOL — [date]
Valid until: [date 5 trading days from today]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠ Analysis is [X] trading days old — consider running full analysis before acting
(only shown if stale or missing)

⚠ Latest report ([date]) differs from entry report ([date]):
  → [key difference — e.g. price target revised, thesis direction changed]
(only shown if reports differ)

── Open Position ────────────────────────────────────────

Entry 1: $[entry] → Current $[price] | P&L: [+/-X%] | Size: [X%]
  Stop: $[stop] ([X%] away) | T1: $[t1] ([X%] away) | T2: $[t2] ([X%] away)

Entry 2: $[entry] → Current $[price] | P&L: [+/-X%] | Size: [X%]
  Stop: $[stop] ([X%] away) | T1: $[t1] ([X%] away) | T2: $[t2] ([X%] away)

Technicals:
  RSI:      [value] ([overbought / neutral / oversold])
  MACD:     [bullish / bearish / neutral]
  vs VWMA:  [above / below] ($[vwma])
  Bollinger:[near upper / mid / near lower]

── Orders Placed ────────────────────────────────────────

Limit: $[limit] GTC (expires [date]) | Current: $[price] ([X%] above/below)
Stop on fill: $[stop] | T1: $[t1] | T2: $[t2]
Status: [Waiting / ⚠ Near limit — may have filled / ⚠ Expired]

── Pending Entry ─────────────────────────────────────────

Entry zone: $[X]–$[X] | Current: $[price] | Status: [IN ZONE / TOO FAR / STALE / WATCH & WAIT]
Stop: $[stop] | T1: $[t1] | T2: $[t2]
Confidence: [HIGH / MEDIUM / LOW / NONE / MISSED / BROKEN]
  → [reason: calm days, volume, RSI]
🗑 STALE — expired [date] — re-run full analysis before placing order
(only shown if stale)

── Thesis ───────────────────────────────────────────────

Status: [Intact / Impaired / Broken]
  → [specific reason cited from report + current data]

News:
  · [headline — date] — [positive / watch / negative]
  · [headline — date] — [positive / watch / negative]

── Action ───────────────────────────────────────────────

Open     → [Hold / Trim X% at $X / Exit — reason]
Orders   → [Monitor — price $X away from limit / Cancel — reason]
Pending  → [Enter — place limit at $X, stop $X, size X% / Wait — reason / Skip — reason]
```

Omit any section (Open / Orders Placed / Pending) if symbol has no position in that state.

---

## Updating POSITIONS.md

Only update when user explicitly confirms an action after reading the thesis check output:

| User says | Action |
|-----------|--------|
| "exit [SYMBOL]" | Move Open → Closed with exit price |
| "hold [SYMBOL]" | Add stop override note to Open entry |
| "trim [SYMBOL]" | Note partial exit in Open entry, update size |
| "filled" | Move Orders Placed → Open, add fill price, remind to set stop |
| "cancel [SYMBOL]" | Remove from Orders Placed |
| "place order [SYMBOL]" | Move Pending → Orders Placed with limit price and expiry |
