# Insider-Monitor – Stand der Dinge

Directors' Dealings (Art. 19 MAR) von DAX- und MDAX-Firmen seit 2018, live ausgewertet mit der Event Study aus
Tobias' Bachelorarbeit (Uni Bayreuth). Langfristiges Ziel: eine Art GuruFocus für deutsche Aktien.

- Website: https://insider.tobiaszwilling.me (GitHub Pages aus `/docs`, Branch `main`)
- Repository: github.com/tobzwil89/insider (öffentlich); DNS bei Namecheap, CNAME `insider` → `tobzwil89.github.io`
- Technische Übersicht (Dateien, Befehle): README.md; Vorbild-Analyse: GURUFOCUS.md
- Alte Projekte (Sentiment-Tracker, StockPulse, GuruFocus-Analyse) und was davon übernehmbar ist: BESTANDSAUFNAHME.md

## Arbeitsweise

- **Diese Datei nach jedem Schritt aktualisieren** (Tobias' ausdrücklicher Wunsch): Stand, Offen, Verlauf.
- Der Bot committet `daten/` und `docs/` selbst. Vor jedem eigenen Push `git pull` (pull.rebase=true).
  Lokale Testläufe von `lauf.py` verändern `docs/data` und `daten/meldungen.csv` → vor dem Commit mit
  `git checkout -- docs/data daten/meldungen.csv` zurücksetzen, sonst Konflikte mit dem Bot.
- Tobias pusht selbst (kein `gh`, Token mit Rechten Contents + Workflows). Ich committe/pushe nicht.
- Recherche und Screenshots in `.recherche/` (in `.gitignore`).

## Aktueller Stand (22.10.2026 abends)

**Live:** BaFin-Meldungen ab 22.10.2025 (alle 30 Min.) plus EQS-Archiv 2018 bis 21.10.2025; Event Study über
1.572 Ereignisse; Cluster-Käufe mit Telegram; Ranking „Timing der Insider“ (265 Personen); Impressum ausgefüllt.
Ergebnis: Käufe AAR t0 +0,24 %*, t+1 +0,23 %*, vorher signifikant negativ; Verkäufe t+1 −0,41 %*.
Jahreszahlen EQS passen zu den BA-Daten (2018: 211 vs. 239, 2019: 219 vs. 194, 2021: 497 vs. 452).

**Seit 22.10.2026 abends ebenfalls live** (Umsetzung GURUFOCUS.md Punkt 1–4): Firmenseiten als fertiges HTML unter
`/firma/<TICKER>/` (`pipeline/seiten.py`, Texte mit `html.escape`, Markierungen als eingebettetes JSON), Kurse in
`docs/data/kurse/<TICKER>.json`, Weiterleitung `firma.html?t=…`, `sitemap.xml`, `robots.txt`, automatische
Versionsnummern `?v=<Prüfsumme>`, Speculation Rules auf der Startseite. `ereignisse.json` und `data/firmen/` entfernt
(7,5 → 4,8 MB). GBp-Fix (TUI/Unifirm, 16 Meldungen repariert). Live geprüft: 6 Firmenseiten antworten (200),
Deutz/SAP per Screenshot korrekt, Diagramm auch bei 500 px Breite (63 Markierungen bei Rheinmetall).

**Befund Taktung (22.10.2026):** Mit `*/30` hat GitHub in 17 Stunden nur 3 geplante Läufe gestartet (alle erfolgreich).
Geändert auf `13,43 * * * *` (krumme Minuten, lokal, **noch nicht gepusht**). Nach 1–2 Tagen prüfen:
`curl -s "https://api.github.com/repos/tobzwil89/insider/actions/workflows/aktualisieren.yml/runs?per_page=100"`.
Reicht das nicht, externen Auslöser nehmen (z. B. cron-job.org ruft `workflow_dispatch` über die GitHub-API auf;
braucht ein Token mit Actions-Recht).

**Abgleich mit dem ursprünglichen Plan** (Auftrag vom 21.10.2026): Action prüft BaFin regelmäßig ✅ (Taktung s. o.),
Kurse + AR nach BA-Methode + JSON ✅, GitHub Pages unter insider.tobiaszwilling.me ✅, Live-Ticker ✅, Cluster-Käufe ✅,
Kurs mit Insider-Markierungen ✅, CAR-Kurve Käufe vs. Verkäufe laufend ✅, Ranking bestes Timing ✅, Telegram bei
Clustern ✅, „keine Anlageberatung“ + Impressum ✅. Zusätzlich: Historie 2018–2025 aus EQS, Methode-Seite, Firmenseiten als HTML.

**Was manuell bleibt** (alles andere läuft automatisch):
1. Vierteljährlich nach Indexänderungen (März, Juni, Sept., Dez.): `python3 -m pipeline.firmen`, Ergebnis prüfen, pushen;
   danach „Historie laden“ starten (lädt nur neue Firmen, weil die Fortschrittsliste sie nicht kennt).
2. Bei E-Mail von GitHub über einen fehlgeschlagenen Lauf: nachsehen (meist BaFin/Yahoo/EQS kurz nicht erreichbar,
   der nächste Lauf holt alles nach; dauerhaft nur bei Formatänderungen der Quellen).
3. Gelegentlich prüfen, ob die geplanten Läufe noch aktiv sind (60-Tage-Regel; der tägliche Lauf committet immer,
   das sollte als Aktivität reichen).

**Review:** `/code-review ultra` ist kostenpflichtig (nicht kostenlos). Empfehlung: `/code-review high` lokal in einem
neuen Chat (frischer Blick, kein Zusatzpreis über die normale Nutzung hinaus), vor dem GuruFocus-Ausbau.

## Laufendes Vorhaben: Stimmrechtsmitteilungen (§§ 33 ff. WpHG) ab 2018

Auftrag Tobias 22.10.2026: Stimmrechte aus EQS, Historie **ab 2018**, in Blöcken, die man jederzeit abbrechen kann und
die nicht auf Tobias' Rechner laufen (GitHub Action). Alles laufend hier notieren. Danach: Rückkäufe. Probe-Ergebnisse:
`.recherche/eqs_stimmrechte_rueckkaeufe.md`.

- [x] **Block 1 – Leser (22.10.2026):** `pipeline/stimmrechte.py` liest Abschnitt 3 (wer, Sitz), 5 (Schwellendatum),
      6 (Aktien/Instrumente/Summe neu und vorher, Gesamtstimmrechte), Deutsch und Englisch, alte Formulare (Name dann
      aus dem EQS-Seitenkopf). Andere Formulare derselben Kategorie (eigene Aktien, § 43 WpHG, Rücknahmen) →
      `formular=anderes` mit leeren Werten. `eqs.dd_links` hat dafür den Parameter `kategorie` bekommen (Standard unverändert).
- [x] **Block 2 – Historie-Lader (22.10.2026):** `stimmrechte_laden.py` + `.github/workflows/stimmrechte.yml`
      („Stimmrechte laden“). Speichert nach jeder Firma, `if: always()` speichert auch nach Abbruch. Nutzt die
      EQS-IDs aus `eqs_fortschritt.csv`. **Lokal getestet** an SAP, Zalando, Deutz AG: 720 Mitteilungen in 35 Min.
      (~3 s je Mitteilung), Abbruch nach 1 Min. und Fortsetzen geprüft (7 nicht doppelt geladen), keine leeren
      Pflichtfelder, Summe = Aktien + Instrumente bei allen. Die 3 Firmen liegen schon in `daten/stimmrechte*.csv`
      und werden von der Action übersprungen. Die Action selbst ist erst nach dem Push testbar.
- [ ] **Block 3 – Historie laden** (Tobias): committen, pushen, unter Actions „Stimmrechte laden“ → „Run workflow“.
      Wiederholen, bis im Protokoll „Alle Firmen fertig“ steht. Schätzung nach Test: 13.000–23.000 Mitteilungen
      (Zalando 441, SAP 121, Deutz 158), also 11–19 h = **3–4 Läufe à 320 Min.** Danach prüfen:
      `stimmrechte_fortschritt.csv` hat alle Firmennamen aus `firmen.csv`, `formular=anderes` stichprobenartig ansehen.
      - Gepusht (df81c7f). **Lauf 1** (22./23.10., 5 h 20 min, Erfolg, Commit aa77184): 34 von 90 Firmen fertig
        (bis „Fuchs Petrolub“), 6.735 Mitteilungen, keine doppelt, keine leeren Pflichtfelder. Auto1, Delivery Hero,
        GEA angefangen, aber offen (einzelne Abrufe fehlgeschlagen, vermutlich EQS-Drosselung → nächster Lauf holt nur
        die fehlenden). Airbus und DWS ohne Mitteilungen (Airbus: ausländisch). Ø 159 Mitteilungen je Firma →
        Rest ~8.000, also **noch 2 Läufe**.
      - 214 × `anderes`: 74 eigene Aktien, 13 × § 43, Korrekturen; **Aroundtown 60** (luxemburgisches Formular, wie bei
        Directors' Dealings nicht unterstützt) und ~40 verstreute (Elmos 9, Delivery Hero 7, Beiersdorf 6 …), noch nicht angesehen.
- [ ] **Block 4 – Laufend aktuell halten:** neue Mitteilungen im täglichen Lauf.
- [ ] **Block 5 – Anzeige:** Bereich „Großaktionäre“ auf den Firmenseiten (je Halter letzter Stand, Aktien und Instrumente getrennt).

## Entscheidungen (mit Grund)

- **Neu statt BA-Code übernommen:** Der alte Code (Dropbox `Uni/Universität Bayreuth/Bachelorarbeit/Code für Analyse
  Final für Bachelorarbeit.rtf`) rechnete in Kalendertagen, zählte Teilausführungen mehrfach (2.409 statt 1.910),
  mischte Prozent/Dezimal bei Fama-French, nutzte unbereinigte Kurse; Daten von finanzen.net ohne klares Datum.
- **t = 0 = Mitteilungsdatum** (BaFin schaltet oft 1–3 Tage später frei; Firmen veröffentlichen vorher über EQS).
- **Ereignis = Firma + Mitteilungstag + Richtung**; nur Vorstand/Aufsichtsrat, nur Aktien, nur Kauf/Verkauf.
- **Nur Marktmodell** (DAX/MDAX), Schätzfenster −130 bis −11, Ereignisfenster ±5 Handelstage, ≥ 100 Schätztage.
  Fama-French entfällt (Faktoren erscheinen monatlich mit Verzögerung).
- **Cluster:** ≥ 3 Personen (ohne eng verbundene) in 14 Tagen nach Geschäftsdatum, ≥ 50.000 €
  (filtert Mitarbeiterprogramme, z. B. ProCredit).
- **ISIN als feste ID**, Ticker für Anzeige und Adresse.
- **Historie aus EQS mit ~88 % Abdeckung** (Tobias: keine Zusatzquellen für den Rest). Lücke auf der Methode-Seite benannt.
- **Ranking** (Tobias): 3 Monate (60 Handelstage), nur Käufe, mind. 3 Käufe. Maß: Überrendite gegenüber DAX/MDAX
  ab Schlusskurs des Geschäftstags (Marktmodell über 60 Tage zu unzuverlässig). Sortiert nach Median
  (Ausreißer wie Auto1/Bertermann: Ø +30 %, Median −0,8 %). Holdings über `bezug_person` zugeordnet.
- **Statisch bleiben** (GitHub Pages), eigener Server erst bei Screener über viele Firmen, Nutzerkonten oder Echtzeit.

## Datenquellen und bekannte Lücken

- **BaFin** (`pipeline/bafin.py`): CSV-Export, rollierend 12 Monate, alle Emittenten. `daten/meldungen.csv` wird nur ergänzt.
- **EQS News** (`pipeline/eqs.py`, `historie.py`, Action „Historie laden“): Firmen-ID per ISIN-Suche, Nachrichtenliste über
  `admin-ajax.php?action=fetch_eqs_financial_news_data`, Meldungstext im MAR-Formular. EQS drosselt still (leere
  Antworten mit Status 200) → `_seite` prüft gegen Seite 1 und wartet. Pause 2 s.
  Abgleich mit BaFin (Zalando, Deutz, SAP): 148/149 Geschäfte exakt gleich, Datum und Position 100 %.
- **Lücken 2018–10/2025** (geprüft an `eqs_historie.csv`): Bayer und BMW nur bis 05/2020, Siemens Energy nur bis 11/2023
  (Verteiler gewechselt); Qiagen, RTL Group gar nicht (Ausland); Aroundtown (HOS-2-Formular, nicht unterstützt).
  Fresenius, FMC, LEG, Lufthansa, Wacker, Renk sind vorhanden. 7 EQS-Geschäfte ohne lesbares Volumen.
  Achtung: Spalte `geschaefte` in `eqs_fortschritt.csv` zählt nur das im jeweiligen Lauf neu Geladene, nicht den Bestand.
- **Stimmrechte** (`pipeline/stimmrechte.py`, `stimmrechte_laden.py`): EQS-Kategorie `stimmrechtsanteile`.
  Viel Rauschen durch Vermögensverwalter (Zalando: Morgan Stanley 161, BlackRock 153 von 441; SAP: BlackRock 84 von 121;
  Deutz: DWS 82 von 158) → Anzeige je Halter nur letzter Stand, Aktien und Instrumente getrennt. Zurückgenommene
  Mitteilungen erscheinen als eigene Meldung („Rücknahme der Veröffentlichung …“), das Original bleibt in den Daten.
- **EQS behält widerrufene Meldungen** (z. B. Zalando 05.08.2026, 4,9 Mio. €), die BaFin löscht sie. Selten.
- **Kurse:** Yahoo, bereinigt. BMW-Vorzüge ohne Kurse. Indexzusammensetzung ist die heutige (Survivorship).
- **Volumen in Fremdwährung** (GBp, USD) werden nicht umgerechnet; betrifft v. a. TUI.

## Offen

- [ ] **Taktung reicht nicht:** gepusht, aber geprüft am 24.10.2026: nur 12 geplante Läufe in ~1,5 Tagen (23.10.: 6 statt
      ~48), alle erfolgreich. Neue Meldungen kommen also mit Stunden Verspätung. Abhilfe: externer Auslöser (cron-job.org
      ruft `workflow_dispatch` über die GitHub-API auf; braucht ein Token mit Actions-Recht). Entscheidung Tobias.
- [ ] Diagramm auf der Firmenseite einmal auf dem echten Handy ansehen.
- [ ] Code-Review (`/code-review high`) in einem neuen Chat.
- [ ] **Datenquelle für Fundamentaldaten klären**, bevor der GuruFocus-Ausbau beginnt: Yahoo (gratis, ~4 Jahre,
      lückenhaft), EODHD / Financial Modeling Prep (~20–30 €/Monat, Lizenz für öffentliche Anzeige prüfen),
      Unternehmensregister (gratis, nur von Hand). ESEF-Probe 22.10.2026 (`.recherche/esef_probe.md`): filings.xbrl.org
      hat keine deutschen Berichte; freier Weg erst über ESAP (EU-Portal, spätestens 10.07.2027). Tobias (22.10.2026):
      nach hinten verschoben, zuerst Stimmrechte und Rückkäufe aus EQS.
- [ ] **Repository-Größe beobachten:** Der Bot committet bei jedem Lauf mehrere MB; GitHub empfiehlt < 1 GB.
      Beim GuruFocus-Ausbau Daten in eigenen Branch oder Release-Dateien auslagern.
- [ ] Geschwärzte Bachelorarbeit auf der Methode-Seite verlinken? PDF in Dropbox unter
      `BA GEDRUCKT/Für Website:Github/BA geschwärzt für Website.pdf`. Entscheidung von Tobias steht aus.
- [ ] GitHub-Token „Insiderhandel Test 1 Github Actions“ läuft nie ab → löschen, bei Bedarf neu mit 90 Tagen.
- [ ] Überzähligen zweiten Telegram-Bot löschen (`/deletebot`).
- [ ] Tooltips im echten Browser prüfen (im Headless-Test nicht simulierbar).
- [ ] Vierteljährlich nach Indexänderungen (März, Juni, Sept., Dez.): `python3 -m pipeline.firmen`, prüfen;
      Korrekturen in `ISIN_ERSATZ`/`TICKER_KORREKTUR`. Danach `historie.py` für neue Firmen (Fortschrittsliste kennt sie nicht).
- [ ] Beobachten: GitHub deaktiviert geplante Läufe nach 60 Tagen ohne Aktivität (Bot-Commits zählen vermutlich).
- [ ] Fremdwährungs-Volumen (GBp/USD) in Euro umrechnen, falls Cluster/Volumen-Anzeigen das brauchen.

## Verlauf

- **21./22.10.2026 (Nacht):** BA-Code und -Daten geprüft; Datenpipeline (BaFin, Kurse, Event Study, Cluster, Export),
  GitHub Action alle 30 Min., Telegram, Website (Start, Firma, Methode, Impressum), Domain live.
- **22.10.2026:** EQS als Quelle für 2018–2025 gefunden und validiert; Action „Historie laden“. Lauf 1 unvollständig
  (stille Drosselung) → Erkennung eingebaut, Lauf 2 vollständig. Leser-Fehler „Betrag und Währung in getrennten Zeilen“
  (bis 2020) behoben und repariert. Zusammenführen BaFin + EQS (`pipeline/meldungen.py`). Ranking gebaut und live.
  GuruFocus-Analyse (GURUFOCUS.md) bewertet; Punkte 1–4 umgesetzt und live, GBp-Fehler behoben.
  Abschlussprüfung: Firmenseiten live geprüft, Plan vollständig umgesetzt, Taktungsproblem gefunden (3 statt ~34 Läufe)
  → Cron auf krumme Minuten.
- **22.10.2026 abends:** ESEF-Probe für Fundamentaldaten (SAP, Deutz, Zalando): kein freier automatischer Weg für
  deutsche Firmen vor ESAP; SEC-Daten sauber, aber nur 4 von 97 Firmen. Details `.recherche/esef_probe.md`.
  Tobias: Fundamentaldaten nach hinten. EQS-Probe Stimmrechte/Rückkäufe (SAP, Zalando, Deutz): beide über die
  vorhandene Nachrichtenliste erreichbar (Kategorie im Pfad). Stimmrechte = einheitliches Formular (DE/EN), viel
  BlackRock-Rauschen; Rückkäufe ohne einheitliches Tabellenformat. Details `.recherche/eqs_stimmrechte_rueckkaeufe.md`.
  Tobias: Stimmrechte zuerst, Historie ab 2018, in abbrechbaren Blöcken auf GitHub, alles hier notieren.
  Block 1 (Leser) und Block 2 (Lader + Action) gebaut und an 3 Firmen getestet; wartet auf Push und Start (Block 3).
- **22.10.2026 spät:** Bestandsaufnahme alter Projekte (`BESTANDSAUFNAHME.md`). Tobias: langfristig Sentiment-Score und
  mehr Aktien als DAX/MDAX. Empfehlung: Sentiment zuerst aus EQS-Ad-hoc-Meldungen, Universum zuerst übrige deutsche Aktien, dann USA (SEC).
- **24.10.2026:** Stand Stimmrechte geprüft: Lauf 1 erfolgreich, 34/90 Firmen, 6.735 Mitteilungen; noch 2 Läufe (Details Block 3).
