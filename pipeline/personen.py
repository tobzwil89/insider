"""Personenseiten: alle Geschäfte eines Vorstands- oder Aufsichtsratsmitglieds über alle Firmen im DAX und MDAX.

Eine Person = gleicher Name ohne Titel und Akzente (ranking.schluessel). Wer bei mehreren Firmen meldet
(Aufsichtsratsmandate, Wechsel), steht auf einer Seite. Geprüft 06.11.2026: alle 42 Namen mit mehreren Firmen sind
echte Mehrfachmandate (Kaeser, Busch, Höttges …).

Auf die Seite kommen die eigenen Geschäfte und die Geschäfte eigener Gesellschaften (Holding, GmbH & Co. KG,
Stiftung), wenn die Meldung die Führungskraft nennt (EQS: „in enger Beziehung zu“). Die BaFin nennt sie nicht; dort
gilt die Zuordnung derselben Gesellschaft aus früheren EQS-Meldungen. Ohne Gesellschaften fehlten Plattner,
Dommermuth, Povlsen, Merckle. Bewusst NICHT: Angehörige (natürliche Personen „in enger Beziehung“) und sonstige
Führungspersonen, bis der Datenschutz geklärt ist (dauerhafte Profile über Privatpersonen, DSGVO). Ebenso nicht:
börsennotierte Konzerne als „eng verbunden“ (United Internet AG bei Dommermuth), deren Käufe sind keine Privatsache.

Überrendite seit dem Geschäft: Rendite der Aktie minus Rendite des Index (DAX bzw. MDAX) vom Schlusskurs des
Geschäftstags bis zum letzten Schlusskurs, wie die Spalte bei Quiver Quantitative.
"""

import re
import unicodedata

import pandas as pd

from pipeline.ranking import FALTEN, ohne_titel, schluessel

POSITIONEN = {"Vorstand", "Aufsichtsrat"}
GESELLSCHAFT = re.compile(
    r"GmbH|mbH|\bAG\b|Aktiengesellschaft|\bSE\b|\bKG\b|KGaA|\bUG\b|S\.?\s?à\.?\s?r\.?\s?l|\bS\.?A\.?\b|\bLtd|Limited|LLC|"
    r"\bL\.?P\.?\b|\bInc\b|B\.V\.|N\.V\.|\bApS\b|A/S|Aktieselskab|Stiftung|Foundation|Trust|Holding|Beteiligung|"
    r"Verwaltung|\bPte\b|\bGbR\b|\bOHG\b|e\.\s?V\.|\bPty\b|Fonds|Fund|Partners|Capital|Invest|Company|Corporation|"
    r"S\.r\.l|S\.p\.A|\bAB\b|\bBV\b|\bNV\b", re.I)
ANREDE = re.compile(r"\b(Herr|Frau)\s+")
RECHTSFORM = re.compile(r"[\s,]+(AG|SE|Aktiengesellschaft|KGaA|SE & Co\. KGaA|N\.V\.|S\.A\.)$", re.I)


def _konzern(name: str) -> str:
    """'Continental Aktiengesellschaft' und 'Continental AG' → 'continental'."""
    return RECHTSFORM.sub("", str(name).strip()).lower()


def anzeigename(name: str) -> str:
    """'Busch, Dr. Roland' → 'Dr. Roland Busch' (Anrede weg, Titel bleibt)."""
    nachname, _, vorname = name.partition(",")
    return re.sub(r"\s+", " ", f"{ANREDE.sub('', vorname)} {nachname}").strip()


def adresse(name: str) -> str:
    """'Östberg, Dr. Niklas' → 'niklas-ostberg' (Vorname-Nachname ohne Titel, nur a–z, 0–9 und Bindestrich)."""
    nachname, _, vorname = ohne_titel(name).partition(",")
    text = unicodedata.normalize("NFKD", f"{vorname} {nachname}".translate(FALTEN)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def zuordnen(meldungen: pd.DataFrame, firmen: pd.DataFrame) -> pd.DataFrame:
    """Meldungen der DAX/MDAX-Firmen, die zu einer Personenseite gehören, mit Spalten
    traeger (Name der Führungskraft), traeger_position (Vorstand/Aufsichtsrat), ueber (Gesellschaft oder leer)."""
    mit_seite = firmen[firmen["ticker"] != ""]
    m = meldungen[meldungen["isin"].isin(mit_seite["isin"])]
    eigene = m[m["position"].isin(POSITIONEN)].assign(traeger=lambda d: d["person"],
                                                       traeger_position=lambda d: d["position"], ueber="")
    # börsennotierte Konzerne (genau unsere Firmen, ohne Rechtsform), nicht Familienholdings wie „RUDOLF FUCHS SE & Co KG“
    konzerne = {_konzern(n) for n in set(mit_seite["name"]) | set(m["emittent"].dropna())}
    eng = m[m["position"].eq("in enger Beziehung") & m["person"].str.contains(GESELLSCHAFT)
            & ~m["person"].map(_konzern).isin(konzerne)].copy()
    bekannt = (eng[eng["bezug_person"].ne("")].sort_values("aktiviert")
               .groupby(["isin", "person"])[["bezug_person", "bezug_position"]].last())
    fehlt = eng["bezug_person"].eq("")
    for spalte in ["bezug_person", "bezug_position"]:
        eng.loc[fehlt, spalte] = [bekannt[spalte].get((i, p), "") for i, p in zip(eng.loc[fehlt, "isin"],
                                                                                   eng.loc[fehlt, "person"])]
    eng = eng[eng["bezug_position"].isin(POSITIONEN)]
    eng = eng.assign(traeger=eng["bezug_person"], traeger_position=eng["bezug_position"], ueber=eng["person"])
    return pd.concat([eigene, eng], ignore_index=True)


def ueberrendite_seit(kurse: pd.DataFrame, ticker: str, benchmark: str, tag) -> float | None:
    if ticker not in kurse or benchmark not in kurse or pd.isna(tag):
        return None
    paar = kurse[[ticker, benchmark]].dropna()
    t0 = paar.index.searchsorted(tag)
    if t0 >= len(paar) - 1:
        return None  # noch kein Kurstag nach dem Geschäft
    start, ende = paar.iloc[t0], paar.iloc[-1]
    return (ende[ticker] / start[ticker] - 1) - (ende[benchmark] / start[benchmark] - 1)


def personen(zusammen: pd.DataFrame, firmen: pd.DataFrame, kurse: pd.DataFrame, rangliste: pd.DataFrame) -> list:
    """zusammen: zuordnen(…) mit Teilausführungen zusammengefasst (export.meldungen_zusammenfassen mit den Spalten
    traeger, traeger_position, ueber). Gibt je Person ein dict für seiten.personenseite zurück, neuestes Geschäft zuerst."""
    if zusammen.empty:
        return []
    mit_seite = firmen[firmen["ticker"] != ""].drop_duplicates("isin").set_index("isin")
    m = zusammen.copy()
    m["ticker"] = m["isin"].map(mit_seite["ticker"])
    m["firma"] = m["isin"].map(mit_seite["name"])
    m["schluessel"] = m["traeger"].map(schluessel)
    m["seit"] = [ueberrendite_seit(kurse, r.ticker, mit_seite.at[r.isin, "benchmark"], r.geschaeftsdatum)
                 if r.instrument == "Aktie" and r.art in ("Kauf", "Verkauf") else None
                 for r in m.itertuples()]
    rang = rangliste.assign(rang=range(1, len(rangliste) + 1), schluessel=rangliste["person"].map(schluessel))

    # Name laut neuester eigener Meldung (sonst laut Gesellschaftsmeldung); gleiche Adresse → -2, -3 …
    namen = (m.assign(eigen=m["ueber"].eq("")).sort_values(["eigen", "aktiviert"])
             .groupby("schluessel")["traeger"].last())
    vergeben, adressen = {}, {}
    for k, name in namen.sort_index().items():
        a = adresse(name) or "person"
        vergeben[a] = vergeben.get(a, 0) + 1
        adressen[k] = a if vergeben[a] == 1 else f"{a}-{vergeben[a]}"

    liste = []
    for k, g in m.groupby("schluessel"):
        g = g.sort_values(["mitteilungsdatum", "aktiviert"], ascending=False)
        mandate = (g.groupby(["ticker", "traeger_position"])
                   .agg(firma=("firma", "first"), meldungen=("person", "size"),
                        von=("geschaeftsdatum", "min"), bis=("geschaeftsdatum", "max"))
                   .reset_index().rename(columns={"traeger_position": "position"}).sort_values("bis", ascending=False))
        liste.append({"schluessel": k, "name": anzeigename(namen[k]), "adresse": adressen[k],
                      "geschaefte": g, "mandate": mandate, "ranking": rang[rang["schluessel"] == k],
                      "letztes": g["geschaeftsdatum"].max()})
    return sorted(liste, key=lambda p: p["letztes"], reverse=True)
