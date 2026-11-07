# US-Kongress und US-Politiker: was noch offen ist

Stand 07.11.2026. Gebaut (nur lokal, Details `CLAUDE.md`, Abschnitt „Personenseiten und US-Politiker“, Schritt 2c/2d):
Repräsentantenhaus 2014–2026 und Senat 2012–2026. Ab Mitte 2022 liest unser eigener Leser die House-Meldungen
(`kongress_laden.py`), alles andere kommt aus dem Hugging-Face-Datensatz `austin-starks/congressional-stock-trades`
(`python3 -m pipeline.kongress_datensatz`). Aufgabe in der Planungs-App: **#68** (Senat) kann geschlossen werden,
sobald Tobias die Seiten angesehen hat.

## 1. Senat und älteres Formular (erledigt 07.11.2026 über den Datensatz)

- Senat: 83 Senatoren, 22.090 Geschäfte; älteres House-Formular und House-Scans: 144.326 Geschäfte aus 6.358 Meldungen.
  Gegen unsere eigenen House-Daten geprüft (Datum und Art 100 %, Kürzel 99,2 %, Betrag 99,5 % gleich).
- Kein DeepSeek-Lauf mehr nötig fürs ältere Formular (`kongress_altformat.py` gelöscht), keine Bild-KI für die Scans.
- Risiko: ein einzelner Betreiber. Fällt er aus, bleibt der letzte Stand; eigener Senatsleser bräuchte die
  Klick-Erklärung bei `efdsearch.senate.gov` (Nutzung nicht kommerziell), die nur Tobias abgeben kann.

## 2. Rechtslage vor dem Livegang (gilt für alles hier)

- 5 U.S.C. § 13107(c) (früher app. § 105(c)) verbietet die Nutzung der Meldungen „für kommerzielle Zwecke“ außer durch
  Nachrichtenmedien, egal aus welcher Quelle (auch über den Datensatz). Quiver, Capitol Trades u. a. veröffentlichen
  trotzdem (vermutlich über die Ausnahme für Nachrichtenmedien). Mit Anwalt klären, ob Rhodus mit Bezahlstufe darunter fällt.
- Bis dahin stehen `daten/kongress*.csv`, `daten/abgeordnete.csv`, `daten/kurse_us.parquet`, `daten/trump*.csv` und
  `docs/politiker/` in `.gitignore`. Livegang: diese Zeilen entfernen, Action nach Muster `rueckkaeufe.yml`, Link auf
  der Startseite.

## 3. Trump (OGE 278-T), ausgelesen 07.11.2026

- 20 Meldungen, 378 Seiten, **10.616 Geschäfte** in `daten/trump.csv`, gelesen vom Bildmodell GLM-4.6V-FlashX (z.AI,
  ~0,46 $). Neu laden: `python3 trump_laden.py --bilder`, dann `python3 trump_laden.py` (setzt fort).
- Offen: Meldung „08.12.2025 (2) AMENDED“ klären (was ersetzt sie?); Firmennamen → Kürzel zuordnen; Seite bauen.
- `.recherche/trump_bilder/` (399 MB) kann nach dem Lauf weg, `daten/trump_texte.csv` (alte Texterkennung) ebenso.

## 4. Kleinere Punkte

- Erledigt 07.11.2026: Geschäfte in GOOG/FOX/NWS erscheinen auf den Seiten GOOGL/FOXA/NWSA.
- Umbenannte oder übernommene Kürzel haben keine Kurse (SQ → XYZ, PXD, ATVI, DFS, MMC, BK …): ein Teil der
  Aktiengeschäfte ohne „Seitdem ggü. S&P 500“. Bei Bedarf Tabelle altes → neues Kürzel.
- Branchen-Kuchen wie bei Quiver (Sektor je Kürzel fehlt noch), Fotos (amtliche Porträts sind gemeinfrei).
- Staatsaufträge und PAC-Spenden: gebaut (S&P 500, Seiten `docs/us/`), siehe `CLAUDE.md` Schritt 4a–c.
- **Lobbying:** lda.gov und lda.senate.gov sperren alle Abrufe von außerhalb (auch Tobias im Browser), ein Schlüssel
  hilft nicht. Weg ohne Schlüssel: Lobbying-Suche des Repräsentantenhauses `disclosurespreview.house.gov` (erreichbar,
  dieselben Meldungen; Schnittstelle dahinter noch untersuchen).
