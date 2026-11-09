"""Lobbying-Ausgaben der S&P-500-Firmen aus den LD-2-Quartalsberichten (Lobbying Disclosure Act).

    python3 -m pipeline.lobbying [--max-minuten N]   → daten/lobbying_berichte.csv (alle Berichte, setzt fort),
                                                       daten/lobbying.csv (kuerzel, jahr, betrag, berichte)

Quelle: Clerk des Repräsentantenhauses, disclosurespreview.house.gov/data/LD/<Jahr>_<n>Quarter_XML.zip (Liste in
LdSearchPastFilings.json, ohne Schlüssel; lda.gov und lda.senate.gov sperren Abrufe von außen). Eine XML-Datei je
Bericht. Gezählt wie bei OpenSecrets: Firma, die selbst lobbyiert (Auftraggeber = Meldender), meldet ihre Ausgaben
(`expenses`); beauftragte Lobbyfirmen melden ihre Einnahmen von diesem Auftraggeber (`income`). Beides zusammen =
Lobbying-Ausgaben der Firma. Korrekturberichte (Q1A …) ersetzen den ursprünglichen Bericht (gleiche senateID,
gleiches Quartal, neuestes Unterschriftsdatum). Firma ↔ Auftraggeber über dieselbe Namensregel wie bei den Spenden.
Werte unter 5.000 $ melden die Formulare als „weniger als 5.000“ → zählen als 0.
"""

import io
import re
import sys
import time
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd
import requests

from pipeline import DATEN, HEADER
from pipeline.staatsauftraege import ZUSATZ, _woerter

BASIS = "https://disclosurespreview.house.gov/data/LD/"
BERICHTE = DATEN / "lobbying_berichte.csv"
ERGEBNIS = DATEN / "lobbying.csv"
FORTSCHRITT = DATEN / "lobbying_fortschritt.csv"
AB_JAHR = 2018
FELDER = ["senateID", "organizationName", "clientName", "selfSelect", "reportYear", "reportType", "income",
          "expenses", "noLobbying", "signedDate"]


def _zahl(text: str) -> float:
    t = re.sub(r"[^0-9.]", "", text or "")
    return float(t) if t else 0.0


def datei_lesen(inhalt: bytes) -> pd.DataFrame:
    zeilen = []
    with zipfile.ZipFile(io.BytesIO(inhalt)) as z:
        for name in z.namelist():
            try:
                wurzel = ET.fromstring(z.read(name))
            except ET.ParseError:
                continue
            zeilen.append({f: (wurzel.findtext(f) or "").strip() for f in FELDER} | {"datei": name})
    return pd.DataFrame(zeilen)


def laden(max_minuten: float = 120) -> None:
    """Lädt alle Quartalsdateien ab AB_JAHR, die neu sind oder sich geändert haben (Zeitstempel in der Liste)."""
    start = time.time()
    liste = requests.get(BASIS + "LdSearchPastFilings.json", headers=HEADER, timeout=60).json()
    quartale = [x for x in liste if "Quarter" in x["file"] and int(x["file"][:4]) >= AB_JAHR]
    fertig = pd.read_csv(FORTSCHRITT, dtype=str) if FORTSCHRITT.exists() else pd.DataFrame(columns=["file", "name"])
    stand = dict(zip(fertig["file"], fertig["name"]))
    berichte = pd.read_csv(BERICHTE, dtype=str, keep_default_na=False) if BERICHTE.exists() else pd.DataFrame()
    for x in quartale:
        if stand.get(x["file"]) == x["name"]:
            continue
        if (time.time() - start) / 60 > max_minuten:
            print("Zeit um, nächster Lauf macht weiter")
            break
        r = requests.get(BASIS + x["file"], headers=HEADER, timeout=600)
        r.raise_for_status()
        neu = datei_lesen(r.content).assign(quelle=x["file"])
        if len(berichte):
            berichte = berichte[berichte["quelle"] != x["file"]]
        berichte = pd.concat([berichte, neu], ignore_index=True)
        berichte.to_csv(BERICHTE, index=False)
        stand[x["file"]] = x["name"]
        pd.DataFrame({"file": list(stand), "name": list(stand.values())}).to_csv(FORTSCHRITT, index=False)
        print(f"{x['file']}: {len(neu)} Berichte")


# Wo der Auftraggeber in den Berichten anders heißt als die Firma
NAMEN = {"GOOGL": ["Google", "Google Client Services"], "META": ["Facebook"],
         "RTX": ["Raytheon Technologies", "United Technologies"]}


def kunde(name: str) -> str:
    """„Meta Platforms, Inc. (formerly Facebook, Inc. and various subsidiaries)“ → „Meta Platforms, Inc.“;
    „Cornerstone Government Affairs obo Google Client Services LLC“ → „Google Client Services LLC“."""
    t = str(name).lstrip("?* ")
    t = re.split(r"\b(?:obo|o/b/o|on behalf of)\b", t, flags=re.I)[-1]
    t = re.split(r"\(|\b(?:fka|f/k/a|formerly|d/b/a|dba)\b", t, flags=re.I)[0]
    t = re.sub(r"\b(?:and|&)\s+(?:its\s+|various\s+|certain\s+)?(?:subsidiaries|affiliates|affiliated companies)\b",
               "", t, flags=re.I)
    return t.strip(" ,;:-")


def je_firma(berichte: pd.DataFrame, firmen: pd.DataFrame) -> pd.DataFrame:
    b = berichte.copy()
    b["quartal"] = b["reportType"].str[:2]
    b["zeit"] = pd.to_datetime(b["signedDate"], errors="coerce", format="mixed")
    b = b[b["quartal"].isin(["Q1", "Q2", "Q3", "Q4"])]
    # Korrektur (Q2A) ersetzt Original: je Meldender/Auftraggeber (senateID) und Quartal der neueste Bericht
    b = b.sort_values("zeit").drop_duplicates(["senateID", "reportYear", "quartal"], keep="last")
    b["betrag"] = [_zahl(e) if s == "Y" else _zahl(i) for s, e, i in zip(b["selfSelect"], b["expenses"], b["income"])]
    kunden = {n: _woerter(kunde(n)) for n in b["clientName"].unique()}
    zeilen = []
    for f in firmen.itertuples():
        namen = {frozenset(_woerter(n)) for n in [f.sec_name, f.name] + NAMEN.get(f.kuerzel, [])}
        treffer = [n for n, k in kunden.items() if any(fw and fw <= k and (k - fw) <= ZUSATZ for fw in namen)]
        if treffer:
            zeilen.append(b[b["clientName"].isin(treffer)].assign(kuerzel=f.kuerzel))
    if not zeilen:
        return pd.DataFrame(columns=["kuerzel", "jahr", "betrag", "berichte"])
    t = pd.concat(zeilen)
    return (t.groupby(["kuerzel", "reportYear"]).agg(betrag=("betrag", "sum"), berichte=("datei", "size"))
            .reset_index().rename(columns={"reportYear": "jahr"}))


def lesen() -> pd.DataFrame:
    return pd.read_csv(ERGEBNIS) if ERGEBNIS.exists() else pd.DataFrame(columns=["kuerzel", "jahr", "betrag", "berichte"])


def main() -> int:
    minuten = float(sys.argv[sys.argv.index("--max-minuten") + 1]) if "--max-minuten" in sys.argv else 120
    laden(minuten)
    berichte = pd.read_csv(BERICHTE, dtype=str, keep_default_na=False)
    firmen = pd.read_csv(DATEN / "us_firmen.csv")
    ergebnis = je_firma(berichte, firmen)
    ergebnis.to_csv(ERGEBNIS, index=False)
    letztes = ergebnis[ergebnis["jahr"].astype(int) == ergebnis["jahr"].astype(int).max() - 1]
    print(f"{len(berichte)} Berichte, {ergebnis['kuerzel'].nunique()} Firmen mit Lobbying; größte im Vorjahr:")
    print(letztes.sort_values("betrag", ascending=False).head(15).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
