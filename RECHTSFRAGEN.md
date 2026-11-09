# Rechtsfragen vor dem Livegang (Stand 08.11.2026)

Vorbereitet von Claude für die Planungs-App #74 und #75. **Keine Rechtsberatung.** Das hier ordnet die Fragen,
entscheiden müssen Tobias bzw. ein Anwalt.

## 1. US-Kongress- und Regierungsdaten (#74)

**Worum es geht:** Politikerseiten (Repräsentantenhaus, Senat), Trump-Seite und die Tabelle „Geschäfte von
Abgeordneten“ auf den US-Firmenseiten. Alles liegt bisher nur lokal (`.gitignore`).

**Gesetz:** 5 U.S.C. § 13107(c) (früher Ethics in Government Act § 105(c)), gilt für die Vermögens- und
Transaktionsmeldungen von Kongress und Regierung, also auch für OGE 278-T (Trump). Es ist rechtswidrig, eine Meldung
zu beschaffen oder zu nutzen
1. für einen rechtswidrigen Zweck,
2. **für einen kommerziellen Zweck, außer durch Nachrichten- und Kommunikationsmedien zur Verbreitung an die
   Allgemeinheit**,
3. zur Bestimmung einer Kreditwürdigkeit,
4. für Spendenaufrufe (politisch oder gemeinnützig).

Folge: zivilrechtliche Geldbuße, die der US-Justizminister einklagen kann (Höchstbetrag gesetzlich festgelegt und an
die Inflation angepasst, genaue Zahl vom Anwalt bestätigen lassen). Das Gesetz nennt keine Ausnahme für die Quelle:
Es gilt auch, wenn wir die Daten über den Hugging-Face-Datensatz statt direkt beziehen.

**Wie es andere machen:** Quiver Quantitative, Capitol Trades (gehört zu 2iQ Research), Unusual Whales und
Senate Stock Watcher zeigen die Daten öffentlich, teils mit Bezahlstufe. Sie treten in der Regel als
Nachrichten-/Informationsangebot für die Allgemeinheit auf. Öffentlich bekannte Verfahren gegen sie kennt Claude nicht
(nicht geprüft, vom Anwalt bestätigen lassen).

**Für Rhodus spricht:** kostenlose, allgemein zugängliche Seiten mit redaktioneller Einordnung (Sonntags-Report) ähneln
einem Nachrichtenangebot.
**Dagegen spricht:** Bezahlstufe (Pro 9 €/Monat), Zweck „Folge den Profis“ ist eher Anlagewerkzeug als Berichterstattung.

**Fragen an den Anwalt (US-Recht):**
1. Fällt eine Finanzdaten-Plattform mit freiem Teil und Bezahlstufe unter die Ausnahme für Nachrichtenmedien?
2. Reicht es, wenn die Kongressdaten nur im **kostenlosen** Teil stehen (nie hinter der Bezahlschranke)?
3. Gilt das Verbot auch für ein Angebot aus Deutschland (Durchsetzbarkeit, Gerichtsstand)?
4. Ändern abgeleitete Werte etwas (Überrendite, Ranking, Hinweis „Abgeordnete kaufen X“) oder nur die Rohdaten?
5. Senat: Die Seite efdsearch.senate.gov verlangt eine Klick-Erklärung „keine kommerzielle Nutzung“. Bindet sie
   uns, wenn wir die Senatsdaten aus einem fremden Datensatz nehmen?

**Vor dem Livegang einer Bezahlstufe (Notiz 09.11.2026):** Im Impressum steht heute „privates, nichtkommerzielles
Projekt“ (stimmt derzeit). Sobald eine Bezahlstufe startet, diesen Satz streichen; dann wird diese Frage akut,
weil die Ausnahme für Nachrichtenmedien die einzige Grundlage für eine kommerzielle Nutzung wäre.

**Vorläufige Empfehlung Claude:** Bis zur Antwort lokal lassen. Wenn live, dann nur im kostenlosen Teil und als
Berichterstattung gestaltet (Texte, Einordnung), nicht als Handelssignal hinter der Bezahlschranke.

## 2. Datenschutz der Personenseiten (#75)

**Worum es geht:** 803 Seiten `docs/person/<name>/` über Vorstände und Aufsichtsräte: Name, Firma, Funktion, alle
Geschäfte seit 2018, „Seitdem ggü. Index“, Platz im Ranking. Sie sind **schon live**
(insider.tobiaszwilling.me/person/ antwortet 08.11.2026), die Datenschutzerklärung erwähnt sie noch nicht → eilt.

**Abwägung (Art. 6 Abs. 1 lit. f DSGVO, berechtigtes Interesse):**
- *Für uns:* Die Angaben sind gesetzliche Pflichtveröffentlichungen (Art. 19 MAR) mit dem ausdrücklichen Zweck,
  den Markt über Geschäfte von Führungskräften zu informieren. Betroffen ist nur die berufliche Rolle, keine privaten
  Daten. Die Firmen veröffentlichen dieselben Meldungen dauerhaft über EQS, viele Finanzportale zeigen sie ohne Frist.
  Informations- und Pressefreiheit (Art. 85 DSGVO) stützen die Auswertung.
- *Gegen uns:* Die BaFin zeigt Meldungen nur 12 Monate, wir dauerhaft. Eine Personenseite **bündelt** alle Mandate
  und Geschäfte zu einem Profil und bewertet die Person (Ranking „Timing“), das wiegt schwerer als die einzelne Meldung.
  „Über X GmbH“ nennt Gesellschaften, die Familiennamen tragen (Sabine Plattner GmbH & Co. KG).
- *Pflichten:* Information nach Art. 14 DSGVO (Daten nicht bei der Person erhoben) → über die Datenschutzerklärung;
  Widerspruchsrecht nach Art. 21 DSGVO muss ausdrücklich genannt werden.

**Empfehlung Claude:**
1. Personenseiten nur mit Vorstand und Aufsichtsrat lassen. **Angehörige und sonstige Führungspersonen nicht
   aufnehmen**: kein öffentliches Amt, geringer Mehrwert, höheres Risiko.
2. Datenschutzerklärung um den Absatz unten ergänzen (ersetzt den letzten Absatz in `docs/impressum.html`).
3. Widersprüche ernst nehmen: Seite der Person entfernen, Geschäfte bleiben anonym in Firmenseiten und Statistik.
4. Kurz von einem Anwalt für Datenschutz/Medienrecht gegenlesen lassen, vor allem das Ranking einzelner Personen.

**Entwurf für `docs/impressum.html`** (noch nicht eingebaut, ersetzt den Absatz „Die Namen der meldepflichtigen
Personen …“):

```html
<p id="personen"><b>Daten über Führungskräfte.</b> Wir zeigen Eigengeschäfte von Mitgliedern des Vorstands und
  Aufsichtsrats börsennotierter Firmen: Name, Firma, Funktion, Art, Tag, Preis und Volumen jedes Geschäfts sowie daraus
  berechnete Werte (Kursentwicklung seit dem Geschäft, Rangliste „Timing der Insider“). Je Person fassen wir diese
  Angaben auf einer eigenen Seite zusammen. Die Daten stammen nicht von den Betroffenen selbst, sondern aus
  Pflichtveröffentlichungen nach Art. 19 der Marktmissbrauchsverordnung (MAR): der Datenbank der BaFin und dem Archiv
  von EQS News. Zweck ist, die Öffentlichkeit und Anleger über Geschäfte von Führungskräften zu informieren, so wie es
  die MAR vorsieht. Rechtsgrundlage ist unser berechtigtes Interesse und das der Öffentlichkeit an dieser Information
  (Art. 6 Abs. 1 lit. f DSGVO). Wir zeigen die Geschäfte ab 2018 ohne festes Ablaufdatum, weil die Firmen die Meldungen
  ebenfalls dauerhaft veröffentlichen und erst die längere Reihe aussagekräftig ist. Angehörige und sonstige Personen in
  enger Beziehung nennen wir nicht auf eigenen Seiten. Du kannst der Verarbeitung deiner Daten aus Gründen, die sich aus
  deiner besonderen Situation ergeben, jederzeit widersprechen (Art. 21 DSGVO), per Mail an tobzwilling(at)gmx.de.
  Wir prüfen den Widerspruch und entfernen im Zweifel die Personenseite.</p>
```
