# Verlauf (ausgelagert aus CLAUDE.md am 09.11.2026)

Neue Einträge unten anhängen: `- **TT.MM.JJJJ (Thema):** …`


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
- **31.10.2026 (8):** EmailOctopus für den Newsletter verworfen (1 Formular im Gratistarif), Kit eingerichtet: Anmeldekarte auf der Startseite, Datenschutzabsatz, Verbindung geprüft.
- **31.10.2026 (9):** Testanmeldungen (gmx, proton) kommen bei Kit an („Unconfirmed“, 2 Mails verschickt), Bestätigungsmails erreichen Tobias aber nicht → Absenderadresse prüfen. Kit-MCP (`app.kit.com/mcp`, in `~/.claude.json`) verbunden, braucht aber Bezahltarif → unbrauchbar. Formular nach unten verschoben (nicht gepusht).
- **31.10.2026 (10):** Ursache gefunden: Absender war tobzwilling@proton.me, proton.me hat DMARC `p=quarantine` (streng) → Kits Mails gelten als gefälscht. Lösung: Sendedomain tobiaszwilling.me bei Kit (über „Set this up for me“, DNS bei Namecheap: CNAME `ckespa`, `cka._domainkey`, `cka2._domainkey` auf convertkit.com, TXT `_dmarc` `v=DMARC1; p=none;`, alle geprüft), Weiterleitung `report@tobiaszwilling.me` → gmx. Offen: Validate in Kit (wartete auf DNS), Absender `report@` anlegen und als Default setzen, Testanmeldung wiederholen.
- **31.10.2026 (11):** Sendedomain tobiaszwilling.me bei Kit verifiziert. Weiterleitung `report@` → gmx kam nicht an (GMX nimmt weitergeleitete Kit-Mails nicht), Ziel auf tobzwilling@proton.me geändert → Absender „Rhodus“ <report@tobiaszwilling.me> bestätigt. Offen: als Default setzen, Testanmeldung.
- **31.10.2026 (12):** Bestätigungsmail von report@tobiaszwilling.me kommt bei Proton an (authentifiziert), bei GMX nicht: Kontakt steht auf „Unconfirmed“, nicht „Bounced“ → vermutlich GMX-Verzögerung/Ordner „Unbekannt“ bei neuer Domain. Offen: am 01.11. GMX erneut prüfen; Bestätigungsmail auf Deutsch (Text-Vorschlag im Chat: Betreff „Bitte bestätige deine Anmeldung zum Sonntags-Report“), eigene Postadresse in Kit statt Seattle; Push der Formular-Verschiebung.
- **31.10.2026 (13):** Bestätigungsmail in Kit auf Deutsch angepasst (Tobias). Offen: eigene Postadresse in Kit (statt Seattle), GMX-Zustellung am 01.11. prüfen, Push der Formular-Verschiebung.
- **31.10.2026 (7):** Eulerpool in Sammler und Kennzahlen eingebaut (EBIT 10 J. bei 91 statt 7 Firmen, Schätzungen bis 3 Jahre), alle Firmen gegen AAQS abgeglichen, ROCE/Verschuldung auf Geschäftsjahr umgestellt (ROCE 96 % gleich mit AlleAktien). Offen: Zykliker-Schwelle (29 statt 13).
- **31.10.2026 (Logo):** MVP-Logo begonnen, nur Bildzeichen (Name noch offen), Graustufen, Wirkung „seriös, belegt“ + „modern, Tech“, Einsatz Sonntags-Report, Website + Favicon, Social Media. Drei Konzepte in `logo/` (v1 verworfen: QR-Code-, Uhrzeiger-, Audio-Wirkung). Übersicht `logo/konzepte-v2.png`, Empfehlung A „Innenblick“. Wartet auf Tobias' Wahl; danach Logo-Paket (Farbe, Favicon, Icons).
- **31.10.2026 (Logo 2):** Tobias verwirft die Tech-Entwürfe: Logo soll elitär, „old money“, seriös wirken, Schriftzug in Serifenschrift. Name jetzt Rhodus. Drei neue Konzepte in `logo/` (Übersicht `logo/rhodus-konzepte-v3.png`): A Inschrift (Cinzel), B Privatbank (Bodoni Moda, Empfehlung), C Münze (Rose von Rhodos, Ring, Cormorant Garamond). Schriften frei lizenziert (OFL, Google Fonts) in `logo/schriften/`, Umwandlung in Pfade mit `logo/bauen.py`. Wartet auf Tobias' Wahl.
- **31.10.2026 (Logo 3):** Tobias wählt A „Inschrift“. Logo-Paket fertig in `logo/kit/` (Richtlinien `logo/kit/RICHTLINIEN.md`): Schriftzug, Monogramm + kräftige Kleinversion, Farben Rhodus-Grün #1E3B2F / Creme #F3EEE2, Favicon-Satz auf grüner Kachel (dunkle Tabs), Profilbild, Newsletter-Kopf 1200×300, Präsentationstafeln. Neu bauen mit `python3 logo/paket.py` (im Ordner `logo/`). Noch nicht auf Website/Newsletter eingesetzt.
- **31.10.2026 (Logo 4):** Aufgeräumt: alle verworfenen Entwürfe, Konzeptübersichten, Testbilder, `bauen.py` und die Schriften Bodoni Moda/Cormorant gelöscht. In `logo/` bleiben nur `kit/`, `paket.py`, `text2path.py`, `praesentation.json` und `schriften/Cinzel.ttf` + `OFL.txt`. Rechtscheck: Schrift (OFL) erlaubt Logo-Nutzung; Urheberrecht am R gibt es nicht (keine Schöpfungshöhe), Schutz nur über eine Marke (Empfehlung: zuerst Wortmarke RHODUS beim DPMA, 290 € für Klassen 36, 41, 42; Bildzeichen vorher in TMview als Bildmarke suchen).
- **31.10.2026 (Aktionärsring):** Bachelorarbeits-Bezug aus Notiz und Gedächtnis entfernt (Tobias: längst durch, Startup). Ring für die Aktionärsstruktur beschlossen; N-PORT-Test: US-Fonds bringen netto Median +8,7 Pp. mit Namen (36 → 48 %). Plan unter „Geplantes Vorhaben: Aktionärsring“, Planungs-App #65. Danach Schritt 1 gebaut: Ring auf den Firmenseiten (lokal geprüft, nicht gepusht). Schritt 2: eigene Aktien aus § 40-Mitteilungen als Segment (11 Firmen ≥ 3 %). Schritt 3: US-Fonds (N-PORT) als Segmente, nächtlich automatisch; Median mit Namen 36 → 49 %. Danach Namen bereinigt, Norwegischer Staatsfonds, Vorzugsaktien und Firmen ohne EQS-Stimmrechte (VW, Sartorius, Wacker, DWS, Airbus, RTL); Median 50,5 %, Thema bis auf Pflegepunkte abgeschlossen. Danach Darstellung auf Tobias' Rückmeldung umgebaut: eine Tabelle als Legende, nur Aktienanteile, unterscheidbare Farben.
- **31.10.2026 (Logos):** `logos_laden.py` gebaut: Firmenlogos von Wikidata/Commons nach `docs/logos/`, 97 von 97 (Hochtief von hochtief.com), Übersicht `logos_uebersicht.html`. Wartet auf Durchsicht durch Tobias, noch nicht auf der Website.
- **31.10.2026 abends:** Action #65 brach ab (`ImportError: DECKEL`): `seiten.py` war committet, das dazugehörige
  `kennzahlen.py` nur lokal. `kennzahlen.py` nachcommittet (4d86a3e), Lauf danach grün. Lehre: vor dem Push
  `git status` prüfen, ob committete Dateien von lokal geänderten abhängen. Noch lokal offen: `fundamental.py`,
  `stimmrechte.py`, `DATENQUELLEN.md`, `ARCHITEKTUR.md`, `logo/`, `newsletter/2026-11-01.md`.
- **31.10.2026 (Logos 2):** Logos auf Firmenseiten und in der Firmenliste eingebaut, lokal geprüft, nicht gepusht.
- **31.10.2026 (Logos 3):** Logo groß rechts im Firmenkopf (Wunsch Tobias), lokal geprüft; Ursache „live keine Logos“: Bot baut nur bei neuen Meldungen neu.
- **31.10.2026 (8):** Zykliker-Regel auf 2× ≥ 40 % verschärft (15 statt 29). Git geprüft: lokal = GitHub (51225c6), Eulerpool-Einbau vollständig gepusht, Action seit #66 grün, Live-Seiten 200. Parallel offen aus anderer Sitzung: `seiten.py`/`style.css` (Logo groß, Aktionärsstruktur), `logo/`, `newsletter/2026-11-01.md`.
- **31.10.2026 (Design System):** Rhodus-Design-System in Claude Design angelegt (privat): https://claude.ai/artifact/X1njLe2gDXmPDRtszcsTRN
  Inhalt: Markenhandbuch, Farben (Markenfarben + alle Farben der Live-Seite aus `docs/style.css`, hell/dunkel), Schriftgrößen der Seite,
  Abstände, Ecken, Logos aus `logo/kit/`, Cinzel, Bausteine Kachel, Karte, Hinweisband, Sonntags-Report-Formular. Quelldateien im
  Scratchpad der Sitzung (nicht gesichert; Bearbeiten über das Artefakt). **Offen (Tobias):** Schrift für Text/Zahlen (Karte „Schriftwahl“:
  Systemschrift, Source Sans 3, IBM Plex Sans, Source Serif 4), Website auf Grün/Creme umstellen oder neutral lassen, Untertitel.
  Landingpage-Entwürfe in Claude Design erst später (Website erst, wenn das Produkt steht).
- **31.10.2026 (Design System 2):** Tobias: heutige Seite wirkt „zu sehr Research-Seite statt Startup/Finance“ → Oberfläche wird neu
  gestaltet. Design System auf das Feste reduziert: Logo, `rhodus-gruen`/`creme` (Tobias: „Website-Farben passen“ = Website in
  Grün/Creme), Cinzel, Ton. Bausteine Kachel/Karte/Hinweisband/Formular und alle Farben/Größen der alten Seite entfernt (Kopie der
  ersten Fassung im Scratchpad `rhodus-ds-v1-sicherung`, sonst über den Versionsverlauf des Artefakts). Untertitel bleibt offen.
  Nächster Schritt: Referenzseiten von Tobias, dann Richtungen auf einer Design-Leinwand.
- **31.10.2026 (Design System 3):** Textschrift festgelegt (Tobias): **Geist** (OFL, Google Fonts), als `sans` im Design System.
  Vergleichskarte „Schriftwahl“ entfernt. Systemschrift (A) gefiel, sieht aber nur auf dem Mac so aus (SF Pro). Untertitel weiter offen.
- **31.10.2026 (Startseite-Richtungen):** Drei Entwürfe der Startseite auf einer Claude-Design-Leinwand (privat):
  https://claude.ai/artifact/416CVL22JqidLmcVQwTuWf – 1 Privatbank (viel Weißraum, Linien, ruhig), 2 Fintech (grüner Kopf,
  Produktkarte, runde Formen, Funktionskacheln), 3 Daten vorn (Tabelle der neuesten Käufe, Event-Study-Kurve, Cluster-Karte).
  Alle in Grün/Creme mit Geist und Logo, nur echte Zahlen (Stand 31.10.2026: 6.151 Meldungen, 94 Firmen, 179 Cluster,
  Knorr-Bremse 30.10., CAAR Käufe −1,66 → −0,97 %). Überschriften sind Vorschläge, nicht beschlossen. Wartet auf Tobias' Wahl.

- **06.11.2026 (Newsletter):** Tobias: „letzten Sonntag ging nichts raus“. Ursache: Versand war nie eingerichtet (nur Entwurfsskript). Tobias will Automatik → gebaut (nicht gepusht): `sonntags_report.umschichtungen` (Kauf + Verkauf derselben Firma am selben Geschäftstag zum Kurs ±1 % = interne Übertragung, eigener Abschnitt, nicht mitgezählt; trifft seit 09/2026 ATOSS, RCM, KST, NFON, Hövelrat, alle plausibel). `--kit` legt Broadcast über Kit-API v4 an (`send_at` Sonntag 08:00 Berlin) und schickt Telegram mit Text und Link; `--entwurf` nur Entwurf zum Testen. Action „Daten aktualisieren“: Schritt „Sonntags-Report planen“ samstags ab 18 Uhr, `newsletter/<Sonntag>.md` wird committet und verhindert Doppelversand. Push-Schutz kennt `sonntags_report`. Sicherung: `.recherche/sicherung_newsletter/`. Kit-API funktioniert im Gratistarif (Test 06.11.2026: Entwurf 26853741 angelegt), Secret `KIT_API_KEY` in GitHub angelegt. **Offen (Tobias):** Testentwurf in Kit löschen, pushen, Sonntag 08.11. prüfen, ob der Report rausging.

- **06.11.2026 (Personenseiten):** Quiver-Vorbild bewertet, Personenseiten für 803 Vorstände/Aufsichtsräte gebaut und
  geprüft (Details unter „Personenseiten und US-Politiker“), Plan für US-Politiker recherchiert (House-Daten getestet).
- **06.11.2026 (Kongress):** Tobias gibt die Reihenfolge frei. Repräsentantenhaus 2014–2026 lokal geladen (Leser, Lader,
  Zuordnung zu Abgeordneten, Politikerseiten wie Quiver), Altformat bis Mitte 2022 bewusst offen. Senat und Trump
  warten auf Entscheidungen Tobias (Erklärung § 105(c) bzw. Kosten Texterkennung). Nur lokal, nicht live.
- **06.11.2026 (Kongress 2):** Senat als Aufgabe #68 in der Planungs-App und in `US_KONGRESS_OFFEN.md` (Tobias: „jetzt
  nicht“). Kostenschätzung Auslesen per Sprachmodell gemessen (~3,70 $, höchstens ~6 $, Details in der .md). US-Universum
  freigegeben → S&P 500 mit Staatsaufträgen (USAspending) und PAC-Spenden (FEC), Seiten `docs/us/`. Lobbying-Register
  braucht einen Schlüssel von Tobias.
- **07.11.2026 (Kongress 3):** Push vom 06.11. enthielt nur die Daten (Patch scheiterte an `docs/index.html`), Patch
  repariert und gepusht (9b4a2af). Kongress-Geschäfte in GOOG/FOX/NWS stehen jetzt auf den Seiten GOOGL/FOXA/NWSA
  (`us_firmen.ZWEITE_GATTUNG`, Alphabet 115 → 245). Älteres Formular und Trump bis kurz vor den bezahlten Lauf vorbereitet
  (Texte geladen, Skripte fertig), DeepSeek-Lauf startet Tobias. Papier-Scans brauchen ein Bild-Modell (Entscheidung).
  Danach (Tobias: „Senat anfangen“, „älteres Formular und Scans aus dem Datensatz“): Senat, älteres House-Formular
  und House-Scans aus dem Hugging-Face-Datensatz congressional-stock-trades, gegen eigene Daten geprüft, nur lokal;
  DeepSeek-Weg für das ältere Formular entfällt. Trump danach mit z.AI-Bildmodell GLM-4.6V-FlashX ausgelesen
  (10.616 Geschäfte aus 378 Seiten, ~0,46 $), Texterkennung verworfen, weil sie Spalten verlor.

- **08.11.2026 (Recherche):** Bullflow (Optionsfluss) und Krypto-Wale bewertet → `DATENQUELLEN.md` Abschnitt 10. Optionsfluss = OPRA, anonym, kein Alleinstellungsmerkmal; Krypto-Wale/Memecoin-Entwickleradressen passen zum Sentiment-Schwerpunkt. Nichts gebaut. Als nächster Schritt notiert (Planungs-App #78).
- **08.11.2026 (Recherche 2):** Fincept-MCP (docs.fincept.in) geprüft und verworfen → `DATENQUELLEN.md` Abschnitt 11.
- **08.11.2026 (Recherche 3):** Microsoft Qlib geprüft: Rahmenwerk für Quant-Modelle, keine Datenquelle, jetzt nicht → `DATENQUELLEN.md` Abschnitt 12.
- **08.11.2026 (Recherche 4):** Scraping-Werkzeuge für eine private Sentiment-Probe bewertet (Scweet, twikit, Apify, Scrapling, Scrapy, Firecrawl) → `DATENQUELLEN.md` Abschnitt 13. Empfehlung: Reddit über Arctic Shift zuerst, X als Stichprobe. Nichts gebaut.
- **08.11.2026 (Sentiment-Probe):** eigener Ordner `~/Desktop/Claude/sentiment-probe` (nur lokal, Stand dort in CLAUDE.md). Reddit 2 Jahre: Aufmerksamkeitsschübe kommen nach dem Kursanstieg, danach −5 % Überrendite in 20 Tagen (Aktien und Krypto) → Signal als Hype-Warnung, Vorbehalte offen.
- **08.11.2026 (Recherche 5):** Nachrichten als Sentiment-Erweiterung überlegt → `DATENQUELLEN.md` Abschnitt 14: als Erklärschicht für Reddit-Hype (mit/ohne Pflichtmeldung, Pump-Merkmale), nicht als eigenes News-Sentiment. Nichts gebaut.
- **08.11.2026 (EDGAR-Test, nur Test):** in `~/Desktop/Claude/sentiment-probe` (`edgar_test.py`, Stand dort): Hype um Quartalszahlen harmlos, Hype + 8-K ohne Zahlen (Verträge, PM, Finanzierung) Median −25 % in 20 Tagen (n 35), ohne Meldung −13 %. Vorläufig, Zufallsfund möglich.
- **08.11.2026 (Fristaufgaben, Claude):** #69 war schon gepusht. #70: /us/ noch 404 (Action „immer“ fehlt). #71:
  Samstagslauf hat den Report in Kit angelegt (Datei `newsletter/2026-11-08.md` entsteht nur nach Annahme durch Kit);
  Versand und Löschen des Testentwurfs prüft Tobias (Kit-MCP nur im Bezahltarif). #72 Trump-Seite gebaut (s. Trump).
  #73 Lobbying-Lader + Abschnitt gebaut (s. 4d). #74/#75 vorbereitet in `RECHTSFRAGEN.md` (neu). #76: `senat.csv`,
  `kongress_alt_texte.csv`, `trump_texte.csv` geprüft, kein Code greift mehr darauf zu; von Tobias gelöscht
  (08.11.2026). Sicherung von `export.py`/
  `seiten.py` vor den Änderungen: `.recherche/sicherung_trump/`. Nicht gepusht.
- **09.11.2026 (Aufräumen):** CLAUDE.md von 125 KB / 1.076 Zeilen auf eine Kurzfassung gekürzt. Details unverändert nach
  `VORHABEN.md`, Verlauf nach `VERLAUF.md`; Sicherung `.recherche/sicherung_claude_md/CLAUDE_2026-11-09.md`.
- **09.11.2026 (Livegang):** Lobbying/Trump-Code gepusht (099af96), `/us/` mit Lobbying live; Test ohne nur lokale
  Dateien bestanden. Datenschutzabsatz `#personen` ins Impressum eingebaut (#75), Lücken der Erklärung in `VORHABEN.md`.
- **09.11.2026 (Impressum 2):** Funde der Prüfung behoben: Verantwortlicher nach DSGVO, Art. 77 + BayLDA, Satz zu
  kontrollierten Gesellschaften, live genutzte Datenquellen ergänzt; Notiz „nichtkommerziell streichen vor Bezahlstufe“.
