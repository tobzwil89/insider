# Technische Architektur – Empfehlung (Planung #7, 30.10.2026)

Ziel laut Tobias: Startup, Finanzdaten-Plattform wie GuruFocus/AlleAktien, global, eigene Datenbank,
Nutzerkonten, Newsletter, später API/MCP (#49) und Sentiment. Diese Datei war ein Vorschlag von Claude.
**Tobias hat am 31.10.2026 entschieden** (Abschnitt „Entschieden“ unten): Supabase, Sammler bleiben in GitHub Actions;
Website-Technik offen.

## 1. Heute

```
GitHub Actions (Python, alle 30 Min. + Knopfdruck-Läufe)
   → CSV-Dateien in daten/ (im Repository)
   → fertiges HTML/JSON in docs/ → GitHub Pages (insider.tobiaszwilling.me)
```

Funktioniert gut und kostet nichts. Ehrliche Grenzen:
- ~~**Taktung:** GitHub startet geplante Läufe unzuverlässig (23.10.: 6 statt ~48 am Tag) → Meldungen kommen Stunden zu spät.~~
  **Gelöst:** cron-job.org startet die Action seit 31.10.2026 alle 30 Min. über die GitHub-API, seit 02.11.2026 stabil
  (46–48 Läufe am Tag).
- **Laufzeit:** Knopfdruck-Läufe enden nach 320 Minuten, große Ladungen brauchen mehrere Starts.
- **Kein Nutzerkonto, kein Screener über freie Filter, keine API** möglich, weil es keinen Server gibt.
- **Daten als CSV im Repository:** gut zum Prüfen, schlecht zum Abfragen (Firma × Jahr × Quelle).
- Nicht dringend: Repository-Größe. Heute 34 MB (`.git`), GitHub empfiehlt < 1 GB.

## 2. Empfohlenes Ziel

```
Sammler (Python, wie heute)  ──schreibt──►  PostgreSQL  ◄──liest──  Website (Next.js)
  läuft per Zeitplan auf einem               eine Datenbank          Seiten vom Server erzeugt
  kleinen eigenen Server                     für alles               und zwischengespeichert
                                                 ▲
                                                 └──  API / MCP (später, #49)
```

| Baustein | Empfehlung | Warum |
|---|---|---|
| Datenbank | **PostgreSQL bei Supabase** | Standard, den jeder Entwickler kennt; Supabase bringt Anmeldung (Nutzerkonten), Sicherungen und eine Oberfläche mit. Kein Einschluss: Es bleibt normales Postgres, Umzug jederzeit. Tobias kennt Supabase aus `startup_2`. |
| Sammler | **Python-Code von heute weiterverwenden**, auf einem Server bei **Hetzner** (~5 €/Monat) mit festem Zeitplan | Löst Taktung (inzwischen über cron-job.org gelöst) und 320-Minuten-Grenze. Der Lese-Code (BaFin, EQS, Stimmrechte, Rückkäufe, 13F) bleibt, nur das Ziel wechselt von CSV zu Datenbank. |
| Website | **Next.js**, Seiten auf dem Server erzeugt und zwischengespeichert | Genau das GuruFocus-Prinzip aus `GURUFOCUS.md` (fertige Seiten, schnell, gut für SEO), dazu Konten, Screener, Bezahlung. Größte Auswahl an fertigen Bausteinen und Vorlagen; Tobias hat damit schon gearbeitet. |
| Hosting Website | Vercel (kostenlos zum Start) | Kein eigener Webserver nötig. |
| Bezahlung | Stripe | Standard für Abos. |
| Newsletter | EmailOctopus → **seit 31.10.2026 Kit** | Abschnitt „Marketing und Website“ in `VORHABEN.md`. |
| KI/Sentiment | als Stapel-Job im Sammler, Ergebnis als Zahl je Firma und Tag in der Datenbank | Keine KI-Aufrufe beim Seitenaufruf → billig und schnell. Für das Produkt einen Anbieter mit EU-Vertrag statt DeepSeek direkt. |
| Statistik | Plausible oder Umami | cookielos, keine Einwilligung nötig. |

**Grundregeln, die bleiben:** ISIN als feste ID, Rohdaten nie überschreiben (nur ergänzen), jede Quelle mit
Abrufdatum und Adresse speichern, Berechnungen (Event Study, Ranking) im Sammler, nicht in der Website.
Als Vorlage für das Datenbankschema die OpenBB-Standardmodelle (`DATENQUELLEN.md` Abschnitt 5).

Laufende Kosten zum Start: ca. 5–10 €/Monat (Hetzner; Supabase und Vercel gratis). Mit Nutzern und mehr Daten
ca. 50 €/Monat (Supabase Pro 25 $, Vercel Pro 20 $). Bezahlte Kurs-/Fundamentaldaten kommen extra (EODHD/FMP ~20–30 €).

## 3. Warum nicht anders

- **Statisch bleiben (wie heute):** reicht für Inhalte, aber nicht für Konten, Screener, API. Das Startup-Ziel braucht das.
- **Alles in Python (FastAPI + Vorlagen):** eine Sprache weniger, aber Oberflächen, Anmeldung und Bezahlung muss man
  mühsam selbst bauen. Für eine hübsche Seite für „Normalos“ ist Next.js der kürzere Weg.
- **Spezial-Datenbanken** (TimescaleDB, ClickHouse): erst bei hunderten Millionen Kurszeilen nötig. Postgres reicht lange.
- **Alles selbst auf einem Server** (auch Datenbank und Website): billiger, aber Sicherungen, Updates und Ausfälle
  liegen dann bei dir. Zum Start lohnt sich „verwaltet“.

## 4. Weg dorthin (in Blöcken, jederzeit abbrechbar)

1. **Datenbank anlegen und befüllen:** Schema entwerfen, alle CSVs einmal importieren, Zahlen gegen die CSVs prüfen.
2. **Sammler schreibt zusätzlich in die Datenbank** (CSV bleibt vorerst als Sicherung). Website unverändert.
3. **Sammler auf den Server umziehen**, GitHub Actions abschalten. ~~Ab hier kommen Meldungen pünktlich.~~ (Pünktlich
   sind sie schon seit cron-job.org, 02.11.2026; Block 3 entfällt vorerst, siehe unten.)
4. **Neue Website** (Next.js) liest aus der Datenbank; die alte bleibt online, bis die neue alles kann. Design erst
   nach Positionierung und Stitch-Entwürfen (Reihenfolge aus „Marketing und Website“).
5. **Konten, Watchlist, Benachrichtigungen, Bezahlung**, danach API/MCP.

Block 1–3 kann Claude weitgehend allein bauen; Tobias muss nur die Konten anlegen (Supabase, Hetzner).

## Entschieden (Tobias, 31.10.2026)

- [x] **Datenbank: PostgreSQL bei Supabase, kostenloses Paket.** Kein Hetzner-Server, solange kein MVP steht.
      Die Sammler laufen weiter in GitHub Actions und schreiben in Supabase (Block 3 „Server-Umzug“ entfällt vorerst).
- [x] **Budget:** bis zum MVP 0 €. Ab richtigem Livegang ~50 €/Monat in Ordnung.
- [x] **Start: nach der Positionierung**, aber bevor das Universum über DAX/MDAX hinaus wächst. Die Positionierung ist
      seit 31.10.2026 erledigt (nur der Name fehlt) → Block 1–2 kann starten, sobald Tobias ein Supabase-Konto anlegt.
- [ ] Website-Technik (Next.js oder anderes) festlegen – jetzt möglich, da die Positionierung steht.

Folgen und Hinweise:
- Kostenloses Supabase-Paket: 500 MB Datenbank (heute ~35 MB CSV, reicht für DAX/MDAX lange). Projekte ohne Aktivität
  werden nach 7 Tagen pausiert. Das passiert nicht, solange die Action regelmäßig schreibt. Tägliche Kurse für
  Tausende Firmen (~2–3 GB) brauchen später Supabase Pro (25 $).
- Taktung: **gelöst.** cron-job.org startet die Action seit 31.10.2026 über die GitHub-API (`workflow_dispatch`),
  seit 02.11.2026 stabil (46–48 Läufe am Tag, geprüft 06.11.2026). Die GitHub-Zeitpläne bleiben als Reserve.
- Beim späteren Umzug auf einen Server zuerst prüfen, ob onvista/TradingView Rechenzentrums-Adressen sperren.
