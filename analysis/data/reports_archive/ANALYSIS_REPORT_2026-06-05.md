# TradingAgents Analysis Report — June 5, 2026

**Session:** Multi-stock AI analysis using TradingAgents (LangGraph pipeline)  
**Model:** Gemini `gemini-3.1-flash-lite` (free tier, 500 RPD)  
**Analyst (me):** Claude Sonnet 4.6 — parallel independent analysis at each stage  
**Stocks covered:** AVGO (Broadcom), TSM (Taiwan Semiconductor), AMD  
**Note:** NVDA was run earlier in session but no log file was saved.

---

## How the Pipeline Works

Each run passes through these agents in sequence:

```
Price Data → Market Analyst → Sentiment Analyst → News Analyst → Fundamentals Analyst
                                    → Bull Researcher ↔ Bear Researcher (1 round each)
                                          → Research Manager → Risk Manager → Trader → Final Decision
```

All agents used `gemini-3.1-flash-lite`. Data comes from Yahoo Finance via `yfinance`.

---

## Known Bugs Found and Fixed This Session

| Bug | Impact | Fix Applied |
|-----|--------|-------------|
| Debate routing: `should_continue_debate` used `startswith("Bull")` string match, which small models strip | Bull ran in infinite loop, Bear never ran | Added `last_speaker` field to state; routing now checks this field |
| USD/TWD price confusion: TSM ADR traded at $444 USD but model used $185 (TWD home-share price) | Wrong entry/stop prices for TSM | Added USD anchor instruction to `build_instrument_context()` for US-listed exchanges |
| Final decision printed 5× | Risk Manager, Trader, Portfolio Manager all produce identical output — pipeline loop | Known issue, not yet fixed — cosmetic only, decision itself is correct |
| Market Analyst writes `FINAL TRANSACTION PROPOSAL: HOLD` prematurely | Framing confusion — this label belongs to the Trader, not the analyst | Known issue, not yet fixed |

---

## Stock 1: AVGO — Broadcom Inc.

**Analysis Date:** June 5, 2026  
**Log:** `broadcom_check.log`

### Price Context

| Date | Close | Event |
|------|-------|-------|
| Jan 2 | $346.89 | Year start |
| Mar 30 | $293.41 | Year low |
| Jun 3 | $479.23 | Pre-earnings high |
| **Jun 4** | **$418.91** | **-12.5% earnings crash (80M+ volume)** |

AVGO reported Q2 FY2026 earnings. Revenue grew, but management did not raise long-term targets → market interpreted as margin/growth ceiling. Stock fell 12-14% in one day on massive volume (3× normal).

### Gemini's Technical Analysis

| Indicator | Value (Jun 4) | Interpretation |
|-----------|---------------|----------------|
| Close | $418.91 | Crashed from $479 high |
| 50-day SMA | $397.07 | Now acting as support |
| 200-day SMA | $354.46 | Long-term floor |
| RSI | 48.08 | Dropped from overbought (74.75) to neutral in one day |
| MACD | 14.16 | Declining from 17.46 |

**Gemini's technical read:** Momentum exhausted. RSI dumped from overbought to neutral in one session. MACD declining. Monitor 50-SMA ($397) as key support.  
**Gemini interim call:** HOLD (from Market Analyst)

### My Technical Read

The RSI drop from 74.75 → 48.08 in a single day is extreme — that's not a healthy pullback, that's a sentiment reset. On 80M+ volume (the highest volume day in the dataset), sellers overwhelmed buyers. The stock gave back an entire week of gains. Key question: is this a "dip" or a "distribution top"? The 50-SMA at $397 is meaningful support, but if that breaks, next stop is $354 (200-SMA). **I read this as more dangerous than Gemini suggested — the risk/reward for new buyers at $418 is poor.**

### Gemini's Sentiment Analysis

| Direction | Source | Evidence |
|-----------|--------|---------|
| Bearish | News | 12-14% crash; "canary in coal mine" for AI margins |
| Bullish | StockTwits | 40% bullish vs 13% bearish — retail buying dip |
| Mixed | Reddit | Leveraged YOLO trades on r/wsb; high-risk appetite |

**Score: 4.0/10 Mixed.** Key insight: institutions framing earnings miss as a structural warning; retail treating it as a buying opportunity. That divergence is itself a risk signal.

**My sentiment read:** The 40% bullish StockTwits reading after a 13% crash is not bullish — it means retail is reflexively buying dips, not analyzing fundamentals. The "canary in the coal mine" framing from institutional analysts is more credible. I score this **3.5/10 (cautiously bearish)** — one notch below Gemini.

### Gemini's Fundamental Analysis

| Metric | Value |
|--------|-------|
| Market Cap | $1.98 Trillion |
| TTM P/E | 69.93 |
| Forward P/E | 21.97 |
| PEG Ratio | 1.05 |
| Revenue (TTM) | $68.3B |
| Operating Margin | **44.94%** |
| ROE | **33.37%** |
| FCF (TTM) | $25.5B |
| Debt-to-Equity | 82.7 (high) |

**Gemini's fundamental read:** Strong profitability metrics. ROE 33% and 45% operating margin are best-in-class. PEG of 1.05 means fair value if growth holds. High debt ($65B) but manageable given FCF of $25.5B. **HOLD** — "market has priced in growth, wait for better entry."

**My fundamental read:** AVGO's fundamentals are genuinely superior to AMD or TSM on efficiency metrics. ROE 33% vs AMD's 8% — this is a different quality of business. The concern is whether the "disappointment" in guidance represents a one-time calibration or a permanent margin ceiling. If margins are peaking at 45%, then forward growth must be exceptional to justify the current valuation. I'd say: **excellent business, but the crash created a temporary overshoot downward and then the market will re-price fairly.** Long term bullish, short term uncertain.

### Debate (NOT VISIBLE — debate agents ran but output not captured in log)

The AVGO log shows no 🐂/🐻 debug prints. This is because the debate routing bug was **not yet fixed** when this run was done. The Bull ran multiple times in a loop without Bear responding.

**Status of debate for AVGO:** Broken (pre-fix). The Research Manager synthesized based on one-sided bull input.

### Final Decision

| | Gemini | Me |
|--|--------|-----|
| **Signal** | BUY | CAUTIOUS BUY |
| **Entry** | $395.00 | $390-400 (at 50-SMA) |
| **Stop Loss** | $354.00 (200-SMA) | $355 (200-SMA -$5 buffer) |
| **Take Profit / Target** | ~$520-540* | $500-520 (pre-crash level) |
| **Time Horizon** | 6–12 months* | 6–12 months |
| **Position Size** | 50% of target allocation | 1.5-2% of portfolio |
| **Rationale** | 12-14% pullback = attractive re-entry at 22x Forward P/E | Same — post-crash reset, but watch $397 support |

*Portfolio Manager price_target was generated but not printed (pipeline bug). Target estimated from pre-crash high and Forward P/E re-rating.

**Agreement: ~85%.** Both agree the crash is a buying opportunity given the quality of the underlying business. Gemini's entry ($395) is smart — at the 50-SMA. My entry range is similar. Stop at 200-SMA ($354) is correct for both. Gemini's "50% of target allocation" is an unusual sizing metric; I prefer absolute portfolio % (1.5-2%).

**Key difference:** Gemini said "fundamental collapse? No." and moved straight to BUY. I would want to see one more day of price stabilization above $397 before entering, to confirm the 50-SMA is holding rather than breaking.

---

## Stock 2: TSM — Taiwan Semiconductor Manufacturing

**Analysis Date:** June 5, 2026  
**Log:** `TSM_check.log` *(this is the pre-USD-fix run — see note below)*

### Important Note: USD Price Bug

The TSM_check.log captured the **first run** before the USD currency fix was applied. TSM trades on NYSE as a USD-denominated ADR at ~$444. Its home shares in Taiwan trade at ~185 TWD — a completely different number. The Trader agent in this log hallucinated the entry price as $185 (TWD home-share price) instead of the correct ~$435 USD.

**The fix:** Added USD anchor to `build_instrument_context()` for US-listed exchanges. A second run was done after the fix and confirmed an entry price of ~$435, aligning with the actual USD ADR price.

For this report: fundamentals/sentiment/news analysis from the log are valid (they correctly referenced USD prices). Only the final entry/stop prices were wrong in this specific log.

### Price Context

| Date | Close | Event |
|------|-------|-------|
| Jan 2 | $318.71 | Year start |
| Mar 30 | $316.50 | Year low |
| Apr 24 | $402.46 | Breakout above $400 |
| **Jun 4** | **$444.92** | Current — near highs |

TSM had a steady, less volatile climb compared to AMD. Up ~40% from January, but in a more orderly fashion. No single crash event like AVGO.

### Gemini's Technical Analysis

| Indicator | Value (Jun 4) | Interpretation |
|-----------|---------------|----------------|
| Close | $444.92 | Near recent highs |
| 50-day SMA | $387.68 | Healthy support below |
| RSI | 65.77 | Bullish, approaching but not at overbought (70) |
| MACD | 13.87 | Rising (from 10.83 on Jun 1) |

**Gemini's technical read:** Clear uptrend. Price above 50-SMA, RSI approaching 70 but not there, MACD rising. "Resilient." Some caution warranted as RSI nears 70.  
**Gemini interim call:** HOLD (from Market Analyst)

### My Technical Read

TSM is the steadiest chart of all four stocks analyzed. The gap between price ($444) and 50-SMA ($387) is 14.5% — meaningful but not extreme (compare AMD at 48% above its 50-SMA). RSI at 65.77 is elevated but not overbought. The MACD trending up is constructive. This is a healthier technical picture than AMD or AVGO post-crash. **I'd call this a proper uptrend with room to run.**

However: TSM carries a structural risk that no technical indicator captures — geopolitical risk (Taiwan-China). A technical buy can become a geopolitical disaster overnight. Position sizing must account for this.

### Gemini's Sentiment Analysis

**Score: 7.5/10 Bullish** — the highest bullish sentiment of all four stocks.

Key points:
- CEO C.C. Wei stated demand for AI chips will outstrip supply "for years"
- TSM described as the "Hormuz Strait of chips" — the essential chokepoint
- Bullish across news, StockTwits, and Reddit
- Geopolitical risk noted but treated as secondary

**My sentiment read:** 7.5/10 is fair. TSM has the strongest structural narrative of any chip company right now — every AI chip (NVDA H100, AMD MI300X, Apple M4) runs through TSMC fabs. The supply constraint story is real and documented by the CEO himself. I would also score **7-7.5/10 bullish**, with the geopolitical discount being the main caveat.

### Gemini's Fundamental Analysis

| Metric | Value (TTM/Annual) |
|--------|-------------------|
| Market Cap | $2.31 Trillion |
| Revenue (TTM) | $4.10T TWD (~$127B USD) |
| P/E (TTM) | 38.03 |
| Forward P/E | 22.78 |
| ROE | **36.21%** |
| Operating Margin | **58.1%** |
| Dividend Yield | 0.85% |
| D/E Ratio | 18.45 (very low) |
| Current Ratio | 2.49 |

**Gemini's fundamental read:** Outstanding. 58% operating margin, 36% ROE, virtually no debt. TSM is the most financially efficient company of the four. Strong FCF. "Essential infrastructure" positioning. Recommended **BUY** for long-term investors.

**My fundamental read:** TSM's fundamentals are genuinely the strongest in the semiconductor sector. 58% operating margin means every dollar of revenue they don't spend on operations falls to profit. ROE of 36% means management is efficient with shareholder capital. The only concern is CapEx — TSM spends enormously on fabs (1.28T TWD annually) to stay ahead. This is a moat-maintenance cost, but it's also why no competitor can catch up. **I agree with BUY on fundamentals — TSM is arguably the highest-quality business in the AI supply chain.**

### Debate

The TSM log does not show 🐂/🐻 debate output. This run was also done before the debate routing fix, so Bull ran in a loop without Bear participating.

**Status of debate for TSM:** Broken (pre-fix).

### Final Decision

| | Gemini (pre-fix log) | Gemini (post-fix run) | Me |
|--|---------------------|----------------------|-----|
| **Signal** | BUY | BUY | BUY |
| **Entry** | ~~$185~~ **(BUG)** | ~$435 | $420-435 |
| **Stop Loss** | ~~$162~~ **(BUG)** | ~$395 | $387 (50-SMA) |
| **Take Profit / Target** | ~~N/A~~ | ~$520-550* | $510-530 |
| **Time Horizon** | ~~N/A~~ | 3–6 months* | 3–6 months |
| **Position Size** | 4% | 4% | 2-3% |

*Portfolio Manager price_target was generated but not printed (pipeline bug). Target derived from Forward P/E 22.78x on next-year EPS estimates.

**Agreement on direction: 100%.** All three analyses agree TSM is a BUY.

**The $185/$162 bug:** These are TSM's TWD home-share prices (~185 TWD = ~$5.70 USD, clearly wrong). The Trader agent bypassed the USD anchor and hallucinated the TWD price. The fix corrected this to ~$435 (USD ADR price), which aligns with my analysis.

**Key difference:** I'd use a tighter position size (2-3% vs 4%) given Taiwan geopolitical risk, even if the fundamentals are strong. The geopolitical risk is a tail risk, but it's a very fat tail.

---

## Stock 3: AMD — Advanced Micro Devices

**Analysis Date:** June 5, 2026  
**Log:** `AMD_check.log`  
**Status:** All fixes applied (debate routing + USD anchor + debug logging)

### Price Context

| Date | Close | Move |
|------|-------|------|
| Apr 6 | $220.18 | Baseline |
| Apr 24 | $347.81 | +58% in 3 weeks |
| May 6 | $421.39 | Breakout |
| May 28 | $518.09 | Continued run |
| Jun 3 | $542.52 | High |
| **Jun 4** | **$523.20** | Pulled back from high |

AMD ran **+138%** from early April to June 3. This is one of the most aggressive runs in the dataset. The Jun 4 pullback of $19 from the high is the first sign of potential exhaustion.

### Gemini's Technical Analysis

| Indicator | Value (Jun 4) |
|-----------|---------------|
| Close | $523.20 |
| 10-day EMA | $503.63 |
| 50-day SMA | **$353.80** |
| 200-day SMA | $244.47 |
| RSI | **70.57** |
| MACD | 49.47 |
| ATR | $27.12 |
| VWMA | $478.22 |
| Bollinger Middle | $471.04 |

**Gemini's technical read:** Strong bullish momentum. RSI near overbought. Elevated ATR = elevated volatility. Use 10-EMA or 20-SMA as stop references. Interim call: **HOLD** (from Market Analyst, who should not be writing HOLD — pipeline issue).

### My Technical Read

The 50-SMA at $353.80 means AMD is **48% above its medium-term average.** That is an extreme extension. For comparison:
- AVGO before its crash: was 20% above 50-SMA → crashed 13%  
- TSM: 14.5% above 50-SMA → healthy

AMD at +48% above 50-SMA is not sustainable. Mean reversion toward $400-430 is mathematically likely in the next 4-8 weeks, even without any negative catalyst. The RSI of 70.57 confirms the overbought condition.

However: a stock can stay overbought for weeks in a strong trend. The question is not "will it correct?" but "when?" Given the ATR of $27, daily swings of 5% are normal — this stock can lose $50 in a day without it meaning anything structural.

**My conclusion: Bullish trend intact, but buying at current price ($523) is chasing. Wait for $490-510 range.**

### Gemini's Sentiment Analysis

| Direction | Source | Evidence |
|-----------|--------|---------|
| Bullish | News | Barclays PT $665; TSMC supply-constrained |
| Bearish | News | AVGO earnings dragging sector down |
| Mixed | StockTwits | 5 bullish vs 4 bearish |
| Bullish | Reddit | Long-term holders up 300%, holding |

**Score: 4.5/10 Mixed.**

**My sentiment read:** 4.5/10 is accurate. I'd score it **5/10 (neutral, slight bullish lean).** The Barclays $665 target is meaningful — 27% upside from $523, implying real institutional conviction. The AVGO overhang is real but temporary ("guilt by association"). Reddit's "up 300% and holding" crowd is actually a risk indicator — these holders won't panic sell, but new buyers at these prices are fragile.

### Gemini's Fundamental Analysis

| Metric | Value |
|--------|-------|
| Market Cap | $853B |
| TTM P/E | **175.57** |
| Forward P/E | 40.22 |
| Revenue (TTM) | $37.45B |
| Profit Margin | 13.37% |
| ROE | **8.06%** |
| ROA | 3.65% |
| Cash | $12.35B |
| Debt | $3.87B |
| FCF (TTM) | $7.17B |
| Beta | **2.40** |

Revenue trajectory (quarterly):
- Q1'25: $7.44B
- Q2'25: $7.69B
- Q3'25: $9.25B
- Q4'25: $10.27B
- **Q1'26: $10.25B** ← slight flattening vs Q4

**Gemini's fundamental read:** High valuation (175x TTM P/E) but Forward P/E of 40x is acceptable in AI context. Fortress balance sheet. $2.4B/quarter R&D investment. Monitor valuation. Beta 2.40 = war-level volatility. **Risk factor highlighted.**

**My fundamental read:**

The most important number Gemini captured correctly: **ROE of 8.06%.** Compare to AVGO's 33% and TSM's 36%. AMD is spending enormous capital to maintain its market position and generating mediocre returns on that capital. This is not a "fortress" — it's a company in an expensive arms race where NVIDIA (ROE ~100%+) holds the commanding position.

The Q1'26 revenue flattening ($10.25B vs $10.27B in Q4) is worth watching — if Q2 doesn't accelerate, the 175x TTM P/E becomes very difficult to justify.

**CUDA moat concern (Gemini missed this):** NVIDIA's software ecosystem (CUDA, cuDNN, Triton, TensorRT) is 15 years deep. AMD's ROCm is improving but enterprises don't rip out proven infrastructure. AMD wins "second source" contracts, not primary AI GPU deployments. This is a ceiling on market share gain.

**EPYC opportunity (Gemini missed this):** AMD's server CPU business (EPYC) is taking massive share from Intel. This is a more predictable, less cyclical revenue stream that provides fundamental support regardless of GPU AI dynamics.

### Debate Analysis

**This is the first run where the debate routing fix was applied.** Both Bull and Bear ran.

#### 🐂 Bull Argument (Gemini)

Key points made:
1. TSMC supply constraint = demand bottleneck, not demand weakness. AMD can't build fast enough.
2. Forward P/E 40x is "reasonable" in hyperscale AI growth context
3. $12.35B cash + healthy D/E = "fortress" balance sheet
4. $2.40B quarterly R&D cementing competitive advantage
5. Barclays $665 PT = institutional confidence
6. Volatility during breakout is normal, not alarming

**Quality: Good.** Correctly engaged with the data. The TSMC argument is particularly strong.

#### 🐻 Bear Argument (Gemini)

Key points made:
1. Forward P/E 40x requires perfect execution — one miss = violent multiple compression
2. ROE 8.06% and ROA 3.65% = capital intensity problem, "buying market position"
3. AVGO weakness signals sector-wide AI spending headwinds — AMD not immune
4. RSI 70.57 + price 48% above 50-SMA = overextended
5. Defensive rotation accelerating = tech outflows coming
6. Stop loss at $465 means "one bad report = double-digit drop"

**Quality: Very good.** The ROE/ROA critique is the sharpest argument in the entire debate. The "capital intensity treadmill" framing is accurate.

#### Debate Assessment

This is **genuinely two-sided debate** — the best we saw across all runs. Both sides engaged with actual data and each other's points. The Bear's ROE argument directly refuted Bull's "fortress" claim. The Bull's TSMC supply-constraint rebuttal directly addressed the Bear's sector-correlation argument.

**Winner (in my view): Slight edge to Bull.** The ROE criticism is valid, but ROE is a lagging metric during a growth investment phase. The structural demand story (TSMC CEO saying demand exceeds supply) is more forward-looking. Barclays $665 is a real institutional data point, not optimism.

**My Bull additions (that Gemini missed):**
- EPYC server CPU share gains from Intel
- AMD as "second source" that hyperscalers need to prevent NVDA monopoly pricing

**My Bear additions (that Gemini missed):**
- CUDA moat — the real ceiling on AMD's GPU market share
- TSMC geopolitical risk as a supply chain vulnerability

### Final Decision

| | Gemini | Me |
|--|--------|-----|
| **Signal** | BUY (limit order) | BUY on pullback |
| **Entry** | $480.50 (range $471-490) | $490-510 |
| **Stop Loss** | $465.00 | $452 (Bollinger $471 - 1×ATR $27) |
| **Take Profit / Target** | ~$620-650* | $600-620 |
| **Time Horizon** | 3–6 months* | 3–6 months |
| **Position Size** | 1.5% | 1.5% |

*Gemini's Portfolio Manager produced a price_target field but it was never printed (pipeline bug). Target derived from Barclays $665 PT discounted for RSI overextension.

**Agreement: ~85%.** Both recommend entering on a pullback rather than chasing at $523.

**Key differences:**
1. **Entry range:** I anchor to the 10-EMA ($503) falling toward $490. Gemini anchors to the Bollinger Middle ($471). Both are reasonable.
2. **Stop loss:** Gemini's $465 is only $6-15 below the entry range ($471-490). With ATR at $27, this stop will get shaken out by normal daily volatility. My $452 (Bollinger Middle minus 1 ATR) gives proper breathing room.
3. **Target:** I set a concrete target ($600-620). Gemini didn't specify an exit.

---

## Overall Comparison: All Stocks

### Final Signals Summary

| Stock | Gemini Signal | Gemini Entry | Gemini Stop | My Signal | My Entry | My Stop | Agreement |
|-------|--------------|-------------|-------------|-----------|----------|---------|-----------|
| **AVGO** | BUY | $395 | $354 | CAUTIOUS BUY | $390-400 | $355 | 85% |
| **TSM** | BUY | $435* | $395* | BUY | $420-435 | $387 | 90% |
| **AMD** | BUY (limit) | $480 | $465 | BUY (pullback) | $490-510 | $452 | 80% |

*TSM post-fix run prices. Pre-fix log showed $185/$162 (currency bug).

### Sentiment Scores

| Stock | Gemini Score | My Score | Gap |
|-------|-------------|---------|-----|
| AVGO | 4.0/10 Mixed | 3.5/10 Slightly bearish | -0.5 |
| TSM | 7.5/10 Bullish | 7.0/10 Bullish | -0.5 |
| AMD | 4.5/10 Mixed | 5.0/10 Neutral | +0.5 |

### Fundamental Quality Ranking

| Stock | ROE | Operating Margin | FCF | Debt | My Rank |
|-------|-----|-----------------|-----|------|---------|
| **TSM** | 36.2% | 58.1% | Very high | Low (D/E 18) | 1st |
| **AVGO** | 33.4% | 44.9% | $25.5B TTM | High (D/E 82) | 2nd |
| **AMD** | 8.1% | ~14% | $7.2B TTM | Low (D/E 6) | 3rd |

### Debate Quality by Run

| Stock | Debate Status | Quality |
|-------|--------------|---------|
| AVGO | Broken (pre-fix) — Bull only, loop | N/A |
| TSM | Broken (pre-fix) — Bull only, loop | N/A |
| AMD | Fixed — Bull ran, then Bear ran | Good — genuinely two-sided |

---

## App Quality Assessment

### What Gemini Did Well
- Correctly identified all key technical indicators and interpreted them accurately
- Fundamental data retrieval and analysis was clean and accurate
- Sentiment scoring was nuanced — correctly picked up AVGO "guilt by association" narrative
- Entry price strategy (limit orders below current price) shows market awareness — not chasing
- The AMD debate, when working, produced genuinely opposing arguments backed by data
- USD price correctly anchored for AMD and AVGO (US-listed exchange)

### What Gemini Missed vs Me
1. **CUDA moat** — the most important structural risk for AMD, never mentioned
2. **EPYC CPU angle** — AMD's most predictable revenue driver, missed in bull case
3. **TSM geopolitical risk sizing** — mentioned but not factored into position size
4. **Stop loss sizing** — Gemini's stops are consistently too tight relative to ATR
5. **Revenue flattening** — AMD Q1'26 = Q4'25, worth flagging
6. **AVGO margin ceiling** — the "canary in coal mine" framing from news was well-identified but not deep enough

### Pipeline Issues to Investigate

| Issue | Description | Severity |
|-------|-------------|----------|
| Final decision prints 5× | Risk Manager, Trader, Portfolio Manager all output identical decision | Low (cosmetic) |
| Market Analyst writes FINAL TRANSACTION PROPOSAL | Wrong agent using Trader's label | Medium (confusing logs) |
| Debate skipped for AVGO/TSM | Pre-fix runs had infinite Bull loop | Fixed |
| `get_verified_market_snapshot` tool error | Called by agents but not registered — always errors | Medium (wasted token calls) |
| Reddit 403 errors | Reddit API blocking — falls back to RSS | Low (handled gracefully) |
| Global news irrelevant | Returns shoe price articles, not tech news | Medium (noise in prompt) |

---

## Sector Context (June 5, 2026)

All four stocks exist in the same macro environment:

- **AVGO earnings miss** was the triggering event for sector-wide concern
- **TSMC CEO confirmed** AI demand exceeds supply capacity — long-term bullish for all chip designers
- **Barclays raised AMD PT to $665** — institutional conviction remains
- **Defensive rotation underway** — Dow hit record high while Nasdaq fell; money moving from tech to financials/healthcare
- **US jobs report pending** — macro uncertainty adding volatility
- **Iran war** — geopolitical backdrop affecting oil and risk sentiment
- **Computex AI summit** — upcoming catalyst for AI chip sentiment

**Key insight across all three stocks:** The AVGO crash was company-specific (guidance failure), not a sector failure. TSM and AMD are structurally different businesses. The market initially sold all chip stocks on AVGO news (guilt by association), creating potential entry opportunities in TSM and AMD.

---

## Reading This Tomorrow: Quick Reference

**If you want to enter positions:**

| Stock | Wait for | Entry zone | Stop | Target | R:R |
|-------|----------|-----------|------|--------|-----|
| AVGO | Stabilization above $397 (50-SMA) | $390-410 | $352-355 | $520-540 | ~3:1 |
| TSM | Any pullback | $420-440 | $385-390 | $520-550 | ~2.5:1 |
| AMD | Pullback to 10-EMA | $490-510 | $450-452 | $620-650 | ~3:1 |

*R:R = Risk:Reward ratio. Entry midpoint used for calculation.*

**Risk-adjusted, best buy opportunity:** TSM. Best fundamentals, least overextended technically, strongest macro narrative.

**Highest risk/reward:** AMD. If AI narrative holds, $600+ is realistic. If macro turns, $400 is realistic. Know your conviction before entering.

**Most complex situation:** AVGO. Short-term broken (post-crash), long-term excellent. Needs a few weeks of consolidation data to know if $397 holds as support.

---

*Report generated: June 5, 2026*  
*Data sources: Yahoo Finance via yfinance, Reddit RSS, StockTwits*  
*AI model: gemini-3.1-flash-lite (Gemini), Claude Sonnet 4.6 (this analysis)*  
*Logs: broadcom_check.log, TSM_check.log, AMD_check.log*
