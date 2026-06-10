"""
fetch_live_data.py — Live price + technicals for morning check.

Usage:
    python fetch_live_data.py AMD
    python fetch_live_data.py AMD MKC
"""

import sys
import datetime
import pandas as pd
import yfinance as yf

sys.path.insert(0, ".")
from fetch_data import fetch_price_and_technicals, fetch_live_quote


def morning_summary(ticker):
    fi = yf.Ticker(ticker).fast_info
    price      = fi.last_price
    prev_close = fi.previous_close
    volume     = fi.last_volume
    day_chg    = (price - prev_close) / prev_close * 100 if prev_close else 0

    df, err = fetch_price_and_technicals(ticker)
    if err or df is None:
        print(f"{ticker}: {err}"); return

    last = df.iloc[-1]

    rsi  = last["RSI"]
    macd = last["MACD"];  sig = last["MACD_signal"]
    vwma = last["VWMA"]
    bb_upper = last["BB_upper"]; bb_lower = last["BB_lower"]; bb_mid = last["BB_mid"]
    ema10 = last["EMA_10"]
    atr   = last["ATR"]

    if macd > sig and df.iloc[-2]["MACD"] <= df.iloc[-2]["MACD_signal"]:
        macd_status = "bullish crossover"
    elif macd < sig and df.iloc[-2]["MACD"] >= df.iloc[-2]["MACD_signal"]:
        macd_status = "bearish crossover"
    elif macd > sig:
        macd_status = f"bullish (MACD {macd:.2f} > Signal {sig:.2f})"
    else:
        macd_status = f"bearish (MACD {macd:.2f} < Signal {sig:.2f})"

    if price >= bb_upper * 0.97:
        bb_pos = f"near upper (${bb_upper:.2f})"
    elif price <= bb_lower * 1.03:
        bb_pos = f"near lower (${bb_lower:.2f})"
    else:
        bb_pos = f"mid (${bb_mid:.2f})"

    if rsi > 70:   rsi_label = "overbought"
    elif rsi < 40: rsi_label = "oversold"
    elif 45 <= rsi <= 55: rsi_label = "neutral"
    else:          rsi_label = "elevated" if rsi > 55 else "low"

    print(f"\n=== {ticker} ===")
    print(f"Price:      ${price:.2f}  ({day_chg:+.2f}%)  Vol: {volume/1e6:.1f}M")
    print(f"EMA10:      ${ema10:.2f}  ATR: ${atr:.2f}")
    print()
    print(f"RSI:        {rsi:.1f}  ({rsi_label})")
    print(f"MACD:       {macd_status}")
    print(f"vs VWMA20:  {'above' if price > vwma else 'below'} (${vwma:.2f})")
    print(f"Bollinger:  {bb_pos}")
    print()
    print("Last 5 days:")
    for idx, row in df.tail(5).iterrows():
        move = abs(row["Close"] - row["Open"]) / row["Open"] * 100
        calm = "calm" if row["Volume"] < 25e6 and move < atr / price * 100 else ""
        print(f"  {str(idx.date())}  ${row['Close']:.2f}  {row['Volume']/1e6:.1f}M  {move:.1f}%  {calm}")


if __name__ == "__main__":
    tickers = [t.upper() for t in sys.argv[1:]] if len(sys.argv) > 1 else ["SPY"]
    for t in tickers:
        morning_summary(t)
