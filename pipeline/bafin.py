"""Directors' Dealings aus der BaFin-Datenbank holen und in daten/meldungen.csv sammeln.

Die BaFin zeigt nur die letzten 12 Monate. Deshalb wird meldungen.csv nur ergänzt, nie
überschrieben: Was einmal gesehen wurde, bleibt, auch wenn es bei der BaFin herausfällt.
Eine Zeile entspricht einer Zeile der BaFin (also auch einzelnen Teilausführungen).
"""

import io
import time
from datetime import date, timedelta

import pandas as pd
import requests

from pipeline import DATEN, HEADER

URL = "https://portal.mvp.bafin.de/database/DealingsInfo/sucheForm.do"
DATEI = DATEN / "meldungen.csv"
SPALTEN = {
    "Emittent": "emittent", "Bafin-ID": "bafin_id", "ISIN": "isin", "Meldepflichtiger": "person",
    "Position / Status": "position", "Art des Instruments": "instrument", "Art des Geschäfts": "art",
    "Durchschnittspreis": "preis_text", "Aggregiertes Volumen": "volumen_text",
    "Mitteilungsdatum": "mitteilungsdatum", "Datum des Geschäfts": "geschaeftsdatum",
    "Ort des Geschäfts": "ort", "Datum der Aktivierung": "aktiviert",
}
# Diese Felder zusammen kennzeichnen eine BaFin-Zeile eindeutig
SCHLUESSEL = ["bafin_id", "isin", "person", "art", "preis_text", "volumen_text",
              "geschaeftsdatum", "ort", "aktiviert"]


def abrufen(versuche: int = 3) -> pd.DataFrame:
    """Alle Meldungen, die die BaFin aktuell anzeigt (rollierend 12 Monate)."""
    heute = date.today()
    params = {"zeitraum": 4, "zeitraumVon": (heute - timedelta(days=400)).strftime("%d.%m.%Y"),
              "zeitraumBis": heute.strftime("%d.%m.%Y"), "emittentName": "", "emittentIsin": "",
              "meldepflichtigerName": "", "emittentButton": "Suche Emittent",
              "d-4000784-e": 1, "6578706f7274": 1}  # Export als CSV
    for versuch in range(1, versuche + 1):
        try:
            antwort = requests.get(URL, params=params, headers=HEADER, timeout=120)
            antwort.raise_for_status()
            text = antwort.content.decode("utf-8-sig")
            if not text.startswith("Emittent;"):
                raise ValueError(f"Antwort ist keine CSV: {text[:80]!r}")
            roh = pd.read_csv(io.StringIO(text), sep=";", dtype=str, keep_default_na=False)
            return roh.rename(columns=SPALTEN)[list(SPALTEN.values())]
        except Exception as fehler:
            if versuch == versuche:
                raise RuntimeError(f"BaFin nicht abrufbar: {fehler}") from fehler
            time.sleep(20 * versuch)


def _betrag(text: pd.Series) -> tuple:
    """'1.234,50 EUR' → (1234.5, 'EUR'). Fehlt die Währung, bleibt sie leer."""
    teile = text.str.strip().str.rsplit(" ", n=1, expand=True).reindex(columns=[0, 1])
    ohne_waehrung = teile[1].fillna("").str.contains(r"\d")
    zahl = teile[0].where(~ohne_waehrung, text.str.strip())
    waehrung = teile[1].where(~ohne_waehrung, "").fillna("")
    wert = pd.to_numeric(zahl.str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
                         errors="coerce")
    return wert, waehrung


def aufbereiten(roh: pd.DataFrame) -> pd.DataFrame:
    """Zahlen und Datumsangaben lesbar machen; Originaltexte bleiben für den Schlüssel erhalten."""
    m = roh.copy()
    m["preis"], m["waehrung"] = _betrag(m["preis_text"])
    m["volumen"], _ = _betrag(m["volumen_text"])
    for spalte in ["mitteilungsdatum", "geschaeftsdatum"]:
        m[spalte] = pd.to_datetime(m[spalte], format="%d.%m.%Y", errors="coerce").dt.strftime("%Y-%m-%d")
    m["aktiviert"] = pd.to_datetime(m["aktiviert"], format="%d.%m.%Y %H:%M:%S",
                                    errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")
    return m


def aktualisieren() -> pd.DataFrame:
    """Holt die BaFin-Liste, hängt Unbekanntes an meldungen.csv an und gibt nur die neuen Zeilen zurück."""
    aktuell = aufbereiten(abrufen())
    if DATEI.exists():
        bekannt = pd.read_csv(DATEI, dtype=str, keep_default_na=False)
        schon_da = set(map(tuple, bekannt[SCHLUESSEL].to_numpy()))
        neu = aktuell[[tuple(z) not in schon_da for z in aktuell[SCHLUESSEL].to_numpy()]]
    else:
        bekannt, neu = None, aktuell
    neu = neu.drop_duplicates(SCHLUESSEL).copy()
    if neu.empty:
        return neu
    neu["erstmals_gesehen"] = pd.Timestamp.now(tz="Europe/Berlin").strftime("%Y-%m-%d %H:%M:%S")
    alle = neu if bekannt is None else pd.concat([bekannt, neu], ignore_index=True)
    alle.sort_values(["aktiviert", "emittent"], ascending=False, kind="stable").to_csv(DATEI, index=False)
    return neu


def lade_meldungen() -> pd.DataFrame:
    m = pd.read_csv(DATEI, dtype=str, keep_default_na=False)
    for spalte in ["preis", "volumen"]:
        m[spalte] = pd.to_numeric(m[spalte], errors="coerce")
    for spalte in ["mitteilungsdatum", "geschaeftsdatum", "aktiviert"]:
        m[spalte] = pd.to_datetime(m[spalte], errors="coerce")
    return m


if __name__ == "__main__":
    neu = aktualisieren()
    print(f"{len(neu)} neue Meldungen, gespeichert in {DATEI}")
