# Insider-Monitor – Stand der Dinge

Directors' Dealings (Art. 19 MAR) von DAX- und MDAX-Firmen seit 2018, live ausgewertet mit der Event Study aus
Tobias' Bachelorarbeit (Uni Bayreuth). Langfristiges Ziel: eine Art GuruFocus für deutsche Aktien.

- Website: https://insider.tobiaszwilling.me (GitHub Pages aus `/docs`, Branch `main`)
- Repository: github.com/tobzwil89/insider (öffentlich); DNS bei Namecheap, CNAME `insider` → `tobzwil89.github.io`
- Technische Übersicht (Dateien, Befehle): README.md; Vorbild-Analyse: GURUFOCUS.md

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
- **EQS behält widerrufene Meldungen** (z. B. Zalando 05.08.2026, 4,9 Mio. €), die BaFin löscht sie. Selten.
- **Kurse:** Yahoo, bereinigt. BMW-Vorzüge ohne Kurse. Indexzusammensetzung ist die heutige (Survivorship).
- **Volumen in Fremdwährung** (GBp, USD) werden nicht umgerechnet; betrifft v. a. TUI.

## Offen

- [ ] **Push der neuen Taktung** (`13,43 * * * *`) und nach 1–2 Tagen Anzahl der geplanten Läufe prüfen.
- [ ] Diagramm auf der Firmenseite einmal auf dem echten Handy ansehen.
- [ ] Code-Review (`/code-review high`) in einem neuen Chat.
- [ ] **Datenquelle für Fundamentaldaten klären**, bevor der GuruFocus-Ausbau beginnt: Yahoo (gratis, ~4 Jahre,
      lückenhaft), EODHD / Financial Modeling Prep (~20–30 €/Monat), Bundesanzeiger (gratis, mühsam).
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
