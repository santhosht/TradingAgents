# Trading Rules — Simple Reference Guide

A practical, symbol-agnostic cheatsheet for entries, exits, hold periods, and cooldowns.

> **How this file works:** Rules marked 🔵 are general theory. Rules marked 🟠 came from a real trade or analysis — these are the ones that actually matter.

---

## REAL LESSONS (experience-derived)

### 🟠 Sector Contagion — Don't Buy on the Panic Day
*(Learned: AMD selloff June 5 2026, triggered by Broadcom earnings miss)*

When a major company in a sector reports bad earnings, the whole sector sells off together — even companies that did nothing wrong. This is contagion: the market panics and sells the entire group.

**The rule:** When a peer company reports bad news, wait 1–2 days before entering any stock in that sector. The panic selling will finish, and the price will still be at a good level — you don't need to catch the exact bottom.

```
Contagion check before entry:
  Did a major peer report bad earnings in the last 2 days?
  YES → Wait 2 days minimum before entering any stock in that sector
  NO  → Proceed with normal entry checklist
```

---

### 🟠 Above Analyst Consensus = No Cushion
*(Learned: AMD at $487 vs analyst mean target $482, June 5 2026)*

Analysts who cover a stock full-time — they talk to management, build detailed models, know the business inside out — publish a "fair value" price called the mean target. If the stock is already trading above that number, you are paying more than what the average expert thinks it's worth. Any small piece of bad news brings the stock straight back down — and you're immediately in a loss with no buffer.

**The rule:** Before entering, compare current price to analyst mean target. If price is above the mean target, either wait for a pullback below it, or accept you are betting on the most optimistic scenario with no margin for error.

```
Analyst consensus check:
  Current price < Analyst mean target  → Good cushion, proceed
  Current price = Analyst mean target  → Caution, size smaller
  Current price > Analyst mean target  → Wait for pullback below mean target
```

---

## 1. BEFORE YOU ENTER — The Cooldown Check

After any stock has fallen hard, run all 3 checks before entering:

```
COOLDOWN FORMULA

  ✓ Price   : 2 consecutive green closes (close > previous close)
  ✓ RSI     : Reset to 45–55 range
  ✓ Volume  : Current day volume < 60% of recent selloff day volume

  ALL 3 GREEN = safe to enter
  ANY 1 RED   = wait one more day, recheck
```

### RSI Cheatsheet
| RSI Value | What it means | Action |
|-----------|--------------|--------|
| Above 70 | Overbought — rally extended | Do not buy, wait for pullback |
| 55–70 | Bullish momentum | Can enter on dips |
| 45–55 | Neutral — cooled down | Best entry zone after a pullback |
| 40–45 | Mild oversold | Can enter, but confirm 2 green closes first |
| Below 40 | Oversold / panic | Wait — can drop further before bouncing |

### Volume Cheatsheet
| Volume vs Average | Signal |
|-------------------|--------|
| 2× average or more | Panic selling or euphoric buying — do not chase |
| 1.2–2× average | Active trend day — wait for confirmation |
| 0.8–1.2× average | Normal — neutral |
| Below 0.6× average | Sellers/buyers exhausted — consolidation |

---

## 2. ENTRY RULES

```
ENTRY FORMULA

  Entry price = key support level (VWMA, Bollinger mid, prior consolidation zone)
  Entry type  = LIMIT ORDER only (never market buy into a falling stock)
  Entry style = staged (2 tranches is safer than all-in)

  Tranche 1 = 50–60% of intended position at primary support
  Tranche 2 = remaining 40–50% only if:
                → price holds Tranche 1 zone for 2+ days
                → RSI stays above 40
                → no new negative catalyst
```

### Key Support Levels to Look For (in priority order)
1. **VWMA 20** — volume-weighted cost basis of recent buyers (strongest)
2. **Bollinger Midline** — dynamic mean-reversion line
3. **Prior consolidation zone** — price that traded sideways before the rally
4. **EMA 10** — short-term momentum floor
5. **Round numbers** — $400, $450, $500 etc. — act as psychological support

### Entry Red Flags — Do NOT Enter If:
- Stock is down >3% intraday and still falling
- Volume is 2× normal on a down day (panic selling not done)
- RSI still above 60 after a pullback (not cooled)
- Price is below VWMA AND Bollinger midline (two supports broken)
- No clear floor — lower lows every day

---

## 3. STOP LOSS RULES

```
STOP LOSS FORMULA

  Stop = Entry price − (1.5 × ATR)

  ATR = Average True Range over 14 days
        (represents normal daily price noise for that stock)

  Example:
    Entry = $472
    ATR   = $29
    Stop  = $472 − (1.5 × $29) = $472 − $43.5 = $428.50 → use $428

  NEVER set stop tighter than 1.5×ATR — you will be stopped out by noise
  NEVER set stop looser than 2.5×ATR — risk becomes unmanageable
```

### Stop Loss Rules
| Rule | Detail |
|------|--------|
| Set it immediately | Place stop order the moment your limit buy fills |
| Never move down | If you widen the stop, you're changing the trade's risk profile |
| Move UP only | Trail stop upward after Target 1 hits |
| Hard stop | Treat it as automatic — no emotional override |

### Trailing Stop After Target 1
```
  After price reaches Target 1:
    → Sell 35–40% of position
    → Move stop up to just below major support (e.g., Bollinger midline)
    → Let remaining position run to Target 2
```

---

## 4. POSITION SIZING RULES

```
POSITION SIZE FORMULA

  Max position size = 2% portfolio risk rule

  Shares = (Portfolio × Risk%) / (Entry − Stop)

  Example:
    Portfolio  = $100,000
    Risk %     = 1% ($1,000 max loss)
    Entry      = $472
    Stop       = $428
    Risk/share = $44

    Shares = $1,000 / $44 = 22 shares
    Dollar value = 22 × $472 = $10,384 = 10.4% of portfolio

  Adjust down for high-Beta stocks (Beta > 2):
    High Beta → reduce position size by 30–50%
    Beta 2.5 stock → treat as if risk/share is 2.5× higher
```

### Beta Adjustment Table
| Beta | Position size adjustment |
|------|------------------------|
| Below 1.0 | Can use full calculated size |
| 1.0–1.5 | Reduce by 10–20% |
| 1.5–2.0 | Reduce by 20–35% |
| 2.0–2.5 | Reduce by 35–50% |
| Above 2.5 | Reduce by 50%+ — treat as high-risk |

---

## 5. PROFIT TARGET RULES

```
TARGET FORMULA

  Minimum R:R to enter a trade = 1.5:1

  R:R = (Target − Entry) / (Entry − Stop)

  Example:
    Entry  = $472
    Stop   = $428  → Risk  = $44
    Target = $546  → Reward = $74
    R:R    = $74 / $44 = 1.68:1  ✓ (above 1.5 minimum)

  If R:R < 1.5:1 → do not take the trade, entry price is too high
```

### Target Setting Guidelines
| Target | Where to set it | Action at target |
|--------|----------------|-----------------|
| Target 1 | Next major resistance (prior high, round number) | Sell 35–40% of position |
| Target 2 | Analyst consensus high or 2× the risk from entry | Sell 35–40% of position |
| Remainder | Hold with trailing stop | Exit when trailing stop hits |

---

## 6. HOLD PERIOD RULES

```
HOLD PERIOD FRAMEWORK

  Time horizon = based on your target, not a calendar date

  Short-term trade  : Target 1 only, exit fully → days to weeks
  Medium-term trade : Target 1 partial + Target 2 → weeks to 3 months
  Long-term trade   : Full pyramid, trailing stop → 6–12 months
```

### When to EXIT Before Your Target (Override Rules)
These override the hold period — exit immediately if any occur:

1. **Earnings miss** — revenue or EPS below your pre-defined threshold
2. **Stop loss hit** — no exceptions, no "give it one more day"
3. **Thesis broken** — the specific reason you bought is no longer true
4. **Two consecutive closes below major support** — VWMA or Bollinger midline
5. **Sector leadership collapses** — your stock's sector goes from #1 to last place

### What to Ignore During Hold (Do NOT exit for these)
- Normal daily moves within ATR range
- News headlines that don't affect revenue or earnings
- Social media sentiment (Reddit, StockTwits panic posts)
- The fact that another stock is doing better
- The stock going up then pulling back slightly

---

## 7. EARNINGS CHECK RULE

Every earnings report, run this 2-number test:

```
EARNINGS FORMULA

  Revenue  > Previous quarter revenue  → HOLD signal
  EPS      > Previous quarter EPS      → HOLD signal

  Both growing   → Hold, thesis intact
  One flat       → Hold with caution, reduce position by 25%
  One declining  → Cut position to half
  Both declining → EXIT fully
```

---

## 8. COOLDOWN DECISION TREE (Quick Reference)

```
Is price making lower lows day after day?
├── YES → Wait. Not cooled. Check again tomorrow.
└── NO  →
        Is RSI above 55?
        ├── YES → Wait. Momentum not reset yet.
        └── NO  →
                Is today's volume elevated (>1.2× average)?
                ├── YES → Wait. Sellers still active.
                └── NO  →
                        Do you have 2 consecutive green closes?
                        ├── NO  → Wait one more day.
                        └── YES → COOLED. Calculate entry, stop, size → ENTER.
```

---

## 9. QUICK FORMULAS SUMMARY

```
Stop Loss        = Entry − (1.5 × ATR)
Position Shares  = (Portfolio × 1%) / (Entry − Stop)
R:R Ratio        = (Target − Entry) / (Entry − Stop)
Min R:R to enter = 1.5:1
Cooldown RSI     = 45–55
Cooldown Volume  = below 60% of selloff day volume
Tranche 2 rule   = only add if price holds Tranche 1 zone for 2+ days
Trailing stop    = move up to prior support after Target 1 hits
Earnings rule    = Revenue AND EPS both growing → hold
```

---

## 10. ONE-PAGE CHECKLIST (Print This)

```
BEFORE ENTERING
  □ Cooldown confirmed (2 green closes + RSI 45–55 + volume shrinking)
  □ Entry is at a key support level (VWMA / BB mid / consolidation zone)
  □ Stop loss calculated (1.5×ATR below entry)
  □ R:R is at least 1.5:1 to Target 1
  □ Position size calculated (1–2% portfolio risk max)
  □ Beta adjusted (reduce size if Beta > 2)
  □ Limit order placed (NOT market order)

AFTER ENTRY
  □ Stop loss order placed immediately
  □ Target 1 sell order placed
  □ Earnings date noted — know your revenue/EPS thresholds

DURING HOLD
  □ Ignore daily noise within ATR range
  □ Check earnings report when it comes — apply earnings formula
  □ Move stop up only after Target 1 hits

EXIT TRIGGERS (immediate, no debate)
  □ Stop loss hit
  □ Earnings miss (revenue OR EPS declining)
  □ Two consecutive closes below VWMA
  □ Original thesis no longer valid
```
