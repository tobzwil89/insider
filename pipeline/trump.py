"""Geschäfte von Donald J. Trump (daten/trump.csv, gelesen von trump_laden.py) für die Politikerseiten aufbereiten.

    python3 -m pipeline.trump        Zuordnung prüfen: Trefferquote und unklare Namen ausgeben

Die Meldungen (OGE 278-T) nennen nur Namen in Brokerschreibweise („WORKDAY INC CLASS A“, „AUTOMATIC DATA PROCESSIN“,
„BAXTER INTL INC“), keine Kürzel. Zuordnung über die SEC-Liste company_tickers.json: beide Seiten gleich bereinigen
(Rechtsformen, Gattung, Zusätze wie UNSOLICITED weg, Abkürzungen ausgeschrieben), dann gleicher Name; sonst abgeschnittener
Name als eindeutiger Anfang eines SEC-Namens. Anleihen (Zins, Fälligkeit) bekommen kein Kürzel.
Rechtlich wie die Kongressdaten (5 U.S.C. § 13107(c)) → nur lokal, daten/trump.csv steht in .gitignore.
"""

import re

import pandas as pd
import requests

from pipeline import DATEN

SEC = "https://www.sec.gov/files/company_tickers.json"
SEC_HEADER = {"User-Agent": "insider-monitor tobzwilling@gmx.de"}
TICKER_DATEI = DATEN / "sec_tickers.json"

ANLEIHE = re.compile(r"%|\bDUE\b|\bB/E\b|\bPERP\b|\bNOTES?\b|\bBDS?\b|\bREV\b|\bRFDG\b|\bSER [A-Z0-9]+\b|\d{2}/\d{2}/\d{2,4}")
ZUSAETZE = (r"\b(UNSOLICITED|SOLICITED|DISCRETIONARY|NEW|COM|COMMON|STOCK|SHS|ORD|REIT|ADR|ADS|SPON|SPONSORED|THE|"
            r"CLASS|EQUITY|PAR|IRELAND|MASS|NEV|MD|VA)\b")
GATTUNG = r"\b(CLASS|CL|CI|SER|SERIES)( SERIES)? ?[A-C]\b"
RECHTSFORM = r"\b(INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|COS|LTD|LIMITED|PLC|NV|SA|AG|LP|LLC|HLDGS|HLDG|HOLDINGS|HOLDING|GROUP|COMPANIES|GRP|TR|TRUST|DE|DEL)\b"
ABKUERZUNG = {"INTL": "INTERNATIONAL", "ASSOCS": "ASSOCIATES", "PPTYS": "PROPERTIES", "PPTY": "PROPERTY",
              "MKTS": "MARKETS", "BKG": "BANKING", "SYS": "SYSTEMS", "TECHNOLOGIES": "TECHNOLOGY",
              "TECHS": "TECHNOLOGY", "TECH": "TECHNOLOGY", "SVCS": "SERVICES", "SVC": "SERVICE", "FINL": "FINANCIAL",
              "NATL": "NATIONAL", "AMER": "AMERICA", "AMERN": "AMERICAN", "BANCORPORATION": "BANCORP",
              "PHARMACEUTICALS": "PHARMACEUTICAL", "PHARMA": "PHARMACEUTICAL", "MFG": "MANUFACTURING",
              "INDS": "INDUSTRIES", "LABS": "LABORATORIES", "COMMNS": "COMMUNICATIONS", "COMMUNICATION": "COMMUNICATIONS",
              "ENTMT": "ENTERTAINMENT", "MGMT": "MANAGEMENT", "RES": "RESOURCES", "SCIENCES": "SCIENCE",
              "SOLUTIONS": "SOLUTION", "PRODS": "PRODUCTS", "CMNTY": "COMMUNITY", "BK": "BANK", "ENTERPRISES": "ENTERPRISE",
              "UTD": "UNITED", "WHSL": "WHOLESALE", "INSTRS": "INSTRUMENTS", "PMTS": "PAYMENTS", "WKS": "WORKS",
              "PTS": "PARTS", "MED": "MEDICAL", "RESH": "RESEARCH", "INDTY": "INDEMNITY", "RLTY": "REALTY",
              "INVT": "INVESTMENT", "MTG": "MORTGAGE", "ASSOC": "ASSOCIATES", "IBM": "INTERNATIONAL BUSINESS MACHINES",
              "WTR": "WATER", "NAT": "NATURAL", "UTILS": "UTILITIES", "FMRS": "FARMERS", "MATLS": "MATERIALS",
              "PETE": "PETROLEUM", "INDL": "INDUSTRIAL", "NAV": "NAVIGATION", "INTERNTL": "INTERNATIONAL", "GEN": "GENERAL", "ELEC": "ELECTRIC", "CTRS": "CENTERS", "DEV": "DEVELOPMENT"}


def anleihe(name: str) -> bool:
    return bool(ANLEIHE.search(str(name).upper()))


def bereinigen(name: str) -> str:
    t = str(name).upper().replace("&", " AND ").replace("*", " ")
    t = re.sub(r"[^A-Z0-9 ]+", " ", t)
    t = re.sub(GATTUNG, " ", t)
    t = re.sub(ZUSAETZE, " ", t)
    t = " ".join(ABKUERZUNG.get(w, w) for w in t.split())
    t = re.sub(RECHTSFORM, " ", t)
    woerter = t.split()
    while woerter and len(woerter[-1]) == 1 and len(woerter) > 1:  # „ROYAL CARIBBEAN GROU F“, „… H F“: Auslands-Kennung
        woerter.pop()
    return " ".join(woerter)


def sec_liste() -> pd.DataFrame:
    """kuerzel, titel, cik, schluessel; eine Zeile je CIK (erstes Kürzel = Hauptgattung laut SEC-Reihenfolge)."""
    if not TICKER_DATEI.exists():
        TICKER_DATEI.write_bytes(requests.get(SEC, headers=SEC_HEADER, timeout=60).content)
    d = pd.read_json(TICKER_DATEI, orient="index").rename(columns={"ticker": "kuerzel", "title": "titel", "cik_str": "cik"})
    d["schluessel"] = d["titel"].map(bereinigen)
    return d


def zuordnen(namen: pd.Series, sec: pd.DataFrame) -> pd.Series:
    """Name → Kürzel ("" ohne Treffer). Gattung B/C: Kürzel derselben Firma mit dem Buchstaben, falls vorhanden."""
    je_cik = sec.groupby("cik")["kuerzel"].apply(list).to_dict()
    erstes = sec.drop_duplicates("cik").drop_duplicates("schluessel")
    genau = dict(zip(erstes["schluessel"], erstes["cik"]))
    schluessel = list(genau)
    ergebnis = {}
    def eindeutig(schl):  # Schlüssel nur behalten, wenn er genau eine Firma trifft
        z = pd.Series(list(genau.values()), index=[schl(k) for k in genau])
        z = z.groupby(level=0).agg(lambda x: x.iloc[0] if x.nunique() == 1 else None)
        return z.dropna().to_dict()
    ohne_leer = eindeutig(lambda k: k.replace(" ", ""))   # EXXON MOBIL = EXXONMOBIL
    sortiert = eindeutig(lambda k: " ".join(sorted(k.split())))  # DISNEY WALT = WALT DISNEY
    for name in namen.dropna().unique():
        if anleihe(name):
            ergebnis[name] = ""
            continue
        s = bereinigen(name)
        cik = genau.get(s) or ohne_leer.get(s.replace(" ", "")) or sortiert.get(" ".join(sorted(s.split())))
        if cik is None and len(s) >= 8:  # abgeschnittene Brokernamen („… TECHNOLOGI“, „… COR“): eindeutiger Anfang
            treffer = {genau[k] for k in schluessel if k.startswith(s)}
            if not treffer and len(str(name)) >= 20 and " " in s:
                rest, letztes = s.rsplit(" ", 1)
                treffer = {genau[k] for k in schluessel if k == rest or k.startswith(s)}
            cik = treffer.pop() if len(treffer) == 1 else None
        if cik is None:
            ergebnis[name] = ""
            continue
        kuerzel = je_cik[cik]
        g = re.search(r"\b(?:CLASS|CL|CI)(?: SERIES)? ?([BC])\b", str(name).upper())
        passend = [k for k in kuerzel if g and re.search(rf"[-.]?{g.group(1)}$", k) and len(k) > 1]
        stamm = [k for k in kuerzel if "-" not in k] or kuerzel  # AMH statt Vorzugsaktie AMH-H
        ergebnis[name] = passend[0] if passend else stamm[0]
    return namen.map(ergebnis).fillna("")


ART = {"purchase": "Kauf", "sale": "Verkauf", "partial sale": "Teilverkauf", "exchange": "Tausch"}


def geschaefte() -> pd.DataFrame:
    """daten/trump.csv in der Form der Kongress-Transaktionen (für politiker.politiker), leer ohne Datei."""
    datei = DATEN / "trump.csv"
    if not datei.exists():
        return pd.DataFrame()
    t = pd.read_csv(datei).dropna(subset=["beschreibung"])
    t = t.drop_duplicates(["datei", "nr", "beschreibung", "art", "datum"])  # doppelt gelesene Zeilen (AMENDED: 4)
    t["kuerzel"] = zuordnen(t["beschreibung"], sec_liste())
    return pd.DataFrame({
        "bioguide": "trump", "politiker": "Donald J. Trump", "partei": "Republikaner", "bezirk": "Präsident",
        "kammer": "reg", "doc_id": t["datei"], "jahr": "", "url": t["url"],
        "eingereicht": pd.to_datetime(t["meldedatum"]), "gemeldet": pd.to_datetime(t["meldedatum"]),
        "datum": pd.to_datetime(t["datum"], errors="coerce"), "art": t["art"].map(ART).fillna(t["art"]),
        "kuerzel": t["kuerzel"], "wertpapier": t["beschreibung"],
        "anlageart": ["AN" if anleihe(n) else ("ST" if k else "") for n, k in zip(t["beschreibung"], t["kuerzel"])],
        "betrag_von": t["betrag_von"], "betrag_bis": t["betrag_bis"], "inhaber": "", "status": "",
        "beschreibung": "",
    })


if __name__ == "__main__":
    g = geschaefte()
    aktien = g[g["anlageart"].ne("AN")]
    print(f"{len(g)} Geschäfte, davon Anleihen {g['anlageart'].eq('AN').sum()}, übrige {len(aktien)}, "
          f"mit Kürzel {aktien['kuerzel'].ne('').sum()} ({aktien['kuerzel'].ne('').mean():.0%})")
    offen = aktien[aktien["kuerzel"].eq("")]["wertpapier"].value_counts()
    print(f"Ohne Kürzel: {len(offen)} Namen; häufigste:")
    print(offen.head(40).to_string())
