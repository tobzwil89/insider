"""Aktiengeschäfte der US-Abgeordneten (Repräsentantenhaus, STOCK Act) laden: pipeline/kongress.py.

    python3 kongress_laden.py                       alle Jahre ab 2014, höchstens 320 Minuten
    python3 kongress_laden.py --jahre 2026          nur dieses Jahr (nächtlicher Lauf: aktuelles und Vorjahr)
    python3 kongress_laden.py --max-minuten 30      in Blöcken; ein neuer Aufruf macht dort weiter

Liest jede Meldung (PTR) nur einmal; welche schon gelesen sind, steht in daten/kongress_fortschritt.csv
(status ok / scan / leer). Ergebnis: daten/kongress.csv, eine Zeile je Transaktion. Gespeichert wird alle 25 Meldungen,
ein Abbruch verliert also höchstens diese. Fehlgeschlagene Abrufe bleiben offen und werden beim nächsten Mal versucht.
"""

import argparse
import sys
import time

import pandas as pd
import requests

from pipeline import DATEN, kongress

ERGEBNIS = DATEN / "kongress.csv"
FORTSCHRITT = DATEN / "kongress_fortschritt.csv"
MELDUNG = ["doc_id", "jahr", "name", "nachname", "vorname", "bezirk", "eingereicht"]
SPALTEN = MELDUNG + ["inhaber", "wertpapier", "kuerzel", "anlageart", "art", "datum", "gemeldet", "betrag_von",
                     "betrag_bis", "status", "unterkonto", "beschreibung", "kommentar"]
PAUSE = 0.3  # Sekunden zwischen zwei PDFs (der Server ist schnell, aber höflich bleiben)


def _speichern(transaktionen: list, meldungen: list) -> None:
    if transaktionen:
        pd.DataFrame(transaktionen).reindex(columns=SPALTEN).to_csv(
            ERGEBNIS, mode="a", header=not ERGEBNIS.exists(), index=False, date_format="%Y-%m-%d")
    if meldungen:
        pd.DataFrame(meldungen).to_csv(FORTSCHRITT, mode="a", header=not FORTSCHRITT.exists(), index=False,
                                       date_format="%Y-%m-%d")


def main() -> int:
    parser = argparse.ArgumentParser()
    heute = pd.Timestamp.today()
    parser.add_argument("--jahre", nargs="*", type=int, default=list(range(2014, heute.year + 1)))
    parser.add_argument("--max-minuten", type=float, default=320)
    args = parser.parse_args()
    ende = time.monotonic() + args.max_minuten * 60

    fertig = set(pd.read_csv(FORTSCHRITT, dtype=str)["doc_id"]) if FORTSCHRITT.exists() else set()
    sitzung = requests.Session()
    neu_t, neu_m, fehler, gelesen = [], [], 0, 0
    for jahr in sorted(args.jahre, reverse=True):  # neueste zuerst
        try:
            liste = kongress.verzeichnis(jahr)
        except Exception as e:
            print(f"{jahr}: Verzeichnis nicht abrufbar ({e})")
            fehler += 1
            continue
        offen = liste[~liste["doc_id"].isin(fertig)]
        print(f"{jahr}: {len(liste)} Meldungen, davon {len(offen)} neu", flush=True)
        for m in offen.to_dict("records"):
            if time.monotonic() > ende:
                _speichern(neu_t, neu_m)
                print(f"Zeitbudget erreicht nach {gelesen} Meldungen, beim nächsten Aufruf geht es weiter")
                return 0
            try:
                status, t = kongress.lesen(jahr, m["doc_id"], sitzung)
            except Exception as e:
                print(f"  {m['doc_id']} ({m['name']}): fehlgeschlagen ({e})")
                fehler += 1
                continue
            neu_t += [{**{k: m[k] for k in MELDUNG}, **x} for x in t]
            neu_m.append({**{k: m[k] for k in MELDUNG}, "status": status, "transaktionen": len(t),
                          "geladen": heute.strftime("%Y-%m-%d")})
            fertig.add(m["doc_id"])
            gelesen += 1
            if len(neu_m) >= 25:
                _speichern(neu_t, neu_m)
                neu_t, neu_m = [], []
            if status != "scan":
                time.sleep(PAUSE)
    _speichern(neu_t, neu_m)
    print(f"Fertig: {gelesen} Meldungen gelesen" + (f", {fehler} fehlgeschlagen (beim nächsten Aufruf erneut)" if fehler else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
