"""Meldungen des Repräsentantenhauses im älteren Formular (2014 bis Mitte 2022) mit DeepSeek auslesen.

    python3 kongress_altformat.py --texte          1. PDF-Texte laden (kostenlos, ~1 h, setzt fort)
    python3 kongress_altformat.py --probe 30       2. 30 zufällige Meldungen nach .recherche/ (von Hand prüfen)
    python3 kongress_altformat.py                  3. alle, neueste zuerst, bis das Guthaben unter 0,05 $ fällt

Das ältere Formular zerlegt die Marken („F ILING S TATUS“), setzt Kästchen als „fedcb“ und schreibt Unterkonto und
nächstes Wertpapier in eine Zeile; der Regelleser in pipeline/kongress.py gibt dafür status `alt` (siehe
daten/kongress_fortschritt.csv). Hier liest DeepSeek je Meldung die Rohfelder, die Umwandlung (Art, Inhaber, Betrag,
Datum) macht derselbe Code wie beim neuen Formular. Ergebnis: daten/kongress_alt.csv (Spalten wie kongress.csv),
erledigte Meldungen in daten/kongress_alt_fortschritt.csv. Schlüssel: DEEPSEEK_API_KEY in .env.
"""

import argparse
import io
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import pypdf
import requests

from kongress_laden import MELDUNG, SPALTEN
from pipeline import DATEN, kongress

TEXTE = DATEN / "kongress_alt_texte.csv"
ERGEBNIS = DATEN / "kongress_alt.csv"
FERTIG = DATEN / "kongress_alt_fortschritt.csv"
API = "https://api.deepseek.com"
MODELL = "deepseek-flash"
REST = 0.05  # $; darunter wird aufgehört
PARALLEL = 8
BLOCK = 80  # Meldungen je Block; danach speichern und Guthaben prüfen
STUECK = 12000  # Zeichen je Anfrage (~35 Geschäfte); längere Meldungen gehen seitenweise in mehreren Anfragen
SEITE = "\n\f\n"  # Seitentrenner im gespeicherten Text

ANWEISUNG = """You read the extracted text of a US House "Periodic Transaction Report" (old PDF layout). The text is
garbled: labels are split ("F ILING S TATUS", "S UbHoLDING o F", "D eSCrIPTION", "C OMMeNTS"), checkboxes appear as
"fedcb"/"gfedc", and a SUBHOLDING OF value often runs straight into the next asset name on the same line.
Each transaction has: an optional owner code (SP, JT or DC) placed directly BEFORE the asset name (it may stand at the
end of the previous line), the asset name with ticker in parentheses and asset type in brackets like [ST],
the transaction type (P, S, S (partial) or E), transaction date, notification date, and an amount range.
Return JSON {"transaktionen": [...]}, one entry per transaction in document order, with the fields:
- "owner": "SP", "JT", "DC" or "" if none
- "asset": full asset name including the ticker in parentheses, without the [XX] code and without any subholding text
- "ticker": ticker without parentheses, or ""
- "asset_type": the two-letter code in brackets, or ""
- "type": "P", "S", "S (partial)" or "E"
- "date": transaction date as MM/DD/YYYY
- "notification_date": as MM/DD/YYYY
- "amount": amount exactly as written, e.g. "$1,001 - $15,000" or "Over $50,000,000"
- "filing_status": "New", "Amended" or "Deleted" (value after FILING STATUS), or ""
- "subholding": value after SUBHOLDING OF, or ""
- "description": value after DESCRIPTION, or ""
- "comments": value after COMMENTS, or ""
Skip the header, the asset class details, the IPO question and the certification. Do not invent anything."""


def _schluessel() -> str:
    return next(z.split("=", 1)[1].strip().strip("\"'") for z in open(".env") if z.startswith("DEEPSEEK_API_KEY"))


def guthaben(sitzung: requests.Session) -> float:
    antwort = sitzung.get(f"{API}/user/balance", timeout=30).json()
    return sum(float(b["total_balance"]) for b in antwort["balance_infos"] if b["currency"] == "USD")


def texte_laden() -> None:
    """PDF-Text jeder Meldung mit status `alt` nach daten/kongress_alt_texte.csv (speichert alle 50)."""
    alle = pd.read_csv(DATEN / "kongress_fortschritt.csv", dtype=str)
    alle = alle[alle["status"] == "alt"]
    da = set(pd.read_csv(TEXTE, dtype=str, usecols=["doc_id"])["doc_id"]) if TEXTE.exists() else set()
    offen = alle[~alle["doc_id"].isin(da)].sort_values("eingereicht", ascending=False)
    print(f"{len(alle)} Meldungen im älteren Formular, {len(offen)} Texte offen", flush=True)
    sitzung, zeilen, fehler = requests.Session(), [], 0
    for i, m in enumerate(offen.to_dict("records"), 1):
        try:
            r = sitzung.get(kongress.pdf_url(m["jahr"], m["doc_id"]), headers=kongress.KOPF, timeout=60)
            r.raise_for_status()
            seiten = [s.extract_text() or "" for s in pypdf.PdfReader(io.BytesIO(r.content)).pages]
            zeilen.append({"doc_id": m["doc_id"], "jahr": m["jahr"],
                           # kaputte Unicode-Zeichen in manchen PDFs → ersetzen, sonst scheitert das Speichern
                           "text": SEITE.join(seiten).replace("\x00", "").encode("utf-8", "replace").decode()})
        except Exception as e:
            print(f"  {m['doc_id']}: fehlgeschlagen ({e})", flush=True)
            fehler += 1
        if len(zeilen) >= 50 or i == len(offen):
            pd.DataFrame(zeilen).to_csv(TEXTE, mode="a", header=not TEXTE.exists(), index=False)
            zeilen = []
            print(f"  {i} von {len(offen)}", flush=True)
        time.sleep(0.3)
    print("Fertig" + (f", {fehler} fehlgeschlagen (beim nächsten Aufruf erneut)" if fehler else ""))


def umwandeln(roh: dict) -> dict:
    """Rohfelder von DeepSeek → Spalten wie beim neuen Formular (kongress.transaktionen)."""
    von, bis = kongress._betrag(str(roh.get("amount") or ""))
    t = {"inhaber": kongress.INHABER.get(str(roh.get("owner") or "").strip(), "selbst"),
         "wertpapier": "", "kuerzel": "", "anlageart": "",
         "art": kongress.ART.get(str(roh.get("type") or "").strip(), str(roh.get("type") or "")),
         "datum": pd.to_datetime(roh.get("date"), format="%m/%d/%Y", errors="coerce"),
         "gemeldet": pd.to_datetime(roh.get("notification_date"), format="%m/%d/%Y", errors="coerce"),
         "betrag_von": von, "betrag_bis": bis, "status": str(roh.get("filing_status") or ""),
         "unterkonto": str(roh.get("subholding") or ""), "beschreibung": str(roh.get("description") or ""),
         "kommentar": str(roh.get("comments") or "")}
    typ = str(roh.get("asset_type") or "").strip()
    kongress._name_ergaenzen(t, f"{roh.get('asset') or ''} [{typ}]" if typ else str(roh.get("asset") or ""))
    if not t["kuerzel"] and roh.get("ticker"):
        t["kuerzel"] = str(roh["ticker"]).upper().replace(" ", "")
    return t


def stuecke(text: str) -> list:
    """Lange Meldungen seitenweise in Stücke bis STUECK Zeichen teilen (sonst wird die Antwort zu lang)."""
    ergebnis = [""]
    for seite in text.split(SEITE):
        if ergebnis[-1] and len(ergebnis[-1]) + len(seite) > STUECK:
            ergebnis.append("")
        ergebnis[-1] += seite + "\n"
    return ergebnis


def auslesen(sitzung: requests.Session, text: str) -> tuple[list, int, int]:
    """Text → (Rohfelder je Transaktion, Eingabe-Token, Ausgabe-Token)."""
    roh, ein, aus = [], 0, 0
    for stueck in stuecke(text):
        antwort = sitzung.post(f"{API}/chat/completions", timeout=300, json={
            "model": MODELL, "temperature": 0, "response_format": {"type": "json_object"},
            "thinking": {"type": "disabled"}, "max_tokens": 8192,
            "messages": [{"role": "system", "content": ANWEISUNG}, {"role": "user", "content": stueck}],
        })
        antwort.raise_for_status()
        daten = antwort.json()
        if daten["choices"][0].get("finish_reason") == "length":
            raise ValueError("Antwort abgeschnitten")
        roh += json.loads(daten["choices"][0]["message"]["content"]).get("transaktionen", [])
        ein, aus = ein + daten["usage"]["prompt_tokens"], aus + daten["usage"]["completion_tokens"]
    return roh, ein, aus


def _versuch(sitzung: requests.Session, m: dict) -> tuple | None:
    try:
        return auslesen(sitzung, m["text"])
    except (requests.RequestException, ValueError, KeyError) as fehler:
        print(f"  {m['doc_id']}: fehlgeschlagen ({fehler})", flush=True)
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--texte", action="store_true", help="nur PDF-Texte laden (kostenlos)")
    parser.add_argument("--probe", type=int, help="N zufällige Meldungen nach .recherche/kongress_alt_probe.csv")
    args = parser.parse_args()
    if args.texte:
        texte_laden()
        return 0
    meldungen = pd.read_csv(DATEN / "kongress_fortschritt.csv", dtype=str)[MELDUNG]
    texte = pd.read_csv(TEXTE, dtype=str).drop_duplicates("doc_id").merge(meldungen, on=["doc_id", "jahr"])
    if args.probe:
        texte = texte.sample(args.probe, random_state=1)
        ziel, fertig_datei = DATEN.parent / ".recherche/kongress_alt_probe.csv", None
        erledigt = set()
    else:
        texte = texte.sort_values("eingereicht", ascending=False)
        ziel, fertig_datei = ERGEBNIS, FERTIG
        erledigt = set(pd.read_csv(FERTIG, dtype=str)["doc_id"]) if FERTIG.exists() else set()
    texte = texte[~texte["doc_id"].isin(erledigt)]

    sitzung = requests.Session()
    sitzung.headers["Authorization"] = f"Bearer {_schluessel()}"
    start = guthaben(sitzung)
    print(f"Guthaben {start:.2f} $, {len(texte)} Meldungen offen", flush=True)
    ein = aus = 0
    for von in range(0, len(texte), BLOCK):
        if von and guthaben(sitzung) < REST:
            print(f"Guthaben unter {REST} $, Schluss (nächster Aufruf macht weiter)")
            break
        block = texte.iloc[von:von + BLOCK].to_dict("records")
        with ThreadPoolExecutor(PARALLEL) as pool:
            ergebnisse = list(pool.map(lambda m: _versuch(sitzung, m), block))
        zeilen, fertig = [], []
        for m, ergebnis in zip(block, ergebnisse):
            if ergebnis is None:
                continue
            roh, e, a = ergebnis
            ein, aus = ein + e, aus + a
            zeilen += [{**{k: m[k] for k in MELDUNG}, **umwandeln(r)} for r in roh]
            fertig.append({"doc_id": m["doc_id"], "transaktionen": len(roh)})
        if zeilen:
            pd.DataFrame(zeilen).reindex(columns=SPALTEN).to_csv(
                ziel, mode="a", header=not ziel.exists(), index=False, date_format="%Y-%m-%d")
        if fertig_datei and fertig:
            pd.DataFrame(fertig).to_csv(fertig_datei, mode="a", header=not fertig_datei.exists(), index=False)
        print(f"{von + len(block)} Meldungen, {ein} + {aus} Token", flush=True)
    print(f"Fertig: {ein} Eingabe- + {aus} Ausgabe-Token, Guthaben {guthaben(sitzung):.2f} $ (vorher {start:.2f} $)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
