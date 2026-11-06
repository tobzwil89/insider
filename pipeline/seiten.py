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
from pipeline.kennzahlen import DECKEL, KRITERIEN
from pipeline.ranking import schluessel

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


def person_link(name: str, personen: dict | None, wurzel: str) -> str:
    """Name als Link zur Personenseite, wenn es eine gibt (personen: Namensschlüssel → Adresse)."""
    a = personen.get(schluessel(name)) if personen else None
    return f'<a href="{wurzel}person/{a}/">{e(name)}</a>' if a else e(name)


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

def logo_datei(isins: list) -> str | None:
    """Dateiname des Firmenlogos in docs/logos/ (geladen von logos_laden.py) oder None."""
    for isin in isins:
        for datei in sorted((DOCS / "logos").glob(f"{isin}.*")):
            return datei.name
    return None


def firmenlogo(isins: list, name: str, wurzel: str, groesse: str = "") -> str:
    """Logo auf heller Kachel; ohne Logo der Anfangsbuchstabe als Platzhalter."""
    datei = logo_datei(isins)
    if datei:
        return f'<span class="firmenlogo {groesse}"><img src="{wurzel}logos/{e(datei)}" alt="Logo {e(name)}"></span>'
    return f'<span class="firmenlogo {groesse} leer" aria-hidden="true">{e(name[:1].upper())}</span>'


def firmenseite(f: dict, meldungen: pd.DataFrame, ereignisse: pd.DataFrame, ranking: pd.DataFrame,
                letzter_kurs: tuple, v: dict, aktionaere: pd.DataFrame, rueckkaeufe: pd.DataFrame | None = None,
                kennzahlen: dict | None = None, rueck_ohne_meldungen: bool = False,
                ring: dict | None = None, personen: dict | None = None) -> str:
    """f: ticker, name, index, benchmark, isins. ranking: Zeilen dieser Firma mit Spalte 'rang'.
    aktionaere: Zeilen dieser Firma aus stimmrechte.grossaktionaere.
    ring: Argumente für aktionaersring (export.ring_daten); None = kein Ring.
    rueckkaeufe: Zeilen dieser Firma aus rueckkaeufe.jahre; None = Historie noch nicht geladen, Abschnitt fehlt.
    kennzahlen: Zeile aus kennzahlen.csv; None = Abschnitt fehlt.
    rueck_ohne_meldungen: EQS führt für die Firma keine Rückkaufmeldungen → „keine Daten“ statt „keine Rückkäufe“.
    personen: Namensschlüssel → Adresse der Personenseite (Vorstand und Aufsichtsrat), für die Links."""
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
             for r in ereignisse.sort_values("mitteilungsdatum", ascending=False).itertuples()])

    if ranking.empty:
        rk_html = ('<p class="leer">Keine Führungskraft dieser Firma hat mindestens 3 Käufe mit abgeschlossenen '
                   '3 Monaten.</p>')
    else:
        rk_html = _tabelle(
            [("#", "zahl"), ("Person", ""), ("Käufe", "zahl"), ("Typisch (Median)", "zahl"),
             ("Durchschnitt", "zahl"), ("Besser als Index", "zahl"), ("Zeitraum", "")],
            [[(str(r.rang), "zahl"),
              (f'{person_link(r.person, personen, "../../")}<div class="klein">{e(POSITION.get(r.position, r.position))}</div>', ""),
              (str(r.kaeufe), "zahl"), (prozent(r.median), f"zahl {_vorzeichen_klasse(r.median)}"),
              (prozent(r.ueberrendite), "zahl"), (f"{zahl(r.trefferquote * 100)} %", "zahl"),
              (e(f"{r.erster_kauf:%Y}" if r.erster_kauf.year == r.letzter_kauf.year
                 else f"{r.erster_kauf:%Y}–{r.letzter_kauf:%Y}"), "datum")]
             for r in ranking.itertuples()])

    vorzug = ('<p class="erklaerung"><b>An der Börse gehandelt werden nur Vorzugsaktien ohne Stimmrecht.</b> '
              'Die Prozente beziehen sich auf die Stammaktien. Sie werden den Familien Porsche und Piëch über '
              'Beteiligungsgesellschaften und Stimmbindungen vollständig zugerechnet (bei der Porsche AG über '
              'Porsche SE und Volkswagen), deshalb meldet jedes Mitglied die vollen 100 %. Hier stehen sie in einer Zeile.</p>' if f["ticker"] in NUR_VORZUG else "")
    ga_html = aktionaersstruktur(**ring) if ring else ""
    if not ga_html:
        ga_html = ('<p class="leer">Keine Halter über den Meldeschwellen laut den Stimmrechtsmitteilungen '
                   'im EQS-Archiv seit 2018. Das heißt nicht, dass es keine Großaktionäre gibt.</p>')

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
              (f'{person_link(r.person, personen if r.position in ("Vorstand", "Aufsichtsrat") else None, "../../")}'
               f'<div class="klein">{e(POSITION.get(r.position, r.position))}</div>', ""),
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
    seite = f"""<!doctype html>
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

  <div class="kapitel-raster">
  <header class="kopf firmenkopf">
    <div>
      <div class="marke"><a href="../../">← Insider-Monitor</a></div>
      <h1>{e(f['name'])}</h1>
      <p class="unterzeile">{e(f['ticker'])} · {e(f['index'])} · ISIN {e(', '.join(f['isins']))}</p>
    </div>
    {firmenlogo(f['isins'], f['name'], '../../', 'gross')}
  </header>

  <!--KAPITEL-->
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
{fundamental_abschnitt(kennzahlen)}
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
      <h2>Aktionäre</h2>
      <p class="erklaerung">Wem die Aktien gehören, soweit es öffentlich ist. Großaktionäre laut ihrer letzten
        Stimmrechtsmitteilung (§§ 33 ff. WpHG, Meldepflicht ab 3 %, ausgewertet seit 2018 aus dem EQS-Archiv), dazu
        eigene Aktien der Firma, der Norwegische Staatsfonds und US-Fonds (Pflichtmeldungen an die SEC). <b>Gezählt werden
        nur Aktien.</b> Instrumente wie Optionen, Wertpapierleihe oder Derivate sind Rechte auf Aktien, keine Aktien;
        sie stehen klein beim Halter und zählen nicht mit. Einträge mit „geprüft“ haben wir von Hand mit
        veröffentlichten Angaben abgeglichen. Der Rest ist Streubesitz: Anleger unter der Meldeschwelle, deren Namen
        nicht veröffentlicht werden.</p>
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
  </div>

  <script type="application/json" id="daten">{daten_json}</script>
  <script src="../../gemeinsam.js?v={v['gemeinsam.js']}"></script>
  <script src="../../firma.js?v={v['firma.js']}"></script>
</body>
</html>
"""
    return mit_kapiteln(seite)


def mit_kapiteln(seite: str) -> str:
    """Jedem Kapitel (Karte mit Überschrift) eine Sprungmarke geben und daraus die Kapitelleiste bauen."""
    kapitel = []

    def marke(m):
        titel = m[1]
        anker = re.sub(r"[^a-z0-9]+", "-", titel.lower().translate(str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}))).strip("-")
        kapitel.append((anker, titel))
        return f'<section class="karte" id="{anker}">\n      <h2>{titel}</h2>'

    seite = re.sub(r'<section class="karte">\s*<h2>([^<]+)</h2>', marke, seite)
    links = "".join(f'<li><a href="#{a}">{t}</a></li>' for a, t in kapitel)
    return seite.replace("<!--KAPITEL-->", f'<nav class="kapitel" aria-label="Kapitel"><ul>{links}</ul></nav>', 1)


def _prozent_text(x) -> str:
    return f"{zahl(x, 2)} %" if x < 0.1 else f"{zahl(x, 1)} %"


def aktionaersstruktur(aktionaere: pd.DataFrame, eigene: dict | None = None, fonds: dict | None = None,
                       norwegen: dict | None = None, gattung: str | None = None,
                       stamm_aktionaere: pd.DataFrame | None = None) -> str:
    """Ring und eine Tabelle, die zugleich Legende ist: jede Zeile ein Ringsegment, gleiche Zahl, gleiche Farbe.
    Gezählt wird nur der Aktienanteil; Instrumente stehen klein beim Halter. Reihenfolge und Farben (feste Palette,
    --serie-1 … 8): bis zu 4 Großaktionäre ab 1 %, „weitere gemeldete Halter“, eigene Aktien, Norwegischer
    Staatsfonds, US-Fonds (eine Zeile, Aufteilung klein), Rest grau. gattung 'vorzug': Ring über die Vorzugsaktien,
    die Stimmrechte (stamm_aktionaere) stehen als Satz darunter. Nichts bekannt → leerer Text."""
    halter = aktionaere.sort_values("aktien", ascending=False)
    gross = halter[halter["aktien"] >= 1]
    # 8 Farben: Halter ab 1 % einzeln, solange neben den übrigen Segmenten Farben frei sind
    frei = 8 - sum(map(bool, [eigene, norwegen, fonds]))
    if len(gross) + (len(halter) > len(gross)) > frei:
        gross = gross.head(frei - 1)
    klein = halter.drop(gross.index)
    segmente = []  # (Name-HTML, Anteil, Stand-HTML)

    def instrumente(r) -> str:
        return (f'<div class="klein">zusätzlich {_prozent_text(r.instrumente)} über Instrumente, zählen nicht mit</div>'
                if r.instrumente and r.instrumente > 0.005 else "")

    for r in gross.itertuples():
        segmente.append((e(r.halter)
                         + (f'<div class="klein">dieselben Aktien auch bei: {e(r.weitere)}</div>' if r.weitere else "")
                         + instrumente(r), r.aktien,
                         f'<a href="{e(r.url)}" rel="nofollow">{datum(r.schwellendatum)}</a>'
                         + (f'<div class="klein">geprüft {datum(r.geprueft)}</div>' if not _leer(r.geprueft) else "")))
    if not klein.empty:
        liste = "; ".join(f'<a href="{e(r.url)}" rel="nofollow">{e(r.halter)}</a> {_prozent_text(r.aktien)}'
                          + (f" (+ {_prozent_text(r.instrumente)} Instrumente)" if r.instrumente > 0.005 else "")
                          for r in klein.itertuples())
        segmente.append((f'Weitere gemeldete Halter<div class="klein">{liste}</div>', klein["aktien"].sum(), ""))
    if eigene:
        quelle = ("Mitteilung" if str(eigene["url"]).startswith("https://www.eqs-news.com") else "Firmenangabe")
        segmente.append(("Eigene Aktien der Firma", eigene["anteil"],
                         f'<a href="{e(eigene["url"])}" rel="nofollow">{datum(eigene["schwellendatum"])}</a>'
                         f'<div class="klein">{quelle}</div>'))
    if norwegen:
        segmente.append(("Norwegischer Staatsfonds", norwegen["anteil"],
                         f'<a href="https://www.nbim.no/en/investments/all-investments/" rel="nofollow">'
                         f'{datum(norwegen["stichtag"])}</a>'))
    if fonds:
        summe = sum(w for _, w in fonds["teile"]) + fonds["weitere"]
        teile = ", ".join(f"{e(n)} {_prozent_text(w)}" for n, w in fonds["teile"][:4])
        rest = summe - sum(w for _, w in fonds["teile"][:4])
        segmente.append(("US-Fonds<div class=\"klein\">" + teile + (f", weitere {_prozent_text(rest)}" if rest > 0.05 else "")
                         + ("; ohne Konzerne, die oben schon gemeldet sind" if len(gross) or len(klein) else "")
                         + "</div>", summe,
                         f'{datum(fonds["stichtag"])}<div class="klein">Meldungen an die SEC</div>'))
    bekannt, gesehen = 0.0, []
    for name, wert, stand in segmente:
        wert = min(wert, 100 - bekannt)  # Schutz, falls alles zusammen über 100 % ergibt
        if wert > 0.05:
            gesehen.append((name, wert, stand))
            bekannt += wert
    if not gesehen:
        return ""
    rest = 100 - bekannt
    stufen, zeilen, start, luecke = [], [], 0.0, 0.4 if len(gesehen) > 1 or rest > 0.05 else 0
    for i, (name, wert, stand) in enumerate(gesehen):
        farbe = f"var(--serie-{i + 1})"
        stufen.append(f"{farbe} {start:.2f}% {start + max(wert - luecke, 0.2):.2f}%, "
                      f"var(--flaeche) {start + max(wert - luecke, 0.2):.2f}% {start + wert:.2f}%")
        zeilen.append([(f'<div class="ring-name"><span class="ring-farbe" style="background:{farbe}"></span><div>{name}</div></div>', ""),
                       (_prozent_text(wert), "zahl"), (stand, "datum")])
        start += wert
    if rest > 0.05:
        stufen.append(f"var(--ring-rest) {start:.2f}% 100%")
        erklaerung = ("Streubesitz und alle übrigen Anleger (für Vorzugsaktien gibt es keine Stimmrechtsmitteilungen)"
                      if gattung == "vorzug" else "Streubesitz: Anleger unter 3 % (nicht meldepflichtig)"
                      + ("" if eigene else ", eigene Aktien unter 3 %") + (", Fonds außerhalb der USA" if fonds else ""))
        zeilen.append([(f'<div class="ring-name"><span class="ring-farbe" style="background:var(--ring-rest)"></span>'
                        f'<div>Übrige Aktien<div class="klein">{erklaerung}</div></div></div>', ""),
                       (_prozent_text(rest), "zahl"), ("", "datum")])
    titel = {"stamm": "Stammaktien (mit Stimmrecht)", "vorzug": "Vorzugsaktien (ohne Stimmrecht)"}.get(gattung, "Aktien")
    beschreibung = "; ".join(f"{re.sub('<[^>]+>', '', n.split('<div')[0])} {zahl(w, 1)} %" for n, w, _ in gesehen)
    stimmrechte_satz = ""
    if gattung == "vorzug" and stamm_aktionaere is not None and not stamm_aktionaere.empty:
        stimmrechte_satz = ('<p class="erklaerung">Die Stimmrechte liegen bei den Stammaktien: '
                            + ", ".join(f"{e(r.halter)} {_prozent_text(r.aktien)}"
                                        for r in stamm_aktionaere.sort_values("aktien", ascending=False).head(4).itertuples())
                            + ".</p>")
    return (f'<div class="ring-block"><div class="ring" role="img" '
            f'aria-label="{e(titel)}: {e(beschreibung)}; übrige {zahl(rest, 1)} %" '
            f'style="background:conic-gradient({", ".join(stufen)})"><div class="ring-mitte">'
            f'<b>{zahl(bekannt, 0)} %</b><span>mit Namen bekannt</span></div></div>'
            f'<div class="ring-tabelle">'
            + (f'<p class="klein ring-bezug">Anteile bezogen auf die {titel}.</p>' if gattung else "")
            + _tabelle([("Halter", ""), ("Anteil", "zahl"), ("Stand", "")], zeilen)
            + f'</div></div>{stimmrechte_satz}')


# --- Finanzkennzahlen (Planung #6, nur lokal: kennzahlen.csv liegt nicht im Repository) --------------

def _betrag(x, waehrung) -> str:
    if _leer(x):
        return "–"
    zeichen = "€" if waehrung in ("EUR", None) or _leer(waehrung) else waehrung
    return f"{zahl(x / 1e9, 1)} Mrd. {zeichen}" if abs(x) >= 1e9 else f"{zahl(x / 1e6, 1)} Mio. {zeichen}"


def _faktor(x, stellen: int = 1) -> str:
    return "–" if _leer(x) else ("−" if x < 0 else "") + zahl(abs(x), stellen) + "×"


def _liste(titel: str, zeilen: list) -> str:
    dl = "".join(f"<dt>{e(n)}</dt><dd>{w}</dd>" for n, w in zeilen)
    return f'<div class="fk-gruppe"><h3>{e(titel)}</h3><dl>{dl}</dl></div>'


def _balken(titel: str, reihe: dict, waehrung) -> str:
    """Senkrechte Balken je Jahr, Schätzungen („2026e“) heller. reihe: {Jahr: Wert}."""
    werte = [w for w in reihe.values() if not _leer(w)]
    if not werte:
        return ""
    hoch = max(abs(w) for w in werte) or 1
    saeulen = "".join(
        f'<div class="fk-saeule{" schaetzung" if str(j).endswith("e") else ""}{" minus" if w < 0 else ""}" '
        f'title="{e(j)}: {e(_betrag(w, waehrung))}"><div class="fk-balken" style="height:{abs(w) / hoch * 100:.1f}%">'
        f'</div><div class="fk-jahr">{e(str(j)[2:] if len(str(j)) >= 4 else j)}</div></div>'
        for j, w in reihe.items() if not _leer(w))
    return (f'<div class="fk-diagramm"><h3>{e(titel)} <span class="klein">je Geschäftsjahr, helle Säulen = '
            f'Schätzung, höchster Wert {e(_betrag(hoch, waehrung))}</span></h3><div class="fk-saeulen">{saeulen}</div></div>')


KATEGORIE_TEXT = {  # Einteilung nach Peter Lynch, Regeln in kennzahlen.kategorie
    "Schnell wachsend": "Umsatz wächst seit 10 Jahren um mindestens 12 % pro Jahr (Lynch: Fast Grower).",
    "Solide wachsend": "Umsatz wächst um 5 bis 12 % pro Jahr (Lynch: Stalwart).",
    "Langsam wachsend": "Umsatz wächst um weniger als 5 % pro Jahr (Lynch: Slow Grower).",
    "Zykliker": "Operatives Ergebnis ist in 10 Jahren mindestens zweimal um mindestens 40 % eingebrochen (Lynch: Cyclical).",
    "Turnaround": "Verlust im letzten Geschäftsjahr oder in zwei der letzten drei (Lynch: Turnaround).",
    "Substanzwert": "Börsenwert unter 80 % des Buchwerts (Lynch: Asset Play).",
}


def fundamental_abschnitt(k: dict | None) -> str:
    """k: Zeile dieser Firma aus kennzahlen.csv (Reihen als JSON-Text). None → kein Abschnitt."""
    if not k:
        return ""
    w = k["waehrung"]
    finanz = k["finanzwert"] is True or k["finanzwert"] == "True"
    ebit = "EBIT" if k["ebit_reihe"] == "ebit" else "EBITDA"
    pct = lambda x: "–" if _leer(x) else zahl(x * 100, 1) + " %"
    kennzahlen = _liste("Bewertung", [
        ("Börsenwert", _betrag(k["marktkap"], w)), ("KGV (letzte 12 Monate)", zahl(k["kgv_ttm"], 1)),
        ("KGV (Schätzung)", zahl(k["kgv_forward"], 1)), ("KUV", zahl(k["kuv"], 1)), ("KBV", zahl(k["kbv"], 1))])
    rentabilitaet = _liste("Rentabilität", [
        ("Gewinnmarge", pct(k["gewinnmarge"])), ("Eigenkapitalrendite", pct(k["ek_rendite"])),
        ("ROCE", pct(k["roce"])), ("FCF-Rendite", pct(k["fcf_rendite"])),
        ("Dividendenrendite", pct(k["dividendenrendite"]))])
    risiko = _liste("Risiko", [
        ("Nettoverschuldung / EBIT", _faktor(k["verschuldung_ebit"])),
        ("Nettoverschuldung / EBITDA", _faktor(k["verschuldung_ebitda"])),
        (f"Größter {ebit}-Rückgang (10 J.)", pct(k["max_rueckgang_ebit_10j"])),
        ("Jahre mit Gewinn (10 J.)", "–" if _leer(k["gewinnjahre_10j"]) else f"{int(k['gewinnjahre_10j'])} von 10"),
        ("Gewinnanstiege (10 J.)", "–" if _leer(k["gewinnanstiege_10j"]) else f"{int(k['gewinnanstiege_10j'])} von 10")])
    wachstum = _liste("Wachstum pro Jahr", [
        ("Umsatz 10 J.", prozent(k["umsatz_wachstum_10j"])), ("Umsatz 3 J.", prozent(k["umsatz_wachstum_3j"])),
        ("Umsatz nächstes Jahr (Schätzung)", prozent(k["umsatz_wachstum_1je"])),
        (f"{ebit} 10 J.", prozent(k["ebit_wachstum_10j"])),
        ("Gewinn je Aktie 3 J. (Schätzung)", prozent(k["eps_wachstum_3je"])),
        ("Renditeerwartung", prozent(k["renditeerwartung"]) + (
            f'<div class="klein">Wachstum auf {zahl(DECKEL * 100)} % gedeckelt</div>'
            if k["renditeerwartung_gedeckelt"] in (True, "True") else ""))])
    punkte = []
    for schluessel, text, _, _ in KRITERIEN:
        wert = k[schluessel]
        zeichen, klasse = ("–", "offen") if _leer(wert) else ("✓", "ja") if wert in (True, "True") else ("✗", "nein")
        punkte.append(f'<li class="{klasse}"><span>{zeichen}</span>{e(text)}</li>')
    check = (f'<div class="fk-check"><h3>Qualitätscheck: {int(k["q_erfuellt"])} von {int(k["q_bewertbar"])} '
             f'<span class="klein">bewertbaren Kriterien erfüllt</span></h3><ul>{"".join(punkte)}</ul></div>')
    kat = KATEGORIE_TEXT.get(k["kategorie"])
    kategorie = (f'<p class="fk-kategorie"><b>Kategorie: {e(k["kategorie"])}</b> · {e(kat)}</p>' if kat else "")
    balken = _balken("Umsatz", json.loads(k["reihe_umsatz"]), w) + \
        ("" if finanz else _balken(k["reihe_ebit_art"], json.loads(k["reihe_ebit"]), w))
    hinweis = (" <b>Bank oder Versicherung:</b> EBIT, ROCE und Nettoverschuldung sind hier nicht aussagekräftig und fehlen."
               if finanz else "")
    return f"""
    <section class="karte">
      <h2>Finanzkennzahlen</h2>
      <p class="erklaerung">Geschäftsjahr {e(k['letztes_gj'])}, Bewertung zum aktuellen Kurs. Selbst berechnet aus
        TradingView, Eulerpool, onvista und SEC. {e(ebit)}-Werte über 10 Jahre {"aus dem EBIT" if ebit == "EBIT" else
        "aus dem EBITDA, weil das EBIT nur für die letzten Jahre vorliegt"}. Renditeerwartung = erwartetes Wachstum
        des Gewinns je Aktie + Dividendenrendite.{hinweis}</p>
      {kategorie}
      <div class="fk-gruppen">{kennzahlen}{rentabilitaet}{risiko}{wachstum}</div>
      <div class="fk-diagramme">{balken}</div>
      {check}
    </section>
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


def _guru_rahmen(titel: str, beschreibung: str, adresse: str, wurzel: str, kopf: str, inhalt: str, v: dict,
                 quelle: str = "Formular 13F der US-Börsenaufsicht SEC") -> str:
    """Gemeinsames Seitengerüst (Gurus, Personen); wurzel = relativer Weg zur Startseite ('../' oder '../../')."""
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
  <div class="hinweisband">Keine Anlageberatung. Alle Angaben ohne Gewähr, Quelle: {e(quelle)}.</div>
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


# --- Personenseiten (Vorstand und Aufsichtsrat, pipeline/personen.py) ----------------------------------

QUELLE_DD = "BaFin-Datenbank der Eigengeschäfte von Führungskräften, EQS-Archiv"
NUR_EIGENE = ("Enthalten sind eigene Geschäfte und Geschäfte eigener Gesellschaften (Holding, Stiftung), wenn die "
              "Meldung die Person nennt. Geschäfte von Angehörigen stehen nur auf der Firmenseite.")


def _volumen_je_jahr(aktien: pd.DataFrame, geld=euro) -> str:
    """Käufe und Verkäufe je Jahr (Geschäftsdatum) als Säulenpaare. Spalten geschaeftsdatum, art, volumen und
    (falls vorhanden) waehrung: dann nur Euro-Beträge. geld formatiert die Beträge (euro oder dollar)."""
    eur = aktien[aktien["geschaeftsdatum"].notna()]
    if "waehrung" in eur:
        eur = eur[eur["waehrung"].fillna("EUR").eq("EUR")]
    if eur["volumen"].fillna(0).sum() <= 0:
        return '<p class="leer">Keine Volumenangaben.</p>'
    t = (eur.assign(jahr=eur["geschaeftsdatum"].dt.year).pivot_table(index="jahr", columns="art", values="volumen",
                                                                       aggfunc="sum", fill_value=0))
    jahre = range(int(t.index.min()), max(int(t.index.max()), pd.Timestamp.now().year) + 1)
    t = t.reindex(jahre, fill_value=0)
    hoch = max(t.get("Kauf", pd.Series([0])).max(), t.get("Verkauf", pd.Series([0])).max()) or 1
    saeulen = ""
    for jahr, r in t.iterrows():
        balken = "".join(
            f'<div class="jv-balken {art.lower()}" style="height:{r.get(art, 0) / hoch * 100:.1f}%" '
            f'title="{jahr} {e(art)}: {e(geld(r.get(art, 0)))}"></div>'
            for art in ("Kauf", "Verkauf") if r.get(art, 0) > 0)
        saeulen += f'<div class="jv-jahr">{balken}<div class="fk-jahr">{jahr}</div></div>'
    beschreibung = "; ".join(f"{j}: Käufe {geld(r.get('Kauf', 0))}, Verkäufe {geld(r.get('Verkauf', 0))}"
                             for j, r in t.iterrows() if r.sum() > 0)
    return (f'<div class="legende"><span><span class="punkt" style="background:var(--kauf)"></span>Käufe</span>'
            f'<span><span class="punkt" style="background:var(--verkauf)"></span>Verkäufe</span>'
            f'<span class="klein">höchster Wert {e(geld(hoch))}</span></div>'
            f'<div class="jv-saeulen" role="img" aria-label="{e(beschreibung)}">{saeulen}</div>')


def personenseite(p: dict, v: dict) -> str:
    """p: Eintrag aus personen.personen (name, adresse, geschaefte, mandate, ranking, letztes)."""
    g = p["geschaefte"]
    aktien = g[g["instrument"].eq("Aktie")]
    kaeufe, verkaeufe = aktien[aktien["art"].eq("Kauf")], aktien[aktien["art"].eq("Verkauf")]
    eur = lambda x: x.loc[x["waehrung"].fillna("EUR").eq("EUR"), "volumen"].sum()
    letzte = g.loc[g["geschaeftsdatum"].idxmax()] if g["geschaeftsdatum"].notna().any() else g.iloc[0]
    rollen = list(dict.fromkeys(f"{r.position} bei {r.firma}" for r in p["mandate"].itertuples()))

    kacheln = "".join([
        _kachel("Handelsvolumen", euro(eur(kaeufe) + eur(verkaeufe)), "Aktien, Käufe und Verkäufe"),
        _kachel("Käufe", zahl(len(kaeufe)), f"zusammen {euro(eur(kaeufe))}"),
        _kachel("Verkäufe", zahl(len(verkaeufe)), f"zusammen {euro(eur(verkaeufe))}"),
        _kachel("Letztes Geschäft", datum(p["letztes"]), letzte["firma"]),
    ])
    mandate = _tabelle(
        [("Firma", ""), ("Position", ""), ("Meldungen", "zahl"), ("Geschäfte von – bis", "")],
        [[(f'<a href="../../firma/{e(r.ticker)}/">{e(r.firma)}</a>', ""), (e(r.position), ""),
          (zahl(r.meldungen), "zahl"), (f"{datum(r.von)} – {datum(r.bis)}", "datum")]
         for r in p["mandate"].itertuples()])
    timing = ""
    if not p["ranking"].empty:
        timing = """
    <section class="karte">
      <h2>Timing der Käufe</h2>
      <p class="erklaerung">Überrendite gegenüber DAX bzw. MDAX in den 3 Monaten nach den Aktienkäufen, ab 3 Käufen je
        Firma. Der Rang bezieht sich auf alle Insider im DAX und MDAX (<a href="../../">Startseite</a>,
        <a href="../../methode.html#ranking">Methode</a>).</p>
      """ + _tabelle(
            [("Rang", "zahl"), ("Firma", ""), ("Käufe", "zahl"), ("Typisch (Median)", "zahl"), ("Durchschnitt", "zahl"),
             ("Besser als Index", "zahl"), ("Zeitraum", "")],
            [[(str(r.rang), "zahl"), (f'<a href="../../firma/{e(r.ticker)}/">{e(r.name)}</a>', ""),
              (str(r.kaeufe), "zahl"), (prozent(r.median), f"zahl {_vorzeichen_klasse(r.median)}"),
              (prozent(r.ueberrendite), "zahl"), (f"{zahl(r.trefferquote * 100)} %", "zahl"),
              (e(f"{r.erster_kauf:%Y}" if r.erster_kauf.year == r.letzter_kauf.year
                 else f"{r.erster_kauf:%Y}–{r.letzter_kauf:%Y}"), "datum")]
             for r in p["ranking"].itertuples()]) + "\n    </section>"
    geschaefte = _tabelle(
        [("Veröffentlicht", ""), ("Geschäft", ""), ("Firma", ""), ("Art", ""), ("Instrument", ""),
         ("Volumen", "zahl"), ("Kurs", "zahl"), ("Seitdem ggü. Index", "zahl")],
        [[(datum(r.mitteilungsdatum), "datum"), (datum(r.geschaeftsdatum), "datum"),
          (f'<a href="../../firma/{e(r.ticker)}/">{e(r.firma)}</a><div class="klein">{e(r.traeger_position)}'
           + (f" · über {e(r.ueber)}" if r.ueber else "") + "</div>", ""),
          (_art(r.art), ""), (e(r.instrument), ""), (euro(r.volumen, r.waehrung), "zahl"), (zahl(r.preis, 2), "zahl"),
          (prozent(r.seit), f"zahl {_vorzeichen_klasse(r.seit)}")]
         for r in g.itertuples()])

    kopf = (f'<div class="marke"><a href="../">← Alle Insider</a></div><h1>{e(p["name"])}</h1>'
            f'<p class="unterzeile">{e(" · ".join(rollen))} <span class="klein">(laut Meldungen seit 2018)</span></p>')
    inhalt = f"""<div class="kacheln">{kacheln}</div>
    <section class="karte">
      <h2>Handelsvolumen je Jahr</h2>
      <p class="erklaerung">Aktienkäufe und -verkäufe nach Geschäftsdatum, in Euro. {NUR_EIGENE}</p>
      {_volumen_je_jahr(aktien)}
    </section>
    <section class="karte">
      <h2>Firmen</h2>
      <p class="erklaerung">Position zum Zeitpunkt der Meldungen. Ämter ohne Aktiengeschäft tauchen hier nicht auf.</p>
      {mandate}
    </section>{timing}
    <section class="karte">
      <h2>Alle Geschäfte</h2>
      <p class="erklaerung">Teilausführungen am selben Tag sind zusammengefasst. <b>Seitdem ggü. Index</b>: Kursentwicklung
        der Aktie seit dem Schlusskurs am Geschäftstag minus DAX bzw. MDAX, bis zum letzten Schlusskurs (bereinigt um
        Dividenden und Splits). Bei Käufen spricht ein Plus für gutes Timing, bei Verkäufen ein Minus.</p>
      {geschaefte}
    </section>"""
    firmen = ", ".join(dict.fromkeys(p["mandate"]["firma"]))
    return _guru_rahmen(f"{p['name']}: Aktienkäufe und -verkäufe",
                        f"Alle gemeldeten Aktiengeschäfte von {p['name']} ({firmen}) seit 2018: {len(kaeufe)} Käufe, "
                        f"{len(verkaeufe)} Verkäufe, Handelsvolumen je Jahr und Überrendite seit dem Geschäft.",
                        f"person/{p['adresse']}/", "../../", kopf, inhalt, v, QUELLE_DD)


def personen_uebersicht(liste: list, v: dict) -> str:
    zeilen = []
    for p in liste:
        aktien = p["geschaefte"][p["geschaefte"]["instrument"].eq("Aktie")]
        m = p["mandate"]
        weitere = m["firma"].nunique() - 1
        zeilen.append([
            (f'<a href="{e(p["adresse"])}/">{e(p["name"])}</a>', ""),
            (f'{e(m.iloc[0]["position"])} · {e(m.iloc[0]["firma"])}'
             + (f' <span class="klein">+ {weitere} weitere</span>' if weitere else ""), ""),
            (zahl(aktien["art"].eq("Kauf").sum()), "zahl"), (zahl(aktien["art"].eq("Verkauf").sum()), "zahl"),
            (datum(p["letztes"]), "datum")])
    kopf = ('<div class="marke"><a href="../">← Insider-Monitor</a></div><h1>Insider: Vorstände und Aufsichtsräte</h1>'
            f'<p class="unterzeile">{zahl(len(liste))} Personen aus DAX und MDAX mit gemeldeten Geschäften seit 2018.</p>')
    inhalt = ('<section class="karte"><h2>Alle Personen</h2><p class="erklaerung">Sortiert nach dem letzten Geschäft. '
              f'Firma und Position laut der neuesten Meldung. {NUR_EIGENE} Suche mit Strg+F bzw. ⌘+F.</p>'
              + _tabelle([("Person", ""), ("Position · Firma", ""), ("Käufe", "zahl"), ("Verkäufe", "zahl"),
                          ("Letztes Geschäft", "")], zeilen) + "</section>")
    return _guru_rahmen("Insider: Vorstände und Aufsichtsräte im DAX und MDAX",
                        "Aktienkäufe und -verkäufe aller Vorstände und Aufsichtsräte im DAX und MDAX seit 2018, "
                        "je Person auf einer Seite.", "person/", "../", kopf, inhalt, v, QUELLE_DD)


# --- US-Kongress (pipeline/kongress.py, pipeline/politiker.py) ---------------------------------------------

QUELLE_KONGRESS = "Periodic Transaction Reports des US-Repräsentantenhauses (STOCK Act), Clerk of the House"
ERKLAERUNG_KONGRESS = (
    "Abgeordnete des US-Repräsentantenhauses müssen Wertpapiergeschäfte über 1.000 $ binnen 45 Tagen melden, auch die "
    "von Ehepartnern und Kindern (STOCK Act). Gemeldet wird nur eine Betragsspanne, z. B. 1.001–15.000 $; Summen "
    "rechnen mit der Mitte der Spanne und sind deshalb Schätzungen. Noch nicht ausgewertet: Papiermeldungen (Scans) und Meldungen im älteren "
    "Formular (bis Mitte 2022); sie stehen als Links bei den Personen.")


def dollar(x) -> str:
    if _leer(x):
        return "–"
    if abs(x) >= 1e6:
        return f"{zahl(x / 1e6, 1)} Mio. $"
    if abs(x) >= 1e4:
        return f"{zahl(x / 1e3)} Tsd. $"
    return f"{zahl(x)} $"


def _spanne(von, bis) -> str:
    if _leer(von):
        return "–"
    if _leer(bis):
        return f"über {zahl(von)} $"
    return f"{zahl(von)} $" if von == bis else f"{zahl(von)} – {zahl(bis)} $"


# Anlagearten laut House-Formular (fd.house.gov/reference/asset-type-codes.aspx); Aktien (ST) ohne Zusatz
ANLAGEART = {"OP": "Option", "GS": "Staats-/Kommunalanleihe", "CS": "Unternehmensanleihe", "EF": "ETF",
             "MF": "Investmentfonds", "CT": "Krypto", "PS": "Aktie (nicht börsennotiert)", "HN": "Hedgefonds",
             "AB": "Wertpapier mit Sicherheiten", "OI": "Beteiligung", "OT": "Sonstiges"}


def _wertpapier(r) -> str:
    kuerzel = f'<b>{e(r.kuerzel)}</b> ' if r.kuerzel else ""
    art = ANLAGEART.get(getattr(r, "anlageart", ""), "")
    return (f'{kuerzel}<span class="klein">{e(r.wertpapier.replace(f"({r.kuerzel})", "").strip())}'
            + (f' · <b>{e(art)}</b>' if art else "") + "</span>")


def _kongress_art(art: str) -> str:
    """Wie _art, aber Teilverkauf in der Farbe der Verkäufe."""
    farbe = FARBE.get("Verkauf" if art == "Teilverkauf" else art, "var(--sonstiges)")
    return f'<span class="art"><span class="punkt" style="background:{farbe}"></span>{e(art)}</span>'


def politikerseite(p: dict, v: dict) -> str:
    """p: Eintrag aus politiker.politiker (name, partei, bezirk, geschaefte, letztes, meldungen, adresse, scans)."""
    g = p["geschaefte"]
    kauf, verkauf = g[g["art"].eq("Kauf")], g[g["art"].isin(["Verkauf", "Teilverkauf"])]
    kacheln = "".join([
        _kachel("Handelsvolumen", dollar(g["betrag"].sum()), "geschätzt, Mitte der Spannen"),
        _kachel("Käufe", zahl(len(kauf)), f"etwa {dollar(kauf['betrag'].sum())}"),
        _kachel("Verkäufe", zahl(len(verkauf)), f"etwa {dollar(verkauf['betrag'].sum())}"),
        _kachel("Letztes Geschäft", datum(p["letztes"]), f"{zahl(p['meldungen'])} Meldungen"),
    ])
    jahre = g.assign(geschaeftsdatum=g["datum"], volumen=g["betrag"],
                     art=g["art"].replace({"Teilverkauf": "Verkauf"}))
    aktien = g[g["anlageart"].eq("ST") & g["kuerzel"].ne("")]
    top = (aktien.groupby("kuerzel").agg(wertpapier=("wertpapier", "first"), kaeufe=("art", lambda x: x.eq("Kauf").sum()),
                                         verkaeufe=("art", lambda x: x.isin(["Verkauf", "Teilverkauf"]).sum()),
                                         betrag=("betrag", "sum"), letztes=("datum", "max"))
           .sort_values("betrag", ascending=False).head(10).reset_index())
    top_html = _tabelle(
        [("Aktie", ""), ("Käufe", "zahl"), ("Verkäufe", "zahl"), ("Volumen (geschätzt)", "zahl"), ("Zuletzt", "")],
        [[(_wertpapier(r), ""), (zahl(r.kaeufe), "zahl"), (zahl(r.verkaeufe), "zahl"), (dollar(r.betrag), "zahl"),
          (datum(r.letztes), "datum")] for r in top.itertuples()]) if len(top) else '<p class="leer">Keine Aktien.</p>'
    geschaefte = _tabelle(
        [("Gemeldet", ""), ("Geschäft", ""), ("Wertpapier", ""), ("Art", ""), ("Inhaber", ""), ("Betrag", "zahl"),
         ("Seitdem ggü. S&P 500", "zahl")],
        [[(f'<a href="{e(r.url)}" rel="nofollow">{datum(r.eingereicht)}</a>', "datum"), (datum(r.datum), "datum"),
          (_wertpapier(r) + (f'<div class="klein">{e(r.beschreibung)}</div>' if r.beschreibung else ""), ""),
          (_kongress_art(r.art), ""), (e(r.inhaber), ""), (_spanne(r.betrag_von, r.betrag_bis), "zahl"),
          (prozent(r.seit), f"zahl {_vorzeichen_klasse(r.seit)}")]
         for r in g.itertuples()])
    scans = p.get("scans")
    scan_html = ""
    if scans is not None and len(scans):
        scan_html = ('<p class="erklaerung">Außerdem ' + zahl(len(scans)) + ' weitere Meldung(en), noch nicht ausgewertet (Papier oder älteres Formular): '
                     + ", ".join(f'<a href="{e(s.url)}" rel="nofollow">{datum(s.eingereicht)}</a>'
                                 for s in scans.itertuples()) + ".</p>")
    kopf = (f'<div class="marke"><a href="../">← US-Kongress</a></div><h1>{e(p["name"])}</h1>'
            f'<p class="unterzeile">{e(p["partei"])} · Repräsentantenhaus · {e(p["bezirk"])}</p>')
    inhalt = f"""<div class="kacheln">{kacheln}</div>
    <section class="karte">
      <h2>Handelsvolumen je Jahr</h2>
      <p class="erklaerung">Käufe und Verkäufe aller Wertpapiere nach Geschäftsdatum, geschätzt aus der Mitte der
        gemeldeten Spannen. {e(ERKLAERUNG_KONGRESS)}</p>
      {_volumen_je_jahr(jahre, dollar)}
    </section>
    <section class="karte">
      <h2>Meistgehandelte Aktien</h2>
      {top_html}
    </section>
    <section class="karte">
      <h2>Alle Geschäfte</h2>
      <p class="erklaerung">Neueste zuerst; das Datum „Gemeldet“ führt zur Originalmeldung. Inhaber: selbst, Ehepartner,
        gemeinsam oder Kind. <b>Seitdem ggü. S&amp;P 500</b>: Kursentwicklung der Aktie seit dem Schlusskurs am
        Geschäftstag minus S&amp;P 500, bis zum letzten Schlusskurs (Yahoo, bereinigt). Bei Käufen spricht ein Plus für
        gutes Timing, bei Verkäufen ein Minus. Optionen und Anleihen ohne Wert.</p>
      {scan_html}{geschaefte}
    </section>"""
    return _guru_rahmen(f"{p['name']}: Aktiengeschäfte", f"Alle gemeldeten Wertpapiergeschäfte von {p['name']} "
                        f"({p['partei']}, {p['bezirk']}) laut STOCK Act: Käufe, Verkäufe, Volumen je Jahr und "
                        "Überrendite seit dem Geschäft.", f"politiker/{p['adresse']}/", "../../", kopf, inhalt, v,
                        QUELLE_KONGRESS)


def politiker_uebersicht(liste: list, neueste: pd.DataFrame, v: dict) -> str:
    """liste: politiker.politiker(…); neueste: die letzten Geschäfte aller Abgeordneten (mit Spalte adresse)."""
    zeilen = [[(f'<a href="{e(p["adresse"])}/">{e(p["name"])}</a><div class="klein">{e(p["partei"])} · '
                f'{e(p["bezirk"])}</div>', ""), (zahl(len(p["geschaefte"])), "zahl"),
               (dollar(p["geschaefte"]["betrag"].sum()), "zahl"), (datum(p["letztes"]), "datum")] for p in liste]
    letzte = _tabelle(
        [("Gemeldet", ""), ("Geschäft", ""), ("Abgeordnete(r)", ""), ("Wertpapier", ""), ("Art", ""),
         ("Betrag", "zahl")],
        [[(f'<a href="{e(r.url)}" rel="nofollow">{datum(r.eingereicht)}</a>', "datum"), (datum(r.datum), "datum"),
          (f'<a href="{e(r.adresse)}/">{e(r.politiker)}</a><div class="klein">{e(r.partei)}</div>', ""),
          (_wertpapier(r), ""), (_kongress_art(r.art), ""), (_spanne(r.betrag_von, r.betrag_bis), "zahl")]
         for r in neueste.itertuples()])
    kopf = ('<div class="marke"><a href="../">← Insider-Monitor</a></div><h1>Aktiengeschäfte im US-Kongress</h1>'
            f'<p class="unterzeile">{zahl(len(liste))} Abgeordnete des Repräsentantenhauses mit gemeldeten Geschäften.</p>')
    inhalt = (f'<section class="karte"><h2>Neueste Geschäfte</h2><p class="erklaerung">{e(ERKLAERUNG_KONGRESS)}</p>'
              f'{letzte}</section><section class="karte"><h2>Alle Abgeordneten</h2><p class="erklaerung">Sortiert nach '
              'dem letzten Geschäft. Suche mit Strg+F bzw. ⌘+F.</p>'
              + _tabelle([("Abgeordnete(r)", ""), ("Geschäfte", "zahl"), ("Volumen (geschätzt)", "zahl"),
                          ("Letztes Geschäft", "")], zeilen) + "</section>")
    return _guru_rahmen("Aktiengeschäfte im US-Kongress", "Aktienkäufe und -verkäufe der Abgeordneten des "
                        "US-Repräsentantenhauses laut STOCK Act, je Person mit Volumen und Timing.", "politiker/", "../",
                        kopf, inhalt, v, QUELLE_KONGRESS)


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
