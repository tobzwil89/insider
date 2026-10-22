"""Timing der Insider: Wie liefen die Aktien in den 3 Monaten nach ihren Käufen?

Je Kauf: Überrendite = Rendite der Aktie minus Rendite des Index (DAX bzw. MDAX) über 60
Handelstage, gemessen ab dem Schlusskurs des Geschäftstags. Mehrere Käufe derselben Person am
selben Tag zählen als einer. Käufe eng verbundener Personen (z. B. Holdings) zählen für die
Führungskraft, wenn die Meldung sie nennt (EQS-Meldungen). Ins Ranking kommt, wer mindestens
3 Käufe mit vollständigen 60 Handelstagen hat. Sortiert wird nach dem Median (dem typischen
Kauf), damit ein einzelner Glückstreffer nicht das Ranking bestimmt. Verkäufe zählen nicht: Sie haben oft private
Gründe (Steuern, Diversifikation) und sagen wenig über Insiderwissen.
"""

import re

import pandas as pd

TAGE = 60
MIN_KAEUFE = 3
# Titel nur mit Punkt entfernen, damit Namen wie "Pol" oder "Drescher" erhalten bleiben
TITEL = re.compile(r"\b(Professor\b|Prof\.|Dr\.(-Ing\.)?|Dipl\.-?[A-Za-z.]*|h\.\s?c\.|rer\.|nat\.|pol\.|oec\.|med\.|jur\.|phil\.|Mag\.|MBA\b)")


def _schluessel(name: str) -> str:
    """'Georgi, Professor Dr. Andreas Arthur' und 'Georgi, Dr. Andreas Arthur' → gleicher Schlüssel."""
    return re.sub(r"\s+", " ", TITEL.sub("", name)).strip(" ,").lower()


def kaeufe_mit_rendite(meldungen: pd.DataFrame, firmen: pd.DataFrame, kurse: pd.DataFrame) -> pd.DataFrame:
    mit_ticker = firmen[firmen["ticker"] != ""][["isin", "ticker", "name", "benchmark"]]
    k = meldungen[meldungen["instrument"].eq("Aktie") & meldungen["art"].eq("Kauf")].merge(mit_ticker, on="isin")
    eng = k["position"].eq("in enger Beziehung")
    k.loc[eng, "person"] = k.loc[eng, "bezug_person"]
    k.loc[eng, "position"] = k.loc[eng, "bezug_position"]
    k = k[k["person"].ne("") & k["position"].isin(["Vorstand", "Aufsichtsrat", "Sonstige Führungsperson"])]
    k = k.assign(schluessel=k["person"].map(_schluessel))
    k = (k.groupby(["schluessel", "ticker", "geschaeftsdatum"])
         .agg(person=("person", "last"), position=("position", "last"), name=("name", "first"),
              benchmark=("benchmark", "first"), volumen=("volumen", "sum"))
         .reset_index())

    renditen = []
    for z in k.itertuples():
        if z.ticker not in kurse or z.benchmark not in kurse:
            renditen.append(None)
            continue
        paar = kurse[[z.ticker, z.benchmark]].dropna()
        t0 = paar.index.searchsorted(z.geschaeftsdatum)
        if t0 + TAGE >= len(paar):
            renditen.append(None)  # noch keine 60 Handelstage seit dem Kauf
            continue
        start, ende = paar.iloc[t0], paar.iloc[t0 + TAGE]
        renditen.append((ende[z.ticker] / start[z.ticker] - 1) - (ende[z.benchmark] / start[z.benchmark] - 1))
    return k.assign(ueberrendite=renditen).dropna(subset=["ueberrendite"])


def ranking(kaeufe: pd.DataFrame) -> pd.DataFrame:
    """Eine Zeile je Person und Firma, sortiert nach der typischen (Median-)Überrendite."""
    g = kaeufe.sort_values("geschaeftsdatum").groupby(["schluessel", "ticker"])
    r = g.agg(person=("person", "last"), position=("position", "last"), name=("name", "first"),
              kaeufe=("ueberrendite", "size"), ueberrendite=("ueberrendite", "mean"),
              median=("ueberrendite", "median"), trefferquote=("ueberrendite", lambda x: (x > 0).mean()),
              volumen=("volumen", "sum"), erster_kauf=("geschaeftsdatum", "min"),
              letzter_kauf=("geschaeftsdatum", "max")).reset_index()
    return (r[r["kaeufe"] >= MIN_KAEUFE].sort_values(["median", "ueberrendite"], ascending=False, ignore_index=True)
            .drop(columns="schluessel"))
