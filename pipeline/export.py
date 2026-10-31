"""Schreibt die Ergebnisse als JSON nach docs/data/ für die statische Website.

    stand.json            Zeitpunkt der Berechnung, Kennzahlen, Methodenparameter
    neueste.json          die letzten Meldungen aller Emittenten (Teilausführungen zusammengefasst)
    cluster.json          erkannte Cluster-Käufe
    caar.json             AAR/CAAR-Kurven für Käufe und Verkäufe
    ereignisse.json       alle ausgewerteten Ereignisse mit CAR
    firmen.json           Übersicht der Firmen mit eigener Seite
    ranking.json          Insider mit dem besten Timing (Überrendite 3 Monate nach Käufen)
    kurse/<TICKER>.json   je Firma: Schlusskurse als [Datum, Kurs] für das Diagramm

Außerdem (pipeline/seiten.py): docs/firma/<TICKER>/index.html als fertige Seite je Firma (mit Großaktionären
aus daten/stimmrechte.csv),
docs/sitemap.xml und Versionsnummern (?v=) für CSS/JS.
"""

import json
import math
import shutil

import numpy as np
import pandas as pd

from pipeline import AUSGABE, DATEN, event_study as es, cluster as cl, gurus, ranking as rk, rueckkaeufe, seiten, stimmrechte

NEUESTE = 300        # so viele Meldungen im Live-Ticker
KURS_JAHRE = 10      # so weit reicht der Kursverlauf auf den Firmenseiten (ab Beginn der Historie)


def _sauber(x):
    """Macht pandas/numpy-Werte JSON-tauglich (NaN → null, Datum → Text)."""
    if isinstance(x, dict):
        return {k: _sauber(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, np.ndarray)):
        return [_sauber(v) for v in x]
    if isinstance(x, pd.Timestamp):
        return None if pd.isna(x) else (x.strftime("%Y-%m-%d") if x == x.normalize()
                                        else x.strftime("%Y-%m-%d %H:%M:%S"))
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return None if math.isnan(x) else round(float(x), 6)
    if x is pd.NaT:
        return None
    return x


def _schreibe(name: str, inhalt) -> None:
    pfad = AUSGABE / name
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(json.dumps(_sauber(inhalt), ensure_ascii=False, separators=(",", ":")),
                    encoding="utf-8")


def _zeilen(df: pd.DataFrame) -> list:
    return df.to_dict(orient="records")


def meldungen_zusammenfassen(m: pd.DataFrame) -> pd.DataFrame:
    """Teilausführungen derselben Person am selben Mitteilungstag zu einer Zeile zusammenfassen."""
    m = m.assign(stueck=m["volumen"] / m["preis"])
    g = (m.groupby(["isin", "person", "art", "instrument", "mitteilungsdatum"], dropna=False)
         .agg(emittent=("emittent", "first"), position=("position", "first"),
              waehrung=("waehrung", "first"), volumen=("volumen", "sum"), stueck=("stueck", "sum"),
              geschaeftsdatum=("geschaeftsdatum", "min"), aktiviert=("aktiviert", "max"),
              teilausfuehrungen=("person", "size"))
         .reset_index())
    # Durchschnittspreis gewichtet nach Stückzahl; ohne Preisangabe bleiben Preis und Volumen leer
    g["preis"] = (g["volumen"] / g["stueck"]).where(g["stueck"] > 0)
    g["volumen"] = g["volumen"].where(g["stueck"] > 0)
    return g.drop(columns="stueck").sort_values("aktiviert", ascending=False, ignore_index=True)


def exportiere(meldungen: pd.DataFrame, firmen: pd.DataFrame, kurse: pd.DataFrame,
               ereignisse: pd.DataFrame, ar: pd.DataFrame, cluster: pd.DataFrame,
               rangliste: pd.DataFrame) -> None:
    mit_seite = firmen[firmen["ticker"] != ""]
    isin_zu_ticker = dict(zip(mit_seite["isin"], mit_seite["ticker"]))
    zusammen = meldungen_zusammenfassen(meldungen)
    zusammen["ticker"] = zusammen["isin"].map(isin_zu_ticker)

    caar = es.zusammenfassung(ar)
    car = es.car_je_ereignis(ar) if not ar.empty else pd.DataFrame(columns=["id", "car", "car_ab_0", "tage_nach"])
    ausgewertet = ereignisse.merge(car, on="id")

    _schreibe("stand.json", {
        "berechnet": pd.Timestamp.now(tz="Europe/Berlin").strftime("%Y-%m-%d %H:%M:%S"),
        "letzte_meldung": meldungen["aktiviert"].max(),
        "meldungen_seit": meldungen["mitteilungsdatum"].min(),
        "anzahl_meldungen": len(meldungen), "anzahl_ereignisse": len(ausgewertet),
        "letzter_kurstag": kurse.index.max(),
        "methode": {"modell": "Marktmodell (DAX bzw. MDAX)", "ereignisfenster": es.EREIGNISFENSTER,
                    "schaetzfenster": es.SCHAETZFENSTER, "min_schaetztage": es.MIN_SCHAETZTAGE,
                    "positionen": sorted(es.POSITIONEN), "cluster_tage": cl.FENSTER_TAGE,
                    "cluster_personen": cl.MIN_PERSONEN, "cluster_volumen": cl.MIN_VOLUMEN,
                    "ranking_tage": rk.TAGE, "ranking_min_kaeufe": rk.MIN_KAEUFE},
    })
    _schreibe("neueste.json", _zeilen(zusammen.head(NEUESTE)))
    _schreibe("cluster.json", _zeilen(cluster.assign(ticker=cluster["isin"].map(isin_zu_ticker))))
    _schreibe("caar.json", {art: _zeilen(teil.drop(columns="art"))
                            for art, teil in caar.groupby("art")} if not caar.empty else {})
    _schreibe("ranking.json", _zeilen(rangliste))
    # Nicht mehr genutzte Dateien früherer Versionen entfernen
    (AUSGABE / "ereignisse.json").unlink(missing_ok=True)
    shutil.rmtree(AUSGABE / "firmen", ignore_errors=True)

    v = seiten.versionen()
    seiten.versionen_eintragen(v)
    rang = rangliste.assign(rang=range(1, len(rangliste) + 1))
    kurs_start = kurse.index.max() - pd.DateOffset(years=KURS_JAHRE)
    aktionaere = stimmrechte.grossaktionaere(pd.read_csv(DATEN / "stimmrechte.csv"),
                                             pd.read_csv(DATEN / "grossaktionaere_geprueft.csv"))
    # Rückkäufe nur für Firmen, deren Historie fertig geladen ist (sonst hieße „keine“ nur „noch nicht geladen“)
    rk_datei, rk_fertig = DATEN / "rueckkaeufe.csv", DATEN / "rueckkaeufe_fortschritt.csv"
    rueck = rueckkaeufe.jahre(pd.read_csv(rk_datei)) if rk_datei.exists() else pd.DataFrame(columns=["firma"])
    rk_fortschritt = pd.read_csv(rk_fertig) if rk_fertig.exists() else pd.DataFrame(columns=["name", "meldungen"])
    rk_geladen = set(rk_fortschritt["name"])
    # Firmen, für die EQS gar keine Meldungen dieser Kategorie führt (z. B. BMW, anderer Verteiler):
    # dort heißt „nichts gefunden“ nur „keine Daten“, nicht „keine Rückkäufe“
    rk_ohne = set(rk_fortschritt.loc[rk_fortschritt["meldungen"].eq(0), "name"]) - set(rueck["firma"])
    uebersicht = []
    for ticker, f in mit_seite.groupby("ticker"):
        eigene = zusammen[zusammen["ticker"] == ticker]
        verlauf = kurse[ticker].dropna() if ticker in kurse else pd.Series(dtype=float)
        verlauf = verlauf[verlauf.index >= kurs_start]
        _schreibe(f"kurse/{ticker}.json", [[d, round(float(p), 2)] for d, p in verlauf.items()])
        stamm = {"ticker": ticker, "name": f["name"].iloc[0], "index": f["index"].iloc[0],
                 "benchmark": f["benchmark"].iloc[0], "isins": list(f["isin"])}
        letzter = (verlauf.index[-1], verlauf.iloc[-1]) if len(verlauf) else None
        seiten.schreiben(seiten.DOCS / "firma" / ticker / "index.html", seiten.firmenseite(
            stamm, eigene, ausgewertet[ausgewertet["ticker"] == ticker], rang[rang["ticker"] == ticker], letzter, v,
            aktionaere[aktionaere["firma"] == stamm["name"]],
            rueck[rueck["firma"] == stamm["name"]] if stamm["name"] in rk_geladen else None,
            rueck_ohne_meldungen=stamm["name"] in rk_ohne))
        uebersicht.append({"ticker": ticker, "name": stamm["name"], "index": stamm["index"],
                           "meldungen": len(eigene),
                           "letzte_meldung": eigene["mitteilungsdatum"].max() if len(eigene) else None})
    _schreibe("firmen.json", sorted(uebersicht, key=lambda x: x["name"].lower()))
    # Seiten von Firmen entfernen, die nicht mehr im Index sind
    for ordner in (seiten.DOCS / "firma").iterdir():
        if ordner.name not in set(mit_seite["ticker"]):
            shutil.rmtree(ordner)
    depots = gurus.alle_depots()
    for d in depots:
        seiten.schreiben(seiten.DOCS / "gurus" / seiten.kurzname(d["name"]) / "index.html", seiten.guruseite(d, v))
    if depots:
        seiten.schreiben(seiten.DOCS / "gurus" / "index.html", seiten.gurus_uebersicht(depots, v))
    guru_adressen = ["gurus/"] + [f"gurus/{seiten.kurzname(d['name'])}/" for d in depots] if depots else []
    (seiten.DOCS / "sitemap.xml").write_text(seiten.sitemap(sorted(mit_seite["ticker"].unique()), guru_adressen),
                                             encoding="utf-8")
