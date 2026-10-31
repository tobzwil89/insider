"""Firmenlogos einmal herunterladen und lokal unter docs/logos/<ISIN>.<svg|png> speichern.

    python3 logos_laden.py          nur fehlende Logos laden
    python3 logos_laden.py --neu    alle neu laden (z. B. nach Logo-Wechsel bei Wikidata)

Quelle: Wikidata (ISIN = P946, Logo = P154), Datei von Wikimedia Commons.
Vorrang hat daten/logos_hand.csv (isin,url) für Firmen ohne oder mit falschem Logo bei Wikidata.
Ergebnis: daten/logos.csv (isin, name, datei, quelle) und logos_uebersicht.html zum Durchsehen.
"""

import argparse
import csv
import html
import time
from pathlib import Path

import requests

ORDNER = Path(__file__).parent
FIRMEN = ORDNER / "daten" / "firmen.csv"
HAND = ORDNER / "daten" / "logos_hand.csv"
LISTE = ORDNER / "daten" / "logos.csv"
LOGOS = ORDNER / "docs" / "logos"
UEBERSICHT = ORDNER / "logos_uebersicht.html"
KOPF = {"User-Agent": "Rhodus-Logos/1.0 (https://insider.tobiaszwilling.me)"}


def lies_csv(pfad):
    if not pfad.exists():
        return []
    with open(pfad, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def wikidata_logos(isins):
    """ISIN → Liste der Logo-Adressen (meist eine, manchmal mehrere)."""
    werte = " ".join(f'"{i}"' for i in isins)
    abfrage = f"SELECT ?isin ?logo WHERE {{ VALUES ?isin {{ {werte} }} ?f wdt:P946 ?isin . ?f wdt:P154 ?logo . }}"
    antwort = requests.get("https://query.wikidata.org/sparql", params={"query": abfrage, "format": "json"},
                           headers=KOPF, timeout=60)
    antwort.raise_for_status()
    logos = {}
    for zeile in antwort.json()["results"]["bindings"]:
        url = zeile["logo"]["value"].replace("http://", "https://")
        logos.setdefault(zeile["isin"]["value"], [])
        if url not in logos[zeile["isin"]["value"]]:
            logos[zeile["isin"]["value"]].append(url)
    return logos


def endung(url, inhalt):
    if inhalt.lstrip()[:5] in (b"<?xml", b"<svg ") or url.lower().endswith(".svg"):
        return "svg"
    if inhalt[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if inhalt[:3] == b"\xff\xd8\xff":
        return "jpg"
    return None


def lade(url):
    for versuch in range(3):
        antwort = requests.get(url, headers=KOPF, timeout=60)
        if antwort.status_code == 429:  # Wikimedia drosselt: kurz warten
            time.sleep(5 * (versuch + 1))
            continue
        antwort.raise_for_status()
        return antwort.content
    raise RuntimeError("zu viele Anfragen (429)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--neu", action="store_true", help="alle Logos neu laden")
    args = parser.parse_args()

    firmen = lies_csv(FIRMEN)
    hand = {z["isin"]: z["url"] for z in lies_csv(HAND)}
    wiki = wikidata_logos([f["isin"] for f in firmen])
    alt = {z["isin"]: z for z in lies_csv(LISTE)}
    LOGOS.mkdir(parents=True, exist_ok=True)

    ergebnis = []
    for firma in firmen:
        isin, name = firma["isin"], firma["name"]
        if isin in hand:
            url, quelle = hand[isin], "Hand"
        elif isin in wiki:
            url, quelle = wiki[isin][0], "Wikidata" + (f" (1 von {len(wiki[isin])})" if len(wiki[isin]) > 1 else "")
        else:
            ergebnis.append({"isin": isin, "name": name, "datei": "", "quelle": "fehlt"})
            continue

        vorher = alt.get(isin)
        if not args.neu and vorher and vorher["datei"] and (LOGOS / vorher["datei"]).exists() and vorher["url"] == url:
            ergebnis.append(vorher)
            continue
        try:
            inhalt = lade(url)
            art = endung(url, inhalt)
            if not art:
                raise RuntimeError("weder SVG noch PNG/JPG")
            for f in LOGOS.glob(f"{isin}.*"):
                f.unlink()  # alte Version mit anderer Endung entfernen
            (LOGOS / f"{isin}.{art}").write_bytes(inhalt)
            ergebnis.append({"isin": isin, "name": name, "datei": f"{isin}.{art}", "quelle": quelle, "url": url})
            print(f"ok     {name}")
        except Exception as fehler:
            print(f"FEHLER {name}: {fehler}")
            ergebnis.append({"isin": isin, "name": name, "datei": "", "quelle": f"Fehler: {fehler}", "url": url})
        time.sleep(0.5)

    with open(LISTE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["isin", "name", "datei", "quelle", "url"])
        w.writeheader()
        for z in ergebnis:
            w.writerow({k: z.get(k, "") for k in w.fieldnames})

    schreibe_uebersicht(ergebnis)
    fehlen = [z["name"] for z in ergebnis if not z["datei"]]
    print(f"\n{len(ergebnis) - len(fehlen)} von {len(ergebnis)} Firmen mit Logo.")
    if fehlen:
        print(f"Ohne Logo ({len(fehlen)}): " + ", ".join(fehlen))
        print(f"→ in {HAND.name} eintragen (isin,url) und erneut starten.")


def schreibe_uebersicht(ergebnis):
    kacheln = []
    for z in sorted(ergebnis, key=lambda z: (bool(z["datei"]), z["name"].lower())):
        bild = (f'<img src="docs/logos/{html.escape(z["datei"])}" alt="">' if z["datei"]
                else '<div class="leer">kein Logo</div>')
        kacheln.append(f'<figure>{bild}<figcaption><b>{html.escape(z["name"])}</b><br>'
                       f'{html.escape(z["isin"])} · {html.escape(z["quelle"])}</figcaption></figure>')
    UEBERSICHT.write_text(f"""<!doctype html><meta charset="utf-8"><title>Logos prüfen</title>
<style>
body{{font:14px system-ui;margin:24px;background:#f3eee2;color:#1e3b2f}}
.raster{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}}
figure{{margin:0;background:#fff;border-radius:8px;padding:12px;text-align:center}}
img,.leer{{height:60px;max-width:100%;object-fit:contain;display:block;margin:8px auto 12px}}
.leer{{line-height:60px;color:#b00;border:1px dashed #b00}}
figcaption{{font-size:12px;color:#555}}
</style>
<h1>Logos prüfen ({sum(1 for z in ergebnis if z["datei"])} von {len(ergebnis)})</h1>
<p>Fehlende zuerst. Falsches oder veraltetes Logo: Adresse in daten/logos_hand.csv eintragen.</p>
<div class="raster">{''.join(kacheln)}</div>
""", encoding="utf-8")


if __name__ == "__main__":
    main()
