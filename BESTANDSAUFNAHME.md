# Bestandsaufnahme: alte Projekte und was der Insider-Monitor davon übernehmen kann

Stand: 22.10.2026. Durchgesehen wurden vier Ordner auf Tobias' Rechner (nur gelesen, nichts geändert).
Ziel laut Tobias: langfristig eine Seite wie gurufocus.com bzw. alleaktien.de, **mit Sentiment-Score** und
**mehr Aktien als DAX/MDAX**. Stand und Architektur des Insider-Monitors: `CLAUDE.md`, `GURUFOCUS.md`, `ALTERNATIVE_DATEN.md`.

## Übersicht der Fundorte

| Ordner | Was drin ist | Zeitraum |
|---|---|---|
| `~/Desktop/Claude/insider` | Dieses Projekt, live | Okt. 2026 |
| `~/gurufocus-analyse` | REA-Analyse von gurufocus.com: `BERICHT.md`, API-Katalog, Netzwerk-Mitschnitt | 12.10.2026 |
| `~/sentiment_data` | Rohdaten des alten Sentiment-Trackers (Reddit, X, ein NVDA-Ergebnis) | 14.04.2026 |
| `~/Startups/stock_pulse_neu` | Python-Pipeline „StockPulse“: Scraper, Ticker-Erkennung, Sentiment, Yahoo-Lader, Score | Apr. 2026 |
| `~/Startups/startup_2` | Next.js + Supabase + Groq, Krypto-Scraper (CoinGecko) mit KI-Kurztexten | Dez. 2025 |
| `~/Startups/startup_2_neuer_versuch` | Next.js-Grundgerüst, fast leer | März 2026 |
| `~/Startups/startup_2_3_versuch` | Next.js-App „StockPulse“ mit Landingpage, Dashboard, Abo 29 €, nur Beispieldaten | Apr. 2026 |

## 1. gurufocus-analyse

Fundort: `~/gurufocus-analyse/BERICHT.md`, `daten/api_methoden_katalog.csv` (937 API-Methoden),
`daten/datenanfragen_api.csv` (57 Abrufe), `daten/api_antwortstrukturen.json` (Feldnamen ohne Werte).

- Schon verarbeitet in `GURUFOCUS.md`, Punkte 1–4 umgesetzt (fertiges HTML je Firma, Vorabladen, Versionsnummern, Datenmodell).
- **Noch nützlich:** Der API-Katalog als Checkliste, was eine Aktienseite enthält: Übersicht, Finanzhistorie,
  Bewertung (GF Value), Score und Ränge (Wachstum, Profitabilität, Bilanz, Momentum), Analystenschätzungen,
  Branchenmedian als Vergleichslinie.
- **Kernlehre:** GuruFocus kauft Rohdaten ein (FactSet, QuoteMedia, Refinitiv). Die eigene Leistung sind die
  Kennzahlen darauf. Genau das ist hier übertragbar.
- **Nicht übernehmen:** den Code in `skripte/quellen/` (GuruFocus-Eigentum, Scraping laut Nutzungsbedingungen untersagt).

## 2. Der alte Sentiment-Tracker (April 2026)

Fundorte: `~/sentiment_data/*.json`, `~/Startups/stock_pulse_neu/Scraper/`, `stage1_ticker_extraction.py`,
`stage2_sentiment_analysis.py`, `config.py`, `ticker_extractor_v2.py`, `validation_labels_v2.csv`, `STAGE1_README.md`, `STAGE2_README.md`.

Ablauf damals:
1. **Abruf (14.04.2026, einmalig):** 180 Tweets von 9 Konten (DeItaone, Fxhedgers, unusual_whales, zerohedge,
   KobeissiLetter, financialjuice, aleabitoreddit, KawzInvests, StockMKTNewz) und 60 Reddit-Beiträge
   (wallstreetbets, stocks, pennystocks). Über die inoffiziellen Kommandozeilen-Werkzeuge `twitter` und `rdt`
   (`Scraper/twitter_scraper.py`, `Scraper/reddit_scraper.py`), Ausgabe nach `~/sentiment_data`.
2. **Ticker-Erkennung (25.04.2026):** Suchmuster für `$NVDA` (strikt) und `NVDA` (locker, mit Sperrliste wie CEO, WSJ).
   Beiträge mit mehr als 3 Tickern verworfen. 353 Beiträge von Hand gekennzeichnet (`validation_labels_v2.csv`).
3. **Stimmung:** Schlagwortzählung (`BULLISH_KEYWORDS` / `BEARISH_KEYWORDS` in `config.py`) im Umkreis von 150 Zeichen um den Ticker.
4. **Ergebnis** (`stage2_sentiment_analysis_20260425_234713.json`): 84 Ticker-Bewertungen, 60 % neutral,
   51 % mit geringem Vertrauen. Danach nicht weiterverfolgt, nie regelmäßig gelaufen.

Bewertung:
- **Wiederverwendbar:** die Stufen (Abruf → Ticker finden → Stimmung je Ticker → Tageswert je Aktie) und die
  Handkennzeichnung als Prüfdatensatz für jede künftige Methode.
- **Nicht wiederverwendbar:** die Schlagwortzählung (erkennt weder Ironie noch Verneinung, „puts“ ist nicht immer
  bärisch) und der Abruf über X (verstößt gegen deren Regeln, bricht ständig ab).

## 3. StockPulse-Pipeline (`~/Startups/stock_pulse_neu`)

| Datei | Inhalt | Übernehmen? |
|---|---|---|
| `scoring/spqs_s.py` | Score aus 10 Kriterien zu je 1 Punkt in Gruppen (Überleben, Wachstum, Effizienz, Insider/Markt), **Vertrauenswert sinkt, wenn Daten fehlen** (`real` 1,0 / `partial` 0,5 / `stub` 0) | **Ja, der Aufbau.** Kriterien neu wählen (waren für Cannabis-Pennystocks gedacht). Insider-Kriterium war nur ein Platzhalter, hier gibt es echte Daten. |
| `loaders/load_fundamentals.py` | Yahoo-Bilanz/GuV/Cashflow (~4 Jahre, 4 Quartale), Feldnamen über Alias-Listen (`*_FIELD_MAP`), nicht zuordenbare Felder in `_unmapped_rows` | **Ja, als Startpunkt**, falls Yahoo die erste Quelle wird. Löst dasselbe Problem wie in der ESEF-Probe (gleiche Kennzahl, anderer Name). |
| `loaders/calc_indicators.py` | RSI, gleitende Durchschnitte 50/200, Volatilität, MACD, Bollinger, Abstand zu 52-Wochen-Hoch/-Tief | Eventuell später für die Firmenseite, geringer Nutzen. |
| `loaders/load_market_data.py` | Stammdaten + 10 Jahre Kurse aus Yahoo, als Parquet | Nein, `pipeline/kurse.py` macht das schon. |
| `ticker_extractor_v2.py` | Ticker in Freitext finden, mit Sperrliste | Nur, wenn Social-Media-Sentiment kommt (siehe Abschnitt 5). |

Der Score-Aufbau ist im Grunde das, was alleaktien.de mit dem „Qualitätsscore“ macht: eine durchschaubare
Checkliste statt einer Blackbox.

## 4. Die Next.js-Versuche (`~/Startups/startup_2*`)

- `startup_2`: Krypto, CoinGecko-Daten nach Supabase, KI-Kurztexte über Groq (`scraper.py`, `src/app/api/analyze-stock/route.ts`).
- `startup_2_3_versuch`: Landingpage, Dashboard, Screener, Watchlist, Anmeldung über Supabase (`supabase_migration.sql`,
  `watchlist_migration.sql`), Preisseite 0 € / 29 €. Läuft fast nur mit `src/lib/mockData.ts`.
- `src/lib/sasEngine.ts` (SAS-Score): rechnet mit erfundenen Eingaben (Patentzahl, Marktgröße). **Fehler:** Laut
  Kommentar soll hoher Leerverkaufsanteil mehr Hype bedeuten, die Formel `100 - shortInterest` rechnet umgekehrt.

**Nicht übernehmen.** Widerspricht der Entscheidung „statisch bleiben“, kostet Betrieb, die KI-Texte sind nicht überprüfbar.
Einzig die Seitenaufteilung (Dashboard, Screener, Watchlist, Aktienseite) taugt als Ideenliste.

**Aufräumen:** In `startup_2/.env`, `.env.local` und `startup_2_3_versuch/.env*` liegen echte Schlüssel
(Groq, Gemini, Supabase). Kein Ordner ist ein Git-Repository, Risiko gering. Nicht mehr genutzte Schlüssel beim Anbieter sperren.

## 5. Ziel Sentiment-Score: was dafür realistisch ist

Grundsatz: Der Score muss sich wie die Insider-Daten **mit der Event Study prüfen lassen**. Ein Score, dessen
Wirkung man nicht belegen kann, schadet der Glaubwürdigkeit der Seite.

Mögliche Quellen, nach Eignung sortiert:

1. **Ad-hoc-Mitteilungen und Unternehmensnachrichten (EQS):** Gewinnwarnung, Prognoseerhöhung, Auftrag, Rücktritt.
   Kommen über `pipeline/eqs.py`, deckt alle deutschen Emittenten ab, rechtlich unbedenklich. Einordnung zuerst über
   Regeln (feste Formulierungen wie „Prognose angehoben“), später über ein Sprachmodell als einmaliger Lauf je Meldung
   (geringe Kosten, Ergebnis wird gespeichert, kein Chat). Wirkung über die vorhandene Event Study messbar.
   → **Empfohlener erster Baustein.**
2. **Reddit (offizielle API):** Für US-Aktien ausreichend Beiträge, für deutsche kaum (r/mauerstrassenwetten ist klein).
   Kostenlos nur für nicht-kommerzielle Nutzung, Bedingungen vor dem Start prüfen.
3. **StockTwits:** Nutzer kennzeichnen ihre Beiträge selbst als bullish/bearish, dadurch entfällt die Schlagwortfrage.
   Fast nur US-Aktien. Zugang und Bedingungen ungeprüft.
4. **X/Twitter:** Offizielle API teuer, inoffizieller Abruf verstößt gegen die Regeln. Nicht empfohlen.

Bausteine aus dem alten Tracker, die dann wieder gebraucht werden: Ticker-Erkennung (für deutsche Aktien
auch über Firmennamen, nicht nur Kürzel), Handkennzeichnung als Prüfdatensatz, Tageswert je Aktie.

## 6. Ziel mehr Aktien: was sich dadurch ändert

| Erweiterung | Insider-Daten | Fundamentaldaten | Aufwand |
|---|---|---|---|
| SDAX, TecDAX, übrige deutsche Aktien | BaFin-Export enthält schon alle Emittenten; EQS ebenfalls | Gleiches Problem wie heute (kein freier Weg vor ESAP, spätestens 10.07.2027) | klein: `pipeline/firmen.py` erweitern |
| USA | SEC Form 4 (gratis, gemeinfrei) | **SEC companyfacts gratis und sauber** (siehe `.recherche/esef_probe.md`) | mittel: neue Quelle, aber die Datenfrage ist gelöst |
| Übriges Europa | je Land eigene Meldestelle, uneinheitlich | wie Deutschland | groß, zuletzt |

Folgen für die Architektur (Entscheidung „statisch bleiben“ aus `CLAUDE.md`):
- Bis einige hundert Firmen reicht GitHub Pages mit einer Screener-JSON-Datei.
- Bei tausenden Firmen (z. B. ganze USA) wird das Repository zu groß (GitHub empfiehlt < 1 GB, der Bot committet
  schon heute mehrere MB je Lauf). Dann Daten auslagern (Release-Dateien, Objektspeicher) oder doch ein eigener Server.
  Das ist der Punkt aus `GURUFOCUS.md` Abschnitt 5 „Wann statisch nicht mehr reicht“.
- ISIN als feste ID passt auch für US-Aktien. Yahoo-Ticker bleiben nur für Anzeige und Adresse.

## 7. Empfohlene Reihenfolge

1. Stimmrechte fertig laden (Block 3 in `CLAUDE.md`, liegt bei Tobias).
2. Quelle für Fundamentaldaten entscheiden. Yahoo ist gratis, erlaubt laut Nutzungsbedingungen aber keine öffentliche
   Weitergabe. Sauber: Bezahlquelle mit Anzeigelizenz (EODHD, FMP, ca. 20–30 €/Monat) oder zuerst US-Aktien über die SEC.
3. Qualitätsscore je Firma nach dem Aufbau von `spqs_s.py` (Checkliste + Vertrauenswert), Insider-Daten als eigener Baustein.
4. Ad-hoc-Sentiment aus EQS, Wirkung mit der Event Study messen.
5. Universum erweitern: zuerst übrige deutsche Aktien (Daten liegen schon vor), dann USA.
6. Social-Media-Sentiment erst, wenn US-Aktien dabei sind, und nur über offizielle Zugänge.
