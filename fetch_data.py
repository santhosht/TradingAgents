"""
fetch_data.py — Fetch all market data for a stock and format it for Claude analysis.

Usage:
    python fetch_data.py TICKER
    python fetch_data.py AMD
    python fetch_data.py SPY 2026-06-05

Output: prints a formatted data block + saves to TICKER_data.txt
Paste the output into Claude chat along with ANALYSIS_PROCESS.md
"""

import sys
import datetime
import json
import time
import html
import re
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

import pandas as pd
import yfinance as yf

# ── Config ────────────────────────────────────────────────────────────────────

TICKER        = sys.argv[1].upper() if len(sys.argv) > 1 else "SPY"
DATE          = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().strftime("%Y-%m-%d")
LOOKBACK_DAYS = 60    # display days (after indicator warmup)
NEWS_DAYS     = 7
REDDIT_SUBS   = ["wallstreetbets", "stocks", "investing"]

# Match the app's User-Agent so Reddit/StockTwits don't rate-limit
_UA = "tradingagents/0.2 (+https://github.com/TauricResearch/TradingAgents)"

# ── Helpers ───────────────────────────────────────────────────────────────────

def sep(title=""):
    if title:
        return f"\n{'='*60}\n  {title}\n{'='*60}"
    return "\n" + "-"*60

def safe(val, fmt=".2f"):
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return "N/A"
        return format(val, fmt)
    except Exception:
        return str(val)

# ── 1. Price & Technicals ─────────────────────────────────────────────────────

def fetch_price_and_technicals(ticker, lookback=60):
    end   = datetime.date.today()
    start = end - datetime.timedelta(days=lookback + 260)  # 260 extra for 200-SMA warmup
    df = yf.download(ticker, start=start.isoformat(), end=end.isoformat(), auto_adjust=True, progress=False)
    if df.empty:
        return None, "No price data found."

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.sort_index()

    # SMA
    df["SMA_50"]  = df["Close"].rolling(50).mean()
    df["SMA_200"] = df["Close"].rolling(200).mean()
    # EMA
    df["EMA_10"]  = df["Close"].ewm(span=10, adjust=False).mean()
    # Bollinger Bands (20, 2)
    df["BB_mid"]  = df["Close"].rolling(20).mean()
    df["BB_std"]  = df["Close"].rolling(20).std()
    df["BB_upper"]= df["BB_mid"] + 2 * df["BB_std"]
    df["BB_lower"]= df["BB_mid"] - 2 * df["BB_std"]
    # RSI (14)
    delta = df["Close"].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, float("nan"))
    df["RSI"] = 100 - (100 / (1 + rs))
    # MACD (12, 26, 9)
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"]        = ema12 - ema26
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_hist"]   = df["MACD"] - df["MACD_signal"]
    # ATR (14)
    high_low   = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close  = (df["Low"]  - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(14).mean()
    # VWMA (20)
    df["VWMA"] = (df["Close"] * df["Volume"]).rolling(20).sum() / df["Volume"].rolling(20).sum()
    # MFI (14) — Money Flow Index (app supports this, our script previously missed it)
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    raw_mf  = typical * df["Volume"]
    pos_mf  = raw_mf.where(typical > typical.shift(1), 0).rolling(14).sum()
    neg_mf  = raw_mf.where(typical < typical.shift(1), 0).rolling(14).sum()
    mf_ratio = pos_mf / neg_mf.replace(0, float("nan"))
    df["MFI"] = 100 - (100 / (1 + mf_ratio))

    # Drop incomplete today row, trim to display window
    df = df[df["Close"].notna()]
    df = df.tail(lookback)
    return df, None


def format_price_section(df, ticker):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    out  = []
    out.append(sep(f"PRICE & TECHNICALS — {ticker}"))

    out.append("\n[Last 20 Trading Days]\n")
    out.append(f"{'Date':<12} {'Open':>8} {'High':>8} {'Low':>8} {'Close':>8} {'Volume':>12}")
    out.append("-" * 62)
    for idx, row in df.tail(20).iterrows():
        date_str = idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)[:10]
        out.append(
            f"{date_str:<12} {safe(row['Open']):>8} {safe(row['High']):>8} "
            f"{safe(row['Low']):>8} {safe(row['Close']):>8} {int(row['Volume'] or 0):>12,}"
        )

    out.append(sep("KEY INDICATORS (latest trading day)"))
    out.append(f"  Close        : ${safe(last['Close'])}")
    out.append(f"  Prev Close   : ${safe(prev['Close'])}")
    chg = last['Close'] - prev['Close']
    pct = chg / prev['Close'] * 100 if prev['Close'] else 0
    out.append(f"  Day Change   : {'+' if chg>=0 else ''}{safe(chg)} ({'+' if pct>=0 else ''}{safe(pct)}%)")
    out.append(f"")
    out.append(f"  EMA 10       : ${safe(last['EMA_10'])}")
    out.append(f"  SMA 50       : ${safe(last['SMA_50'])}")
    out.append(f"  SMA 200      : ${safe(last['SMA_200'])}")
    out.append(f"  VWMA 20      : ${safe(last['VWMA'])}")
    out.append(f"")
    out.append(f"  RSI (14)     : {safe(last['RSI'])}")
    out.append(f"  MFI (14)     : {safe(last['MFI'])}")
    out.append(f"  MACD         : {safe(last['MACD'])}")
    out.append(f"  MACD Signal  : {safe(last['MACD_signal'])}")
    out.append(f"  MACD Hist    : {safe(last['MACD_hist'])}")
    out.append(f"")
    out.append(f"  Bollinger Up : ${safe(last['BB_upper'])}")
    out.append(f"  Bollinger Mid: ${safe(last['BB_mid'])}")
    out.append(f"  Bollinger Low: ${safe(last['BB_lower'])}")
    out.append(f"  ATR (14)     : ${safe(last['ATR'])}")

    out.append(sep("PRICE vs MOVING AVERAGES"))
    close = last['Close']
    for label, ma_val in [("SMA 50", last['SMA_50']), ("SMA 200", last['SMA_200']), ("EMA 10", last['EMA_10'])]:
        if ma_val and not pd.isna(ma_val):
            diff = (close - ma_val) / ma_val * 100
            sign = "above" if diff >= 0 else "below"
            out.append(f"  Price is {abs(diff):.1f}% {sign} {label} (${safe(ma_val)})")

    return "\n".join(out)

# ── 2. Fundamentals (overview) ────────────────────────────────────────────────

def fetch_fundamentals(ticker):
    t    = yf.Ticker(ticker)
    info = t.info or {}
    out  = []
    out.append(sep(f"FUNDAMENTALS OVERVIEW — {ticker}"))

    fields = [
        ("Company",          info.get("longName") or info.get("shortName")),
        ("Sector",           info.get("sector")),
        ("Industry",         info.get("industry")),
        ("Exchange",         info.get("exchange")),
        ("Currency",         info.get("currency")),
        ("Market Cap",       f"${info.get('marketCap', 0)/1e9:.2f}B" if info.get("marketCap") else "N/A"),
        ("Beta",             safe(info.get("beta"))),
        ("52W High",         safe(info.get("fiftyTwoWeekHigh"))),
        ("52W Low",          safe(info.get("fiftyTwoWeekLow"))),
        ("50D Avg",          safe(info.get("fiftyDayAverage"))),
        ("200D Avg",         safe(info.get("twoHundredDayAverage"))),
        ("",                 ""),
        ("P/E (TTM)",        safe(info.get("trailingPE"))),
        ("Forward P/E",      safe(info.get("forwardPE"))),
        ("PEG Ratio",        safe(info.get("pegRatio"))),
        ("Price/Book",       safe(info.get("priceToBook"))),
        ("EV/EBITDA",        safe(info.get("enterpriseToEbitda"))),
        ("Book Value",       safe(info.get("bookValue"))),
        ("",                 ""),
        ("Revenue (TTM)",    f"${info.get('totalRevenue', 0)/1e9:.2f}B" if info.get("totalRevenue") else "N/A"),
        ("Gross Profit",     f"${info.get('grossProfits', 0)/1e9:.2f}B" if info.get("grossProfits") else "N/A"),
        ("EBITDA",           f"${info.get('ebitda', 0)/1e9:.2f}B" if info.get("ebitda") else "N/A"),
        ("Net Income",       f"${info.get('netIncomeToCommon', 0)/1e9:.2f}B" if info.get("netIncomeToCommon") else "N/A"),
        ("Gross Margin",     f"{(info.get('grossMargins', 0) or 0)*100:.1f}%"),
        ("Op Margin",        f"{(info.get('operatingMargins', 0) or 0)*100:.1f}%"),
        ("Profit Margin",    f"{(info.get('profitMargins', 0) or 0)*100:.1f}%"),
        ("ROE",              f"{(info.get('returnOnEquity', 0) or 0)*100:.1f}%"),
        ("ROA",              f"{(info.get('returnOnAssets', 0) or 0)*100:.1f}%"),
        ("",                 ""),
        ("EPS (TTM)",        safe(info.get("trailingEps"))),
        ("Forward EPS",      safe(info.get("forwardEps"))),
        ("",                 ""),
        ("Cash",             f"${info.get('totalCash', 0)/1e9:.2f}B" if info.get("totalCash") else "N/A"),
        ("Total Debt",       f"${info.get('totalDebt', 0)/1e9:.2f}B" if info.get("totalDebt") else "N/A"),
        ("D/E Ratio",        safe(info.get("debtToEquity"))),
        ("Current Ratio",    safe(info.get("currentRatio"))),
        ("FCF (TTM)",        f"${info.get('freeCashflow', 0)/1e9:.2f}B" if info.get("freeCashflow") else "N/A"),
        ("",                 ""),
        ("Div Yield",        f"{(info.get('dividendYield', 0) or 0)*100:.2f}%"),
        ("Payout Ratio",     f"{(info.get('payoutRatio', 0) or 0)*100:.1f}%"),
        ("",                 ""),
        ("Analyst Target",   f"${safe(info.get('targetMeanPrice'))}"),
        ("Target High",      f"${safe(info.get('targetHighPrice'))}"),
        ("Target Low",       f"${safe(info.get('targetLowPrice'))}"),
        ("Recommendation",   (info.get("recommendationKey") or "N/A").upper()),
    ]

    for label, val in fields:
        if label == "":
            out.append("")
        else:
            out.append(f"  {label:<18}: {val}")

    return "\n".join(out)

# ── 3. Financial Statements ───────────────────────────────────────────────────

def _fmt_statement(df, title, ticker):
    """Format a quarterly financial statement DataFrame cleanly."""
    out = [sep(f"{title} — {ticker} (Quarterly)")]
    if df is None or df.empty:
        out.append("  No data available.")
        return "\n".join(out)
    # Show last 4 quarters, key rows only (limit rows to avoid context bloat)
    df = df.iloc[:, :4]  # last 4 quarters
    df.columns = [str(c)[:10] for c in df.columns]
    out.append(df.to_string())
    return "\n".join(out)

def fetch_financial_statements(ticker):
    t   = yf.Ticker(ticker)
    out = []
    try:
        out.append(_fmt_statement(t.quarterly_income_stmt,  "INCOME STATEMENT", ticker))
    except Exception as e:
        out.append(f"\n[Income Statement Error: {e}]")
    try:
        out.append(_fmt_statement(t.quarterly_balance_sheet, "BALANCE SHEET", ticker))
    except Exception as e:
        out.append(f"\n[Balance Sheet Error: {e}]")
    try:
        out.append(_fmt_statement(t.quarterly_cashflow, "CASH FLOW STATEMENT", ticker))
    except Exception as e:
        out.append(f"\n[Cash Flow Error: {e}]")
    return "\n".join(out)

# ── 4. Insider Transactions ───────────────────────────────────────────────────

def fetch_insider_transactions(ticker):
    out = [sep(f"INSIDER TRANSACTIONS — {ticker}")]
    try:
        t    = yf.Ticker(ticker)
        data = t.insider_transactions
        if data is None or data.empty:
            out.append("  No insider transactions reported.")
        else:
            out.append(data.head(15).to_string())
    except Exception as e:
        out.append(f"  Error: {e}")
    return "\n".join(out)

# ── 5. News ───────────────────────────────────────────────────────────────────

def fetch_news(ticker, days=7):
    t    = yf.Ticker(ticker)
    news = t.news or []
    out  = [sep(f"NEWS — {ticker} (last {days} days)")]
    shown = 0
    for item in news:
        try:
            content = item.get("content", {})
            title   = content.get("title") or item.get("title", "")
            summary = content.get("summary") or ""
            source  = content.get("provider", {}).get("displayName") if isinstance(content.get("provider"), dict) else ""
            pub_ts  = content.get("pubDate") or ""
            if not title:
                continue
            out.append(f"\n• {title}")
            if source:
                out.append(f"  Source : {source}")
            if pub_ts:
                out.append(f"  Date   : {pub_ts[:10]}")
            if summary:
                out.append(f"  Summary: {summary[:300]}")
            shown += 1
            if shown >= 15:
                break
        except Exception:
            continue
    if shown == 0:
        out.append("  No recent news found.")
    return "\n".join(out)

# ── 6. Reddit ─────────────────────────────────────────────────────────────────

def _strip_html(content):
    if not content:
        return ""
    if "<!-- SC_OFF -->" in content and "<!-- SC_ON -->" in content:
        content = content.split("<!-- SC_OFF -->")[1].split("<!-- SC_ON -->")[0]
    text = re.sub(r"<[^>]+>", " ", content)
    return " ".join(html.unescape(text).split())

def _fetch_sub_json(ticker, sub, limit=5):
    qs  = urlencode({"q": ticker, "restrict_sr": "on", "sort": "new", "t": "week", "limit": limit})
    url = f"https://www.reddit.com/r/{sub}/search.json?{qs}"
    req = Request(url, headers={"User-Agent": _UA, "Accept": "application/json"})
    try:
        with urlopen(req, timeout=10) as resp:
            payload = json.loads(resp.read())
        children = (payload.get("data") or {}).get("children") or []
        return [c.get("data", {}) for c in children if isinstance(c, dict)], "json"
    except Exception:
        return [], "json_failed"

def _fetch_sub_rss(ticker, sub, limit=5):
    qs  = urlencode({"q": ticker, "restrict_sr": "on", "sort": "new", "t": "week", "limit": limit})
    url = f"https://www.reddit.com/r/{sub}/search.rss?{qs}"
    req = Request(url, headers={"User-Agent": _UA})
    ns  = {"atom": "http://www.w3.org/2005/Atom"}
    posts = []
    try:
        with urlopen(req, timeout=10) as resp:
            root = ET.fromstring(resp.read())
        for entry in root.findall("atom:entry", ns)[:limit]:
            t_el = entry.find("atom:title", ns)
            p_el = entry.find("atom:published", ns)
            c_el = entry.find("atom:content", ns)
            title = t_el.text if t_el is not None else ""
            pub   = p_el.text if p_el is not None else ""
            body  = _strip_html(c_el.text if c_el is not None else "")
            created_utc = None
            try:
                normalized = pub[:-1] + "+00:00" if pub.endswith("Z") else pub
                created_utc = datetime.datetime.fromisoformat(normalized).timestamp()
            except Exception:
                pass
            posts.append({"title": title, "score": None, "num_comments": None,
                          "created_utc": created_utc, "selftext": body, "source": "rss"})
    except Exception:
        pass
    return posts, "rss"

def fetch_reddit(ticker, subs=REDDIT_SUBS):
    out = [sep(f"REDDIT SENTIMENT — {ticker}")]
    total = 0
    for i, sub in enumerate(subs):
        if i > 0:
            time.sleep(0.4)
        posts, source = _fetch_sub_json(ticker, sub)
        if not posts:
            posts, source = _fetch_sub_rss(ticker, sub)
        total += len(posts)
        via_rss = source == "rss"
        if not posts:
            out.append(f"\n[r/{sub}]\n  No posts found mentioning {ticker} in the past 7 days.")
            continue
        header = f"\n[r/{sub} — {len(posts)} posts"
        header += " via RSS (no scores)" if via_rss else ""
        header += "]"
        out.append(header)
        for p in posts:
            title   = (p.get("title") or "").replace("\n", " ").strip()
            score   = p.get("score")
            comments= p.get("num_comments")
            created = p.get("created_utc")
            date_s  = time.strftime("%Y-%m-%d", time.gmtime(created)) if created else "?"
            meta    = date_s
            if score is not None and comments is not None:
                meta += f" · {score}↑ · {comments}c"
            selftext = (p.get("selftext") or "").replace("\n", " ").strip()[:200]
            out.append(f"  [{meta}] {title}")
            if selftext:
                out.append(f"    ↳ {selftext}")
    if total == 0:
        out.append("  No Reddit posts found across all subreddits.")
    return "\n".join(out)

# ── 7. StockTwits ─────────────────────────────────────────────────────────────

def fetch_stocktwits(ticker):
    out = [sep(f"STOCKTWITS SENTIMENT — {ticker}")]
    url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
    req = Request(url, headers={"User-Agent": _UA, "Accept": "application/json"})
    try:
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        msgs = data.get("messages", []) if isinstance(data, dict) else []
        if not msgs:
            out.append("  No messages found.")
            return "\n".join(out)
        bull = bear = unlabeled = 0
        lines = []
        for m in msgs[:30]:
            created  = m.get("created_at", "")
            user     = (m.get("user") or {}).get("username", "?")
            entities = m.get("entities") or {}
            sent_obj = entities.get("sentiment") or {}
            sentiment= sent_obj.get("basic") if isinstance(sent_obj, dict) else None
            body     = (m.get("body") or "").replace("\n", " ").strip()[:280]
            if sentiment == "Bullish":
                bull += 1; tag = "Bullish"
            elif sentiment == "Bearish":
                bear += 1; tag = "Bearish"
            else:
                unlabeled += 1; tag = "no-label"
            lines.append(f"  [{created[:10]} · @{user} · {tag}] {body}")
        total = bull + bear + unlabeled
        bull_pct = round(100 * bull / total) if total else 0
        bear_pct = round(100 * bear / total) if total else 0
        out.append(f"  Bullish: {bull} ({bull_pct}%) · Bearish: {bear} ({bear_pct}%) · Unlabeled: {unlabeled} · Total: {total}")
        out.append("")
        out.extend(lines)
    except Exception as e:
        out.append(f"  Unavailable: {type(e).__name__}")
    return "\n".join(out)

# ── 8. Global Macro News ──────────────────────────────────────────────────────

def fetch_global_news():
    out = [sep("GLOBAL MACRO NEWS")]
    feeds = [
        ("Reuters Markets", "https://feeds.reuters.com/reuters/businessNews"),
        ("Yahoo Finance",   "https://finance.yahoo.com/news/rssindex"),
    ]
    for name, url in feeds:
        out.append(f"\n[{name}]")
        try:
            req  = Request(url, headers={"User-Agent": _UA})
            with urlopen(req, timeout=10) as resp:
                root = ET.fromstring(resp.read())
            items = root.findall(".//item")[:8]
            if not items:
                out.append("  No items.")
                continue
            for item in items:
                t_el  = item.find("title")
                title = t_el.text if t_el is not None else ""
                out.append(f"  • {(title or '').strip()[:120]}")
        except Exception as e:
            out.append(f"  Unavailable: {type(e).__name__}")
    return "\n".join(out)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\nFetching data for {TICKER} as of {DATE}...")

    sections = []

    header = f"""
{'#'*60}
  MARKET DATA REPORT
  Ticker : {TICKER}
  Date   : {DATE}
  Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'#'*60}

[Claude: Follow ANALYSIS_PROCESS.md. Data below is the input for analysis.]
"""
    sections.append(header)

    print("  → Price & technicals...")
    df, err = fetch_price_and_technicals(TICKER)
    sections.append(format_price_section(df, TICKER) if not err else f"\n[Price Error: {err}]")

    print("  → Fundamentals overview...")
    sections.append(fetch_fundamentals(TICKER))

    print("  → Financial statements (income/balance/cashflow)...")
    sections.append(fetch_financial_statements(TICKER))

    print("  → Insider transactions...")
    sections.append(fetch_insider_transactions(TICKER))

    print("  → News...")
    sections.append(fetch_news(TICKER))

    print("  → Reddit sentiment...")
    sections.append(fetch_reddit(TICKER))

    print("  → StockTwits...")
    sections.append(fetch_stocktwits(TICKER))

    print("  → Global macro news...")
    sections.append(fetch_global_news())

    sections.append(f"\n{'#'*60}\n  END OF DATA\n{'#'*60}\n")

    output = "\n".join(sections)

    filename = f"{TICKER}_data.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"\n  ✓ Saved to {filename}")
    print(f"  ✓ Paste into Claude chat with ANALYSIS_PROCESS.md\n")
    print(output)


if __name__ == "__main__":
    main()
