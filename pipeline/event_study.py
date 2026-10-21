"""Event Study nach der Methode der Bachelorarbeit, mit Marktmodell auf Handelstagen.

Ereignis: alle Käufe bzw. alle Verkäufe von Aktien durch Vorstand oder Aufsichtsrat einer
Firma, die am selben Tag mitgeteilt wurden. Teilausführungen und mehrere Personen am selben
Tag sind also ein Ereignis, sonst würde dieselbe Kursreaktion mehrfach gezählt.
t = 0 ist der erste Handelstag am oder nach dem Mitteilungsdatum.

Marktmodell: R_i = α + β · R_Index (DAX oder MDAX), geschätzt per OLS im Schätzfenster.
Abnormale Rendite: AR = R_i − (α + β · R_Index), Renditen logarithmiert.
"""

import numpy as np
import pandas as pd
from scipy import stats

EREIGNISFENSTER = (-5, 5)      # Handelstage um t = 0
SCHAETZFENSTER = (-130, -11)   # 120 Handelstage, endet 10 Tage vor dem Ereignis
MIN_SCHAETZTAGE = 100
POSITIONEN = {"Vorstand", "Aufsichtsrat"}
RICHTUNGEN = {"Kauf", "Verkauf"}


def ereignisse(meldungen: pd.DataFrame, firmen: pd.DataFrame) -> pd.DataFrame:
    """Meldungen zu Ereignissen zusammenfassen (Firma, Mitteilungstag, Richtung)."""
    mit_ticker = firmen[firmen["ticker"] != ""]
    m = meldungen[meldungen["instrument"].eq("Aktie") & meldungen["art"].isin(RICHTUNGEN)
                  & meldungen["position"].isin(POSITIONEN) & meldungen["isin"].isin(mit_ticker["isin"])]
    m = m.merge(mit_ticker[["isin", "name", "ticker", "benchmark", "index"]], on="isin")
    e = (m.groupby(["ticker", "mitteilungsdatum", "art"])
         .agg(name=("name", "first"), isin=("isin", "first"), benchmark=("benchmark", "first"),
              index=("index", "first"), volumen=("volumen", "sum"), meldungen=("person", "size"),
              personen=("person", lambda p: sorted(set(p))))
         .reset_index().sort_values("mitteilungsdatum", ignore_index=True))
    e["id"] = e["ticker"] + "_" + e["mitteilungsdatum"].dt.strftime("%Y%m%d") + "_" + e["art"].str[0]
    return e


def abnormale_renditen(ereignisse: pd.DataFrame, kurse: pd.DataFrame) -> pd.DataFrame:
    """Eine Zeile je Ereignis und Tag t im Ereignisfenster. Ereignisse ohne genug Daten fehlen."""
    renditen = np.log(kurse / kurse.shift(1))
    zeilen = []
    for e in ereignisse.itertuples():
        if e.ticker not in renditen or e.benchmark not in renditen:
            continue
        r = renditen[[e.ticker, e.benchmark]].dropna()
        t0 = r.index.searchsorted(e.mitteilungsdatum)
        if t0 >= len(r):
            continue  # noch kein Handelstag seit der Mitteilung
        a, b = SCHAETZFENSTER
        schaetz = r.iloc[max(t0 + a, 0): max(t0 + b + 1, 0)]
        if len(schaetz) < MIN_SCHAETZTAGE:
            continue
        beta, alpha, *_ = stats.linregress(schaetz[e.benchmark], schaetz[e.ticker])
        start, ende = EREIGNISFENSTER
        for t in range(start, ende + 1):
            if 0 <= t0 + t < len(r):
                tag = r.iloc[t0 + t]
                zeilen.append({"id": e.id, "art": e.art, "t": t, "datum": r.index[t0 + t],
                               "ar": tag[e.ticker] - (alpha + beta * tag[e.benchmark])})
    return pd.DataFrame(zeilen, columns=["id", "art", "t", "datum", "ar"])


def zusammenfassung(ar: pd.DataFrame) -> pd.DataFrame:
    """AAR, t-Test gegen null und CAAR je Richtung und Tag t, wie in der Arbeit."""
    teile = []
    for art, gruppe in ar.groupby("art"):
        s = gruppe.groupby("t")["ar"].agg(aar="mean", n="size")
        test = gruppe.groupby("t")["ar"].apply(lambda x: stats.ttest_1samp(x, 0))
        s["t_stat"] = [x.statistic for x in test]
        s["p_wert"] = [x.pvalue for x in test]
        s["caar"] = s["aar"].cumsum()
        s["art"] = art
        teile.append(s.reset_index())
    return pd.concat(teile, ignore_index=True) if teile else pd.DataFrame()


def car_je_ereignis(ar: pd.DataFrame) -> pd.DataFrame:
    """Kumulierte abnormale Rendite je Ereignis: gesamt und ab t = 0."""
    return ar.groupby("id").apply(lambda g: pd.Series({
        "car": g["ar"].sum(), "car_ab_0": g.loc[g["t"] >= 0, "ar"].sum(),
        "tage_nach": int(g["t"].max())}), include_groups=False).reset_index()
