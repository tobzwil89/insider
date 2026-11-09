# Vorhaben im Detail (Archiv aus CLAUDE.md, ausgelagert 09.11.2026)

Unverändert aus der alten CLAUDE.md übernommen: alle Vorhaben mit Plan, Prüfungen, Zahlen und Begründungen.
Der aktuelle Kurzstand steht in `CLAUDE.md`. Neue Details zu einem Vorhaben hier im passenden Abschnitt ergänzen.

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

## Geplantes Vorhaben: Aktionärsring (Planungs-App #65), Stand 31.10.2026

Auftrag Tobias 31.10.2026: Auf der Firmenseite soll man sehen, wer wie viel hält, aufgeteilt auf fast 100 %. Heute stehen
dort im Median ~36 % Großaktionäre, der Rest fehlt und wirkt unvollständig. **Darstellung: Ring** (Entscheidung Tobias),
Aussehen nach Entwurf von Tobias (nicht selbst gestalten). Grundsatz: Der Ring zeigt 100 %, aber nicht 100 % mit Namen;
der unbekannte Rest wird benannt, nie erfunden (Aktienregister nicht öffentlich, Meldepflicht erst ab 3 %).

**Test N-PORT (31.10.2026, Skripte `.recherche/nport_test.py`, `.recherche/nport_netto.py`, Treffer
`.recherche/2026q2_nport_treffer.csv`):** SEC-Datensatz „Form N-PORT Data Sets“
(`www.sec.gov/files/dera/data/form-n-port-data-sets/<JJJJ>q<N>_nport.zip`, ~440 MB gepackt je Quartal, alle US-Fonds mit
vollständigen Beständen, Stichtag bis ~3 Monate alt). Direkt aus dem Zip gelesen (25 s), Tabellen IDENTIFIERS (ISIN) →
FUND_REPORTED_HOLDING (Stück, nur `UNIT=NS`, `ASSET_CAT=EC`) → FUND_REPORTED_INFO/REGISTRANT/SUBMISSION; je Fonds
(`SERIES_ID`) nur der neueste Bericht; Prozent = Stück / Gesamtstimmrechte aus der letzten Stimmrechtsmitteilung.
Ergebnis (2026q2, Stichtage meist 31.03.2026):
- US-Fonds halten im Median **10,7 %** (DAX 14,1, MDAX 7,6; Spitze Brenntag 31 %, Lanxess 25 %).
- **Netto nach Abzug der Überschneidung** (Fondsfamilie steckt schon im Großaktionär, z. B. iShares in BlackRock, MFS bei
  Zalando): Median **+8,7 Prozentpunkte** mit Namen. Mit Namen zusammen dann Median 48 % statt 36 %.
  Beispiele (groß → zusammen): SAP 26 → 36 %, Zalando 22 → 33 %, Siemens 10 → 22 %, Allianz 8 → 17 %, Hugo Boss 70 → 78 %.
  32 von 81 Firmen bleiben unter 40 % mit Namen. Erwartung vorher (10–25 Pp.) war zu hoch, die Wirklichkeit liegt am unteren Rand.
- ADR/andere ISIN bringen wenig (SAP +0,4 %). Fehlende Treffer: Fresenius, Qiagen (andere ISIN, vgl. `EP_KENNUNG`);
  Firmen mit zwei Gattungen (VW, Henkel, Sartorius, BMW, Porsche) brauchen Gesamtzahl je Gattung, sonst falsche Prozente.
- Fondsfamilien-Zuordnung im Test grob über Stichwörter → im echten Bau saubere Tabelle Fondsgesellschaft → Konzern.

**Plan (Schritt für Schritt, je Schritt abbrechbar):**
- [x] 1. **Ring gebaut (31.10.2026, nicht gepusht).** Tobias: „einfach einen Ring, in unseren Farben“ (kein Entwurf nötig).
      `seiten.aktionaersring(aktionaere)` über der Großaktionärs-Tabelle: CSS-Ring (`conic-gradient`, kein Skript), nur Spalte
      Aktien (Instrumente sind keine Aktien), Halter ≥ 1 % einzeln (höchstens 7), kleinere als „Weitere gemeldete Halter“,
      Summe auf 100 % gedeckelt; Blau `--kauf` in abnehmender Stärke, Rest „Übrige Aktien“ (Streubesitz, Halter unter 3 %,
      eigene Aktien) in `--ring-rest` (Grau, im dunklen Modus kräftiger als `--gitter`). Mitte: „x % mit Namen bekannt“.
      Stile `.ring*` am Ende von `style.css`. 85 Firmenseiten mit Ring. Geprüft per Bildschirmfoto hell/dunkel, 950 und 520 px
      (SAP 26 %, Hugo Boss 70 %, Allianz 8 %). Sicherung vorher: `.recherche/sicherung_ring/`.
- [x] 2. **Eigene Aktien im Ring (31.10.2026, nicht gepusht).** Quelle: Mitteilungen nach § 40 Abs. 1 Satz 2 WpHG (Firma meldet
      ihren Bestand, wenn er 3, 5 oder 10 % berührt), die schon als `anderes` in `stimmrechte.csv` lagen. Rückkäufe taugen
      nicht (Einziehungen unbekannt). `stimmrechte.eigene_aktien_lesen` (Formular DE/EN: Abschnitt 3 Datum, „Neu“/„Resulting
      situation“ → Anteil und Gesamtzahl), `stimmrechte.eigene_aktien` (letzter Stand je Firma ab 2018, **nur ≥ 3 %**, weil
      darunter keine Meldepflicht mehr besteht). `stimmrechte_laden.eigene_aktien_nachladen()` läuft am Ende jedes Aufrufs
      (auch nachts) und liest nur fehlende → `daten/stimmrechte_eigene_aktien.csv` (wird von der Action über
      `daten/stimmrechte*.csv` mit committet). Erstlauf lokal: 123 Mitteilungen in 5 Min., keine Lesefehler.
      **11 Firmen mit ≥ 3 %:** SAP 5,0, Scout24 5,0, Salzgitter 4,9, United Internet 10,0 (2023), FMC, Mercedes, DHL, Ionos,
      Hochtief (2020), Lanxess (2019), Munich Re (2019) je ~3 %. Alte Stände können zwischen den Schwellen (3–5, 5–10 %)
      veraltet sein → Datum mit Link steht in der Legende. Segment „Eigene Aktien der Firma“ in `--sonstiges` (Mittelgrau),
      zählt zu „mit Namen bekannt“ (SAP 26 → 31 %). Keine Firma steht zugleich als eigener Großaktionär drin (geprüft).
      Geprüft per Bildschirmfoto hell/dunkel.
      **Nebenbefund (nicht behoben):** Halternamen mit Ort, z. B. „Salzgitter Aktiengesellschaft, Salzgitter,, Deutschland“ bei Aurubis.
- [x] 3. **US-Fonds im Ring (31.10.2026, nicht gepusht).** `pipeline/fonds_us.py`: `laden()` liest das neueste Quartal von
      der SEC-Seite, lädt nur, wenn es in `daten/fonds_us.csv` noch fehlt (Zip in temporären Ordner, danach gelöscht,
      ~1,5 Min.), behält nur unsere ISINs, je ISIN und Fondsträger eine Zeile (isin, gesellschaft, stueck, fonds, stichtag,
      quartal; 2026q3: 9.508 Zeilen, 94 Firmen, 650 KB; nur das neueste Quartal). `KONZERNE`: Fondsträger → Konzern
      (iShares → BlackRock, EUPAC/New Perspective … → Capital Group, Hartford → auch Wellington usw.) mit Muster für
      Großaktionärsnamen. `je_firma` rechnet in % der Gesamtstimmrechte (letzte Stimmrechtsmitteilung) und lässt Konzerne
      weg, die schon als Großaktionär gemeldet sind (geprüft: SAP ohne iShares, Zalando ohne MFS, Brenntag ohne Artisan,
      Harris, Hartford). Ring: bis 4 Konzerne einzeln „(US-Fonds)“, Rest „Weitere US-Fonds“, dunkleres Blau, Stand und
      Hinweis unter dem ersten Eintrag. **Nicht bei Firmen mit zwei Gattungen** (VW, Henkel, Sartorius, BMW, Fuchs …)
      und Porsche (`NUR_VORZUG`), weil die Stimmrechte nur Stammaktien zählen. Workflow „Stimmrechte laden“: nachts
      Schritt „US-Fonds laden“ (`continue-on-error`), committet `daten/fonds_us.csv` mit.
      **Ergebnis: Median „mit Namen bekannt“ 49 % (vorher 36 %), 73 Seiten mit US-Fonds.** SAP 26 → 41 % (mit eigenen
      Aktien), Allianz 8 → 18 %, Siemens 10 → 22 %, Hugo Boss 70 → 77 %, Brenntag 70 %. Bildschirmfoto hell/dunkel geprüft.
      Offen: Fresenius/Qiagen ohne Treffer (andere ISIN), Vorzugsaktien-Firmen ohne Fonds (bräuchten Gesamtzahl je
      Gattung), „Weitere US-Fonds“ oft 4–6 % (Zuordnungstabelle bei Bedarf erweitern).
- [x] 4. **Norwegischer Staatsfonds (31.10.2026, nicht gepusht).** `pipeline/norwegen.py`: NBIM-JSON-Schnittstelle der Seite
      nbim.no/en/investments/all-investments/ (`/api/investments/v2/init.json` → neueste Datei, z. B. `2026-06-30.json`;
      Felder n = Name, cc = Land, at = 0 Aktien, o = Eigentumsanteil %). Halbjährlich, lädt nur bei neuem Stand →
      `daten/norwegen.csv` (firma, name_nbim, anteil, stichtag). Zuordnung über bereinigten Namen + `NAMEN` (9 Abweichungen,
      z. B. DHL = „Deutsche Post AG“). 88 von 90 Firmen; Airbus fehlt bei NBIM absichtlich (ethischer Ausschluss), Deutz
      nicht gehalten. Segment „Norwegischer Staatsfonds“ in `--link`; entfällt, wenn Norwegen schon Großaktionär ist
      (Vonovia: Ministry of Finance 10,1 %) und bei Firmen mit zwei Gattungen (NBIM nennt nur einen Anteil je Firma).
      Workflow „Stimmrechte laden“: Schritt „Norwegischen Staatsfonds laden“ nachts, committet `daten/norwegen.csv`.
- [x] 5. **Vorzugsaktien und Firmen ohne EQS-Stimmrechte (31.10.2026, nicht gepusht).** `daten/aktiengattungen.csv`
      (firma, isin, gattung stamm/vorzug/einzig, stueck, eigene, stand, quelle; alle Zahlen mit Quelle, Fuchs nach HV 05/2026
      65,5 Mio. je Gattung). `export.ring_daten` (Hilfsfunktion in `exportiere`): Stammseite = Großaktionäre + US-Fonds der
      Stamm-ISIN / Stammaktien; Vorzugsseite = nur US-Fonds der Vorzugs-ISIN / Vorzugsaktien (+ eigene Aktien), Satz über dem
      Ring „Der Ring zeigt die Vorzugsaktien …“; `einzig` = eine Gattung, Gesamtzahl aus der Tabelle (Wacker, DWS haben keine
      EQS-Stimmrechte). Fresenius/TUI (alte + neue ISIN) zählen jetzt alle ISINs der Firma. Kein Ring, wenn nichts bekannt ist.
      `firmenseite(ring=…)` statt einzelner Argumente. **Geprüfte Großaktionäre ergänzt** (`grossaktionaere_geprueft.csv`):
      VW (Porsche SE 53,3, Niedersachsen 20,0, Katar 17,0; VW-Seite Aktionärsstruktur 31.12.2025), Sartorius (Testaments-
      vollstrecker 50,3, Bio-Rad 34,8, eigene Aktien 8,6 % der Stämme; H1-Factsheet, auf ausgegebene Aktien umgerechnet),
      Wacker (Familie 66,9 = 100 − Streubesitz 33,09 laut IR), DWS (Deutsche Bank 79,5), Airbus (SOGEPA 10,83, GZBV 10,82,
      SEPI 4,08; Zweitquelle uamr.de, Stand 31.12.2025), RTL (Bertelsmann 75,1; Quelle Wikipedia, Angaben schwanken 75,1–76,3).
      **Namen bereinigt:** `stimmrechte.anzeigename` kürzt „Name, Ort, Land“ nur, wenn der letzte Teil ein Land ist
      (Salzgitter-Fall); 11 Kandidaten geprüft, „Günter, Prof. Dr. Zimmer“ und „ACS, ACTIVIDADES …“ bleiben ganz.
      **Ergebnis:** 94 Seiten mit Ring, Median „mit Namen bekannt“ ohne Vorzugsseiten **50,5 %** (Start: 36 %); VW-Stämme 91 %,
      Sartorius 94 %, DWS 81 %, RTL 76 %, Wacker 73 %, Airbus 26 %. Vorzugsseiten 2–9 % (dort gibt es keine Meldepflicht).
      Bildschirmfotos hell/dunkel geprüft.
- [x] 6. **Darstellung überarbeitet (31.10.2026, Rückmeldung Tobias mit Bildschirmfoto Commerzbank):** Ring wirkte nach links
      verschoben, Blautöne nicht unterscheidbar, zwei Listen (Legende + Tabelle) mit widersprüchlichen Zahlen (BlackRock
      3,1 % Aktien im Ring, 4,38 % „Zusammen“ in der Tabelle). Lösung: `seiten.aktionaersstruktur` ersetzt `aktionaersring`
      + Großaktionärs-Tabelle: **eine Tabelle = Legende** (Farbfeld, Halter, Anteil, Stand) rechts neben dem Ring über die
      volle Breite (CSS-Grid 180 px | Rest, unter 640 px untereinander). **Nur Aktienanteil**, Spalten Instrumente/Zusammen
      entfallen; Instrumente klein beim Halter („zusätzlich x % über Instrumente, zählen nicht mit“). Kleine Halter in
      „Weitere gemeldete Halter“ mit Namen, Link und Instrumenten klein. US-Fonds als eine Zeile mit Aufteilung klein.
      Farben: feste kategoriale Palette `--serie-1…8` (dataviz-Richtlinie, gleiche Familie wie `--kauf`/`--verkauf`,
      hell/dunkel mit `validate_palette.js` geprüft: alle Pflichtprüfungen bestanden, Kontrastwarnung durch beschriftete
      Tabelle abgedeckt), 2-px-Lücken zwischen Segmenten. Halter ab 1 % einzeln, solange Farben frei sind (max. 8).
      Einheitlich eine Nachkommastelle. Überschrift „Aktionäre“, Erklärtext gekürzt. Vorzugsseiten: Hinweis „Anteile bezogen
      auf die Vorzugsaktien“, Stimmrechte der Stammaktien als ein Satz darunter. Bildschirmfotos CBK hell, SAP dunkel,
      VOW3 520 px geprüft. Dabei versehentlich gelöschte Logo-Stile in `style.css` sofort wiederhergestellt.
- **Offen / Pflege (Thema sonst abgeschlossen):**
      - BMW: aktuelle Zahl der Stamm-/Vorzugsaktien fehlt (letzte Stimmrechtsmitteilung 2020) → US-Fonds bei BMW aus.
      - Qiagen, RTL, Airbus: keine Gesamtzahl der Aktien → keine US-Fonds. Qiagen meldet Stimmrechte über **pressetext**
        statt EQS (auch für andere Auslandsfirmen prüfen: zweite Quelle für Stimmrechtsmitteilungen).
      - Bio-Rad hält ~28 % der Sartorius-Vorzüge (Factsheet), Vorzugsseiten kennen bisher keine Großaktionäre.
      - Jährlich prüfen: `aktiengattungen.csv` (Kapitalmaßnahmen, Einziehungen) und neue Einträge in `grossaktionaere_geprueft.csv`.
      - Airbus und RTL mit besseren Primärquellen belegen (Airbus-IR-Seite gab 404, RTL-Seite nicht abrufbar).
- USA-Aktien später: 13F + 13D/13G + Form 4 decken dort meist 70–90 % mit Namen ab.

## Laufendes Vorhaben: Personenseiten und US-Politiker (nach Vorbild Quiver Quantitative), Stand 06.11.2026

Auftrag Tobias 06.11.2026 (Bildschirmfoto Quiver, Seite Nancy Pelosi): Personenseiten bauen, erst nur Vorstand und
Aufsichtsrat; danach US-Politiker „so wie Quiver, im Prinzip alles“.
- [x] **1. Personenseiten (06.11.2026, nicht gepusht, Patch `.recherche/personenseiten.patch`):** `pipeline/personen.py`,
      Seiten `docs/person/<vorname-nachname>/` und Übersicht `docs/person/` (`seiten.personenseite`, `personen_uebersicht`),
      Einträge in `sitemap.xml`. Inhalt wie Quiver: Kacheln (Handelsvolumen, Käufe, Verkäufe, letztes Geschäft),
      Handelsvolumen je Jahr (Kauf/Verkauf als Säulenpaare, nur Euro, Stile `.jv-*`), Firmen/Mandate, Platz im Ranking,
      alle Geschäfte mit **„Seitdem ggü. Index“** (Aktie minus DAX/MDAX vom Schlusskurs am Geschäftstag bis heute).
      Personen = gleicher Name ohne Titel/Akzente, Reihenfolge der Wörter egal (`ranking.schluessel`, ersetzt
      `_schluessel`; behebt „Dr“ ohne Punkt, „Herr“, „Pring Giza, Helen“ = „Giza, Helen Pring“, López = Lopez). Alle 42
      Namen mit mehreren Firmen geprüft = echte Mehrfachmandate (Kaeser, Busch, Höttges, Bock …). **803 Personen.**
      Enthalten: eigene Geschäfte + Geschäfte **eigener Gesellschaften** („über X GmbH“; EQS nennt die Führungskraft, BaFin
      nicht → Zuordnung derselben Gesellschaft aus früheren EQS-Meldungen). Sonst fehlten Plattner, Dommermuth, Povlsen,
      Merckle. **Nicht enthalten:** Angehörige (natürliche Personen „in enger Beziehung“), sonstige Führungspersonen,
      börsennotierte Konzerne als „eng verbunden“ (United Internet AG, Continental). Links: Firmenseiten (Tabellen „Alle
      Meldungen“, „Timing“), Startseite (Ticker nur DAX/MDAX, Ranking über Feld `seite` in `neueste.json`/`ranking.json`),
      Fußzeile „Insider (Personen)“. Geprüft per Bildschirmfoto (Plattner hell, Kaeser dunkel, Dommermuth 420 px, Übersicht)
      und gerenderte Startseite (Ranking verlinkt 257 von 269, Rest sonstige Führungspersonen und Lothar Lanz, dessen
      Ranking-Käufe von einer Angehörigen stammen). 6,8 MB, ändert sich bei jedem täglichen Lauf (Spalte „Seitdem“).
      **Live erst nach Bot-Lauf „Daten aktualisieren“ mit „immer“.**
- [ ] **Datenschutz klären (vor Ausbau):** Dauerhafte Profile über natürliche Personen (DSGVO, berechtigtes Interesse);
      BaFin löscht nach 12 Monaten, wir zeigen dauerhaft. Danach entscheiden: Angehörige und sonstige Führungspersonen
      aufnehmen? Firmennamen mit Personennamen („Sabine Plattner GmbH & Co. Beteiligungs-KG“) stehen schon jetzt als „über …“.
      Datenschutzerklärung (`impressum.html`) um die Personenseiten ergänzen.
      **08.11.2026 vorbereitet (#75):** `RECHTSFRAGEN.md` Abschnitt 2: Abwägung, Empfehlung (keine Angehörigen), fertiger
      Absatz `#personen` für `impressum.html` (noch nicht eingebaut). **Eilt:** Personenseiten sind live (/person/ = 200).
      **09.11.2026 eingebaut (OK Tobias):** ersetzt den Absatz „Die Namen der meldepflichtigen Personen …“; Id `personen`
      gab es vorher nicht; Kontakt tobzwilling(at)gmx.de wie im Impressum. Sicherung `.recherche/sicherung_impressum/`.
      Geprüft per Bildschirmfoto (1300 und 520 px). Abgleich mit den Seiten: keine Angehörigen auf eigenen Seiten,
      „Seitdem ggü. Index“ auf allen, „Timing der Käufe“ auf 254 von 803. **Gemeldete Lücken (nicht selbst formuliert):**
      (1) Der Text nennt nur Vorstand/Aufsichtsrat, die Seiten zeigen auch Geschäfte eigener Gesellschaften („über Hasso
      Plattner Fund GmbH & Co. KG“, auch „über Sabine Plattner …“ mit dem Namen einer Angehörigen). (2) Verantwortlicher
      im Sinne der DSGVO nicht ausdrücklich so benannt (nur „Angaben gemäß § 5 DDG“). (3) Beschwerderecht ohne Art. 77 und
      ohne zuständige Behörde (BayLDA). (4) „Keine Anlageberatung“ nennt die Seite „privates, nichtkommerzielles Projekt“
      (passt nicht zur Pro-Stufe). (5) „Datenquellen“ nennt die US-Quellen (USAspending, FEC, LD-2, SEC) nicht.
      Art. 15–21 sind genannt.
- [ ] **Nebenbefund, nicht behoben:** 13 Geschäfte stehen doppelt (gleiche Meldung an zwei Tagen bei EQS veröffentlicht,
      z. B. Kaeser/Daimler Truck 18.01.2022), betrifft auch Firmenseiten und Event Study.
- [x] **2a. Repräsentantenhaus: Leser + Lader (06.11.2026, Freigabe Tobias „leg los“, nur lokal):** `pipeline/kongress.py`
      (Verzeichnis-Zip je Jahr, PTR-PDF mit `pypdf`, neu in `requirements.txt`; Kapitälchen kommen als `\x00` → entfernt;
      Zeilenleser: Inhaber, Wertpapier, Kürzel, Anlageart, Art, Geschäfts-/Meldetag, Betragsspanne, Status, Unterkonto,
      Beschreibung; Beschreibung läuft nur nach voller Zeile ≥ 100 Zeichen weiter; Namensreste hinter der Transaktionszeile).
      `python3 kongress_laden.py [--jahre 2026] [--max-minuten N]` → `daten/kongress.csv` (eine Zeile je Transaktion),
      `daten/kongress_fortschritt.csv` (doc_id, status ok/scan/leer); setzt fort, speichert alle 25 Meldungen, ~3 Meldungen/s.
      Geprüft 2026: 457 Meldungen, 401 elektronisch → 3.671 Transaktionen, alle mit Anlageart, jede Aktie mit Kürzel, kein
      Datum fehlt; Pelosi und Moskowitz (50 Transaktionen) von Hand gegen PDF geprüft. 56 Papier-Scans (DocID 8…/9…) ohne
      Text → `scan`, auf der Seite als Link (Texterkennung später).
      **Daten und Seiten nur lokal** (`.gitignore`: `daten/kongress*.csv`, `daten/abgeordnete.csv`, `docs/politiker/`),
      weil 5 U.S.C. app. § 105(c) die Nutzung „für kommerzielle Zwecke“ außer durch Nachrichtenmedien verbietet → vor dem
      Livegang klären (Quiver, Capitol Trades u. a. veröffentlichen trotzdem). Livegang = 4 Zeilen aus `.gitignore`, Action
      nach Muster `rueckkaeufe.yml`, Link auf der Startseite.
- [x] **2b. Politikerseiten (06.11.2026, nur lokal):** `pipeline/politiker.py`: Abgeordnete aus „congress-legislators“
      (gemeinfrei, `daten/abgeordnete.csv`, Amtszeiten ab 2011), Zuordnung Nachname im Bezirk → Nachname im Bundesstaat
      (alter Bezirk nach Neuzuschnitt, McCormick GA06) → einzige Person im Bezirk; 2026: alle Transaktionen zugeordnet,
      105 Personen, Namen geprüft. Seiten `docs/politiker/<name>/` + Übersicht (`seiten.politikerseite`,
      `politiker_uebersicht`, Aufruf `export.kongress_exportieren`, nur wenn `daten/kongress.csv` existiert): Kacheln,
      Volumen je Jahr (Mitte der Spannen), meistgehandelte Aktien, alle Geschäfte mit Link zur Originalmeldung und
      „Seitdem ggü. S&P 500“ (Yahoo, in Blöcken à 150 Symbole, zweiter Versuch; über 1.000 Symbole auf einmal → Yahoo
      liefert still nichts). Branchen-Kuchen und Fotos (amtliche Porträts sind gemeinfrei) noch nicht.
      **Historie geladen (06.11.2026, lokal, 60 Min.):** 7.978 Meldungen 2014–2026. Ab Mitte 2022 sauber: 1.989 Meldungen,
      20.885 Transaktionen, keine fehlende Anlageart/Status/Datum. **Älteres Formular (2014 bis Mitte 2022, 3.994
      Meldungen)** zerlegt die Marken („F ILINg S TATUS“), setzt Kästchen als „fedcb“ und schreibt Beschreibung und
      nächstes Wertpapier in eine Zeile → regelbasiert nicht trennbar, `kongress.ALTFORMAT` → status `alt`, nicht
      ausgewertet (stehen wie die 2.003 Scans als Links auf der Personenseite). Bereits geladene Altformat-Zeilen einmalig
      umgestuft (Regel: Meldung ohne jeden Status oder „leer“; 0 gemischte Meldungen). Korrekturen: „Amended“ ersetzt frühere
      Zeilen desselben Geschäfts, „Deleted“ löscht sie (`politiker.korrekturen`). „Gemeldet“ = Einreichungsdatum laut
      Verzeichnis, nicht das selbst eingetragene „Notification Date“ (Tippfehler wie 2204).
      **Kurse:** Yahoo sperrte diesen Rechner nach ~3 Abrufen mit je 1.300–1.900 Symbolen für etwa eine Stunde (auch AAPL
      einzeln „Too Many Requests“) → `politiker.kurse` mit Speicher `daten/kurse_us.parquet` (nur lokal, braucht pyarrow):
      fehlende Symbole in Blöcken à 50 mit 5 s Pause, danach je Lauf nur die letzten Tage; leerer Block = Sperre → Abbruch,
      nächster Lauf macht weiter. Die DAX/MDAX-Kurse der Action sind davon nicht betroffen (andere IP).
- [x] **2c/2d. Senat, älteres House-Formular und House-Scans aus fertigem Datensatz (07.11.2026, Tobias: „nimm das
      ältere Formular und die Scans aus dem Datensatz“, nur lokal).** `efdsearch.senate.gov` verlangt eine
      Klick-Erklärung (Nutzung nicht kommerziell), die Claude nicht abgeben darf → stattdessen **Hugging Face
      `austin-starks/congressional-stock-trades`** (Parquet je Jahr, ~9 MB, ~20 h aktuell; Code MIT, Daten „other“ mit
      Hinweis auf 5 U.S.C. § 13107(c), räumt keine Rechte ein): House + Senat 2012–2026, 10.883 Meldungen, 187.288
      Geschäfte; elektronische Senatsmeldungen aus HTML, Papier/Scans per Texterkennung + Seitenbild, nur veröffentlicht,
      wenn zwei Lesungen übereinstimmen; `memberId` = bioguide. **Abgleich mit unseren House-Daten ab Mitte 2022:** 1.976
      von 1.989 Meldungen gleich viele Geschäfte, Datum und Art 100 %, Kürzel 99,2 % (er lässt Vorzugsaktien wie `T$A`
      leer), Betrag 99,5 % (er genauer: Cent, „Over“); er verwirft Zeilen mit unmöglichem Datum (Cawthorn 20020894).
      Älteres Formular: 36.729 Geschäfte gegen 36.783 Datumspaare im eigenen PDF-Text, 99 % der Meldungen gleich.
      `python3 -m pipeline.kongress_datensatz` → `daten/kongress_datensatz.csv` (41 MB, .gitignore; Spalten wie
      `kongress.csv` + kammer, bioguide, url): **Senat 22.090 Geschäfte, 83 Personen; House 144.326 Geschäfte aus 6.358
      Meldungen** (älteres Formular 36.729, Scans 107.539, davon Ro Khanna ~43.000, McCaul ~34.000). Vom House nur
      Meldungen, die unser Leser nicht mit `ok` gelesen hat; ab Mitte 2022 bleibt die eigene Quelle.
      Anlageart: Scans/Papier haben keine → Aktie, wenn der Datensatz ein Börsenkürzel bestätigt (`resolutionStatus`
      printed/resolved). `export.kongress_exportieren` hängt den Datensatz an (`politiker.datensatz_zuordnen`: Name,
      Partei, Bezirk aus `abgeordnete.csv`), Seiten zeigen „Senat · AL“ bzw. „Repräsentantenhaus · CA17“, Link zur
      Originalmeldung. Kursspeicher begann 28.04.2015 → `ueberrendite_seit` gibt „–“, wenn am Geschäftstag kein Kurs da
      ist (vorher stiller Fehlwert). Geprüft per Bildschirmfoto (Tuberville). Manuell neu laden wie `kongress_laden.py`.
      **Ersetzt:** `kongress_altformat.py` (DeepSeek-Weg, gelöscht; `daten/kongress_alt_texte.csv` kann weg) und die
      Scan-Frage. **Abhängigkeit:** ein einzelner Betreiber; fällt er aus, bleibt der letzte Stand. Eigener Senatsleser nur
      mit Klick-Erklärung (Entscheidung Tobias).
- [ ] **3. Trump/Regierung (OGE 278-T), geprüft 06.11.2026:** PDFs frei bei `extapps2.oge.gov/201/Presiden.nsf/…` und
      whitehouse.gov (ohne Klick-Erklärung, aber gleiches Gesetz § 105(c)). Trumps Meldungen sind **Scans mit schlechter
      Texterkennung** („Tn.imp“ statt Trump), bis 113 Seiten und ~3.700 Geschäfte je Quartal (Presse) → nur mit besserer
      Texterkennung oder Sprachmodell lesbar. Entscheidung Tobias (Kosten).
      **Ausgelesen 07.11.2026 (Schlüssel von Tobias: z.AI, `ZAI_API_KEY` in `.env`, ~0,46 $):** `trump_laden.py --bilder`
      holt die Liste über die Domino-Schnittstelle (`President and Vice President Index?ReadViewEntries&ExpandView&
      OutputFormat=JSON`, 20 Meldungen 278-T 08/2025–09/2026, ohne Jahresberichte und Abschlussbericht 2021), lädt die PDFs
      nach `.recherche/trump/` und speichert jede Seite als JPEG (`seitenbilder.swift`, `.recherche/trump_bilder/`, 399 MB,
      nach dem Lauf löschbar; Liste `daten/trump_seiten.csv`). Danach liest das Bildmodell **GLM-4.6V-FlashX** (0,04/0,40 $
      je Mio. Token, 2 Anfragen gleichzeitig, bis 3 Versuche, Kostendeckel `BUDGET`) jede Seite → `daten/trump.csv`.
      **Texterkennung verworfen:** Apple Vision verlor ganze Spalten (Art nur in 60 %, Datum in 75 % der Zeilen), ein
      Textmodell (GLM-4.7-Flash) erfand dann Werte (Verkäufe vom 8.7.2026 als „purchase 11.08.2025“); `ocr.swift` gelöscht.
      Prüfung von Hand am Bild: Seite 31 (09.8.2026) 33/33 Zeilen richtig mit FlashX und mit dem kostenlosen
      GLM-4.6V-Flash (nur 1 Anfrage gleichzeitig, deshalb nicht genommen). **Ergebnis: 378/378 Seiten, 10.616 Geschäfte**
      (6.504 Käufe, 4.112 Verkäufe); Zeilennummern in 18 von 20 Meldungen lückenlos (2.26.2026 (1): Nr. 156/166 fehlen,
      2 doppelt; 1.14.2026: Nr. 108 fehlt; AMENDED: 4 doppelt). Betrag fehlt bei 11 %: Meldung 08.12.2026 und Seite 5 der
      AMENDED-Meldung sind rechts abgeschnitten gescannt (Spalte „Amount“ fehlt schon im PDF). 2 Daten nach dem Meldedatum
      aufs Meldejahr korrigiert. **Offen:** Meldung „08.12.2025 (2) AMENDED“ (145 Zeilen) klären, was sie in der
      Meldung 08.12.2025 (507 Zeilen) ersetzt; Seite für Trump bauen (Kürzel fehlen, nur Firmennamen wie
      „WORKDAY INC CLASS A“ → Zuordnung zu Kürzeln nötig, z. B. SEC company_tickers).
      **Seite gebaut 08.11.2026 (#72, nur lokal):** `pipeline/trump.py` macht aus `daten/trump.csv` Zeilen im Format der
      Kongress-Geschäfte (bioguide `trump`, kammer `reg` = „Regierung“), `export.kongress_exportieren` hängt sie an →
      `docs/politiker/donald-j-trump/` mit derselben Vorlage wie die Abgeordneten, Übersicht nennt „dazu Präsident Trump“.
      Kürzel über SEC `company_tickers.json` (Kopie `daten/sec_tickers.json`, .gitignore): beide Namen bereinigt
      (Rechtsform, Gattung, UNSOLICITED, Abkürzungen INTL/PPTYS/WHSL …), dann gleich, ohne Leerzeichen gleich
      (EXXON MOBIL), Wörter vertauscht (DISNEY WALT) oder abgeschnittener Brokername als eindeutiger Anfang
      („… TECHNOLOGI“). Anleihen (Zins/Fälligkeit) ohne Kürzel. **91 % der 8.631 Nicht-Anleihen mit Kürzel**,
      Stichprobe 70/70 richtig (nach Fix: Stammaktie vor Vorzugsaktie, AMH statt AMH-H). Ohne Kürzel v. a. ETFs/Geldmarktfonds
      und übernommene Firmen (EA, Qorvo nicht mehr in der SEC-Liste). Seite: 10.615 Geschäfte, ~2,0 Mrd. $ (Mitte der
      Spannen). **AMENDED geklärt:** „08.12.2025 (2) AMENDED“ deckt 02.–22.07.2025 ab, genau die Lücke zwischen (1) und (3),
      keine Zeile kommt in einer anderen Meldung vor → ersetzt nur ein nicht mehr gelistetes Original, nichts zu tun.
      **Offen:** Erklärtexte der Trump-Seite sprechen noch von Kongress/Inhaber.
- [x] **4a–c. US-Firmen (Freigabe Tobias 06.11.2026 „Universum über DAX/MDAX: ja“), gebaut 06.11.2026, nicht gepusht:**
      - `python3 -m pipeline.us_firmen` → `daten/us_firmen.csv`: S&P 500 (Wikipedia-Tabelle) + amtlicher Name aus
        SEC `company_tickers.json` (500 Firmen; GOOGL/GOOG je CIK einmal).
      - `python3 -m pipeline.staatsauftraege [--max-minuten N]` → `daten/staatsauftraege.csv` (kuerzel, geschaeftsjahr,
        betrag ab US-GJ 2016) + `staatsauftraege_zuordnung.csv`: USAspending-API ohne Schlüssel, Suche nach Namen,
        Kandidat auf Konzernebene (P, alle Töchter), Treffer nur bei gleichen Namenswörtern (+ Rechtsformen, wenige
        Zusätze) → „Apple“ ≠ „Apple Hospitality REIT“; Sonderfälle in `NAMEN` (Google Public Sector, 3M Company).
        Geprüft: Lockheed GJ 2025 72,9 Mrd. $, Boeing, RTX, HII, Microsoft gefunden; Apple hat keine nennenswerten.
        ~1,3 Firmen/Min. (USAspending langsam), setzt fort.
      - `python3 -m pipeline.spenden` → `daten/spenden.csv` (+ `spenden_kandidaten.csv`, `spenden_pacs.csv`, zusammen
        1,4 MB): FEC-Massendateien je Zyklus 2022/24/26 ohne Schlüssel (cm, cn, pas2), Firmen-PACs (Typ Q/N, Org. C) über
        „Connected Organization“, Spenden Art 24K an Kandidaten, Kandidat → bioguide über `fec` in `abgeordnete.csv`.
        ~210 Firmen mit PAC, 64–75 Mio. $ je Zyklus; größte 2023/24 Home Depot, AT&T, Comcast, Honeywell, UPS, Boeing,
        Lockheed. Namen: offiziell (congress-legislators) bzw. `spenden.fec_name` („WITTMAN, ROBERT J. MR.“ → „Robert J. Wittman“).
      - Seiten `docs/us/<KÜRZEL>/` + `docs/us/` (`seiten.us_firmenseite`, `us_uebersicht`, `export.us_exportieren`):
        Kacheln, Staatsaufträge je GJ (Balken), PAC-Spenden nach Partei je Zyklus + größte Empfänger; **lokal zusätzlich**
        „Geschäfte von Abgeordneten“ in dieser Aktie (NVDA: 274 seit Mitte 2022) und Spenden-Abschnitt auf den
        Politikerseiten. Die US-Seiten nutzen nur gemeinfreie Daten → **gehen mit dem nächsten Push live** (Fußzeile
        „US-Firmen: Staat und Politik“, Sitemap), Kongress-Teil fehlt dort, weil `daten/kongress.csv` lokal bleibt.
      - Manuell (vierteljährlich): `us_firmen`, `staatsauftraege` (Zuordnung löschen für Neuprüfung), `spenden`.
- [ ] **4d. Lobbying:** `lda.gov/api/v1/` (und das alte `lda.senate.gov`) antworten 06.11.2026 mit 403 von Akamai, auch die
      Doku, auch von außen. **07.11.2026:** Tobias erreicht lda.gov auch im Browser nicht (auch privat) → kein
      Schlüsselproblem, Akamai sperrt Abrufe von außerhalb (lda.gov, lda.senate.gov, auch `/system/public/` = 403).
      Erreichbar ist die Lobbying-Suche des Repräsentantenhauses `disclosurespreview.house.gov` (dieselben LD-1/LD-2-
      Meldungen, Datenschnittstelle hinter der Suchseite noch nicht untersucht) → nächster Weg, ohne Schlüssel.
      **08.11.2026 (#73):** Die Suchseite hat keine Abfrage-Schnittstelle mehr (Hinweis: seit 31.07.2026 nur noch
      ZIP-Downloads), aber alle LD-2-Berichte als XML: Liste `disclosurespreview.house.gov/data/LD/LdSearchPastFilings.json`,
      Dateien `data/LD/<Jahr>_<n>Quarter_XML.zip` (~50 MB, ~26.000 Berichte je Quartal, täglich aktualisiert).
      `python3 -m pipeline.lobbying [--max-minuten N]` lädt ab 2018 nur neue/geänderte Quartale →
      `daten/lobbying_berichte.csv` + `lobbying_fortschritt.csv` (beide .gitignore, groß) und `daten/lobbying.csv`
      (kuerzel, jahr, betrag, berichte; wird committet, öffentliche Daten). Zählweise wie OpenSecrets: eigene Ausgaben
      (`expenses`, wenn Auftraggeber = Meldender) + Honorare beauftragter Firmen (`income`); Korrektur (Q2A) ersetzt das
      Original (je senateID und Quartal das neueste Unterschriftsdatum). Firma ↔ Auftraggeber mit derselben Namensregel wie
      Spenden. Abschnitt „Lobbying“ auf `docs/us/<KÜRZEL>/` (Balken je Jahr) statt des Platzhalters.
      **Ergebnis:** 36 Quartale 2018–2026, 768.476 Berichte (Erstlauf ~40 Min., 114 MB), **414 von 500 Firmen**.
      Namen der Auftraggeber werden vorher gekürzt (`lobbying.kunde`: Klammern, „fka/formerly“, „and its
      subsidiaries/affiliates“ weg, bei „obo X“ zählt X), sonst fehlte Meta fast ganz (2,4 statt ~30 Mio. $);
      Zusatznamen in `NAMEN` (Alphabet = Google/Google Client Services, Meta = Facebook, RTX = Raytheon/United
      Technologies). Geprüft 2025: Meta 29,7, GM 24,0, Amazon 20,9, Lockheed 17,5, Google 16,8, AT&T 14,2,
      Microsoft 12,8 Mio. $ (Größenordnung wie OpenSecrets, eher etwas höher). Bildschirmfoto META geprüft.
      Manuell (vierteljährlich, wie Spenden): `python3 -m pipeline.lobbying`, `daten/lobbying.csv` committen.
      **Live seit 09.11.2026** (Commit 099af96, Bot baute danach neu; /us/META/ zeigt Lobbying). Test im sauberen
      Arbeitsbaum ohne nur lokale Dateien: 500 Seiten, alle mit Abschnitt Lobbying (86 ohne Berichte mit Erklärtext),
      keine Politikerseiten, keine Kongress-/Trump-Zeilen. Push-Schutz deckt `trump`/`lobbying` automatisch ab.
- [ ] **2. US-Politiker (Plan, Freigabe Tobias 06.11.2026):** eigene Daten aus den Primärquellen statt Quiver-API.
      Quiver-API: Hobbyist ~30 $/Monat und Trader ~75 $/Monat nur **privat** (keine kommerzielle Nutzung), kommerziell erst
      „Startup“ ~250 $/Monat bzw. Enterprise auf Anfrage (laut api.quiverquant.com 06.11.2026; Weitergabe/Anzeige
      nicht geregelt → schriftlich klären). Primärquellen (gemeinfrei, STOCK Act):
      Repräsentantenhaus `disclosures-clerk.house.gov/public_disc/financial-pdfs/<Jahr>FD.zip` (Verzeichnis, täglich
      neu; 2026: 457 Transaktionsmeldungen, Typ P) + PDF je Meldung `public_disc/ptr-pdfs/<Jahr>/<DocID>.pdf`
      (elektronisch eingereichte haben Text, getestet Pelosi 20035143; handschriftliche Scans brauchen Texterkennung);
      Senat `efdsearch.senate.gov` (Akamai-Botsperre, Nutzungsbedingung per Klick, schwerer). Beträge nur als Spannen
      (1.001–15.000 $ …). Reihenfolge: 1) Kongress-Geschäfte (House, dann Senat), 2) Politikerseiten wie Pelosi,
      3) Trump/Regierung (OGE Form 278-T), 4) Lobbying (Senate LDA, offizielle API), Staatsaufträge (USAspending, offizielle
      API), Spenden (FEC, offizielle API). Vermögen schätzen (Jahresmeldung, Spannen) und Patente erst später.

## Laufendes Vorhaben: Firmenlogos, Stand 31.10.2026

Auftrag Tobias 31.10.2026: Logo für jede Firma. Plan (Tobias: „ja bitte“): einmal laden, lokal in `docs/logos/` speichern
(keine fremden Dienste beim Seitenaufruf), von Hand durchsehen, erst danach auf der Website einbauen.
- [x] 1. **Skript (31.10.2026, nicht gepusht):** `python3 logos_laden.py` (`--neu` lädt alles neu) → `docs/logos/<ISIN>.svg|png|jpg`
      (1,4 MB), Liste `daten/logos.csv` (isin, name, datei, quelle, url), Übersicht `logos_uebersicht.html` (im
      Projektordner, nicht in `docs/`, in `.gitignore`). Quelle Wikidata (ISIN P946 → Logo P154, Datei von Commons);
      `daten/logos_hand.csv` (isin,url) hat Vorrang. Per ISIN 88 von 97; die übrigen per Namenssuche bei Wikidata
      gefunden und in die Handliste eingetragen (Fresenius 2. ISIN, Qiagen, Aroundtown, Fuchs ×2, Jenoptik, Renk, Schaeffler).
      **Ergebnis 97 von 97.** Hochtief fehlte bei Wikidata und Commons → SVG von hochtief.com in die Handliste. Keine SVG enthält `<script>`.
- [ ] 2. **Tobias:** Übersicht durchsehen. Verdacht auf veraltete Logos (Claude, nicht geprüft): Nordex (mit „acciona“),
      TUI (mit „Aktiengesellschaft“), Jenoptik (blaues Kästchen), Hella (Forvia-Doppellogo), Porsche AG (Wappen statt Schriftzug),
      Fuchs (kleines PNG mit Werbespruch).
- [x] 2a. Tobias 31.10.2026: „Passt, alles einbauen“ (Verdachtsfälle bleiben vorerst).
- [x] 3. **Eingebaut (31.10.2026, nicht gepusht):** `seiten.logo_datei`/`firmenlogo` (Logo neben dem Namen im Kopf der
      Firmenseite, weiße Kachel auch im dunklen Modus, ohne Logo Anfangsbuchstabe), Feld `logo` in `firmen.json`
      (`export.py`), kleines Logo in der Firmenliste der Startseite (`start.js`), Stile `.firmenlogo`/`.titelzeile` am Ende
      von `style.css`. Lokal geprüft per Bildschirmfoto (SAP hell, Hochtief dunkel 420 px, Firmenliste): 94 von 94 Seiten mit Logo.
      Die Firmenseiten baut der Bot beim nächsten Lauf neu.
      **Nachtrag 31.10.2026 (Tobias):** Logo groß rechts im Kopf der Firmenseite (`.firmenkopf`, `.firmenlogo.gross` 220×96,
      unter 600 px 112×52) statt klein vor dem Namen. Live fehlten die Logos nach dem Push, weil der Bot ohne neue BaFin-Meldung
      nicht neu rechnet (und `--immer` nur werktags) → nach Änderungen an `seiten.py` Action „Daten aktualisieren“ mit „immer“ starten. Noch nicht in Ticker, Cluster und Ranking (nur Firmenname).
      **Nachtrag 06.11.2026:** Die CSS-Regeln aus dem Nachtrag waren nie in `style.css` angekommen (Commit e059200 enthielt nur
      die Aktionärsring-Stile), deshalb stand das Logo klein links. Jetzt ergänzt: `header.firmenkopf` (Flex, Logo rechts),
      `.firmenlogo.gross` 240×104, unter 600 px 120×56. Lokal geprüft (Rheinmetall 1300 px, SAP 520 px). Gepusht 06.11.2026 (ead6284).
- **Tooltip Kursdiagramm (06.11.2026, Tobias):** Bei 5 Jahren lag weniger als 1 px pro Handelstag, Insider-Punkte waren
  kaum zu treffen. `liniendiagramm` in `gemeinsam.js`: Marker im Umkreis von 16 px rasten ein (sonst wie bisher nächster Tag).
  Test RHM 5 Jahre, Maus 8 px neben jedem Punkt: vorher 2/64, nachher 64/64 Tooltips mit Geschäft. Gepusht 06.11.2026.
- **Kapitelleiste Firmenseite (06.11.2026, Tobias: „bau es so im heutigen Stil“):** `seiten.mit_kapiteln` gibt jeder
  `<section class="karte"><h2>` eine `id` und baut daraus `<nav class="kapitel">` (fehlende Kapitel fallen von selbst weg).
  Ab 1240 px Leiste links (180 px, mitlaufend, `.kapitel-raster` als Raster um Kopf/Leiste/Inhalt/Fuß), darunter waagerechte
  Zeile oben (mitlaufend, wischbar). `firma.js` markiert das aktuelle Kapitel. Geprüft an RHM (hell/dunkel 1400 px, 520 px,
  Sprünge per Messwert). Aussehen nur vorläufig, kommt mit der Neugestaltung neu. Gepusht 06.11.2026; live erst nach Bot-Lauf „immer“.
- **Kapitelleiste auch auf der Startseite (07.11.2026, Tobias):** `docs/index.html` von Hand ergänzt (`.kapitel-raster`,
  `nav.kapitel`, `id` je Karte; „Sonntags-Report“ behält `#newsletter`). Markier-Skript von `firma.js` nach `gemeinsam.js`
  verschoben (läuft nur, wenn eine Leiste da ist). Geprüft 1400/520 px, Sprünge zu Timing/Firmen/Report, RHM weiter ok.
  Sicherung: `.recherche/sicherung_kapitel_start/`. Neue Karte auf der Startseite → Link in der Leiste von Hand ergänzen.
  **Fehler und Reparatur 07.11.2026:** Die Sprungmarken `#cluster` und `#firmen` gab es schon als Ids der Listen,
  `start.js` füllte deshalb die ganze Karte (Firmenliste und Cluster zerschossen, live). Umbenannt in `#cluster-kaeufe`
  und `#firmenliste`; keine doppelten Ids mehr auf Start- und Firmenseiten. Lehre: vor neuen Ids nach vorhandenen suchen.
- **Kursreaktion je Ereignis (06.11.2026, Tobias):** Tabelle jetzt neueste zuerst (`sort_values(..., ascending=False)`). Gepusht 06.11.2026.
- **Erklärtexte volle Breite (06.11.2026, Tobias):** `max-width: 760px` bei `.karte .erklaerung` entfernt, gilt für alle Karten. Geprüft RHM „Aktionäre“ 1400 px. Gepusht 06.11.2026.
- Rechtlich: Logos nur zur Kennzeichnung der Firma zeigen, kein Anschein einer Partnerschaft → zu „vor dem Livegang klären“.

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
      - **Name: Rhodus (festgelegt von Tobias, 31.10.2026).** Herkunft: Äsop „Hic Rhodus, hic salta!“ („Hier ist Rhodos,
        hier spring!“ = zeig es hier, statt nur zu erzählen); zitiert von Hegel (Vorrede Rechtsphilosophie) und Marx.
        Lesart: Rhodus ist der Ort, an dem geprüft wird, was stimmt – Insiderkäufe UND Schwarmstimmung. Die Masse ist
        nicht der Gegner (Sentiment/Schwarmintelligenz ist Kernpunkt, Korrektur Tobias).
        - **Untertitel offen.** „Taten statt Worte“ / „Facta, non verba“ verworfen (wertet Sentiment ab).
        - Domains frei (31.10.): rhodus.io, rhodus.ai, hicrhodus.io. Tobias kauft vorerst kein .com/.de; Umbenennung
          später möglich. Websuche: keine Finanzfirma „Rhodus“ (nächste: Rho, Rhodon). **TMview: frei** (geprüft von Tobias
          mit Claude im Browser, 31.10.2026).
          Markenprüfung 31.10.2026 (indirekt, TMview blockt Skripte): in USPTO (Justia), Web und Firmensuche kein
          „RHODUS“; ähnlich nur RHODOS (USA, Rosen, gelöscht), Rhodium/Rhodes in fremden Branchen. Offiziell noch nicht
          geprüft → Tobias hat danach selbst in TMview gesucht: frei.
        - Verworfen in der Namensrunde: deutsche Namen (Profispur, Aktienspur … nicht global), englische Kunstnamen
          (Noctmoor, Ardeamont: albern), Glaux, Pythia, Delphi (Delphi Digital = Research für Anleger, „OK Delphi“
          ändert nichts), Babylon (Babylon Health pleite), Geminus (zu nah an Gemini). Echte lat./griech. Einzelwörter
          (Facta, Signa, Proba …) sind auf .com/.io/.ai alle vergeben. Reserve: Examen (lat. Bienenschwarm + Prüfung).
- [ ] 2. Newsletter starten: schlichtes EmailOctopus-Formular, verlinkt von der jetzigen Seite; Skript, das samstags
      einen Entwurf des Sonntags-Reports aus den eigenen Daten vorbereitet.
      **Skript fertig (31.10.2026, gepusht):** `python3 sonntags_report.py [JJJJ-MM-TT]` → `newsletter/<Datum>.md`
      (Stichtag = Sonntag, betrachtet die 7 Tage davor nach Mitteilungsdatum): 5 größte Käufe, neue Cluster, Käufer mit
      guter Bilanz (aus `ranking.json`, nur Ø und Median > 0), 3 größte Verkäufe. Liest nur `docs/data`, also vorher
      `git pull`. Getestet an den Wochen bis 04.10. und 01.11.2026. Nur Deutsch (Englisch fehlt noch). 
      **Anmeldung (31.10.2026, gepusht ca2db4c, live geprüft): Kit statt EmailOctopus.** EmailOctopus hat nach einem Update keine Listen
      mehr, nur Tags, und im Gratistarif nur 1 Formular (das hat Roleplay) → bleibt nur für `roleplay-landing`. Kit
      (kit.com, Gratistarif laut Drittquellen 10.000 Abonnenten, Formulare unbegrenzt), Formular-ID `10125562`.
      Karte „Sonntags-Report“ auf der Startseite an vorletzter Stelle (vor „Firmen im DAX und MDAX“, Tobias 31.10.2026) (`docs/index.html`, eigenes HTML-Formular, sendet per
      `fetch` an `app.kit.com/forms/10125562/subscriptions`, Feld `email_address`; Kits Skript wird nicht geladen),
      Stile `.report-formular` in `style.css`, Datenschutzabsatz `#newsletter` in `impressum.html`. Geprüft: Kit erlaubt
      Anfragen von fremden Seiten (CORS `*`), ungültige Adresse im Browser abgelehnt; echte Anmeldung noch nicht getestet.
      Bestätigungsmail („Incentive email“) laut Tobias eingeschaltet und deutsch. **Offen:** echte Anmeldung auf der Live-Seite testen;
      Grundlage USA-Übermittlung (Text nennt Standardvertragsklauseln; DPF-Zertifizierung nur über Drittseite gesehen) auf
      kit.com/privacy prüfen. **Versand automatisch seit 06.11.2026** (Tobias): samstags ab 18 Uhr in Kit geplant für Sonntag 8 Uhr, Telegram-Hinweis zum Prüfen/Stoppen (Details Verlauf 06.11.2026).
- [ ] 3. Mit 5–10 Anlegern sprechen. Leitfaden, Anschreiben, Auswertungstabelle: `newsletter/GESPRAECHE.md` (31.10.2026).
      Die Gespräche prüfen jetzt Zielgruppe und Preisidee aus der Positionierung (31.10.2026).
- [ ] 4. Weiter am Produkt (Datenbank, Sentiment); Website danach.

**Marke und Design (Stand 31.10.2026, Werkzeug: Claude Design statt Google Stitch):**
- **Design System „Rhodus“** (Grundlage für alles Gestaltete): https://claude.ai/artifact/X1njLe2gDXmPDRtszcsTRN
  Fest: Name Rhodus, Logo aus `logo/kit/` (unverändert), Farben Rhodus-Grün #1E3B2F + Creme #F3EEE2 **auch für die Website**,
  Cinzel nur fürs Logo, **Geist** für Text und Zahlen (Tobias), Ton (du, keine erfundenen Zahlen, Sonntags-Report = CTA).
  Offen: Untertitel, Oberfläche (Bausteine, Abstände, Datenfarben, dunkler Modus). Die heutige Seite gilt als „zu sehr
  Research-Seite“ (Tobias) → ihr Aussehen nicht übernehmen.
- **Startseite, drei Richtungen** auf einer Design-Leinwand: https://claude.ai/artifact/416CVL22JqidLmcVQwTuWf
  (1 Privatbank, 2 Fintech, 3 Daten vorn). **Wartet auf Tobias' Wahl.** Danach: gewählte Gestaltung als Bausteine ins
  Design System, echte Website erst später.
- Beides ist privat; anderen Sitzungen über das Artifact-Werkzeug lesbar (`read` mit der Adresse).
- **Vorlagen von Tobias (08.11.2026):** Fortix, Mosa AI, Patensify, Apollo, Bits, folk. Bilder und Beschreibung in
  `.recherche/design_referenzen/` (`REFERENZEN.md`). Mosa AI nicht gesehen (Land-book sperrt per Cloudflare, Original
  nicht gefunden); bei den Land-book-Einträgen den heutigen Stand der Originalseiten fotografiert.
- **Startseite, drei neue Richtungen nach diesen Vorlagen** (08.11.2026, privat): https://claude.ai/artifact/QuKEGndLbFhxJ68DNuHuDe
  A Klarheit (Fortix + Patensify: zweifarbige Riesenüberschrift, Kartenfächer, Zahl 6.151 aus Punkten), B Werkzeug
  (Apollo + folk: Seite im Rahmen, große Produktansicht Firmenseite, Quellen-Raster, Abschnitts-Etiketten), C Ruhe (Bits:
  warmer Grund, Zeitleisten-Karte Knorr-Bremse, „Hic Rhodus“-Band in Cinzel, Kartenraster, klickbare Quizfrage aus der
  Event Study). Neu gegenüber dem Design System: Gold `#c9a961` als Akzent (nur Vorschlag). Sentiment als Platzhalter
  „In Arbeit“. **Wartet auf Tobias' Wahl** (auch gegenüber den ersten drei Richtungen).

## Nächste Schritte (Stand 31.10.2026, nach Rauszoomen mit Tobias)

Ziel bleibt: Startup, Finanzdaten-Plattform „GuruFocus für Europa, günstiger“ + „Folge den Profis“ + Sentiment.
Fundamentaldaten sind dafür Pflicht, aber nicht das Alleinstellungsmerkmal.
**Korrektur Tobias 06.11.2026:** Insider, Großaktionäre, Rückkäufe, Guru-Depots und alles Bisherige sind KEIN
Alleinstellungsmerkmal (haben etablierte Anbieter auch). Das Alleinstellungsmerkmal soll eine **Sentimentanalyse von
Reddit und Twitter/X für Krypto und Pennystocks** werden, die es bei etablierten Anbietern bisher nicht gibt.
Reihenfolge laut Empfehlung Claude:
1. ✅ **Eulerpool eingebaut (31.10.2026, Details unter Fundamentaldaten, Block „Eulerpool“).** Ursprünglicher Auftrag: Leser in `pipeline/fundamental.py`
   (GuV, Bilanz, Cashflow, Schätzungen; Ist-Jahre von Schätzjahren trennen; Werte in Mio. → ×1e6; verschlüsselte
   Antworten überspringen, nie entschlüsseln), in `kennzahlen.PRIORITAET` vor onvista/TradingView für EBIT und
   Schätzungen; dann alle Firmen automatisch gegen `/api/1/aaqs/by-isin` abgleichen (nur Prüfung, nicht anzeigen) und
   Formeln nachschärfen (ROCE, Verschuldung). Danach Fundamentaldaten als fertig betrachten, **nicht weiter ausbauen**.
2. **Kleine Fehler auf der Live-Seite zuerst beheben:** Rückkäufe „keine Daten“ ✅ (31.10., gepusht);
   Taktung: cron-job.org einrichten (Tobias, Abschnitt Offen).
3. **Positionierung: erledigt 31.10.2026** (siehe Marketing Schritt 1). Name: **Rhodus** (31.10.2026, TMview frei), Untertitel offen.
4. **Newsletter „Sonntags-Report“ + 5–10 Gespräche mit Anlegern** (Marketing Schritt 2–3): erste echte Rückmeldung.
5. **Architektur entschieden (31.10.2026, `ARCHITEKTUR.md` unten):** Supabase (Postgres, kostenlos), Sammler bleiben
   in GitHub Actions, kein Hetzner bis MVP, 0 € bis MVP. Umsetzung (Block 1–2) nach der Positionierung (erledigt) und
   bevor das Universum über DAX/MDAX hinaus wächst, **kann also jetzt starten**; braucht ein Supabase-Konto von Tobias.
   Website-Technik ist noch festzulegen.
6. **Vor dem Livegang:** Rechtslage der Quellen; legaler Weg mit Anzeigerecht wäre Eulerpool Builder (99 $/Monat).

## Einstieg für einen neuen Chat (Stand 28.10.2026)

**Was das ist:** Tobias baut aus dem Insider-Monitor
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
- [x] **Eulerpool (31.10.2026, nur lokal):** `fundamental.eulerpool` holt je Firma GuV, Bilanz, Cashflow (Präfix
      `guv.`/`bilanz.`/`cf.`, Millionen ×1e6, Gewinn je Aktie nicht), Schätzungen (`schaetzung.*`, Periode „JJJJe“, schon
      in ganzen Einheiten) und AAQS (Quelle `aaqs`, nur Prüfung, nie anzeigen). Schlüssel `EULERPOOL_API_KEY` aus `.env`,
      ohne Schlüssel übersprungen. Verschlüsselte Antworten (SAP-Schätzungen) werden übersprungen. `EP_KENNUNG`: Fresenius,
      Henkel, Fuchs, Sartorius kennt Eulerpool nur unter der anderen ISIN. Lauf jetzt **~6 Min.**, `fundamental.csv` 21 MB,
      ~530 Abrufe (Kontingent 100.000/Monat).
      `kennzahlen`: Eulerpool zuerst für EBIT (`PRIORITAET`), Schätzungen nächstes Jahr (`EP_SCHAETZUNG`), Gewinn je Aktie
      in 3 Jahren; Balken zeigen bis zu 3 Schätzjahre. **Währungsschutz** `ep_passt`: Eulerpool rechnet in Berichtswährung,
      TradingView in Handelswährung → Eulerpool nur, wenn der Umsatz im letzten Geschäftsjahr auf 10 % gleich ist. Greift
      nicht bei Qiagen, RTL, NVIDIA (Währung/Geschäftsjahr) und Deutsche Börse, Hannover Rück, Commerzbank (Umsatzbegriff);
      die fallen auf die alten Quellen zurück. Ergebnis: 99 von 105 Firmen mit Eulerpool, **echtes EBIT über 10 Jahre bei
      91 statt 7 Firmen.** Eulerpools Ist-Gewinn je Aktie = onvista bereinigt bei 87 % (±5 %).
      **Formeln nachgeschärft** (Abgleich aller Firmen gegen AAQS, `.recherche/eulerpool_abgleich.py`): ROCE und
      Verschuldung jetzt mit EBIT des Geschäftsjahrs statt der letzten 12 Monate (zur Bilanz am selben Jahresende),
      Nettoschulden = Schulden − Bargeld ohne kurzfristige Anlagen (TradingView `cash_n_equivalents_fy`). Gleich mit AAQS
      (±1 Pp. bzw. ±0,1×): ROCE 36 → 96 %, Verschuldung 15 → 50 % (Rest: Leasing/Finanzsparten, Mercedes, VW, Siemens
      Energy), EBIT-Wachstum 10 J. 96 %, EK-Rendite 96 %, Umsatzwachstum 89 %, größter EBIT-Rückgang 87 % (gleiche Formel;
      Rest junge Firmen). Renditeerwartung nur 11 % gleich: eigene Formel mit Deckel, bewusst nicht angeglichen.
      **Zykliker-Regel verschärft (Tobias 31.10.2026):** jetzt **zweimal ≥ 40 %** Einbruch in 10 Jahren (vorher 2× ≥ 25 %)
      → 15 Zykliker (u. a. Deutz, Krones, Lufthansa, Mercedes, Airbus, MTU, Nordex, Kion, Siemens Energy); DHL, Zalando,
      Fresenius, Infineon nicht mehr. VW, BMW, Traton jetzt Substanzwert (KBV < 0,8). Verworfen: 3× ≥ 25 % (nur 9, ohne
      Deutz/Traton). Text in `seiten.KATEGORIE_TEXT` angepasst.
      Vorher (2× ≥ 25 %): Mit echtem EBIT statt EBITDA (schwankt stärker) gab es **29 statt 13 Zykliker**
      (neu u. a. VW, Mercedes, Lufthansa, Infineon, Kion, aber auch DHL, Zalando, FMC, Fresenius); Substanzwerte 6 → 1, weil
      Zykliker Vorrang hat. Qualitätscheck bei 37 Firmen geändert. 10/10: Atoss, Nemetschek, Alphabet, Microsoft (SAP jetzt
      nicht mehr). Geprüft per Bildschirmfoto (Deutz: 10 J. EBIT, Schätzsäulen 26e–28e), `docs/` zurückgesetzt.
      Sicherung des Stands davor: `.recherche/sicherung_eulerpool/`. **Fundamentaldaten damit fertig, nicht weiter ausbauen.**
- [ ] Danach offen: Handyansicht auf echtem Gerät; SEC um IFRS erweitern (Freigabe Tobias); Universum über DAX/MDAX hinaus (Freigabe Tobias);
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
- [ ] **Nächster Schritt: Krypto-Wale (Tobias 08.11.2026, Planungs-App #78).** Test eine Woche: große Überweisungen
      auf Solana/Ethereum über Gratis-Schnittstellen (Etherscan, Solana-RPC, mempool.space), Börsenadressen erkennen
      (Zufluss zur Börse = möglicher Verkauf), bei neuen Memecoins Entwickler-/Sniper-/gebündelte Käufe vor dem Start
      (Vorbild Bubblemaps). Ziel: „Wal/Entwickler kauft vor dem Reddit/X-Hype“ als Teil des Alleinstellungsmerkmals.
      Recherche `DATENQUELLEN.md` Abschnitt 10; Optionsfluss à la Bullflow verworfen (anonym, Lizenz, kein USP).
**Tobias 28.10.2026: Alles Recherchierte wird übernommen**, auch Cookies und Umgehung von Bot-Sperren (noch nicht live,
kein Geld). Rechtslage erst vor dem Start klären (Status-Spalte in `DATENQUELLEN.md`). Noch nichts gebaut, erst Recherche.


# Anhang: Entscheidungen, Datenquellen und Offen in voller Länge (Stand 08.11.2026)

### Entscheidungen (mit Grund)

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

### Datenquellen und bekannte Lücken

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

### Offen

- [x] **Taktung reicht nicht** (**gelöst, geprüft 06.11.2026:** cron-job.org-Läufe 02.–05.11. je 46–48/Tag, alle erfolgreich; 31.10.2026 erneut gezählt: 24.–30.10. je 5–7 geplante Läufe statt 48, Lücken bis 6,5 h,
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
- [ ] Überzähligen zweiten Telegram-Bot löschen (`/deletebot`). **Achtung (08.11.2026):** @Insiderhandeltest2bot sendet jetzt die Hype-Warnungen der Sentiment-Probe → nicht löschen; vorher klären, welchen Bot die GitHub-Action nutzt.
- [ ] Tooltips im echten Browser prüfen (im Headless-Test nicht simulierbar).
- [ ] Vierteljährlich nach Indexänderungen (März, Juni, Sept., Dez.): `python3 -m pipeline.firmen`, prüfen;
      Korrekturen in `ISIN_ERSATZ`/`TICKER_KORREKTUR`. Danach `historie.py` für neue Firmen (Fortschrittsliste kennt sie nicht).
- [ ] Beobachten: GitHub deaktiviert geplante Läufe nach 60 Tagen ohne Aktivität (Bot-Commits zählen vermutlich).
- [ ] Fremdwährungs-Volumen (GBp/USD) in Euro umrechnen, falls Cluster/Volumen-Anzeigen das brauchen.

