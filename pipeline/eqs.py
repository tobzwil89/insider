"""Directors' Dealings aus dem Archiv von EQS News (früher DGAP), für die Zeit vor den BaFin-Daten.

Die BaFin zeigt nur 12 Monate. EQS verbreitet die Pflichtmeldungen der meisten deutschen
Emittenten und hält sie seit Jahren vor. Jede Meldung folgt dem einheitlichen MAR-Formular;
daraus werden dieselben Spalten gelesen wie aus der BaFin-CSV, plus Uhrzeit der
Veröffentlichung und bei eng verbundenen Personen die zugehörige Führungskraft.

Höflich abrufen: eine Anfrage pro Sekunde.
"""

import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

AJAX = "https://www.eqs-news.com/wp/wp-admin/admin-ajax.php?lang=de"
SUCHE = "https://www.eqs-news.com/de/search-results/"
HEADER = {"User-Agent": "Mozilla/5.0 (insider.tobiaszwilling.me; tobzwilling@gmx.de)"}
PAUSE = 1.0
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
    treffer = re.findall(r"company/[a-z0-9\-]+/news/([0-9a-f\-]{36})",
                         _holen(SUCHE, searchtype="company", searchword=isin))
    return treffer[0] if treffer else None


def dd_links(uuid: str, ab: pd.Timestamp, bis: pd.Timestamp | None = None) -> list:
    """(URL, Titel) aller Directors'-Dealings-Meldungen einer Firma von `ab` bis `bis` (neueste zuerst)."""
    links, seite, datum = [], 1, None
    while True:
        html = _holen(AJAX, action="fetch_eqs_financial_news_data", pageLimit=30, pageNo=seite,
                      loadFrom="mysql", companyId=uuid, companyName=uuid, parseBy="newsgrouping")
        if not html.strip():
            return links
        for knoten in BeautifulSoup(html, "lxml").select("[data-financial-news-date-grouped], a[data-financial-news-item]"):
            if knoten.name == "p":
                t, m, j = knoten.get_text(strip=True).split()
                datum = pd.Timestamp(int(j), MONATE[m], int(t))
            elif datum >= ab and (bis is None or datum <= bis) and "/news/directors-dealings/" in knoten["href"]:
                titel = knoten.select_one(".news__heading")
                links.append((knoten["href"], titel.get_text(strip=True) if titel else ""))
        if datum is not None and datum < ab:
            return links
        seite += 1


def nur_zuteilung(titel: str) -> bool:
    """True, wenn der Titel eindeutig kein Kauf oder Verkauf ist (z. B. '…, Zuteilung').
    Ältere Titel wie 'DGAP-DD: SAP SE deutsch' nennen die Art nicht; die werden geladen."""
    if "," not in titel or titel.startswith(("DGAP-DD", "EQS-DD")):
        return False
    art = titel.rsplit(",", 1)[1].strip()
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
        return []
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
        i_agg = block.index("d) Aggregierte Informationen") if "d) Aggregierte Informationen" in block else -1
        werte = block[i_agg + 3: i_agg + 5] if i_agg >= 0 else ["", ""]
        preis_text, volumen_text = (werte + ["", ""])[:2]
        geschaefte.append(dict(basis,
            instrument=_nach(block, "Art:"), isin=_nach(block, "ISIN:"),
            art=art_text if art_text in ("Kauf", "Verkauf") else "Sonstiges", art_text=art_text,
            preis_text=preis_text, volumen_text=volumen_text,
            preis=_zahl(preis_text), volumen=_zahl(volumen_text),
            waehrung=(preis_text.split() + [""])[1] if preis_text else "",
            geschaeftsdatum=_datum(_nach(block, "e) Datum des Geschäfts")),
            ort=_nach(block, "Name:", block.index("f) Ort des Geschäfts")) if "f) Ort des Geschäfts" in block else ""))
    return geschaefte
