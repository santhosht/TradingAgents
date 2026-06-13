# Daily Scan Process

**Trigger:** User says "daily scan"

**Purpose:** Start-of-day full portfolio scan. Covers all open positions, orders placed, and pending entries. Tells you exactly what needs attention today before you do anything else.

**Key rules:**
- Fetch all symbols in parallel — do not serialize
- Never update POSITIONS.md unless user confirms an action
- Stale pending positions are still scanned — stale only gates placing an order, not the scan
- News is light by default, deeper automatically on any flagged symbol
- Always write LAST_DAILY_SCAN.md at the end — thesis check reads this file

---

## Step 1 — Read POSITIONS.md

Extract all three sections:

**Open positions:** symbol, all entries (entry price, stop, size, targets), thesis-break rule, action flags (e.g. "trim flagged Jun 9"), report folder ("Based on" field)

**Orders placed:** symbol, limit price, GTC expiry date, stop on fill, targets

**Pending:** symbol, entry range, breakout alt (trigger price + volume), stop on fill, stale-after date, special status (e.g. "WATCH AND WAIT")

Also note any ⚠ action flags already in POSITIONS.md (trim/exit decisions pending) — these go directly into TODAY'S ACTIONS.

---

## Step 2 — Fetch live prices (all symbols in parallel)

Fetch ALL symbols across open + orders placed + pending in one parallel batch:

```bash
python3 analysis/fetch_live_data.py SYMBOL
```

Outputs: current price, day change %, volume, RSI, MACD, EMA10, ATR, last 5 days candles.

Run one subprocess per symbol simultaneously — do not wait for one to finish before starting the next.

---

## Step 3 — Fetch news (adaptive depth)

For every symbol fetch light news first:

```
WebFetch: https://finviz.com/quote.ashx?t=SYMBOL
Extract: analyst price target, top 3 headlines, any PT changes or downgrades
```

After evaluating flags (Step 4 + Step 5), go deeper automatically on any flagged symbol:

```
WebSearch: "[SYMBOL] [company name] news site:finance.yahoo.com OR site:reuters.com OR site:bloomberg.com"
(last 48–72 hours)
```

**Go deeper when:**
- Stop hit or stop close
- Entry zone hit or breakout near
- Target near or reached
- Action flag already in POSITIONS.md
- Named catalyst in POSITIONS.md is within 3 days

Limit: up to 3 extra fetches per flagged symbol. Surface the most important gap.

---

## Step 4 — Evaluate open positions

For each open position entry calculate:
- P&L % = (current − entry) / entry × 100
- Stop distance % = (current − stop) / current × 100
- T1 distance % = (T1 − current) / current × 100
- T2 distance % = (T2 − current) / current × 100

Apply flags:

| Condition | Flag |
|-----------|------|
| price ≤ stop | 🔴 STOP HIT — exit immediately |
| price within 3% above stop | 🟠 STOP CLOSE — $[stop] is [X%] away |
| price within 3% below T1 | 🟢 T1 NEAR — ready to sell half at $[T1] |
| price ≥ T1 (not yet taken) | 🟢 T1 REACHED — sell half now |
| price ≥ T2 (not yet taken) | 🟢 T2 REACHED — sell remaining now |
| thesis-break rule triggered | 🔴 THESIS BREAK — [specific condition] |
| P&L ≥ 20% with no flag yet | 💰 QUICK WIN — up [X%], approaching T1 |
| action flag in POSITIONS.md | ⚠ ACTION PENDING — [flag text from POSITIONS.md] |

**No-analysis flag:** Check each open symbol against `analysis/data/reports/SYMBOL_*/`. If no folder exists:

| Condition | Flag |
|-----------|------|
| No report + any flag triggered | 🟡 NO ANALYSIS — [flag] triggered, run full analysis before acting |
| No report + position >6% portfolio | 🟡 NO ANALYSIS — concentrated position, no thesis on record |

---

## Step 5 — Evaluate orders placed

For each order:
- Check current price vs limit price
- Check GTC expiry date vs today

| Condition | Flag |
|-----------|------|
| price ≤ limit + 2% | ⚠ NEAR LIMIT — may have filled, confirm with broker |
| expiry date passed | ⚠ ORDER EXPIRED — confirm with broker |
| price > limit + 15% | ⚪ UNLIKELY TO FILL — price moved well above limit |

---

## Step 6 — Evaluate pending positions

For each pending entry check:
1. **Dip entry** — is current price at or below the suggested entry range?
2. **Breakout alt** — is price within 3% of breakout trigger, or past it?
3. **Stale** — is today past the stale-after date? (does NOT skip the price check)
4. **Watch & wait** — does the entry have an explicit "do not enter yet" condition?
5. **Stale soon** — is stale-after date within 2 trading days?

| Condition | Flag |
|-----------|------|
| price ≤ entry range top | 🟢 ENTRY ZONE — price at $[X], suggested entry $[Y]–$[Z] |
| price within 3% of breakout trigger | 🚀 BREAKOUT NEAR — $[X] trigger, [Y%] away |
| price ≥ breakout trigger (check volume) | 🚀 BREAKOUT TRIGGERED — close >$[X] on vol >[Y]M |
| price well above entry, no breakout signal | ⚪ TOO FAR — entry $[X] is [Y%] below current |
| stale-after date passed | 🗑 STALE — expired [date], re-run before placing order |
| stale-after within 2 trading days | ⏰ STALE SOON — expires [date], still interested? |
| explicit watch-and-wait status | ⏸ WATCH & WAIT — [condition from POSITIONS.md] |

Flags can combine — e.g. 🟢 ENTRY ZONE + 🗑 STALE means price is ready but analysis needs refresh before placing order.

---

## Step 7 — Calculate portfolio P&L

Sum across all open positions:
- Total cost basis
- Total current value
- Total P&L $ and %

---

## Step 8 — Write LAST_DAILY_SCAN.md

Overwrite `analysis/data/checks/LAST_DAILY_SCAN.md`. Three layers:

---

### Layer 1 — Today's Actions (top, what you read first)

```
Daily Scan — [date] [time]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Portfolio: [+/-$X] ([+/-X%]) across [N] open positions

🎯 TODAY'S ACTIONS:
  🔴 SYMBOL — STOP HIT — exit at market, say "exit SYMBOL"
  🔴 SYMBOL — THESIS BREAK — [rule triggered], say "exit SYMBOL"
  🟠 SYMBOL — STOP CLOSE — $[stop] is [X%] away — watch closely
  🟢 SYMBOL — T1 NEAR — sell half at $[T1], say "sell half SYMBOL"
  🟢 SYMBOL — ENTRY ZONE — price $[X] in zone $[Y]–$[Z] — run thesis check first
  🚀 SYMBOL — BREAKOUT NEAR — $[X] trigger [Y%] away — watch volume
  💰 SYMBOL — QUICK WIN — up [X%] — T1 at $[T1] ([Y%] away)
  ⚠ SYMBOL — ACTION PENDING — [flag from POSITIONS.md e.g. "trim flagged Jun 9"]
  ⚠ SYMBOL — NEAR LIMIT — confirm with broker if filled
  🟡 SYMBOL — NO ANALYSIS — [flag] triggered, run full analysis before acting

📋 WATCH LIST:
  ⏰ SYMBOL — stale [date] — still interested?
  ⏸ SYMBOL — WATCH & WAIT — [condition]
  ⚪ SYMBOL — TOO FAR — entry [X%] below current

✓ All clear   ← use this line instead of 🎯 TODAY'S ACTIONS if nothing flagged
```

---

### Layer 2 — Full Detail (for reference)

```
── Open Positions ───────────────────────────────────────

SYMBOL  | Entry   | Current | P&L    | Stop      | → T1      | → T2
--------|---------|---------|--------|-----------|-----------|-------
AMD     | $475.00 | $XXX.XX | +X.X%  | $419 (X%) | $523 (X%) | $600 (X%)
NVDA    | $131.29 | $XXX.XX | +X.X%  | $196 (X%) | $309 (X%) | $370 (X%)

── Orders Placed ────────────────────────────────────────

SYMBOL | Limit   | Current | Status
-------|---------|---------|-------
FTNT   | $130.50 | $XXX.XX | [status]

── Pending Positions ────────────────────────────────────

SYMBOL | Entry Zone  | Current | Breakout Alt       | Status
-------|-------------|---------|---------------------|-------
FTNT   | $130.50     | $XXX.XX | >$150.07 vol>7.5M  | 🚀 BREAKOUT NEAR
ADBE   | $212–$218   | $XXX.XX | >$248.57 vol>8M    | ⏸ WATCH & WAIT

── News Highlights ──────────────────────────────────────

SYMBOL: [headline — date] ← [positive / watch / negative]
```

---

### Layer 3 — Structured Data (for thesis check to read)

```
── FLAGGED SYMBOLS ──────────────────────────────────────
SYMBOL | FLAG | PRICE | REPORT
FTNT | ENTRY_ZONE | $130.20 | analysis/data/reports/FTNT_20260610_133733
UNH  | STOP_CLOSE | $383.50 | none
AMD  | ACTION_PENDING | $XXX.XX | analysis/data/reports/AMD_20260609_XXXXXX
MSTR | NO_ANALYSIS | $XXX.XX | none
```

Only flagged symbols appear in this section. Thesis check reads this to know which symbols need attention and where their reports are.

---

## Updating POSITIONS.md

Only update when user confirms:

| User says | Action |
|-----------|--------|
| "exit [SYMBOL]" | Move Open → Closed with exit price |
| "hold [SYMBOL]" | Add stop override note to Open entry |
| "filled" | Move Orders Placed → Open, add fill price, remind to set stop |
| "sell half [SYMBOL]" | Note T1 partial exit, update remaining size |
| "place order [SYMBOL]" | Move Pending → Orders Placed with limit price and expiry |
| "cancel [SYMBOL]" | Remove from Orders Placed |
