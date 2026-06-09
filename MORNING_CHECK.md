# Morning Check Process

**Trigger:** User says "morning check"

**Key rules:**
- Never update any MD files during morning check unless user explicitly asks
- Each entry is independent — own stop, own targets, own report
- Report age = trading days only (Mon–Fri), skip weekends
- Price/technicals fetched via yfinance directly in session — no script, no file saved
- Reuse fetch_price_and_technicals() and fetch_live_quote() logic from fetch_data.py
- Calm day check uses last 5 days from 60-day candle history — no manual tracking needed
- Latest report = highest timestamp folder in reports/SYMBOL_*/
- Entry report = "Based on" field in POSITIONS.md

---

## Step 1 — List positions and ask which to check

Read POSITIONS.md. Show all open and pending symbols with entry count:

```
"You have these positions:
 Open:
   1. AMD (2 entries)
   2. MKC (1 entry)
 Pending:
   1. ADBE
   2. INTU

 Which symbols do you want to check today?"
```

Wait for user to select symbols.

---

## Step 2 — Read POSITIONS.md for selected symbols

For each selected symbol extract:
- All entries (entry price, stop, targets, size, based-on report)
- Pending entry zone if applicable
- Earnings check thresholds

---

## Step 3 — Loop per symbol → ask which entries → loop per entry

For each symbol show its entries and ask which to check:

```
"AMD has these entries:
 1. Entry $475 — stop $419 — based on Jun 7 report
 2. Entry $440 — stop $383 — based on Jun 9 report
 Which entries to check? (or 'all')"
```

Wait for user to select entries. Then for each selected entry run Steps 3a–5.

### Step 3a — Check report age FIRST

Find latest report: scan reports/SYMBOL_* folders, pick highest timestamp.
Calculate age in trading days only (Mon–Fri, skip weekends):

```
Age <= 5 trading days:
  → Proceed to Step 3b

Age > 5 trading days + today is weekday:
  → ⚠ "Latest SYMBOL report is X trading days old.
      A) Run fresh analysis now (say 'analyse SYMBOL fresh')
      B) Continue with existing report anyway"
  → Wait for user to pick

Age > 5 trading days + today is weekend:
  → ⚠ "Latest SYMBOL report is X trading days old.
      Markets closed today — action needed Monday"
  → Continue to Step 3b automatically
```

### Step 3b — Ask report depth

```
"How much detail for SYMBOL?
 A) Standard — decision.md + manager.md (recommended, fast)
 B) Full — complete_report.md (⚠ heavy operation, slow)"
```

Default to A if no answer within one exchange.

### Step 3c — Read entry report

From "Based on" field in POSITIONS.md:
- Read reports/SYMBOL_YYYYMMDD_HHMMSS/5_portfolio/decision.md
- Read reports/SYMBOL_YYYYMMDD_HHMMSS/2_research/manager.md

### Step 3d — Read latest report

Find latest report folder (highest timestamp in reports/SYMBOL_*):
- If same as entry report → skip, already read
- If different → read decision.md + manager.md (or complete_report.md if user chose B)

---

## Step 4 — Fetch price and technicals

Run ONCE per symbol (reuse across all entries of same symbol). No file saved.

Run directly in session using yfinance:
- fetch_live_quote() logic → current price, day change %, volume
- fetch_price_and_technicals() logic → RSI, MACD, VWMA, Bollinger, EMA10, ATR (60 days)

Both functions are defined in fetch_data.py — reuse the same logic.

---

## Step 5 — Output per entry

### Part A — Current entry status

```
SYMBOL Entry X — $[entry] → Current $[price] — P&L [+/-X%]
Stop:     $[stop] ([X]% away)
Target 1: $[t1] ([X]% away) | Target 2: $[t2] ([X]% away)

Technicals:
  RSI:      [value] ([overbought >70 / neutral 45-55 / oversold <40])
  MACD:     [bullish crossover / bearish crossover / neutral]
  vs VWMA:  [above / below] ($[vwma])
  Bollinger:[near upper / mid / near lower] ($[value])

Thesis:  [Intact / Impaired / Broken]
  → [specific reason cited from report]

Action: [Hold / Watch stop closely / Exit / Take partial profit at $XXX]

⚠ Flags (only shown if triggered):
  Stop within 3%         → WATCH CLOSELY — stop $[stop], price $[price]
  Target 1 within 3%     → READY TO SELL HALF at $[t1]
  Earnings within 7 days → Check: revenue >[threshold], EPS >[threshold]
```

### Part B — New entry opportunity from latest report

Only shown if latest report differs from entry report AND suggests an entry zone.

Using the 60-day candle data already fetched in Step 4, analyse last 5 days:
- Count consecutive calm days inside zone
  (calm = volume < 25M AND price move < 1×ATR)
- Is price holding the zone or just touching and bouncing?
- Volume trend: shrinking or growing over last 5 days?
- RSI: cooling toward 45-55 or still elevated?
- Any big red candles breaking below the zone?

Output confidence rating:

```
HIGH confidence (3+ calm days, volume shrinking, RSI cooling, price holding):
  → "ENTER — place limit at $[zone midpoint]
     Stop: $[stop] | Target 1: $[t1] | Target 2: $[t2]"

MEDIUM confidence (2 calm days but volume still elevated):
  → "Enter half size only, watch closely"

LOW confidence (price in zone but RSI high / volume not shrinking):
  → "Wait one more day"

NO ENTRY (price touched zone but not holding):
  → "Zone not confirmed as support — skip"

ZONE MISSED (price moved above zone top):
  → "Price above $[zone top] — don't chase"

ZONE BROKEN (price dropped below zone bottom):
  → "Price below $[zone bottom] — do not enter"
```

---

## Step 6 — Loop

After Step 5 for current entry → next selected entry → back to Step 3.
After all entries for symbol done → next selected symbol → back to Step 1 symbol loop.
