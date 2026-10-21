"""Baut daten/firmen.csv: aktuelle DAX- und MDAX-Mitglieder mit ISIN und Yahoo-Ticker.

Weg: Firmen-Links aus den Tabellen der deutschen Wikipedia → ISINs aus Wikidata (P946)
→ Yahoo-Ticker über die Yahoo-Suche nach der ISIN. Eine Zeile je Aktiengattung, damit
auch Meldungen zu Vorzugs- oder Stammaktien derselben Firma zugeordnet werden.

Aufruf (nach Indexänderungen, etwa vierteljährlich): python3 -m pipeline.firmen
Ergebnis danach kurz von Hand prüfen.
"""

import time
import urllib.parse

import pandas as pd
import requests
from bs4 import BeautifulSoup

from pipeline import DATEN, HEADER

INDIZES = {"DAX": "^GDAXI", "MDAX": "^MDAXI"}
# Bevorzugte Börsen bei mehreren Treffern: Xetra, dann andere Euro-Börsen
BOERSEN = ["GER", "FRA", "PAR", "AMS", "BRU", "MIL", "MCE", "VIE"]
# Wikidata führt teils veraltete oder unvollständige ISINs (geprüft am 21.10.2026 an Yahoo
# und den BaFin-Meldungen): alte ISIN → aktuelle ISINs derselben Aktie
ISIN_ERSATZ = {
    "NL0000240000": ["NL0015002CX3"],                  # Qiagen
    "DE0007850000": ["DE000RENK730"],                  # Renk
    "DE0006229107": ["DE000A2NB601"],                  # Jenoptik
    "CY0105562116": ["LU1673108939"],                  # Aroundtown
    "DE0005790406": ["DE000A3E5D56"],                  # Fuchs Stammaktie
    "DE0005790430": ["DE000A3E5D64"],                  # Fuchs Vorzugsaktie
    "DE000SHA0019": ["DE000SHA0100"],                  # Schaeffler nach Fusion mit Vitesco
    "DE0005785604": ["DE0005785604", "DE000FRE5EN2"],  # Fresenius, beide ISINs in BaFin-Meldungen
}
# Yahoo-Suche liefert hier keinen oder einen falschen Börsenplatz; Ziel ist Xetra (.DE)
TICKER_KORREKTUR = {
    "NL0015002CX3": "QIA.DE", "NL0000235190": "AIR.DE", "DE0005785604": "FRE.DE",
    "DE000FRE5EN2": "FRE.DE", "DE000DWS1007": "DWS.DE", "DE000TKMS001": "TKMS.DE",
    "DE000SHA0100": "SHA0.DE",
}


def _artikel(index: str) -> list:
    html = requests.get(f"https://de.wikipedia.org/wiki/{index}", headers=HEADER, timeout=30).text
    for tabelle in BeautifulSoup(html, "lxml").find_all("table"):
        kopf = [th.get_text(strip=True) for th in tabelle.find("tr").find_all("th")]
        if "Name" not in kopf or "Branche" not in kopf:
            continue
        spalte = kopf.index("Name")
        titel = []
        for zeile in tabelle.find_all("tr")[1:]:
            zellen = zeile.find_all(["td", "th"])
            link = zellen[spalte].find("a") if len(zellen) > spalte else None
            if link:
                titel.append(urllib.parse.unquote(link["href"].split("/wiki/")[-1]).replace("_", " "))
        return titel
    raise RuntimeError(f"Keine Mitgliedertabelle auf der Wikipedia-Seite {index} gefunden")


def _wikidata(titel: list) -> dict:
    """Wikipedia-Titel → (Name, [ISINs])."""
    ergebnis = {}
    for i in range(0, len(titel), 40):
        teil = titel[i: i + 40]
        seiten = requests.get("https://de.wikipedia.org/w/api.php", headers=HEADER, timeout=30, params={
            "action": "query", "prop": "pageprops", "ppprop": "wikibase_item", "redirects": 1,
            "titles": "|".join(teil), "format": "json"}).json()["query"]
        umleitung = {u["to"]: u["from"] for u in seiten.get("redirects", []) + seiten.get("normalized", [])}
        ids = {}
        for seite in seiten["pages"].values():
            q = seite.get("pageprops", {}).get("wikibase_item")
            if q:
                ids[q] = umleitung.get(seite["title"], seite["title"])
        daten = requests.get("https://www.wikidata.org/w/api.php", headers=HEADER, timeout=30, params={
            "action": "wbgetentities", "ids": "|".join(ids), "props": "claims|labels",
            "languages": "de", "format": "json"}).json()["entities"]
        for q, e in daten.items():
            isins = [c["mainsnak"]["datavalue"]["value"] for c in e["claims"].get("P946", [])
                     if "datavalue" in c["mainsnak"] and c.get("rank") != "deprecated"]
            ergebnis[ids[q]] = (e["labels"].get("de", {}).get("value", ids[q]), isins)
    return ergebnis


def _yahoo_ticker(isin: str) -> str | None:
    antwort = requests.get("https://query2.finance.yahoo.com/v1/finance/search", timeout=30,
                           headers={"User-Agent": "Mozilla/5.0"},
                           params={"q": isin, "quotesCount": 10, "newsCount": 0})
    treffer = [q for q in antwort.json().get("quotes", []) if q.get("quoteType") == "EQUITY"]
    treffer.sort(key=lambda q: BOERSEN.index(q["exchange"]) if q.get("exchange") in BOERSEN else 99)
    return treffer[0]["symbol"] if treffer else None


def baue_firmen() -> pd.DataFrame:
    zeilen = []
    for index, benchmark in INDIZES.items():
        titel = _artikel(index)
        wd = _wikidata(titel)
        print(f"{index}: {len(titel)} Firmen")
        for t in titel:
            name, isins = wd.get(t, (t, []))
            if not isins:
                print(f"  ohne ISIN: {t}")
            for isin in [neu for alt in isins for neu in ISIN_ERSATZ.get(alt, [alt])]:
                if isin[:2] == "US":  # ADRs in Dollar, gehören nicht zur Indexaktie
                    continue
                ticker = TICKER_KORREKTUR.get(isin) or _yahoo_ticker(isin)
                time.sleep(0.3)
                zeilen.append({"isin": isin, "name": name, "index": index, "benchmark": benchmark,
                               "ticker": ticker or ""})
                if not ticker:
                    print(f"  ohne Ticker: {name} {isin}")
    firmen = pd.DataFrame(zeilen).drop_duplicates("isin")
    firmen.to_csv(DATEN / "firmen.csv", index=False)
    print(f"{len(firmen)} Aktiengattungen gespeichert, davon {(firmen.ticker != '').sum()} mit Ticker")
    return firmen


if __name__ == "__main__":
    baue_firmen()
