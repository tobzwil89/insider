from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
DATEN = WURZEL / "daten"
AUSGABE = WURZEL / "docs" / "data"
HEADER = {"User-Agent": "insider-pipeline/0.1 (+https://insider.tobiaszwilling.me)"}
