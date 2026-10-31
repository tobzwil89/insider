"""Fundamentaldaten aus Gratis-Quellen sammeln (Planung #6, erst nur lokal).

Drei Quellen, alle ohne Schlüssel:
- TradingView-Screener (inoffiziell): alle Märkte, je Firma bis 20 Geschäftsjahre (Umsatz, EBITDA, Gewinn, FCF …),
  dazu aktuelle Kennzahlen und Schätzungen für das nächste Geschäftsjahr.
- onvista (inoffiziell, per ISIN): 4 Jahre Bilanz/GuV mit EBIT und Eigenkapital, Schätzungen bis ~2029.
- SEC companyfacts (offiziell, nur US-Firmen): ~15 Jahre vollständige Abschlüsse.

Ergebnis: daten/fundamental.csv im langen Format, eine Zeile je Firma, Quelle, Periode und Posten.
Jeder Lauf ersetzt die Datei (neuester Stand je Quelle). Periode: Geschäftsjahr („2025“), Schätzung („2026e“)
oder „aktuell“ (Kennzahlen zum Abrufzeitpunkt).

Aufruf: python3 -m pipeline.fundamental
"""

import datetime as dt
import re
import time

import pandas as pd
import requests

from pipeline import DATEN

DATEI = DATEN / "fundamental.csv"
BROWSER = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/141.0 Safari/537.36"}
SEC_HEADER = {"User-Agent": "insider-monitor tobzwilling@gmx.de"}

# US-Testauswahl (Ticker → TradingView-Symbol), damit der Weg über die SEC mitgetestet wird
USA_TEST = {
    "AAPL": "NASDAQ:AAPL", "MSFT": "NASDAQ:MSFT", "NVDA": "NASDAQ:NVDA", "AMZN": "NASDAQ:AMZN",
    "GOOGL": "NASDAQ:GOOGL", "META": "NASDAQ:META", "KO": "NYSE:KO", "AXP": "NYSE:AXP",
    "JNJ": "NYSE:JNJ", "BAC": "NYSE:BAC",
}

# Zusätzliche Firmen außerhalb von DAX/MDAX (ISIN → Yahoo-Ticker): Atoss zum Abgleich mit der AlleAktien-Karte
ZUSATZ = {"DE0005104400": "AOF.DE"}

# TradingView: Jahresreihen (neuestes Jahr zuerst, Länge = fiscal_period_fy_h)
TV_REIHEN = ["total_revenue", "gross_profit", "ebitda", "net_income", "earnings_per_share_diluted",
             "dps_common_stock_prim_issue", "free_cash_flow", "capital_expenditures_unchanged",
             "total_assets", "total_debt"]
# TradingView: Werte zum Abrufzeitpunkt
TV_AKTUELL = ["close", "market_cap_basic", "price_earnings_ttm", "price_sales_current", "price_book_fq",
              "net_margin_ttm", "gross_margin_ttm", "oper_income_margin_fy", "return_on_equity_fy",
              "return_on_assets_fy", "return_on_capital_employed_fy", "return_on_invested_capital_fy",
              "free_cash_flow_ttm", "dividends_yield_current", "net_debt_fy", "total_debt_fy",
              "cash_n_short_term_invest_fy", "total_equity_fy", "shrhldrs_equity_fy", "ebit_ttm", "ebitda_ttm",
              "total_revenue_ttm", "net_income_ttm", "earnings_per_share_diluted_ttm", "oper_income_fy",
              "total_current_liabilities_fy", "total_assets_fy", "total_shares_outstanding_fundamental",
              "net_debt_to_ebitda_fy", "cash_f_operating_activities_ttm", "dps_common_stock_prim_issue_fy",
              "number_of_employees"]
# TradingView: Schätzungen für das nächste Geschäftsjahr
TV_SCHAETZUNG = ["revenue_forecast_next_fy", "earnings_per_share_forecast_next_fy", "ebit_estimate_fy",
                 "ebitda_estimate_fy", "net_income_estimate_fy", "free_cash_flow_estimate_fy", "dps_estimate_fy"]
TV_TEXT = ["isin", "description", "currency", "sector", "industry"]

# SEC: unser Postenname → mögliche XBRL-Bezeichnungen (erste vorhandene je Jahr gilt)
SEC_POSTEN = {
    "umsatz": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
               "RevenuesNetOfInterestExpense", "SalesRevenueGoodsNet"],
    "ebit": ["OperatingIncomeLoss"],
    "gewinn": ["NetIncomeLoss"],
    "abschreibungen": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization"],
    "operativer_cf": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "dividende_je_aktie": ["CommonStockDividendsPerShareDeclared", "CommonStockDividendsPerShareCashPaid"],
    "eigenkapital": ["StockholdersEquity"],
    "bilanzsumme": ["Assets"],
    "kurzfr_verbindlichkeiten": ["LiabilitiesCurrent"],
    "kasse": ["CashAndCashEquivalentsAtCarryingValue"],
    "langfr_schulden": ["LongTermDebt", "LongTermDebtNoncurrent"],
}


def _zeile(isin, symbol, quelle, periode, posten, wert, waehrung, heute):
    return {"isin": isin, "symbol": symbol, "quelle": quelle, "periode": str(periode), "posten": posten,
            "wert": wert, "waehrung": waehrung, "abgerufen": heute}


def tradingview_symbole(isins: list[str], ticker: dict[str, str]) -> dict[str, str]:
    """ISIN → TradingView-Symbol. Bevorzugt die Hauptnotiz, sonst Xetra (z. B. Vorzugsaktien),
    sonst das Yahoo-Kürzel auf Xetra (TradingView führt z. B. Qiagen unter einer neueren ISIN)."""
    def suche(filter_):
        r = requests.post("https://scanner.tradingview.com/global/scan", headers=BROWSER, timeout=60,
                          json={"filter": filter_, "columns": ["isin", "exchange"], "range": [0, 5000]})
        r.raise_for_status()
        return r.json()["data"]

    ergebnis = {z["d"][0]: z["s"] for z in suche([{"left": "isin", "operation": "in_range", "right": isins},
                                                    {"left": "is_primary", "operation": "equal", "right": True}])}
    rest = [i for i in isins if i not in ergebnis]
    if rest:
        for z in suche([{"left": "isin", "operation": "in_range", "right": rest}]):
            if z["d"][1] == "XETR":
                ergebnis.setdefault(z["d"][0], z["s"])
    for isin in isins:  # nur, wenn das Symbol nicht schon einer anderen ISIN gehört (alte Zweit-ISIN, z. B. Fresenius)
        if isin not in ergebnis and ticker.get(isin, "").endswith(".DE") \
                and "XETR:" + ticker[isin].removesuffix(".DE") not in ergebnis.values():
            ergebnis[isin] = "XETR:" + ticker[isin].removesuffix(".DE")
    return ergebnis


def tradingview(symbole: list[str], heute: str, isin_von: dict[str, str]) -> list[dict]:
    """Ein Abruf für alle Symbole. Alle Werte in Handelswährung (TradingView rechnet z. B. Qiagen von USD in EUR um).
    isin_von: Symbol → unsere ISIN (sonst gilt die ISIN von TradingView)."""
    spalten = TV_TEXT + ["fiscal_period_fy_h"] + [f"{r}_fy_h" for r in TV_REIHEN] \
        + TV_AKTUELL + TV_SCHAETZUNG
    r = requests.post("https://scanner.tradingview.com/global/scan", headers=BROWSER, timeout=60,
                      json={"symbols": {"tickers": symbole}, "columns": spalten,
                            "price_conversion": {"to_symbol": True}})
    r.raise_for_status()
    zeilen = []
    for z in r.json()["data"]:
        w = dict(zip(spalten, z["d"]))
        isin, symbol, wae = isin_von.get(z["s"], w["isin"]), z["s"], w["currency"]
        jahre = w["fiscal_period_fy_h"] or []
        for reihe in TV_REIHEN:
            for jahr, wert in zip(jahre, w[f"{reihe}_fy_h"] or []):
                if wert is not None:
                    zeilen.append(_zeile(isin, symbol, "tradingview", jahr, reihe, wert, wae, heute))
        for feld in TV_AKTUELL:
            if w[feld] is not None:
                zeilen.append(_zeile(isin, symbol, "tradingview", "aktuell", feld, w[feld], wae, heute))
        naechstes = f"{jahre[0] + 1}e" if jahre else "naechstes"
        for feld in TV_SCHAETZUNG:
            if w[feld] is not None:
                zeilen.append(_zeile(isin, symbol, "tradingview", naechstes, feld, w[feld], wae, heute))
        for feld, posten in [("sector", "sector"), ("industry", "industry"), ("description", "name")]:
            if w[feld]:
                zeilen.append(_zeile(isin, symbol, "tradingview", "aktuell", posten, w[feld], "", heute))
    return zeilen


def _jahr(label: str) -> str:
    """onvista schreibt abweichende Geschäftsjahre als „24/25“ bzw. „25/26e“ → Endjahr wie bei TradingView."""
    m = re.fullmatch(r"\d{2}/(\d{2})(e?)", label)
    return f"20{m.group(1)}{m.group(2)}" if m else label


def onvista(isin: str, symbol: str, heute: str) -> list[dict]:
    """Alle Zahlenfelder aus Bilanz-, Kennzahlen- und Bewertungsliste (Präfix bilanz./kennzahl./bewertung.)."""
    time.sleep(0.5)
    r = requests.get(f"https://api.onvista.de/api/v1/stocks/ISIN:{isin}/snapshot", headers=BROWSER, timeout=60)
    if r.status_code == 404:
        return []
    r.raise_for_status()
    d = r.json()
    zeilen = []
    for liste, praefix in [("stocksBalanceSheetList", "bilanz"), ("stocksCnFinancialList", "kennzahl"),
                           ("stocksCnFundamentalList", "bewertung")]:
        for eintrag in (d.get(liste) or {}).get("list", []):
            wae = eintrag.get("isoCurrency", "")
            for feld, wert in eintrag.items():
                if isinstance(wert, (int, float)) and not isinstance(wert, bool) and feld not in ("idYear",):
                    zeilen.append(_zeile(isin, symbol, "onvista", _jahr(eintrag["label"]), f"{praefix}.{feld}", wert,
                                         wae, heute))
    return zeilen


def sec(ticker: str, isin: str, symbol: str, ciks: dict, heute: str) -> list[dict]:
    """Jahreswerte aus companyfacts. Ein Wert je Kalenderjahr über das SEC-Feld „frame“ (CY2024 bzw. CY2024Q4I)."""
    cik = ciks.get(ticker)
    if not cik:
        return []
    time.sleep(0.2)
    r = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json", headers=SEC_HEADER, timeout=60)
    r.raise_for_status()
    gaap = r.json()["facts"].get("us-gaap", {})
    zeilen = []
    for posten, namen in SEC_POSTEN.items():
        gefunden = {}  # Jahr → (Wert, Einheit)
        for name in namen:
            for einheit, werte in gaap.get(name, {}).get("units", {}).items():
                for f in werte:
                    m = re.fullmatch(r"CY(\d{4})(Q4I)?", f.get("frame", ""))
                    if m:
                        gefunden.setdefault(int(m.group(1)), (f["val"], einheit.split("/")[0]))
        for jahr, (wert, einheit) in sorted(gefunden.items()):
            zeilen.append(_zeile(isin, symbol, "sec", jahr, posten, wert, einheit, heute))
    return zeilen


def laden() -> pd.DataFrame:
    heute = dt.date.today().isoformat()
    firmen = pd.read_csv(DATEN / "firmen.csv").dropna(subset=["ticker"])  # ohne Ticker = alte Zweit-ISIN
    firmen = pd.concat([firmen, pd.DataFrame({"isin": list(ZUSATZ), "ticker": list(ZUSATZ.values()),
                                              "name": list(ZUSATZ.values())})])
    symbole = tradingview_symbole(firmen["isin"].tolist(), dict(zip(firmen["isin"], firmen["ticker"])))
    fehlend = sorted(set(firmen["name"]) - set(firmen["name"][firmen["isin"].isin(symbole)]))
    print(f"TradingView: {len(symbole)} von {len(firmen)} Firmen gefunden, fehlen: {', '.join(fehlend) or '–'}")

    zeilen = tradingview(list(symbole.values()) + list(USA_TEST.values()), heute,
                         {s: i for i, s in symbole.items()})
    print(f"TradingView: {len(zeilen)} Zeilen")
    us_isin = {z["symbol"]: z["isin"] for z in zeilen}

    for isin in firmen["isin"][firmen["isin"].isin(symbole)]:
        try:
            zeilen += onvista(isin, symbole.get(isin, ""), heute)
        except requests.RequestException as fehler:
            print(f"onvista {isin}: {fehler}")
    print(f"mit onvista: {len(zeilen)} Zeilen")

    ciks = {e["ticker"]: e["cik_str"] for e in requests.get(
        "https://www.sec.gov/files/company_tickers.json", headers=SEC_HEADER, timeout=60).json().values()}
    for ticker, symbol in USA_TEST.items():
        zeilen += sec(ticker, us_isin.get(symbol, ""), symbol, ciks, heute)
    print(f"mit SEC: {len(zeilen)} Zeilen")

    df = pd.DataFrame(zeilen)
    df.to_csv(DATEI, index=False)
    return df


if __name__ == "__main__":
    laden()
