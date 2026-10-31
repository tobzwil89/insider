"""Fertige HTML-Seiten je Firma (wie GuruFocus' Server-Side Rendering, nur ohne Server).

Jede Firma bekommt docs/firma/<TICKER>/index.html mit allen Zahlen und Tabellen schon im HTML.
Der Besucher sieht sofort Inhalt, Suchmaschinen finden jede Firma einzeln, Links sind teilbar.
Nur das Kursdiagramm zeichnet firma.js; die Kurse kommen aus data/kurse/<TICKER>.json.

Alle Texte aus BaFin/EQS gehen durch html.escape (sie sind fremde Daten).
"""

import hashlib
import html
import json
import math
import re
from pathlib import Path

import pandas as pd

from pipeline import AUSGABE

DOCS = AUSGABE.parent
WEBSITE = "https://insider.tobiaszwilling.me"
STATISCH = ["style.css", "gemeinsam.js", "start.js", "firma.js"]
INDEXNAME = {"^GDAXI": "dem DAX", "^MDAXI": "dem MDAX"}
FARBE = {"Kauf": "var(--kauf)", "Verkauf": "var(--verkauf)"}
# Börsennotiert sind nur stimmrechtslose Vorzugsaktien; die Stimmrechte liegen bei einem festen Kreis
NUR_VORZUG = {"PAH3.DE", "P911.DE"}
POSITION = {"in enger Beziehung": "eng verbunden", "Sonstige Führungsperson": "Führungsperson"}


# --- Formatierung wie fmt in gemeinsam.js ---------------------------------------------------

def _leer(x) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x)) or x is pd.NaT


def zahl(x, stellen: int = 0) -> str:
    if _leer(x):
        return "–"
    return f"{x:,.{stellen}f}".replace(",", " ").replace(".", ",").replace(" ", ".")


def euro(x, waehrung: str = "EUR") -> str:
    if _leer(x):
        return "–"
    zeichen = "€" if waehrung in ("EUR", "", None) or _leer(waehrung) else waehrung
    if abs(x) >= 1e6:
        return f"{zahl(x / 1e6, 1)} Mio. {zeichen}"
    if abs(x) >= 1e4:
        return f"{zahl(x / 1e3)} Tsd. {zeichen}"
    return f"{zahl(x)} {zeichen}"


def prozent(x, stellen: int = 1) -> str:
    if _leer(x):
        return "–"
    return ("+" if x > 0 else "−" if x < 0 else "") + zahl(abs(x) * 100, stellen) + " %"


def datum(d) -> str:
    return "–" if _leer(d) else pd.Timestamp(d).strftime("%d.%m.%Y")


def e(text) -> str:
    return "" if _leer(text) else html.escape(str(text))


def _vorzeichen_klasse(x) -> str:
    return "" if _leer(x) else "positiv" if x > 0 else "negativ" if x < 0 else ""


def _art(art: str) -> str:
    return (f'<span class="art"><span class="punkt" style="background:{FARBE.get(art, "var(--sonstiges)")}">'
            f'</span>{e(art)}</span>')


def _tabelle(kopf: list, zeilen: list) -> str:
    """kopf: [(Text, Klasse)], zeilen: Listen von (HTML, Klasse)."""
    th = "".join(f'<th class="{k}">{e(t)}</th>' for t, k in kopf)
    tr = "".join("<tr>" + "".join(f'<td class="{k}">{h}</td>' for h, k in z) + "</tr>" for z in zeilen)
    return f'<div class="tabelle-rahmen"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def _kachel(label: str, wert: str, zusatz: str) -> str:
    return (f'<div class="kachel"><div class="label">{e(label)}</div><div class="wert">{e(wert)}</div>'
            f'<div class="zusatz">{e(zusatz)}</div></div>')


# --- Versionsnummern: Prüfsumme statt ?v=2 von Hand -------------------------------------------

def versionen() -> dict:
    return {d: hashlib.sha1((DOCS / d).read_bytes()).hexdigest()[:8] for d in STATISCH}


def versionen_eintragen(v: dict) -> None:
    """Setzt ?v=<Prüfsumme> in den handgeschriebenen Seiten (index, methode, impressum, firma.html)."""
    for seite in DOCS.glob("*.html"):
        text = seite.read_text(encoding="utf-8")
        neu = re.sub(r'(style\.css|gemeinsam\.js|start\.js|firma\.js)\?v=[0-9a-z]+', lambda m: f"{m[1]}?v={v[m[1]]}", text)
        if neu != text:
            seite.write_text(neu, encoding="utf-8")


# --- Firmenseite --------------------------------------------------------------------------------

def firmenseite(f: dict, meldungen: pd.DataFrame, ereignisse: pd.DataFrame, ranking: pd.DataFrame,
                letzter_kurs: tuple, v: dict, aktionaere: pd.DataFrame, rueckkaeufe: pd.DataFrame | None = None,
                rueck_ohne_meldungen: bool = False) -> str:
    """f: ticker, name, index, benchmark, isins. ranking: Zeilen dieser Firma mit Spalte 'rang'.
    aktionaere: Zeilen dieser Firma aus stimmrechte.grossaktionaere.
    rueckkaeufe: Zeilen dieser Firma aus rueckkaeufe.jahre; None = Historie noch nicht geladen, Abschnitt fehlt.
    rueck_ohne_meldungen: EQS führt für die Firma keine Rückkaufmeldungen → „keine Daten“ statt „keine Rückkäufe“."""
    index_name = INDEXNAME.get(f["benchmark"], f["benchmark"])
    aktien = meldungen[meldungen["instrument"].eq("Aktie")]
    kaeufe, verkaeufe = aktien[aktien["art"].eq("Kauf")], aktien[aktien["art"].eq("Verkauf")]
    ev_kauf = ereignisse[ereignisse["art"].eq("Kauf")]
    kacheln = "".join([
        _kachel("Schlusskurs", f"{zahl(letzter_kurs[1], 2)} €" if letzter_kurs else "–",
                f"am {datum(letzter_kurs[0])}" if letzter_kurs else ""),
        _kachel("Insider-Käufe", zahl(len(kaeufe)), f"zusammen {euro(kaeufe['volumen'].sum())}"),
        _kachel("Insider-Verkäufe", zahl(len(verkaeufe)), f"zusammen {euro(verkaeufe['volumen'].sum())}"),
        _kachel("Ø Reaktion nach Käufen", prozent(ev_kauf["car_ab_0"].mean() if len(ev_kauf) else None),
                f"CAR Tag 0 bis +5, {len(ev_kauf)} Ereignisse"),
    ])

    if ereignisse.empty:
        ev_html = ('<p class="leer">Noch keine auswertbaren Ereignisse. Es braucht mindestens 100 Handelstage '
                   'Kurshistorie vor der Meldung.</p>')
    else:
        ev_html = _tabelle(
            [("Veröffentlicht", ""), ("Art", ""), ("Personen", ""), ("Volumen", "zahl"),
             ("CAR −5 bis +5", "zahl"), ("CAR 0 bis +5", "zahl")],
            [[(datum(r.mitteilungsdatum), "datum"), (_art(r.art), ""), (e("; ".join(r.personen)), ""),
              (euro(r.volumen), "zahl"), (prozent(r.car), f"zahl {_vorzeichen_klasse(r.car)}"),
              (prozent(r.car_ab_0) + (f'<div class="klein">erst bis Tag +{int(r.tage_nach)}</div>'
                                      if r.tage_nach < 5 else ""), f"zahl {_vorzeichen_klasse(r.car_ab_0)}")]
             for r in ereignisse.sort_values("mitteilungsdatum").itertuples()])

    if ranking.empty:
        rk_html = ('<p class="leer">Keine Führungskraft dieser Firma hat mindestens 3 Käufe mit abgeschlossenen '
                   '3 Monaten.</p>')
    else:
        rk_html = _tabelle(
            [("#", "zahl"), ("Person", ""), ("Käufe", "zahl"), ("Typisch (Median)", "zahl"),
             ("Durchschnitt", "zahl"), ("Besser als Index", "zahl"), ("Zeitraum", "")],
            [[(str(r.rang), "zahl"),
              (f'{e(r.person)}<div class="klein">{e(POSITION.get(r.position, r.position))}</div>', ""),
              (str(r.kaeufe), "zahl"), (prozent(r.median), f"zahl {_vorzeichen_klasse(r.median)}"),
              (prozent(r.ueberrendite), "zahl"), (f"{zahl(r.trefferquote * 100)} %", "zahl"),
              (e(f"{r.erster_kauf:%Y}" if r.erster_kauf.year == r.letzter_kauf.year
                 else f"{r.erster_kauf:%Y}–{r.letzter_kauf:%Y}"), "datum")]
             for r in ranking.itertuples()])

    vorzug = ('<p class="erklaerung"><b>An der Börse gehandelt werden nur Vorzugsaktien ohne Stimmrecht.</b> '
              'Die Prozente beziehen sich auf die Stammaktien. Sie werden den Familien Porsche und Piëch über '
              'Beteiligungsgesellschaften und Stimmbindungen vollständig zugerechnet (bei der Porsche AG über '
              'Porsche SE und Volkswagen), deshalb meldet jedes Mitglied die vollen 100 %. Hier stehen sie in einer Zeile.</p>' if f["ticker"] in NUR_VORZUG else "")
    if aktionaere.empty:
        ga_html = ('<p class="leer">Keine Halter über den Meldeschwellen laut den Stimmrechtsmitteilungen '
                   'im EQS-Archiv seit 2018. Das heißt nicht, dass es keine Großaktionäre gibt.</p>')
    else:
        ga_html = _tabelle(
            [("Halter", ""), ("Aktien", "zahl"), ("Instrumente", "zahl"), ("Zusammen", "zahl"), ("Stand", "")],
            [[(e(r.halter) + (f'<div class="klein">dieselben Aktien auch bei: {e(r.weitere)}</div>' if r.weitere else ""), ""),
              (f"{zahl(r.aktien, 2)} %", "zahl"), (f"{zahl(r.instrumente, 2)} %", "zahl"),
              (f"<b>{zahl(r.summe, 2)} %</b>", "zahl"),
              (f'<a href="{e(r.url)}" rel="nofollow">{datum(r.schwellendatum)}</a>'
               + (f'<div class="klein">geprüft {datum(r.geprueft)}</div>' if not _leer(r.geprueft) else ""), "datum")]
             for r in aktionaere.itertuples()])

    if rueckkaeufe is None:
        rueck_abschnitt = ""
    else:
        if rueck_ohne_meldungen:
            rueck_html = ('<p class="leer">Keine Daten: Das EQS-Archiv enthält für diese Firma keine Rückkaufmeldungen '
                          'seit 2018. Das heißt nicht, dass es keine Rückkäufe gab; viele Firmen veröffentlichen '
                          'über einen anderen Verteiler.</p>')
        elif rueckkaeufe.empty:
            rueck_html = '<p class="leer">Keine Aktienrückkäufe seit 2018 laut EQS-Archiv.</p>'
        else:
            rueck_html = _tabelle(
                [("Jahr", ""), ("Handelstage", "zahl"), ("Aktien", "zahl"), ("Volumen", "zahl"), ("Ø Kurs", "zahl"),
                 ("Letzter Kauf", "")],
                [[(str(r.jahr), "datum"), (zahl(r.tage), "zahl"), (zahl(r.stueck), "zahl"), (euro(r.volumen), "zahl"),
                  (f"{zahl(r.kurs, 2)} €", "zahl"), (datum(r.letzter), "datum")]
                 for r in rueckkaeufe.itertuples()])
        rueck_abschnitt = f"""
    <section class="karte">
      <h2>Aktienrückkäufe</h2>
      <p class="erklaerung">Eigene Aktien, die die Firma über die Börse zurückgekauft hat, laut ihren wöchentlichen
        Meldungen nach Art. 5 MAR (EQS-Archiv seit 2018). Volumen = Stückzahl × Tagesdurchschnittskurs, ohne Nebenkosten.
        Zurückgekaufte Aktien werden meist eingezogen oder für Mitarbeiterprogramme genutzt.</p>
      {rueck_html}
    </section>
"""

    if meldungen.empty:
        m_html = '<p class="leer">Seit Beginn der Aufzeichnung keine Meldungen.</p>'
    else:
        m_html = _tabelle(
            [("Veröffentlicht", ""), ("Geschäft", ""), ("Person", ""), ("Art", ""), ("Instrument", ""),
             ("Volumen", "zahl"), ("Kurs", "zahl")],
            [[(datum(r.mitteilungsdatum), "datum"), (datum(r.geschaeftsdatum), "datum"),
              (f'{e(r.person)}<div class="klein">{e(POSITION.get(r.position, r.position))}</div>', ""),
              (_art(r.art), ""), (e(r.instrument), ""), (euro(r.volumen, r.waehrung), "zahl"),
              (zahl(r.preis, 2), "zahl")]
             for r in meldungen.itertuples()])

    # Für die Markierungen im Kursdiagramm; "</" maskieren, damit kein Text das <script> beenden kann
    marker = aktien[aktien["art"].isin(FARBE)][["geschaeftsdatum", "art", "person", "volumen", "waehrung"]]
    daten = {"ticker": f["ticker"], "name": f["name"], "marker": [
        {"geschaeftsdatum": pd.Timestamp(m.geschaeftsdatum).strftime("%Y-%m-%d"),
         "art": m.art, "person": m.person, "volumen": None if _leer(m.volumen) else round(float(m.volumen), 2),
         "waehrung": m.waehrung} for m in marker.dropna(subset=["geschaeftsdatum"]).itertuples()]}
    daten_json = json.dumps(daten, ensure_ascii=False).replace("</", "<\\/")

    titel = f"{f['name']}: Insider-Käufe und -Verkäufe"
    beschreibung = (f"Directors' Dealings bei {f['name']} ({f['ticker']}): {len(kaeufe)} Käufe und "
                    f"{len(verkaeufe)} Verkäufe von Vorstand und Aufsichtsrat seit 2018, Kursreaktionen und Timing.")
    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(titel)} · Insider-Monitor</title>
  <meta name="description" content="{e(beschreibung)}">
  <link rel="canonical" href="{WEBSITE}/firma/{e(f['ticker'])}/">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><rect width='16' height='16' rx='3' fill='%232a78d6'/><path d='M3 11l3-3 2 2 5-5' stroke='white' stroke-width='2' fill='none'/></svg>">
  <link rel="stylesheet" href="../../style.css?v={v['style.css']}">
</head>
<body>
  <div class="hinweisband">Keine Anlageberatung. Alle Angaben ohne Gewähr, Quellen: BaFin-Datenbank der Eigengeschäfte von Führungskräften, EQS-Archiv.</div>

  <header class="kopf">
    <div class="marke"><a href="../../">← Insider-Monitor</a></div>
    <h1>{e(f['name'])}</h1>
    <p class="unterzeile">{e(f['ticker'])} · {e(f['index'])} · ISIN {e(', '.join(f['isins']))}</p>
  </header>

  <main>
    <div class="kacheln">{kacheln}</div>

    <section class="karte">
      <h2>Kurs und Insider-Geschäfte</h2>
      <p class="erklaerung">Schlusskurse bereinigt um Dividenden und Splits. Punkte markieren Aktienkäufe und -verkäufe
        von Führungskräften am Tag des Geschäfts. Fahre über das Diagramm für Details.</p>
      <div class="filter">
        <div class="knopfgruppe" id="zeitraum">
          <button aria-pressed="false" data-monate="6">6 Monate</button>
          <button aria-pressed="false" data-monate="12">1 Jahr</button>
          <button aria-pressed="false" data-monate="24">2 Jahre</button>
          <button aria-pressed="true" data-monate="60">5 Jahre</button>
          <button aria-pressed="false" data-monate="999">Alles</button>
        </div>
      </div>
      <div class="legende">
        <span><span class="strich" style="background:var(--kurs)"></span>Schlusskurs</span>
        <span><span class="punkt" style="background:var(--kauf)"></span>Insider-Kauf</span>
        <span><span class="punkt" style="background:var(--verkauf)"></span>Insider-Verkauf</span>
      </div>
      <div id="kurs"></div>
    </section>

    <section class="karte">
      <h2>Kursreaktion je Ereignis</h2>
      <p class="erklaerung">Abnormale Rendite (CAR) gegenüber dem Marktmodell mit {e(index_name)},
        von 5 Handelstagen vor bis 5 nach der Veröffentlichung. Nur Vorstand und Aufsichtsrat, Käufe und Verkäufe am selben
        Tag sind je ein Ereignis. Einzelne Ereignisse schwanken stark, aussagekräftig ist erst der Durchschnitt
        auf der <a href="../../">Startseite</a>.</p>
      {ev_html}
    </section>

    <section class="karte">
      <h2>Timing der Insider</h2>
      <p class="erklaerung">Überrendite gegenüber {e(index_name)} in den 3 Monaten nach den Aktienkäufen, für Personen
        mit mindestens 3 Käufen. Der Rang bezieht sich auf alle Insider im DAX und MDAX
        (<a href="../../">Startseite</a>, <a href="../../methode.html#ranking">Methode</a>).</p>
      {rk_html}
    </section>

    <section class="karte">
      <h2>Großaktionäre</h2>
      <p class="erklaerung">Stimmrechtsanteile laut der letzten Stimmrechtsmitteilung je Halter (§§ 33 ff. WpHG),
        gezählt ab 3 % in Aktien oder 5 % zusammen mit Instrumenten. Stand ist das Datum der Schwellenberührung,
        der Link führt zur Mitteilung. <b>Was jemand besitzt, steht in der Spalte Aktien.</b> Instrumente sind
        keine Aktien, sondern Rechte darauf (Optionen, Wertpapierleihe, Derivate): Hinter derselben Aktie stehen oft
        mehrere Instrumente, etwa bei Käufer und Verkäufer einer Option. Die Spalten Instrumente und Zusammen
        lassen sich deshalb nicht addieren und können über 100 % ergeben. Melden Mutter, Tochter oder Familienmitglieder
        dieselben Aktien, steht das in einer Zeile.
        <b>Ausgewertet sind Mitteilungen seit 2018 aus dem EQS-Archiv:</b> Wer seinen Anteil seitdem nicht verändert hat
        (oft Gründerfamilien oder Mutterkonzerne), fehlt hier. Nach Umfirmierungen kann ein Halter doppelt erscheinen.
        Einträge mit „geprüft“ haben wir von Hand mit veröffentlichten Angaben abgeglichen (Firma oder Wirtschaftspresse, Link zur Quelle).</p>
      {vorzug}{ga_html}
    </section>
{rueck_abschnitt}
    <section class="karte">
      <h2>Alle Meldungen</h2>
      {m_html}
    </section>
  </main>

  <footer>
    <p><b>Keine Anlageberatung.</b> Diese Seite zeigt öffentlich gemeldete Daten und statistische Auswertungen. Sie ist keine
      Empfehlung, Wertpapiere zu kaufen oder zu verkaufen.</p>
    <p><a href="../../methode.html">Methode</a> · <a href="../../impressum.html">Impressum und Datenschutz</a></p>
  </footer>

  <script type="application/json" id="daten">{daten_json}</script>
  <script src="../../gemeinsam.js?v={v['gemeinsam.js']}"></script>
  <script src="../../firma.js?v={v['firma.js']}"></script>
</body>
</html>
"""


# --- Guru-Depots (13F) ----------------------------------------------------------------------------

STATUS_FARBE = {"neu": "var(--kauf)", "aufgestockt": "var(--kauf)", "reduziert": "var(--verkauf)",
                "verkauft": "var(--verkauf)"}


def kurzname(name: str) -> str:
    """'Warren Buffett (Berkshire Hathaway)' → 'warren-buffett' für die Adresse."""
    return re.sub(r"[^a-z]+", "-", name.split("(")[0].lower()).strip("-")


def usd(x) -> str:
    if _leer(x):
        return "–"
    if abs(x) >= 1e9:
        return f"{zahl(x / 1e9, 1)} Mrd. $"
    return f"{zahl(x / 1e6, 1)} Mio. $"


def _guru_rahmen(titel: str, beschreibung: str, adresse: str, wurzel: str, kopf: str, inhalt: str, v: dict) -> str:
    """Gemeinsames Seitengerüst; wurzel = relativer Weg zur Startseite ('../' oder '../../')."""
    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(titel)} · Insider-Monitor</title>
  <meta name="description" content="{e(beschreibung)}">
  <link rel="canonical" href="{WEBSITE}/{adresse}">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><rect width='16' height='16' rx='3' fill='%232a78d6'/><path d='M3 11l3-3 2 2 5-5' stroke='white' stroke-width='2' fill='none'/></svg>">
  <link rel="stylesheet" href="{wurzel}style.css?v={v['style.css']}">
</head>
<body>
  <div class="hinweisband">Keine Anlageberatung. Alle Angaben ohne Gewähr, Quelle: Formular 13F der US-Börsenaufsicht SEC.</div>
  <header class="kopf">{kopf}</header>
  <main>{inhalt}</main>
  <footer>
    <p><b>Keine Anlageberatung.</b> Diese Seite zeigt öffentlich gemeldete Daten. Sie ist keine
      Empfehlung, Wertpapiere zu kaufen oder zu verkaufen.</p>
    <p><a href="{wurzel}methode.html">Methode</a> · <a href="{wurzel}impressum.html">Impressum und Datenschutz</a></p>
  </footer>
</body>
</html>
"""


ERKLAERUNG_13F = ("Wer in den USA mehr als 100 Mio. USD in US-Wertpapieren verwaltet, muss jedes Quartal seine "
                  "Positionen melden (Formular 13F). Die Meldung kommt bis zu 45 Tage nach Quartalsende, die "
                  "Positionen können sich seitdem also geändert haben. Enthalten sind nur an US-Börsen gehandelte "
                  "Papiere (deutsche Aktien nur als ADR, z. B. SAP oder Deutsche Bank), keine Leerverkäufe, kein Bargeld.")


def guruseite(d: dict, v: dict) -> str:
    p = d["positionen"]
    gehalten = p[p["status"] != "verkauft"]
    vq = f"Veränderung zum {datum(d['vorquartal'])} nach Stückzahl." if d["vorquartal"] else ""
    tabelle = _tabelle(
        [("Wertpapier", ""), ("Wert", "zahl"), ("Anteil", "zahl"), ("Stück", "zahl"), ("Veränderung", "")],
        [[(f'{e(r.emittent)}<div class="klein">{e(r.klasse)}{" · " + e(r.put_call) if r.put_call else ""}</div>', ""),
          (usd(r.wert_usd), "zahl"), ("–" if _leer(r.anteil) else f"{zahl(r.anteil * 100, 1)} %", "zahl"),
          (zahl(r.stueck), "zahl"),
          (f'<span class="art"><span class="punkt" style="background:{STATUS_FARBE.get(r.status, "var(--sonstiges)")}">'
           f'</span>{e(r.status)}</span>'
           + (f' <span class="klein">{prozent(r.veraenderung, 0)}</span>'
              if r.status in ("aufgestockt", "reduziert") else ""), "")]
         for r in p.itertuples()])
    kopf = (f'<div class="marke"><a href="../">← Alle Investoren</a></div><h1>{e(d["name"])}</h1>'
            f'<p class="unterzeile">13F-Meldung zum {datum(d["quartal"])}, eingereicht am {datum(d["eingereicht"])}'
            f' · <a href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&amp;CIK={d["cik"]}&amp;type=13F"'
            f' rel="nofollow">Originalmeldungen bei der SEC</a></p>')
    kacheln = "".join([
        _kachel("Depotwert", usd(d["wert"]), "nur Aktien, ohne Optionen"),
        _kachel("Positionen", zahl(len(gehalten)), f"Stand {datum(d['quartal'])}"),
        _kachel("Neu gekauft", zahl((p["status"] == "neu").sum()), "im letzten Quartal"),
        _kachel("Ganz verkauft", zahl((p["status"] == "verkauft").sum()), "im letzten Quartal"),
    ])
    inhalt = (f'<div class="kacheln">{kacheln}</div><section class="karte"><h2>Positionen</h2>'
              f'<p class="erklaerung">{ERKLAERUNG_13F} {vq} Bei Optionen (Put/Call) ist der Wert der des Basiswerts; '
              f'sie zählen nicht zum Anteil.</p>{tabelle}</section>')
    return _guru_rahmen(f"{d['name']}: Depot laut 13F", f"Aktiendepot von {d['name']} laut SEC-Meldung zum "
                        f"{datum(d['quartal'])}: Positionen, Käufe und Verkäufe.",
                        f"gurus/{kurzname(d['name'])}/", "../../", kopf, inhalt, v)


def gurus_uebersicht(depots: list, v: dict) -> str:
    zeilen = []
    for d in sorted(depots, key=lambda d: -d["wert"]):
        p = d["positionen"]
        top = p[p["put_call"] == ""].iloc[0]
        zeilen.append([(f'<a href="{kurzname(d["name"])}/">{e(d["name"])}</a>', ""), (usd(d["wert"]), "zahl"),
                       (zahl((d["positionen"]["status"] != "verkauft").sum()), "zahl"),
                       (f'{e(top.emittent)} <span class="klein">{zahl(top.anteil * 100, 0)} %</span>', ""),
                       (datum(d["quartal"]), "datum")])
    kopf = ('<div class="marke"><a href="../">← Insider-Monitor</a></div><h1>Depots bekannter Investoren</h1>'
            '<p class="unterzeile">Was Buffett und andere bekannte Investoren laut ihren Pflichtmeldungen bei der '
            'US-Börsenaufsicht halten.</p>')
    inhalt = (f'<section class="karte"><h2>Investoren</h2><p class="erklaerung">{ERKLAERUNG_13F} '
              'Steht beim Stand ein älteres Quartal, kam seitdem keine neue Meldung (z. B. Fonds geschlossen).</p>'
              + _tabelle([("Investor", ""), ("Depotwert", "zahl"), ("Positionen", "zahl"),
                          ("Größte Position", ""), ("Stand", "")], zeilen) + "</section>")
    return _guru_rahmen("Depots bekannter Investoren (13F)", "Aktiendepots von Warren Buffett, Bill Ackman und "
                        "anderen bekannten Investoren laut SEC-Formular 13F.", "gurus/", "../", kopf, inhalt, v)


def sitemap(ticker: list, weitere: list = ()) -> str:
    heute = pd.Timestamp.now().strftime("%Y-%m-%d")
    adressen = ([f"{WEBSITE}/", f"{WEBSITE}/methode.html"] + [f"{WEBSITE}/firma/{t}/" for t in ticker]
                + [f"{WEBSITE}/{a}" for a in weitere])
    eintraege = "".join(f"<url><loc>{html.escape(a)}</loc><lastmod>{heute}</lastmod></url>" for a in adressen)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{eintraege}</urlset>\n')


def schreiben(pfad: Path, text: str) -> None:
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(text, encoding="utf-8")
