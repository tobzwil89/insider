"""Geschäfte von Donald J. Trump aus den Transaktionsmeldungen (OGE Form 278-T) lesen. Nur lokal (nur macOS).

    python3 trump_laden.py --texte        1. PDFs laden und mit Apple Vision erkennen (kostenlos, ~1 h, setzt fort)
    python3 trump_laden.py --probe 3      2. 3 zufällige Seiten nach .recherche/trump_probe.csv (von Hand prüfen)
    python3 trump_laden.py                3. alle Seiten mit DeepSeek, bis das Guthaben unter 0,05 $ fällt

Die Meldungen stehen bei der OGE (extapps2.oge.gov, Ansicht „President and Vice President Index“, über die
Domino-Schnittstelle ReadViewEntries als JSON). Es sind Scans mit schlechter eingebetteter Texterkennung, deshalb
erkennt ocr.swift (Apple Vision) jede Seite neu und gibt die Position jedes Textstücks aus; hier werden daraus wieder
Tabellenzeilen (gleiche Höhe = gleiche Zeile). Verwechselt werden trotzdem einzelne Ziffern (6/8, $ als S oder 5):
Ein Jahr nach dem Meldedatum wird auf das Meldejahr zurückgesetzt (Spalte datum_korrigiert), der Tag kann um
wenige Tage falsch sein. PDFs in .recherche/trump/, Texte daten/trump_texte.csv, Geschäfte daten/trump.csv.
Rechtlich wie die Kongressdaten (5 U.S.C. app. § 105(c)) → nur lokal, steht in .gitignore.
"""

import argparse
import csv
import io
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

from kongress_altformat import API, MODELL, PARALLEL, REST, _schluessel, guthaben
from pipeline import DATEN

OGE = "https://extapps2.oge.gov"
ANSICHT = OGE + "/201/Presiden.nsf/President%20and%20Vice%20President%20Index?ReadViewEntries&ExpandView&Count=5000&OutputFormat=JSON"
KOPF = {"User-Agent": "Mozilla/5.0 (compatible; Rhodus/1.0; Forschung zu Pflichtmeldungen)"}
PDFS = DATEN.parent / ".recherche" / "trump"
TEXTE = DATEN / "trump_texte.csv"
ERGEBNIS = DATEN / "trump.csv"
OCR = Path(__file__).with_name("ocr.swift")
SPALTEN = ["datei", "url", "meldedatum", "seite", "nr", "beschreibung", "art", "datum", "datum_korrigiert",
           "ueber_30_tage", "betrag_von", "betrag_bis"]

ANWEISUNG = """You read one OCR'd page of a US "OGE Form 278-T" periodic transaction report. Each line is one table row
(columns separated by " | "): row number, description of the asset, transaction type, date, "notification received
over 30 days ago" (yes/no), amount range. A long description may wrap onto its own line above or below its row.
OCR errors are common: "purchaso"/"purchano" = purchase, "S" or "5" in front of an amount = "$", "." used for ",".
Return JSON {"geschaefte": [...]}, one entry per transaction row, with:
- "nr": row number as integer, or null if unreadable
- "beschreibung": asset description, cleaned of obvious OCR noise but otherwise as written
- "art": "purchase", "sale", "partial sale" or "exchange"
- "datum": transaction date as MM/DD/YYYY exactly as read (do not guess a different year)
- "ueber_30_tage": true for yes, false for no, null if unreadable
- "betrag_von", "betrag_bis": amount range as integers in dollars (e.g. $1,001 - $15,000 → 1001, 15000;
  "Over $50,000,000" → 50000000 and null)
Skip the form header, page footers and column headings. Do not invent rows."""


def meldungen() -> list:
    """Transaktionsmeldungen (278-T) von Donald J. Trump: [{datei, url, meldedatum}]."""
    eintraege = requests.get(ANSICHT, headers=KOPF, timeout=60).json()["viewentry"]
    ergebnis = []
    for e in eintraege:
        html = json.dumps(e)
        m = re.search(r"href='(/201/Presiden\.nsf/PAS\+Index/[0-9A-F]{32}/\$FILE/([^']+))'", html)
        if not m or "trump" not in m[2].lower() or not re.search(r"278-?T", m[2], re.I):
            continue
        d = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{2,4})", m[2])
        jahr = int(d[3]) + (2000 if len(d[3]) == 2 else 0)
        ergebnis.append({"datei": m[2], "url": OGE + m[1].replace(" ", "%20"),
                         "meldedatum": pd.Timestamp(jahr, int(d[1]), int(d[2]))})
    return ergebnis


def zeilen(tsv: str) -> dict:
    """Ausgabe von ocr.swift → {seite: Text, eine Tabellenzeile je Zeile, Spalten mit ' | '}."""
    d = pd.read_csv(io.StringIO(tsv), sep="\t", header=None, names=["seite", "y", "x", "h", "text"],
                    quoting=csv.QUOTE_NONE, dtype={"text": str}).dropna(subset=["text"])
    seiten = {}
    for seite, g in d.groupby("seite"):
        reihen, aktuell, y0 = [], [], None
        for r in g.sort_values("y", ascending=False).itertuples():
            if y0 is not None and abs(r.y - y0) > r.h * 0.6:
                reihen.append(aktuell)
                aktuell = []
            if not aktuell:
                y0 = r.y
            aktuell.append(r)
        reihen.append(aktuell)
        seiten[int(seite)] = "\n".join(" | ".join(t.text for t in sorted(z, key=lambda t: t.x)) for z in reihen)
    return seiten


def texte_laden() -> None:
    PDFS.mkdir(parents=True, exist_ok=True)
    da = set(pd.read_csv(TEXTE, usecols=["datei"])["datei"]) if TEXTE.exists() else set()
    liste = meldungen()
    offen = [m for m in liste if m["datei"] not in da]
    print(f"{len(liste)} Meldungen 278-T, {len(offen)} offen", flush=True)
    for m in offen:
        pdf = PDFS / m["datei"].replace("/", "_")
        if not pdf.exists():
            r = requests.get(m["url"], headers=KOPF, timeout=120)
            r.raise_for_status()
            pdf.write_bytes(r.content)
        tsv = subprocess.run(["swift", str(OCR), str(pdf)], capture_output=True, text=True, check=True).stdout
        seiten = zeilen(tsv)
        pd.DataFrame([{**m, "seite": s, "text": t} for s, t in seiten.items()]).to_csv(
            TEXTE, mode="a", header=not TEXTE.exists(), index=False, date_format="%Y-%m-%d")
        print(f"  {m['datei']}: {len(seiten)} Seiten", flush=True)


def datum(text, meldedatum: pd.Timestamp) -> tuple:
    """MM/DD/YYYY → (Datum, korrigiert?). Liegt es nach dem Meldedatum (Ziffer falsch gelesen), gilt das Meldejahr,
    notfalls das Jahr davor."""
    d = pd.to_datetime(text, format="%m/%d/%Y", errors="coerce")
    if pd.isna(d) or d <= meldedatum:
        return d, False
    for jahr in (meldedatum.year, meldedatum.year - 1):
        try:
            neu = d.replace(year=jahr)
        except ValueError:
            continue
        if neu <= meldedatum:
            return neu, True
    return pd.NaT, True


def auslesen(sitzung: requests.Session, text: str) -> tuple[list, int, int]:
    antwort = sitzung.post(f"{API}/chat/completions", timeout=300, json={
        "model": MODELL, "temperature": 0, "response_format": {"type": "json_object"},
        "thinking": {"type": "disabled"}, "max_tokens": 8192,
        "messages": [{"role": "system", "content": ANWEISUNG}, {"role": "user", "content": text}],
    })
    antwort.raise_for_status()
    daten = antwort.json()
    if daten["choices"][0].get("finish_reason") == "length":
        raise ValueError("Antwort abgeschnitten")
    roh = json.loads(daten["choices"][0]["message"]["content"]).get("geschaefte", [])
    return roh, daten["usage"]["prompt_tokens"], daten["usage"]["completion_tokens"]


def _versuch(sitzung, s: dict):
    try:
        return auslesen(sitzung, s["text"])
    except (requests.RequestException, ValueError, KeyError) as fehler:
        print(f"  {s['datei']} Seite {s['seite']}: fehlgeschlagen ({fehler})", flush=True)
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--texte", action="store_true", help="nur PDFs laden und erkennen (kostenlos)")
    parser.add_argument("--probe", type=int, help="N zufällige Seiten nach .recherche/trump_probe.csv")
    args = parser.parse_args()
    if args.texte:
        texte_laden()
        return 0
    seiten = pd.read_csv(TEXTE, parse_dates=["meldedatum"])
    if args.probe:
        seiten, ziel = seiten.sample(args.probe, random_state=1), DATEN.parent / ".recherche/trump_probe.csv"
    else:
        ziel = ERGEBNIS
        if ziel.exists():
            fertig = set(zip(*pd.read_csv(ziel, usecols=["datei", "seite"]).values.T))
            seiten = seiten[[(d, s) not in fertig for d, s in zip(seiten["datei"], seiten["seite"])]]
    sitzung = requests.Session()
    sitzung.headers["Authorization"] = f"Bearer {_schluessel()}"
    start = guthaben(sitzung)
    print(f"Guthaben {start:.2f} $, {len(seiten)} Seiten offen", flush=True)
    ein = aus = 0
    liste = seiten.to_dict("records")
    for von in range(0, len(liste), 40):
        if von and guthaben(sitzung) < REST:
            print(f"Guthaben unter {REST} $, Schluss (nächster Aufruf macht weiter)")
            break
        block = liste[von:von + 40]
        with ThreadPoolExecutor(PARALLEL) as pool:
            ergebnisse = list(pool.map(lambda s: _versuch(sitzung, s), block))
        neu = []
        for s, e in zip(block, ergebnisse):
            if e is None:
                continue
            roh, a, b = e
            ein, aus = ein + a, aus + b
            for g in roh:
                d, korr = datum(g.get("datum"), s["meldedatum"])
                neu.append({"datei": s["datei"], "url": s["url"], "meldedatum": s["meldedatum"], "seite": s["seite"],
                            "nr": g.get("nr"), "beschreibung": g.get("beschreibung"), "art": g.get("art"),
                            "datum": d, "datum_korrigiert": korr, "ueber_30_tage": g.get("ueber_30_tage"),
                            "betrag_von": g.get("betrag_von"), "betrag_bis": g.get("betrag_bis")})
            if not roh:  # leere Seite trotzdem vermerken, damit sie nicht erneut läuft
                neu.append({"datei": s["datei"], "url": s["url"], "meldedatum": s["meldedatum"], "seite": s["seite"]})
        if neu:
            pd.DataFrame(neu).reindex(columns=SPALTEN).to_csv(ziel, mode="a", header=not ziel.exists(), index=False,
                                                              date_format="%Y-%m-%d")
        print(f"{von + len(block)} Seiten, {ein} + {aus} Token", flush=True)
    print(f"Fertig: {ein} Eingabe- + {aus} Ausgabe-Token, Guthaben {guthaben(sitzung):.2f} $ (vorher {start:.2f} $)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
