# Position Tracking Process

This file defines how to manage, review, and update positions.
Data lives in `POSITIONS.md`. Analysis lives in `reports/`.

---

## 1. When to Read POSITIONS.md

Read `POSITIONS.md` whenever the user:
- Asks about a specific ticker ("what should I do with ADBE?")
- Asks for a position review or daily update
- Says "I bought X" or "I sold X" — update POSITIONS.md accordingly
- Asks "follow my position on X"

**Pending vs Open — critical distinction:**
- **Pending positions**: Read `POSITIONS.md` only. Report entry conditions, staleness, and upcoming catalysts. Do NOT fetch live data.
- **Open positions**: Follow the full Step 2b live data fetch (Yahoo Finance quote + Finviz + StockAnalysis).

---

## 2. Updating POSITIONS.md

| Event | Action |
|-------|--------|
| User enters a trade | Move from Pending → Open Positions with actual entry price, size, date. No Yahoo Finance fetch needed — just update the file. |
| User closes a trade | Move from Open → Closed with exit price and result % |
| Stop hit | Move to Closed, record "stopped out at $X" |
| Target 1 reached | Note partial exit in Open Positions, update remaining size |
| Target 2 reached | Move to Closed |
| User modifies stop | Update stop in Open Positions |

---

## 3. Report Staleness Rules

A report is stale when ANY of these are true:
- Report is >5 trading days old
- Price has moved >7% from the entry range in the report
- A named catalyst in the report has already passed (earnings, product launch, etc.)
- The stop price was hit

**If stale:** Warn the user — "⚠ This report is X days old / [catalyst] has passed — analysis may be outdated. Consider re-running the pipeline for a fresh view." — then CONTINUE using the last known analysis. Do not block.

**Report folder naming:** `reports/SYMBOL_YYYYMMDD_HHMMSS` — use the date in the folder name to check staleness.

---

## 4. Position Review — Step by Step

### Step 1 — Check staleness
- Get report folder from POSITIONS.md
- Apply rules in Section 3
- Warn if stale, continue either way

### Step 2 — Read the analysis
- Start with `reports/SYMBOL_YYYYMMDD_HHMMSS/5_portfolio/decision.md`
- If deeper context needed, also read:
  - `complete_report.md` — full pipeline summary
  - `2_research/manager.md` — bull/bear debate verdict
  - `1_analysts/fundamentals.md` — financial data

### Step 2b — Fetch live data
Fetch all of the following in parallel:

| URL | What to extract |
|-----|----------------|
| `https://finance.yahoo.com/quote/SYMBOL/` | Current price, day range, 52-week range, volume vs avg volume |
| `https://finviz.com/quote.ashx?t=SYMBOL` | P/E, forward P/E, EPS, gross margin, analyst price target, recent news headlines |
| `https://stockanalysis.com/stocks/SYMBOL/financials/` | Gross margin, FCF, EPS (TTM) |
| `https://stockanalysis.com/stocks/SYMBOL/` | Analyst targets (mean, low, high), consensus rating, market cap, recent news |

Note: Yahoo Finance sub-pages (`/key-statistics/`, `/analysis/`, `/news/`) return 503 — use Finviz and StockAnalysis instead.

Use this data to:
- Calculate P&L, distance to stop, distance to targets
- Check if any financial metrics have shifted vs the original report (e.g. margin compression, EPS revision)
- Flag any news that maps to exit triggers or upgrade conditions in the report
- Note if next earnings date is imminent (within 2 weeks)

### Step 3 — Compare current reality to the thesis
- Is the investment thesis still intact?
- Has any exit trigger from the report fired?
- Has any upgrade condition from the report been met?

### Step 4 — Deliver the update in this format

```
SYMBOL — Position Review — [date]

Price:    $X.XX  (entry $X.XX → P&L: +/-X%)
Stop:     $X.XX  (X% / $X.XX away)
Target 1: $X.XX  (X% away) — [sell instruction from report]
Target 2: $X.XX  (X% away) — [sell instruction from report]

Thesis: [Intact / Partially impaired / Broken]
  → [cite the specific trigger or condition from the report]

Catalyst: [any imminent event named in the report]

Action: [Hold / Take partial at T1 / Trail stop to $X / Exit — reason]
```

---

## 5. When to Suggest a Full Re-Run

Suggest re-running the full pipeline (`ANALYSIS_PROCESS.md`) when:
- Report is stale AND the user is deciding whether to add to the position
- A major catalyst has passed (earnings, product launch, regulatory event)
- The stock has moved >15% from entry in either direction
- User asks "is this still a good buy?"
