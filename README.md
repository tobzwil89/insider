# Insider-Monitor

Directors' Dealings aus der BaFin-Datenbank, laufend ausgewertet mit der Event Study aus meiner Bachelorarbeit (Marktmodell, Ereignisfenster ±5 Handelstage). Ziel: insider.tobiaszwilling.me

## Ablauf

```
python3 lauf.py            # BaFin abfragen; nur bei neuen Meldungen neu rechnen
python3 lauf.py --immer    # immer neu rechnen (täglich nach Börsenschluss)
python3 -m pipeline.firmen # DAX/MDAX-Liste neu aufbauen (nach Indexänderungen)
```

## Dateien

| Datei | Zweck |
|---|---|
| `daten/meldungen.csv` | alle je gesehenen BaFin-Meldungen; wird nur ergänzt, weil die BaFin nur 12 Monate zeigt |
| `daten/firmen.csv` | DAX/MDAX: ISIN → Name, Index, Yahoo-Ticker (nach Neuaufbau von Hand prüfen) |
| `pipeline/bafin.py` | CSV-Export der BaFin holen, neue Zeilen erkennen |
| `pipeline/kurse.py` | bereinigte Schlusskurse von Yahoo |
| `pipeline/event_study.py` | Ereignisse bilden, Marktmodell, AR, AAR, CAAR, t-Test |
| `pipeline/cluster.py` | Cluster-Käufe (≥ 3 Personen in 14 Tagen, ≥ 50.000 €) |
| `pipeline/export.py` | JSON für die Website nach `docs/data/` |

## Methode, Unterschiede zur Bachelorarbeit

- Fenster in **Handelstagen** (Arbeit: Kalendertage im Code)
- t = 0 ist der erste Handelstag am oder nach dem **Mitteilungsdatum**
- ein Ereignis = Firma + Mitteilungstag + Richtung; Teilausführungen und mehrere Personen am selben Tag zählen einmal
- nur Vorstand und Aufsichtsrat, nur Aktien, nur Kauf/Verkauf
- dividenden- und splitbereinigte Kurse; nur Marktmodell (Fama-French-Faktoren erscheinen zu spät)

## Automatik (GitHub Action)

`.github/workflows/aktualisieren.yml` läuft alle 30 Minuten (`lauf.py`) und werktags um 17:15 UTC (`lauf.py --immer`). Geänderte Daten in `daten/` und `docs/data/` werden committet; GitHub Pages veröffentlicht `docs/` mit jedem Commit.

Telegram bei neuen Cluster-Käufen, wenn die Secrets `TELEGRAM_TOKEN` und `TELEGRAM_CHAT_ID` gesetzt sind:

1. In Telegram `@BotFather` → `/newbot` → Token kopieren
2. Dem neuen Bot irgendeine Nachricht schreiben
3. `python3 -m pipeline.telegram --chat-id <TOKEN>` zeigt die Chat-ID
4. Test: `TELEGRAM_TOKEN=<TOKEN> TELEGRAM_CHAT_ID=<ID> python3 -m pipeline.telegram --test`
5. Beides auf GitHub unter Settings → Secrets and variables → Actions als Repository-Secret anlegen

Beim ersten Lauf mit Token werden vorhandene Cluster nur vermerkt (`daten/gemeldete_cluster.txt`), nicht gesendet.
