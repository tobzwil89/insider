"""Stimmrechtsmitteilungen aller DAX/MDAX-Firmen seit 2018 aus dem EQS-Archiv laden.

    python3 stimmrechte_laden.py                     ab 2018-01-01 bis heute, höchstens 320 Minuten
    python3 stimmrechte_laden.py --max-minuten 30    in Blöcken; ein neuer Aufruf macht dort weiter
    python3 stimmrechte_laden.py --tage 14           nur die letzten 14 Tage, alle Firmen (täglicher Lauf)
    python3 stimmrechte_laden.py --alt               Archiv vor 2018; Fließtexte zusätzlich nach stimmrechte_texte.csv

Läuft als GitHub Action „Stimmrechte laden“ (kann jederzeit abgebrochen werden). Ergebnis:
daten/stimmrechte.csv (eine Zeile je Mitteilung) und daten/stimmrechte_fortschritt.csv (welche
Firmen fertig sind). Beides wird nach jeder Firma gespeichert, ein Abbruch kostet höchstens eine Firma.
Am Ende jedes Aufrufs: Mitteilungen über eigene Aktien (ab 2018) nach daten/stimmrechte_eigene_aktien.csv (nur fehlende).
"""

import argparse
import sys
import time

import pandas as pd

from pipeline import DATEN, eqs, stimmrechte

ERGEBNIS = DATEN / "stimmrechte.csv"
FORTSCHRITT = DATEN / "stimmrechte_fortschritt.csv"
FORTSCHRITT_ALT = DATEN / "stimmrechte_alt_fortschritt.csv"
TEXTE = DATEN / "stimmrechte_texte.csv"
EIGENE = DATEN / "stimmrechte_eigene_aktien.csv"
SPALTEN = ["firma", "isin", "veroeffentlicht", "schwellendatum", "meldepflichtiger", "sitz",
           "aktien", "instrumente", "summe", "aktien_vorher", "instrumente_vorher", "summe_vorher",
           "gesamtstimmrechte", "korrektur", "formular", "url"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--von", default="2018-01-01")
    parser.add_argument("--max-minuten", type=float, default=320)
    parser.add_argument("--firmen", nargs="*", help="nur diese Firmennamen (zum Testen)")
    parser.add_argument("--tage", type=int, help="nur neue Mitteilungen der letzten N Tage, Fortschritt bleibt unberührt")
    parser.add_argument("--alt", action="store_true", help="Mitteilungen vor 2018 (eigene Fortschrittsliste)")
    args = parser.parse_args()
    ende = time.monotonic() + args.max_minuten * 60
    von = pd.Timestamp.today().normalize() - pd.Timedelta(days=args.tage) if args.tage else pd.Timestamp(args.von)
    bis = None
    fortschritt = FORTSCHRITT
    if args.alt:
        von, bis, fortschritt = pd.Timestamp("2000-01-01"), pd.Timestamp("2017-12-31"), FORTSCHRITT_ALT

    firmen = pd.read_csv(DATEN / "firmen.csv", dtype=str, keep_default_na=False)
    if args.firmen:
        firmen = firmen[firmen["name"].isin(args.firmen)]
    fertig = set(pd.read_csv(fortschritt, dtype=str)["name"]) if fortschritt.exists() and not args.tage else set()
    gelesen = set(pd.read_csv(ERGEBNIS, usecols=["url"])["url"]) if ERGEBNIS.exists() else set()
    # EQS-IDs aus der Directors'-Dealings-Historie wiederverwenden, das spart die Suche
    bekannt = pd.read_csv(DATEN / "eqs_fortschritt.csv", dtype=str, keep_default_na=False)
    bekannt = dict(zip(bekannt["name"], bekannt["uuid"]))

    offen_firmen = []
    for name, gattungen in firmen.groupby("name", sort=True):
        if name in fertig:
            continue
        if time.monotonic() > ende:
            print("Zeitbudget erreicht, beim nächsten Aufruf geht es weiter")
            return 0
        try:
            uuid = bekannt.get(name) or next((u for u in map(eqs.firma_uuid, gattungen["isin"]) if u), None)
            links = eqs.dd_links(uuid, von, bis, kategorie=stimmrechte.KATEGORIE) if uuid else []
        except eqs.Gedrosselt as fehler:
            print(f"{name}: {fehler}, beim nächsten Aufruf erneut")
            offen_firmen.append(name)
            continue
        offen = [u for u, _ in links if u not in gelesen]
        zeilen, fehlgeschlagen = [], 0
        for url in offen:
            try:
                zeilen.append(dict(stimmrechte.lesen(url), firma=name, isin=gattungen["isin"].iloc[0]))
            except Exception as fehler:  # Firma bleibt offen, der nächste Aufruf holt nur die fehlenden
                fehlgeschlagen += 1
                print(f"  fehlgeschlagen: {url} ({fehler})")
            if time.monotonic() > ende:
                break
        if zeilen:
            neu = pd.DataFrame(zeilen).reindex(columns=SPALTEN)
            neu.to_csv(ERGEBNIS, mode="a", header=not ERGEBNIS.exists(), index=False)
            gelesen.update(neu["url"])
            texte = [z for z in zeilen if z.get("text")]
            if args.alt and texte:
                pd.DataFrame(texte)[["url", "firma", "isin", "veroeffentlicht", "text"]] \
                    .to_csv(TEXTE, mode="a", header=not TEXTE.exists(), index=False)
        if time.monotonic() > ende:
            print(f"Zeitbudget erreicht mitten in {name}, beim nächsten Aufruf geht es weiter")
            return 0
        if fehlgeschlagen:
            print(f"{name}: {fehlgeschlagen} Mitteilungen fehlgeschlagen, Firma bleibt offen")
            offen_firmen.append(name)
            continue
        if args.tage:
            if offen:
                print(f"{name}: {len(offen)} neue Mitteilungen", flush=True)
            continue
        pd.DataFrame([{"name": name, "uuid": uuid or "", "mitteilungen": len(links), "geladen": len(offen)}]) \
            .to_csv(fortschritt, mode="a", header=not fortschritt.exists(), index=False)
        fertig.add(name)
        print(f"{name}: {len(links)} Mitteilungen, {len(offen)} gelesen", flush=True)
    if offen_firmen:
        print(f"Noch offen ({len(offen_firmen)}): {', '.join(offen_firmen)}; beim nächsten Aufruf erneut")
    else:
        print("Alle Firmen fertig")
    return 0


def eigene_aktien_nachladen() -> None:
    """Mitteilungen über eigene Aktien (ab 2018) aus stimmrechte.csv lesen, die noch nicht in EIGENE stehen."""
    st = pd.read_csv(ERGEBNIS, usecols=["firma", "veroeffentlicht", "formular", "url"])
    kandidaten = st[st["formular"].eq("anderes") & st["veroeffentlicht"].ge("2018")
                    & st["url"].str.contains(stimmrechte.EIGENE_URL, case=False, na=False)]
    gelesen = set(pd.read_csv(EIGENE, usecols=["url"])["url"]) if EIGENE.exists() else set()
    zeilen = []
    for r in kandidaten[~kandidaten["url"].isin(gelesen)].itertuples():
        try:
            zeilen.append(dict(stimmrechte.eigene_aktien_lesen(r.url), firma=r.firma, veroeffentlicht=r.veroeffentlicht))
        except Exception as fehler:  # beim nächsten Lauf erneut
            print(f"  eigene Aktien fehlgeschlagen: {r.url} ({fehler})")
    if zeilen:
        pd.DataFrame(zeilen)[["firma", "veroeffentlicht", "schwellendatum", "anteil", "anteil_vorher", "gesamt", "url"]] \
            .to_csv(EIGENE, mode="a", header=not EIGENE.exists(), index=False)
    print(f"Eigene Aktien: {len(zeilen)} Mitteilungen neu gelesen")


if __name__ == "__main__":
    ergebnis = main()
    eigene_aktien_nachladen()
    sys.exit(ergebnis)
