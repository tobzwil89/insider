"""Anteile des Norwegischen Staatsfonds (Norges Bank Investment Management) an unseren Firmen.

NBIM veröffentlicht halbjährlich alle Aktienbestände mit Eigentumsanteil in Prozent (Stand 30.06. und 31.12.).
Die Daten kommen aus derselben JSON-Schnittstelle, die die Seite nbim.no/en/investments/all-investments/ nutzt.
Eine ISIN gibt es dort nicht, zugeordnet wird über den Namen (bereinigt) und `NAMEN` für Abweichungen.

    python3 -m pipeline.norwegen          neuesten Stand laden, falls noch nicht vorhanden
"""

import re
import sys

import pandas as pd
import requests

from pipeline import DATEN

ERGEBNIS = DATEN / "norwegen.csv"
BASIS = "https://www.nbim.no/api/investments/v2/"
HEADER = {"User-Agent": "Mozilla/5.0 (insider.tobiaszwilling.me)"}

# Unser Firmenname → Name bei NBIM, wo die Bereinigung nicht reicht (geprüft 31.10.2026).
# Airbus fehlt bei NBIM absichtlich (ethischer Ausschluss), Deutz hält der Fonds nicht.
NAMEN = {
    "BMW": "Bayerische Motoren Werke AG",
    "DHL AG": "Deutsche Post AG",
    "Infineon": "Infineon Technologies AG",
    "Munich Re": "Muenchener Rueckversicherungs-Gesellschaft AG in Muenchen",
    "Lufthansa Group": "Deutsche Lufthansa AG",
    "Fraport": "Fraport AG Frankfurt Airport Services Worldwide",
    "Fuchs Petrolub SE": "FUCHS SE",
    "Porsche": "Dr Ing hc F Porsche AG",
    "Schaeffler Gruppe": "Schaeffler AG",
}
WEG = r"\b(ag|se|sa|nv|kgaa|gmbh|co|aktiengesellschaft|group|holding|the|unternehmen)\b"


def _norm(name: str) -> str:
    name = name.lower().replace("ü", "ue").replace("ö", "oe").replace("ä", "ae")
    return " ".join(re.sub(WEG, " ", re.sub(r"[^a-z0-9 ]", " ", name)).split())


def _json(datei: str) -> dict:
    antwort = requests.get(BASIS + datei, headers=HEADER, timeout=60)
    antwort.raise_for_status()
    return antwort.json()["data"]


def laden() -> None:
    neuester = max(_json("init.json")["details"], key=lambda x: x["date"])
    stichtag = neuester["date"][:10]
    if ERGEBNIS.exists() and stichtag in set(pd.read_csv(ERGEBNIS)["stichtag"]):
        print(f"Norwegen: {stichtag} schon vorhanden")
        return
    nbim = pd.DataFrame(_json(f"{neuester['fileName']}?v={neuester['v']}"))
    nbim = nbim[nbim["at"].eq(0)]  # 0 = Aktien
    nach_name = dict(zip(nbim["n"], nbim["o"]))
    eindeutig = nbim.assign(k=nbim["n"].map(_norm)).drop_duplicates("k", keep=False).set_index("k")
    zeilen = []
    for firma in pd.read_csv(DATEN / "firmen.csv")["name"].drop_duplicates():
        name = NAMEN.get(firma) or (eindeutig.loc[_norm(firma), "n"] if _norm(firma) in eindeutig.index else None)
        if name in nach_name:
            zeilen.append({"firma": firma, "name_nbim": name, "anteil": nach_name[name], "stichtag": stichtag})
    pd.DataFrame(zeilen).to_csv(ERGEBNIS, index=False)  # nur der neueste Stand
    print(f"Norwegen: {stichtag} geladen, {len(zeilen)} Firmen")


if __name__ == "__main__":
    laden()
    sys.exit(0)
