# Morning Check Process

**Trigger:** User says "morning check"

**Key rules:**
- Never update any MD files during morning check unless user explicitly asks
- Each entry is independent — own stop, own targets, own report
- Report age = trading days only (Mon–Fri), skip weekends
- Price/technicals fetched via yfinance directly in session — no script, no file saved
- Reuse fetch_price_and_technicals() and fetch_live_quote() logic from fetch_data.py
- Calm day check uses last 5 days from 60-day candle history — no manual tracking needed
- Latest report = highest timestamp folder in analysis/data/reports/SYMBOL_*/
- Entry report = "Based on" field in POSITIONS.md

---

## Step 1 — List positions and ask which to check

Read POSITIONS.md. For each pending symbol check report age (trading days only, Mon–Fri). Show all open and pending symbols with entry count and staleness warnings:

```
"You have these positions:
 Open:
   1. AMD (2 entries)
   2. MKC (1 entry)
 Pending:
   1. ADBE  ⚠ 12 trading days old — consider removing or re-running
   2. INTU
   3. LULU
   4. NKE

 Which symbols do you want to check today?"
```

Pending staleness rule: if report age > 10 trading days, show ⚠ next to the symbol. No action required here — stale cleanup is a separate process.

Wait for user to select symbols.

---

## Step 2 — Read POSITIONS.md for selected symbols

For each selected symbol extract:
- All entries (entry price, stop, targets, size, based-on report)
- Pending entry zone if applicable
- Earnings check thresholds

---

## Step 3 — Loop per symbol → branch on open vs pending

- If **Open**: show its entries and ask which to check:

```
"AMD has these entries:
 1. Entry $475 — stop $419 — based on Jun 7 report
 2. Entry $440 — stop $383 — based on Jun 9 report
 Which entries to check? (or 'all')"
```

Wait for user to select entries. Then for each selected entry run Steps 3a–5.

- If **Pending**: skip entry selection. Go directly to Step 3a using the report from the "Based on" field in POSITIONS.md.

### Step 3a — Check report age FIRST

Find latest report: scan analysis/data/reports/SYMBOL_* folders, pick highest timestamp.
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
- Read analysis/data/reports/SYMBOL_YYYYMMDD_HHMMSS/5_portfolio/decision.md
- Read analysis/data/reports/SYMBOL_YYYYMMDD_HHMMSS/2_research/manager.md

### Step 3d — Read latest report

Find latest report folder (highest timestamp in analysis/data/reports/SYMBOL_*):
- If same as entry report → skip, already read
- If different → read decision.md + manager.md (or complete_report.md if user chose B)

---

## Step 4 — Fetch price and technicals

Run ONCE per symbol (reuse across all entries of same symbol). No file saved.

```bash
python3 analysis/fetch_live_data.py SYMBOL
```

Outputs: current price, day change %, volume, RSI, MACD, VWMA20, Bollinger, EMA10, ATR, last 5 days.

Also fetch Finviz in parallel (ONCE per symbol):

```
WebFetch: https://finviz.com/quote.ashx?t=SYMBOL
Extract: analyst price target, recent news headlines (top 3–5)
```

Use the news headlines in Step 5 to flag any exit triggers (earnings miss, sector contagion, guidance cut, analyst downgrade).

---

## Step 5 — Output per entry

- If **Open**: show Part A then Part B (if applicable)
- If **Pending**: skip Part A, go directly to Part B

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

News: (top 3 from Finviz — only show if relevant to thesis or exit triggers)
  · [headline]

⚠ Flags (only shown if triggered):
  Stop within 3%         → WATCH CLOSELY — stop $[stop], price $[price]
  Target 1 within 3%     → READY TO SELL HALF at $[t1]
  Earnings within 7 days → Check: revenue >[threshold], EPS >[threshold]
  News exit trigger      → [headline that maps to: earnings miss / sector contagion / guidance cut / analyst downgrade]
```

### Part B — New entry opportunity from latest report

- If **Open**: only shown if latest report differs from entry report AND suggests an entry zone
- If **Pending**: always shown — this is the primary output

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
