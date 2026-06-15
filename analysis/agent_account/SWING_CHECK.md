# Swing Check Process

**Trigger:** User says "swing check SYMBOL"

**Purpose:** Quick swing trade decision on top of an existing analysis. Reads decision.md, fetches live price and light news, answers 5 swing-specific questions, and gives one clear BUY / WAIT / SKIP recommendation with exact order parameters for the $1000 agent account.

**Key rules:**
- If no analysis report found for SYMBOL → stop immediately, tell user: "No analysis found for SYMBOL — run full analysis first"
- decision.md is the only report file needed — do not read other report files
- Always fetch a fresh live price — never use cached data
- Output is 1 page max — no long explanations
- Always write output to `analysis/data/checks/swing/SYMBOL.md`

---

## Step 1 — Check for existing analysis

Scan `analysis/data/reports/SYMBOL_*/` for any existing report folder.

- **No folder found** → stop. Tell user: "No analysis found for SYMBOL — run full analysis first." Do not proceed.
- **Folder found** → pick the highest timestamp folder. Read `5_portfolio/decision.md` only.

Extract from decision.md:
- Entry zone (low and high)
- Stop loss
- T1 target
- T2 target
- Time horizon
- Key risk (the one thing that invalidates the thesis)
- ATR (if mentioned in stop logic)

---

## Step 2 — Fetch live price and technicals

```bash
python3 analysis/fetch_live_data.py SYMBOL
```

Extract: current price, RSI, MACD (value, signal, histogram), EMA10, ATR, Bollinger (upper, mid, lower), VWMA20, last 5 days candles (price, volume, move%).

---

## Step 3 — Fetch light news

```
WebFetch: https://finviz.com/quote.ashx?t=SYMBOL
Extract: top 3 headlines, dates, any earnings date, any analyst PT change in last 7 days
```

---

## Step 4 — Answer the 5 swing questions

Using decision.md + live data + news, answer each:

**Q1 — Is momentum turning right now?**
- MACD histogram: narrowing toward zero (turning) or widening (still falling)?
- RSI: below 35 and flattening or starting to rise?
- Last 5 days candles: at least 1 green day after 2+ red days?
- Verdict: TURNING / NEUTRAL / STILL FALLING

**Q2 — Near-term catalyst within 14 days?**
- Earnings date within 14 days? (check Finviz)
- Named catalyst in decision.md within 14 days? (Fed meeting, product launch, index inclusion, earnings)
- Any analyst PT change in last 7 days?
- Verdict: YES — [what and when] / NO

**Q3 — Specific entry trigger**
- If price is IN entry zone and RSI < 40 and at least 1 green day in last 5: → enter at market open next session
- If price is IN entry zone but RSI > 40 or no green day yet: → wait for first green close, then enter next morning
- If price is ABOVE entry zone but within 2%: → set limit at entry zone top, wait for pullback
- If price is ABOVE entry zone by more than 2%: → SKIP (missed the entry)
- If price is BELOW entry zone: → WAIT (falling, not yet at support)

**Q4 — Expected days to T1 based on ATR**
- Daily range to T1 = T1 price − current price
- ATR days = range to T1 ÷ ATR (rounded up)
- If ATR days ≤ 14 trading days: feasible swing target
- If ATR days > 14 trading days: T1 is too far for a swing — use a closer target (midpoint between entry and T1)

**Q5 — Resistance between entry and T1?**
- Check: EMA10, VWMA20, Bollinger mid — are any of these between current price and T1?
- If yes: note as partial resistance — price may stall there before reaching T1
- These are not blockers, just levels to watch

---

## Step 5 — Final decision

Combine all 5 answers into one decision:

**BUY** — all of:
- Price in entry zone (or within 2% above with limit set)
- Momentum TURNING or at least NEUTRAL
- ATR days to T1 ≤ 14
- Key risk from decision.md is not currently firing

**WAIT** — any of:
- Price not yet in zone (still falling toward it)
- Momentum STILL FALLING (MACD widening, no green day)
- Near-term catalyst within 3 days that could move against the thesis

**SKIP** — any of:
- Price more than 2% above entry zone (missed)
- Price below stop loss level
- Key risk from decision.md has fired (named event happened)
- No analysis found (already handled in Step 1)

---

## Step 6 — Conviction scoring and allocation

Score the BUY signal to determine how much to allocate. Do not allocate equally — size by conviction.

**Conviction score — High / Medium / Low:**

| Score | Conditions | Suggested allocation |
|-------|-----------|---------------------|
| High | R:R ≥ 2:1 AND momentum TURNING AND catalyst present | $250–$300 |
| Medium | R:R ≥ 1.5:1 AND momentum TURNING or NEUTRAL | $150–$200 |
| Low | R:R < 1.5:1 OR momentum NEUTRAL only, no catalyst | $75–$100 |

Rules:
- Low conviction → allocate minimum or skip; do not force deploy cash
- Remaining cash after allocation stays idle — do not fill for the sake of filling
- The agent account scan process (AGENT_ACCOUNT.md) reads this conviction score to rank across all candidates

**Calculate order parameters:**

```
Conviction:    [High / Medium / Low]
Allocation:    $[X] (based on conviction above)
Entry:         $[price] limit
Shares:        [allocation ÷ entry price, 3 decimal places]
Stop order:    $[stop from decision.md]
Target order:  $[swing target] — use T1 if ATR days ≤ 14, else midpoint
Risk $:        (entry − stop) × shares
Reward $:      (target − entry) × shares
R:R:           reward ÷ risk
```

---

## Step 7 — Write output

Overwrite `analysis/data/checks/swing/SYMBOL.md`:

```
Swing Check — SYMBOL — [date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Based on: analysis/data/reports/SYMBOL_[timestamp]
Report age: [X] trading days

── Decision ─────────────────────────────────────────────

🟢 BUY  /  ⏳ WAIT  /  ⛔ SKIP
[one line reason]

── Live Data ────────────────────────────────────────────

Price:    $[X]  ([+/-X%] today)
RSI:      [X]   ([oversold / neutral / overbought])
MACD:     [TURNING / NEUTRAL / STILL FALLING] — histogram [narrowing / widening]
Bollinger:[near lower / mid / near upper]

── Swing Questions ──────────────────────────────────────

Q1 Momentum:   [TURNING / NEUTRAL / STILL FALLING] — [reason]
Q2 Catalyst:   [YES — earnings Jun 22 / NO]
Q3 Entry:      [Enter at market / Wait for green close / Set limit $X / SKIP]
Q4 ATR days:   [X] days to T1 ($[T1]) — [feasible / use midpoint $X instead]
Q5 Resistance: [EMA10 $X in the way / Clear path to T1]

── Order Parameters ($1000 account) ─────────────────────

Conviction:    [High / Medium / Low]
Allocation:    $[X]
Entry limit:   $[X]
Shares:        [X.XXX] (fractional)
Stop order:    $[X]
Target order:  $[X]
Risk:          $[X]
Reward:        $[X]
R:R:           [X]:1
```
