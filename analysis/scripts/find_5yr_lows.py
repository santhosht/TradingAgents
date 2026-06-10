"""
find_5yr_lows.py — Screen S&P 500 or Nasdaq 100 stocks near their 5-year low.

Uses a two-pass approach:
  Pass 1 — batch 1yr download (100 symbols/request) → keep stocks near 52-week low
  Pass 2 — individual 5yr download for candidates only → compute true 5yr low

Usage:
    python3 scripts/find_5yr_lows.py --sp500                     # S&P 500 (default)
    python3 scripts/find_5yr_lows.py --nasdaq100                 # Nasdaq 100
    python3 scripts/find_5yr_lows.py --symbols NKE LULU INTU     # specific symbols
    python3 scripts/find_5yr_lows.py --sp500 --threshold 15 --output sp500_lows.csv

Options:
    --sp500        Screen S&P 500 (default if no index flag given)
    --nasdaq100    Screen Nasdaq 100
    --symbols      Override: space-separated symbols
    --threshold    Max % above 5yr low to flag (default: 10)
    --prefilter    Max % above 52-week low to pass into Pass 2 (default: 20)
    --batch-size   Symbols per batch in Pass 1 (default: 100)
    --output       Save results CSV to this path (optional)
"""

import argparse
import datetime
import math
import sys
import time
import warnings

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")


# ── Index symbol lists (as of June 2026) ─────────────────────────────────────

SP500_SYMBOLS = [
    "MMM","AOS","ABT","ABBV","ACN","ADBE","AMD","AES","AFL","A","APD","ABNB","AKAM",
    "ALB","ARE","ALGN","ALLE","LNT","ALL","GOOGL","GOOG","MO","AMZN","AMCR","AEE",
    "AAL","AEP","AXP","AIG","AMT","AWK","AMP","AME","AMGN","APH","ADI","ANSS","AON",
    "APA","AAPL","AMAT","APTV","ACGL","ADM","ANET","AJG","AIZ","T","ATO","ADSK","ADP",
    "AZO","AVB","AVY","AXON","BKR","BALL","BAC","BK","BBWI","BAX","BDX","WRB","BBY",
    "BIO","TECH","BIIB","BLK","BX","BA","BSX","BMY","AVGO","BR","BRO","BF-B",
    "BLDR","BG","CDNS","CZR","CPT","CPB","COF","CAH","KMX","CCL","CARR","CAT","CBOE",
    "CBRE","CDW","CE","COR","CNC","CDAY","CF","CRL","SCHW","CHTR","CVX","CMG",
    "CB","CHD","CI","CINF","CTAS","CSCO","C","CFG","CLX","CME","CMS","KO","CTSH",
    "CL","CMCSA","CAG","COP","ED","STZ","CEG","COO","CPRT","GLW","CPAY","CTVA","CSGP",
    "COST","CTRA","CRWD","CCI","CSX","CMI","CVS","DHR","DRI","DVA","DAY","DECK","DE",
    "DAL","DVN","DXCM","FANG","DLR","DFS","DG","DLTR","D","DPZ","DOV","DOW","DHI",
    "DTE","DUK","DD","EMN","ETN","EBAY","ECL","EIX","EW","EA","ELV","EMR","ENPH",
    "ETR","EOG","EPAM","EQT","EFX","EQIX","EQR","ESS","EL","ETSY","EG","ES",
    "EXC","EXPE","EXPD","EXR","XOM","FFIV","FDS","FICO","FAST","FRT","FDX","FIS",
    "FITB","FSLR","FE","FI","FMC","F","FTNT","FTV","FOXA","FOX","BEN","FCX","GRMN",
    "IT","GE","GEHC","GEV","GEN","GNRC","GD","GIS","GM","GPC","GILD","GPN","GL",
    "GDDY","GS","HAL","HIG","HAS","HCA","DOC","HSIC","HSY","HES","HPE","HLT","HOLX",
    "HD","HON","HRL","HST","HWM","HPQ","HUBB","HUM","HBAN","HII","IBM","IEX","IDXX",
    "ITW","INCY","IR","PODD","INTC","ICE","IFF","IP","IPG","INTU","ISRG","IVZ","INVH",
    "IQV","IRM","JKHY","J","JBL","JPM","K","KVUE","KDP","KEY",
    "KEYS","KMB","KIM","KMI","KKR","KLAC","KHC","KR","LHX","LH","LRCX","LW","LVS",
    "LDOS","LEN","LII","LLY","LIN","LYV","LKQ","LMT","L","LOW","LULU","LYB","MTB",
    "MRO","MPC","MKTX","MAR","MMC","MLM","MAS","MA","MTCH","MKC","MCD","MCK","MDT",
    "MRK","META","MET","MTD","MGM","MCHP","MU","MSFT","MAA","MRNA","MHK","MOH","TAP",
    "MDLZ","MPWR","MNST","MCO","MS","MOS","MSI","MSCI","NDAQ","NTAP","NFLX","NEM",
    "NWSA","NWS","NEE","NKE","NI","NDSN","NSC","NTRS","NOC","NCLH","NRG","NUE","NVR",
    "NVDA","NWL","ORLY","OXY","ODFL","OMC","ON","OKE","ORCL","OTIS","PCAR",
    "PKG","PLTR","PH","PAYX","PAYC","PYPL","PNR","PEP","PFE","PCG","PM","PSX","PNW",
    "PNC","POOL","PPG","PPL","PFG","PG","PGR","PRU","PLD","PTC","PSA","PHM","QRVO",
    "PWR","QCOM","DGX","RL","RJF","RTX","O","REG","REGN","RF","RSG","RMD","RVTY",
    "ROK","ROL","ROP","ROST","RCL","SPGI","CRM","SBAC","SLB","STX","SRE","NOW","SHW",
    "SPG","SWKS","SJM","SW","SNA","SOLV","SO","LUV","SWK","SBUX","STT","STLD","STE",
    "SYK","SMCI","SYF","SNPS","SYY","TMUS","TROW","TTWO","TPR","TRGP","TGT","TEL",
    "TDY","TFX","TER","TSLA","TXN","TXT","TMO","TJX","TSCO","TT","TDG","TRV","TRMB",
    "TFC","TYL","TSN","USB","UBER","UDR","ULTA","UNP","UAL","UPS","URI","UNH","UHS",
    "VLO","VTR","VLTO","VRSN","VRSK","VZ","VRTX","VTRS","VICI","V","VST","VMC",
    "WAB","WMT","WBD","WM","WAT","WEC","WFC","WELL","WST","WDC","WY","WMB","WTW",
    "GWW","WYNN","XEL","XYL","YUM","ZBRA","ZBH","ZTS",
]

NASDAQ100_SYMBOLS = [
    "ADBE","ADI","ADP","ADSK","AEP","AMAT","AMD","AMGN","AMZN","ANSS",
    "APLD","AAPL","APP","ASML","AVGO","AXON","BIIB","BKNG","BKR","CDNS",
    "CDW","CEG","CHTR","CMCSA","COST","CPRT","CRWD","CSCO","CSGP","CSX",
    "DDOG","DXCM","EA","EXC","FANG","FAST","FTNT","GEHC","GFS","GILD",
    "GOOGL","HON","IDXX","ILMN","INTC","INTU","ISRG","KDP","KHC","KLAC",
    "LRCX","LULU","MAR","MCHP","MDB","MDLZ","MELI","META","MNST","MRNA",
    "MRVL","MSFT","MU","NFLX","NDSN","NVDA","ODFL","ON","ORLY","PAYX",
    "PCAR","PDD","PYPL","QCOM","REGN","ROP","ROST","SBUX","SIRI","SNPS",
    "TEAM","TMUS","TSLA","TTD","TTWO","TXN","VRSK","VRTX","WBA","WBD",
    "WDAY","XEL","ZS","ZM",
]


# ── Pass 1: batch 1yr download → 52-week low pre-filter ──────────────────────

def pass1_prefilter(symbols: list[str], prefilter_pct: float, batch_size: int) -> list[str]:
    print(f"\nPass 1 — 1yr batch download ({len(symbols)} symbols, {batch_size}/batch)")
    print(f"  Pre-filter: keep symbols within {prefilter_pct}% of 52-week low\n")

    end   = datetime.date.today()
    start = end - datetime.timedelta(days=370)

    candidates = []
    errors     = 0
    batches    = math.ceil(len(symbols) / batch_size)

    for i in range(batches):
        batch = symbols[i * batch_size : (i + 1) * batch_size]
        print(f"  Batch {i+1}/{batches} ({len(batch)} symbols)...", end=" ", flush=True)

        try:
            raw = yf.download(
                batch,
                start=start.isoformat(),
                end=end.isoformat(),
                auto_adjust=True,
                progress=False,
                group_by="ticker",
            )

            batch_hits = 0
            for sym in batch:
                try:
                    if len(batch) == 1:
                        close = raw["Close"]
                        low   = raw["Low"]
                    else:
                        close = raw[sym]["Close"]
                        low   = raw[sym]["Low"]

                    close = close.dropna()
                    low   = low.dropna()
                    if close.empty:
                        continue

                    current = float(close.iloc[-1])
                    low_52w = float(low.min())
                    pct     = (current - low_52w) / low_52w * 100 if low_52w else 999

                    if pct <= prefilter_pct:
                        candidates.append(sym)
                        batch_hits += 1
                except Exception:
                    errors += 1

            print(f"{batch_hits} candidates")

        except Exception as e:
            print(f"batch error: {e}")
            errors += 1

        time.sleep(0.3)

    print(f"\n  Pass 1 done — {len(candidates)} candidates from {len(symbols)} symbols ({errors} errors)")
    return candidates


# ── Pass 2: individual 5yr download → true 5yr low ───────────────────────────

def pass2_screen(candidates: list[str], threshold_pct: float) -> pd.DataFrame:
    print(f"\nPass 2 — 5yr individual download ({len(candidates)} candidates)")
    print(f"  Final filter: within {threshold_pct}% of 5-year low\n")

    end   = datetime.date.today()
    start = end - datetime.timedelta(days=365 * 5 + 5)

    rows = []
    for i, sym in enumerate(candidates, 1):
        print(f"  [{i}/{len(candidates)}] {sym:<8}", end=" ", flush=True)
        try:
            df = yf.download(sym, start=start.isoformat(), end=end.isoformat(),
                             auto_adjust=True, progress=False)
            if df.empty:
                print("no data")
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            low_5yr = float(df["Low"].min())
            current = float(df["Close"].iloc[-1])
            pct     = (current - low_5yr) / low_5yr * 100

            flag = "★" if pct <= threshold_pct else ""
            print(f"current=${current:.2f}  5yr_low=${low_5yr:.2f}  {pct:+.1f}%  {flag}")

            rows.append({
                "Symbol":      sym,
                "Current":     round(current, 2),
                "5yr Low":     round(low_5yr, 2),
                "% Above Low": round(pct, 1),
                "Near Low?":   pct <= threshold_pct,
            })
        except Exception as e:
            print(f"error: {e}")

        if i % 50 == 0:
            time.sleep(1)

    df_out = pd.DataFrame(rows)
    if df_out.empty:
        return df_out
    return df_out.sort_values("% Above Low").reset_index(drop=True)


# ── Output ────────────────────────────────────────────────────────────────────

def print_results(df: pd.DataFrame, threshold_pct: float, output_path: str | None):
    near = df[df["Near Low?"]]

    print(f"\n{'='*60}")
    print(f"  RESULTS — within {threshold_pct}% of 5-year low: {len(near)} / {len(df)} symbols")
    print(f"{'='*60}")
    if near.empty:
        print("  None found.")
    else:
        print(near[["Symbol", "Current", "5yr Low", "% Above Low"]].to_string(index=False))

    print(f"\n{'='*60}")
    print("  FULL CANDIDATES (sorted by % above 5yr low)")
    print(f"{'='*60}")
    print(df[["Symbol", "Current", "5yr Low", "% Above Low", "Near Low?"]].to_string(index=False))

    if output_path:
        df.to_csv(output_path, index=False)
        print(f"\n  Saved to {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Screen S&P 500 or Nasdaq 100 stocks near 5-year low")
    index_group = parser.add_mutually_exclusive_group()
    index_group.add_argument("--sp500",      action="store_true", help="Screen S&P 500 (default)")
    index_group.add_argument("--nasdaq100",  action="store_true", help="Screen Nasdaq 100")
    index_group.add_argument("--symbols",    nargs="+",           help="Screen specific symbols")
    parser.add_argument("--threshold",  type=float, default=10.0,
                        help="Max %% above 5yr low to flag (default: 10)")
    parser.add_argument("--prefilter",  type=float, default=20.0,
                        help="Max %% above 52-week low to pass into Pass 2 (default: 20)")
    parser.add_argument("--batch-size", type=int,   default=100,
                        help="Symbols per batch in Pass 1 (default: 100)")
    parser.add_argument("--output",     default=None,
                        help="Save results to this CSV path")
    args = parser.parse_args()

    t0 = time.time()

    if args.nasdaq100:
        symbols    = NASDAQ100_SYMBOLS
        index_name = "Nasdaq 100"
    elif args.symbols:
        symbols    = [s.upper() for s in args.symbols]
        index_name = "custom"
    else:
        symbols    = SP500_SYMBOLS
        index_name = "S&P 500"

    print(f"\n{'='*60}")
    print(f"  5-YEAR LOW SCREENER")
    print(f"  Index     : {index_name} ({len(symbols)} symbols)")
    print(f"  Date      : {datetime.date.today()}")
    print(f"  Threshold : within {args.threshold}% of 5yr low")
    print(f"  Pre-filter: within {args.prefilter}% of 52-week low")
    print(f"{'='*60}")

    candidates = pass1_prefilter(symbols, args.prefilter, args.batch_size)

    if not candidates:
        print("\nNo candidates passed the pre-filter.")
        sys.exit(0)

    df = pass2_screen(candidates, args.threshold)

    if df.empty:
        print("\nNo data returned in Pass 2.")
        sys.exit(0)

    print_results(df, args.threshold, args.output)

    print(f"\n  Total time: {(time.time() - t0)/60:.1f} min")


if __name__ == "__main__":
    main()
