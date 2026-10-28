"""Stimmrechtsmitteilungen (§§ 33 ff. WpHG) aus EQS News lesen.

Wer 3, 5, 10, 15, 20, 25, 30, 50 oder 75 % der Stimmrechte einer Firma über- oder unterschreitet,
muss das melden. Die Mitteilung folgt einem einheitlichen Formular mit nummerierten Abschnitten,
auf Deutsch oder Englisch. Gelesen werden Abschnitt 3 (wer), 5 (Datum der Schwellenberührung) und
6 (Anteile neu und laut letzter Mitteilung: Aktien, Instrumente, Summe).

Andere Formulare in derselben Kategorie (z. B. „Erwerb oder Veräußerung eigener Aktien“) werden
mit formular="anderes" und leeren Werten gespeichert, damit sie nicht bei jedem Lauf neu geladen werden.
"""

import re

import pandas as pd
from bs4 import BeautifulSoup

from pipeline import eqs

KATEGORIE = "stimmrechtsanteile"
NEU = ("neu", "New", "Resulting situation")
LETZTE = ("letzte Mitteilung", "Previous notification")


def _prozent(text: str) -> float | None:
    """'5,004 %', '5.10 %', 'n/a %' oder '%' → 5.004, 5.1, None, None."""
    roh = text.replace("%", "").strip().replace(",", ".")
    try:
        return float(roh)
    except ValueError:
        return None


def _abschnitt(zeilen: list, nummer: str) -> int:
    """Index der Zeile, mit der Abschnitt `nummer` beginnt (z. B. '3. '), sonst -1."""
    return next((i for i, z in enumerate(zeilen) if z.startswith(nummer)), -1)


def _wert(zeilen: list, i: int) -> str:
    """Text hinter 'Bezeichnung: Wert' oder, wenn die Zeile mit ':' endet, die nächste Zeile."""
    if i < 0 or i >= len(zeilen):
        return ""
    z = zeilen[i]
    if z.endswith(":"):
        return zeilen[i + 1] if i + 1 < len(zeilen) else ""
    return z.split(":", 1)[1].strip() if ":" in z else z


def _reparieren(zeile: str) -> str:
    """Doppelt kodierten Text zurückwandeln: 'VerÃ¶ffentlichung' → 'Veröffentlichung'.
    Kommt bei einzelnen EQS-Seiten vor (z. B. Auto1, 05.02.2021); der Seitenkopf ist dort korrekt."""
    if "Ã" not in zeile and "Â" not in zeile:
        return zeile
    try:
        return zeile.encode("latin-1").decode("utf-8")
    except UnicodeError:
        return zeile


def lesen(url: str, html: str | None = None) -> dict:
    """Eine Stimmrechtsmitteilung → eine Zeile für stimmrechte.csv."""
    soup = BeautifulSoup(html or eqs._holen(url), "lxml")
    for t in soup(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    text = "\n".join(map(_reparieren, soup.get_text("\n", strip=True).split("\n")))
    anfang = max(text.find("Für den Inhalt der Mitteilung"), text.find("The issuer is solely responsible"))
    if anfang < 0:
        raise eqs.Gedrosselt(f"Meldung ohne Inhalt: {url}")
    zeit = re.search(r"(\d{2})\.(\d{2})\.(\d{4}) / (\d{2}:\d{2})", text[max(0, anfang - 400): anfang])
    zeile = {"url": url, "veroeffentlicht": f"{zeit[3]}-{zeit[2]}-{zeit[1]} {zeit[4]}:00" if zeit else "",
             "korrektur": "Korrektur" in text[max(0, anfang - 600): anfang]}

    zeilen = [re.sub(r"\s+", " ", z).strip() for z in text[anfang:].split("\n")]
    i3, i4, i5, i6, i7 = (_abschnitt(zeilen, f"{n}. ") for n in range(3, 8))
    i_neu = next((i for i in range(i6, i7) if zeilen[i] in NEU), -1) if 0 <= i6 < i7 else -1
    if min(i3, i4, i5, i_neu) < 0:
        return dict(zeile, formular="anderes")

    i_letzte = next((i for i in range(i_neu, i7) if zeilen[i] in LETZTE), -1)
    neu = zeilen[i_neu + 1: i_neu + 5]
    letzte = zeilen[i_letzte + 1: i_letzte + 4] if i_letzte >= 0 else ["", "", ""]
    sitz = next((i for i in range(i3 + 2, i4) if zeilen[i].startswith(("Registrierter Sitz", "City of registered"))), -1)
    wer = _wert(zeilen, i3 + 1)
    if zeilen[i3 + 1].startswith(("Natürliche Person", "Natural person")) and zeilen[i3 + 1].endswith(":") \
            and i3 + 3 < i4 and not zeilen[i3 + 3].endswith(":"):
        wer += " " + zeilen[i3 + 3]  # Vorname und Nachname in getrennten Zeilen
    if wer.endswith(":"):  # altes Formular (bis 2017): Name verteilt auf mehrere Zeilen → Name aus dem EQS-Seitenkopf
        kopf = text[:anfang].split("\n")
        i_kopf = next((i for i, z in enumerate(kopf) if re.search(r"\d{1,2} \w+ \d{4} \d{2}:\d{2}$", z)), -1)
        wer = kopf[i_kopf + 2] if 0 <= i_kopf < len(kopf) - 2 else ""
    return dict(zeile, formular="stimmrechte",
                meldepflichtiger=wer, sitz=_wert(zeilen, sitz).strip(" ,"),
                schwellendatum=pd.to_datetime(zeilen[i5 + 1], dayfirst=True, errors="coerce"),
                aktien=_prozent(neu[0]), instrumente=_prozent(neu[1]), summe=_prozent(neu[2]),
                gesamtstimmrechte=re.sub(r"\D", "", neu[3]),
                aktien_vorher=_prozent(letzte[0]), instrumente_vorher=_prozent(letzte[1]),
                summe_vorher=_prozent(letzte[2]))


# --- Auswertung für die Firmenseiten -------------------------------------------------------------

RECHTSFORM = re.compile(r"^(inc|ltd|llc|llp|lp|l\.p|plc|corp|co|s\.a|sa|ag|se|n\.v|nv|gmbh|s\.à r\.l|s\.a\.r\.l)\.?$", re.I)


def _schluessel(name: str) -> str:
    """Gleicher Halter, verschiedene Schreibweisen → gleicher Schlüssel.
    'BlackRock, Inc., Wilmington, DE, USA' und 'BlackRock, Inc.' → 'blackrockinc'.
    Ältere Formulare hängen Ort und Land an den Namen; abgeschnitten wird ab dem ersten Teil nach einem Komma,
    der keine Rechtsform ist."""
    name = name.split(" / ")[-1].replace("City and registered office", "")
    teile = name.split(",")
    behalten = [teile[0]] + [t for t in teile[1:2] if RECHTSFORM.match(t.strip())]
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\bthe\b", "", ",".join(behalten).lower()))


def grossaktionaere(df: pd.DataFrame) -> pd.DataFrame:
    """Letzter Stand je Firma und Halter.
    Nur wer mindestens 3 % in Aktien oder 5 % insgesamt hält: Das sind die niedrigsten Schwellen (Aktien 3 %,
    Instrumente und Summe 5 %). Darunter kann ein Halter ohne neue Mitteilung aussteigen, der Stand wäre unsicher.
    Spalten: firma, halter, aktien, instrumente, summe, schwellendatum, url; sortiert nach Summe."""
    df = df[df["formular"].eq("stimmrechte") & df["meldepflichtiger"].fillna("").ne("")].copy()
    df["schluessel"] = df["meldepflichtiger"].map(_schluessel)
    df["schwellendatum"] = pd.to_datetime(df["schwellendatum"], errors="coerce")
    df["summe"] = df["summe"].fillna(df["aktien"])
    letzte = df.sort_values(["schwellendatum", "veroeffentlicht"]).groupby(["firma", "schluessel"]).tail(1)
    # Anzeigename: kürzeste Schreibweise des Halters (meist die ohne Ort und Land)
    namen = df.assign(laenge=df["meldepflichtiger"].str.len()).sort_values("laenge") \
        .groupby("schluessel")["meldepflichtiger"].first()
    letzte["halter"] = letzte["schluessel"].map(namen)
    return (letzte[(letzte["aktien"] >= 3) | (letzte["summe"] >= 5)]
            .sort_values(["firma", "summe"], ascending=[True, False])
            [["firma", "halter", "aktien", "instrumente", "summe", "schwellendatum", "url"]]
            .reset_index(drop=True))
