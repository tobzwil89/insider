"""Directors' Dealings aus dem Archiv von EQS News (früher DGAP), für die Zeit vor den BaFin-Daten.

Die BaFin zeigt nur 12 Monate. EQS verbreitet die Pflichtmeldungen der meisten deutschen
Emittenten und hält sie seit Jahren vor. Jede Meldung folgt dem einheitlichen MAR-Formular;
daraus werden dieselben Spalten gelesen wie aus der BaFin-CSV, plus Uhrzeit der
Veröffentlichung und bei eng verbundenen Personen die zugehörige Führungskraft.

Höflich abrufen: Pause zwischen Anfragen. EQS drosselt still, indem es leere Antworten mit
Status 200 schickt. Deshalb wird eine leere Antwort, die eigentlich Inhalt haben müsste,
nach Wartezeiten wiederholt (WARTEN) statt als Ende gewertet.
"""

import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

AJAX = "https://www.eqs-news.com/wp/wp-admin/admin-ajax.php?lang=de"
SUCHE = "https://www.eqs-news.com/de/search-results/"
HEADER = {"User-Agent": "Mozilla/5.0 (insider.tobiaszwilling.me; tobzwilling@gmx.de)"}
PAUSE = 2.0
WARTEN = [30, 60, 120, 240]  # Sekunden zwischen Wiederholungen nach einer leeren Antwort


class Gedrosselt(Exception):
    """EQS liefert trotz Wiederholungen keinen Inhalt."""
MONATE = {m: i for i, m in enumerate(["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
                                       "September", "Oktober", "November", "Dezember"], 1)}


def _holen(url, **params) -> str:
    for versuch in range(3):
        try:
            antwort = requests.get(url, params=params or None, headers=HEADER, timeout=60)
            antwort.raise_for_status()
            time.sleep(PAUSE)
            return antwort.text
        except requests.RequestException:
            time.sleep(10 * (versuch + 1))
    raise RuntimeError(f"EQS nicht erreichbar: {url}")


def firma_uuid(isin: str) -> str | None:
    """EQS-ID einer Firma. Ohne Treffer wird gewartet und wiederholt, weil auch die Suche gedrosselt wird."""
    for warten in WARTEN[:3]:
        treffer = re.findall(r"company/[a-z0-9\-]+/news/([0-9a-f\-]{36})",
                             _holen(SUCHE, searchtype="company", searchword=isin))
        if treffer:
            return treffer[0]
        time.sleep(warten)
    return None


def _listenseite(uuid: str, seite: int) -> str:
    return _holen(AJAX, action="fetch_eqs_financial_news_data", pageLimit=30, pageNo=seite,
                  loadFrom="mysql", companyId=uuid, companyName=uuid, parseBy="newsgrouping")


def _seite(uuid: str, seite: int) -> str:
    """Listenseite; leer nur, wenn die Liste wirklich zu Ende ist.
    Seite 1 hat immer Inhalt: Ist auch sie leer, drosselt EQS gerade, also warten."""
    for warten in WARTEN:
        html = _listenseite(uuid, seite)
        if html.strip():
            return html
        if seite > 1 and _listenseite(uuid, 1).strip():
            return _listenseite(uuid, seite)  # EQS antwortet wieder: zweite Chance, sonst echtes Ende
        time.sleep(warten)
    raise Gedrosselt(f"EQS liefert für {uuid} keine Nachrichtenliste")


def dd_links(uuid: str, ab: pd.Timestamp, bis: pd.Timestamp | None = None,
             kategorie: str = "directors-dealings") -> list:
    """(URL, Titel) aller Meldungen einer Kategorie (Teil der Adresse, z. B. 'stimmrechtsanteile')
    einer Firma von `ab` bis `bis` (neueste zuerst). Standard: Directors' Dealings."""
    links, seite, datum = [], 1, None
    while True:
        html = _seite(uuid, seite)
        if not html.strip():
            return links
        for knoten in BeautifulSoup(html, "lxml").select("[data-financial-news-date-grouped], a[data-financial-news-item]"):
            if knoten.name == "p":
                t, m, j = knoten.get_text(strip=True).split()
                datum = pd.Timestamp(int(j), MONATE[m], int(t))
            elif datum >= ab and (bis is None or datum <= bis) and f"/news/{kategorie}/" in knoten["href"]:
                titel = knoten.select_one(".news__heading")
                links.append((knoten["href"], titel.get_text(strip=True) if titel else ""))
        if datum is not None and datum < ab:
            return links
        seite += 1


def nur_zuteilung(titel: str) -> bool:
    """True, wenn der Titel eindeutig kein Kauf oder Verkauf ist (z. B. '…, Zuteilung').
    Ältere Titel wie 'DGAP-DD: SAP SE deutsch' nennen die Art nicht; die werden geladen."""
    rest = titel.split(": ", 1)[-1]  # Titel: "Firma: Person, Art des Geschäfts"
    if "," not in rest or titel.startswith(("DGAP-DD", "EQS-DD")):
        return False
    art = rest.split(",", 1)[1]
    return "Kauf" not in art and "Verkauf" not in art


def _zahl(text: str) -> float | None:
    """'1.234,50 EUR', '2250,00 EUR' oder '125.5 EUR' → float."""
    roh = text.split()[0] if text else ""
    if "," in roh:
        roh = roh.replace(".", "").replace(",", ".")
    try:
        return float(roh)
    except ValueError:
        return None


def _datum(text: str) -> str | None:
    """'19.10.2026; UTC+2' oder '2021-08-16; UTC+2' → '2026-10-19'."""
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})|(\d{2})\.(\d{2})\.(\d{4})", text or "")
    if not m:
        return None
    return f"{m[1]}-{m[2]}-{m[3]}" if m[1] else f"{m[6]}-{m[5]}-{m[4]}"


def _aggregiert(block: list) -> tuple:
    """Preis und Volumen aus 'd) Aggregierte Informationen'. Neuere Meldungen schreiben
    '17,2105 EUR' in eine Zeile, ältere (bis 2020) Betrag und Währung in getrennte Zeilen."""
    if "d) Aggregierte Informationen" not in block:
        return "", ""
    i = block.index("d) Aggregierte Informationen") + 1
    ende = next((j for j in range(i, len(block)) if block[j].startswith("e) ")), len(block))
    text = " ".join(z for z in block[i:ende] if z not in ("Preis", "Aggregiertes Volumen"))
    werte = re.findall(r"(\d[\d.,]*)\s*([A-Z][A-Za-z]{2})?", text)  # auch "GBp" (Pence)
    werte = [f"{zahl} {waehrung}".strip() for zahl, waehrung in werte[:2]]
    return tuple((werte + ["", ""])[:2])


def _nach(zeilen: list, marke: str, start: int = 0) -> str:
    """Erste Zeile nach der Zeile `marke` (ab Position `start`)."""
    for i in range(start, len(zeilen) - 1):
        if zeilen[i] == marke:
            return zeilen[i + 1]
    return ""


def _person(zeilen: list) -> str:
    """'Nachname, Titel Vorname' wie bei der BaFin, oder Name einer juristischen Person."""
    if "Name und Rechtsform:" in zeilen[:8]:
        return _nach(zeilen, "Name und Rechtsform:")
    titel, vorname, nachname = (_nach(zeilen, k) for k in ("Titel:", "Vorname:", "Nachname(n):"))
    if titel in ("Vorname:", "Nachname(n):"):
        titel = ""
    return f"{nachname}, {(titel + ' ') if titel else ''}{vorname}".strip(", ")


def _position(text: str) -> str:
    if "Aufsichtsrat" in text:
        return "Aufsichtsrat"
    if "Vorstand" in text:
        return "Vorstand"
    return "Sonstige Führungsperson"


def meldung_lesen(url: str, html: str | None = None) -> list:
    """Eine EQS-Meldung → Liste von Geschäften (meist eins) im Format von meldungen.csv."""
    soup = BeautifulSoup(html or _holen(url), "lxml")
    for t in soup(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    text = soup.get_text("\n", strip=True)
    anfang, ende = text.find("1. Angaben zu den Personen"), text.find("Ende der Mitteilung")
    if anfang < 0:
        # Echte Meldung in anderem Formular (z. B. englisch/luxemburgisch): nicht unterstützt
        if "Für den Inhalt der Mitteilung" in text or "The issuer is solely responsible" in text:
            return []
        raise Gedrosselt(f"Meldung ohne Inhalt: {url}")
    kopf = text[max(0, anfang - 400): anfang]
    zeilen = text[anfang: ende if ende > 0 else None].split("\n")
    zeit = re.search(r"(\d{2})\.(\d{2})\.(\d{4}) / (\d{2}:\d{2})", kopf)
    veroeffentlicht = f"{zeit[3]}-{zeit[2]}-{zeit[1]} {zeit[4]}:00" if zeit else None

    i_grund = zeilen.index("2. Grund der Meldung") if "2. Grund der Meldung" in zeilen else 0
    i_emittent = next((i for i, z in enumerate(zeilen) if z.startswith("3. Angaben zum Emittenten")), i_grund)
    grund = zeilen[i_grund:i_emittent]
    eng = "Person steht in enger Beziehung zu:" in grund
    bezug = _person(grund) if eng else ""
    position = _position(_nach(grund, "Position:"))

    basis = {
        "emittent": _nach(zeilen, "a) Name", i_emittent), "person": _person(zeilen[:i_grund]),
        "position": "in enger Beziehung" if eng else position,
        "bezug_person": bezug, "bezug_position": position if eng else "",
        "korrektur": "Korrekturmeldung" in " ".join(grund),
        "mitteilungsdatum": veroeffentlicht[:10] if veroeffentlicht else None,
        "aktiviert": veroeffentlicht, "quelle": "eqs", "url": url,
    }
    # Abschnitt 4 kann mehrere Geschäfte enthalten; jedes beginnt mit "a) Beschreibung des Finanzinstruments"
    starts = [i for i, z in enumerate(zeilen) if z.startswith("a) Beschreibung des Finanzinstruments")]
    geschaefte = []
    for n, s in enumerate(starts):
        block = zeilen[s: starts[n + 1] if n + 1 < len(starts) else len(zeilen)]
        art_text = _nach(block, "b) Art des Geschäfts")
        preis_text, volumen_text = _aggregiert(block)
        geschaefte.append(dict(basis,
            instrument=_nach(block, "Art:"), isin=_nach(block, "ISIN:"),
            art=art_text if art_text in ("Kauf", "Verkauf") else "Sonstiges", art_text=art_text,
            preis_text=preis_text, volumen_text=volumen_text,
            preis=_zahl(preis_text), volumen=_zahl(volumen_text),
            waehrung=(preis_text.split() + [""])[1] if preis_text else "",
            geschaeftsdatum=_datum(_nach(block, "e) Datum des Geschäfts")),
            ort=_nach(block, "Name:", block.index("f) Ort des Geschäfts")) if "f) Ort des Geschäfts" in block else ""))
    return geschaefte
