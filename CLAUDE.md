# Insider-Monitor – Stand der Dinge

Directors' Dealings (Art. 19 MAR) von DAX- und MDAX-Firmen seit 2018, live ausgewertet mit der Event Study aus
Tobias' Bachelorarbeit (Uni Bayreuth). Langfristiges Ziel: ein Startup, eine Finanzdaten-Plattform wie GuruFocus, global (Einstieg unten).

- Website: https://insider.tobiaszwilling.me (GitHub Pages aus `/docs`, Branch `main`)
- Repository: github.com/tobzwil89/insider (öffentlich); DNS bei Namecheap, CNAME `insider` → `tobzwil89.github.io`
- Technische Übersicht (Dateien, Befehle): README.md; Vorbild-Analyse: GURUFOCUS.md
- Alte Projekte (Sentiment-Tracker, StockPulse, GuruFocus-Analyse) und was davon übernehmbar ist: BESTANDSAUFNAHME.md
- Recherche Datenquellen für den Ausbau (OpenBB, last30days-skill, FinceptTerminal, mit Adressen): DATENQUELLEN.md
- Vorschlag Zielarchitektur (Postgres + Python-Sammler auf Server + Next.js, noch nicht entschieden): ARCHITEKTUR.md

## Stimmrechte abgeschlossen (30.10.2026), nächstes Vorhaben: Rückkäufe

30.10.2026 umgesetzt (nicht gepusht, Tobias pusht): Auslöser war Tobias' Hinweis „Hugo Boss über 100 %“.
- **Stände vor 2018 ausgeblendet** (Tobias: ja): automatische Einträge mit Schwellendatum < 2018 fallen weg, geprüfte bleiben.
- **Doppelzählungen** in `stimmrechte.grossaktionaere`: (a) *Konzernkette*: Halter, die je am selben Tag denselben Bestand
  gemeldet haben, bilden eine Kette; je Kette gilt der neueste Stand (vor dem 3-%-Filter, damit Unterschreitungen zählen:
  Parsifal 3,05 % → David Zorub 2,92 %); gleicher Bestand → eine Zeile, weitere Namen klein darunter („dieselben Aktien
  auch bei“). (b) *Umfirmierung*: ein Halter mit gleichem Namensanfang (4 Zeichen) meldet später genau diesen Stand als
  „vorher“ (PFC S.r.l. → PFC S.p.A., Norwegen-Schreibweisen). Ohne Namensbedingung 83 Treffer mit Fehlern (Bund/Hensoldt,
  Bertermann/Auto1) → verworfen. Ebenso verworfen: gleicher Wert ab 10 % an verschiedenen Tagen (löschte Bund 25,1 %).
- Sortierung nach Aktien statt Zusammen; Erklärtext: Instrumente sind keine Aktien, Spalten Instrumente/Zusammen nicht addierbar.
- Geprüfte Liste ergänzt: Porsche, Porsche SE, Traton → eine Zeile „Familien Porsche und Piëch“ (100 / 100 / 87,52 %,
  Mitteilungen 04.04.2025, `*` vor 05.04.2025); Knorr-Bremse: Heinz Hermann Thiele ausgeblendet (Erbfall 2021, Stiftung 58,99 %).
- Ergebnis: 309 Zeilen bei 83 Firmen, keine Firma mehr über 100 % in Aktien. Hugo Boss 70,2 %
  (Ashley 49,41, Zignago/PFC 14,15, Silchester 5,08, Banken/Händler 1,6). Screenshot geprüft, `docs/` zurückgesetzt.
- **Rheinmetall/Scout24:** kein Leserfehler, EQS zeigt bei je einer Mitteilung (2016) einen fremden KKR-Pressetext →
  `stimmrechte.DEFEKT` (als `anderes`), beide Firmen fertig. `stimmrechte_laden.py` meldet offene Firmen jetzt
  („Noch offen (n): …“), getestet mit simuliertem Fehler.
- **Von Hand nachgetragen (30.10.2026, nach den Mitteilungen geprüft):** Brenntag Kühne Holding 20,10 % (Stähelin meldet als
  Testamentsvollstrecker, eine Zeile); Fonds stecken im Anteil ihres Verwalters → Fonds ausgeblendet: Artisan Funds (Brenntag,
  Adidas), Flossbach SICAV (Brenntag, Bechtle), First Eagle Global Fund (Merck); FMC: alte Dodge-&-Cox-Meldung 2022 aus,
  Fonds 2026 bleibt. Nemetschek: Ralf 2022 ausgeblendet (dieselbe Nemetschek-Stiftung, heute 45,07 % laut Georg 02.07.2026).
  Ergebnis 303 Zeilen. Rebase-Konflikt in `daten/stimmrechte.csv` (Bot hatte angehängt) gelöst, beide Teile behalten, Sicherung
  im Branch `sicherung-vor-rebase` (nach erfolgreichem Push löschbar: `git branch -D sicherung-vor-rebase`).
- **Bekannte Reste:** Leser speichert bei manchen Familienformularen nur Vornamen („Dr. Wolfgang“, „Georg F.W.“,
  „Maria Elisabeth“). Neue Fonds-/Verwalter-Paare tauchen mit neuen Mitteilungen auf → bei der jährlichen Prüfung der
  geprüften Liste mit ansehen. Verschoben (Tobias): Henkel-Poolmeldungen `anderes`, 806 Fließtexte 2008–2012 (DeepSeek).
**Vorhaben Stimmrechte ist erledigt** (Tobias 30.10.2026). Rückkäufe: siehe eigenes Vorhaben unten (Block 4 wartet auf Push und Start der Action).

## Marketing und Website (Planungs-App #9), Stand 30.10.2026

**Verworfen und gelöscht (30.10.2026):** eigene Testseite `docs/labor/` (Design ohne Absprache, zu eng auf Insiderdaten,
kein zentraler CTA) und ein Google-Stitch-Entwurf (KI-Einheitsbrei, erfundene Zahlen wie „14.800 Abonnenten“ oder eine
„Uni-Mannheim-Studie“ → wäre abmahnfähig). Lehre: erst Strategie, dann Marke, dann Texte, dann Design, dann Bau.

**Entscheidungen Tobias:** Deutsch und Englisch von Anfang an. Positionierung „GuruFocus für Europa, wesentlich
günstiger“ + „Folge den Profis“, Sentiment-Analyse als großer Bestandteil (ob GuruFocus Sentiment hat: ungeprüft).
CTA: Newsletter, Formular mit **EmailOctopus** (läuft schon in `roleplay-landing`). Brauchbare Idee aus Stitch:
„Sonntags-Report“ mit den spannendsten Insiderkäufen der Woche.

**Empfehlung Claude (Tobias hat zugestimmt, mit Schritt 1 zu beginnen):** Aufwendige Website erst, wenn das Produkt steht
(dann echter Designer oder hochwertige Vorlage, nicht generiert). Jetzt:
- [x] 1. Positionierung in einer Sitzung (31.10.2026), Entscheidungen Tobias:
      - **Zielgruppe:** Privatanleger, die selbst Einzelaktien auswählen. Reihenfolge: DACH → Europa und USA → Rest der Welt.
        Seite Deutsch und Englisch von Anfang an.
      - **Versprechen:** „GuruFocus für Europa, günstiger“ + Insider + Sentiment. Begründung Tobias: Der Markt läuft heute
        stark über X/Twitter und Reddit (Hype, Pennystocks, Krypto), dort gelten die alten Regeln nicht; Vorbild Nancy Pelosi (USA).
        Vorschlag Claude für die Überschrift (offen): „Was die Profis tun, was die Masse redet und was davon stimmt“
        (Profis gegen Hype, belegt durch die eigene Event Study). „Günstiger“ als Nebenbotschaft, nicht als Überschrift
        (AlleAktien nutzt ebenfalls Eulerpool-Daten). Grenzen: Politikerdepots gibt es nur in den USA (STOCK Act), in der EU
        keine vergleichbaren Daten → kommt mit der USA-Phase; Krypto hat keine Insidermeldungen; Pennystock-Hype rechtlich heikel.
      - **Preis:** kostenlos (Sonntags-Report, Daten mit Verzögerung); Pro 9 €/Monat bzw. 89 €/Jahr; Gründerpreis 59 €/Jahr
        dauerhaft für die ersten 100. Vergleich: AlleAktien ≈ 290 €/Jahr, GuruFocus ≈ 450–550 $/Region. Eulerpool Builder
        (99 $/Monat) ist ab etwa 15 Zahlenden gedeckt.
      - **Name:** offen, eigene kurze Runde. Geprüft 31.10.2026 (whois): profispur.de/.com, followtheinsiders.com,
        aktienspur.de frei; insiderblick.de, kapitalspur.de vergeben. Vor dem Kauf Marke bei DPMA/EUIPO prüfen.
- [ ] 2. Newsletter starten: schlichtes EmailOctopus-Formular, verlinkt von der jetzigen Seite; Skript, das samstags
      einen Entwurf des Sonntags-Reports aus den eigenen Daten vorbereitet.
      **Skript fertig (31.10.2026, nicht gepusht):** `python3 sonntags_report.py [JJJJ-MM-TT]` → `newsletter/<Datum>.md`
      (Stichtag = Sonntag, betrachtet die 7 Tage davor nach Mitteilungsdatum): 5 größte Käufe, neue Cluster, Käufer mit
      guter Bilanz (aus `ranking.json`, nur Ø und Median > 0), 3 größte Verkäufe. Liest nur `docs/data`, also vorher
      `git pull`. Getestet an den Wochen bis 04.10. und 01.11.2026. Nur Deutsch (Englisch fehlt noch). Offen: EmailOctopus-
      Liste + Formularcode von Tobias, Link auf der Seite, Datenschutztext (Vorlage `roleplay-landing`); Versand samstags
      automatisch erst, wenn der Report von Hand ein paar Wochen gut war.
- [ ] 3. Mit 5–10 Anlegern sprechen. Leitfaden, Anschreiben, Auswertungstabelle: `newsletter/GESPRAECHE.md` (31.10.2026).
      Die Gespräche prüfen jetzt Zielgruppe und Preisidee aus der Positionierung (31.10.2026).
- [ ] 4. Weiter am Produkt (Datenbank, Sentiment); Website danach.

## Nächste Schritte (Stand 31.10.2026, nach Rauszoomen mit Tobias)

Ziel bleibt: Startup, Finanzdaten-Plattform „GuruFocus für Europa, günstiger“ + „Folge den Profis“ + Sentiment.
Fundamentaldaten sind dafür Pflicht, aber nicht das Alleinstellungsmerkmal (das sind Insider, Großaktionäre, Rückkäufe,
Guru-Depots, später Sentiment). Reihenfolge laut Empfehlung Claude:
1. **Neuer Chat: Eulerpool einbauen** (`DATENQUELLEN.md` Abschnitt 9): Leser in `pipeline/fundamental.py`
   (GuV, Bilanz, Cashflow, Schätzungen; Ist-Jahre von Schätzjahren trennen; Werte in Mio. → ×1e6; verschlüsselte
   Antworten überspringen, nie entschlüsseln), in `kennzahlen.PRIORITAET` vor onvista/TradingView für EBIT und
   Schätzungen; dann alle Firmen automatisch gegen `/api/1/aaqs/by-isin` abgleichen (nur Prüfung, nicht anzeigen) und
   Formeln nachschärfen (ROCE, Verschuldung). Danach Fundamentaldaten als fertig betrachten, **nicht weiter ausbauen**.
2. **Kleine Fehler auf der Live-Seite zuerst beheben:** Rückkäufe „keine Daten“ ✅ (31.10., gepusht);
   Taktung: cron-job.org einrichten (Tobias, Abschnitt Offen).
3. **Positionierung: erledigt 31.10.2026** (siehe Marketing Schritt 1), nur der Name ist noch offen.
4. **Newsletter „Sonntags-Report“ + 5–10 Gespräche mit Anlegern** (Marketing Schritt 2–3): erste echte Rückmeldung.
5. **Architektur entschieden (31.10.2026, `ARCHITEKTUR.md` unten):** Supabase (Postgres, kostenlos), Sammler bleiben
   in GitHub Actions, kein Hetzner bis MVP, 0 € bis MVP. Umsetzung (Block 1–2) nach der Positionierung (erledigt) und
   bevor das Universum über DAX/MDAX hinaus wächst, **kann also jetzt starten**; braucht ein Supabase-Konto von Tobias.
   Website-Technik ist noch festzulegen.
6. **Vor dem Livegang:** Rechtslage der Quellen; legaler Weg mit Anzeigerecht wäre Eulerpool Builder (99 $/Monat).

## Einstieg für einen neuen Chat (Stand 28.10.2026)

**Was das ist:** Tobias (Bachelorarbeit Uni Bayreuth, Event Study zu Directors' Dealings) baut aus dem Insider-Monitor
ein **Startup**: eine Finanzdaten-Plattform nach Vorbild GuruFocus/AlleAktien, **global** (Deutschland, USA, weitere
Märkte), mit eigener Datenbank. Der heutige Stand (statische Website auf GitHub Pages, Python-Pipeline in GitHub Actions)
ist nur der Anfang; **Tech-Stack ist offen**, Umzug auf eine richtige Datenbank ist geplant.

**Aktuelle Phase: Recherche.** Noch nichts davon gebaut. Ergebnisse in `DATENQUELLEN.md` (zuerst Lesehinweis und
Abschnitt 7 lesen). Geprüft: OpenBB, last30days-skill, FinceptTerminal.

**Lesereihenfolge:** diese Datei (Stand, Vorhaben, Offen) → `DATENQUELLEN.md` (Quellen für den Ausbau) →
`GURUFOCUS.md` (Vorbild, Aufbau der Seiten) → `ALTERNATIVE_DATEN.md` (Rechtslage, Meldeschwellen, Ausbauideen) →
`BESTANDSAUFNAHME.md` (alte eigene Projekte) → `README.md` (Dateien und Befehle).

**So arbeitet Tobias (bitte einhalten):**
- Deutsch, einfache Sprache, direkt; widersprechen, wenn er falschliegt; klare Empfehlung statt Optionsliste.
- **Startup-Sicht:** Repositories und Quellen nach Nutzen fürs Produkt bewerten, nicht nach „passt in die GitHub Action“
  oder „nur deutsche Aktien“. In der Recherche **alles aufnehmen**, auch graue Wege (Browser-Cookies, Umgehung von
  Bot-Sperren); Rechtslage nur als Hinweis „vor dem Start klären“.
- **Nicht ungefragt bauen:** Fragt er „Ist X nützlich?“, ist das eine Recherchefrage, kein Bauauftrag.
- **Alles notieren**, laufend in dieser Datei (Stand, Offen, Verlauf) und in den Recherchedateien.
- Er **pusht selbst**: am Ende jedes Schritts die Befehle zum Committen/Pushen als Codeblock geben (Dateien einzeln
  `git add`, nie `git add .`; `.env` mit API-Schlüssel ist in `.gitignore`).
- Bei schweren Datenquellen fertige Lösungen bevorzugen, bei einfachen schlank selbst bauen.

**Offene Entscheidungen von Tobias:** Reihenfolge des Ausbaus (Sentiment/News, USA über SEC, Datenbank-Umzug);
ob die Regel „kein Fincept-Code“ bleibt (Urheberrecht AGPL, nicht nur Nutzungsbedingungen); Taktung der Action (s. „Offen“).

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
      - **Lauf 2–4** (24.10., alle Erfolg, letzter Commit bed033a, Protokoll „Alle Firmen fertig“). Geprüft 28.10.2026:
        89 von 90 Firmen fertig, `stimmrechte.csv` 17.396 Mitteilungen aus 83 Firmen (16.997 Stimmrechte, 399 `anderes`).
        Spalte `geladen` im Fortschritt zählt nur das im jeweiligen Lauf Gelesene (wie bei `eqs_fortschritt.csv`),
        Bestand ist vollständig (z. B. Delivery Hero 749/749). **Einzig offen: Auto1**, 2 Mitteilungen vom 05.02.2021
        „ohne Inhalt“. Ursache: Die Seiten haben Inhalt, aber doppelt kodierten Text bei EQS („VerÃ¶ffentlichung“,
        „StraÃe“), daran scheitert der Leser. Auto1 bleibt deshalb dauerhaft offen und wird bei jedem Lauf erneut versucht.
        **Behoben 28.10.2026:** `stimmrechte._reparieren` dekodiert solche Zeilen neu (latin-1 → UTF-8). Auto1 lokal
        nachgeladen (409 Mitteilungen) → **alle 90 Firmen fertig, Block 3 erledigt.**
      - Dabei gefunden und im Leser behoben: Natürliche Personen mit Vor- und Nachname in getrennten Zeilen wurden nur
        mit Vornamen gespeichert (57 alte Zeilen, z. B. „Gérald“ statt „Gérald Frère“). 28.10.2026 neu gelesen: 53 korrigiert,
        4 waren richtig (RAG-Stiftung, AXA). Hochtief 14.11.2023 (ACS, 75,71 %) ohne Namen: Leerzeichen hinter
        „Legal entity:“ → Leser entfernt jetzt Leerzeichen am Zeilenende (25 Stichproben ohne Abweichung), Zeile korrigiert.
        Bekannt, nicht behoben: Scout24 2019, 2 Mitteilungen Sand Grove ohne Prozentwerte.
      - 214 × `anderes`: 74 eigene Aktien, 13 × § 43, Korrekturen; **Aroundtown 60** (luxemburgisches Formular, wie bei
        Directors' Dealings nicht unterstützt) und ~40 verstreute (Elmos 9, Delivery Hero 7, Beiersdorf 6 …), noch nicht angesehen.
- [x] **Block 4 – Laufend aktuell halten (28.10.2026, noch nicht gepusht):** `stimmrechte_laden.py --tage 14` lädt für
      alle Firmen nur Mitteilungen der letzten 14 Tage, die noch fehlen; Fortschrittsliste bleibt unberührt.
      Eigener nächtlicher Zeitplan in `stimmrechte.yml` (`37 2 * * *`, höchstens 60 Min.), weil der Lauf **~12 Min.**
      dauert (EQS-Pause 2 s je Abruf) und das 15-Min.-Limit von „Daten aktualisieren“ sprengen würde. Knopfdruck
      lädt weiter die Historie. Lokal getestet: 12 Min., 28 neue Mitteilungen (23.–28.10.), keine Duplikate, keine
      leeren Pflichtfelder. Nach dem Push: am nächsten Morgen unter Actions prüfen, ob der Lauf um ~03:37 Uhr lief.
- [x] **Block 5 – Anzeige (28.10.2026, noch nicht gepusht):** Abschnitt „Großaktionäre“ auf jeder Firmenseite
      (`stimmrechte.grossaktionaere`, Aufruf in `export.py`, HTML in `seiten.py`). Je Firma und Halter die letzte
      Mitteilung (nach Schwellendatum). Gezeigt nur **≥ 3 % Aktien oder ≥ 5 % zusammen**: Darunter kann ein Halter
      ohne Meldung aussteigen (Schwellen Instrumente/Summe beginnen erst bei 5 %), der Stand wäre unsicher.
      Schreibweisen zusammengefasst über `_schluessel` (Ort/Land hinter dem Namen abgeschnitten, „X / Y“ → Y),
      Anzeigename = kürzeste Schreibweise. Keine Summenzeile (Zurechnung: Stiftung und Stifter, Konzern und Fonds).
      Ergebnis: 422 Halter bei 79 Firmen; lokal geprüft (Hochtief, Hugo Boss, Screenshot Desktop und 420 px).
      **Lücke (auf der Seite benannt):** nur Mitteilungen ab 2018, stabile Großaktionäre fehlen (HDI bei Talanx,
      Schulenberg bei Eventim, Kronseder bei Krones). Volkswagen, Sartorius, Wacker: gar keine Mitteilungen bei EQS
      (anderer Verteiler). Umfirmierungen erscheinen doppelt (Hugo Boss: PFC S.r.l. 2020 und PFC S.p.A. 2025).
- [x] **Block 6 – Lücke vor 2018 schließen** (abgeschlossen 30.10.2026: ab 2018 automatisch, davor nur geprüfte Einträge) (Entscheidung Tobias): EQS-Archiv vor 2018 laden (alte Formulare
      nach § 21 WpHG a. F. prüfen) und/oder Quelle für VW/Sartorius/Wacker suchen (Unternehmensregister).
      **Test 28.10.2026** (Talanx, Eventim, Krones; Ergebnisse `.recherche/stimmrechte_vor2018_probe.csv`,
      `.recherche/fliesstext_probe.py/.csv`): vor 2018 nur 1 / 94 / 13 Mitteilungen. Ab ~2016 Standardformular
      (Eventim: 28 gelesen), davor **Fließtext ohne Formular** (79 von 108 → `anderes`). Die Daten stehen drin
      (HDI 89,08 % an Talanx 2012, Nora Kronseder 51,85 % an Krones 2013), aber ein Regex-Leser findet den Namen
      nur in 10 von 79 Fällen, und der Prozentwert ist oft der falsche (z. B. zugerechneter Teil statt Gesamt).
      Zusätzlich: Alte Werte können legal veraltet sein (HDI heute ~77 %, von 89 % aus keine Schwelle berührt).
      Optionen: (a) Fließtext einmalig mit Claude auslesen lassen (API-Schlüssel nötig, Kosten vorher berechnen),
      (b) Großaktionäre der betroffenen Firmen von Hand pflegen, (c) Lücke lassen. **Tobias 28.10.2026: Option (a),
      mit DeepSeek** (eigener API-Schlüssel; Empfehlung V4.1-Flash, Probe mit 30 Texten vor dem Gesamtlauf).
      - [x] **6a – Lader (28.10.2026):** `stimmrechte_laden.py --alt` lädt 2000–2017 mit eigener Fortschrittsliste
            `stimmrechte_alt_fortschritt.csv`. Formular-Mitteilungen wie gewohnt nach `stimmrechte.csv`; Fließtexte als
            `formular=anderes` dort und zusätzlich mit Text nach `stimmrechte_texte.csv`. Leser kennt jetzt auch das alte
            Datumsformat (ohne „/“, sonst aus dem EQS-Kopf). Getestet: Krones (13, ab 2008) und Talanx (1) lokal geladen.
            Workflow „Stimmrechte laden“ hat den Schalter „Archiv vor 2018“. **Tobias:** pushen, mit Haken starten,
            wiederholen bis „Alle Firmen fertig“.
      - [ ] **6b – Auslesen mit DeepSeek** (lokal, Schlüssel in `.env`, steht in `.gitignore`): je Text Halter, Sitz,
            Schwellendatum, Aktien/Instrumente/Summe als JSON → Zeilen mit `formular=fliesstext` in `stimmrechte.csv`.
            Erst 30 Texte gegen Handprüfung, dann alle. Anzeige: Hinweis „Stand laut Mitteilung von …“, Text auf der
            Seite anpassen (Lücke vor 2018 dann kleiner, aber alte Werte können legal veraltet sein).
            **Stand 29.10.2026:** `stimmrechte_fliesstext.py` gebaut, schreibt nach `daten/stimmrechte_fliesstext.csv`
            (eigene Datei, `stimmrechte.csv` unverändert), neueste Jahre zuerst, 8 Anfragen parallel, setzt fort, wo es
            aufgehört hat. Modell `deepseek-flash`, **ohne Nachdenken** (`thinking: disabled`; Probe ohne und mit Nachdenken
            identisch, 85 % weniger Ausgabe-Token). Probe 30 Texte (`.recherche/fliesstext_deepseek_probe*.csv`): 10 von Hand
            gegen den Originaltext geprüft, alle Werte richtig (auch 100 % bei LEG/Porsche und 60 % Goldman bei Kion sind echt);
            Feld `korrektur` teils uneinheitlich. Gesamtlauf: **4.229 von 5.035 Texten** (2013–2017 vollständig, 2012 433/494,
            2011 90/228, 2010 38/260, 2008–2009 fehlen), 7.346 Halterzeilen, 32 ohne Prozentwert. Kosten **~0,93 $**
            (5,0 Mio. Eingabe- + 0,65 Mio. Ausgabe-Token), Guthaben leer (0,05 $). Meine Schätzung vorher (0,20–0,40 $) war
            falsch, die Probe war für eine Kostenmessung zu klein (Guthaben nur auf Cent genau). DeepSeek lehnte schon bei
            angezeigten 0,12 $ ab (402), die Guthaben-Abfrage hinkt nach. Geprüft: HDI 89,08 % an Talanx, Nora Kronseder 51,85 %.
            - [ ] Rest (806 Texte, 2008–2012): nach dem Aufladen `python3 stimmrechte_fliesstext.py` (holt nur die fehlenden,
                  geschätzt ~0,20 $).
            - [ ] Anzeige: **nicht automatisch** (Prüfung 29.10.2026). Mit allen alten Daten 1.276 statt 488 Zeilen,
                  857 mit Stand vor 2018, viele überholt: Ketten von Tochterfirmen melden gemeinsam, beim Ausstieg nur die
                  Mutter (Permira bei Hugo Boss, BlackRock-Töchter bei Allianz). Regel „Mitteilung überholt, wenn ein Mitglied
                  später meldet“ → 951 Zeilen, hilft aber nicht, weil im EQS-Archiv vor 2018 viele Ausstiege ganz fehlen.
                  Auch bei ≥ 25 % in Aktien (76 Halter, 20 Firmen) etwa die Hälfte falsch: CVC/Evonik, Volvo/Deutz, Perry/LEG,
                  Hueck/Hella, Wacker/Siltronic (57,8 statt ~31 %), Renk 2011 = alte Renk AG. Richtig: HDI/Talanx,
                  Kronseder/Krones, KPS+Schulenberg/Eventim, Quandt/BMW, Henkel-Pool, Weichai/Kion, Nemetschek.
                  **Tobias 29.10.2026: Daten nur als Kandidatenliste, von Hand prüfen.**
            - [x] **6c – Geprüfte Großaktionäre (29.10.2026, nicht gepusht):** `daten/grossaktionaere_geprueft.csv`
                  (firma, halter, aktien, stand, geprueft, quelle), eingelesen in `export.py`, verarbeitet in
                  `stimmrechte.grossaktionaere(df, geprueft)`: Halter mit Wert ersetzt den automatischen Eintrag (Schlüssel
                  über `_schluessel`), ohne Wert blendet ihn aus, `*` blendet alle automatischen Einträge der Firma vor `stand`
                  aus. Anzeige: unter dem Datum „geprüft TT.MM.JJJJ“, Link zur Quelle, Satz im Erklärtext.
                  Von den 20 Kandidaten-Firmen zeigten 9 den großen Halter schon aus Meldungen ab 2018 (Merckle, Faurecia, ACS,
                  Schaeffler, Nemetschek, Haaß/Fuchs, RAG/Evonik, Porsche SE, Siltronic). Eingetragen: Talanx (HDI 76,7 %),
                  Krones (Kronseder-Konsortium 51,9 %), Henkel (Aktienbindungsvertrag 61,85 % der Stämme, 19.03.2026), Kion
                  (Weichai 46,5 %), BMW (Quandt + Klatten zusammen 50,2 %, Einzelwerte ohne Primärquelle), Aroundtown (Avisco
                  Trust 15,01 %). **Dabei gefundene Fehler, die live waren:** Renk zeigte die Porsche-Familie mit 76 % aus
                  Meldungen der alten Renk AG (2016–2018) → ausgeblendet, IR-Tabelle 17.07.2026 eingetragen (Seite blockt
                  Abrufe, Werte aus dem Suchauszug). Hella zeigte Hueck-Pool 60 % von 2015 und Faurecia 80,59 % → Forvia 81,59 %.
                  Eventim zeigte KPS 50,2 % und Schulenberg 43,2 % → KPS 38,83 % (Platzierung 11/2019; 40 % ist keine Schwelle,
                  daher keine Mitteilung). Verworfen (überholt): CVC/Evonik, Volvo/Deutz, Perry+Goldman/LEG, UniCredit/Hugo Boss.
                  Geprüft mit nachgebautem Lauf ohne BaFin/Telegram (Talanx, Renk, Eventim, Henkel korrekt), `docs/` danach zurückgesetzt.
            - [ ] Bekannt, nicht behoben: Henkel-Familienmeldungen bei EQS landen als `anderes` (Leser), BMW ohne Meldungen
                  der Familie seit 2018; weitere alte Stände 2015–2017 aus Formularen in der Anzeige (z. B. Deutz Source Markets
                  2017, Krones Deutsche AM 2016) nicht geprüft. Geprüfte Einträge veralten: etwa jährlich neu abgleichen.
- Porsche SE / Porsche AG (28.10.2026): 100 % je Familienmitglied ist korrekt (Stammaktien vollständig zugerechnet,
  gehandelt werden nur Vorzüge). Hinweis auf der Seite über `seiten.NUR_VORZUG`; „Name (1.)“ = „Name“ im Schlüssel.

## Laufendes Vorhaben: Aktienrückkäufe (Art. 5 MAR) ab 2018

Auftrag Tobias 30.10.2026 (nach Abschluss Stimmrechte). Quelle: EQS-Kategorie `sonstige-kapitalmarktinformationen`
(Titel nichtssagend, enthält auch Anleihen-/§-50-Meldungen → jede Meldung wird geöffnet). Probe-Skripte `.recherche/rueckkauf_*.py`.

- [x] **Block 1 – Leser (30.10.2026):** `pipeline/rueckkaeufe.py`. Kein einheitliches Format (Datum `2026-10-19`,
      `19.10.2026`, `04/05/2026`, `16. März 2018`; teils eine Zeile je Handelsplatz; bis ~2019 Text mit festen Spalten,
      teils nur ein Leerzeichen zwischen Datum und Stückzahl). Gelesen wird jede Folge Datum → Stückzahl → Kurs, je Tag
      zusammengezählt (Ø Kurs gewichtet). Erkennung: Verordnung 596/2014 oder 2016/1052 oder „Rückkauf/buy-back“
      (Heidelberg nennt die Verordnung nicht). Kontrollzahl `stueck_text` = letzte Nennung „insgesamt / eine Anzahl von N Aktien“.
      Test an 13 Firmen: alle Abweichungen liegen an den Meldungen (Telekom 22.04.2024 Text ≠ Tabelle, Mercedes 02.08.2024
      ohne Werte, Allianz 2018 Zahlendreher, Allianz 02.04.2024 Tabelle verrutscht, SAP 05.08.2025 Datum 07-01 statt 08-01).
      Nicht bei EQS: BMW (Verteiler seit 2020 gewechselt, wie bei Directors' Dealings), Munich Re nicht geprüft.
- [x] **Block 2 – Lader + Action (30.10.2026, nicht gepusht):** `rueckkaeufe_laden.py` (wie `stimmrechte_laden.py`:
      `--max-minuten`, `--tage`, `--firmen`, speichert je Firma, meldet offene Firmen) → `daten/rueckkaeufe.csv`
      (firma, isin, veroeffentlicht, art, datum, stueck, kurs, stueck_text, url; je Rückkauftag eine Zeile),
      `daten/rueckkaeufe_fortschritt.csv`. Workflow `.github/workflows/rueckkaeufe.yml` „Rückkäufe laden“: Knopfdruck =
      Historie (320 Min.), nachts `17 3 * * *` nur 14 Tage. Lokal getestet (SAP, Zalando, Deutz): Abbruch nach 4 Min. und
      Fortsetzen ohne Doppelte, 184 Meldungen, Kontrollzahl 169/170. Zalando 2024 und 2025 je 100,0 Mio. € = Programmgröße.
- [x] **Block 3 – Anzeige (30.10.2026, nicht gepusht):** `rueckkaeufe.jahre` (je Firma und Jahr: Handelstage, Stück,
      Volumen, Ø Kurs, letzter Tag; gleicher Tag aus zwei Meldungen nur einmal), Abschnitt „Aktienrückkäufe“ auf der
      Firmenseite nach den Großaktionären. Nur für Firmen in `rueckkaeufe_fortschritt.csv`, sonst fehlt der Abschnitt
      (sonst stünde „keine Rückkäufe“ bei noch nicht geladenen Firmen). Lokal geprüft (SAP, Allianz ohne Abschnitt), `docs/` zurückgesetzt.
- [x] **Block 4 – Historie laden (30.10.2026):** Läufe 14:29 (4 h 10 min) und 18:54 melden „Alle Firmen fertig“.
      90 Firmen, 16.144 Zeilen (15.321 Rückkauftage, 823 `anderes`). Kontrollzahl: 2.939 Meldungen stimmen, 192 ohne,
      150 „Abweichungen“ sind nur die kumulierte Programmsumme (BASF, Brenntag, Puma: Differenz zur Vormeldung passt),
      83 echte Abweichungen, davon 48 Scout24 (2019–2024), Rest einzeln (Allianz, Telekom, Commerzbank, Talanx …).
- [x] **Fehler auf der Live-Seite (behoben und gepusht 31.10.2026, per Patch `.recherche/rueckkauf-keine-daten.patch`):**
      Firmen mit `meldungen=0` in `rueckkaeufe_fortschritt.csv` und ohne Zeile in `rueckkaeufe.csv` bekommen jetzt
      „Keine Daten: Das EQS-Archiv enthält … keine Rückkaufmeldungen“ (`export.rk_ohne`, `firmenseite(rueck_ohne_meldungen=)`).
      Lokal getestet mit den Bot-Daten: 36 Seiten „Keine Daten“ (34 Firmen, VW/Sartorius je 2 Gattungen), 14 behalten
      „Keine Aktienrückkäufe“, SAP Tabelle. Ursprünglicher Befund: 34 Firmen haben bei EQS **0 Meldungen** in der Kategorie (u. a. BMW, K+S, Rheinmetall,
      Volkswagen) und bekommen trotzdem „Keine Aktienrückkäufe seit 2018 laut EQS-Archiv.“ BMW (Verteiler gewechselt)
      und K+S (Programm 2023) haben aber zurückgekauft → bei 0 Meldungen besser „keine Daten“ statt „keine Rückkäufe“.
- [ ] Offen aus der Prüfung: Scout24-Abweichungen ansehen; `art=anderes` mit „Rückkauf“ im Text (braucht die Meldungstexte).
- [ ] Später: laufende Programme (Ankündigung nach lit. a: Volumen, Zeitraum) anzeigen; Rückkäufe im Kursdiagramm markieren.

## Geplantes Vorhaben: Fundamentaldaten (Planung #6), Stand 30.10.2026

Auftrag Tobias 30.10.2026: viele Finanzkennzahlen, mindestens die Datenpunkte der AlleAktien-Karte (Beispiel Atoss).
**Vorgaben Tobias:** kein Geld ausgeben, global denken (nicht nur Europa), erst nur lokal testen (nicht live) →
Lizenzfragen erst vor dem Start. Erster Plan (Bezahlanbieter EODHD/FMP) von Tobias verworfen.

Gratis-Quellen getestet (30.10.2026, Atoss/SAP/Deutz/Apple/Toyota; Probe-Dateien im Scratchpad, nicht gesichert):
- **TradingView-Screener** (`scanner.tradingview.com/<markt>/scan` per POST, `…/symbol?symbol=XETR:AOF&fields=…`,
  Feldliste `…/global/metainfo`, 4.143 Felder), ohne Schlüssel, alle Märkte (Deutschland 40.159, USA 20.061 Zeilen).
  **20 Jahre** je Firma: Umsatz, Bruttogewinn, EBITDA, Gewinn, Gewinn je Aktie, Dividende, FCF, Capex, Bilanzsumme,
  Schulden (`*_fy_h`, auch Quartale `*_fq_h`). Aktuell: Marktkap., KGV, KUV, KBV, Margen, EK-Rendite, ROCE, ROIC,
  Nettoverschuldung, EBIT TTM; Schätzung nächstes Jahr (Umsatz, EBIT, EBITDA, Gewinn, FCF, Dividende).
  **Fehlt:** EBIT- und Eigenkapital-Historie, Schätzungen über 1 Jahr. Abgleich Atoss mit AlleAktien (04.10.2026):
  Gewinnmarge 25,6 = 25,6 %, Umsatzwachstum 10 J. 15,5 = 15,5 %, Nettoverschuldung/EBITDA −1,6 = −1,6; EK-Rendite
  54,6 statt 49,8 und ROCE 67,4 statt 61,6 (andere Definition) → solche Kennzahlen selbst rechnen.
- **SEC companyfacts** (offiziell): USA ~15 Jahre vollständige Abschlüsse inkl. EBIT (Apple ab 2009).
- **onvista** (`api.onvista.de/api/v1/stocks/ISIN:<ISIN>/snapshot`, per ISIN): 4 Jahre Bilanz/GuV (EBIT, Eigenkapital),
  **Schätzungen bis 2028e/2029e** (Gewinn je Aktie, KGV, Dividende; EBIT-Schätzung bei Atoss leer).
- **Yahoo**: 4 Jahre GuV, 5 Jahre Bilanz/Cashflow, Schätzungen 2 Jahre (nur Umsatz, Gewinn je Aktie).
- **Nasdaq** (inoffiziell): USA 4 Jahre, Gewinnschätzungen 4 Jahre (Apple bis 2029).
- **stockanalysis.com**: 5 Jahre, Schätzungen 1 Jahr, Rest hinter Bezahlschranke. **MarketScreener**: 403 (Cloudflare).
- Nicht getestet (brauchen Gratis-Schlüssel): Finnhub, Alpha Vantage, SimFin, FMP/EODHD-Gratisstufe.

Lücken: EBIT älter als 4 Jahre außerhalb der USA (Ersatz: EBITDA oder Gewinn aus TradingView, so beschriften);
Umsatz-/EBIT-Schätzungen für 3 Jahre (nur 1 Jahr; Gewinn je Aktie 3–4 Jahre über onvista/Nasdaq).

Plan (Tobias 31.10.2026: „so machen“), nur lokal, in abbrechbaren Blöcken:
- [x] **1. Sammler (31.10.2026):** `python3 -m pipeline.fundamental` (~1,5 Min.) → `daten/fundamental.csv` (5 MB, lang:
      isin, symbol, quelle, periode, posten, wert, waehrung, abgerufen; jeder Lauf ersetzt die Datei). TradingView
      (ein Abruf für alle, `price_conversion: to_symbol` → alles in Handelswährung, auch Qiagen USD→EUR), onvista je ISIN
      (Posten mit Präfix `bilanz.`/`kennzahl.`/`bewertung.`, Geschäftsjahr „24/25“ → „2025“), SEC für 10 US-Testfirmen
      (`USA_TEST`, ein Wert je Jahr über das SEC-Feld `frame`). Symbole per ISIN (Hauptnotiz, sonst Xetra, sonst
      Yahoo-Kürzel; Qiagen hat bei TradingView eine neuere ISIN). Atoss als Zusatzfirma (`ZUSATZ`) für den Abgleich.
      Ergebnis: alle 95 Firmen, Umsatz im Median 20 Jahre (unter 10 nur junge Firmen: Porsche, Renk, TKMS, Aumovio …).
      **Abgleich der Quellen:** Umsatz TradingView vs. onvista 94 % auf 1 % gleich, Gewinn 84 %; Abweichungen durch
      angepasste Vorjahre (Continental 2024 nach Aumovio-Abspaltung, Rheinmetall 2024) und Banken/Versicherer
      (andere Umsatzdefinition). SEC: Banken (AXP, BAC) ohne EBIT, JNJ/AXP Lücken, ältere Jahre teils angepasst.
- [x] **2. Kennzahlen (31.10.2026):** `python3 -m pipeline.kennzahlen` → `daten/kennzahlen.csv` (eine Zeile je Firma,
      Formeln im Modul). Beide CSV in `.gitignore` (inoffizielle Quellen, öffentliches Repository → nur lokal).
      Abgleich Atoss mit der AlleAktien-Karte (AA rechnete am 04.10. mit Kurs 83 €, wir mit 94,30 €): exakt gleich
      Gewinnmarge 25,6 %, EK-Rendite 49,8 % (Gewinn / Eigenkapital am Jahresende), Umsatzwachstum 10 J. 15,5 %,
      max. EBIT-Rückgang 0 %, Gewinnanstiege 10/10; nah dran EBIT-Wachstum 10 J. 19,9 statt 19,6 % (EBITDA als Ersatz),
      Nettoverschuldung/EBITDA −1,5 statt −1,6, Renditeerwartung 15,5 statt 16,5 %; ROCE 66 statt 62 % (andere
      Kapitalbasis). Kursabhängige Werte (KGV, KBV, Dividendenrendite) passen nach Umrechnung auf den Kurs.
      Bekannte Schwächen: Renditeerwartung = Gewinnwachstum je Aktie 3 J. (onvista) + Dividendenrendite → bei
      niedriger Ausgangsbasis unplausibel hoch (Deutz 60 %, Rheinmetall 67 %); fehlt für US-Firmen (keine onvista-Daten,
      Nasdaq hätte Gewinnschätzungen); Siemens-Verschuldung enthält die Finanzsparte (3,0 × EBITDA); EBIT 10 J. nur USA.
- [x] **3. Lokale Anzeige (31.10.2026):** Abschnitt „Finanzkennzahlen“ nach dem Kursdiagramm (`seiten.fundamental_abschnitt`):
      Bewertung, Rentabilität, Risiko, Wachstum, Balken Umsatz und EBIT (10 Jahre + Schätzung, reines HTML/CSS, Stile
      `.fk-*` in `style.css`). `export.py` liest `daten/kennzahlen.csv` nur, wenn sie existiert; sie steht in `.gitignore`,
      also **zeigt die Action den Abschnitt nie → Code kann gefahrlos gepusht werden.** Banken/Versicherer ohne
      EBIT-Diagramm und ohne Umsatzschätzung (Allianz zeigte +31 %). Geprüft per Bildschirmfoto (SAP, Allianz), alle 94
      Seiten mit Abschnitt, `docs/` danach zurückgesetzt. **Lokal ansehen:** `python3 -m pipeline.fundamental`,
      `python3 -m pipeline.kennzahlen`, `PYTHONPATH=. python3 .recherche/seiten_lokal.py` (wie `lauf.py` ohne BaFin,
      Gurus, Telegram), `python3 -m http.server 8765 --directory docs` → http://localhost:8765/firma/SAP.DE/,
      danach `git checkout -- docs/data docs/firma docs/sitemap.xml docs/*.html docs/gurus`.
      **Architektur (Tobias' Frage, 31.10.2026):** nicht nach Markt trennen, sondern ein Datenmodell (langes Format)
      mit Quellen als austauschbaren Lesern; welche Quelle je Posten gilt, steht in `kennzahlen.PRIORITAET`.
      Getrennt nach Schwierigkeit wird nur beim Livegang: US-Abschlüsse über die SEC sind offiziell und sofort
      zeigbar, Schätzungen und Kurse sind auch in den USA grau; deutsche Abschlüsse sind nur grau verfügbar
      (bis ESAP 2027 oder Lizenz).
- [x] **4. Qualitätscheck, Kategorie, Renditeerwartung (31.10.2026):** in `kennzahlen.py` (`KRITERIEN`, `kategorie`,
      `renditeerwartung`), Anzeige in `seiten.fundamental_abschnitt` (Häkchenliste, Kategorie mit Erklärung).
      Qualitätscheck: 10 eigene Kriterien (Umsatz 10 J./3 J. ≥ 5 %, EBIT bzw. EBITDA 10 J. ≥ 5 %, Gewinnschätzung ≥ 5 %,
      Nettoverschuldung ≤ 2 × EBIT (bei Verlust nur ohne Schulden), Gewinn in ≥ 9 von 10 Jahren, Einbruch ≤ 25 %,
      EK-Rendite ≥ 15 %, ROCE ≥ 15 %, Marge ≥ 10 %); fehlende Daten zählen nicht, Ergebnis „x von y bewertbaren“.
      10/10: SAP, Nemetschek, Atoss, Alphabet; 0/9: Bayer, Wacker, Lanxess, Salzgitter.
      Kategorie nach Peter Lynch (Vorrang in dieser Reihenfolge): Turnaround (Verlust letztes Jahr oder 2 von 3),
      Zykliker (operatives Ergebnis in 10 J. mindestens **zweimal** ≥ 25 % zum Vorjahr eingebrochen; erste Fassung mit
      „einmal ≥ 40 %“ ergab 29 Zykliker inkl. Rational/Amazon wegen Corona → verworfen), Substanzwert (KBV < 0,8, keine
      Finanzwerte), sonst nach Umsatzwachstum ≥ 12 % / 5–12 % / < 5 %. Verteilung: 29 langsam, 28 solide, 16 schnell,
      13 Zykliker, 13 Turnaround, 6 Substanzwerte. Grenzfälle: Siemens als Zykliker (Konzernumbau), Aroundtown
      „schnell wachsend“ (Zukäufe).
      Renditeerwartung: Gewinnwachstum je Aktie (3 J. onvista, sonst 1 J. TradingView, damit auch USA) **gedeckelt auf
      20 % p. a.** + Dividendenrendite, Hinweis auf der Seite, wenn gedeckelt (vorher Deutz 60 %, Rheinmetall 67 %).
      Burggraben-Text nicht automatisch. Geprüft per Bildschirmfoto (SAP, Deutz), `docs/` zurückgesetzt.
- [x] **Nasdaq und Märkte (31.10.2026):** `fundamental.nasdaq` holt US-Gewinnschätzungen (4 Jahre, Posten
      `eps_schaetzung`, `analysten`); `kennzahlen` nimmt sie, wenn onvista fehlt (Ist-Gewinn je Aktie TradingView →
      Schätzung in 3 Jahren; Vorsicht: Nasdaq bereinigt, Ist nach US-GAAP). Alle 10 US-Testfirmen haben jetzt
      Renditeerwartung aus 3 Jahren (Apple 14 %, NVIDIA gedeckelt). Bekannt: Firmen mit Geschäftsjahr bis Januar
      (NVIDIA) können um ein Jahr verrutschen (TradingView-Jahr vs. Nasdaq „Jan 2027“), nicht geprüft.
      Marktabdeckung geprüft → `DATENQUELLEN.md` Abschnitt 8: TradingView hat alle großen Börsen mit 20 Jahren
      (USA, China, HK, Taiwan, Korea, Japan, Indien, ganz Europa, Kanada, Australien, Brasilien …), Schätzungen bei
      Nebenwerten dünner. onvista auch große Auslandswerte (nicht China-A, nicht Indien). **SEC hat offizielle Daten
      für ausländische Firmen mit US-Notierung (20-F, teils IFRS)**: Vorschlag, `sec()` um `ifrs-full` zu erweitern.
- [ ] Danach offen: Handyansicht auf echtem Gerät; Schätzungen über 1 Jahr für Umsatz/EBIT (keine Gratisquelle
      gefunden); SEC um IFRS erweitern (Freigabe Tobias); Universum über DAX/MDAX hinaus (Freigabe Tobias);
      vor dem Livegang Rechtslage TradingView/onvista/Nasdaq.

## Laufendes Vorhaben: Guru-Depots (13F der SEC)

Auftrag Tobias 28.10.2026: Depots bekannter Investoren (Buffett usw.) wie bei GuruFocus. OpenBB (github.com/openbq-org/OpenBB,
früher OpenBB-finance, Apache 2.0) für diesen Zweck verworfen (später aus Startup-Sicht neu bewertet: `DATENQUELLEN.md` Abschnitt 5): keine deutschen Insider-/Fundamentaldaten, `openbb-sec` zieht
95 Pakete nach (Webserver, MCP, ruff), 13F selbst lesen sind ~80 Zeilen mit vorhandenen Paketen. Tobias: bei komplizierten
Datenquellen fertige Lösungen nutzen, hier selbst bauen.

- [x] **Block 1 – Leser (28.10.2026, nicht gepusht):** `pipeline/gurus.py` (`python3 -m pipeline.gurus`) holt je Guru die
      letzten 8 Meldungen 13F-HR von data.sec.gov und speichert jede Zeile nach `daten/gurus.csv` (lädt nur fehlende).
      7 Gurus in `GURUS` (CIK geprüft; Berkshire = 1067983). Werte vor 03.01.2023 in Tausend USD → ×1000.
      Test: 56 Meldungen, 1.942 Zeilen, 55 s, keine leeren Felder, 268 KB. Berkshire 266–299 Mrd. USD je Quartal, Apple vorn.
      Nicht gelesen: Nachträge 13F-HR/A (Berkshire reicht vertrauliche Positionen so nach), 13F-NT (Pershing Q2/2026:
      Positionen meldet eine andere Gesellschaft). Scion meldet seit Q3/2025 nicht mehr (Burry hat geschlossen).
      **Deutsche Firmen:** nur Deutsche Bank bei Tepper (2025–2026). 13F enthält nur US-gehandelte Papiere.
      **Formfehler bei der SEC:** Baupost meldet auch nach 2023 in Tausend → `positionen` erkennt das am Median-Preis
      je Aktie < 1 USD und rechnet ×1000. Nach Korrektur liegen alle Median-Preise zwischen 18 und 238 USD.
- [x] **Block 2 – Anzeige (28.10.2026, nicht gepusht):** `gurus.depot`/`alle_depots` fassen je CUSIP + Put/Call zusammen
      und vergleichen mit dem Vorquartal nach Stückzahl (neu / aufgestockt / reduziert / verkauft / unverändert, ±0,5 %).
      Anteil nur über Aktien (Optionen = Wert des Basiswerts). Seiten `docs/gurus/` (Übersicht) und
      `docs/gurus/<name>/` aus `seiten.guruseite`/`gurus_uebersicht`, Aufruf in `export.py`, Einträge in `sitemap.xml`,
      Link in der Fußzeile der Startseite. Geprüft: Screenshot Buffett und Übersicht (Werte stimmen, Apple 22 %, Alphabet +45 %).
      Bildschirmfotos unter ~500 px schneiden rechts ab, auch bei bestehenden Firmenseiten → Werkzeug, nicht Seite.
- [x] **Block 3 – Automatisch (28.10.2026, nicht gepusht):** `lauf.py --immer` (werktags 17:15 UTC) ruft `gurus.laden()` auf,
      Fehler bei der SEC brechen den Lauf nicht ab. Ganzer Lauf lokal getestet (15 s). **Tobias:** committen und pushen
      (`pipeline/gurus.py`, `daten/gurus.csv`, `docs/gurus/`, `lauf.py`, `pipeline/export.py`, `pipeline/seiten.py`,
      `docs/index.html`, `CLAUDE.md`), danach https://insider.tobiaszwilling.me/gurus/ ansehen.
      Push während laufender Action „Stimmrechte laden“ geprüft (28.10.2026): kein Konflikt, die Action committet nur
      `daten/stimmrechte*.csv` und macht vor dem Push `git pull --rebase`. Wird der eigene Push abgelehnt: `git pull`, `git push`.
- [ ] **Guru-Bereich umbauen (Tobias 28.10.2026):** passt noch nicht gut in die Seite. Übergangsweise nur ein Link
      in der Fußzeile der Startseite (vorher im Kopf). Beim GuruFocus-Ausbau richtig einbinden (Navigation, eigener
      Bereich neben Insidern und Großaktionären, Verknüpfung mit Firmenseiten).
- [ ] Später: Nachträge 13F-HR/A, Hinweis auf Firmenseiten bei US-Notierung (z. B. Deutsche Bank bei Tepper), mehr Investoren.

## Geplantes Vorhaben: Sentiment und News (Freigabe Tobias steht aus)

Tobias 28.10.2026: „Ich brauche unbedingt eine Sentiment- und News-Sektion“, ohne KI-Agent. **Vorgabe: Startup, kein
Hobbyprojekt. Tech-Stack offen (eigene Datenbank kommt), Markt global, nicht auf GitHub Actions oder Deutschland beschränken.**
Gründliche Prüfung von last30days-skill: `DATENQUELLEN.md` Abschnitt 4.

Vorschlag (Reihenfolge offen, Entscheidung Tobias):
- [ ] **Ranking-Engine aus last30days übernehmen** (MIT, nur Standardbibliothek): einheitliches Datenmodell, Relevanz,
      Engagement-Gewichtung, Rank Fusion, Duplikate, Story-Cluster → Grundgerüst für News-Feed und Sentiment.
- [ ] **Quellen anbinden:** Pflichtmeldungen (EQS, SEC 8-K), Polymarket, Stellenanzeigen (Greenhouse/Lever/Ashby),
      Bluesky, Hacker News, Reddit (Arctic-Shift-Archiv, interne Seitenteile), X (Cookies/GraphQL oder API), YouTube (yt-dlp),
      StockTwits und alle weiteren Anschlüsse aus `DATENQUELLEN.md` Abschnitt 4.
- [ ] **Stimmungswert je Firma und Tag** in der Datenbank: jede Meldung/jeden Beitrag einmal bewerten (Finanz-Wörterbuch,
      FinBERT oder Sprachmodell im Stapel), Firmenzuordnung über ISIN/Ticker; danach Event Study auf Stimmungsänderungen.
- [ ] **Lizenzierte Nachrichten** für die News-Sektion prüfen: GDELT (frei), Benzinga/Polygon/Tiingo (bezahlt).
**Tobias 28.10.2026: Alles Recherchierte wird übernommen**, auch Cookies und Umgehung von Bot-Sperren (noch nicht live,
kein Geld). Rechtslage erst vor dem Start klären (Status-Spalte in `DATENQUELLEN.md`). Noch nichts gebaut, erst Recherche.

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

- [ ] **Taktung reicht nicht** (31.10.2026 erneut gezählt: 24.–30.10. je 5–7 geplante Läufe statt 48, Lücken bis 6,5 h,
      0 Fehler). Lösung vorbereitet: Kommentar im Workflow, Anleitung cron-job.org an Tobias gegeben (Token fein
      abgestuft, nur Repo insider, Actions: Read and write; POST auf `…/workflows/aktualisieren.yml/dispatches` mit
      `{"ref":"main","inputs":{"immer":"false"}}`, sonst rechnet jeder Lauf neu und committet). **Eingerichtet 31.10.2026**, Testlauf 204, Lauf 17:34 UTC erfolgreich. Nach 1–2 Tagen Läufe zählen (Soll ~48/Tag), dann Punkt abhaken (Planungs-App #62). Workflow-Kommentar gepusht 31.10.2026. Alt: gepusht, aber geprüft am 24.10.2026: nur 12 geplante Läufe in ~1,5 Tagen (23.10.: 6 statt
      ~48), alle erfolgreich. Neue Meldungen kommen also mit Stunden Verspätung. Abhilfe: externer Auslöser (cron-job.org
      ruft `workflow_dispatch` über die GitHub-API auf; braucht ein Token mit Actions-Recht). Entscheidung Tobias.
- [ ] Diagramm auf der Firmenseite einmal auf dem echten Handy ansehen.
- [ ] Code-Review (`/code-review high`) in einem neuen Chat.
- [ ] **Datenquelle für Fundamentaldaten klären**, bevor der GuruFocus-Ausbau beginnt: Yahoo (gratis, ~4 Jahre,
      lückenhaft), EODHD / Financial Modeling Prep (~20–30 €/Monat, Lizenz für öffentliche Anzeige prüfen),
      Unternehmensregister (gratis, nur von Hand). ESEF-Probe 22.10.2026 (`.recherche/esef_probe.md`): filings.xbrl.org
      hat keine deutschen Berichte; freier Weg erst über ESAP (EU-Portal, spätestens 10.07.2027). Tobias (22.10.2026):
      nach hinten verschoben, zuerst Stimmrechte und Rückkäufe aus EQS.
      **Uni-Datenbanken (Nova SBE, geprüft 28.10.2026):** WRDS (Compustat, I/B/E/S, BoardEx, 13f), LSEG Workspace,
      Bloomberg, Orbis, Pitchbook sind Lizenzen nur für Lehre/Forschung → **nicht für die öffentliche Website**
      (Weitergabe/Anzeige verboten, Risiko für den Uni-Zugang). Nutzbar nur privat zum Prüfen (EQS-Abdeckung ~88 %,
      fehlende Großaktionäre vor 2018) und für eine mögliche Forschungs-/Masterarbeit. Empfehlung: WRDS-Konto anlegen
      (Uni-Mail, Subscriber „Universidade Nova de Lisboa – Nova SBE“, Typ „Students“); vor jeder indirekten Nutzung
      Nutzungsbedingungen bei der Bibliothek erfragen.
- [ ] **Zukünftiger Schritt: FinceptTerminal als Datenquelle testen** (Tobias 28.10.2026, nur Daten, kein Code
      übernehmen). **Quellenkatalog (~240 Skripte) ausgewertet: `DATENQUELLEN.md` Abschnitt 6.** github.com/Fincept-Corporation/FinceptTerminal, C++/Qt-Desktop-Programm, ~33.000 Sterne.
      Ziel: mehr Finanzdaten für ein vollständiges Bild (Fundamentaldaten, Kennzahlen usw.).
      Lizenz (gelesen 28.10.2026, Version 2.0): Software AGPL-3.0 nur für privat/einzelne Studierende,
      sonst kostenpflichtige Lizenz; **Fincept-Daten und -APIs eigener Dienst, gratis nur „individual personal
      and educational use“**. Strafandrohungen ab 50.000 USD, Gerichtsstand Delhi. Kein Fincept-Code und kein
      Nachbau des Aussehens (Trade Dress) in die Website.
      Test (abbrechbar, an SAP/Zalando/Deutz wie bisher): 1) Welche Daten gibt es für DAX/MDAX, wie weit zurück,
      wie vollständig? 2) Eigene Fincept-Daten oder nur Durchreichen fremder Quellen (Yahoo, FRED …)? Dann lieber
      die Originalquelle direkt nutzen. 3) Gibt es eine abrufbare Schnittstelle oder nur das Programm?
      4) **Vor jeder Anzeige auf der Website** schriftlich klären (support@fincept.in), ob die öffentliche Anzeige
      erlaubt ist: Website ist öffentlich, nicht nur privat. Vergleich mit EODHD/FMP (Punkt darüber).
- [ ] **Große Datenbank, Ausbau auf USA und weitere Märkte** (Tobias 28.10.2026, perspektivisch): Quellen in
      `DATENQUELLEN.md`. Empfohlene Reihenfolge USA (alles SEC, offiziell, gratis): Form 4 (Insider), companyfacts
      (Fundamentaldaten), 13D/13G (Großaktionäre), Finra (Leerverkäufe). Inoffizielle Quellen (Nasdaq, TMX) nur nach
      Prüfung der Nutzungsbedingungen. Datenbank-Frage hängt mit „Statisch bleiben“ und „Repository-Größe“ zusammen.
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
- **28.10.2026:** Stimmrechte-Historie geprüft: fertig bis auf 2 Auto1-Mitteilungen (Kodierungsfehler bei EQS).
  Leser repariert (Kodierung, zweizeilige Personennamen), Auto1 nachgeladen → Block 3 fertig. Block 4 gebaut und getestet. 53 alte Namen korrigiert.
  Gepusht (f71f27b). Hochtief-Name repariert, Block 5 (Großaktionäre auf den Firmenseiten) gebaut und lokal geprüft.
  Gepusht (f26ea18). Test Block 6: Mitteilungen vor ~2016 sind Fließtext, Regex-Leser unbrauchbar (Details Block 6).
  Porsche-Hinweis. Block 6a (Lader vor 2018) gebaut und an Krones/Talanx getestet.
  Lizenz von FinceptTerminal geprüft; Test als Datenquelle als zukünftiger Schritt unter „Offen“ aufgenommen.
  Datenbankliste der Nova SBE bewertet: nur für Forschung/Prüfung, nicht für die Website (Notiz unter „Offen“, Fundamentaldaten).
- **28.10.2026 abends:** OpenBB geprüft und verworfen (Begründung unter „Guru-Depots“). Guru-Depots Block 1–3 gebaut und getestet (Baupost-Einheitenfehler abgefangen). `.env^t^t` in `.env` umbenannt (Schlüssel war nicht von `.gitignore` erfasst). Push-Befehle an Tobias übergeben (Stimmrechte-Action lief parallel, kein Konflikt). Gepusht (b9c18da). Guru-Link in die Fußzeile verschoben, Umbau als offener Punkt notiert. OpenBB-Quellen in `DATENQUELLEN.md` erfasst (17 Anschlüsse im Repository mit Adressen und Schlüsselpflicht, 16 ausgelagerte PyPI-Pakete wie FMP und Yahoo; Korrektur: diese gibt es weiterhin, nur nicht mehr im Repository). last30days-skill für Sentiment/News geprüft (`DATENQUELLEN.md` Abschnitt 4): nicht für die Website, StockTwits sperrt Skript-Abrufe (403), deutsche Foren fehlen; Empfehlung bleibt Sentiment aus EQS. Nachfrage Code-Übernahme beantwortet, Plan „Sentiment und News“ (3 Blöcke) notiert, Freigabe steht aus. Tobias: Startup-Sicht, Stack offen, global → last30days gründlich neu bewertet (Ranking-Engine übernehmbar, Quellen nach Rechtslage sortiert, Finanz-Perlen: StockTwits, Polymarket, Stellenanzeigen); Plan „Sentiment und News“ neu gefasst. Tobias: alles übernehmen, auch graue Wege → Quellen-Katalog in `DATENQUELLEN.md` vollständig (inkl. Arctic Shift), Status nur als Hinweis für vor dem Start. Bisherige Repositories aus Startup-Sicht neu bewertet: OpenBB (180 Datenmodelle als Schema-Vorlage, Anbieter-Code übernehmbar, Abschnitt 5), FinceptTerminal (~240 Datenquellen, u. a. OpenFIGI, GLEIF, Wikipedia-Aufrufe, SimFin, Quiver, Abschnitt 6), Überblick Abschnitt 7. Einstiegsabschnitt für neue Chats oben in dieser Datei.
- **29.10.2026:** Archiv vor 2018 (6a) per Action geladen: 88 von 90 Firmen. Rheinmetall und Scout24 offen (je 1 Mitteilung
  „ohne Inhalt“, auch lokal reproduzierbar, Seite hat aber Inhalt → Leserfehler, nicht Drosselung). Außerdem meldet
  `stimmrechte_laden.py` „Alle Firmen fertig“, obwohl Firmen offen sind (irreführend, nicht behoben). 6b: Fließtexte mit
  DeepSeek ausgelesen, bis das Guthaben (1 $) aufgebraucht war: 4.229 von 5.035 Texten (Details Block 6b).
  Gepusht (967d34a). Automatische Anzeige der alten Daten verworfen (zu viele überholte Stände), stattdessen von Hand
  geprüfte Liste (6c); dabei Fehler bei Renk, Hella, Eventim gefunden und behoben.
- **30.10.2026:** Stimmrechte: Stände vor 2018 ausgeblendet, Konzernketten/Umfirmierungen zusammengefasst (Hugo Boss nicht mehr über 100 %), Porsche/Traton/Knorr-Bremse geprüft, Rheinmetall/Scout24 (EQS-Seiten defekt) abgeschlossen, Meldung „Alle Firmen fertig“ korrigiert. Danach Doppelungen Brenntag/Nemetschek/Fonds von Hand bereinigt, Vorhaben Stimmrechte abgeschlossen.
- **30.10.2026 (2):** Landingpage (#9) geplant: Rückfragen geklärt (E-Mails + Schaufenster, Englisch, Name offen, Testseite `docs/labor/`), Plan in 6 Phasen oben unter „Geplantes Vorhaben: Landingpage“. Google Stitch geprüft (MCP-Anbindung nur über inoffizielles Paket). Noch nichts gebaut. Rückkäufe Block 1–3 gebaut (Leser, Lader + Action, Anzeige), lokal getestet, wartet auf Push.
- **30.10.2026 (3):** Landingpage Phase 0+1: Testseite `docs/labor/` gebaut (Arbeitsname Boardtrades, Englisch, Live-Tafel, Event-Study-Kurve, Cluster-Stapel, Abdeckung, Fragen, Warteliste ohne Anschluss), `robots.txt` sperrt `/labor/`. Geprüft bei 1440/768/390 px. Nicht gepusht.
- **30.10.2026 (4):** Tobias lehnt Testseiten-Design ab; neue Reihenfolge Marketing → Stitch → Bau, EmailOctopus statt Buttondown. `docs/labor/` und `robots.txt`-Änderung nicht pushen.
- **30.10.2026 (5):** Verworfene Landingpage-Arbeit gelöscht (`docs/labor/`, `.taste-skill/`, `robots.txt`/`.gitignore` zurückgesetzt). Abschnitt „Marketing und Website“ neu gefasst: erst Positionierung, dann Newsletter.
- **30.10.2026 (6):** Rückkäufe Block 4 geprüft (Planung #60): Historie vollständig geladen, Kontrollzahlen ausgewertet, Fehler „keine Rückkäufe“ bei Firmen ohne EQS-Meldungen gefunden (noch nicht behoben).
- **30.10.2026 (7):** `ARCHITEKTUR.md` geschrieben (Planung #7): heutige Grenzen, empfohlenes Ziel, Weg in 5 Blöcken, offene Entscheidungen. Nichts gebaut.
- **30.10.2026 (8):** Fundamentaldaten (#6): erster Plan (Bezahlanbieter) von Tobias verworfen (kein Geld, global, nur lokal). Gratis-Quellen getestet, TradingView-Screener liefert 20 Jahre für alle Märkte; neuer Plan unter „Geplantes Vorhaben: Fundamentaldaten“, nichts gebaut.
- **31.10.2026:** Fundamentaldaten (#6) Block 1 (Sammler TradingView/onvista/SEC) und Block 2 (Kennzahlen) gebaut und gegen AlleAktien-Karte Atoss geprüft; Daten nur lokal (`.gitignore`), nicht gepusht.
- **31.10.2026 (2):** Fundamentaldaten Block 3: Abschnitt „Finanzkennzahlen“ auf den Firmenseiten (nur lokal, weil Daten in `.gitignore`), Quellen-Prioritätstabelle, Fehler „11 von 10“ und Allianz-Umsatzschätzung behoben.
- **31.10.2026 (3):** Fundamentaldaten Block 4: Qualitätscheck (10 Kriterien), Kategorie nach Peter Lynch, gedeckelte Renditeerwartung; Vorhaben #6 (lokal) abgeschlossen.
- **31.10.2026 (4):** Nasdaq-Gewinnschätzungen für US-Firmen eingebaut; Abdeckung von 32 Märkten geprüft (`DATENQUELLEN.md` Abschnitt 8), SEC hat auch ausländische Firmen mit US-Notierung.
- **31.10.2026 (5):** Eulerpool-API geprüft (nur Webseiten, `DATENQUELLEN.md` Abschnitt 9): Gratis 100.000 Abrufe für Prototypen, Schätzungen nur eingeschränkt; Builder 99 $/Monat mit Anzeigerecht. Probe wartet auf Gratis-Schlüssel von Tobias.
- **31.10.2026 (6):** Eulerpool mit Gratis-Schlüssel getestet (`DATENQUELLEN.md` Abschnitt 9): GuV mit EBIT über 25–43 Jahre weltweit, Schätzungen bis 2030, teils verschlüsselt (SAP, nicht umgehen); Eulerpool ist Datenlieferant von AlleAktien (AAQS-Adresse liefert die Kartenwerte). Einbau wartet auf Freigabe.
- **31.10.2026 (7):** Sonntags-Report: `sonntags_report.py` (Entwurf aus eigenen Daten) und `newsletter/GESPRAECHE.md` (Leitfaden Anlegergespräche). Formular wartet auf EmailOctopus-Liste von Tobias.
