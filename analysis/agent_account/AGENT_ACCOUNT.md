# Agent Account Process

**Trigger:** User says "agent scan" or "agent account"

**Purpose:** Full management cycle for the $1000 Robinhood agent account. Fetches current account state, scans all existing analyses for swing candidates, runs swing check on each, ranks by conviction, and places orders via MCP. Re-run every 2–3 days.

**Key rules:**
- Always fetch account state first — never assume cash or positions
- Only trade symbols that have an existing analysis report (≤10 trading days old)
- Never place orders without running swing check first
- Fractional shares are fine — no minimum share count
- Do not force deploy all cash — idle cash is fine if signals are weak
- Never update POSITIONS.md for agent account trades — agent account is separate

---

## Step 1 — Fetch agent account state (MCP)

Using Robinhood MCP, fetch:
- Current open positions: symbol, shares, avg cost, current value
- Open orders: symbol, order type, limit price, status
- Available cash / buying power
- Total account value

```
MCP: get_portfolio or equivalent Robinhood MCP tool
```

Build a summary:
```
Agent Account State — [date]
Total value:    $[X]
Cash available: $[X]
Open positions: [SYMBOL ($X), SYMBOL ($X), ...]
Open orders:    [SYMBOL limit $X, ...]
```

If cash available = $0 → stop. Tell user: "No cash available in agent account. Wait for a position to close."

---

## Step 2 — Scan all existing analyses

List all report folders: `analysis/data/reports/SYMBOL_*/`

For each folder:
1. Extract symbol name and report date from folder name (SYMBOL_YYYYMMDD_HHMMSS)
2. Calculate report age in trading days
3. Read `5_portfolio/decision.md` — extract rating (Overweight / Underweight / Neutral)

**Filter out:**
- Report age > 10 trading days → skip (stale)
- Rating = Underweight → skip
- Symbol already in agent account open positions → skip (already trading)
- Symbol already in agent account open orders → skip (order pending)

**Output:** candidate list of fresh, Overweight symbols not already in account

If candidate list is empty → tell user: "No fresh candidates available. Run full analysis on new symbols or wait for existing analyses to refresh."

---

## Step 3 — Run swing check on all candidates

For each candidate from Step 2, run the full swing check process (SWING_CHECK.md):
- Fetch live price + technicals
- Fetch Finviz news
- Answer 5 swing questions
- Get decision: BUY / WAIT / SKIP
- Get conviction score: High / Medium / Low
- Get order parameters

Run all candidates in parallel — do not serialize.

**Filter:** keep only BUY decisions. Remove WAIT and SKIP.

If no BUY signals → tell user: "No BUY signals today. WAITs: [list]. Re-run in 1–2 days."

---

## Step 4 — Rank and allocate

Rank BUY signals by conviction score, then by R:R within each tier:

| Rank | Conviction | Allocation |
|------|-----------|------------|
| 1st | High | $250–$300 |
| 2nd | High | $250–$300 |
| 3rd | Medium | $150–$200 |
| 4th | Medium | $150–$200 |
| 5th+ | Low | $75–$100 |

Rules:
- Do not exceed available cash from Step 1
- If total allocation > available cash → reduce lowest conviction positions first
- If remaining cash after all allocations < $75 → leave it idle
- No forced allocation — if only 1 BUY signal exists, deploy only that amount

**Output allocation table:**
```
Symbol | Conviction | Allocation | Shares   | Entry   | Stop  | Target
-------|-----------|------------|----------|---------|-------|-------
NVDA   | High      | $300       | 1.460    | $205.50 | $189  | $235
GOOGL  | Medium    | $200       | 0.556    | $360    | $338  | $404
Cash kept idle: $500
```

---

## Step 5 — Place orders via MCP

For each symbol in allocation table, place 3 orders in sequence via Robinhood MCP:

1. **Buy limit order** — entry price, GTC (good till cancelled), fractional shares
2. **Stop loss sell order** — stop price from decision.md, GTC
3. **Target sell order** — limit sell at swing target, GTC

```
MCP: place_order — buy limit SYMBOL [shares] at $[entry] GTC
MCP: place_order — sell stop SYMBOL [shares] at $[stop] GTC
MCP: place_order — sell limit SYMBOL [shares] at $[target] GTC
```

After placing each set of 3 orders, confirm order IDs returned by MCP.

If MCP does not support stop or limit sell orders → flag to user: "Stop/target orders not supported via MCP — monitor manually via daily scan."

---

## Step 6 — Output summary

Print a clean summary of what was done:

```
Agent Account Scan — [date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Account: $[total] | Cash before: $[X] | Cash after: $[X]

Orders placed:
  ✅ NVDA  — buy 1.460 @ $205.50 | stop $189 | target $235 | risk $24 | reward $43
  ✅ GOOGL — buy 0.556 @ $360    | stop $338 | target $404 | risk $12 | reward $24

Skipped (WAIT):
  ⏳ AMZN — MACD still falling, wait for green close
  ⏳ AAPL — Tata key risk active

Cash kept idle: $[X]

Next run: [date 2-3 trading days from now]
```

---

## Step 7 — Re-run cadence

Re-run "agent scan" every 2–3 trading days:
- Positions may have closed (stop or target hit) → cash freed up
- WAIT signals may have flipped to BUY
- New analyses may have been added as fresh candidates
- Stale analyses (>10 days) drop off the candidate list automatically
