# US-Kongress und US-Politiker: was noch offen ist

Stand 06.11.2026. Gebaut ist das Repräsentantenhaus ab Mitte 2022 (nur lokal, siehe `CLAUDE.md`, Abschnitt
„Personenseiten und US-Politiker“). Aufgabe in der Planungs-App: **#68** (Senat).

## 1. Senat (wartet auf Tobias, „jetzt nicht“)

- `efdsearch.senate.gov` verlangt vor der Suche eine Erklärung per Klick: Die Meldungen werden nicht für kommerzielle
  Zwecke genutzt (5 U.S.C. app. § 105(c); erlaubt sind Nachrichtenmedien). Claude darf das nicht in Tobias' Namen bestätigen.
- Danach technisch einfach: elektronische Senats-Meldungen sind HTML-Tabellen. Laut Erfahrungsberichten sperrt Akamai
  Rechenzentrums-IPs (GitHub Actions) → lokal laden.

## 2. Rechtslage vor dem Livegang (gilt für alles hier)

- Dasselbe Gesetz gilt für die Meldungen des Repräsentantenhauses (dort ohne Klick). Quiver, Capitol Trades u. a.
  veröffentlichen trotzdem (vermutlich über die Ausnahme für Nachrichtenmedien). Mit Anwalt klären, ob Rhodus mit
  Bezahlstufe darunter fällt.
- Bis dahin stehen `daten/kongress*.csv`, `daten/abgeordnete.csv`, `daten/kurse_us.parquet` und `docs/politiker/` in
  `.gitignore`. Livegang: diese Zeilen entfernen, Action nach Muster `rueckkaeufe.yml`, Link auf der Startseite.

## 3. Auslesen per Sprachmodell (Schätzung 06.11.2026, gemessen an Stichproben)

Grundlage: DeepSeek V4-Flash, 0,14 $ je Mio. Eingabe- und 0,28 $ je Mio. Ausgabe-Token (passt zur eigenen Rechnung
aus Block 6b: 5,0 + 0,65 Mio. Token = 0,93 $). Texterkennung für Scans lokal und kostenlos mit Apple Vision
(`swift`, getestet an einer Papiermeldung von Chuck Fleischmann 2024: Text gut lesbar, Spaltenzuordnung geht verloren).

| Paket | Umfang (Stichprobe) | Token ein / aus | Kosten | Unsicherheit |
|---|---|---|---|---|
| Altformat House 2014 – Mitte 2022 | 3.994 Meldungen, Ø 3.150 Zeichen, Ø 13 Geschäfte (40 Stichproben) → ~52.000 Geschäfte | ~5,6 / ~2,4 Mio. | **~1,50 $** | gering: Text ist da, nur ungeordnet |
| Trump (OGE 278-T) | 20 Meldungen 08/2025–10/2026; Seitenzahl geschätzt 600–1.000, ~20.000–35.000 Geschäfte | ~1,2 / ~1,4 Mio. | **~0,60 $** | mittel: Scans mit Tabellen, erst neu erkennen (Apple Vision) |
| Papier-Scans House | 2.003 Meldungen, Ø 4,6 Seiten (30 Stichproben) → ~9.200 Seiten, ~45.000 Geschäfte | ~7,5 / ~2,0 Mio. | **~1,60 $** | hoch: Kästchen Kauf/Verkauf stehen getrennt von der Zeile |

**Zusammen ~3,70 $, mit Sicherheitsaufschlag (×1,5) höchstens etwa 6 $.** Die Schätzung von Block 6b lag um den Faktor
3 zu niedrig (Probe zu klein) → deshalb hier mit Aufschlag und je Paket erst eine Probe (30 Meldungen, ~0,05 $) mit
Handprüfung, dann Gesamtlauf. Apple Vision braucht lokal etwa 2–4 s je Seite (~8 h für alle Scans, in Blöcken).

Empfohlene Reihenfolge: Altformat (billig, sicher, bringt 2014–2022) → Trump (hohes Interesse) → Scans (nur wenn die
Probe sauber ist; sonst ein Sprachmodell mit Bildeingabe, Preis vorher prüfen).

DeepSeek-Guthaben war am 29.10.2026 leer (0,05 $) → vor dem Lauf aufladen.

**Stand 07.11.2026:** Altformat und Trump sind bis zum bezahlten Schritt vorbereitet (`kongress_altformat.py`,
`trump_laden.py`, Texte liegen in `daten/`). Trump gemessen: 378 Seiten, ~16.000 Zeilen → neu geschätzt ~0,30 $.
Die Scans gehen mit Apple Vision + DeepSeek **nicht**: Die Kreuze für Kauf/Verkauf und Betragsspanne werden nicht als
Text erkannt. Dafür braucht es ein Modell, das Bilder liest (~9.200 Seiten) → Preis vorher prüfen, Entscheidung Tobias.

Befehle (im Projektordner, wo `.env` liegt):

    python3 kongress_altformat.py --probe 30     # ~0,02 $, Ergebnis .recherche/kongress_alt_probe.csv
    python3 kongress_altformat.py                # Rest, ~1,70 $ (36.000 Geschäfte)
    python3 trump_laden.py --probe 3             # Ergebnis .recherche/trump_probe.csv
    python3 trump_laden.py                       # Rest, ~0,30 $

## 4. Kleinere Punkte

- Erledigt 07.11.2026: Geschäfte in GOOG/FOX/NWS erscheinen auf den Seiten GOOGL/FOXA/NWSA.
- Umbenannte oder übernommene Kürzel haben keine Kurse (SQ → XYZ, PXD, ATVI, DFS, MMC, BK …): 5 % der Aktiengeschäfte
  ohne „Seitdem ggü. S&P 500“. Bei Bedarf Tabelle altes → neues Kürzel.
- Branchen-Kuchen wie bei Quiver (Sektor je Kürzel fehlt noch), Fotos (amtliche Porträts sind gemeinfrei).
- Staatsaufträge und PAC-Spenden: gebaut (S&P 500, Seiten `docs/us/`), siehe `CLAUDE.md` Schritt 4a–c.
- **Lobbying:** Das Register (lda.gov) sperrt Abrufe ohne Schlüssel (403). Tobias: kostenlosen Schlüssel unter
  lda.gov/api/register beantragen, in `.env` als `LDA_API_KEY` eintragen.
