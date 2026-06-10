# Trading Learnings

Lessons captured from real trades and analysis. These are observations and context — not rules to mechanically apply. Each trade is judged on its own analysis.

> **How this file works:** Entries marked 🔵 are general observations. Entries marked 🟠 came from a specific real trade — these carry the most weight as context.

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

**The rule:** Before entering, compare current price to analyst mean target. If price is above the mean target, either wait for a pullback below it, or accept you are betting on the most optimistic scenario with no margin for error. Use the **mean target** for planning R:R and position sizing — not the high target. The high target is an outlier held by the most optimistic analyst; it belongs only as a trailing objective for a residual position after Target 1 hits, never as the basis for entry sizing.

```
Analyst consensus check:
  Current price < Analyst mean target  → Good cushion, proceed
  Current price = Analyst mean target  → Caution, size smaller
  Current price > Analyst mean target  → Wait for pullback below mean target

  For R:R and sizing: always use analyst mean as T2 baseline
  Analyst high target: only valid as a trailing target for residual position after T1 hits
```

---

### 🟠 Insider Selling Caps Position Size
*(Learned: AMD analysis June 6 2026 — CEO sold $73M, CTO sold $18.4M, zero insider purchases in 3 months)*

When a company's CEO and other senior insiders are consistently selling large amounts of stock with no one buying, it is a real signal that deserves to constrain your position size — even if the bull case is strong. These people know the actual product timelines, customer conversations, and competitive threats better than any analyst. Their revealed preference (cash over stock) is information.

This does not mean you must avoid the stock. It means you cannot size aggressively when the most informed insiders are distributing.

**The rule:** Before entering a high-valuation stock (P/E > 50×), check insider transactions for the last 90 days. If the CEO has sold >$50M with zero insider purchases across the leadership team, cap position size at 3–4% maximum regardless of the bull case quality.

```
Insider selling check (applies to high-valuation stocks, P/E > 50×):
  CEO sales in last 90 days < $20M, or insider purchases exist  → No constraint, normal sizing
  CEO sales $20M–$50M, no purchases                            → Reduce max size by 25%
  CEO sales > $50M, no purchases, multiple officers selling     → Cap at 3–4% maximum
```

---

### 🟠 High-Multiple Stocks — Count the Required Conditions
*(Learned: AMD at 156× trailing P/E, AMD analysis June 6 2026)*

When a stock trades at a very high trailing P/E (above 100×), the entire valuation rests on a chain of future assumptions all holding simultaneously. The more conditions that must hold, the more fragile the bull case — because you only need one to crack for the thesis to break and estimates to get cut.

Before sizing, enumerate the required conditions explicitly. Each one that must hold independently is a risk multiplier.

**The rule:** At P/E > 100× trailing, list every assumption required for the bull case. If there are more than 3 independent conditions that must all hold, cap position at 5% maximum.

```
AMD June 2026 example — required conditions (5 total):
  1. EPS inflects from $3.36 annualized → $13.08 forward (4× in a few quarters)
  2. MI400 ramps without Nvidia capturing incremental market
  3. Hyperscaler capex continues — no deceleration beyond Broadcom guidance
  4. China export restrictions don't escalate
  5. Rate pressure doesn't trigger further multiple compression

  5 required conditions → cap at 5% even with Overweight rating
  Bear needs only 1 to crack → asymmetric fragility at high multiples
```

---

### 🟠 Selling Winners Early, Holding Losers Forever — The Core Behavioral Mistake
*(Learned: full transaction history review, June 2026)*

The most expensive pattern in the history: profitable positions (NVDA, FTNT, GOOGL) were sold quickly, while losing positions (XRP, ADA, crypto) were held indefinitely with no exit.

- NVDA bought at $90 → sold 9 shares at $186–$214, before it reached analyst mean $309
- FTNT bought at $88 → sold 6 shares at $104–$113, before it reached $143
- XRP fell from $2.16 to $1.15 with no exit
- ADA fell from $0.62 to $0.16 with no exit

This happens because booking a profit feels good and cutting a loss feels like failure. The market rewards the opposite.

**The rule:** Don't sell because a stock is "up enough." Sell when it reaches the pre-defined target (analyst mean, resistance level). Hold the plan, not the emotion.

---

### 🟠 Crypto: When It Doubles, Sell Half
*(Learned: BTC/XRP/ADA history review, June 2026)*

Crypto moves faster and bigger than stocks. There is no analyst mean, no earnings floor, no fundamental anchor. When Fear & Greed turns, it drops from 90 to 10 in weeks.

Real examples from this portfolio:
- BTC entered at $94,136. Ran to $108,000 (+15%). Now $62,850. No partial exit taken.
- XRP entered at $2.16. Ran to $3.40 (+57%). Now $1.15 (-47%). No partial exit taken.

**The rule:** When any crypto position doubles from entry, sell half. You recover your original investment. The remaining half is house money running for free.

```
Crypto profit-taking trigger:
  Position is up 100%+ from entry  → Sell 50%, hold rest with stop at entry
  Position is up 50% from entry    → Sell 30%, move stop to entry
  Fear & Greed drops below 30      → Sell another 20–30% regardless of price
```

---

### 🟠 IPO FOMO — One Position Per Month
*(Learned: September 2025 IPO rush — 7 IPOs bought in 3 weeks)*

In Sep–Oct 2025, $3,123 was deployed across 7 new IPOs in 3 weeks with no time to research any of them properly. This is FOMO: excitement about new listings causing rushed entries without a thesis.

Results: FIGR worked (+54%), CRWV partially worked, KLAR/VIA/STUB/GEMI/FRMI all deeply underwater.

**The rule:** Maximum one new position opened per month. Research it before buying — understand the business, the lock-up expiry date, and the post-IPO selling pressure before committing capital.

```
IPO entry checklist:
  □ What does the company actually do, and is it growing revenue?
  □ When does the lock-up period expire? (90–180 days post-IPO = heavy selling)
  □ Is the current price above or below the IPO price?
  □ Have I waited for lock-up expiry selling to finish?
  □ Is this the only new position I'm opening this month?
```

---

### 🟠 Sold Quality Stock, Rebought Higher — Permanent Cost Basis Damage
*(Learned: GOOGL trade Oct–Nov 2025)*

GOOGL bought at $150 (great entry). Sold at $255–$291 to lock in profit. Immediately rebought at $276 — a higher price than the sale. The original $150 cost basis was permanently gone, replaced with a $276 entry.

This happens when you sell a quality company but still believe in it. The result: pay taxes on the gain, lose the low entry, rebuild at a worse price.

**The rule:** If you sell a quality stock for profit because you want to "take gains," don't buy it back in the same week. Either hold it or exit it. If you sell and immediately rebuy higher, you've paid taxes for nothing.

---

### 🔵 How to Find Support — Before Adding to Any Existing Position
*(Applied whenever considering adding more shares to a current holding)*

**Support level** = price floor where buyers historically step in. Adding to a position is only valid when price pulls back to a real support level — not just because it dropped from a recent high.

**3 ways to identify support (check at least 2 before adding):**

**Method 1 — Chart bounces**
Open Yahoo Finance or TradingView. Set chart to 3–6 month view. Look for price levels where the stock touched and bounced back up at least twice. The more bounces, the stronger the support.

**Method 2 — Moving averages (dynamic support)**
- 50-day MA = medium-term support
- 200-day MA = long-term support
If stock is in an uptrend and pulls back to touch the 50-day MA with volume shrinking = strong add candidate.

**Method 3 — Prior consolidation zone**
Where did the stock trade sideways for 2+ weeks before a big move? That range becomes support on the way back down.

**Step 1 — Find support levels FIRST (before watching price)**

Open TradingView (free) → search the stock → 6 month chart → add two indicators:
- MA 50 (50-day moving average line)
- MA 200 (200-day moving average line)

Wherever those lines sit = your support levels. Read the price off the line.

Also look for: price levels where stock bounced 2+ times before (chart bounces), and flat sideways zones (prior consolidation).

Write down your support levels before anything happens. Set a price alert in your broker at those levels.

```
NVDA example:
  Support Level 1: ~$204  (50-day MA)
  Support Level 2: ~$189  (200-day MA)
  → Set price alerts at both levels
  → Forget it, live your life, wait for alert
```

**Step 2 — When price alert triggers, run all 5 checks**

Price reaching support = yellow light (start watching). NOT a buy signal yet.

```
Stock has pulled back to support. Should I add?

  □ RSI between 40–55? (cooled down, not overbought)
  □ Volume below average? (sellers exhausted)
  □ 2 consecutive green closes at this level? (buyers confirmed)
  □ MA line holding? (price above 50MA or 200MA, not broken)
  □ Original thesis still intact? (earnings still growing?)

  ALL 5 GREEN → ADD
  ANY 1 RED   → Wait one more day, recheck
```

**The traffic signal:**
| Signal | Meaning |
|---|---|
| Price reaches support | Yellow — slow down, start watching |
| All 5 checks pass | Green — add now |
| Any check fails | Red — wait one more day |

**200-day MA — special rule:**
The 200 MA is watched by every fund and institutional investor. When price drops to it and holds = one of the strongest add signals in the market.

But if price **breaks below** 200 MA and closes below it 2 consecutive days → do NOT add. That is a breakdown, not a bounce. Exit or reduce instead.

```
200 MA holding (closes above it) → strong add signal
200 MA broken (2 closes below)   → warning, reduce position
```

**What is NOT a valid reason to add:**
- Stock dropped from a recent high (not the same as reaching support)
- You want a lower average (averaging for the sake of averaging)
- It "feels cheap" compared to where you bought

**Support vs breakdown — how to tell:**
| Signal | Pullback — add | Breakdown — wait |
|--------|---------------|-----------------|
| Volume | Shrinking as price falls | High on down days |
| Price action | Bouncing at a clear level | Cutting through levels |
| Moving averages | Holding above 50-day MA | Breaking below 50-day MA |
| Green closes | 2 consecutive green closes | Lower lows every day |

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
                → price CLOSES above Tranche 1 zone (not just intraday touch)
                → price holds Tranche 1 zone for 2+ days
                → RSI stays above 40
                → no new negative catalyst

  Intraday touches of support that don't hold into the close are whipsaws.
  Always wait for the daily close to confirm support is holding before adding.
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
    → Sell 35–40% of position (standard)
    → Move stop up to just below major support (e.g., Bollinger midline)
    → Let remaining position run to Target 2

  Exception — thin R:R to T1 (R:R < 1.5:1 to T1 but > 2.5:1 to T2):
    → Sell 50% at Target 1 instead of 35–40%
    → Trail remaining 50% toward Target 2 with a tighter trailing stop
    → This locks in more profit early when T1 is close to entry,
      while keeping participation if T2 is far enough to justify the trade
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

## 11. ANALYSIS VALIDITY & WEEKLY CYCLE

```
ANALYSIS IS VALID FOR 5 TRADING DAYS (1 WEEK) ONLY

After analysis gives you an entry zone (e.g. $430–$445):

  Days 1–5:
    Price inside zone AND 2 calm days?  → Enter
    Price left zone (up or down)?       → Do NOT chase. Move on.
    Week ends, never entered?           → Re-run analysis on Day 6

  Day 6+: Analysis is stale. Re-run before doing anything.
```

### What "2 calm days" means
```
  Calm day = volume below 25M AND price move less than 1×ATR in the day
  Not calm = big red/green candle, volume spike, news event
```

### The weekly cycle (repeat forever)
```
  Week 1: Watch entry zone for 5 days
            2 calm days inside zone → enter
            Never entered           → re-run analysis

  Week 2: New analysis, new zone, same 2-calm-day rule
            Repeat until entered or thesis changes
```

### What to do when price moves out of zone
```
  Price goes UP above zone  →  Don't chase. Existing position benefits. No new entry.
  Price drops below zone    →  Do NOT enter. Risk has increased. Watch your stop.
  Price hits stop loss      →  Broker exits automatically. Accept the loss.
```

### After stop loss triggers — re-entry cycle
```
  Stop hit → position closed
           → Wait 2 calm days for price to stabilize
           → THEN re-run analysis
           → Treat it as a completely fresh trade
           → No averaging, no memory of previous loss
           → New entry zone, new stop, new targets
```

### Each entry is fully independent
```
  Every entry has its own stop and its own targets.
  The $475 lot and the $440 lot are separate trades.
  Stop hit on one does not affect the other.
  Never adjust a stop downward to "save" a losing position.
```

### After Target 1 hits
```
  Sell half at Target 1
  Move stop up to breakeven (your entry price) for remaining half
  Let remaining half run to Target 2
```

---

## 10. ONE-PAGE CHECKLIST (Print This)

```
BEFORE ENTERING
  □ Cooldown confirmed (2 green closes + RSI 45–55 + volume shrinking)
  □ Entry is at a key support level (VWMA / BB mid / consolidation zone)
  □ Stop loss calculated (1.5×ATR below entry)
  □ R:R is at least 1.5:1 to Target 1 (use analyst MEAN for T2, not high target)
  □ Position size calculated (1–2% portfolio risk max)
  □ Beta adjusted (reduce size if Beta > 2)
  □ Insider check (P/E > 50×): CEO sold > $50M in 90 days? → cap at 3–4%
  □ Conditions check (P/E > 100×): more than 3 required assumptions? → cap at 5%
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
