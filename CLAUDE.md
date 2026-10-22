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

**Nächste Schritte:**
1. Tobias pusht und startet „Historie laden“; Ergebnis prüfen (Anzahl je Firma in `eqs_fortschritt.csv`, Stichproben).
2. Zusammenführen: `bafin.lade_meldungen()` um `eqs_historie.csv` ergänzen (Spalte `quelle`), nur EQS-Zeilen vor Beginn der BaFin-Daten (22.10.2025) verwenden. Gekennzeichnete Korrekturmeldungen ersetzen ältere Meldungen mit gleicher ISIN/Person/Geschäftsdatum. Event Study über 2018–heute, Kurse ab 2017 laden, Methode-Seite anpassen (Quellen, 88 %-Lücke).

**Ranking (danach; Idee, noch nicht mit Tobias abgestimmt):** je Person abnormale Rendite 20/60 Handelstage nach dem Geschäftsdatum, Verkäufe mit umgekehrtem Vorzeichen, mindestens 3 Geschäfte, Trefferquote dazu; Holdings über „in enger Beziehung zu“ der Führungskraft zuordnen; nüchterne Darstellung ohne wertende Sprache.

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
