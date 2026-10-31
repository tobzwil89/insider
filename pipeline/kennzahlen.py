"""Kennzahlen je Firma aus daten/fundamental.csv (Planung #6, erst nur lokal).

Alle Kennzahlen selbst gerechnet, Formeln stehen hier. Quellen: TradingView (Jahresreihen bis 20 Jahre, aktuelle
Werte, Schätzung nächstes Jahr), Eulerpool (EBIT 25+ Jahre weltweit, Schätzungen bis ~2030), onvista (EBIT und
Eigenkapital 4 Jahre, Gewinnschätzungen 3 Jahre), SEC (EBIT USA), Nasdaq (Gewinnschätzungen USA).

EBIT über 10 Jahre kommt aus Eulerpool (oder SEC). Fehlt es, gilt für 10-Jahres-Werte EBITDA als Ersatz,
Spalte `ebit_reihe` sagt, welche Reihe genommen wurde. Spalte `eulerpool` sagt, ob Eulerpool genutzt wurde.

Banken und Versicherer (Sektor „Finance“): EBIT, ROCE und Nettoverschuldung ergeben dort keinen Sinn → leer.

Aufruf: python3 -m pipeline.kennzahlen
"""

import json

import pandas as pd

from pipeline import DATEN

DATEI = DATEN / "kennzahlen.csv"

# Welche Quelle gilt je Posten? Die erste in der Liste, deren letztes Jahr höchstens 1 Jahr hinter dem neuesten
# Umsatzjahr liegt (sonst wäre z. B. EBIT der SEC von 2014 bei JNJ „aktuell“). Je Firma und Posten genau eine Quelle,
# keine Mischung über die Jahre. Neue Quelle = neue Zeile hier, der Rest des Codes bleibt gleich.
PRIORITAET = {
    "umsatz": [("tradingview", "total_revenue"), ("sec", "umsatz"), ("onvista", "bilanz.turnover")],
    "gewinn": [("tradingview", "net_income"), ("sec", "gewinn"), ("onvista", "bilanz.incomeAfterMi")],
    "ebitda": [("tradingview", "ebitda")],
    "ebit": [("eulerpool", "guv.ebit"), ("sec", "ebit"), ("onvista", "kennzahl.cnEbit")],
    "eigenkapital": [("onvista", "bilanz.shareholdersEquity"), ("sec", "eigenkapital")],
}
# Eulerpool-Schätzungen (bis ~2030) vor TradingView (nur nächstes Jahr): TradingView-Feld → Eulerpool-Feld
EP_SCHAETZUNG = {"revenue_forecast_next_fy": "revenueEstimate", "ebit_estimate_fy": "ebitEstimate",
                 "earnings_per_share_forecast_next_fy": "epsEstimate"}


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

    def reihe(posten):
        for quelle, name in PRIORITAET[posten]:
            if quelle == "eulerpool" and not ep_passt:
                continue
            r = jahresreihe(quelle, name)
            if len(r) and (letztes_jahr is None or r.index[-1] >= letztes_jahr - 1):
                return r, quelle
        return pd.Series(dtype=float), None

    def aktuell(posten):
        x = g[(g.quelle == "tradingview") & (g.periode == "aktuell") & (g.posten == posten)].wert.dropna()
        return x.iloc[0] if len(x) else None

    def teile(a, b):
        return a / b if a is not None and b not in (None, 0) else None

    text = g[g.posten.isin(["name", "sector", "industry"])].set_index("posten").text.to_dict()
    finanz = text.get("sector") == "Finance"
    letztes_jahr, ep_passt = None, False
    umsatz, q_umsatz = reihe("umsatz")
    letztes_jahr = int(umsatz.index[-1]) if len(umsatz) else None
    # Eulerpool rechnet in Berichtswährung (Qiagen USD), TradingView in Handelswährung (Qiagen EUR). Eulerpool nur
    # nutzen, wenn der Umsatz im letzten Geschäftsjahr auf 10 % gleich ist (gleiche Währung, gleiches Geschäftsjahr).
    ep_umsatz = jahresreihe("eulerpool", "guv.revenue")
    ep_passt = bool(letztes_jahr in ep_umsatz.index and umsatz.iloc[-1] > 0
                    and abs(ep_umsatz[letztes_jahr] / umsatz.iloc[-1] - 1) <= 0.10)

    def ep_schaetzung(feld, jahr):
        x = g[(g.quelle == "eulerpool") & (g.posten == f"schaetzung.{feld}") & (g.periode == f"{jahr}e")].wert.dropna()
        return x.iloc[0] if ep_passt and len(x) else None
    gewinn, _ = reihe("gewinn")
    ebitda, _ = reihe("ebitda")
    ebit, q_ebit = reihe("ebit")
    ebit_reihe, reihe10 = ("ebit", ebit) if len(ebit) >= 11 else ("ebitda", ebitda)

    # Eigenkapitalrendite: Gewinn des letzten Geschäftsjahrs / Eigenkapital am Jahresende (wie AlleAktien)
    ek, _ = reihe("eigenkapital")
    ek_rendite = None
    if letztes_jahr in ek.index and letztes_jahr in gewinn.index:
        ek_rendite = teile(gewinn[letztes_jahr], ek[letztes_jahr])

    # Gewinn je Aktie: letztes Ist-Jahr und Schätzung in 3 Jahren. Zuerst Eulerpool (Ist verwässert, stimmt bei 87 %
    # der Firmen auf 5 % mit dem bereinigten Wert von onvista), dann onvista (bereinigt), dann Nasdaq (nur USA).
    eps_3je = None
    eps_ep = jahresreihe("eulerpool", "guv.diluted_eps")
    if letztes_jahr in eps_ep.index and ep_schaetzung("epsEstimate", letztes_jahr + 3) is not None:
        a, b = eps_ep[letztes_jahr], ep_schaetzung("epsEstimate", letztes_jahr + 3)
        eps_3je = (b / a) ** (1 / 3) - 1 if a > 0 and b > 0 else None
    eps = g[(g.quelle == "onvista") & (g.posten == "kennzahl.cnEpsAdj")].set_index("periode").wert.dropna()
    if eps_3je is None and letztes_jahr and str(letztes_jahr) in eps.index and f"{letztes_jahr + 3}e" in eps.index:
        a, b = eps[str(letztes_jahr)], eps[f"{letztes_jahr + 3}e"]
        eps_3je = (b / a) ** (1 / 3) - 1 if a > 0 and b > 0 else None
    eps_tv = jahresreihe("tradingview", "earnings_per_share_diluted")
    # Ohne onvista (US-Firmen): Nasdaq-Schätzung in 3 Jahren gegen den Ist-Gewinn je Aktie (TradingView, verwässert).
    # Achtung: Nasdaq schätzt meist bereinigte Gewinne, der Ist-Wert ist nach US-GAAP → bei Sondereffekten schief.
    eps_nq = g[(g.quelle == "nasdaq") & (g.posten == "eps_schaetzung")].set_index("periode").wert.dropna()
    if eps_3je is None and letztes_jahr and f"{letztes_jahr + 3}e" in eps_nq.index and letztes_jahr in eps_tv.index:
        a, b = eps_tv[letztes_jahr], eps_nq[f"{letztes_jahr + 3}e"]
        eps_3je = (b / a) ** (1 / 3) - 1 if a > 0 and b > 0 else None

    def schaetzung(posten):
        """Schätzung für das nächste Geschäftsjahr: Eulerpool, sonst TradingView."""
        if letztes_jahr and posten in EP_SCHAETZUNG:
            w = ep_schaetzung(EP_SCHAETZUNG[posten], letztes_jahr + 1)
            if w is not None:
                return w
        x = g[(g.quelle == "tradingview") & (g.posten == posten) & g.periode.str.endswith("e")].wert.dropna()
        return x.iloc[0] if len(x) else None

    def schaetzreihe(posten):
        """Schätzungen für die Balken: bis 3 Jahre aus Eulerpool, sonst 1 Jahr aus TradingView."""
        if not letztes_jahr:
            return {}
        r = {f"{letztes_jahr + i}e": ep_schaetzung(EP_SCHAETZUNG[posten], letztes_jahr + i) for i in (1, 2, 3)}
        r = {j: w for j, w in r.items() if w is not None}
        w = schaetzung(posten)
        return r or ({f"{letztes_jahr + 1}e": w} if w else {})

    # ROCE und Verschuldung: Ergebnis des letzten Geschäftsjahrs zur Bilanz am selben Jahresende (wie AlleAktien,
    # geprüft gegen AAQS). Vorher EBIT der letzten 12 Monate zur Jahresbilanz → ROCE nur bei 39 % der Firmen gleich.
    # Nettoschulden = Schulden − Bargeld (ohne kurzfristige Geldanlagen). Fehlt die EBIT-Reihe: 12-Monats-Wert.
    ebit_letzt = ebit.get(letztes_jahr) if letztes_jahr else None
    ebit_gj = ebit_letzt if ebit_letzt is not None else aktuell("ebit_ttm")
    ebitda_gj = ebitda.get(letztes_jahr) if letztes_jahr in ebitda.index else aktuell("ebitda_ttm")
    netto_schulden = aktuell("net_debt_fy")
    if aktuell("total_debt_fy") is not None and aktuell("cash_n_equivalents_fy") is not None:
        netto_schulden = aktuell("total_debt_fy") - aktuell("cash_n_equivalents_fy")
    kapital = None
    if aktuell("total_assets_fy") is not None and aktuell("total_current_liabilities_fy") is not None:
        kapital = aktuell("total_assets_fy") - aktuell("total_current_liabilities_fy")
    dividende = aktuell("dividends_yield_current")

    gewinn10 = gewinn[gewinn.index > (letztes_jahr or 0) - 10]  # 10 Geschäftsjahre
    gewinn11 = gewinn[gewinn.index > (letztes_jahr or 0) - 11]  # 11 Jahre = 10 Veränderungen
    zeile = {
        "name": text.get("name"), "sektor": text.get("sector"), "branche": text.get("industry"),
        "finanzwert": finanz, "letztes_gj": letztes_jahr, "jahre_umsatz": len(umsatz),
        "waehrung": g[(g.periode == "aktuell") & (g.posten == "close")].waehrung.iloc[0]
        if (g.posten == "close").any() else None,
        "quelle_umsatz": q_umsatz, "quelle_ebit": q_ebit, "eulerpool": ep_passt,
        # Jahresreihen für die Balken (je Jahr; Schätzung nächstes Jahr mit „e“)
        "reihe_umsatz": {**{int(j): w for j, w in umsatz.iloc[-10:].items()},
                         **({} if finanz else schaetzreihe("revenue_forecast_next_fy"))},
        "reihe_ebit": {**{int(j): w for j, w in (ebit if len(ebit) else ebitda).iloc[-10:].items()},
                       **(schaetzreihe("ebit_estimate_fy") if len(ebit) else {})},
        "reihe_ebit_art": "EBIT" if len(ebit) else "EBITDA",
        # Kennzahlen
        "marktkap": aktuell("market_cap_basic"), "kurs": aktuell("close"),
        "kgv_ttm": aktuell("price_earnings_ttm"),
        "kgv_forward": teile(aktuell("close"), schaetzung("earnings_per_share_forecast_next_fy")),
        "kuv": aktuell("price_sales_current"), "kbv": aktuell("price_book_fq"),
        # Rentabilität
        "gewinnmarge": teile(aktuell("net_income_ttm"), aktuell("total_revenue_ttm")),
        "ek_rendite": ek_rendite,
        "roce": None if finanz else teile(ebit_gj, kapital),
        "fcf_rendite": teile(aktuell("free_cash_flow_ttm"), aktuell("market_cap_basic")),
        "dividendenrendite": dividende / 100 if dividende is not None else None,
        # Risiko
        "verschuldung_ebit": None if finanz else teile(netto_schulden, ebit_gj),
        "netto_schulden": netto_schulden, "ebit_gj": ebit_gj,
        "verschuldung_ebitda": None if finanz else teile(netto_schulden, ebitda_gj),
        "ebit_reihe": ebit_reihe,
        "max_rueckgang_ebit_10j": None if finanz else _max_rueckgang(reihe10.iloc[-11:]),
        "gewinnjahre_10j": int((gewinn10 > 0).sum()) if len(gewinn10) else None,
        "gewinnanstiege_10j": int((gewinn11.diff().iloc[1:] >= 0).sum()) if len(gewinn11) > 1 else None,
        # Wachstum
        "umsatz_wachstum_10j": _wachstum(umsatz, 10),
        "umsatz_wachstum_3j": _wachstum(umsatz, 3),
        # Banken/Versicherer: Umsatzschätzung anders abgegrenzt als der Ist-Umsatz (Allianz +31 %) → leer
        "umsatz_wachstum_1je": None if finanz else teile(schaetzung("revenue_forecast_next_fy"), umsatz.iloc[-1] if len(umsatz) else None),
        "ebit_wachstum_10j": None if finanz else _wachstum(reihe10, 10),
        "ebit_wachstum_3j": None if finanz else _wachstum(ebit, 3),
        "ebit_wachstum_1je": None if finanz else teile(schaetzung("ebit_estimate_fy"), ebit_letzt),
        "eps_wachstum_3je": eps_3je,
        "eps_wachstum_1je": teile(schaetzung("earnings_per_share_forecast_next_fy"),
                                  eps_tv.get(letztes_jahr) if letztes_jahr and eps_tv.get(letztes_jahr, 0) > 0 else None),
    }
    for name in ["umsatz_wachstum_1je", "ebit_wachstum_1je", "eps_wachstum_1je"]:
        if zeile[name] is not None:
            zeile[name] -= 1
    zeile.update(renditeerwartung(zeile, dividende))
    zeile["kategorie"] = kategorie(zeile, gewinn, reihe10.iloc[-11:])
    zeile.update(qualitaet(zeile))
    return zeile


# Renditeerwartung = erwartetes Gewinnwachstum je Aktie p. a. + Dividendenrendite. Wachstum aus den Schätzungen für
# 3 Jahre (onvista), sonst für 1 Jahr (TradingView). Gedeckelt auf 20 % p. a.: Nach einem schwachen Jahr ergibt
# die Schätzung sonst Fantasiewerte (Deutz +60 %, Rheinmetall +67 %), die sich nicht dauerhaft fortschreiben lassen.
DECKEL = 0.20


def renditeerwartung(z: dict, dividende) -> dict:
    wachstum = z["eps_wachstum_3je"] if z["eps_wachstum_3je"] is not None else z["eps_wachstum_1je"]
    if wachstum is None or dividende is None:
        return {"renditeerwartung": None, "renditeerwartung_gedeckelt": False}
    return {"renditeerwartung": min(wachstum, DECKEL) + dividende / 100, "renditeerwartung_gedeckelt": wachstum > DECKEL}


def kategorie(z: dict, gewinn: pd.Series, ergebnis10: pd.Series) -> str | None:
    """Einteilung nach Peter Lynch („One Up on Wall Street“), eigene Schwellen. Reihenfolge = Vorrang."""
    if gewinn.empty:
        return None
    letzte3 = gewinn.iloc[-3:]
    if gewinn.iloc[-1] <= 0 or (letzte3 <= 0).sum() >= 2:
        return "Turnaround"  # Verlust im letzten Jahr oder in 2 der letzten 3 Jahre
    vorjahr = ergebnis10.shift(1)
    einbrueche = ((vorjahr > 0) & (ergebnis10 <= vorjahr * 0.75)).sum()
    if not z["finanzwert"] and einbrueche >= 2:
        return "Zykliker"  # operatives Ergebnis in 10 Jahren mindestens zweimal um ≥ 25 % zum Vorjahr eingebrochen
        # (einmal reicht nicht: sonst wäre jede Firma mit Corona-Delle 2020 ein Zykliker)
    if z["kbv"] is not None and 0 < z["kbv"] < 0.8 and not z["finanzwert"]:
        return "Substanzwert"  # Börsenwert deutlich unter dem Buchwert (Lynch: „Asset Play“)
    wachstum = z["umsatz_wachstum_10j"] if z["umsatz_wachstum_10j"] is not None else z["umsatz_wachstum_3j"]
    if wachstum is None:
        return None
    if wachstum >= 0.12:
        return "Schnell wachsend"  # Lynch: „Fast Grower“
    if wachstum >= 0.05:
        return "Solide wachsend"  # Lynch: „Stalwart“
    return "Langsam wachsend"  # Lynch: „Slow Grower“


# Qualitätscheck: 10 Kriterien mit eigenen Schwellen. Nicht bewertbare (Daten fehlen, bei Banken/Versicherern
# EBIT-Kennzahlen) zählen weder als erfüllt noch als verfehlt; Ergebnis „erfüllt von bewertbar“.
KRITERIEN = [
    ("q_umsatz_10j", "Umsatz wächst über 10 Jahre um mindestens 5 % pro Jahr", "umsatz_wachstum_10j", lambda x: x >= 0.05),
    ("q_umsatz_3j", "Umsatz wächst über 3 Jahre um mindestens 5 % pro Jahr", "umsatz_wachstum_3j", lambda x: x >= 0.05),
    ("q_ebit_10j", "Operatives Ergebnis wächst über 10 Jahre um mindestens 5 % pro Jahr", "ebit_wachstum_10j",
     lambda x: x >= 0.05),
    ("q_eps", "Analysten erwarten mindestens 5 % mehr Gewinn je Aktie pro Jahr", "eps_wachstum", lambda x: x >= 0.05),
    ("q_schulden", "Nettoverschuldung höchstens 2 Jahres-EBIT", "verschuldung_ebit", lambda x: x <= 2),
    ("q_gewinnjahre", "Gewinn in mindestens 9 der letzten 10 Jahre", "gewinnjahre_10j", lambda x: x >= 9),
    ("q_rueckgang", "Operatives Ergebnis in 10 Jahren nie um mehr als 25 % eingebrochen", "max_rueckgang_ebit_10j",
     lambda x: x <= 0.25),
    ("q_ek_rendite", "Eigenkapitalrendite mindestens 15 %", "ek_rendite", lambda x: x >= 0.15),
    ("q_roce", "Rendite auf das eingesetzte Kapital (ROCE) mindestens 15 %", "roce", lambda x: x >= 0.15),
    ("q_marge", "Gewinnmarge mindestens 10 %", "gewinnmarge", lambda x: x >= 0.10),
]


def qualitaet(z: dict) -> dict:
    werte = {**z, "eps_wachstum": z["eps_wachstum_3je"] if z["eps_wachstum_3je"] is not None else z["eps_wachstum_1je"]}
    ergebnis = {}
    for schluessel, _, feld, regel in KRITERIEN:
        x = werte[feld]
        if feld == "verschuldung_ebit" and x is not None and z["ebit_gj"] is not None and z["ebit_gj"] <= 0:
            x = None if z["netto_schulden"] is None else (0 if z["netto_schulden"] <= 0 else 99)  # Verlust: nur ohne Schulden ok
        ergebnis[schluessel] = None if x is None or pd.isna(x) else bool(regel(x))
    bewertet = [v for v in ergebnis.values() if v is not None]
    ergebnis["q_erfuellt"], ergebnis["q_bewertbar"] = sum(bewertet), len(bewertet)
    return ergebnis


def berechnen() -> pd.DataFrame:
    d = pd.read_csv(DATEN / "fundamental.csv", dtype={"periode": str}, low_memory=False)
    d["text"] = d.wert
    d["wert"] = pd.to_numeric(d.wert, errors="coerce")
    ergebnis = pd.DataFrame([{"isin": isin, **firma(g)} for isin, g in d.groupby("isin")])
    ergebnis.assign(reihe_umsatz=ergebnis.reihe_umsatz.map(json.dumps),
                    reihe_ebit=ergebnis.reihe_ebit.map(json.dumps)).to_csv(DATEI, index=False)
    return ergebnis


if __name__ == "__main__":
    berechnen()
