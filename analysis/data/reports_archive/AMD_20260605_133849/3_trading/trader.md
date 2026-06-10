# Agent 8 — Trader
**Ticker:** AMD | **Date:** 2026-06-05 | **Run ID:** AMD_20260605_133849

---

## Transaction Proposal

### Action: BUY (Limit, Staged Entry)

---

## Reasoning

The Research Manager has issued an **Overweight** rating — constructive but not a reckless chase. My job as Trader is to translate that into a concrete, executable transaction with specific prices, stops, and sizing.

The key facts I anchor on:

**Technical:**
- EMA-10 at $503.63 — primary short-term support
- ATR at $29.38 — minimum stop distance 1.5×ATR = $44.07
- June 4 intraday low $499.87 — market tested and held the $500 level
- MACD histogram +0.84 — momentum has paused, not reversed
- RSI 67 — not overbought, approaching zone

**Fundamental:**
- Q1'26 FCF: $2.566B — business is cash generative and real
- Forward EPS: $13.01 — massive earnings inflection, if it materializes
- Forward P/E: 38.21x — reasonable for the growth rate
- Analyst consensus: STRONG BUY, mean target $482, high target $665

**Setup:**
AMD pulled back from $542.52 ATH to $523.20 close on June 4 — a controlled -3.56% on moderate volume (29M), following Broadcom-driven sector contagion. The intraday recovery from $499.87 to $523.20 in a single session shows strong buying support at the $500 level. This is the entry zone.

---

## Entry

### Primary Limit Order
**Entry price: $499 – $507 (midpoint $503)**

Set a limit buy order at **$503** (GTC — Good Till Cancelled, valid 5 trading days).

- $503 is the EMA-10 to-the-dollar — the most precise support level in the current structure
- $499–$507 provides an adequate range given the $29.38 daily ATR; $503 is the optimal limit within this range
- This entry is not a market order — it requires a pullback from the current $523.20 close. A retest of the EMA-10 zone is likely within the next 3–5 trading days given the sector headwinds
- Do not chase above $510 with a limit order — if the stock gaps up without revisiting $499–$507, move to the breakout entry instead

### Breakout Entry (Alternative — if primary entry never fills)
**Entry price: $547 on a close above $545 with volume >35M**

If AMD rallies without pulling back to $503:
- Wait for a daily close above the June 3 ATH of $542.52 with volume confirming (>35M shares)
- Buy at market open the following morning with a limit not exceeding $547
- This is a momentum entry, not a value entry — size it at 50% of the primary position size

---

## Stop Loss

### Hard Stop: $459

Calculation: $503 (entry midpoint) - $44.07 (1.5 × ATR $29.38) = **$458.93, rounded to $459**

- Place the stop loss as a stop-market order immediately after the limit fill
- This stop is $44 below entry — enough buffer to survive a bad sector day (1.5 ATR is approximately 1.5 days of worst-case noise)
- Do NOT move this stop downward under any circumstances
- Only trail the stop upward after AMD holds $550 for 5 consecutive days (trail to $510 at that point)

The $459 stop level also has technical significance: it sits below the May 19 close of $414, May 20 open of $428, and the VWMA-20 region around $467 — if AMD trades at $459, the trend has materially broken, not merely pulled back.

**For breakout entry at $547:** Stop moves to $500 — below the critical $499.87 intraday support tested June 4. A close below $500 after a breakout entry signals the breakout was false.

---

## Position Sizing

**Recommended: 4% of total portfolio**

Rationale:
- AMD Beta = 2.49: the stock moves 2.49x the S&P 500; on a bad market day, AMD can fall 12–15%
- ATR $29.38 on a $503 entry = 5.8% daily range — extreme
- Risk per share = $503 - $459 = $44 per share
- At 4% portfolio allocation and a $459 stop, if stopped out you lose approximately: (4% × portfolio) × ($44/$503) = 4% × 8.7% = **~0.35% of total portfolio**. This is a controlled, tolerable loss on a single position.

**Maximum allowed:** 6% of portfolio. Beyond that, AMD's volatility makes the position psychologically and mechanically unmanageable.

**Staged approach:** Consider entering 2% at $499–$507, holding the other 2% in reserve:
- If AMD pulls further to $467–$475, deploy the remaining 2% (Bollinger midline/VWMA zone)
- Average entry improves, stops remain the same

---

## Transaction Summary

| Parameter | Value |
|-----------|-------|
| Action | BUY (Limit) |
| Primary Entry | $499–$507 (limit at $503) |
| Breakout Entry | $547 (only on close >$545, vol >35M) |
| Stop Loss | $459 (hard, do not adjust down) |
| Target 1 | $590 (4–8 weeks) |
| Target 2 | $650 (3–5 months) |
| Position Size | 4% of portfolio (max 6%) |
| Risk per Trade | ~0.35% of portfolio if stopped out |
| R:R at $503 entry | ($590–$503) / ($503–$459) = $87/$44 = **2.0:1** |
| R:R at $503 to T2 | ($650–$503) / ($503–$459) = $147/$44 = **3.3:1** |
| ATR used | $29.38 |
| Stop distance | 1.5 × ATR = $44.07 |
| Beta | 2.49 — size conservatively |

---

## Risk Notes

1. **Earnings risk is binary:** AMD's next earnings report will confirm or deny the $13.01 forward EPS path. Do not hold a full position through earnings without confirming the thesis first. Consider reducing to 2% if holding through the earnings date.

2. **Sector contagion risk:** Broadcom's selloff demonstrates AMD can decline 5–10% in a day on non-AMD news. The $459 stop absorbs this; if the stop is not in place, you are exposed to gap-down risk.

3. **Above consensus risk:** At $523, AMD is above analyst mean targets. If a major bank downgrades or reduces target, the stock can reprice quickly. The EMA-10 entry at $503 buys you a $20 buffer below current price.

4. **Breakout entry is higher risk:** If entering at $547 (breakout), the R:R to Target 1 ($590) is only ($590–$547)/($547–$500) = $43/$47 = 0.9:1. Only use the breakout entry for a smaller position (2% max) on strong volume confirmation.
