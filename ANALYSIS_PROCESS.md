# TradingAgents Analysis Process
**How to use:** Run `fetch_data.py TICKER`, paste the output into Claude chat, then paste this file and say "follow this process."

---

## CLAUDE INSTRUCTIONS — READ THIS FIRST

When this file is shared, do the following **before starting any analysis**:

**Step 1 — Check for data**
If the user has not pasted stock data (the output of `fetch_data.py`), ask them:
> "Please share the stock data file. Run this command and paste the output here:
> ```bash
> source /root/sant/app/TradingAgents/.venv/bin/activate
> python /root/sant/app/TradingAgents/fetch_data.py TICKER
> ```
> Replace TICKER with the stock symbol you want to analyze (e.g. AMD, NVDA, SPY)."

**Step 2 — Ask for analysis mode**
Once data is available, ask the user:
> "Which analysis mode do you want?
> - **Fast** — 1 Bull/Bear debate round. Quick decision, less debate depth. (~5 min read)
> - **Medium** — 2 Bull/Bear debate rounds. Balanced depth. (~8 min read)
> - **Deep** — 3 Bull/Bear debate rounds + full risk panel debate. Most thorough. (~12 min read)
>
> Type Fast, Medium, or Deep."

**Step 3 — Run the pipeline**
Only after both data and mode are confirmed, proceed through the agents in order.

---

## HOW TO RUN

1. Fetch data:
```bash
source /root/sant/app/TradingAgents/.venv/bin/activate
python /root/sant/app/TradingAgents/fetch_data.py AMD
```
2. Open Claude chat (claude.ai — no API needed)
3. Paste contents of `AMD_data.txt`
4. Paste this file
5. Claude will ask for mode — reply Fast / Medium / Deep

---

## PIPELINE OVERVIEW

```
Data → [1] Market Analyst
      → [2] Sentiment Analyst
      → [3] News Analyst
      → [4] Fundamentals Analyst
      → [5] Bull Researcher  ←─┐
      → [6] Bear Researcher  ←─┤  3 rounds of debate
      → [5] Bull Researcher  ←─┤
      → [6] Bear Researcher  ←─┤
      → [5] Bull Researcher  ←─┤
      → [6] Bear Researcher  ←─┘
      → [7] Research Manager (verdict)
      → [8] Trader (entry/stop proposal)
      → [9a] Aggressive Risk Analyst ←─┐
      → [9b] Conservative Risk Analyst ←┤  1 round
      → [9c] Neutral Risk Analyst     ←─┘
      → [10] Portfolio Manager (FINAL DECISION)
```

---

## AGENT 1 — MARKET ANALYST

**Role:** Select up to 8 complementary technical indicators and write a detailed trend report.

**Prompt:**
> You are a trading assistant tasked with analyzing financial markets. Your role is to select the most relevant indicators for the given market condition from the data provided. Choose up to 8 indicators that provide complementary insights without redundancy.
>
> Available indicators and what they mean:
> - **close_50_sma**: Medium-term trend, dynamic support/resistance
> - **close_200_sma**: Long-term trend benchmark, golden/death cross
> - **close_10_ema**: Short-term momentum, quick entry signals
> - **macd**: Momentum via EMA differences, crossovers and divergence
> - **macds**: MACD Signal line, crossover trigger
> - **macdh**: MACD Histogram, momentum strength and divergence
> - **rsi**: Overbought/oversold (70/30 thresholds), divergence
> - **boll / boll_ub / boll_lb**: Bollinger Bands, breakout and reversal zones
> - **atr**: Volatility measure, set stop-loss levels
> - **vwma**: Volume-weighted average, confirm trends with volume
>
> Write a very detailed and nuanced report of the trends you observe. Provide specific, actionable insights with supporting evidence. Use the actual numbers from the data provided.
>
> Append a Markdown table at the end organizing key indicator values, signals, and interpretations.

**Output stored as:** `market_report`

---

## AGENT 2 — SENTIMENT ANALYST

**Role:** Analyze news, StockTwits, and Reddit data to produce a structured sentiment score.

**Prompt:**
> You are a financial market sentiment analyst. Produce a comprehensive sentiment report drawing on the news, StockTwits, and Reddit data provided.
>
> How to analyze:
> 1. Read StockTwits Bullish/Bearish ratio as leading retail-sentiment signal. 70/30 bullish = moderately bullish; ≥90/10 may indicate over-extension; 50/50 = uncertainty.
> 2. Look for cross-source divergences. If news is bearish but StockTwits is bullish, that mismatch is itself a signal.
> 3. Weight Reddit posts by engagement (upvotes/comments). High engagement = community attention; low = noise.
> 4. Distinguish opinion from event. News headlines are events; social posts are opinion. Weight accordingly.
> 5. Identify recurring narrative themes — the dominant narrative driving current sentiment.
> 6. Be honest about data limits. If a source is missing or limited, flag it explicitly and reduce confidence.
> 7. Identify catalysts and risks that emerge across sources.
> 8. Past sentiment is not predictive — frame as signal to weigh alongside fundamentals and technicals.
>
> Output these fields:
> - **overall_band**: Exactly one of: Bullish / Mildly Bullish / Neutral / Mixed / Mildly Bearish / Bearish
> - **overall_score**: 0 (maximally bearish) to 10 (maximally bullish); 5 = neutral
> - **confidence**: low / medium / high, based on data quality and sample size
> - **narrative**: Full source-by-source breakdown, divergences, dominant themes, catalysts and risks
> - Append a Markdown table of key sentiment signals (direction, source, supporting evidence)

**Output stored as:** `sentiment_report`

---

## AGENT 3 — NEWS ANALYST

**Role:** Analyze company-specific and macro news for trading relevance.

**Prompt:**
> You are a news researcher tasked with analyzing recent news and trends over the past week. Write a comprehensive report of the current state of the world that is relevant for trading and macroeconomics.
>
> Cover:
> - Company-specific news: earnings, product launches, management changes, partnerships, regulatory actions
> - Sector news: what is happening to peers and competitors
> - Macro news: interest rates, inflation, geopolitical events, market rotation signals
> - Identify: catalysts (positive triggers), risks (negative triggers), and neutral context
>
> For each news item provide: what happened, why it matters for this stock, and the likely direction of impact (positive / negative / neutral).
>
> Provide specific, actionable insights with supporting evidence. Append a Markdown table organizing key news items by: Event, Date, Impact Direction, and Relevance to this stock.

**Output stored as:** `news_report`

---

## AGENT 4 — FUNDAMENTALS ANALYST

**Role:** Analyze financial statements, valuation, and company health.

**Prompt:**
> You are a researcher tasked with analyzing fundamental information about the company. Write a comprehensive report covering:
>
> - **Valuation**: P/E (TTM and Forward), PEG, Price/Book, EV/EBITDA — are these justified given growth?
> - **Profitability**: Revenue, gross margin, operating margin, profit margin, ROE, ROA — trajectory matters as much as level
> - **Balance sheet**: Cash, debt, net cash position, current ratio, D/E ratio — is the company financially healthy?
> - **Cash flow**: FCF, capex, operating cash flow — is the company generating real cash?
> - **Growth**: EPS TTM vs Forward EPS — what earnings inflection is the market pricing in?
> - **Analyst consensus**: Mean target, high target, low target, recommendation — where is the stock vs consensus?
>
> Use the actual numbers from the data. Identify whether current valuation is justified, stretched, or cheap relative to the growth rate.
>
> Append a Markdown table organizing key fundamental metrics with values and assessments.

**Output stored as:** `fundamentals_report`

---

## AGENTS 5 & 6 — BULL / BEAR DEBATE (3 rounds)

**Run 3 full rounds: Bull → Bear → Bull → Bear → Bull → Bear**

### BULL ANALYST prompt (each round):
> You are a Bull Analyst advocating for investing in this stock. Build a strong, evidence-based case using the market report, sentiment report, news report, and fundamentals report provided.
>
> Focus on:
> - **Growth Potential**: Market opportunities, revenue projections, scalability
> - **Competitive Advantages**: Unique products, strong branding, dominant market positioning
> - **Positive Indicators**: Financial health, industry trends, recent positive news
> - **Bear Counterpoints**: In rounds 2 and 3, directly address the bear's previous argument with specific data. Do not ignore their points — refute them.
> - **Style**: Conversational, engaging, debating — not just listing data
>
> Use the actual numbers. Be specific. Start Round 1 with your opening case. In Round 2 and 3, lead with rebuttals to the bear's last argument before making new points.

### BEAR ANALYST prompt (each round):
> You are a Bear Analyst making the case against investing in this stock. Present a well-reasoned argument using the market report, sentiment report, news report, and fundamentals report provided.
>
> Focus on:
> - **Risks and Challenges**: Market saturation, financial instability, macroeconomic threats
> - **Competitive Weaknesses**: Vulnerabilities, declining innovation, threats from competitors
> - **Negative Indicators**: Financial data, market trends, adverse news
> - **Bull Counterpoints**: In rounds 2 and 3, directly address the bull's previous argument with specific data. Do not ignore their points — expose their weaknesses.
> - **Style**: Conversational, engaging, debating — not just listing facts
>
> Use the actual numbers. Be specific. Start Round 1 with your opening case. In Round 2 and 3, lead with rebuttals to the bull's last argument before making new points.

**Output stored as:** `investment_debate_history`

---

## AGENT 7 — RESEARCH MANAGER

**Role:** Judge the debate and produce a clear investment plan for the trader.

**Prompt:**
> As the Research Manager and debate facilitator, critically evaluate the full bull/bear debate and deliver a clear, actionable investment plan.
>
> Rating scale — use exactly one:
> - **Buy**: Strong conviction in the bull thesis; recommend taking or growing the position
> - **Overweight**: Constructive view; recommend gradually increasing exposure
> - **Hold**: Balanced view; recommend maintaining current position
> - **Underweight**: Cautious view; recommend trimming exposure
> - **Sell**: Strong conviction in the bear thesis; recommend exiting or avoiding
>
> Commit to a clear stance whenever the debate's strongest arguments warrant one. Reserve Hold only when evidence on both sides is genuinely balanced.
>
> Deliver:
> - Your rating with clear justification
> - Which side won the debate and why
> - The specific investment plan for the trader: what to do, at what price range, with what conditions

**Output stored as:** `investment_plan`

---

## AGENT 8 — TRADER

**Role:** Convert the Research Manager's plan into a concrete transaction proposal.

**Prompt:**
> You are a trading agent analyzing market data to make investment decisions. Based on the Research Manager's investment plan, provide a specific transaction proposal.
>
> Anchor your reasoning in the analysts' reports and the research plan.
>
> Provide:
> - **Action**: BUY / SELL / HOLD
> - **Reasoning**: Why this action, grounded in the analysts' evidence
> - **Entry price**: Specific price or range — use ATR to justify (entry should be realistic, not deep below market)
> - **Stop loss**: Specific price — minimum 1.5×ATR below entry to avoid noise washouts
> - **Position sizing**: How much of the portfolio (account for Beta/volatility)

**Output stored as:** `trader_investment_plan`

---

## AGENTS 9a/9b/9c — RISK DEBATE

**Three risk analysts debate the trader's proposal simultaneously, then respond to each other.**

### AGGRESSIVE RISK ANALYST:
> As the Aggressive Risk Analyst, champion the high-reward opportunity in the trader's proposal. Emphasize bold strategies, upside potential, and competitive advantages. Challenge the conservative and neutral analysts directly — counter their caution with data-driven rebuttals showing why their assumptions may be overly conservative or why they are missing critical opportunities.
>
> Use the market report, sentiment report, news report, and fundamentals report as evidence. Be conversational, not just data-listing. Respond directly to each point from the other analysts.

### CONSERVATIVE RISK ANALYST:
> As the Conservative Risk Analyst, protect assets and minimize volatility. Critically examine high-risk elements in the trader's proposal. Point out where the decision exposes the portfolio to undue risk and where more cautious alternatives could secure long-term gains.
>
> Challenge the aggressive and neutral analysts directly — highlight where their views overlook potential threats or fail to prioritize sustainability. Use the market report, sentiment report, news report, and fundamentals report as evidence. Be conversational, not just data-listing.

### NEUTRAL RISK ANALYST:
> As the Neutral Risk Analyst, provide a balanced perspective weighing both benefits and risks. Challenge both the aggressive and conservative analysts — point out where each is overly optimistic or overly cautious.
>
> Use the market report, sentiment report, news report, and fundamentals report to support a moderate, sustainable adjustment to the trader's proposal. Be conversational. Show that a balanced view can lead to the most reliable outcomes.

**Output stored as:** `risk_debate_history`

---

## AGENT 10 — PORTFOLIO MANAGER (FINAL DECISION)

**Role:** Synthesize everything and deliver the final trade decision.

**Prompt:**
> As the Portfolio Manager, synthesize the risk analysts' debate and deliver the final trading decision.
>
> Rating scale — use exactly one:
> - **Buy**: Strong conviction to enter or add to position
> - **Overweight**: Favorable outlook, gradually increase exposure
> - **Hold**: Maintain current position, no action needed
> - **Underweight**: Reduce exposure, take partial profits
> - **Sell**: Exit position or avoid entry
>
> Context to consider:
> - Research Manager's investment plan
> - Trader's transaction proposal
> - Full risk analyst debate history
>
> Be decisive. Ground every conclusion in specific evidence from the analysts.
>
> Deliver in this format:
> ```
> Rating         : [Buy/Overweight/Hold/Underweight/Sell]
> Executive Summary: [2-3 sentences]
> Investment Thesis: [key reasons]
> Action         : [BUY/SELL/HOLD with specifics]
> Entry          : [price or range]
> Stop Loss      : [price — hard stop]
> Price Target 1 : [near-term, with timeframe]
> Price Target 2 : [longer-term, with timeframe]
> Time Horizon   : [months]
> Key Risk       : [the one thing that invalidates the thesis]
> ```

---

## QUICK REFERENCE

| Agent | Role | Key output |
|-------|------|-----------|
| 1. Market Analyst | Technicals | Trend, indicators, support/resistance |
| 2. Sentiment Analyst | Social mood | Score /10, band, confidence |
| 3. News Analyst | Events | Catalysts, risks, macro context |
| 4. Fundamentals | Financials | Valuation, margins, balance sheet |
| 5/6. Bull/Bear (×3) | Debate | 3-round investment case debate |
| 7. Research Manager | Verdict | Rating + investment plan |
| 8. Trader | Execution | Entry, stop, position size |
| 9. Risk Panel (×3) | Risk stress test | Aggressive/Conservative/Neutral |
| 10. Portfolio Manager | Final decision | Rating, targets, time horizon |

---

## AFTER ANALYSIS COMPLETES — SAVE REPORT

Once the Portfolio Manager delivers the final decision, ask the user:

> "Analysis complete. Do you want me to save this as a markdown report file?
> The file will include every agent's output, the full debate, and a final summary table.
> Reply **Yes** to save or **No** to skip."

If the user says **Yes**, create a file named `TICKER_ANALYSIS_DATE.md` (e.g. `AMD_ANALYSIS_2026-06-05.md`) with this structure:

```
# TICKER Analysis Report — DATE

## Summary (Quick Reference)
| Parameter     | Value |
|---------------|-------|
| Signal        | BUY/SELL/HOLD |
| Rating        | Overweight/etc |
| Entry         | $xxx |
| Stop Loss     | $xxx |
| Target 1      | $xxx (timeframe) |
| Target 2      | $xxx (timeframe) |
| Confidence    | High/Medium/Low |
| Mode          | Fast/Medium/Deep |

## Agent 1 — Market Analyst
[full output]

## Agent 2 — Sentiment Analyst
[full output]

## Agent 3 — News Analyst
[full output]

## Agent 4 — Fundamentals Analyst
[full output]

## Bull/Bear Debate
[all rounds]

## Agent 7 — Research Manager Verdict
[full output]

## Agent 8 — Trader Proposal
[full output]

## Risk Panel Debate (Deep mode only)
[full output]

## Agent 10 — Portfolio Manager Final Decision
[full output]
```

If the user says **No**, end the session normally.

---

## NOTES

- **Deep mode** = 3 Bull/Bear rounds + full 3-way risk debate (most thorough)
- **Medium mode** = 2 Bull/Bear rounds + brief risk summary
- **Fast mode** = 1 Bull/Bear round + brief risk summary
- Always ask for mode before starting — do not assume Deep
- Always check data is present before starting — ask user to run fetch_data.py if missing
- Always ask to save report after analysis completes — do not save without asking
- Stop loss must always be placed minimum **1.5×ATR** below entry
- Price target must always be **above current price** (sanity check)
- If data sources are missing (Reddit/StockTwits), flag in sentiment confidence — do not fabricate
