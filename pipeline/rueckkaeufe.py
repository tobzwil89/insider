"""Aktienrückkäufe (Art. 5 MAR) aus EQS News lesen.

Firmen, die eigene Aktien zurückkaufen, melden mindestens wöchentlich je Handelstag Stückzahl und
Durchschnittskurs. Ein einheitliches Formular gibt es nicht: Das Datum steht als '2026-10-19',
'19.10.2026', '04/05/2026' oder '16. März 2018' da, manche Firmen geben je Handelsplatz eine Zeile an,
alte Meldungen (bis ~2019) sind Text mit festen Spaltenbreiten. Gelesen wird deshalb jede Folge
„Datum, Stückzahl, Kurs“ im Meldungstext; mehrere Zeilen desselben Tages werden zusammengezählt.

Selbstkontrolle: Fast jede Meldung nennt die Gesamtzahl im Text („insgesamt 42.848 Aktien“). Sie wird
als `stueck_text` gespeichert und muss zur Summe der gelesenen Tage passen.

Andere Meldungen derselben Kategorie (Anleihen, Ankündigungen eines Programms, Sonstiges) werden mit
art="anderes" gespeichert, damit sie nicht bei jedem Lauf neu geladen werden.
"""

import re

import pandas as pd
from bs4 import BeautifulSoup

from pipeline import eqs

KATEGORIE = "sonstige-kapitalmarktinformationen"
MONATE = {**eqs.MONATE, "Jänner": 1, **{m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
     "November", "December"], 1)}, **{m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}}
DATUM = re.compile(r"(\d{4})-(\d{2})-(\d{2})|(\d{1,2})[./](\d{1,2})[./](\d{4})|(\d{1,2})\.? ?([A-Za-zäÄ]+)\.? (\d{4})")
STUECK = re.compile(r"\d{1,3}(?:[.,' ]\d{3})+|\d+")
KURS = re.compile(r"(?:€|EUR)? ?(\d{1,3}(?:[.,]\d{3})*[.,]\d{1,6}|\d+)(?: ?(?:€|EUR))?")
# Heidelberg Materials nennt die Verordnung nicht, nur „Aktienrückkaufprogramm“
RUECKKAUF = re.compile(r"596/2014|2016/1052|rückkauf|buy-?back|repurchase", re.I)
INSGESAMT = re.compile(r"(?:insgesamt|a total of|eine Anzahl von)(?: Stück)? ([\d.,]+) (?:Stück |eigene )?(?:Aktien|shares)", re.I)


def _datum(text: str) -> pd.Timestamp | None:
    m = DATUM.fullmatch(text)
    if not m:
        return None
    if m[1]:
        j, mo, t = int(m[1]), int(m[2]), int(m[3])
    elif m[4]:
        t, mo, j = int(m[4]), int(m[5]), int(m[6])
    elif m[8] in MONATE:
        t, mo, j = int(m[7]), MONATE[m[8]], int(m[9])
    else:
        return None
    try:
        return pd.Timestamp(j, mo, t)
    except ValueError:
        return None


def _stueck(text: str) -> int | None:
    return int(re.sub(r"\D", "", text)) if STUECK.fullmatch(text) else None


def _kurs(text: str) -> float | None:
    """'193,82' / '25.6666' / '€40,6507' / '1.734,50' → float. Das letzte Trennzeichen ist das Komma."""
    m = KURS.fullmatch(text.strip())
    if not m:
        return None
    zahl = m[1]
    letztes = max(zahl.rfind(","), zahl.rfind("."))
    if letztes < 0:
        return float(zahl)
    return float(re.sub(r"\D", "", zahl[:letztes]) + "." + zahl[letztes + 1:])


def _teile(text: str) -> list:
    """Meldungstext → einzelne Zellen: Zeilenumbrüche und alte Spalten (2+ Leerzeichen) trennen."""
    # Zahl-Datum am Zeilenanfang abtrennen, auch wenn nur ein Leerzeichen folgt ('14.06.2019 115.766')
    text = re.sub(r"(?m)^\s*(\d{1,2}[./]\d{1,2}[./]\d{4}|\d{4}-\d{2}-\d{2}) ", r"\1\n", text)
    return [t.strip() for z in text.split("\n") for t in re.split(r"\s{2,}|\t", z) if t.strip()]


def tage(text: str) -> list:
    """Alle Folgen Datum → Stückzahl → Kurs, je Tag zusammengefasst: [(datum, stueck, kurs), …]."""
    zellen = _teile(text)
    gefunden = {}
    for i in range(len(zellen) - 2):
        datum = _datum(zellen[i])
        if datum is None:
            continue
        stueck, kurs = _stueck(zellen[i + 1]), _kurs(zellen[i + 2])
        if stueck is None or kurs is None or stueck == 0:
            continue
        s, v = gefunden.get(datum, (0, 0.0))
        gefunden[datum] = (s + stueck, v + stueck * kurs)
    return [(d, s, round(v / s, 4)) for d, (s, v) in sorted(gefunden.items())]


def lesen(url: str, html: str | None = None) -> list:
    """Eine Meldung → Zeilen für rueckkaeufe.csv: je Rückkauftag eine Zeile, sonst eine Zeile art='anderes'."""
    soup = BeautifulSoup(html or eqs._holen(url), "lxml")
    for t in soup(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    text = soup.get_text("\n", strip=True)
    anfang = max(text.find("Für den Inhalt der Mitteilung"), text.find("The issuer is solely responsible"))
    if anfang < 0:
        raise eqs.Gedrosselt(f"Meldung ohne Inhalt: {url}")
    zeit = re.search(r"(\d{2})\.(\d{2})\.(\d{4})(?: /)? (\d{2}:\d{2})", text[max(0, anfang - 400): anfang])
    ende = text.find("Ende der Mitteilung", anfang)
    text = text[anfang: ende if ende > 0 else None]
    veroeffentlicht = f"{zeit[3]}-{zeit[2]}-{zeit[1]} {zeit[4]}:00" if zeit else ""

    gefunden = tage(text) if RUECKKAUF.search(text) else []
    if not gefunden:
        return [{"url": url, "veroeffentlicht": veroeffentlicht, "art": "anderes"}]
    # letzte Nennung: Schlussmeldungen nennen zuerst die ganze Tranche, danach die Woche (Brenntag 06.03.2024)
    insgesamt = INSGESAMT.findall(re.sub(r"\s+", " ", text))
    return [{"url": url, "veroeffentlicht": veroeffentlicht, "art": "rueckkauf", "datum": d, "stueck": s,
             "kurs": k, "stueck_text": re.sub(r"\D", "", insgesamt[-1]) if insgesamt else ""}
            for d, s, k in gefunden]


# --- Auswertung für die Firmenseiten -------------------------------------------------------------

def jahre(df: pd.DataFrame) -> pd.DataFrame:
    """Rückkäufe je Firma und Jahr: Handelstage, Stück, Volumen (Stück × Kurs), Ø Kurs, letzter Rückkauftag.
    Ein Tag zählt einmal, auch wenn er in zwei Meldungen steht (Korrektur, Schluss- und Zwischenmeldung)."""
    r = df[df["art"].eq("rueckkauf")].drop_duplicates(["firma", "datum", "stueck", "kurs"])
    r = r.assign(datum=pd.to_datetime(r["datum"]), volumen=r["stueck"] * r["kurs"])
    j = r.groupby(["firma", r["datum"].dt.year.rename("jahr")]).agg(
        tage=("datum", "nunique"), stueck=("stueck", "sum"), volumen=("volumen", "sum"), letzter=("datum", "max"))
    return j.assign(kurs=j["volumen"] / j["stueck"]).reset_index().sort_values(["firma", "jahr"], ascending=[True, False])
