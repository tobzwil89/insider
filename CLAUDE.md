# Insider-Monitor – Projektstand

Directors' Dealings (Art. 19 MAR) aus der BaFin-Datenbank, live ausgewertet mit der Event Study aus Tobias' Bachelorarbeit (Uni Bayreuth, DAX/MDAX 2018–2024). Langfristiges Ziel: eine Art GuruFocus für deutsche Aktien.

- Website: https://insider.tobiaszwilling.me (GitHub Pages aus `/docs`, Branch `main`)
- Repository: github.com/tobzwil89/insider (öffentlich)
- DNS: Namecheap, CNAME `insider` → `tobzwil89.github.io`
- Aufbau und Befehle: siehe README.md

## Wie es läuft

- GitHub Action `.github/workflows/aktualisieren.yml`: alle 30 Min `lauf.py` (rechnet nur bei neuen Meldungen), werktags 17:15 UTC `lauf.py --immer`. Der Bot committet `daten/` und `docs/data/` selbst; vor eigenen Pushes daher immer `git pull` (pull.rebase=true).
- Telegram bei neuen Cluster-Käufen; Secrets `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID` sind in GitHub gesetzt und getestet.
- Website: reines HTML/CSS/JS ohne Bibliotheken und Build-Schritt; Diagramme als eigenes SVG in `docs/gemeinsam.js`.

## Entscheidungen (mit Grund)

- **Neu statt Übernahme des BA-Codes:** Der alte Code (Dropbox `Uni/Universität Bayreuth/Bachelorarbeit/Code für Analyse Final für Bachelorarbeit.rtf`) rechnete in Kalendertagen statt Handelstagen, zählte Teilausführungen mehrfach (2.409 statt 1.910 Ereignisse), mischte Prozent- und Dezimaleinheiten bei Fama-French und nutzte unbereinigte Kurse. Die Daten waren von finanzen.net kopiert, ohne eindeutiges Veröffentlichungsdatum.
- **t = 0 = Mitteilungsdatum**, nicht das Freischaltungsdatum bei der BaFin (das liegt oft 1–3 Tage später; Firmen veröffentlichen vorher über EQS).
- **Ereignis = Firma + Mitteilungstag + Richtung**; nur Vorstand und Aufsichtsrat, nur Aktien, nur Kauf/Verkauf.
- **Nur Marktmodell** (DAX bzw. MDAX), Schätzfenster −130 bis −11, Ereignisfenster ±5 Handelstage, mindestens 100 Schätztage. Fama-French fällt weg, weil die Faktoren nur monatlich mit Verzögerung erscheinen.
- **Cluster:** ≥ 3 Personen (ohne eng verbundene) in 14 Tagen nach Geschäftsdatum, ≥ 50.000 €. Die Mindestsumme filtert Mitarbeiterprogramme heraus (z. B. ProCredit, monatlich ~17.600 €).
- **Firmen über die ISIN identifizieren**, eine JSON-Datei je Firma. Grundlage für den späteren GuruFocus-Ausbau.
- **BaFin liefert nur 12 Monate**, deshalb wird `daten/meldungen.csv` nur ergänzt, nie überschrieben. Daten liegen ab 22.10.2025 vor.
- **Ranking einzelner Personen zurückgestellt** (Datenschutz-Grauzone), auf Wunsch von Tobias.

## In Arbeit (Stand 23.10.2026, nachts)

Reihenfolge laut Tobias: 1. Historie 2018–2025 nachholen, 2. Ranking der Insider, GuruFocus-Ausbau erst danach.

**Historie über EQS News** (eqs-news.com), Recherche in `.recherche/` (nicht committen):
- Firmen-ID per ISIN: `https://www.eqs-news.com/de/search-results/?searchtype=company&searchword=<ISIN>` → Link `company/<slug>/news/<uuid>`
- Nachrichtenliste je Firma: GET `https://www.eqs-news.com/wp/wp-admin/admin-ajax.php?lang=de` mit `action=fetch_eqs_financial_news_data, pageLimit=30, pageNo=N, loadFrom=mysql, companyId=<uuid>, companyName=<uuid>, parseBy=newsgrouping`. Liefert HTML; leere Antwort = Ende. Reicht bis etwa 2010 zurück. Directors' Dealings haben `/news/directors-dealings/` in der URL.
- Meldungstext = einheitliches MAR-Formular: Name, Position, „steht in enger Beziehung zu“ (Vorname/Nachname/Position – damit lassen sich Holdings einer Führungskraft zuordnen, was die BaFin-CSV nicht kann), Art des Instruments, ISIN, Art des Geschäfts, Preis/Volumen, aggregiert, Datum des Geschäfts, Ort, **Veröffentlichung mit Uhrzeit**.
- `pipeline/eqs.py`: `firma_uuid(isin)`, `dd_links(uuid, ab)`, `meldung_lesen(url)` → Zeilen im Format von meldungen.csv plus `bezug_person`, `bezug_position`, `korrektur`, `quelle`, `url`. An Meldungen von 2021 und 2026 getestet; Wiederholung bei Netzfehlern eingebaut.
- **Abdeckung geprüft (23.10.2026):** EQS hat ~88 % der BaFin-Meldungen der letzten 12 Monate (Zählung je Firma in `.recherche/fertig.log`). Fehlt ganz: Siemens Energy, Bayer, Fresenius, BMW. Teilweise: Lufthansa, LEG, Wacker, Renk. EQS zählt je Firma, nicht je Aktiengattung (Sartorius, Fuchs). **Tobias hat entschieden: mit 88 % weitermachen, Lücke auf der Methode-Seite offen benennen.**
- EQS hat oft mehr Meldungen als die BaFin-Zählung (z. B. Zalando 74 vs. 22); keine Sprach-Duplikate, sondern viele Einzelmeldungen.

**Stand 22.10.2026 vormittags:**
- Abgleich Geschäft für Geschäft (Zalando, Deutz, SAP, letzte 12 Monate): 148 von 149 BaFin-Geschäften exakt bei EQS gefunden; Mitteilungsdatum und Position 100 % gleich. Ausreißer: EQS behält widerrufene Meldungen (Zalando 05.08.2026, 4,9 Mio. €, später „hat nicht stattgefunden“), die BaFin löscht sie.
- `historie.py` + Action `.github/workflows/historie.yml` („Historie laden“, per Knopfdruck, max. 320 Min., speichert nach jeder Firma in `daten/eqs_historie.csv` und `daten/eqs_fortschritt.csv`, setzt bei Neustart fort). Lokal mit 3 Min. getestet. Titel mit eindeutig anderer Art als Kauf/Verkauf werden übersprungen (`eqs.nur_zuteilung`).
- Beide Workflows machen vor dem Push `git pull --rebase`, weil sie parallel committen können.

**Lauf 1 der Action (22.10.2026):** unvollständig, weil EQS GitHub still gedrosselt hat (leere Antworten mit Status 200) und der Code das als Listenende wertete. Folge: Listen brachen ab (SAP erst ab 2022, Zalando ab 2025), Firmen ohne Treffer. Behoben in `pipeline/eqs.py` (`_seite`: leere Seite → Seite 1 gegenprüfen, sonst warten 30/60/120/240 s; `Gedrosselt`; Meldung ohne Inhalt = Fehler, Firma bleibt offen) und Pause 2 s. `eqs_fortschritt.csv` von Lauf 1 liegt in `.recherche/`, die geladenen Geschäfte bleiben und werden nicht erneut abgerufen. Nicht unterstützt: luxemburgisches HOS-2-Formular (Aroundtown), nur englische Meldungen.

**Nächste Schritte:**
1. Tobias pusht und startet „Historie laden“; Ergebnis prüfen (Anzahl je Firma in `eqs_fortschritt.csv`, Stichproben).
2. ~~Zusammenführen~~ erledigt lokal (22.10.2026, noch nicht gepusht – erst nach Lauf 2 pushen, sonst rechnet die Live-Seite mit unvollständiger Historie): `pipeline/meldungen.py` `lade_alle()` = BaFin + EQS vor erster BaFin-Meldung, Korrekturen ersetzen Vorgänger; `lauf.py` nutzt es, Kurse ab 2017; Firmen-Kursdiagramm mit 5 Jahre/Alles; Texte auf Start-, Methode-, Impressum-Seite (Quellen, 88 %, Indexzusammensetzung). Test mit Lauf-1-Daten: 1.126 Ereignisse; Käufe AAR t0 +0,21 %*, t+1 +0,22 %* (BA: +0,33 % t+1), Verkäufe t+1 −0,52 %*.

**Ranking (gebaut 22.10.2026, lokal, noch nicht gepusht):** Tobias' Entscheidungen: 3 Monate (60 Handelstage), nur Käufe, mind. 3 Käufe. Maß: Überrendite = Aktienrendite − Indexrendite (DAX/MDAX) ab Schlusskurs des Geschäftstags (Marktmodell über 60 Tage zu unzuverlässig). Sortiert nach Median (Ausreißer, z. B. Bertermann/Auto1: Ø +30 %, Median −0,8 %). Holdings über `bezug_person` der Führungskraft zugeordnet; Titel für Namensabgleich entfernt (nur mit Punkt). `pipeline/ranking.py`, `docs/data/ranking.json`, Tabelle auf Start- und Firmenseite, Abschnitt auf Methode-Seite. Handrechnung Elmos/Meyer stimmt (+34,6 %).

**Leser-Fehler gefunden (22.10.2026):** Meldungen bis 2020 schreiben Betrag und Währung in getrennte Zeilen → Volumen/Preis leer (fast alle von 2018/2019). Behoben mit `eqs._aggregiert`. Bereits geladene Zeilen reparieren: `historie.py --reparieren` bzw. Action-Häkchen „reparieren“.

**Reihenfolge nach Lauf 2:** 1. Tobias pusht den lokalen Stand, 2. „Historie laden“ mit Häkchen „reparieren“, 3. „Daten aktualisieren“ manuell starten, 4. Ergebnis prüfen (Jahre 2018/2019 vs. BA-Daten, Ranking, Event Study).

Skript-/Stil-Dateien haben `?v=2` (Cache von GitHub Pages bis 10 Min.); bei JS/CSS-Änderungen hochzählen.

## Offen

- [x] Impressum ausgefüllt (23.10.2026), aber noch nicht gepusht
- [ ] Geschwärzte Bachelorarbeit auf der Methode-Seite verlinken? PDF liegt in Dropbox unter `BA GEDRUCKT/Für Website:Github/BA geschwärzt für Website.pdf`. Entscheidung von Tobias steht aus.
- [ ] GitHub-Token „Insiderhandel Test 1 Github Actions“ läuft nie ab → löschen und bei Bedarf ein neues mit 90 Tagen anlegen (Rechte: Contents und Workflows, Read and write)
- [ ] Überzähligen zweiten Telegram-Bot in BotFather löschen (`/deletebot`)
- [ ] Tooltips beim Darüberfahren im echten Browser prüfen (im Test nicht simulierbar)
- [ ] Vierteljährlich nach Indexänderungen (März, Juni, Sept., Dez.): `python3 -m pipeline.firmen`, Ergebnis prüfen; Korrekturen stehen in `ISIN_ERSATZ` und `TICKER_KORREKTUR`
- [ ] Bekannte Lücken: BMW-Vorzüge (keine Yahoo-Kurse), alte TUI-ISIN
- [ ] Historie 2018–2025 nachholen: prüfen, ob das EQS-Archiv sich sauber abrufen lässt
- [ ] Beobachten: GitHub deaktiviert geplante Läufe nach 60 Tagen ohne Aktivität; unklar, ob Bot-Commits zählen
- [ ] Später: Ranking „Insider mit dem besten Timing“, GuruFocus-Ausbau (Fundamentaldaten, Bewertungen, weitere Indizes)
