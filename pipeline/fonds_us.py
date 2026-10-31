"""Bestände von US-Fonds an unseren Firmen aus den N-PORT-Daten der SEC.

Jeder in den USA zugelassene Fonds meldet vierteljährlich alle Positionen (Form N-PORT). Die SEC stellt das je
Quartal als Zip bereit (~440 MB gepackt). `laden()` prüft, ob es ein neues Quartal gibt, liest nur Positionen in
unseren ISINs direkt aus dem Zip (ohne Entpacken) und speichert je ISIN und Fondsgesellschaft eine Zeile nach
daten/fonds_us.csv. Das Zip wird danach gelöscht.

    python3 -m pipeline.fonds_us          neuestes Quartal laden, falls noch nicht vorhanden
"""

import csv
import io
import re
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests

from pipeline import DATEN

ERGEBNIS = DATEN / "fonds_us.csv"
SEITE = "https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets"
DATEI = "https://www.sec.gov/files/dera/data/form-n-port-data-sets/{}_nport.zip"
HEADER = {"User-Agent": "insider-monitor tobzwilling@gmx.de"}  # SEC verlangt Name und Kontakt

# Fondsgesellschaft (Muster im Namen des Fondsträgers) → Konzern zur Anzeige, Muster im Namen eines Großaktionärs.
# Steht derselbe Konzern schon unter den Großaktionären, sind seine Fonds dort mitgezählt und fallen hier weg.
KONZERNE = [
    ("BlackRock", r"ishares|blackrock", r"blackrock"),
    ("Vanguard", r"vanguard", r"vanguard"),
    ("Capital Group", r"eupac|new perspective|capital income builder|capital world|international growth & income|"
                      r"smallcap world|income fund of america|american funds|growth fund of america|"
                      r"washington mutual|fundamental investors", r"capital research|capital group"),
    ("Fidelity", r"fidelity", r"fmr|fidelity"),
    ("Dodge & Cox", r"dodge & cox", r"dodge"),
    ("Dimensional", r"dimensional|^dfa ", r"dimensional"),
    ("Charles Schwab", r"schwab", r"schwab"),
    ("Causeway", r"causeway", r"causeway"),
    ("Harris Associates (Oakmark)", r"harris associates", r"harris associates"),
    ("State Street (SPDR)", r"spdr|select sector", r"state street"),
    ("Goldman Sachs", r"goldman sachs", r"goldman"),
    ("TIAA/Nuveen", r"tiaa|college retirement", r"tiaa|nuveen"),
    ("T. Rowe Price", r"t\. rowe", r"t\. rowe"),
    ("MFS", r"^mfs ", r"massachusetts financial"),
    ("JPMorgan", r"j\.p\. morgan|jpmorgan", r"jpmorgan|j\.p\. morgan"),
    ("Artisan", r"artisan", r"artisan"),
    ("Franklin Templeton", r"franklin|templeton", r"franklin"),
    ("DWS (Xtrackers)", r"dbx etf", r"dws"),
    ("Thornburg", r"thornburg", r"thornburg"),
    ("First Eagle", r"first eagle", r"first eagle"),
    ("WisdomTree", r"wisdomtree", r"wisdomtree"),
    ("First Trust", r"first trust", r"first trust"),
    ("Janus Henderson", r"janus", r"janus"),
    ("American Century", r"american century", r"american century"),
    ("Invesco", r"invesco", r"invesco"),
    ("Hartford", r"hartford", r"hartford|wellington"),
    ("Principal", r"principal funds", r"principal"),
]


def konzern(gesellschaft: str) -> tuple[str, str | None]:
    """Fondsträger → (Anzeigename, Muster für Großaktionäre). Unbekannte behalten ihren Namen."""
    g = gesellschaft.lower()
    for name, muster, halter in KONZERNE:
        if re.search(muster, g):
            return name, halter
    return gesellschaft, None


def neuestes_quartal() -> str:
    seite = requests.get(SEITE, headers=HEADER, timeout=60).text
    return max(re.findall(r"(\d{4}q[1-4])_nport\.zip", seite))


def _zeilen(z: zipfile.ZipFile, name: str):
    with z.open(name) as f:
        yield from csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace"), delimiter="\t")


def auswerten(zip_pfad: Path, isins: set, quartal: str) -> pd.DataFrame:
    """Zip → je ISIN und Fondsträger: Stückzahl, Zahl der Fonds, mittlerer Stichtag. Je Fonds nur der neueste Bericht."""
    csv.field_size_limit(10**9)
    z = zipfile.ZipFile(zip_pfad)
    pos_isin = {r["HOLDING_ID"]: r["IDENTIFIER_ISIN"] for r in _zeilen(z, "IDENTIFIERS.tsv") if r["IDENTIFIER_ISIN"] in isins}
    pos = pd.DataFrame([(r["ACCESSION_NUMBER"], pos_isin[r["HOLDING_ID"]], float(r["BALANCE"] or 0))
                        for r in _zeilen(z, "FUND_REPORTED_HOLDING.tsv")
                        if r["HOLDING_ID"] in pos_isin and r["UNIT"] == "NS" and r["ASSET_CAT"] == "EC"],
                       columns=["acc", "isin", "stueck"])
    serie = pd.DataFrame([(r["ACCESSION_NUMBER"], r["SERIES_ID"]) for r in _zeilen(z, "FUND_REPORTED_INFO.tsv")],
                         columns=["acc", "serie"])
    traeger = pd.DataFrame([(r["ACCESSION_NUMBER"], r["REGISTRANT_NAME"]) for r in _zeilen(z, "REGISTRANT.tsv")],
                           columns=["acc", "gesellschaft"])
    sub = pd.DataFrame([(r["ACCESSION_NUMBER"], r["REPORT_DATE"], r["FILING_DATE"]) for r in _zeilen(z, "SUBMISSION.tsv")],
                       columns=["acc", "stichtag", "eingereicht"])
    for spalte in ["stichtag", "eingereicht"]:
        sub[spalte] = pd.to_datetime(sub[spalte], format="%d-%b-%Y")
    meta = serie.merge(traeger, on="acc").merge(sub, on="acc")
    neueste = meta.sort_values(["stichtag", "eingereicht"]).groupby("serie").tail(1)  # Nachträge ersetzen Vorgänger
    pos = pos.merge(neueste, on="acc")
    erg = pos.groupby(["isin", "gesellschaft"]).agg(stueck=("stueck", "sum"), fonds=("serie", "nunique"),
                                                    stichtag=("stichtag", "median")).reset_index()
    erg["stichtag"] = erg["stichtag"].dt.date
    erg["quartal"] = quartal
    return erg


def laden() -> None:
    quartal = neuestes_quartal()
    if ERGEBNIS.exists() and quartal in set(pd.read_csv(ERGEBNIS, usecols=["quartal"])["quartal"]):
        print(f"US-Fonds: {quartal} schon vorhanden")
        return
    isins = set(pd.read_csv(DATEN / "firmen.csv")["isin"])
    with tempfile.TemporaryDirectory() as ordner:
        pfad = Path(ordner) / f"{quartal}.zip"
        with requests.get(DATEI.format(quartal), headers=HEADER, stream=True, timeout=120) as antwort:
            antwort.raise_for_status()
            with open(pfad, "wb") as f:
                for stueck in antwort.iter_content(1 << 20):
                    f.write(stueck)
        erg = auswerten(pfad, isins, quartal)
    erg.to_csv(ERGEBNIS, index=False)  # nur das neueste Quartal behalten
    print(f"US-Fonds: {quartal} geladen, {len(erg)} Zeilen, {erg['isin'].nunique()} Firmen")


def je_firma(fonds: pd.DataFrame, halter: list, gesamt: float, mindestens: float = 0.5) -> dict | None:
    """Fondsbestände einer ISIN → {'teile': [(Konzern, %)], 'weitere': %, 'stichtag': Datum}.
    halter: Namen der Großaktionäre dieser Firma; deren Konzerne fallen weg (dort schon mitgezählt).
    Konzerne ab `mindestens` % einzeln, der Rest als 'weitere'."""
    if fonds.empty or not gesamt:
        return None
    halter = " ".join(halter).lower()
    k = fonds.assign(konzern=fonds["gesellschaft"].map(lambda g: konzern(g)[0]),
                     doppelt=fonds["gesellschaft"].map(lambda g: bool(konzern(g)[1]) and bool(re.search(konzern(g)[1], halter))))
    k = k[~k["doppelt"]]
    anteile = (100 * k.groupby("konzern")["stueck"].sum() / gesamt).sort_values(ascending=False)
    einzeln = anteile[anteile >= mindestens]
    return {"teile": list(einzeln.items()), "weitere": float(anteile.sum() - einzeln.sum()),
            "stichtag": pd.to_datetime(fonds["stichtag"]).median()}


if __name__ == "__main__":
    laden()
    sys.exit(0)
