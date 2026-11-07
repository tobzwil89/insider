"""Geschäfte von Donald J. Trump aus den Transaktionsmeldungen (OGE Form 278-T) lesen. Nur lokal, nur macOS.

    python3 trump_laden.py --bilder              1. PDFs laden, jede Seite als JPEG (kostenlos, setzt fort)
    python3 trump_laden.py --probe 3             2. 3 zufällige Seiten nach .recherche/trump_probe_<modell>.csv
    python3 trump_laden.py                       3. alle Seiten (setzt fort), höchstens BUDGET $
    python3 trump_laden.py --modell glm-4.6v-flash   kostenloses Modell (nur eine Anfrage gleichzeitig, langsam)

Die Meldungen stehen bei der OGE (extapps2.oge.gov, Ansicht „President and Vice President Index“, über die
Domino-Schnittstelle ReadViewEntries als JSON). Es sind Scans. Texterkennung (eingebettet oder Apple Vision) verliert
ganze Spalten (07.11.2026 gemessen: Art nur in 60 %, Datum in 75 % der Zeilen), ein Textmodell rät dann. Deshalb liest
ein Bild-Sprachmodell von z.AI (GLM-4.6V) jede Seite direkt. Ein Jahr nach dem Meldedatum wird auf das Meldejahr
zurückgesetzt (Spalte datum_korrigiert). PDFs in .recherche/trump/, Seitenbilder in .recherche/trump_bilder/, Liste
daten/trump_seiten.csv, Geschäfte daten/trump.csv. Schlüssel: ZAI_API_KEY (Umgebung oder .env).
Rechtlich wie die Kongressdaten (5 U.S.C. § 13107(c)) → nur lokal, steht in .gitignore.
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

from pipeline import DATEN

API = "https://api.z.ai/api/paas/v4"
# Preise $ je Mio. Token (Eingabe, Ausgabe) laut docs.z.ai, Stand 07.11.2026
PREISE = {"glm-4.6v-flash": (0, 0), "glm-4.6v-flashx": (0.04, 0.4), "glm-4.6v": (0.3, 0.9)}
MODELL = "glm-4.6v-flashx"
BUDGET = 1.0  # $; z.AI zeigt kein Guthaben per Schnittstelle → aus den gezählten Token rechnen und hier aufhören
# gleichzeitige Anfragen: kostenloses Modell nur 1; FlashX bei 4 rund 20 % Fehler (429, Abbrüche), daher 2
PARALLEL = {"glm-4.6v-flash": 1, "glm-4.6v-flashx": 2}
ARTEN = {"purchase", "sale", "partial sale", "exchange"}

OGE = "https://extapps2.oge.gov"
ANSICHT = OGE + "/201/Presiden.nsf/President%20and%20Vice%20President%20Index?ReadViewEntries&ExpandView&Count=5000&OutputFormat=JSON"
KOPF = {"User-Agent": "Mozilla/5.0 (compatible; Rhodus/1.0; Forschung zu Pflichtmeldungen)"}
PDFS = DATEN.parent / ".recherche" / "trump"
BILDER = DATEN.parent / ".recherche" / "trump_bilder"
SEITEN = DATEN / "trump_seiten.csv"
ERGEBNIS = DATEN / "trump.csv"
SEITENBILDER = Path(__file__).with_name("seitenbilder.swift")
SPALTEN = ["datei", "url", "meldedatum", "seite", "nr", "beschreibung", "art", "datum", "datum_korrigiert",
           "ueber_30_tage", "betrag_von", "betrag_bis"]

ANWEISUNG = """This image is one page of a US "OGE Form 278-T" periodic transaction report. Read the transactions table:
columns # (row number), Description, Type, Date, Notification Received Over 30 Days Ago (yes/no), Amount.
Return only JSON {"geschaefte": [...]}, one entry per table row, in order, with:
- "nr": row number as integer
- "beschreibung": the description exactly as printed
- "art": "purchase", "sale", "partial sale" or "exchange", as printed in the Type column
- "datum": the date exactly as printed, MM/DD/YYYY
- "ueber_30_tage": true for yes, false for no
- "betrag_von", "betrag_bis": amount range as integers in dollars (e.g. $1,001 - $15,000 → 1001, 15000;
  "Over $50,000,000" → 50000000 and null)
If a cell is empty or unreadable, use null. Never copy a value from another row. If the page has no transactions
table (cover page, signatures), return {"geschaefte": []}."""


def _schluessel() -> str:
    """ZAI_API_KEY aus der Umgebung, sonst aus .env."""
    if os.environ.get("ZAI_API_KEY"):
        return os.environ["ZAI_API_KEY"]
    return next(z.split("=", 1)[1].strip().strip("\"'") for z in open(".env") if z.startswith("ZAI_API_KEY"))


def kosten(modell: str, ein: int, aus: int) -> float:
    p_ein, p_aus = PREISE.get(modell, (1.4, 4.4))  # unbekanntes Modell: hoher Preis, damit das Budget hält
    return (ein * p_ein + aus * p_aus) / 1e6


def meldungen() -> list:
    """Transaktionsmeldungen (278-T) von Donald J. Trump: [{datei, url, meldedatum}]."""
    eintraege = requests.get(ANSICHT, headers=KOPF, timeout=60).json()["viewentry"]
    ergebnis = []
    for e in eintraege:
        m = re.search(r"href='(/201/Presiden\.nsf/PAS\+Index/[0-9A-F]{32}/\$FILE/([^']+))'", json.dumps(e))
        if not m or "trump" not in m[2].lower() or not re.search(r"278-?T", m[2], re.I):
            continue
        d = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{2,4})", m[2])
        jahr = int(d[3]) + (2000 if len(d[3]) == 2 else 0)
        ergebnis.append({"datei": m[2], "url": OGE + m[1].replace(" ", "%20"),
                         "meldedatum": pd.Timestamp(jahr, int(d[1]), int(d[2]))})
    return ergebnis


def bilder_laden() -> None:
    """Jede Meldung als PDF laden und jede Seite als JPEG speichern; Liste der Seiten nach daten/trump_seiten.csv."""
    PDFS.mkdir(parents=True, exist_ok=True)
    da = set(pd.read_csv(SEITEN, usecols=["datei"])["datei"]) if SEITEN.exists() else set()
    liste = meldungen()
    offen = [m for m in liste if m["datei"] not in da]
    print(f"{len(liste)} Meldungen 278-T, {len(offen)} offen", flush=True)
    for i, m in enumerate(liste):
        if m not in offen:
            continue
        name = m["datei"].replace("/", "_")
        pdf = PDFS / name
        if not pdf.exists():
            r = requests.get(m["url"], headers=KOPF, timeout=120)
            r.raise_for_status()
            pdf.write_bytes(r.content)
        ordner = BILDER / Path(name).stem
        anzahl = int(subprocess.run(["swift", str(SEITENBILDER), str(pdf), str(ordner)], capture_output=True,
                                    text=True, check=True).stdout.strip())
        pd.DataFrame([{**m, "seite": s, "bild": str((ordner / f"{s}.jpg").relative_to(DATEN.parent))}
                      for s in range(1, anzahl + 1)]).to_csv(SEITEN, mode="a", header=not SEITEN.exists(),
                                                              index=False, date_format="%Y-%m-%d")
        print(f"  {m['datei']}: {anzahl} Seiten", flush=True)


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


def _json(text: str) -> dict:
    """JSON aus der Antwort, auch wenn das Modell es in ```json … ``` einpackt oder nur die Liste schickt."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        daten = json.loads(text)
    except ValueError:
        # Selten baut das Modell eine kaputte Hülle um saubere Zeilen ({"geschaften": [{…}], {…}, …) →
        # die einzelnen Zeilenobjekte direkt lesen
        zeilen = [json.loads(z) for z in re.findall(r"\{[^{}]*\}", text) if '"nr"' in z]
        if not zeilen:
            raise
        return {"geschaefte": zeilen}
    return {"geschaefte": daten} if isinstance(daten, list) else daten


def auslesen(sitzung: requests.Session, bild: Path, modell: str) -> tuple[list, int, int]:
    daten_url = "data:image/jpeg;base64," + base64.b64encode(bild.read_bytes()).decode()
    for versuch in range(5):
        antwort = sitzung.post(f"{API}/chat/completions", timeout=600, json={
            "model": modell, "temperature": 0, "thinking": {"type": "disabled"}, "max_tokens": 16384,
            "messages": [{"role": "user", "content": [{"type": "image_url", "image_url": {"url": daten_url}},
                                                      {"type": "text", "text": ANWEISUNG}]}],
        })
        if antwort.status_code != 429:  # zu viele gleichzeitige Anfragen: warten, neu versuchen
            break
        time.sleep(20 * (versuch + 1))
    antwort.raise_for_status()
    daten = antwort.json()
    if daten["choices"][0].get("finish_reason") == "length":
        raise ValueError("Antwort abgeschnitten")
    roh = _json(daten["choices"][0]["message"]["content"]).get("geschaefte", [])
    return roh, daten["usage"]["prompt_tokens"], daten["usage"]["completion_tokens"]


def _versuch(sitzung, s: dict, modell: str):
    """Bis zu drei Versuche: Das Modell liefert manchmal kaputtes JSON oder bricht ab, beim nächsten Mal meist nicht."""
    for versuch in range(3):
        try:
            return auslesen(sitzung, DATEN.parent / s["bild"], modell)
        except (requests.RequestException, ValueError, KeyError) as fehler:
            letzter = fehler
    print(f"  {s['datei']} Seite {s['seite']}: fehlgeschlagen ({letzter})", flush=True)
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bilder", action="store_true", help="nur PDFs laden und Seitenbilder erzeugen (kostenlos)")
    parser.add_argument("--probe", type=int, help="N zufällige Seiten nach .recherche/trump_probe_<modell>.csv")
    parser.add_argument("--seiten", nargs="*", default=[], help="nur diese Seiten (Datei:Seite), für Prüfungen")
    parser.add_argument("--modell", default=MODELL, help=f"z.AI-Modell, Standard {MODELL}")
    args = parser.parse_args()
    if args.bilder:
        bilder_laden()
        return 0
    seiten = pd.read_csv(SEITEN, parse_dates=["meldedatum"])
    if args.probe or args.seiten:
        ziel = DATEN.parent / f".recherche/trump_probe_{args.modell}.csv"
        if args.seiten:
            wahl = {tuple(x.rsplit(":", 1)) for x in args.seiten}
            seiten = seiten[[(d, str(s)) in wahl for d, s in zip(seiten["datei"], seiten["seite"])]]
        else:
            seiten = seiten[seiten["seite"] > 1].sample(args.probe, random_state=1)  # Seite 1 = Deckblatt
    else:
        ziel = ERGEBNIS
        if ziel.exists():
            fertig = set(zip(*pd.read_csv(ziel, usecols=["datei", "seite"]).values.T))
            seiten = seiten[[(d, s) not in fertig for d, s in zip(seiten["datei"], seiten["seite"])]]
    sitzung = requests.Session()
    sitzung.headers["Authorization"] = f"Bearer {_schluessel()}"
    print(f"Modell {args.modell}, {len(seiten)} Seiten offen, Budget {BUDGET} $", flush=True)
    ein = aus = 0
    liste = seiten.to_dict("records")
    for von in range(0, len(liste), 20):
        if kosten(args.modell, ein, aus) > BUDGET:
            print(f"Budget {BUDGET} $ erreicht, Schluss (nächster Aufruf macht weiter)")
            break
        block = liste[von:von + 20]
        with ThreadPoolExecutor(PARALLEL.get(args.modell, 4)) as pool:
            ergebnisse = list(pool.map(lambda s: _versuch(sitzung, s, args.modell), block))
        neu = []
        for s, e in zip(block, ergebnisse):
            if e is None:
                continue
            roh, a, b = e
            ein, aus = ein + a, aus + b
            for g in roh:  # Modell schreibt teils „Purchase“
                g["art"] = str(g["art"]).strip().lower() if g.get("art") else None
            roh = [g for g in roh if g.get("art") in ARTEN or g.get("nr") is not None]
            for g in roh:
                d, korr = datum(g.get("datum"), s["meldedatum"])
                neu.append({"datei": s["datei"], "url": s["url"], "meldedatum": s["meldedatum"], "seite": s["seite"],
                            "nr": g.get("nr"), "beschreibung": g.get("beschreibung"), "art": g.get("art"),
                            "datum": d, "datum_korrigiert": korr, "ueber_30_tage": g.get("ueber_30_tage"),
                            "betrag_von": g.get("betrag_von"), "betrag_bis": g.get("betrag_bis")})
            if not roh:  # Seite ohne Geschäfte trotzdem vermerken, damit sie nicht erneut läuft
                neu.append({"datei": s["datei"], "url": s["url"], "meldedatum": s["meldedatum"], "seite": s["seite"]})
        if neu:
            pd.DataFrame(neu).reindex(columns=SPALTEN).to_csv(ziel, mode="a", header=not ziel.exists(), index=False,
                                                              date_format="%Y-%m-%d")
        print(f"{von + len(block)} Seiten, {ein} + {aus} Token, ~{kosten(args.modell, ein, aus):.2f} $", flush=True)
    print(f"Fertig: {ein} Eingabe- + {aus} Ausgabe-Token, ~{kosten(args.modell, ein, aus):.2f} $")
    return 0


if __name__ == "__main__":
    sys.exit(main())
