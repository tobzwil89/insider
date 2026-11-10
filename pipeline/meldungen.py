"""Alle Meldungen in einer Tabelle: BaFin ab 22.10.2025 (laufend) und davor das EQS-Archiv.

Damit sich nichts doppelt, kommen aus dem EQS-Archiv nur Meldungen, die vor der ersten
BaFin-Meldung veröffentlicht wurden. Korrekturmeldungen ersetzen frühere Meldungen derselben
Person zum selben Geschäft (selten: 1 von rund 2.300).
"""

import pandas as pd

from pipeline import DATEN, bafin

EQS_DATEI = DATEN / "eqs_historie.csv"
SCHLUESSEL = ["isin", "person", "geschaeftsdatum", "art"]


def _eqs(bis: pd.Timestamp) -> pd.DataFrame:
    if not EQS_DATEI.exists():
        return pd.DataFrame()
    e = pd.read_csv(EQS_DATEI, dtype=str, keep_default_na=False)
    e["aktiviert"] = pd.to_datetime(e["aktiviert"], errors="coerce")
    e = e[e["aktiviert"] < bis].sort_values("aktiviert")
    korrigiert = e[e["korrektur"] == "True"]
    for _, k in korrigiert.iterrows():
        alt = (e[SCHLUESSEL] == k[SCHLUESSEL]).all(axis=1) & (e["aktiviert"] < k["aktiviert"])
        e = e[~alt]
    return e.drop_duplicates(["url"] + SCHLUESSEL + ["volumen"])


def lade_alle() -> pd.DataFrame:
    b = bafin.lade_meldungen().assign(quelle="bafin")
    e = _eqs(b["mitteilungsdatum"].min())
    if not e.empty:
        for spalte in ["preis", "volumen"]:
            e[spalte] = pd.to_numeric(e[spalte], errors="coerce")
        for spalte in ["mitteilungsdatum", "geschaeftsdatum"]:
            e[spalte] = pd.to_datetime(e[spalte], errors="coerce")
    alle = pd.concat([b, e], ignore_index=True).fillna({"bezug_person": "", "bezug_position": ""})
    return _doppelte_entfernen(alle)


GESCHAEFT = ["isin", "person", "geschaeftsdatum", "art", "instrument", "preis", "volumen"]


def _doppelte_entfernen(m: pd.DataFrame) -> pd.DataFrame:
    """Dasselbe Geschäft in mehreren Mitteilungen (meist EQS-Berichtigung, die eqs.py nicht als Korrektur erkennt):
    Zeilen der letzten Mitteilung behalten (richtige Angaben), Mitteilungsdatum der ersten setzen (ab da öffentlich,
    wichtig für t = 0). Gleiche Zeilen innerhalb einer Mitteilung bleiben (Teilausführungen).
    Prüfung und Gründe: .recherche/strukturbruch.md Abschnitt 4."""
    m = m.sort_values("aktiviert", kind="stable").reset_index(drop=True)
    mitteilung = m["url"].where(m["quelle"] == "eqs",
                                m["bafin_id"].astype(str) + "|" + m["mitteilungsdatum"].astype(str))
    gruppe = m.assign(_m=mitteilung).groupby(GESCHAEFT, dropna=False)
    letzte = gruppe["_m"].transform("last")
    erste = gruppe["mitteilungsdatum"].transform("min")
    # Nur mit bezifferten Werten: Ohne Volumen sehen verschiedene Geschäfte gleich aus (Zalando 14.03.2023: 18 Optionsgeschäfte
    # „nicht bezifferbar“); dann lieber einen Doppelten stehen lassen als ein echtes Geschäft löschen.
    beziffert = pd.to_numeric(m["volumen"], errors="coerce").fillna(0) > 0
    return m.assign(mitteilungsdatum=erste.where(beziffert, m["mitteilungsdatum"]))[
        (mitteilung == letzte) | ~beziffert].reset_index(drop=True)
