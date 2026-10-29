"""Alte Stimmrechtsmitteilungen (vor 2016, Fließtext ohne Formular) mit DeepSeek auslesen.

    python3 stimmrechte_fliesstext.py --probe 30     30 zufällige Texte nach .recherche/ (zum Prüfen von Hand)
    python3 stimmrechte_fliesstext.py                alle, neueste Jahre zuerst, bis das Guthaben unter 0,05 $ fällt

Liest daten/stimmrechte_texte.csv, schreibt daten/stimmrechte_fliesstext.csv (Spalten wie stimmrechte.csv,
formular=fliesstext, eine Zeile je Meldepflichtigem). Speichert nach jedem Block; ein neuer Aufruf macht
dort weiter (Block à 80 Texte). Schlüssel: DEEPSEEK_API_KEY in .env.
"""

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

from pipeline import DATEN
from stimmrechte_laden import SPALTEN

TEXTE = DATEN / "stimmrechte_texte.csv"
ERGEBNIS = DATEN / "stimmrechte_fliesstext.csv"
API = "https://api.deepseek.com"
MODELL = "deepseek-flash"
MAX_ZEICHEN = 12000  # danach folgen nur noch Listen einzelner Instrumente
REST = 0.05  # $; darunter wird aufgehört
PARALLEL = 8  # gleichzeitige Anfragen
BLOCK = 80  # Texte je Block; danach speichern und Guthaben prüfen

ANWEISUNG = """Du liest eine deutsche Stimmrechtsmitteilung (WpHG, oft Fließtext, teils Deutsch und Englisch doppelt).
Gib JSON zurück: {"meldungen": [...]}, ein Eintrag je Meldepflichtigem (Person oder Firma, die gemeldet hat;
bei Ketten von Tochterfirmen jede eigene Meldung einzeln, deutsche und englische Fassung derselben Meldung nur einmal).
Felder je Eintrag:
- "meldepflichtiger": Name ohne Ort
- "sitz": Ort und Land, sonst null
- "schwellendatum": Tag der Schwellenberührung als JJJJ-MM-TT
- "aktien": gesamter Stimmrechtsanteil aus Aktien in % (Zahl, direkt plus zugerechnet zusammen, nicht nur der zugerechnete Teil)
- "instrumente": Anteil aus (Finanz-)Instrumenten in % (Summe aller Instrumente), sonst null
- "summe": Gesamtanteil in %, sonst null
- "gesamtstimmrechte": Gesamtzahl der Stimmrechte des Emittenten, sonst null
- "korrektur": true, wenn die Mitteilung eine frühere korrigiert
Prozentwerte als Zahl mit Punkt (3,27% → 3.27). Ist es keine Stimmrechtsmitteilung (z. B. eigene Aktien,
Gesamtzahl der Stimmrechte), gib {"meldungen": []} zurück. Nichts erfinden."""


def _schluessel() -> str:
    return next(z.split("=", 1)[1].strip().strip("\"'") for z in open(".env") if z.startswith("DEEPSEEK_API_KEY"))


def guthaben(sitzung: requests.Session) -> float:
    antwort = sitzung.get(f"{API}/user/balance", timeout=30).json()
    return sum(float(b["total_balance"]) for b in antwort["balance_infos"] if b["currency"] == "USD")


def _kuerzen(text: str) -> str:
    """Kopf ('Für den Inhalt …') und DGAP-Fußtext weglassen, dann auf MAX_ZEICHEN kürzen."""
    text = text.split("Die DGAP Distributionsservices")[0]
    text = text.split("-" * 20, 1)[-1] if "Für den Inhalt" in text[:200] else text
    return text.strip()[:MAX_ZEICHEN]


def auslesen(sitzung: requests.Session, text: str) -> tuple[list, int, int]:
    """Text → (Meldungen, Eingabe-Token, Ausgabe-Token)."""
    antwort = sitzung.post(f"{API}/chat/completions", timeout=180, json={
        "model": MODELL, "temperature": 0, "response_format": {"type": "json_object"},
        "thinking": {"type": "disabled"},  # gleiches Ergebnis in der Probe, ~85 % weniger Ausgabe-Token
        "messages": [{"role": "system", "content": ANWEISUNG}, {"role": "user", "content": _kuerzen(text)}],
    })
    antwort.raise_for_status()
    daten = antwort.json()
    nutzung = daten["usage"]
    meldungen = json.loads(daten["choices"][0]["message"]["content"]).get("meldungen", [])
    return meldungen, nutzung["prompt_tokens"], nutzung["completion_tokens"]


def _versuch(sitzung: requests.Session, t) -> tuple | None:
    try:
        return auslesen(sitzung, t.text)
    except (requests.RequestException, ValueError, KeyError) as fehler:
        print(f"  fehlgeschlagen: {t.url} ({fehler})", flush=True)
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", type=int, help="N zufällige Texte nach .recherche/fliesstext_deepseek_probe.csv")
    args = parser.parse_args()
    texte = pd.read_csv(TEXTE).drop_duplicates("url")
    if args.probe:
        texte, ziel = texte.sample(args.probe, random_state=1), DATEN.parent / ".recherche/fliesstext_deepseek_probe.csv"
    else:
        texte, ziel = texte.sort_values("veroeffentlicht", ascending=False), ERGEBNIS
    erledigt = set(pd.read_csv(ziel, usecols=["url"])["url"]) if ziel.exists() else set()
    texte = texte[~texte["url"].isin(erledigt)]

    sitzung = requests.Session()
    sitzung.headers["Authorization"] = f"Bearer {_schluessel()}"
    start = guthaben(sitzung)
    print(f"Guthaben {start:.2f} $, {len(texte)} Texte offen", flush=True)
    ein = aus = 0
    for von in range(0, len(texte), BLOCK):
        if von and guthaben(sitzung) < REST:
            print(f"Guthaben unter {REST} $, Schluss vor {texte['veroeffentlicht'].iloc[von][:10]}")
            break
        block = list(texte.iloc[von:von + BLOCK].itertuples())
        with ThreadPoolExecutor(PARALLEL) as pool:
            ergebnisse = list(pool.map(lambda t: _versuch(sitzung, t), block))
        zeilen = []
        for t, ergebnis in zip(block, ergebnisse):
            if ergebnis is None:
                continue
            meldungen, e, a = ergebnis
            ein, aus = ein + e, aus + a
            # Leere Liste: trotzdem eine Zeile, damit der Text beim nächsten Aufruf nicht erneut läuft
            zeilen += [dict(m, firma=t.firma, isin=t.isin, veroeffentlicht=t.veroeffentlicht, formular="fliesstext",
                            url=t.url) for m in meldungen] or [dict(firma=t.firma, isin=t.isin, url=t.url,
                                                                    veroeffentlicht=t.veroeffentlicht, formular="anderes")]
        if zeilen:
            pd.DataFrame(zeilen).reindex(columns=SPALTEN) \
                .to_csv(ziel, mode="a", header=not ziel.exists(), index=False)
        print(f"{von + len(block)} Texte, bis {block[-1].veroeffentlicht[:10]}, {ein} + {aus} Token", flush=True)
    print(f"Fertig: {ein} Eingabe- + {aus} Ausgabe-Token, Guthaben {guthaben(sitzung):.2f} $ (vorher {start:.2f} $)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
