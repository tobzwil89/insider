# Vorbild GuruFocus: was sie gut machen und was wir übernehmen

Stand: 22.10.2026. Grundlage ist eine Analyse von gurufocus.com mit REA (Netzwerk-Mitschnitt im echten Chrome,
statische Analyse aller 48 JavaScript-Dateien, Zeitmessung über die Performance-API des Browsers) sowie ein
Vergleich mit dem Insider-Monitor (Live-Seite und Code in diesem Ordner).

## Kurzfassung

GuruFocus ist schnell, weil der Server **fertige Seiten** schickt und die Daten **schon abfragefertig vorbereitet**
sind, nicht wegen besonderer Technik. Ihr Technik-Stapel ist eher alt (Nuxt 2, Vue 2, PHP/Laravel, etwa 0,5 MB JavaScript).

Der Insider-Monitor macht den wichtigsten Teil schon genauso: Python rechnet alles vor und schreibt fertiges JSON.
Was fehlt, ist **vorgerendertes HTML je Firma**. Heute sieht der Besucher erst „Lade …“, bis HTML, JavaScript
und JSON nacheinander geladen sind.

## 1. Was GuruFocus macht

### Daten
- **Rohdaten sind eingekauft** (steht im Footer jeder Aktienseite): Kurse von QuoteMedia, Fundamentaldaten von FactSet,
  Analystenschätzungen von Refinitiv und FactSet. „Data is updated daily.“
- **Eigene Arbeit sind die Kennzahlen darauf:** GF Value, GF Score, Ränge (Wachstum, Profitabilität, Bilanz, Momentum).
  Diese Werte werden auf dem Server berechnet und fertig ausgeliefert.
- **Dazu kommen** Nachrichten (Zacks, Benzinga), SEC-Pflichtmeldungen, Fondsbriefe und ein KI-Chat (selbst
  betriebenes Dify). Die Guru- und Insider-Daten stammen sehr wahrscheinlich aus den SEC-Meldungen 13F und Form 4
  (Vermutung, nicht beobachtet).
- **Jede Aktie hat eine interne, feste ID** (MSFT = `US04EJ`, NVDA = `US04L5`), unabhängig vom Börsenkürzel.

### Backend
- **Cloudflare vor allem:** Bot-Schutz (curl und Headless-Browser bekommen 403), HTTP/3, Zwischenspeicher am Rand
  des Netzes (Edge-Cache).
- **Eigene REST-API** unter `/reader/_api/...`, sehr wahrscheinlich PHP/Laravel (Seitenformat der Antworten,
  Laravel-Passport-Login). Die Antworten verraten den internen Server `10.171.162.70:8899`.
- **Daten kommen diagrammfertig:** Der Kursverlauf ist eine Liste von `[Datum, Wert]`-Paaren und geht ohne
  Umrechnung ins Diagramm. Eine Aktienseite ruft etwa 20 kleine, spezialisierte Endpunkte auf (Kurs, Ränge,
  Schätzungen, Nachrichten), jeder mit 0,1 bis 330 KB.
- **Schutz gegen Scraping:** Jede API-Anfrage trägt einen signierten Zeitstempel (`Signature`-Header).

### Frontend
1. **Server-Side Rendering:** Das HTML enthält die komplette Seite mit Kurs, Kennzahlen und Text
   (552 KB roh, 73 KB komprimiert). Dazu kommen die Startdaten als `window.__NUXT__`.
2. **HTML 60 Sekunden zwischengespeichert:** Der Server muss die Seite meist gar nicht neu bauen.
3. **JavaScript, CSS und Schriften ein Jahr im Cache:** Der Dateiname enthält eine Prüfsumme (Hash), eine neue
   Version heißt also anders.
4. **Code-Splitting und Preload:** Jede Seite lädt nur ihren Code, 43 Preload-Hinweise im HTML.
5. **Kein Neuladen beim Reiterwechsel:** Ein Klick auf „Financials“ lädt kein neues HTML, nur 3 API-Aufrufe.
6. **Links vorab laden:** Sichtbare Links laden ihren Code in Leerlaufzeiten schon herunter.
7. **Besuchte Reiter bleiben im Speicher (`keepAlive`)**, dazu ein eigener Cache im Arbeitsspeicher
   (15 Minuten, 200 Einträge) und der Abbruch veralteter Anfragen.

**Gemessen (AMZN, leerer Cache):** erstes Byte 301 ms, **erster Inhalt 436 ms**, fertig 823 ms. Danach laden die
API-Daten parallel weiter (140–700 ms je Aufruf).

## 2. Vergleich mit dem Insider-Monitor

| | GuruFocus | Insider-Monitor heute |
|---|---|---|
| Daten aufbereiten | Server rechnet, API liefert fertig | Python-Pipeline rechnet, schreibt fertiges JSON ✅ |
| Format Kursverlauf | `[Datum, Wert]`-Paare | `[Datum, Wert]`-Paare ✅ |
| Feste ID je Aktie | interne `stockid` | ISIN intern, Yahoo-Ticker in der URL ✅ |
| Datenquellen genannt | Footer jeder Seite | Hinweisband + Methode-Seite ✅ |
| HTML enthält Inhalt | ja (SSR) | nein, erst „Lade …“ ❌ |
| Adresse je Aktie | `/stock/AAPL/summary` | `firma.html?t=SAP.DE` (für Suchmaschinen eine Seite) ❌ |
| Wartekette beim Laden | HTML, fertig | HTML → JS → JSON nacheinander ❌ |
| Übertragene Menge | ~550 KB (HTML + JS) | ~14 KB ✅ |
| Cache für JS/CSS | 1 Jahr, Hash im Namen | 10 Min. (GitHub Pages fest), `?v=2` von Hand |
| Navigation | ohne Neuladen | jede Seite neu, bei 14 KB unkritisch |

**Gemessen (SAP-Firmenseite, leerer Cache):** erstes Byte 186 ms. JSON kommt erst ab 396 ms und ist nach
etwa 570 ms da. Erst dann stehen Zahlen auf der Seite, vorher „Lade …“.

## 3. Was wir übernehmen (nach Nutzen sortiert)

### 1. Firmenseiten als fertiges HTML erzeugen (größter Gewinn)
Das ist die gurufocus-Idee ohne Server: `export.py` schreibt zusätzlich zur JSON-Datei je Firma eine HTML-Datei,
z. B. `docs/firma/SAP.DE/index.html` (Adresse: `/firma/SAP.DE/`). Darin stehen Name, ISIN, Kacheln und die
Meldungstabelle schon als HTML, und das JSON wird direkt eingebettet. Das Diagramm zeichnet `firma.js` wie bisher.

Was es bringt:
- **Zahlen sofort sichtbar**, kein „Lade …“ und keine Wartekette mehr.
- **Google findet jede Firma einzeln** („SAP Insider Käufe“), mit eigenem Titel und eigener Beschreibung.
- **Schönere Links** zum Teilen (`/firma/SAP.DE/` statt `firma.html?t=SAP.DE`).
- Passt zu den Projektregeln: kein Build-Werkzeug, keine Bibliothek. Python schreibt die Dateien sowieso schon.

Aufwand: klein bis mittel. Eine HTML-Vorlage als Python-String plus `html.escape` für alle Texte aus BaFin/EQS
(die Regel „nur textContent“ gilt dann sinngemäß für die Vorlage).
Die alte Adresse `firma.html?t=…` als Weiterleitung behalten, damit vorhandene Links funktionieren.

### 2. Links vorab laden (5 Zeilen)
GuruFocus lädt Links vor, bevor man klickt. Bei uns geht das ohne Code mit den „Speculation Rules“ des Browsers,
einem kurzen Block im `<head>` jeder Seite:

```html
<script type="speculationrules">
{"prerender": [{"where": {"href_matches": "/firma/*"}, "eagerness": "moderate"}]}
</script>
```

Was es bringt: Fährt man mit der Maus über eine Firma, baut Chrome die Seite im Hintergrund fertig. Der Klick wirkt
dann wie ein Reiterwechsel bei gurufocus, ohne dass wir eine Single-Page-App bauen. Andere Browser ignorieren den
Block. Sinnvoll erst nach Punkt 1, weil dann die Zielseite schon den Inhalt enthält.

### 3. Versionsnummer automatisch statt `?v=2` von Hand
`export.py` kann an `style.css` und die JS-Dateien eine kurze Prüfsumme des Inhalts hängen (`firma.js?v=3f9a1c`).
Was es bringt: Man kann das Hochzählen nicht mehr vergessen. Schneller wird es nicht, weil GitHub Pages den Cache
fest auf 10 Minuten setzt.

### 4. Für den GuruFocus-Ausbau: Datenmodell jetzt schon so anlegen
- **Fertig rechnen, fertig ausliefern:** Kennzahlen (später z. B. Bewertung, Ränge) in der Pipeline berechnen, nie im
  Browser. Das ist genau, was GuruFocus mit GF Value macht.
- **ISIN als feste ID behalten**, Ticker nur für die Anzeige und die Adresse (wie gurufocus' `stockid`).
- **Je Firma kleine Teil-Dateien statt einer großen**, sobald neue Bereiche dazukommen
  (z. B. `firmen/SAP.DE/kurse.json`, `…/fundamental.json`). Die Seite lädt nur, was sie zeigt.
- **Datenquelle und Stand auf jeder Seite nennen**, wie im gurufocus-Footer (machen wir schon).

## 4. Was wir bewusst nicht übernehmen

| GuruFocus | Warum nicht |
|---|---|
| Nuxt/Vue, Element UI, zwei Diagramm-Bibliotheken | ~0,5 MB JavaScript; unsere Seiten sind mit ~14 KB schon leichter. Fertiges HTML aus Python bringt den Hauptvorteil ohne das Gewicht. |
| Eigener API-Server (Laravel) | Kostet Betrieb und Geld. Statische Dateien auf GitHub Pages reichen, solange alles einmal pro Lauf berechnet werden kann. |
| Single-Page-App (Wechsel ohne Neuladen) | Lohnt erst bei schweren Seiten. Bei uns erledigen Punkt 1 und 2 das fast genauso gut. |
| Eigener Cache im Browser, Abbruch von Anfragen | Der normale HTTP-Cache des Browsers macht das bei statischen Dateien von selbst. |
| Signierte Anfragen, Bot-Schutz | Unsere Daten sind öffentlich (BaFin), das Repository auch. Nichts zu schützen. |
| Cloudflare davor | Wäre der Weg zu längerem Cache und eigenem Header. Erst nötig, wenn GitHub Pages zu langsam oder zu eng wird. |

## 5. Wann statisch nicht mehr reicht

Ein eigener Server (z. B. Python mit FastAPI und SQLite) lohnt sich erst, wenn eins davon eintritt:
- **Freie Filter über alle Firmen** (Screener) mit so vielen Kombinationen, dass man sie nicht vorab als JSON
  schreiben kann. Bei ~90 DAX/MDAX-Firmen passt ein Screener noch locker in eine einzige JSON-Datei.
- **Nutzerkonten** (Watchlist, Benachrichtigungen pro Person).
- **Daten, die öfter als alle 30 Minuten frisch sein müssen** (Echtzeitkurse).

Bis dahin ist das heutige Modell, „Pipeline rechnet, GitHub Pages liefert aus“, im Kern genau das, was GuruFocus
mit viel mehr Technik macht.
