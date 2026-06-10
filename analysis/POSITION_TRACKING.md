# Position Tracking Process

**Trigger:** User asks about a ticker, position status, or "how is X doing"

**Key rules:**
- Always read POSITIONS.md first — it is the source of truth for entry price, stop, targets, report folder
- Pending positions: follow all steps except Step 2 — fetch live data to check if price is still inside entry zone
- Open positions: follow all steps
- Never update POSITIONS.md unless user explicitly says "I bought", "I sold", or asks to update

---

## Step 1 — Read POSITIONS.md and ask which to check

Read POSITIONS.md. For each pending symbol check report age (trading days only, Mon–Fri). Show all open, orders-placed, and pending symbols with staleness warnings:

```
"You have these positions:
 Open:
   1. AMD
   2. MKC
 Orders Placed (limit submitted — awaiting fill):
   1. FTNT — limit $130.50 — expires 2026-06-24
 Pending:
   1. ADBE  ⚠ 12 trading days old — consider removing or re-running
   2. INTU
   3. LULU
   4. NKE

 Which symbol do you want to check?"
```

Pending staleness rule: if report age > 10 trading days, show ⚠ next to the symbol. No action required here — stale cleanup is a separate process.
Orders Placed staleness rule: show ⚠ if GTC expiry date has passed — flag as "order may have expired, confirm with broker."

Wait for user to select.

- If **Open**: proceed to Step 2
- If **Orders Placed**: skip Step 2, go directly to Step 3, then use Orders Placed format in Step 5
- If **Pending**: skip Step 2, go directly to Step 3

---

## Step 2 — Read all entries and check staleness

Read ALL entries for the selected symbol from POSITIONS.md. For each entry:
- Extract entry price, stop, targets, size, report folder
- Check staleness against the report folder date

A report is stale when ANY of these are true:
- Report is >5 trading days old
- Price has moved >7% from the entry range in the report
- A named catalyst in the report has already passed (earnings, product launch, etc.)
- The stop price was hit

**If stale:** warn the user — "⚠ This report is X days old / [catalyst] has passed — analysis may be outdated." — then CONTINUE. Do not block.

All entries are included in the summary — no entry selection prompt.

**Report folder naming:** `analysis/data/reports/SYMBOL_YYYYMMDD_HHMMSS` — use the date in the folder name to check staleness.

---

## Step 3 — Read the latest decision report

Find the latest report folder: scan `analysis/data/reports/SYMBOL_*`, pick the highest timestamp.

Read: `analysis/data/reports/SYMBOL_YYYYMMDD_HHMMSS/5_portfolio/decision.md`

If deeper context needed, also read:
- `2_research/manager.md` — bull/bear debate verdict
- `1_analysts/fundamentals.md` — financial data

This single report covers the current thesis for all entries — do not read older report folders.

---

## Step 4 — Fetch live data

Fetch ONCE per symbol (reuse across all entries). Fetch all 4 in parallel:

| URL | What to extract |
|-----|----------------|
| `https://finance.yahoo.com/quote/SYMBOL/` | Current price, day range, 52-week range, volume vs avg volume |
| `https://finviz.com/quote.ashx?t=SYMBOL` | P/E, forward P/E, EPS, gross margin, analyst price target, recent news headlines |
| `https://stockanalysis.com/stocks/SYMBOL/financials/` | Gross margin, FCF, EPS (TTM) |
| `https://stockanalysis.com/stocks/SYMBOL/` | Analyst targets (mean, low, high), consensus rating, market cap, recent news |

Note: Yahoo Finance sub-pages (`/key-statistics/`, `/analysis/`, `/news/`) return 503 — use Finviz and StockAnalysis instead.

Use this data to:
- Calculate P&L, distance to stop, distance to targets
- Check if any financial metrics have shifted vs the original report (margin compression, EPS revision)
- Flag any news that maps to exit triggers or upgrade conditions
- Note if next earnings date is imminent (within 2 weeks)

---

## Step 5 — Deliver the update

### Open position format

```
SYMBOL — Position Review — [date]

Entry 1: $[entry]  → Current $[price]  P&L: [+/-X%]  Size: [X%]
  Stop: $[stop] ([X%] away) | T1: $[t1] ([X%] away) | T2: $[t2] ([X%] away)

Entry 2: $[entry]  → Current $[price]  P&L: [+/-X%]  Size: [X%]
  Stop: $[stop] ([X%] away) | T1: $[t1] ([X%] away) | T2: $[t2] ([X%] away)

Thesis: [Intact / Partially impaired / Broken]
  → [cite the specific trigger or condition from the report]

News: [top 3 headlines from Finviz — only if relevant to thesis or exit triggers]

Catalyst: [any imminent event named in the report]

Action: [Hold / Take partial at T1 / Trail stop to $X / Exit — reason]
```

Repeat Entry lines for each entry. Thesis, News, Catalyst, and Action are shared across all entries — shown once at the bottom.

### Orders Placed format

```
SYMBOL — Limit Order — [date]

Limit:    $[limit_price] GTC (placed [placed_date], expires [expiry_date])
Current:  $[price] ([X%] above/below limit)
Stop on fill: $[stop] | Target 1: $[t1] | Target 2: $[t2]

Status: [Waiting — price above limit / ⚠ Near limit — may have filled / ⚠ Order expired]

⚠ Flags:
  Price ≤ limit + 2%  → "Check broker — may have filled. Set stop $[stop] immediately if so."
  Price > limit + 15% → "Price well above limit — consider cancelling or re-evaluating."
  Expiry passed       → "GTC order may have expired — confirm with broker."
```

### Pending position format

```
SYMBOL — Pending — [date]

Entry zone: $X–$X  (report valid until [stale date])
Stop:       $X.XX
Target 1:   $X.XX | Target 2: $X.XX

Status: [Waiting / Zone missed / Zone broken / Stale — re-run needed]

Next catalyst: [e.g. earnings Jun 11 — exit if gross margin <89%]
```

---

## Step 6 — Suggest a full re-run if needed

Suggest re-running the full pipeline (`ANALYSIS_PROCESS.md`) when:
- Report is stale AND user is deciding whether to add to the position
- A major catalyst has passed (earnings, product launch, regulatory event)
- Stock has moved >15% from entry in either direction
- User asks "is this still a good buy?"

---

## Updating POSITIONS.md

Only update when the user explicitly reports an action:

| Event | Action |
|-------|--------|
| User places a limit order | Move from Pending → Orders Placed with limit price and GTC expiry |
| User says limit filled | Move from Orders Placed → Open with actual fill price, size, date; remind to set stop |
| User cancels order | Remove from Orders Placed |
| User enters a trade (no prior limit) | Move from Pending → Open with actual entry price, size, date |
| User closes a trade | Move from Open → Closed with exit price and result % |
| Stop hit | Move to Closed, record "stopped out at $X" |
| Target 1 reached | Note partial exit in Open, update remaining size |
| Target 2 reached | Move to Closed |
| User modifies stop | Update stop in Open |
