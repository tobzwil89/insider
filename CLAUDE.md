# Insider-Monitor / Rhodus – Stand der Dinge

Directors' Dealings (Art. 19 MAR) von DAX- und MDAX-Firmen seit 2018, live ausgewertet mit einer Event Study, dazu
Großaktionäre, Rückkäufe, Guru-Depots, Personenseiten und US-Firmen. Das ist Tobias' **Startup** (Produktname
**Rhodus**): eine Finanzdaten-Plattform wie GuruFocus, global, günstiger. Alleinstellungsmerkmal soll eine
**Sentimentanalyse von Reddit und X für Krypto und Pennystocks** werden (Tobias 06.11.2026); alles Bisherige haben
etablierte Anbieter auch.

- Website: https://insider.tobiaszwilling.me (GitHub Pages aus `/docs`, Branch `main`)
- Repository: github.com/tobzwil89/insider (öffentlich); DNS bei Namecheap, CNAME `insider` → `tobzwil89.github.io`

## Dateien zum Nachlesen

Diese Datei ist absichtlich kurz (wird bei jedem Start geladen). Details stehen hier:
- `VORHABEN.md`: jedes Vorhaben im Detail (Plan, Prüfungen, Zahlen, Begründungen), Anhang mit den alten Listen
  Entscheidungen/Datenquellen/Offen in voller Länge. **Vor Arbeit an einem Vorhaben den passenden Abschnitt lesen.**
- `VERLAUF.md`: was wann gemacht wurde.
- `README.md` (Dateien, Befehle), `GURUFOCUS.md` (Vorbild), `DATENQUELLEN.md` (Quellen für den Ausbau, Abschnitte 1–14),
  `ALTERNATIVE_DATEN.md` (Rechtslage, Meldeschwellen), `BESTANDSAUFNAHME.md` (alte Projekte), `ARCHITEKTUR.md`
  (Zielarchitektur), `RECHTSFRAGEN.md` (#74 Kongressdaten, #75 Datenschutz Personenseiten), `US_KONGRESS_OFFEN.md`.
- Sicherung der alten, langen CLAUDE.md: `.recherche/sicherung_claude_md/CLAUDE_2026-11-09.md`.

## Arbeitsweise (bitte einhalten)

- Deutsch, einfache Sprache, direkt; widersprechen, wenn Tobias falschliegt; klare Empfehlung statt Optionsliste.
- **Startup-Sicht:** Quellen nach Nutzen fürs Produkt bewerten. In der Recherche alles aufnehmen, auch graue Wege
  (Cookies, Bot-Sperren); Rechtslage nur als Hinweis „vor dem Start klären“.
- **Nicht ungefragt bauen:** „Ist X nützlich?“ ist eine Recherchefrage, kein Bauauftrag. Bei schweren Datenquellen
  fertige Lösungen bevorzugen, bei einfachen schlank selbst bauen.
- **Notieren nach jedem Schritt:** Kurzstand hier (Abschnitt „Stand je Vorhaben“), Details in `VORHABEN.md`, eine Zeile
  in `VERLAUF.md`. Diese Datei kurz halten, nichts Ausführliches hier anhängen.
- Aufgaben aus der Planungs-App (`~/planung/tasks.json`): erst `~/planung/ANLEITUNG_FUER_CLAUDE.md` lesen.
- **Tobias pusht selbst** (kein `gh`). Am Ende jedes Schritts die Befehle als Codeblock geben: Dateien einzeln
  `git add`, nie `git add .`; `.env` (API-Schlüssel) ist in `.gitignore`. Claude committet/pusht nicht.
- **Push-Reihenfolge:** erst `git add …` + `git commit`, dann `git pull --autostash`, dann `git push`. Ein `git pull`
  vor dem Commit scheitert, sobald irgendeine Datei ungesichert geändert ist (pull.rebase=true, andere Sitzungen
  ändern oft `DATENQUELLEN.md` o. Ä.). Dateien anderer Sitzungen nicht mit hinzufügen.
- Der Bot committet `daten/` und `docs/` selbst. Lokale Läufe verändern `docs/` → nicht committen, vorher
  zurücksetzen: `git checkout -- docs/data docs/firma docs/sitemap.xml docs/*.html docs/gurus daten/meldungen.csv`.
- **Push-Schutz:** `.git/hooks/pre-push` importiert alle Pipeline-Module und Lade-Skripte im hochzuladenden Stand;
  fehlt eine nur lokal geänderte Datei, stoppt der Push. Neue Skripte, die eine Action startet, dort eintragen.
  Lehre 31.10.2026: vor dem Push prüfen, ob committete Dateien von nur lokal geänderten abhängen.
- Nach Änderungen an `seiten.py`/`export.py`: Action „Daten aktualisieren“ mit Haken „immer“ starten, sonst baut der
  Bot die Seiten erst bei der nächsten neuen BaFin-Meldung neu.
- Vor neuen HTML-Ids nach vorhandenen suchen (Fehler 07.11.2026: `#cluster`/`#firmen` doppelt, Startseite zerschossen).
- Lokal ansehen: `PYTHONPATH=. python3 .recherche/seiten_lokal.py`, dann `python3 -m http.server 8765 --directory docs`.
  Bildschirmfoto: Chrome `--headless=new --screenshot=… http://localhost:8765/...`.
- Recherche, Sicherungen und Bildschirmfotos in `.recherche/` (in `.gitignore`).
- **Nur lokal, nie pushen** (`.gitignore`): Kongress-/Trump-Daten (`daten/kongress*.csv`, `abgeordnete.csv`,
  `trump.csv`, `docs/politiker/`; Grund 5 U.S.C. § 13107(c)), Fundamentaldaten (`fundamental.csv`, `kennzahlen.csv`;
  inoffizielle Quellen), `kurse_us.parquet`, `lobbying_berichte.csv`, `sec_tickers.json`.
- **Vor dem Livegang:** Skill `/unslop` über die Seite laufen lassen, Audit zuerst Tobias zeigen; Designentscheidungen trifft Tobias.
- **Vor dem Start einer Bezahlstufe:** im Impressum den Satz „privates, nichtkommerzielles Projekt“ (Abschnitt
  „Keine Anlageberatung“) streichen. Dann wird die Frage zu den Kongressdaten (#74, `RECHTSFRAGEN.md`) akut.

## Stand je Vorhaben (Kurzfassung, Details in `VORHABEN.md`)

**Live und automatisch** (Action „Daten aktualisieren“, über cron-job.org ~48 Läufe/Tag, seit 02.11. stabil):
BaFin-Meldungen + EQS-Archiv 2018–2025, Event Study, Cluster-Käufe mit Telegram, Ranking „Timing der Insider“,
Firmenseiten `/firma/<TICKER>/` mit Kursdiagramm, Kapitelleiste, Logos, Aktionärsring, Rückkäufen.

- **Stimmrechte / Großaktionäre:** erledigt (30.10.2026), nachts aktualisiert. Offen: 806 Fließtexte 2008–2012
  (DeepSeek, verschoben), Henkel-Poolmeldungen als `anderes`, geprüfte Liste jährlich abgleichen.
- **Aktionärsring:** erledigt (31.10.2026), Median „mit Namen bekannt“ 50,5 %. Pflege: BMW-Aktienzahl, Qiagen/RTL/Airbus
  ohne Gesamtzahl, Bio-Rad bei Sartorius-Vorzügen, `aktiengattungen.csv` jährlich, Airbus/RTL bessere Quellen.
- **Rückkäufe:** erledigt, nachts aktualisiert. Offen: Scout24-Abweichungen, `art=anderes`, laufende Programme anzeigen.
- **Fundamentaldaten:** fertig, **nur lokal** (Eulerpool + TradingView + onvista + SEC + Nasdaq), nicht weiter ausbauen.
  Offen: Rechtslage vor dem Livegang; legaler Weg Eulerpool Builder 99 $/Monat.
- **Guru-Depots (13F):** live unter `/gurus/`. Offen: Bereich beim Ausbau richtig einbinden, Nachträge 13F-HR/A.
- **Firmenlogos:** live. Offen: Tobias sieht Verdachtsfälle durch (Nordex, TUI, Jenoptik, Hella, Porsche AG, Fuchs);
  Logos fehlen noch in Ticker/Cluster/Ranking.
- **Personenseiten** (803 Vorstände/Aufsichtsräte, `/person/`): **live.** Datenschutzabsatz `#personen` in
  `docs/impressum.html` eingebaut 09.11.2026 (#75, Text aus `RECHTSFRAGEN.md` Abschnitt 2). Lücken der Erklärung behoben
  09.11.2026 (Verantwortlicher, Art. 77/BayLDA, Gesellschaften, Quellen). Offen: Anwalt liest gegen. Nebenbefund: 13 Geschäfte doppelt (gleiche Meldung an zwei Tagen bei EQS).
- **US-Politiker** (House + Senat 2012–2026, Trump 278-T): **nur lokal**, bis die Rechtsfrage #74 geklärt ist
  (`RECHTSFRAGEN.md` Abschnitt 1). Trump-Seite gebaut 08.11.2026 (91 % mit Kürzel). Offen: Erklärtexte der Trump-Seite
  sprechen noch von Kongress/Inhaber; Fotos, Branchen-Kuchen. Datensatz-Abhängigkeit: Hugging Face
  `austin-starks/congressional-stock-trades` (ein Betreiber).
- **US-Firmen S&P 500** (`/us/<KÜRZEL>/`): Staatsaufträge (USAspending), PAC-Spenden (FEC), **Lobbying** (LD-2 vom
  House-Clerk, 414 von 500 Firmen, gebaut 08.11.2026). **Live seit 09.11.2026** (Commit 099af96; Test ohne
  nur lokale Dateien: 500 Seiten, kein Kongress/Trump).
- **Marketing / Rhodus:** Name Rhodus, Logo-Paket `logo/kit/`, Farben Grün #1E3B2F / Creme #F3EEE2, Schrift Geist.
  Design System https://claude.ai/artifact/X1njLe2gDXmPDRtszcsTRN. Startseiten-Richtungen
  https://claude.ai/artifact/416CVL22JqidLmcVQwTuWf und https://claude.ai/artifact/QuKEGndLbFhxJ68DNuHuDe
  **warten auf Tobias' Wahl.** Sonntags-Report geht automatisch (samstags in Kit geplant für Sonntag 8 Uhr).
  Offen: 5–10 Anlegergespräche (`newsletter/GESPRAECHE.md`), Untertitel, englische Fassung, Kit-Datenschutz (USA).
- **Sentiment (Alleinstellungsmerkmal):** private Probe in `~/Desktop/Claude/sentiment-probe` (eigene CLAUDE.md);
  Reddit-Hype kommt nach dem Kursanstieg → als Hype-Warnung brauchbar. Nächster Schritt Krypto-Wale (#78,
  `DATENQUELLEN.md` Abschnitt 10). Planungs-App #1 (Scraper) läuft in einer anderen Sitzung.
- **Architektur:** entschieden Supabase (Postgres, gratis), Sammler bleiben in GitHub Actions; braucht ein
  Supabase-Konto von Tobias. Website-Technik offen.

## Was manuell bleibt

- Vierteljährlich nach Indexänderungen (März, Juni, Sept., Dez.): `python3 -m pipeline.firmen`, prüfen
  (`ISIN_ERSATZ`/`TICKER_KORREKTUR`), pushen, danach Action „Historie laden“ für neue Firmen.
- Vierteljährlich US: `python3 -m pipeline.us_firmen`, `pipeline.staatsauftraege`, `pipeline.spenden`,
  `pipeline.lobbying`; Ergebnis-CSVs committen.
- Kongressdaten (lokal) bei Bedarf: `python3 kongress_laden.py`, `python3 -m pipeline.kongress_datensatz`.
- Jährlich: `grossaktionaere_geprueft.csv` und `aktiengattungen.csv` prüfen.
- Bei Fehler-Mail von GitHub nachsehen (meist BaFin/Yahoo/EQS kurz weg). 60-Tage-Regel für geplante Läufe beobachten.

## Entscheidungen (Kurzfassung, Gründe in `VORHABEN.md` Anhang)

- t = 0 = Mitteilungsdatum; Ereignis = Firma + Mitteilungstag + Richtung; nur Vorstand/Aufsichtsrat, nur Aktien.
- Nur Marktmodell (DAX/MDAX), Schätzfenster −130 bis −11, Ereignisfenster ±5 Handelstage.
- Cluster: ≥ 3 Personen in 14 Tagen, ≥ 50.000 €. Ranking: 60 Handelstage, nur Käufe, ≥ 3 Käufe, Median der Überrendite.
- ISIN als feste ID, Ticker für Anzeige und Adresse. EQS-Historie mit ~88 % Abdeckung reicht.
- Architektur (31.10.2026, `ARCHITEKTUR.md`): Datenbank Supabase (Postgres, gratis), Sammler bleiben in GitHub Actions,
  0 € bis MVP; Website-Technik offen. Bis zur Umsetzung läuft die Seite weiter statisch auf GitHub Pages.

## Bekannte Lücken der Daten

- EQS 2018–10/2025: Bayer/BMW nur bis 05/2020, Siemens Energy bis 11/2023; Qiagen, RTL gar nicht; Aroundtown nicht lesbar.
- EQS drosselt still (leere Antworten mit Status 200) → Pause 2 s, Prüfung gegen Seite 1.
- Kurse: Yahoo, heutige Indexzusammensetzung (Survivorship). Volumen in GBp/USD nicht umgerechnet (v. a. TUI).

## Offen (allgemein)

- [ ] Anwaltsfragen #74 (Kongressdaten) klären; Datenschutzerklärung gegenlesen lassen (#75).
- [ ] Code-Review (`/code-review high`) in einem neuen Chat. Handyansicht und Tooltips im echten Browser prüfen.
- [ ] Repository-Größe beobachten (Bot committet mehrere MB je Lauf; GitHub empfiehlt < 1 GB).
- [ ] GitHub-Token „Insiderhandel Test 1 Github Actions“ läuft nie ab → löschen, bei Bedarf neu mit 90 Tagen.
- [ ] Zweiten Telegram-Bot nicht löschen: @Insiderhandeltest2bot sendet die Hype-Warnungen der Sentiment-Probe.
- [ ] Geschwärzte Bachelorarbeit auf der Methode-Seite verlinken? Entscheidung Tobias.
- [ ] Später: FinceptTerminal als Datenquelle testen (nur Daten, Lizenz beachten), USA über SEC (Form 4, 13D/G),
      Uni-Datenbanken nur privat zum Prüfen. Details `VORHABEN.md` Anhang „Offen“.
