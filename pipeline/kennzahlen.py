"""Kennzahlen je Firma aus daten/fundamental.csv (Planung #6, erst nur lokal).

Alle Kennzahlen selbst gerechnet, Formeln stehen hier. Quellen: TradingView (Jahresreihen bis 20 Jahre, aktuelle
Werte, Schätzung nächstes Jahr), onvista (EBIT und Eigenkapital 4 Jahre, Gewinnschätzungen 3 Jahre), SEC (EBIT USA).

EBIT über 10 Jahre gibt es nur für US-Firmen (SEC). Sonst gilt für 10-Jahres-Werte EBITDA als Ersatz,
Spalte `ebit_reihe` sagt, welche Reihe genommen wurde.

Banken und Versicherer (Sektor „Finance“): EBIT, ROCE und Nettoverschuldung ergeben dort keinen Sinn → leer.

Aufruf: python3 -m pipeline.kennzahlen
"""

import pandas as pd

from pipeline import DATEN

DATEI = DATEN / "kennzahlen.csv"


def _wachstum(reihe: pd.Series, jahre: int):
    """Jährliches Wachstum (CAGR) vom Wert vor `jahre` Jahren bis zum letzten; leer bei fehlenden/negativen Werten."""
    if len(reihe) <= jahre:
        return None
    start, ende = reihe.iloc[-1 - jahre], reihe.iloc[-1]
    if start <= 0 or ende <= 0:
        return None
    return (ende / start) ** (1 / jahre) - 1


def _max_rueckgang(reihe: pd.Series):
    """Größter Rückgang vom bisherigen Höchststand (0 = nie gefallen). Ab Höchststand ≤ 0 nicht sinnvoll → leer."""
    if reihe.empty or reihe.cummax().min() <= 0:
        return None
    return float((1 - reihe / reihe.cummax()).max())


def firma(g: pd.DataFrame) -> dict:
    """g: alle Zeilen einer ISIN aus fundamental.csv (wert numerisch, Text in `text`)."""
    def jahresreihe(quelle, posten):
        x = g[(g.quelle == quelle) & (g.posten == posten) & g.periode.str.fullmatch(r"\d{4}")]
        return x.set_index(x.periode.astype(int)).wert.dropna().sort_index()

    def aktuell(posten):
        x = g[(g.quelle == "tradingview") & (g.periode == "aktuell") & (g.posten == posten)].wert.dropna()
        return x.iloc[0] if len(x) else None

    def teile(a, b):
        return a / b if a is not None and b not in (None, 0) else None

    text = g[g.posten.isin(["name", "sector", "industry"])].set_index("posten").text.to_dict()
    finanz = text.get("sector") == "Finance"
    letztes = jahresreihe("tradingview", "total_revenue")
    letztes_jahr = int(letztes.index[-1]) if len(letztes) else None

    umsatz = jahresreihe("tradingview", "total_revenue")
    gewinn = jahresreihe("tradingview", "net_income")
    ebitda = jahresreihe("tradingview", "ebitda")
    ebit = jahresreihe("sec", "ebit")
    if len(ebit) < 11:
        ebit = jahresreihe("onvista", "kennzahl.cnEbit")
    ebit_reihe, reihe10 = ("ebit", ebit) if len(ebit) >= 11 else ("ebitda", ebitda)

    # Eigenkapitalrendite: Gewinn des letzten Geschäftsjahrs / Eigenkapital am Jahresende (wie AlleAktien)
    ek = jahresreihe("onvista", "bilanz.shareholdersEquity")
    if ek.empty:
        ek = jahresreihe("sec", "eigenkapital")
    ek_rendite = None
    if letztes_jahr in ek.index and letztes_jahr in gewinn.index:
        ek_rendite = teile(gewinn[letztes_jahr], ek[letztes_jahr])

    # Gewinn je Aktie: letztes Ist-Jahr (onvista) und Schätzung in 3 Jahren
    eps = g[(g.quelle == "onvista") & (g.posten == "kennzahl.cnEpsAdj")].set_index("periode").wert.dropna()
    eps_3je = None
    if letztes_jahr and str(letztes_jahr) in eps.index and f"{letztes_jahr + 3}e" in eps.index:
        a, b = eps[str(letztes_jahr)], eps[f"{letztes_jahr + 3}e"]
        eps_3je = (b / a) ** (1 / 3) - 1 if a > 0 and b > 0 else None

    def schaetzung(posten):
        x = g[(g.quelle == "tradingview") & (g.posten == posten) & g.periode.str.endswith("e")].wert.dropna()
        return x.iloc[0] if len(x) else None

    ebit_ttm, ebitda_ttm = aktuell("ebit_ttm"), aktuell("ebitda_ttm")
    netto_schulden = aktuell("net_debt_fy")
    kapital = None
    if aktuell("total_assets_fy") is not None and aktuell("total_current_liabilities_fy") is not None:
        kapital = aktuell("total_assets_fy") - aktuell("total_current_liabilities_fy")
    dividende = aktuell("dividends_yield_current")
    ebit_letzt = ebit.get(letztes_jahr) if letztes_jahr else None

    gewinn10 = gewinn[gewinn.index > (letztes_jahr or 0) - 11]
    zeile = {
        "name": text.get("name"), "sektor": text.get("sector"), "branche": text.get("industry"),
        "finanzwert": finanz, "letztes_gj": letztes_jahr, "jahre_umsatz": len(umsatz),
        # Kennzahlen
        "marktkap": aktuell("market_cap_basic"), "kurs": aktuell("close"),
        "kgv_ttm": aktuell("price_earnings_ttm"),
        "kgv_forward": teile(aktuell("close"), schaetzung("earnings_per_share_forecast_next_fy")),
        "kuv": aktuell("price_sales_current"), "kbv": aktuell("price_book_fq"),
        # Rentabilität
        "gewinnmarge": teile(aktuell("net_income_ttm"), aktuell("total_revenue_ttm")),
        "ek_rendite": ek_rendite,
        "roce": None if finanz else teile(ebit_ttm, kapital),
        "fcf_rendite": teile(aktuell("free_cash_flow_ttm"), aktuell("market_cap_basic")),
        "dividendenrendite": dividende / 100 if dividende is not None else None,
        # Risiko
        "verschuldung_ebit": None if finanz else teile(netto_schulden, ebit_ttm),
        "verschuldung_ebitda": None if finanz else teile(netto_schulden, ebitda_ttm),
        "ebit_reihe": ebit_reihe,
        "max_rueckgang_ebit_10j": None if finanz else _max_rueckgang(reihe10.iloc[-11:]),
        "gewinnjahre_10j": int((gewinn10 > 0).sum()) if len(gewinn10) else None,
        "gewinnanstiege_10j": int((gewinn10.diff().iloc[1:] >= 0).sum()) if len(gewinn10) > 1 else None,
        # Wachstum
        "umsatz_wachstum_10j": _wachstum(umsatz, 10),
        "umsatz_wachstum_3j": _wachstum(umsatz, 3),
        "umsatz_wachstum_1je": teile(schaetzung("revenue_forecast_next_fy"), umsatz.iloc[-1] if len(umsatz) else None),
        "ebit_wachstum_10j": None if finanz else _wachstum(reihe10, 10),
        "ebit_wachstum_3j": None if finanz else _wachstum(ebit, 3),
        "ebit_wachstum_1je": None if finanz else teile(schaetzung("ebit_estimate_fy"), ebit_letzt),
        "eps_wachstum_3je": eps_3je,
        # Renditeerwartung = erwartetes Gewinnwachstum je Aktie p. a. (3 Jahre) + Dividendenrendite
        "renditeerwartung": eps_3je + dividende / 100 if eps_3je is not None and dividende is not None else None,
    }
    for name in ["umsatz_wachstum_1je", "ebit_wachstum_1je"]:
        if zeile[name] is not None:
            zeile[name] -= 1
    return zeile


def berechnen() -> pd.DataFrame:
    d = pd.read_csv(DATEN / "fundamental.csv", dtype={"periode": str}, low_memory=False)
    d["text"] = d.wert
    d["wert"] = pd.to_numeric(d.wert, errors="coerce")
    ergebnis = pd.DataFrame([{"isin": isin, **firma(g)} for isin, g in d.groupby("isin")])
    ergebnis.to_csv(DATEI, index=False)
    return ergebnis


if __name__ == "__main__":
    berechnen()
