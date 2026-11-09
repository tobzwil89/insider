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
python3 stimmrechte_laden.py          # Stimmrechtsmitteilungen seit 2018 laden (setzt bei Abbruch fort)
python3 logos_laden.py                # fehlende Firmenlogos nach docs/logos/ laden (Wikidata, Vorrang daten/logos_hand.csv)
python3 rueckkaeufe_laden.py          # Aktienrückkäufe seit 2018 aus EQS laden (setzt bei Abbruch fort)
python3 sonntags_report.py [DATUM]    # Sonntags-Report als Entwurf nach newsletter/; mit --kit in Kit planen
python3 -m pipeline.gurus             # 13F-Depots der Gurus von der SEC laden
python3 -m pipeline.us_firmen         # S&P-500-Liste neu aufbauen (vierteljährlich)
python3 -m pipeline.staatsauftraege   # US-Staatsaufträge (USAspending), vierteljährlich
python3 -m pipeline.spenden           # PAC-Spenden (FEC), vierteljährlich
python3 -m pipeline.lobbying          # Lobbying-Berichte (LD-2, House-Clerk), vierteljährlich
```

Lokal ansehen: `cd docs && python3 -m http.server`, dann http://localhost:8000

## Dateien

| Datei | Zweck |
|---|---|
| `daten/meldungen.csv` | alle je gesehenen BaFin-Meldungen; wird nur ergänzt, weil die BaFin nur 12 Monate zeigt |
| `daten/eqs_historie.csv`, `eqs_fortschritt.csv` | Meldungen aus dem EQS-Archiv (2018 bis Oktober 2025) und welche Firmen fertig sind |
| `daten/stimmrechte.csv`, `stimmrechte_fortschritt.csv` | Stimmrechtsmitteilungen (§§ 33 ff. WpHG) seit 2018, eine Zeile je Mitteilung, und welche Firmen fertig sind |
| `daten/firmen.csv` | DAX/MDAX: ISIN → Name, Index, Yahoo-Ticker (nach Neuaufbau von Hand prüfen) |
| `daten/stimmrechte_eigene_aktien.csv`, `grossaktionaere_geprueft.csv`, `aktiengattungen.csv` | eigene Aktien der Firmen (§ 40 WpHG), von Hand geprüfte Großaktionäre, Aktienzahl je Gattung (für den Aktionärsring) |
| `daten/fonds_us.csv`, `norwegen.csv` | US-Fonds (SEC N-PORT, neuestes Quartal) und Norwegischer Staatsfonds (NBIM) mit Anteilen an unseren Firmen |
| `daten/rueckkaeufe.csv`, `rueckkaeufe_fortschritt.csv` | Aktienrückkäufe (Art. 5 MAR) seit 2018, eine Zeile je Rückkauftag, und welche Firmen fertig sind |
| `daten/gurus.csv` | Zeilen der 13F-Meldungen der Gurus (SEC) |
| `daten/logos.csv`, `logos_hand.csv` | Firmenlogos (Quelle Wikidata/Commons) und Handliste mit Vorrang |
| `daten/us_firmen.csv`, `staatsauftraege*.csv`, `spenden*.csv`, `lobbying.csv` | S&P 500, Staatsaufträge je Geschäftsjahr, PAC-Spenden, Lobbying-Ausgaben je Jahr |
| `daten/gemeldete_cluster.txt` | schon per Telegram gemeldete Cluster |
| `pipeline/bafin.py` | CSV-Export der BaFin holen, neue Zeilen erkennen |
| `pipeline/eqs.py` | EQS-Archiv: Firma suchen, Nachrichtenliste blättern (mit Drossel-Erkennung), MAR-Formular lesen |
| `pipeline/stimmrechte.py` | Stimmrechtsformular lesen (Deutsch/Englisch): wer, Datum, Anteile Aktien/Instrumente neu und vorher |
| `pipeline/fonds_us.py`, `pipeline/norwegen.py` | US-Fonds (SEC N-PORT) und Norwegischen Staatsfonds laden, für den Aktionärsring |
| `pipeline/rueckkaeufe.py`, `rueckkaeufe_laden.py` | Rückkaufmeldungen lesen (Datum, Stück, Kurs) und aus EQS laden |
| `stimmrechte_laden.py`, `stimmrechte_fliesstext.py` | Stimmrechtsmitteilungen laden (`--tage 14` nachts, `--alt` vor 2018); alte Fließtexte per DeepSeek auslesen (lokal) |
| `pipeline/gurus.py` | 13F-Depots der Gurus (SEC), Vergleich mit dem Vorquartal |
| `pipeline/personen.py` | Personenseiten für Vorstände und Aufsichtsräte (`docs/person/`) |
| `pipeline/us_firmen.py`, `staatsauftraege.py`, `spenden.py`, `lobbying.py` | US-Firmen (S&P 500): Liste, Staatsaufträge (USAspending), PAC-Spenden (FEC), Lobbying (LD-2) |
| `logos_laden.py` | Firmenlogos nach `docs/logos/` laden |
| `sonntags_report.py` | Sonntags-Report aus `docs/data`, samstags automatisch in Kit geplant |
| `pipeline/fundamental.py`, `kennzahlen.py` | Fundamentaldaten und Kennzahlen, **nur lokal** (Daten in `.gitignore`, die Action zeigt sie nie) |
| `pipeline/kongress.py`, `kongress_datensatz.py`, `politiker.py`, `trump.py`, `kongress_laden.py`, `trump_laden.py`, `seitenbilder.swift` | US-Politiker und Trump, **nur lokal** (Daten und Seiten in `.gitignore`, Rechtsfrage offen) |
| `pipeline/meldungen.py` | BaFin und EQS zu einer Tabelle zusammenführen |
| `pipeline/kurse.py` | bereinigte Schlusskurse von Yahoo |
| `pipeline/event_study.py` | Ereignisse bilden, Marktmodell, AR, AAR, CAAR, t-Test |
| `pipeline/cluster.py` | Cluster-Käufe (≥ 3 Personen in 14 Tagen, ≥ 50.000 €) |
| `pipeline/ranking.py` | Timing der Insider: Überrendite 60 Handelstage nach Käufen, mind. 3 Käufe |
| `pipeline/export.py` | JSON nach `docs/data/`, ruft `seiten.py` auf |
| `pipeline/seiten.py` | fertige Seiten (Firmen `docs/firma/<TICKER>/`, Personen, Gurus, US-Firmen `docs/us/<KÜRZEL>/`), `sitemap.xml`, Versionsnummern |
| `pipeline/telegram.py` | Nachricht bei neuen Cluster-Käufen |
| `docs/index.html`, `start.js` | Startseite: Kennzahlen, CAAR-Kurve, Cluster, Timing, Live-Ticker, Firmenliste |
| `docs/firma/<TICKER>/` | Firmenseite (erzeugt); `docs/firma.js` zeichnet darin das Kursdiagramm |
| `docs/firma.html` | Weiterleitung der alten Adresse `firma.html?t=…` |
| `docs/person/`, `docs/gurus/`, `docs/us/` | Personenseiten, Guru-Depots, US-Firmen (erzeugt) |
| `docs/logos/` | Firmenlogos (von `logos_laden.py`) |
| `newsletter/` | Sonntags-Reports (`<Datum>.md`), Gesprächsleitfaden `GESPRAECHE.md` |
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

- `aktualisieren.yml` („Daten aktualisieren“): **Hauptauslöser ist cron-job.org**, das die Action alle 30 Minuten über die
  GitHub-API startet (`workflow_dispatch` mit `immer=false`, seit 02.11.2026 stabil). Die eigenen GitHub-Zeitpläne
  (`13,43 * * * *`, werktags 17:15 UTC `lauf.py --immer`) bleiben als Reserve, weil GitHub sie nur unzuverlässig startet.
  Höchstens 15 Minuten. Samstags ab 18 Uhr plant derselbe Lauf den Sonntags-Report in Kit (Versand Sonntag 8 Uhr).
  Committet `daten/`, `docs/` und `newsletter/`; GitHub Pages veröffentlicht `docs/` mit jedem Commit.
  Per Knopfdruck mit Häkchen „immer“ rechnet er alles neu (nötig nach Änderungen an `seiten.py`/`export.py`).
- `stimmrechte.yml` („Stimmrechte laden“): nachts 02:37 UTC die Stimmrechtsmitteilungen der letzten 14 Tage, dazu
  US-Fonds (`pipeline.fonds_us`, nur bei neuem Quartal) und Norwegischen Staatsfonds (`pipeline.norwegen`, nur bei neuem
  Stand). Per Knopfdruck: Historie seit 2018 (Häkchen „Archiv vor 2018“ für ältere), höchstens 320 Minuten je Lauf,
  speichert nach jeder Firma.
- `rueckkaeufe.yml` („Rückkäufe laden“): nachts 03:17 UTC die Rückkaufmeldungen der letzten 14 Tage; per Knopfdruck die
  Historie seit 2018 (höchstens 320 Minuten).
- `historie.yml` („Historie laden“, nur per Knopfdruck): lädt das EQS-Archiv der Directors' Dealings, höchstens
  320 Minuten, speichert nach jeder Firma. Häkchen „reparieren“ liest fehlerhafte Meldungen neu.
- Guru-Depots (13F) lädt `lauf.py --immer` mit. US-Firmen, Lobbying und die Firmenliste werden vierteljährlich von Hand
  aktualisiert (Befehle oben).

Telegram bei neuen Cluster-Käufen, wenn die Secrets `TELEGRAM_TOKEN` und `TELEGRAM_CHAT_ID` gesetzt sind:

1. In Telegram `@BotFather` → `/newbot` → Token kopieren
2. Dem neuen Bot irgendeine Nachricht schreiben
3. `python3 -m pipeline.telegram --chat-id <TOKEN>` zeigt die Chat-ID
4. Test: `TELEGRAM_TOKEN=<TOKEN> TELEGRAM_CHAT_ID=<ID> python3 -m pipeline.telegram --test`
5. Beides auf GitHub unter Settings → Secrets and variables → Actions als Repository-Secret anlegen

Beim ersten Lauf mit Token werden vorhandene Cluster nur vermerkt (`daten/gemeldete_cluster.txt`), nicht gesendet.
