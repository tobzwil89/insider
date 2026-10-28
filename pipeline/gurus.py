"""Depots bekannter US-Investoren aus den 13F-Meldungen der SEC lesen.

Wer in den USA mehr als 100 Mio. USD in US-Wertpapieren verwaltet, meldet vierteljährlich spätestens 45 Tage
nach Quartalsende seine Positionen (Formular 13F-HR). Enthalten sind nur an US-Börsen gehandelte Wertpapiere
(auch ADRs wie SAP), keine Leerverkäufe, kein Bargeld.

Je Meldung gibt es eine XML-Tabelle („information table“), eine Zeile je Wertpapier und Verwalter.
Werte bis Ende 2022 in Tausend USD, ab den Meldungen vom 03.01.2023 in USD.
Nachträge (13F-HR/A) werden bisher nicht gelesen.
"""

import time

import pandas as pd
import requests
from lxml import etree

from pipeline import DATEN

# SEC verlangt einen Namen mit Kontakt im User-Agent, höchstens 10 Abrufe je Sekunde
HEADER = {"User-Agent": "insider-monitor tobzwilling@gmx.de"}
DATEI = DATEN / "gurus.csv"

GURUS = {  # CIK bei der SEC → Anzeigename
    1067983: "Warren Buffett (Berkshire Hathaway)",
    1336528: "Bill Ackman (Pershing Square)",
    1061768: "Seth Klarman (Baupost)",
    1709323: "Li Lu (Himalaya Capital)",
    1656456: "David Tepper (Appaloosa)",
    1040273: "Dan Loeb (Third Point)",
    1649339: "Michael Burry (Scion)",
}


def _holen(url: str) -> requests.Response:
    time.sleep(0.2)
    antwort = requests.get(url, headers=HEADER, timeout=60)
    antwort.raise_for_status()
    return antwort


def meldungen(cik: int) -> list[dict]:
    """Alle 13F-HR einer Firma laut SEC (nur die letzten ~1.000 Einreichungen jeder Art)."""
    r = _holen(f"https://data.sec.gov/submissions/CIK{cik:010d}.json").json()["filings"]["recent"]
    return [{"nummer": r["accessionNumber"][i], "quartal": r["reportDate"][i], "eingereicht": r["filingDate"][i]}
            for i, form in enumerate(r["form"]) if form == "13F-HR"]


def positionen(cik: int, nummer: str, eingereicht: str) -> list[dict]:
    """Die Tabelle einer Meldung → eine Zeile je Wertpapier und Verwalter."""
    ordner = f"https://www.sec.gov/Archives/edgar/data/{cik}/{nummer.replace('-', '')}"
    dateien = [d["name"] for d in _holen(f"{ordner}/index.json").json()["directory"]["item"]]
    xml = next(d for d in dateien if d.lower().endswith(".xml") and d != "primary_doc.xml")
    wurzel = etree.fromstring(_holen(f"{ordner}/{xml}").content)
    faktor = 1 if eingereicht >= "2023-01-03" else 1000

    def feld(zeile, name):
        treffer = zeile.xpath(f".//*[local-name()='{name}']/text()")
        return treffer[0].strip() if treffer else ""

    zeilen = [{"emittent": feld(z, "nameOfIssuer"), "klasse": feld(z, "titleOfClass"), "cusip": feld(z, "cusip"),
               "wert_usd": float(feld(z, "value")), "stueck": float(feld(z, "sshPrnamt")),
               "art": feld(z, "sshPrnamtType"), "put_call": feld(z, "putCall")}
              for z in wurzel.xpath("//*[local-name()='infoTable']")]
    # Manche melden auch nach 2023 weiter in Tausend (z. B. Baupost): erkennbar an Preisen unter 1 USD je Aktie
    preise = pd.Series([z["wert_usd"] / z["stueck"] for z in zeilen if z["art"] == "SH" and z["stueck"] > 0])
    if faktor == 1 and len(preise) and preise.median() < 1:
        faktor = 1000
    for z in zeilen:
        z["wert_usd"] *= faktor
    return zeilen


def laden(quartale: int = 8) -> pd.DataFrame:
    """Fehlende Meldungen der letzten `quartale` Quartale je Guru nachladen und in gurus.csv speichern."""
    alt = pd.read_csv(DATEI, dtype=str) if DATEI.exists() else pd.DataFrame(columns=["nummer"])
    bekannt = set(alt["nummer"])
    neu = []
    for cik, name in GURUS.items():
        for m in meldungen(cik)[:quartale]:
            if m["nummer"] in bekannt:
                continue
            zeilen = positionen(cik, m["nummer"], m["eingereicht"])
            print(f"{name}: {m['quartal']} ({len(zeilen)} Zeilen)")
            neu += [{"guru": name, "cik": cik, **m, **z} for z in zeilen]
    daten = pd.concat([alt, pd.DataFrame(neu).astype(str)], ignore_index=True)
    daten.to_csv(DATEI, index=False)
    return daten


def _je_papier(teil: pd.DataFrame) -> pd.DataFrame:
    """Zeilen je Verwalter zu einer Zeile je Wertpapier (CUSIP) und Art (Aktie, Put, Call) zusammenfassen."""
    return (teil.fillna({"put_call": ""}).groupby(["cusip", "put_call"])
            .agg(emittent=("emittent", "first"), klasse=("klasse", "first"),
                 wert_usd=("wert_usd", "sum"), stueck=("stueck", "sum")).reset_index())


def depot(daten: pd.DataFrame, cik: int) -> dict:
    """Letztes Quartal eines Gurus mit Veränderung zum Vorquartal (nach Stückzahl)."""
    eigene = daten[daten["cik"] == cik]
    quartale = sorted(eigene["quartal"].unique(), reverse=True)
    jetzt = _je_papier(eigene[eigene["quartal"] == quartale[0]])
    vorher = (_je_papier(eigene[eigene["quartal"] == quartale[1]]) if len(quartale) > 1
              else jetzt.iloc[:0])
    p = jetzt.merge(vorher[["cusip", "put_call", "emittent", "klasse", "stueck"]], on=["cusip", "put_call"],
                    how="outer", suffixes=("", "_vorher"))
    p["emittent"] = p["emittent"].fillna(p["emittent_vorher"])
    p["klasse"] = p["klasse"].fillna(p["klasse_vorher"])
    p = p.fillna({"wert_usd": 0.0, "stueck": 0.0})
    aenderung = p["stueck"] / p["stueck_vorher"] - 1
    p["veraenderung"] = aenderung.where(p["stueck_vorher"].notna() & (p["stueck"] > 0))
    p["status"] = "unverändert"
    p.loc[aenderung > 0.005, "status"] = "aufgestockt"
    p.loc[aenderung < -0.005, "status"] = "reduziert"
    p.loc[p["stueck_vorher"].isna(), "status"] = "neu"
    p.loc[p["stueck"] == 0, "status"] = "verkauft"
    if len(quartale) < 2:
        p["status"] = ""
    # Optionen zählen zum Wert des Basiswerts, nicht zum Depot; Anteil deshalb nur über Aktien
    aktien = p["put_call"] == ""
    gesamt = p.loc[aktien, "wert_usd"].sum()
    p["anteil"] = (p["wert_usd"] / gesamt).where(aktien)
    zeile = eigene[eigene["quartal"] == quartale[0]].iloc[0]
    return {"name": zeile["guru"], "cik": cik, "quartal": quartale[0], "eingereicht": zeile["eingereicht"],
            "vorquartal": quartale[1] if len(quartale) > 1 else None, "wert": gesamt,
            "positionen": p.sort_values(["wert_usd", "emittent"], ascending=[False, True], ignore_index=True)}


def alle_depots() -> list[dict]:
    if not DATEI.exists():
        return []
    daten = pd.read_csv(DATEI, dtype={"put_call": str, "cusip": str})
    return [depot(daten, cik) for cik in GURUS if cik in set(daten["cik"])]


if __name__ == "__main__":
    laden()
