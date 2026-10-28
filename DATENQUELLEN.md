# Datenquellen für den Ausbau (USA und weitere Märkte)

Stand: 28.10.2026. Grundlage: Auswertung von OpenBB (github.com/openbq-org/OpenBB, früher OpenBB-finance, Stand
Commit 7df7d0c vom 24.10.2026, Lizenz Apache 2.0). Ziel von Tobias: perspektivisch eine große Datenbank, erweitert auf
US-Aktien und andere Märkte. Stand des Projekts: `CLAUDE.md`.

**Lesehinweis:** Abschnitte 1–3 sind die erste, zu enge Bewertung von OpenBB (nur deutsche Daten, GitHub Action).
Maßgeblich ist die Startup-Sicht: Abschnitt 4 (last30days-skill), 5 (OpenBB neu), 6 (FinceptTerminal), 7 (Überblick:
welcher Baustein aus welcher Quelle). Grundsatz von Tobias für die Recherche: alles aufnehmen, auch graue Wege;
die Spalte „Status“ markiert nur, was vor dem Start rechtlich zu klären ist.

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

## 4. Sentiment und News: last30days-skill (gründlich geprüft 28.10.2026, Startup-Sicht)

github.com/mvanhorn/last30days-skill, **MIT-Lizenz** (Code frei übernehmbar, auch kommerziell, Lizenzhinweis behalten),
~66.000 Sterne, sehr aktiv. 107 Python-Module, **nur Standardbibliothek, keine Abhängigkeiten** → leicht übernehmbar.
Frühere Bewertung (Abschnitt-Version vom selben Tag) war zu eng auf GitHub Actions und den deutschen Markt bezogen;
Tobias: Stack offen, globaler Markt, eigene Datenbank, Startup.

### Aufbau: drei Schichten

1. **Quellen-Anschlüsse** (~60 Module): je Plattform ein Abruf, Ergebnis in ein einheitliches Format.
2. **Ranking-Engine** (übernehmbar, ohne KI): `schema.py` (einheitliches Datenmodell je Beitrag), `normalize.py`
   (Plattformdaten → Modell), `relevance.py` (Passt der Beitrag zum Thema?), `signals.py` (Bewertung nach
   Engagement, Frische), `fusion.py` (gewichtete Reciprocal Rank Fusion: Ranglisten mehrerer Quellen zu einer
   zusammenführen), `dedupe.py` (fast gleiche Beiträge entfernen), `cluster.py` (Beiträge zur selben Geschichte bündeln).
   Das ist genau der Kern eines **News-Aggregators**: viele Quellen, eine Liste, ohne Doppelte, nach Story gebündelt.
3. **KI-Schicht** (`planner.py`, `rerank.py`, Zusammenfassung): Suchanfragen planen, Relevanz nachbewerten, Text schreiben.
   Ersetzbar durch eigene Stapelverarbeitung (z. B. jede Meldung einmal mit einem Sprachmodell bewerten).

### Alle Quellen und wie sie an die Daten kommen

**Tobias 28.10.2026: In der Recherche wird alles übernommen**, auch Wege über Browser-Cookies oder um Bot-Sperren herum
(noch nicht live, kein Geld). Spalte „Status“ zeigt nur, was **vor dem Start** geklärt werden muss:
offen = offizielle/öffentliche Schnittstelle · bezahlt = Schlüssel eines Anbieters · grau = Cookies, interne
Seitenteile oder gegen die Plattform-Bedingungen.

| Quelle | Weg (Modul) | Adresse | Status |
|---|---|---|---|
| **Reddit** | Archiv Arctic Shift (`reddit_arctic`) | `arctic-shift.photon-reddit.com/api/posts/search`, `…/comments/search`, `…/posts/ids` | offen (Drittarchiv, **Historie über Jahre**) |
| | interne Seitenteile, ohne Schlüssel (`reddit_listing`, `reddit_search`, `reddit_shreddit`) | `reddit.com/svc/shreddit/community-more-posts/{sort}/?name={sub}`, `…/svc/shreddit/search/?q=…&type=posts`, `…/svc/shreddit/comments/r/{sub}/t3_{id}` | grau |
| | öffentliches JSON (`reddit_public`) | `reddit.com/search.json`, `reddit.com/r/{sub}/search.json` (meist 403) | offen, aber gesperrt |
| | ScrapeCreators (`reddit`, `reddit_enrich`) | `api.scrapecreators.com` | bezahlt |
| **X / Twitter** | X-GraphQL mit Login-Cookies `auth_token` + `ct0` (`bird_x`, eingebaut aus @steipete/bird 0.8.0, MIT) | interne X-Schnittstelle | grau |
| | Cookies aus Chrome/Brave/Edge (Schlüsselbund), Safari, Firefox, laufendem Chrome (CDP), Linux-Hilfsprogramm agentcookie (`cookie_extract`, `chrome_cookies`, `safari_cookies`, `chrome_cdp`, `agentcookie`) | lokal | grau |
| | offizielle X API v2 (`x_api`, `xurl_x`) | `api.x.com/2` | bezahlt (teuer) |
| | xAI-Schnittstelle bzw. Grok-CLI mit X-Suche (`xai_x`, `grok_x`) | `api.x.ai/v1/responses` | bezahlt |
| | Xquik (`xquik`) | `xquik.com/api/v1` | bezahlt |
| **YouTube** | yt-dlp: Suche und Untertitel (`youtube_yt`) | youtube.com | grau |
| | ScrapeCreators | `api.scrapecreators.com/v1/youtube` | bezahlt |
| **TikTok, Instagram, Threads, Pinterest, LinkedIn, Telegram-Kanäle** | ScrapeCreators (je ein Modul; LinkedIn über Google-indexierte Beiträge) | `api.scrapecreators.com/v1/…` | bezahlt (Scraping) |
| **Amazon-Bewertungen** | Bright Data CLI (`amazon`, `brightdata`) | amazon.com | bezahlt (Scraping) |
| **Truth Social** | Mastodon-Schnittstelle mit Token aus den Browser-Entwicklertools (`truthsocial`) | `truthsocial.com/api/v2/search` | grau |
| **Trustpilot** | CLI `trustpilot-pp-cli` hinter Cloudflare (`trustpilot`) | `trustpilot.com/review/{domain}` | grau |
| **StockTwits** | öffentliche Schnittstelle (`stocktwits`) | `api.stocktwits.com/api/2/streams/symbol/{TICKER}.json`, `…/search/symbols.json` | offen, für Skripte gesperrt (403); kommerziell Lizenz |
| **Polymarket** | Gamma-Schnittstelle (`polymarket`) | `gamma-api.polymarket.com/events`, `…/public-search` | offen |
| **Stellenanzeigen** | Job-Board-Schnittstellen Greenhouse, Lever, Ashby, SmartRecruiters (`jobs`, `hiring_signals`) | z. B. `boards-api.greenhouse.io/v1/boards/{firma}`, `api.ashbyhq.com/posting-api/job-board/{firma}` | offen |
| **Meta-Werbung** | ScrapeCreators (`meta_ads`) | `api.scrapecreators.com/v1/facebook/adLibrary` | bezahlt (offizielle Ad-Library-API gibt es auch) |
| **Finanz-Newsletter** | DripStack-Suche (`dripstack`) | `dripstack.xyz` | offen |
| **Hacker News** | Algolia (`hackernews`) | `hn.algolia.com/api/v1` | offen |
| **Bluesky** | AT Protocol mit App-Passwort (`bluesky`) | `bsky.social`, `api.bsky.app` | offen |
| **GitHub** | Suche (`github`) | `api.github.com/search/issues` | offen |
| **Digg, Techmeme, arXiv** | CLIs `digg-pp-cli`, `techmeme-pp-cli`, `arxiv-pp-cli` | Techmeme-Archiv ab ~2005, arXiv Atom-API | offen |
| **dev.to** | Forem-API (`devto`) | `dev.to/api/articles` | offen |
| **Xiaohongshu** (China) | MCP-Server xiaohongshu-mcp (`xiaohongshu_api`) | `/api/v1/feeds/search` | grau |
| **Websuche** | Brave, Exa, Serper, Parallel, Perplexity (`grounding`, `perplexity`, `parallel_mcp`) | je Anbieter | bezahlt |
| | ohne Schlüssel: DuckDuckGo, Startpage (`web_search_keyless`) | `html.duckduckgo.com/html/`, `startpage.com/sp/search` | grau |
| **Webseite → Text** | Jina Reader (`web_fetch_keyless`) | `r.jina.ai/{url}` | offen (kostenlose Stufe) |
| **Audio/Video → Text** | Whisper-Schnittstelle (`transcribe`) | je Anbieter | bezahlt |

### Finanz-Perlen

- **StockTwits** (`api.stocktwits.com/api/2/streams/symbol/<TICKER>.json`): jeder Beitrag mit „Bullish“/„Bearish“ →
  fertiges Stimmungsverhältnis und Beitragsvolumen je Aktie. Für Skripte per Cloudflare gesperrt (Test 28.10.2026: 403),
  laut Code nur private Nutzung. **Für ein Produkt: Datenlizenz bei StockTwits anfragen** (bieten kommerzielle Daten an).
- **DripStack** (`dripstack.xyz`, Suche frei): bezahlte Finanz-Newsletter (Substack), Analysten, Podcasts. Nur
  Überschriften/Auszüge; Bedingungen prüfen.
- **Arctic Shift:** Reddit-Archiv mit Suche über Jahre → historische Stimmung je Aktie (z. B. r/wallstreetbets, r/stocks) für Backtests.
- **Stellenanzeigen, Werbeausgaben, Trustpilot, Amazon-Bewertungen:** klassische alternative Daten für Konsum- und Tech-Aktien.
- **Transkription** (`transcribe.py`, Whisper-API): Videos/Podcasts ohne Untertitel zu Text, z. B. Earnings Calls.

### Was fehlt (müssten wir selbst bauen)

- **Dauerhafte Erfassung:** Das Tool sucht auf Anfrage („letzte 30 Tage“), ein Produkt braucht laufende Erfassung in
  eine Datenbank mit Zeitreihen.
- **Firmenzuordnung:** Erwähnung → Firma → Ticker/ISIN (bei uns schon mit ISIN als ID angelegt). Im Tool nur Cashtags bei StockTwits.
- **Messbarer Stimmungswert:** Das Tool fasst per KI zusammen, rechnet aber keinen Score. Weg: jede Meldung/jeden Beitrag
  einmal bewerten (Finanz-Wörterbuch, FinBERT oder Sprachmodell im Stapel), Score je Firma und Tag speichern.
- **Lizenzierte Nachrichten:** Für eine News-Sektion fehlen klassische Nachrichtenquellen. Kandidaten: Pflichtmeldungen
  (EQS, SEC 8-K, offiziell und gratis), GDELT (weltweite Nachrichten-Datenbank, frei), bezahlt Benzinga/Polygon/Tiingo
  (auch in OpenBB, Abschnitt 2).

### Empfehlung

**Alles übernehmen** (Tobias 28.10.2026): Ranking-Engine (Schicht 2) als Grundgerüst für News-Feed und Sentiment und
sämtliche Quellen-Anschlüsse oben, auch die grauen. Vor dem Start (live/kostenpflichtig) Status „grau“ und „bezahlt“
neu bewerten: Lizenz anfragen (StockTwits, Reddit), offizielle Zugänge prüfen (X API, YouTube Data API, Meta Ad Library).
Quellcode bei Bedarf neu holen (`git clone --depth 1 https://github.com/mvanhorn/last30days-skill`), Modulnamen stehen oben.

## 5. OpenBB neu bewertet (Startup-Sicht, 28.10.2026)

Die erste Bewertung (Abschnitte 1–3, „nichts übernehmen“) war zu eng: Sie fragte nur, ob OpenBB deutsche Insiderdaten
liefert und in die GitHub Action passt. Aus Startup-Sicht (offener Stack, global, eigene Datenbank) ist OpenBB wertvoll,
und zwar nicht als eingebaute Bibliothek, sondern als **Vorlage und Code-Steinbruch** (Apache 2.0: Code darf auch
kommerziell übernommen werden, Lizenz- und Copyright-Hinweis behalten).

1. **Datenmodelle als Vorlage für unser Datenbankschema:** `openbb_platform/core/openbb_core/provider/standard_models/`
   enthält **180 einheitliche Modelle** mit Feldnamen und Beschreibungen, u. a. `balance_sheet`, `income_statement`,
   `cash_flow`, `insider_trading`, `institutional_ownership`, `form_13FHR`, `equity_ownership`, `government_trades`
   (Politiker-Geschäfte), `earnings_call_transcript`, `analyst_estimates`, `price_target`, `esg_score`, `key_metrics`,
   `financial_ratios`, `equity_short_interest`, `options_chains`, `company_news`, `world_news`, `calendar_earnings`,
   `historical_dividends`, `etf_holdings`, `index_constituents`, `yield_curve`, `economic_calendar`.
   Wer eine Finanzdatenbank für viele Anbieter baut, braucht genau so ein Zwischenformat: Jede Quelle wird darauf
   abgebildet, die Website liest nur das Zwischenformat. Liste der Dateien: `.recherche/openbb_baum.txt` (lokal).
2. **Anbieter-Code übernehmen** statt neu schreiben (Abschnitt 1): v. a. SEC (XBRL-Bilanzen vereinheitlicht,
   Form 4, 13D/13G `sec_beneficial_ownership`, Volltextsuche, Vorstandsgehälter, Segmentumsätze), Nasdaq (inoffizielle
   API mit US-Fundamentaldaten, Screener, Insider, Nasdaq Nordic), TMX (Kanada über GraphQL), Cboe (Optionsketten),
   Finra (Leerverkäufe), EZB/FRED/OECD/IWF (Makro).
3. **Ausgelagerte Pakete** (Abschnitt 2) liefern das, was im Repository fehlt: Yahoo (weltweit Kurse und
   Fundamentaldaten, auch Deutschland, ~4 Jahre), FMP (weltweit inkl. Xetra, bezahlt), Benzinga (Nachrichten,
   Analystenurteile), Intrinio, Polygon, Tiingo, Trading Economics, Seeking Alpha (Schätzungen, inoffiziell), Finviz.
4. **Router-Aufbau** (`extensions/*/…_router.py`: equity, etf, index, derivatives, fixedincome, economy, currency,
   crypto, commodity, news) zeigt eine sinnvolle Gliederung für unsere eigene Schnittstelle bzw. Navigation.
5. **Nicht übernehmen:** OpenBB als Ganzes einbauen (95 Abhängigkeiten, eigener Webserver). Besser: Modelle und
   einzelne Anbieter-Module kopieren und an unsere Datenbank anschließen.

## 6. FinceptTerminal als Quellenkatalog (28.10.2026)

github.com/Fincept-Corporation/FinceptTerminal (~33.000 Sterne, C++/Qt-Desktop-Programm mit Python-Skripten in
`fincept-qt/scripts/`). Lizenz und Datenbedingungen: `CLAUDE.md` → Offen → „FinceptTerminal“.
**Wichtig:** Hier geht es nicht um Nutzungsbedingungen einer Plattform, sondern um das Urheberrecht am Code
(AGPL-3.0 nur privat/Studierende, sonst kostenpflichtige Lizenz). Tobias' Entscheidung vom 28.10.2026 „nur Daten,
kein Code übernehmen“ gilt weiter, solange er sie nicht ändert. Übernehmbar ist das **Wissen, welche Quelle es gibt
und welche Adresse sie hat** (Tatsachen, kein geschützter Code); den Abruf schreiben wir selbst.

Umfang: **~240 Datenskripte** (dazu ~400 Handelsstrategien, Analyse-Wrapper, Krypto-Börsen über ccxt).
Für uns wichtig (Adresse aus dem Code gelesen):

| Zweck | Quelle | Adresse | Schlüssel |
|---|---|---|---|
| **Firmen-IDs verknüpfen** (ISIN ↔ Ticker ↔ Börse) | OpenFIGI | `api.openfigi.com/v3` | optional, gratis |
| **Rechtsträger-ID (LEI)** weltweit, Mutter/Tochter | GLEIF | `api.gleif.org/api/v1` | nein |
| Handelsregister weltweit | OpenCorporates | `api.opencorporates.com/v0.4` | ja |
| **Aufmerksamkeit je Firma** (Forschung: Wikipedia-Aufrufe sagen Handelsvolumen voraus) | Wikimedia | `wikimedia.org/api/rest_v1` (Pageviews) | nein |
| Firmennachrichten | GNews (Google-News-Feed, Python-Paket `gnews`) | Google News | nein (grau) |
| Nachrichten → Ticker, Begriffe | eigenes Skript `news_nlp` (Cashtags, Großbuchstaben-Wörter, Wortlisten) | lokal | – |
| **Politiker-Trades, Lobbyismus, alternative Daten** | Quiver Quantitative | `api.quiverquant.com/beta` | ja, bezahlt |
| Parteispenden/Lobbyismus USA | OpenSecrets | `opensecrets.org/api` | ja |
| Kongress | congress.gov, GovTrack, GovInfo | je Behörde | teils |
| **Fundamentaldaten gratis/günstig** | SimFin | `backend.simfin.com/api/v3` | ja, Gratisstufe |
| Fundamentaldaten/Kurse weltweit | EODHD, Finnhub, Twelve Data, Marketstack, Tiingo, Alpha Vantage, FMP, Intrinio, Polygon, Databento | je Anbieter (`eodhd.com/api`, `finnhub.io/api/v1` …) | ja, meist bezahlt |
| SEC-Bilanzen | SEC XBRL | `data.sec.gov/api/xbrl`, `sec.gov/files/company_tickers.json` | nein |
| Yahoo (Kurse, Screener) | Yahoo inoffiziell | `query1.finance.yahoo.com/v1/finance` | nein (grau) |
| TradingView (Screener, Wirtschaftskalender) | inoffiziell | `scanner.tradingview.com`, `economic-calendar.tradingview.com/events` | nein (grau) |
| Prognosemärkte | Kalshi, Polymarket | `api.elections.kalshi.com` | Kalshi ja |
| Deutsche offene Daten | GovData | `govdata.de/ckan/api` | nein |
| China-Markt komplett | AKShare (~25 Skripte), BaoStock | Python-Pakete | nein |
| Zentralbanken | EZB, Fed, BoE, BoJ, SNB, Riksbank, Norges Bank, RBA, BoC, BCB, TCMB, NBP, CNB, MNB u. a. | je Bank | meist nein |
| Statistikämter | Eurostat, ONS, Destatis-nahe (GovData), StatCan, e-Stat Japan, Census, BEA, BLS | je Amt | teils |
| Krypto | CoinGecko, CoinMarketCap, Glassnode, Messari, DefiLlama, DexScreener, Coinglass | je Anbieter | teils |
| Satelliten, Schiffe, Klima (alternative Daten) | MarineTraffic, AISStream, Global Fishing Watch, Copernicus, Sentinel Hub, NASA GIBS, Climate TRACE | je Anbieter | teils |
| Immobilien | Zillow, Redfin, HUD | je Anbieter | teils |

<details><summary>Alle ~240 Datenskripte (Dateinamen in fincept-qt/scripts/)</summary>

abs_data, acled_data, adb_data, aisstream_data, akshare_alternative, akshare_analysis, akshare_bonds, akshare_company_info, akshare_crypto, akshare_currency, akshare_data, akshare_derivatives, akshare_economics_china, akshare_energy, akshare_funds_expanded, akshare_futures, akshare_index, akshare_macro, akshare_misc, akshare_news, akshare_reits, akshare_stocks_board, akshare_stocks_financial, akshare_stocks_funds, akshare_stocks_historical, akshare_stocks_holders, akshare_stocks_hot, akshare_stocks_margin, akshare_stocks_realtime, alpha_vantage_extra_data, alphavantage_data, alternative_me_data, arxiv_data, baostock_data, bcb_data, bea_data, bis_data, bis_stats_data, blockchain_com_data, bls_data, bnm_data, bnr_data, boc_data, boe_data, boi_data, boj_fetcher, canada_gov_api, cboe_data, cboe_vix_data, census_data, census_international_data, cftc_data, climate_trace_data, cnb_data, coincap_data, coingecko, coinglass_data, coinmarketcap_data, coinpaprika_data, compute_technicals, congress_gov_data, copernicus_data, crossref_data, cryptocompare_data, data_gov_hk_api, data_world_data, databento_fno_chain, databento_provider, datagov_au_api, datagovsg_data, datagovuk_api, defillama_data, derivatives_pricing, dexscreener_data, ecb_data, ecb_sdmx_data, econdb_data, economic_calendar, eia_data, eia_electricity_data, eia_natural_gas_data, eia_petroleum_data, eia_steo_data, ember_energy_data, energy_transition_data, entso_e_data, eodhd_data, estat_japan_api, eurostat_data, eurostat_extra_data, exchangerate_data, faostat_data, fdic_data, federal_reserve_data, fetch_company_news, ffn_analysis, fincept_json, finnhub_data, fiscal_data, fitch_connect_data, fmp_data, fmp_extra_data, frankfurter_data, fred_data, fred_economic_data, french_gov_api, gas_infrastructure_data, gfd_data, github_stats_data, glassnode_data, global_competitiveness_data, global_debt_monitor_data, global_findex_data, global_fishing_watch_data, global_forest_watch_data, global_price_index_data, global_solar_atlas_data, global_trade_alert_data, govdata_de_api_complete, government_us_data, govinfo_data, govtrack_data, harvard_dataverse_data, hdx_data, hnb_data, hud_data, iadb_data, iea_data, ilostat_data, imf_data, imf_datamapper_data, intrinio_data, irena_data, irs_data, kaggle_data, lei_data, maddison_project_data, marinetraffic_data, marketstack_data, messari_data, metals_prices_data, mnb_data, multpl_data, n2yo_satellite_data, nasa_gibs_api, nasdaq_data, nber_data, nbp_data, news_geolocation, news_nlp, noaa_climate_data, nominatim_data, norges_bank_data, notebook_cell_runner, numbeo_data, oecd_data, oecd_dev_data, oecd_health_data, ons_data, openCorporates_data, open_exchange_data, open_meteo_data, open_parliament_data, open_secrets_data, openafrica_api, openaq_data, openbb_data, openfigi_data, optimize_portfolio_weights, option_greeks_daemon, oscar_data, overpass_api_data, owid_co2_data, owid_data, paris_agreement_data, penn_world_table_data, polygon_io_data, polymarket, portfolio_metrics, prediction_kalshi, prediction_polymarket, prs_group_data, public_apis_finance_data, pxweb_fetcher, quandl_nasdaq_data, quandl_wiki_data, quantstats_analysis, quantstats_monte_carlo, quiverquant_data, rba_data, redfin_data, relationship_map, reliefweb_data, riksbank_data, rsf_press_freedom_data, scb_data, screener_data, sdmx_json, sec_data, sec_xbrl_data, semantic_scholar_data, sentinelhub_data, simfin_data, snb_data, spain_data, spreadsheet, statcan_data, statista_free_data, swiss_gov_api, tcmb_data, tiingo_data, trading_economics_data, tradingview_data, translate_text, transparency_budget_data, treasury_data, twelve_data, un_comtrade_data, un_comtrade_extended_data, un_population_data, un_sdg_data, un_stats_data, unctad_data, undp_data, unesco_data, unhcr_data, unicef_data, universal_ckan_api, usda_ers_data, usda_fas_data, usda_nass_data, waqi_data, who_data, who_immunization_data, wikipedia_pageviews_data, wisesheets_macro_data, wits_trade_data, world_bank_climate_data, world_bank_commodity_data, world_bank_extra_data, world_pop_data, world_values_survey_data, worldbank_data, worldbank_health_data, worldometers_data, wto_data, yfinance_data, yh_finance_data, zenodo_data, zillow_data

</details>

**Bewertung:** Für einen Startup-Datenbestand ist FinceptTerminal die breiteste Quellenliste, die wir gefunden haben.
Am wertvollsten für das Produkt: OpenFIGI und GLEIF (saubere Firmenzuordnung über Länder hinweg, Grundlage jeder
globalen Datenbank), Wikipedia-Aufrufe (Aufmerksamkeit, frei, mit Forschung belegt), SimFin/EODHD/Finnhub
(Fundamentaldaten), Quiver/OpenSecrets (Politiker-Trades), Kalshi (Prognosemärkte).

## 7. Quer über alle drei Repositories: was wofür

| Baustein fürs Produkt | Beste Quelle laut Recherche |
|---|---|
| Datenbankschema | OpenBB-Standardmodelle (Abschnitt 5) |
| Firmenzuordnung global | OpenFIGI + GLEIF (Abschnitt 6), ISIN bleibt unsere feste ID |
| Insider/Großaktionäre USA | SEC Form 4, 13D/13G (OpenBB-Code, Abschnitt 1) |
| Fundamentaldaten USA | SEC XBRL companyfacts (OpenBB-Code) |
| Fundamentaldaten weltweit | Yahoo (grau, gratis), SimFin, EODHD, FMP (bezahlt) |
| News-Feed | Pflichtmeldungen (EQS, SEC 8-K), GDELT, GNews, Benzinga; Ranking-Engine aus last30days (Abschnitt 4) |
| Sentiment Anleger | Reddit (Arctic Shift, Seitenteile), X, StockTwits, YouTube (Abschnitt 4) |
| Aufmerksamkeit | Wikipedia-Aufrufe (Abschnitt 6), Reddit-Erwähnungen |
| Alternative Daten | Stellenanzeigen, Werbeausgaben (Abschnitt 4), Satelliten/Schiffe (Abschnitt 6) |
| Politiker | Quiver, OpenSecrets, congress.gov (Abschnitt 6); OpenBB `government_trades` |
| Erwartungen | Polymarket, Kalshi |
| Makro/Zinsen | EZB, FRED, Zentralbanken, Statistikämter (Abschnitte 1, 6) |
