"""Ende der Haltefrist nach US-Börsengängen (Lock-up): Ab dann dürfen Gründer und Altaktionäre verkaufen.
Bei kleinen Werten oft Verkaufsdruck, deshalb als Termin für Pennystocks nützlich.

Quelle: Segmara (segmara.com/feeds/ipo-lockups.json), ohne Schlüssel. Lizenz laut Feed: frei mit Nennung
„Data: Segmara, segmara.com/ipo-lockup-expirations“ und Link. Termine sind GESCHÄTZT (Börsengang + 180 Tage);
der echte Termin steht im Prospekt, frühere Freigaben sind möglich. So auch anzeigen.

    python3 -m pipeline.lockups   → daten/lockups.csv (dauerhaft, neue Zeilen werden ergänzt)
                                    docs/data/lockups.json (14 Tage zurück bis 60 Tage voraus)
Läuft nachts in der Action „Stimmrechte laden“.
"""
import json
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

from pipeline import AUSGABE, DATEN, HEADER

URL = "https://segmara.com/feeds/ipo-lockups.json"
DATEI, JSON = DATEN / "lockups.csv", AUSGABE / "lockups.json"


def main():
    d = requests.get(URL, headers=HEADER, timeout=60).json()
    neu = pd.DataFrame(d["items"]).rename(columns={"company": "firma", "ipo_pricing_date": "boersengang",
                                                    "estimated_lockup_end": "lockup_ende_geschaetzt",
                                                    "sec_prospectus_url": "prospekt"})
    neu = neu[["ticker", "firma", "boersengang", "lockup_ende_geschaetzt", "prospekt"]]
    df = pd.concat([pd.read_csv(DATEI, dtype=str), neu]) if DATEI.exists() else neu
    df = df.drop_duplicates(["ticker", "boersengang"], keep="last").sort_values("lockup_ende_geschaetzt")
    df.to_csv(DATEI, index=False)

    heute = datetime.now(timezone.utc).date()
    von, bis = str(heute - timedelta(days=14)), str(heute + timedelta(days=60))
    fenster = df[(df.lockup_ende_geschaetzt >= von) & (df.lockup_ende_geschaetzt <= bis)]
    AUSGABE.mkdir(parents=True, exist_ok=True)
    JSON.write_text(json.dumps({
        "stand": d.get("updated_utc"),
        "quelle": "Data: Segmara, segmara.com/ipo-lockup-expirations",
        "hinweis": "Geschätzt: Börsengang + 180 Tage. Echter Termin im Prospekt, frühere Freigaben möglich.",
        "lockups": fenster.to_dict("records"),
    }, ensure_ascii=False, separators=(",", ":")))
    print(f"Lockups: {len(neu)} im Feed, {len(df)} gesamt, {len(fenster)} im Fenster {von} bis {bis}")


if __name__ == "__main__":
    main()
