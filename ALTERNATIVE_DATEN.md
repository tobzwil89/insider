# Rechtslage und Ausbauideen: Gespräch vom 22.10.2026

Zusammenfassung eines Chats auf claude.ai (nicht Claude Code). Hintergrund: Lassen sich Aktiengeschäfte von
Politikern in Deutschland oder der EU ähnlich wie die Directors' Dealings auswerten? Wenn nicht, welche
anderen öffentlichen Daten passen zum Insider-Monitor? Stand und Architektur des Projekts: `CLAUDE.md`, `GURUFOCUS.md`.

## Kurzfassung

- **Politiker-Tracker nach US-Vorbild ist in Deutschland/EU nicht möglich**: Es gibt keine Pflicht, einzelne Aktiengeschäfte zu melden.
- **Wichtig für die bestehende Event Study**: Die Meldeschwelle für Directors' Dealings hat sich zweimal geändert
  (siehe unten). Das ist ein Strukturbruch in `daten/meldungen.csv` und noch nicht berücksichtigt.
- **Bester Ausbau**: Stimmrechtsmitteilungen, Aktienrückkäufe und Leerverkaufspositionen. Die ersten beiden
  erscheinen ebenfalls über EQS, also wiederverwendbar mit `pipeline/eqs.py`.

## 1. Meldeschwelle Directors' Dealings (Art. 19 MAR): Folgen für die Daten

| Zeitraum | Schwelle pro Person und Kalenderjahr | Grundlage |
|---|---|---|
| 2018–2019 | 5.000 € | Art. 19 Abs. 8 MAR (Standard) |
| 2020–2025 | 20.000 € | Allgemeinverfügung der BaFin nach Art. 19 Abs. 9 MAR (ab 01.01.2020) |
| ab 01.01.2026 | 50.000 € | EU Listing Act (EU-Standard jetzt 20.000 €, Behörden dürfen 10.000–50.000 € wählen); BaFin-Allgemeinverfügung vom 04.12.2025 setzt den Höchstwert |

Meldung an Emittent und BaFin binnen drei Geschäftstagen, der Emittent veröffentlicht danach unverzüglich.

**Offene Aufgaben daraus:**
- [ ] Prüfen, ob die Zahl der Meldungen 2026 sichtbar gesunken ist (Meldungen je Jahr aus `meldungen.csv` zählen).
- [ ] Event Study nach Schwellen-Zeiträumen getrennt rechnen oder einheitlich filtern: Für einen fairen Vergleich
      über alle Jahre nur Ereignisse werten, bei denen das Jahresvolumen der Person 50.000 € überschreitet.
      Erst messen, ob sich AAR/CAAR dadurch ändern, dann entscheiden.
- [ ] Auf der Methode-Seite einen Satz zum Strukturbruch ergänzen (ähnlich wie bei der EQS-Lücke).
- Hinweis: Der Cluster-Filter (≥ 50.000 €) ist zufällig deckungsgleich mit der neuen Schwelle, kein Handlungsbedarf.

## 2. Politiker: welche Pflichten es gibt (und warum sie nicht reichen)

- **Bundestag** (Abgeordnetengesetz, Verhaltensregeln): Beteiligungen und Aktienoptionen nur anzeigen, wenn sie
  **mehr als 5 %** der Anteile ausmachen; Änderungen binnen drei Monaten. Bei DAX/MDAX-Firmen praktisch nie erreicht.
- **Bundesminister und Parlamentarische Staatssekretäre ohne Mandat**: gar keine Offenlegungspflicht.
  AfD-Gesetzentwurf dazu im September 2026 (Drucksache 21/8106), Vorgänger 2024 (20/11617) gescheitert.
- **EU-Parlament**: jährliche Erklärung über finanzielle Interessen (Momentaufnahme, keine Einzelgeschäfte).
  EU-Kommission laut abgeordnetenwatch: Anlagen ab 10.000 € in einer Vermögenserklärung.
- **Zum Vergleich USA**: Kongressmitglieder melden jedes Geschäft ab 1.000 $ einzeln (STOCK Act, bis 45 Tage).

Ergebnis: Kein Datensatz mit Geschäftsdatum, Richtung und Volumen. Als Handelssignal unbrauchbar, höchstens als Recherche.

## 3. Ausbauideen (sortiert nach Nutzen und Passung zur Architektur)

Alle Ideen folgen den bestehenden Regeln: Pipeline rechnet, statische Dateien auf GitHub Pages, ISIN als feste ID.

### A. Kapitalmarktdaten mit Meldepflicht (empfohlen)

1. **Stimmrechtsmitteilungen (§§ 33 ff. WpHG)**: Schwellen 3/5/10/15/20/25/30/50/75 %. Zeigt aktivistische Investoren,
   Übernahmekandidaten, Ausstieg großer Anteilseigner. Erscheint über EQS → `pipeline/eqs.py` erweitern
   (andere Nachrichtenkategorie, anderes Formular). *Ungeprüft: Kategorie-Parameter im `admin-ajax.php`-Aufruf.*
2. **Aktienrückkäufe (Art. 5 MAR)**: wöchentliche Meldung der Emittenten (Stückzahl, Durchschnittspreis).
   Ebenfalls über EQS. Wenig beachtet, gut zu lesen. Auf der Firmenseite als zweite Markierungsart im Kursdiagramm denkbar.
3. **Netto-Leerverkaufspositionen ab 0,5 %** (EU-Leerverkaufsverordnung): öffentlich im Bundesanzeiger
   mit Fonds, Emittent, Position, Datum. Für einen Tracker für stark leerverkaufte Titel: Welche Fonds bauen wo
   Positionen auf oder ab? Gegenstück zu den Insider-Käufen.
   *Ungeprüft: Abrufweg (Export oder nur Suchmaske), Nutzungsbedingungen, Historie.*
4. **Ad-hoc-Mitteilungen mit Sentiment**: Gewinnwarnung vs. Prognoseerhöhung klassifizieren, Kursreaktion mit der
   vorhandenen Event Study messen. Ebenfalls EQS.

**Empfehlung:** 1–3 zu einem Dashboard „Smart Money DE“ zusammenführen. Ein neues Modul je Quelle
(`pipeline/stimmrechte.py`, `pipeline/rueckkaeufe.py`, `pipeline/leerverkauf.py`), Ergebnis als eigene Bereiche auf
den bestehenden Firmenseiten (`/firma/<TICKER>/`). Passt zu GURUFOCUS.md Punkt 4 (kleine Teil-Dateien je Firma).

### B. Politik über Umwege (zweite Ausbaustufe)

5. **Lobbyregister des Bundestags** (verpflichtend, mit API): Lobbyausgaben und Gesetzesvorhaben je Konzern,
   Index „Lobbyausgaben je Börsenwert“.
6. **Öffentliche Aufträge (TED, EU-Ausschreibungsdatenbank)**: Zuschläge an börsennotierte Firmen (Rüstung, Bau, IT).
   Das ehrlichste europäische „Politik-Signal“. Schwierigkeit: Firmennamen in TED auf ISIN abbilden.
7. **Nebentätigkeiten von Abgeordneten** (API von abgeordnetenwatch): Aufsichtsratsmandate × Ausschüsse.
   Recherche, kein Handelssignal.

### C. Verworfen oder später

- Stellenanzeigen (Stepstone/LinkedIn): starkes Signal, aber Scraping verstößt gegen Nutzungsbedingungen.
- Patente (DPMA/EPO): zu langsam für wöchentliche Entscheidungen.
- Google Trends, App-Rankings: nur für wenige Konsumtitel (Zalando, HelloFresh) brauchbar.

**Einschätzung:** Echte Überrendite aus frei verfügbaren Daten ist selten, Profis werten dieselben Quellen schneller aus.
Der größere Nutzen ist das Projekt als Nachweis für Bewerbungen (Beratung/PE), gerade in Verbindung mit der Bachelorarbeit.

## Vorschlag für die nächste Sitzung mit Claude Code

1. Erst die offenen Punkte aus `CLAUDE.md` erledigen (Push der Taktung, Läufe prüfen).
2. Strukturbruch der Meldeschwelle messen (Abschnitt 1).
3. EQS-Kategorien für Stimmrechtsmitteilungen und Rückkäufe untersuchen, Probe an 2–3 Firmen (z. B. SAP, Zalando, Deutz).
4. Abrufweg der Leerverkaufspositionen im Bundesanzeiger prüfen.
5. Danach entscheiden, welche Quelle zuerst gebaut wird, und `CLAUDE.md` (Offen, Entscheidungen) ergänzen.

## Quellen

- PwC Legal, Neue Meldeschwelle für Directors' Dealings: https://legal.pwc.de/de/news/fachbeitraege/neue-meldeschwelle-fuer-directors-dealings-art-19-mar
- Heuking, BaFin erhöht Schwellenwert: https://www.heuking.de/de/news-events/newsletter-fachbeitraege/artikel/listing-act-erleichterungen-bei-directors-dealings-bafin-erhoeht-schwellenwert-fuer-transaktionsmeldungen.html
- IHK-Newsletter 11/2019 (Schwelle 20.000 € ab 2020): https://www.ihk.de/blueprint/servlet/resource/blob/4623318/ea0c372aee9e64b0901c8153f7b8bd1d/newsletter-recht-november-2019-data.pdf
- abgeordnetenwatch, 5-%-Schwelle: https://www.abgeordnetenwatch.de/node/6144
- Bundestag hib 732/2026 (Minister): https://www.bundestag.de/presse/hib/kurzmeldungen-1217118
- Drucksache 20/11617: https://dserver.bundestag.de/btd/20/116/2011617.pdf
- EU-Parlament, Formular Erklärung der finanziellen Interessen: https://www.europarl.europa.eu/mepdif/197652_DFI_LEG9_rev0_DE.pdf
