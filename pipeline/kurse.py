"""Tägliche Schlusskurse von Yahoo, um Dividenden und Splits bereinigt.

Angelehnt an strategie_labor/labor/daten.py, aber ohne Zwischenspeicher: In der GitHub
Action wird jedes Mal frisch geladen, das dauert für rund 100 Ticker nur Sekunden.
"""

import logging

import pandas as pd
import yfinance as yf

logging.getLogger("yfinance").setLevel(logging.CRITICAL)


def lade_kurse(ticker: list, start) -> pd.DataFrame:
    """Schlusskurse als Tabelle: Zeilen = Handelstage, Spalten = Ticker."""
    ticker = sorted(set(ticker))
    df = yf.download(ticker, start=pd.Timestamp(start).strftime("%Y-%m-%d"), auto_adjust=True,
                     progress=False, threads=True)
    if df is None or df.empty:
        raise RuntimeError("Yahoo liefert keine Kurse")
    kurse = df["Close"] if isinstance(df.columns, pd.MultiIndex) else df[["Close"]].set_axis(ticker, axis=1)
    kurse.index = pd.DatetimeIndex(kurse.index).tz_localize(None).normalize()
    # Der heutige Kurs ist erst nach Xetra-Schluss (17:30) endgültig
    jetzt = pd.Timestamp.now(tz="Europe/Berlin")
    if jetzt.hour < 18:
        kurse = kurse[kurse.index < jetzt.tz_localize(None).normalize()]
    fehlend = [t for t in ticker if t not in kurse.columns or kurse[t].isna().all()]
    if fehlend:
        print(f"  ohne Kurse: {', '.join(fehlend)}")
    return kurse.dropna(how="all")
