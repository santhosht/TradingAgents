# Entry & Stop Check Process

**Trigger:** User says "stop check", "check stops", "check positions", "entry check", or "position monitor"

**Purpose:** Two-part scan — (1) fast stop/target check on all Open positions, (2) entry readiness check on all Pending positions with live prices + fresh news.

**Key rules:**
- Open positions: price vs stops and targets
- Pending positions: price vs entry zones + breakout alts + recent news (web search, last 48–72h)
- Orders Placed: quick fill-status check
- No stop-limit orders are set in broker — these checks ARE the stop enforcement mechanism
- If a stop is hit: surface it immediately and ask "did you want to exit?"
- Never update POSITIONS.md unless user confirms an action
- Fetch all symbols in parallel — do not serialize

---

## Part 1 — Stop & Target Check (Open Positions)

### Step 1 — Read POSITIONS.md

Extract all **Open** positions. For each:
- Symbol
- All entries (entry price, stop, size)
- Target 1, Target 2
- Thesis-break exit rule (if defined)

---

### Step 2 — Fetch live prices (all Open symbols in parallel)

For each symbol run:

```bash
python3 analysis/fetch_live_data.py SYMBOL
```

Outputs: current price, day change %, volume, RSI, MACD, EMA10, ATR, last 5 days candles.

Fetch all symbols in parallel — one subprocess per symbol.

---

### Step 3 — Evaluate each entry

For each entry calculate:
- P&L % = (current − entry) / entry × 100
- Stop distance % = (current − stop) / current × 100
- T1 distance % = (T1 − current) / current × 100
- T2 distance % = (T2 − current) / current × 100

Apply flags:

| Condition | Flag |
|-----------|------|
| price ≤ stop | 🔴 STOP HIT — exit immediately |
| price within 2% above stop | 🟠 STOP CLOSE — $[stop] is [X%] away |
| price within 3% below T1 | 🟢 T1 NEAR — ready to sell half at $[T1] |
| price ≥ T1 (not yet taken) | 🟢 T1 REACHED — sell half now |
| price ≥ T2 (not yet taken) | 🟢 T2 REACHED — sell remaining now |
| thesis-break rule triggered | 🔴 THESIS BREAK — [specific condition] |

---

### Step 4 — Output: Stop & Target Dashboard

```
Stop & Target Check — [date] [time]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SYMBOL  | Entry    | Current  | P&L    | Stop      | → T1     | → T2
--------|----------|----------|--------|-----------|----------|--------
AMD     | $475.00  | $XXX.XX  | +X.X%  | $419 (X%) | $523 (X%)| $600 (X%)
NVDA    | $201.00  | $XXX.XX  | +X.X%  | $189 (X%) | $235 (X%)| $298 (X%)

⚠ Flags:
  🔴 AMD — STOP HIT — current $XXX below stop $419 — did you want to exit?
  🟠 NVDA — STOP CLOSE — stop $189 is 1.8% away — watch closely
  🟢 AMD — T1 NEAR — $523 target is 2.1% away — ready to sell half
```

If no flags → show: `✓ All positions inside stops, no targets triggered.`

---

### Step 5 — Per-flag action prompts

After the dashboard, for each 🔴 flag prompt the user:

**Stop hit:**
```
🔴 [SYMBOL] stop hit — current $[price] is below your $[stop] stop.
   → Do you want to exit? Say "exit [SYMBOL]" and I'll update POSITIONS.md.
   → Or say "hold [SYMBOL]" if you've decided to override the stop (I'll note it).
```

**Thesis-break rule triggered:**
```
🔴 [SYMBOL] thesis-break rule: [rule from POSITIONS.md].
   → Current price: $[price] | Rule: [e.g., "close <$199 two consecutive days"]
   → Did this trigger? If yes, say "exit [SYMBOL]" — do not hold past a thesis break.
```

---

## Part 2 — Entry Check (Pending Positions)

### Step 6 — Read POSITIONS.md Pending section

Extract all **Pending** positions. For each:
- Symbol
- Suggested entry range
- Breakout alt (trigger price + volume threshold)
- Stop on fill
- Stale-after date
- Any special status (e.g., "WATCH AND WAIT" with conditions)

---

### Step 7 — Fetch live prices + news (all Pending symbols in parallel)

For each Pending symbol, run in parallel:

```bash
python3 analysis/fetch_live_data.py SYMBOL
```

And web search: `[SYMBOL] [company name] news site:finance.yahoo.com OR site:reuters.com OR site:bloomberg.com`
(last 48–72 hours — surface any earnings, guidance, analyst actions, sector news, M&A)

---

### Step 8 — Evaluate each Pending entry

Check price against:
1. **Dip entry** — is current price at or below the suggested entry range?
2. **Breakout alt** — is price within 3% of breakout trigger, or past it?
3. **Stale** — is today's date past the stale-after date?
4. **Watch & wait** — does the entry have an explicit "do not enter yet" condition?

Apply flags:

| Condition | Flag |
|-----------|------|
| price ≤ entry range top | 🟢 ENTRY ZONE — price at $[X], suggested entry $[Y]–$[Z] |
| price within 3% of breakout trigger | 🚀 BREAKOUT NEAR — $[X] trigger, [Y%] away — watch close |
| price ≥ breakout trigger (check volume) | 🚀 BREAKOUT TRIGGERED — close >$[X] on vol >[Y]M — execute alt entry |
| price well above entry, breakout not near | ⚪ TOO FAR — original entry $[X] is [Y%] below current, no breakout signal |
| stale-after date passed | 🗑 STALE — report expired [date], re-analyze before acting |
| explicit watch-and-wait status | ⏸ WATCH & WAIT — [condition from POSITIONS.md] |

---

### Step 9 — Output: Entry Dashboard

```
Entry Check — Pending Positions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SYMBOL  | Entry Zone      | Current  | Breakout Alt    | Status
--------|-----------------|----------|-----------------|--------
FTNT    | $130.50         | $145.06  | >$150.07 vol>7.5M | 🚀 BREAKOUT NEAR (3.4% away)
ADBE    | $212–$218       | $XXX.XX  | >$248.57 vol>8M   | ⏸ WATCH & WAIT
MKC     | $46.80          | $XXX.XX  | —               | 🟢 ENTRY ZONE / ⚪ TOO FAR

📰 News highlights:
  FTNT: [headline — date] ← supports / watch / negative
  ADBE: [headline — date] ← [relevance to wait condition]
  MKC:  [headline — date] ← [relevance]
```

For each 🟢 or 🚀 flag, add a one-line action prompt:
```
  → FTNT BREAKOUT NEAR: if close >$150.07 on vol >7.5M today → buy 2% at $151–$153, stop $141
  → MKC ENTRY ZONE: price at suggested entry — any negative news? If clean, consider placing limit.
```

For each ⏸ flag, surface the wait condition:
```
  ⏸ ADBE WATCH & WAIT: waiting for (1) new CEO named, (2) Q3 guidance from new management.
     Current price $[X] vs entry zone $212–$218. No order until conditions met.
     📰 [any news about CEO search or management changes]
```

---

## Part 3 — Orders Placed Check

### Step 10 — Orders Placed quick status

After Open + Pending sections, check Orders Placed:

```
Orders Placed — quick status:
  AVGO  limit $360 | current $XXX — [X%] above/below limit — [Not filled / ⚠ Near limit / ⚠ Expired]
```

Flag if:
- Price ≤ limit + 2% (may have filled — confirm with broker)
- Expiry date has passed

---

## Updating POSITIONS.md

Only update when user confirms:

| User says | Action |
|-----------|--------|
| "exit [SYMBOL]" | Move Open → Closed with exit price, record "stopped out at $X" |
| "hold [SYMBOL]" | Add note to Open entry: "stop override [date] at $[price] — user decision" |
| "filled" (on orders) | Move Orders Placed → Open, add fill price, remind to set stop manually in broker |
| "sell half [SYMBOL]" | Note T1 partial exit in Open entry, update size |
| "place order [SYMBOL]" | Move Pending → Orders Placed with limit price and expiry |
