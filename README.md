# Insider-Monitor

Directors' Dealings von DAX- und MDAX-Firmen seit 2018, laufend ausgewertet mit der Event Study aus meiner Bachelorarbeit (Marktmodell, Ereignisfenster ±5 Handelstage). Live: https://insider.tobiaszwilling.me

Aktueller Stand, Entscheidungen und offene Punkte: `CLAUDE.md`.

## Befehle

```
python3 lauf.py                       # BaFin abfragen; nur bei neuen Meldungen neu rechnen
python3 lauf.py --immer               # immer neu rechnen (täglich nach Börsenschluss)
python3 -m pipeline.firmen            # DAX/MDAX-Liste neu aufbauen (nach Indexänderungen)
python3 historie.py                   # EQS-Archiv 2018 bis 21.10.2025 laden (setzt bei Abbruch fort)
python3 historie.py --reparieren      # EQS-Meldungen ohne Volumen oder Währung neu lesen
```

Lokal ansehen: `cd docs && python3 -m http.server`, dann http://localhost:8000

## Dateien

| Datei | Zweck |
|---|---|
| `daten/meldungen.csv` | alle je gesehenen BaFin-Meldungen; wird nur ergänzt, weil die BaFin nur 12 Monate zeigt |
| `daten/eqs_historie.csv`, `eqs_fortschritt.csv` | Meldungen aus dem EQS-Archiv (2018 bis Oktober 2025) und welche Firmen fertig sind |
| `daten/firmen.csv` | DAX/MDAX: ISIN → Name, Index, Yahoo-Ticker (nach Neuaufbau von Hand prüfen) |
| `daten/gemeldete_cluster.txt` | schon per Telegram gemeldete Cluster |
| `pipeline/bafin.py` | CSV-Export der BaFin holen, neue Zeilen erkennen |
| `pipeline/eqs.py` | EQS-Archiv: Firma suchen, Nachrichtenliste blättern (mit Drossel-Erkennung), MAR-Formular lesen |
| `pipeline/meldungen.py` | BaFin und EQS zu einer Tabelle zusammenführen |
| `pipeline/kurse.py` | bereinigte Schlusskurse von Yahoo |
| `pipeline/event_study.py` | Ereignisse bilden, Marktmodell, AR, AAR, CAAR, t-Test |
| `pipeline/cluster.py` | Cluster-Käufe (≥ 3 Personen in 14 Tagen, ≥ 50.000 €) |
| `pipeline/ranking.py` | Timing der Insider: Überrendite 60 Handelstage nach Käufen, mind. 3 Käufe |
| `pipeline/export.py` | JSON nach `docs/data/`, ruft `seiten.py` auf |
| `pipeline/seiten.py` | fertige Firmenseiten `docs/firma/<TICKER>/index.html`, `sitemap.xml`, Versionsnummern |
| `pipeline/telegram.py` | Nachricht bei neuen Cluster-Käufen |
| `docs/index.html`, `start.js` | Startseite: Kennzahlen, CAAR-Kurve, Cluster, Timing, Live-Ticker, Firmenliste |
| `docs/firma/<TICKER>/` | Firmenseite (erzeugt); `docs/firma.js` zeichnet darin das Kursdiagramm |
| `docs/firma.html` | Weiterleitung der alten Adresse `firma.html?t=…` |
| `docs/gemeinsam.js`, `style.css` | Formatierung, Liniendiagramm, Farben (hell und dunkel) |
| `docs/methode.html`, `impressum.html` | Methode, Impressum und Datenschutz |
| `docs/data/` | erzeugte JSON-Dateien; `kurse/<TICKER>.json` für die Diagramme |

## Methode, Unterschiede zur Bachelorarbeit

- Fenster in **Handelstagen** (Arbeit: Kalendertage im Code)
- t = 0 ist der erste Handelstag am oder nach dem **Mitteilungsdatum**
- ein Ereignis = Firma + Mitteilungstag + Richtung; Teilausführungen und mehrere Personen am selben Tag zählen einmal
- nur Vorstand und Aufsichtsrat, nur Aktien, nur Kauf/Verkauf
- dividenden- und splitbereinigte Kurse; nur Marktmodell (Fama-French-Faktoren erscheinen zu spät)
- Daten aus BaFin und EQS-Archiv statt finanzen.net

## Automatik (GitHub Actions)

- `aktualisieren.yml`: alle 30 Minuten `lauf.py`, werktags 17:15 UTC `lauf.py --immer`. Committet `daten/` und `docs/`; GitHub Pages veröffentlicht `docs/` mit jedem Commit.
- `historie.yml` („Historie laden“, per Knopfdruck): lädt das EQS-Archiv, höchstens 320 Minuten, speichert nach jeder Firma. Häkchen „reparieren“ liest fehlerhafte Meldungen neu.

Telegram bei neuen Cluster-Käufen, wenn die Secrets `TELEGRAM_TOKEN` und `TELEGRAM_CHAT_ID` gesetzt sind:

1. In Telegram `@BotFather` → `/newbot` → Token kopieren
2. Dem neuen Bot irgendeine Nachricht schreiben
3. `python3 -m pipeline.telegram --chat-id <TOKEN>` zeigt die Chat-ID
4. Test: `TELEGRAM_TOKEN=<TOKEN> TELEGRAM_CHAT_ID=<ID> python3 -m pipeline.telegram --test`
5. Beides auf GitHub unter Settings → Secrets and variables → Actions als Repository-Secret anlegen

Beim ersten Lauf mit Token werden vorhandene Cluster nur vermerkt (`daten/gemeldete_cluster.txt`), nicht gesendet.
