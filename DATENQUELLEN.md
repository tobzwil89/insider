# Datenquellen für den Ausbau (USA und weitere Märkte)

Stand: 28.10.2026. Grundlage: Auswertung von OpenBB (github.com/openbq-org/OpenBB, früher OpenBB-finance, Stand
Commit 7df7d0c vom 24.10.2026, Lizenz Apache 2.0). Ziel von Tobias: perspektivisch eine große Datenbank, erweitert auf
US-Aktien und andere Märkte. Stand des Projekts: `CLAUDE.md`.

## Was OpenBB ist

OpenBB hat **keine eigenen Daten**. Es ist eine Sammlung von Anschlüssen („Provider“), die Daten bei der Quelle abholen
und in ein einheitliches Format bringen. Für uns ist deshalb nicht OpenBB wertvoll, sondern die Liste, **welche Quelle
was liefert und über welche Adresse**. Dort können wir direkt abholen, wie bei den 13F-Depots (`pipeline/gurus.py`).

Drei Arten von Zugang, wichtig für die öffentliche Website:

- **Offiziell:** dokumentierte Schnittstelle einer Behörde oder Börse. Nutzung meist frei, auch öffentlich.
- **Inoffiziell:** interne Schnittstellen von Webseiten (z. B. api.nasdaq.com). Funktioniert, ist aber nicht
  für Dritte gedacht, kann jederzeit brechen, und die Nutzungsbedingungen verbieten oft die Weiterverbreitung.
  **Vor Anzeige auf der Website Bedingungen prüfen.**
- **Bezahlt:** eigener Schlüssel nötig, öffentliche Anzeige meist nur mit teurerer Lizenz.

## 1. Im Repository enthalten (17 Anschlüsse)

### Unternehmen und Wertpapiere

| Quelle | Zugang | Adresse | Was es gibt | Schlüssel |
|---|---|---|---|---|
| **SEC** (USA) | offiziell | `data.sec.gov/submissions/`, `data.sec.gov/api/xbrl/companyfacts/`, `…/frames/`, `www.sec.gov/Archives/edgar/`, Volltextsuche `efts.sec.gov/LATEST/search-index` | **Bilanzen, GuV, Cashflow aller US-Firmen** (XBRL), Insiderhandel (Form 4), 13F-Depots, Großaktionäre (13D/13G), Vorstandsgehälter, Risikofaktoren, Segmentumsätze, Fondsbestände (N-PORT), nicht gelieferte Aktien (FTD), Berater (`api.adviserinfo.sec.gov`) | nein, aber User-Agent mit Kontakt, max. 10 Abrufe/s |
| **Nasdaq** | inoffiziell | `api.nasdaq.com/api/…`, `api.nasdaq.com/api/nordic/…`, `www.nasdaqtrader.com/dynamic/SymDir` (Tickerliste) | Kurse, Bilanzen, Kennzahlen, Insider, institutionelle Halter, Dividenden, Termine (Quartalszahlen, IPOs), Kursziele, Leerverkäufe, ETF-Bestände; **Nasdaq Nordic** (Stockholm, Kopenhagen, Helsinki, Island): Kurse, Fundamentaldaten, Dividenden, Screener, Nachrichten | nein |
| **TMX** (Kanada) | inoffiziell (so benannt) | `app-money.tmx.com/graphql`, `bondtradedata.ciro.ca` | Kurse, Bilanzen, **Insiderhandel Kanada**, Dividenden, Splits, Leerverkäufe, Indizes, ETFs, Anleihen | nein |
| **Cboe** | inoffiziell (offene CDN-Dateien) | `cdn.cboe.com/api/global/…` | Optionsketten, Indexkurse und -zusammensetzung (auch Europa/Australien), Futures | nein |
| **Finra** (USA) | offiziell + Morningstar | `api.finra.org`, `finra-markets.morningstar.com` | **Leerverkaufsbestände** (Short Interest), Anleihekurse, außerbörslicher Handel (OTC) | nein |
| **Deribit** | offiziell | `www.deribit.com/api` | Krypto-Futures und -Optionen | nein |

### Wirtschaft, Zinsen, Rohstoffe

| Quelle | Zugang | Adresse | Was es gibt | Schlüssel |
|---|---|---|---|---|
| **EZB** | offiziell (SDMX) | `data.ecb.europa.eu` | Leitzinsen, €STR, Wechselkurse, Zinskurve, Bankzinsen, Zahlungsbilanz | nein |
| **FRED** (Fed St. Louis) | offiziell | `api.stlouisfed.org/fred` | > 800.000 Zeitreihen (Zinsen, Inflation, Arbeitsmarkt, auch internationale) | ja, gratis |
| **US-Notenbank** | offiziell | `federalreserve.gov`, `newyorkfed.org`, `ffiec.gov` | Zinsen (SOFR, Fed Funds), Zinskurve, Geldmenge, Bankbilanzen, FOMC-Dokumente | nein |
| **BLS** (US-Statistik) | offiziell | `bls.gov` | Inflation (CPI, PPI), Arbeitsmarkt, Produktivität | ja, gratis |
| **OECD** | offiziell (SDMX) | `sdmx.oecd.org/public` | BIP, Inflation, Arbeitslosigkeit, Frühindikatoren, Hauspreise je Land | nein |
| **IWF** | offiziell | `api.imf.org/external`, `portwatch.imf.org` | Länderdaten, Handel, Schiffsverkehr in Häfen | nein |
| **US-Regierung** | offiziell | `api.usaspending.gov`, `govinfo.gov`, `ers.usda.gov` | Staatsanleihen-Auktionen, Staatsaufträge, Kongress (Gesetze, Abstimmungen), Agrardaten | teils |
| **CFTC** | offiziell | `publicreporting.cftc.gov` | Positionen am Terminmarkt (Commitments of Traders), Swaps | optional |
| **EIA** | offiziell | `eia.gov/opendata` | Öl, Gas, Strom (USA und weltweit) | ja, gratis |
| **JODI** | offiziell | `api.publisher.jodidata.org` | Öl- und Gas-Förderung, -Bestände je Land | nein |
| **Fama-French** | offiziell (Dateien) | `mba.tuck.dartmouth.edu/pages/faculty/ken.french/` | Faktoren, auch für Europa und einzelne Länder (für die Event Study bewusst nicht genutzt, siehe `CLAUDE.md`) | nein |

## 2. Eigene Pakete außerhalb des Repositorys (PyPI)

Diese Anschlüsse sind aus dem Repository ausgelagert, aber weiter als einzelne Pakete erhältlich (Version und Datum
laut PyPI am 28.10.2026). Inhalte nach allgemeinem Kenntnisstand, nicht im Code geprüft.

| Paket | Stand | Quelle | Kurz | Schlüssel |
|---|---|---|---|---|
| openbb-yfinance | 2.0.0, 29.09.2026 | Yahoo Finance (inoffiziell) | Kurse und Fundamentaldaten weltweit, nutzen wir schon direkt | nein |
| openbb-fmp | 1.6.1, 26.05.2026 | Financial Modeling Prep | **Fundamentaldaten weltweit inkl. Xetra**, Kennzahlen, Insider USA | ja, bezahlt |
| openbb-intrinio | 1.6.1 | Intrinio | USA: Fundamentaldaten, Optionen | ja, bezahlt |
| openbb-polygon | 1.5.1, 30.12.2025 | Polygon.io | USA: Kurse in Echtzeit, Ticks | ja, teils gratis |
| openbb-tiingo | 1.6.1 | Tiingo | Kurse, Nachrichten | ja, teils gratis |
| openbb-alpha-vantage | 1.6.1 | Alpha Vantage | Kurse weltweit | ja, gratis begrenzt |
| openbb-benzinga | 1.6.1 | Benzinga | Nachrichten, Analystenurteile | ja, bezahlt |
| openbb-tradingeconomics | 1.6.1 | Trading Economics | Wirtschaftskalender, Länderdaten | ja, bezahlt |
| openbb-econdb | 1.5.1 | EconDB | Wirtschaftsdaten | teils |
| openbb-finviz | 1.5.1 | Finviz (inoffiziell) | US-Screener, Kennzahlen | nein |
| openbb-seeking-alpha | 1.6.1 | Seeking Alpha (inoffiziell) | Gewinnschätzungen | nein |
| openbb-multpl | 1.3.1 | multpl.com | S&P-500-Kennzahlen (KGV usw.) | nein |
| openbb-wsj, openbb-biztoc, openbb-stockgrid | 1.6.1 | WSJ, Biztoc, Stockgrid | Marktbewegungen, Nachrichten, Dark Pools USA | nein |

## 3. Was das für unseren Ausbau heißt

**USA (am leichtesten, alles offiziell und gratis bei der SEC):**
1. Insiderhandel Form 4: Gegenstück zu den Directors' Dealings, gleiche Event Study möglich.
2. Fundamentaldaten aus `companyfacts` (XBRL): Bilanz, GuV, Cashflow für alle US-Firmen, viele Jahre zurück.
   Damit wäre das Fundamentaldaten-Problem für US-Aktien gelöst (für deutsche Aktien weiter offen, siehe `CLAUDE.md`).
3. Großaktionäre 13D/13G: Gegenstück zu den Stimmrechtsmitteilungen.
4. 13F-Depots: schon gebaut (`pipeline/gurus.py`).
5. Leerverkaufsbestände über Finra (`api.finra.org`).

**Weitere Märkte:**
- **Kanada:** Insiderhandel und Fundamentaldaten über TMX, aber inoffiziell. Offizielle Insider-Quelle wäre SEDI.
- **Skandinavien:** Nasdaq Nordic, ebenfalls inoffiziell.
- **Europa allgemein:** Keine Unternehmensdaten in OpenBB. EZB und OECD nur für Wirtschaft und Zinsen.

**Allgemein:** Nur Kurse und Wirtschaftsdaten bei den offiziellen Quellen sind für die öffentliche Website
unbedenklich. Für alles Inoffizielle (Nasdaq, TMX, Cboe, Yahoo, Finviz) vorher Nutzungsbedingungen prüfen und eine
offizielle Alternative suchen. Bei Fundamentaldaten außerhalb der USA bleibt ein bezahlter Anbieter (FMP, EODHD)
der realistische Weg.
