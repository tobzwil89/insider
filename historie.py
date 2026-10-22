"""Einmaliges Nachladen der Directors' Dealings vor Beginn der BaFin-Daten aus dem EQS-Archiv.

    python3 historie.py                     2018-01-01 bis 2025-10-21, höchstens 320 Minuten
    python3 historie.py --max-minuten 30    in Etappen; ein neuer Aufruf macht dort weiter
    python3 historie.py --reparieren        Käufe/Verkäufe ohne Volumen neu lesen (Leser-Fehler bis 22.10.2026)

Läuft als GitHub Action „Historie laden“. Ergebnis: daten/eqs_historie.csv (eine Zeile je
Geschäft) und daten/eqs_fortschritt.csv (welche Firmen fertig sind). Beides wird nach jeder
Firma gespeichert, ein Abbruch kostet also höchstens eine Firma.
"""

import argparse
import sys
import time

import pandas as pd

from pipeline import DATEN, eqs

ERGEBNIS = DATEN / "eqs_historie.csv"
FORTSCHRITT = DATEN / "eqs_fortschritt.csv"


def reparieren(ende: float) -> int:
    """Meldungen mit Kauf/Verkauf, aber ohne Volumen, neu lesen und ersetzen."""
    h = pd.read_csv(ERGEBNIS, dtype=str, keep_default_na=False)
    kaputt = h.loc[h["art"].isin(["Kauf", "Verkauf"]) & h["volumen"].eq(""), "url"].unique()
    neu, ersetzt = [], set()
    for url in kaputt:
        if time.monotonic() > ende:
            break
        try:
            neu += eqs.meldung_lesen(url)
            ersetzt.add(url)
        except Exception as fehler:
            print(f"  fehlgeschlagen: {url} ({fehler})")
    pd.concat([h[~h["url"].isin(ersetzt)], pd.DataFrame(neu)]).to_csv(ERGEBNIS, index=False)
    print(f"{len(ersetzt)} von {len(kaputt)} Meldungen repariert")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--von", default="2018-01-01")
    parser.add_argument("--bis", default="2025-10-21")
    parser.add_argument("--max-minuten", type=float, default=320)
    parser.add_argument("--reparieren", action="store_true")
    args = parser.parse_args()
    ende = time.monotonic() + args.max_minuten * 60
    if args.reparieren:
        return reparieren(ende)
    von, bis = pd.Timestamp(args.von), pd.Timestamp(args.bis)

    firmen = pd.read_csv(DATEN / "firmen.csv", dtype=str, keep_default_na=False)
    fertig = pd.read_csv(FORTSCHRITT, dtype=str) if FORTSCHRITT.exists() else pd.DataFrame(columns=["name"])
    gelesen = set(pd.read_csv(ERGEBNIS, usecols=["url"])["url"]) if ERGEBNIS.exists() else set()

    # EQS führt Firmen, nicht Aktiengattungen: je Firmenname einmal suchen
    for name, gattungen in firmen.groupby("name", sort=True):
        if name in set(fertig["name"]):
            continue
        if time.monotonic() > ende:
            print("Zeitbudget erreicht, beim nächsten Aufruf geht es weiter")
            return 0
        try:
            uuid = next((u for u in map(eqs.firma_uuid, gattungen["isin"]) if u), None)
            links = eqs.dd_links(uuid, von, bis) if uuid else []
        except eqs.Gedrosselt as fehler:
            print(f"{name}: {fehler}, beim nächsten Aufruf erneut")
            continue
        offen = [(u, t) for u, t in links if u not in gelesen and not eqs.nur_zuteilung(t)]
        zeilen, fehlgeschlagen = [], 0
        for url, _ in offen:
            try:
                zeilen += eqs.meldung_lesen(url)
            except Exception as fehler:  # Firma bleibt offen, der nächste Aufruf holt nur die fehlenden
                fehlgeschlagen += 1
                print(f"  fehlgeschlagen: {url} ({fehler})")
            if time.monotonic() > ende:
                break
        if zeilen:
            neu = pd.DataFrame(zeilen)
            neu.to_csv(ERGEBNIS, mode="a", header=not ERGEBNIS.exists(), index=False)
            gelesen.update(neu["url"])
        if time.monotonic() > ende:
            print(f"Zeitbudget erreicht mitten in {name}, beim nächsten Aufruf geht es weiter")
            return 0
        if fehlgeschlagen:
            print(f"{name}: {fehlgeschlagen} Meldungen fehlgeschlagen, Firma bleibt offen")
            continue
        eintrag = pd.DataFrame([{"name": name, "uuid": uuid or "", "meldungen": len(links),
                                 "geladen": len(offen), "geschaefte": len(zeilen)}])
        eintrag.to_csv(FORTSCHRITT, mode="a", header=not FORTSCHRITT.exists(), index=False)
        fertig = pd.concat([fertig, eintrag])
        print(f"{name}: {len(links)} Meldungen, {len(offen)} gelesen, {len(zeilen)} Geschäfte", flush=True)
    print("Alle Firmen fertig")
    return 0


if __name__ == "__main__":
    sys.exit(main())
