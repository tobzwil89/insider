"""Staatsaufträge der US-Bundesregierung je Firma (USAspending.gov, amtlich, ohne Schlüssel, frei nutzbar).

    python3 -m pipeline.staatsauftraege [--max-minuten N]
        → daten/staatsauftraege.csv (kuerzel, geschaeftsjahr, betrag)
          daten/staatsauftraege_zuordnung.csv (kuerzel, recipient_id, empfaenger, gesamt, geprueft am)

Zuordnung: Suche nach dem amtlichen Firmennamen (SEC), Kandidaten auf Konzernebene (recipient_level P: fasst alle
Töchter mit derselben Muttergesellschaft zusammen), der mit den meisten Aufträgen zuerst. Treffer nur, wenn die
Namenswörter gleich sind; erlaubt sind Rechtsformen und wenige allgemeine Zusätze (USA, Federal, Services …).
So wird „Apple“ nicht zu „Apple Hospitality REIT“. Abweichende Namen (Alphabet → Google) stehen in NAMEN.
Betrag = Contract Obligations (zugesagte Mittel aus Aufträgen A–D) je US-Geschäftsjahr (Oktober bis September).
"""

import argparse
import re
import sys
import time
import unicodedata

import pandas as pd
import requests

from pipeline import DATEN

B = "https://api.usaspending.gov/api/v2"
ERGEBNIS = DATEN / "staatsauftraege.csv"
ZUORDNUNG = DATEN / "staatsauftraege_zuordnung.csv"
AB_JAHR = 2016
RECHTSFORM = {"inc", "incorporated", "corp", "corporation", "company", "co", "ltd", "limited", "plc", "the", "llc",
              "lp", "sa", "nv", "ag", "se", "holdings", "holding", "group", "class", "a", "b", "c", "de", "and"}
ZUSATZ = {"usa", "us", "america", "americas", "federal", "government", "services", "solutions", "systems",
          "international", "technologies", "technology", "north", "public", "sector"}
# Wo der Behördenname anders lautet als der Firmenname
NAMEN = {"GOOGL": "Google Public Sector", "MMM": "3M Company", "BRK-B": "Berkshire Hathaway",
         "LH": "Laboratory Corporation of America"}
# Von Hand geprüfte Fehltreffer (06.11.2026): gleiche Namenswörter, aber andere Firma
FALSCH = {"MOS": "Mosaic Technologies Group", "PGR": "Progressive Technology Federal Systems",
          "TPR": "Tapestry Technologies"}


def _woerter(name: str) -> set:
    text = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().lower().replace("&", " and ")
    return set(re.findall(r"[a-z0-9]+", text)) - RECHTSFORM


def passt(firma: str, kandidat: str) -> bool:
    f, k = _woerter(firma), _woerter(kandidat)
    return bool(f) and f <= k and (k - f) <= ZUSATZ


def zuordnen(kuerzel: str, name: str, sitzung: requests.Session) -> dict | None:
    if kuerzel in FALSCH:
        return None
    suche = NAMEN.get(kuerzel, name)
    wort = re.sub(r"[^\w&' -]+", " ", re.sub(r"\b(inc|corp|corporation|company|co|ltd|plc|llc|the)\b\.?", "",
                                                 suche, flags=re.I)).strip()
    if len(wort) < 4:  # „3M“ allein findet die Suche nicht, „3M Company“ schon
        wort = suche
    r = sitzung.post(f"{B}/recipient/", timeout=60, json={"keyword": wort,
                                                          "award_type": "contracts", "limit": 30,
                                                          "sort": "amount", "order": "desc"})
    r.raise_for_status()
    for x in r.json().get("results", []):
        if x.get("recipient_level") == "P" and passt(suche, x.get("name", "")):
            return {"recipient_id": x["id"], "empfaenger": x["name"], "gesamt": x.get("amount")}
    return None


def je_jahr(recipient_id: str, sitzung: requests.Session) -> list:
    r = sitzung.post(f"{B}/search/spending_over_time/", timeout=120, json={
        "group": "fiscal_year",
        "filters": {"recipient_id": recipient_id, "award_type_codes": ["A", "B", "C", "D"],
                    "time_period": [{"start_date": f"{AB_JAHR - 1}-10-01",
                                     "end_date": f"{pd.Timestamp.today().year}-09-30"}]}})
    r.raise_for_status()
    return [{"geschaeftsjahr": int(x["time_period"]["fiscal_year"]), "betrag": x.get("Contract_Obligations") or 0}
            for x in r.json().get("results", [])]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-minuten", type=float, default=120)
    args = parser.parse_args()
    ende = time.monotonic() + args.max_minuten * 60
    firmen = pd.read_csv(DATEN / "us_firmen.csv")
    fertig = set(pd.read_csv(ZUORDNUNG)["kuerzel"]) if ZUORDNUNG.exists() else set()
    sitzung = requests.Session()
    neu, gefunden = 0, 0
    for f in firmen.itertuples():
        if f.kuerzel in fertig:
            continue
        if time.monotonic() > ende:
            print("Zeitbudget erreicht, beim nächsten Aufruf geht es weiter")
            break
        try:
            z = zuordnen(f.kuerzel, f.sec_name, sitzung) or (zuordnen(f.kuerzel, f.name, sitzung)
                                                             if f.name != f.sec_name else None)
            jahre = je_jahr(z["recipient_id"], sitzung) if z else []
        except requests.RequestException as fehler:
            print(f"  {f.kuerzel}: fehlgeschlagen ({fehler}), beim nächsten Aufruf erneut")
            continue
        if jahre:
            pd.DataFrame(jahre).assign(kuerzel=f.kuerzel)[["kuerzel", "geschaeftsjahr", "betrag"]].to_csv(
                ERGEBNIS, mode="a", header=not ERGEBNIS.exists(), index=False)
        pd.DataFrame([{"kuerzel": f.kuerzel, "recipient_id": z["recipient_id"] if z else "",
                       "empfaenger": z["empfaenger"] if z else "", "gesamt": z["gesamt"] if z else None,
                       "geprueft": pd.Timestamp.today().strftime("%Y-%m-%d")}]).to_csv(
            ZUORDNUNG, mode="a", header=not ZUORDNUNG.exists(), index=False)
        neu += 1
        gefunden += bool(z)
        time.sleep(0.5)
    print(f"{neu} Firmen geprüft, {gefunden} mit Staatsaufträgen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
