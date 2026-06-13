# Stop Check Process

**Trigger:** User says "stop check" / "check stops"

**Purpose:** Quick intraday snapshot of all open positions and orders placed. Run anytime during the trading day to see where everything stands — P&L, stop distances, targets, quick wins. Fast. No reports read, no pending scan, no deep news.

**Key rules:**
- No stop-limit orders are set in broker — this check IS the stop enforcement mechanism
- Fetch all symbols in parallel — do not serialize
- Never update POSITIONS.md unless user confirms an action
- No report reading, no news fetching — price data only
- If stop is hit: surface it immediately with exact action

---

## Step 1 — Read POSITIONS.md

Extract all **Open** positions. For each:
- Symbol, all entries (entry price, stop, size, targets T1/T2)
- Thesis-break exit rule (if defined)
- Any action flags already noted (e.g. "trim flagged")

Extract all **Orders Placed**. For each:
- Symbol, limit price, GTC expiry date, stop on fill, targets

---

## Step 2 — Fetch live prices (all symbols in parallel)

For each open + orders placed symbol:

```bash
python3 analysis/fetch_live_data.py SYMBOL
```

Outputs: current price, day change %, volume, RSI, EMA10, ATR.

Run all symbols simultaneously — do not wait for one before starting the next.

---

## Step 3 — Calculate portfolio P&L

Sum across all open positions:
- Total cost basis (entry price × shares, per entry)
- Total current value (current price × shares, per entry)
- Total P&L $ = current value − cost basis
- Total P&L % = total P&L $ / total cost basis × 100

---

## Step 4 — Evaluate each open entry

For each entry calculate:
- P&L % = (current − entry) / entry × 100
- Stop distance % = (current − stop) / current × 100
- T1 distance % = (T1 − current) / current × 100
- T2 distance % = (T2 − current) / current × 100

Apply flags:

| Condition | Flag | Action |
|-----------|------|--------|
| price ≤ stop | 🔴 STOP HIT | Exit at market — say "exit SYMBOL" |
| price within 3% above stop | 🟠 STOP CLOSE | Watch closely — stop $[stop] is [X%] away |
| thesis-break rule triggered | 🔴 THESIS BREAK | Exit immediately — say "exit SYMBOL" |
| price within 3% below T1 | 🟢 T1 NEAR | Ready to sell half — say "sell half SYMBOL" |
| price ≥ T1 (not yet taken) | 🟢 T1 REACHED | Sell half now — say "sell half SYMBOL" |
| price ≥ T2 (not yet taken) | 🟢 T2 REACHED | Sell remaining — say "sell SYMBOL" |
| P&L ≥ 20% with no flag yet | 💰 QUICK WIN | Up [X%] — T1 at $[T1] ([Y%] away) — consider partial |
| action flag in POSITIONS.md | ⚠ ACTION PENDING | [flag text from POSITIONS.md — e.g. "trim flagged Jun 9"] |

---

## Step 5 — Evaluate orders placed

For each order:
- Check current price vs limit price
- Check GTC expiry date vs today

| Condition | Flag | Action |
|-----------|------|--------|
| price ≤ limit + 2% | ⚠ NEAR LIMIT | Check broker — may have filled. Set stop $[stop] immediately if so. |
| expiry date passed | ⚠ ORDER EXPIRED | Confirm with broker — order may have lapsed. |
| price > limit + 15% | ⚪ UNLIKELY TO FILL | Price moved well above limit — consider cancelling. |

---

## Step 6 — Write LAST_STOP_CHECK.md

Overwrite `analysis/data/checks/LAST_STOP_CHECK.md` after every run. No confirmation needed.

```
Stop Check — [date] [time]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Portfolio: [+/-$X total P&L] ([+/-X%]) across [N] positions

🎯 FLAGS:
  🔴 SYMBOL — STOP HIT — exit at market, say "exit SYMBOL"
  🔴 SYMBOL — THESIS BREAK — [rule triggered] — say "exit SYMBOL"
  🟠 SYMBOL — STOP CLOSE — stop $[stop] is [X%] away — watch closely
  🟢 SYMBOL — T1 NEAR — sell half at $[T1], say "sell half SYMBOL"
  🟢 SYMBOL — T1 REACHED — sell half now, say "sell half SYMBOL"
  💰 SYMBOL — QUICK WIN — up [X%], T1 at $[T1] ([Y%] away)
  ⚠ SYMBOL — ACTION PENDING — [flag text]
  ⚠ SYMBOL — NEAR LIMIT — check broker, may have filled

✓ All clear   ← use this line instead of 🎯 FLAGS if nothing flagged

── Open Positions ───────────────────────────────────────

SYMBOL  | Entry   | Current | P&L    | Stop      | → T1      | → T2
--------|---------|---------|--------|-----------|-----------|-------
AMD     | $475.00 | $XXX.XX | +X.X%  | $419 (X%) | $523 (X%) | $600 (X%)
NVDA    | $131.29 | $XXX.XX | +X.X%  | $196 (X%) | $309 (X%) | $370+ (X%)

── Orders Placed ────────────────────────────────────────

SYMBOL | Limit   | Current | Distance | Status
-------|---------|---------|----------|-------
FTNT   | $130.50 | $XXX.XX | [X%]     | [Waiting / ⚠ Near limit / ⚠ Expired]
```

---

## Step 7 — Per-flag action prompts

After the dashboard, for each 🔴 flag prompt the user:

**Stop hit:**
```
🔴 [SYMBOL] stop hit — current $[price] is below your $[stop] stop.
   → Exit at market — say "exit [SYMBOL]" and I'll update POSITIONS.md.
   → Or say "hold [SYMBOL]" to override the stop (I'll note it with today's date).
```

**Thesis-break rule triggered:**
```
🔴 [SYMBOL] thesis-break: [rule from POSITIONS.md]
   → Current price: $[price] | Rule: [e.g. "close <$199 two consecutive days"]
   → If triggered: say "exit [SYMBOL]" — do not hold past a thesis break.
```

For ⚠ NEAR LIMIT, always prompt:
```
⚠ [SYMBOL] limit order near/below current price — did your $[limit] limit fill?
   → If yes: say "filled [SYMBOL]" and I'll move it to Open and remind you to set your stop.
```

---

## Updating POSITIONS.md

Only update when user confirms:

| User says | Action |
|-----------|--------|
| "exit [SYMBOL]" | Move Open → Closed with exit price, record "stopped out at $X" |
| "hold [SYMBOL]" | Add note: "stop override [date] at $[price] — user decision" |
| "filled [SYMBOL]" | Move Orders Placed → Open with fill price, remind to set stop in broker |
| "sell half [SYMBOL]" | Note T1 partial exit in Open entry, update remaining size |
| "cancel [SYMBOL]" | Remove from Orders Placed |
