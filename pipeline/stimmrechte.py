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


# EQS zeigt hier einen fremden Pressetext (KKR) statt der Mitteilung, geprüft 30.10.2026
DEFEKT = {
    "https://www.eqs-news.com/de/news/stimmrechtsanteile/deutsche-bank-aktiengesellschaft-frankfurt-germany-deutschland/c7f93dec-bfb3-4eb6-8d05-c7e1876897bd_en",
    "https://www.eqs-news.com/de/news/stimmrechtsanteile/allianz-global-investors-gmbh-frankfurt-main-deutschland/405e7a19-144a-4c4a-bd26-d2d36e173c74_en",
}


def lesen(url: str, html: str | None = None) -> dict:
    """Eine Stimmrechtsmitteilung → eine Zeile für stimmrechte.csv."""
    if url in DEFEKT:
        return {"url": url, "formular": "anderes"}
    soup = BeautifulSoup(html or eqs._holen(url), "lxml")
    for t in soup(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    text = "\n".join(map(_reparieren, soup.get_text("\n", strip=True).split("\n")))
    anfang = max(text.find("Für den Inhalt der Mitteilung"), text.find("The issuer is solely responsible"))
    if anfang < 0:
        raise eqs.Gedrosselt(f"Meldung ohne Inhalt: {url}")
    zeit = re.search(r"(\d{2})\.(\d{2})\.(\d{4})(?: /)? (\d{2}:\d{2})", text[max(0, anfang - 400): anfang])
    if zeit:
        veroeffentlicht = f"{zeit[3]}-{zeit[2]}-{zeit[1]} {zeit[4]}:00"
    else:  # ältere Seiten: Datum nur im EQS-Kopf, z. B. 'Stimmrechtsanteile | 3 September 2008 10:39'
        kopf = re.search(r"\| (\d{1,2}) (\w+) (\d{4}) (\d{2}:\d{2})", text[:anfang])
        veroeffentlicht = (f"{kopf[3]}-{eqs.MONATE[kopf[2]]:02d}-{int(kopf[1]):02d} {kopf[4]}:00"
                           if kopf and kopf[2] in eqs.MONATE else "")
    zeile = {"url": url, "veroeffentlicht": veroeffentlicht,
             "korrektur": "Korrektur" in text[max(0, anfang - 600): anfang]}

    zeilen = [re.sub(r"\s+", " ", z).strip() for z in text[anfang:].split("\n")]
    i3, i4, i5, i6, i7 = (_abschnitt(zeilen, f"{n}. ") for n in range(3, 8))
    i_neu = next((i for i in range(i6, i7) if zeilen[i] in NEU), -1) if 0 <= i6 < i7 else -1
    if min(i3, i4, i5, i_neu) < 0:
        # Text mitgeben: Mitteilungen vor ~2016 sind Fließtext ohne Formular (Auslesen: stimmrechte_fliesstext.py)
        ende = text.find("Ende der Mitteilung", anfang)
        return dict(zeile, formular="anderes", text=text[anfang: ende if ende > 0 else anfang + 6000])

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
    name = re.sub(r"\s*\(\d+\.\)$", "", name)  # 'Wolfgang Dr. Porsche (1.)' = 'Wolfgang Dr. Porsche
    teile = name.split(",")
    behalten = [teile[0]] + [t for t in teile[1:2] if RECHTSFORM.match(t.strip())]
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\bthe\b", "", ",".join(behalten).lower()))


def grossaktionaere(df: pd.DataFrame, geprueft: pd.DataFrame | None = None) -> pd.DataFrame:
    """Letzter Stand je Firma und Halter.
    Nur wer mindestens 3 % in Aktien oder 5 % insgesamt hält: Das sind die niedrigsten Schwellen (Aktien 3 %,
    Instrumente und Summe 5 %). Darunter kann ein Halter ohne neue Mitteilung aussteigen, der Stand wäre unsicher.
    geprueft: von Hand geprüfte Einträge (daten/grossaktionaere_geprueft.csv). Halter mit Prozentwert ersetzt den
    automatischen Eintrag desselben Halters, ohne Prozentwert blendet ihn aus; Halter '*' blendet alle automatischen
    Einträge der Firma vor `stand` aus (z. B. Meldungen eines Vorgängers mit gleichem Namen).
    Spalten: firma, halter, weitere (gleicher Bestand am gleichen Tag), aktien, instrumente, summe, schwellendatum,
    url, geprueft; sortiert nach Aktien."""
    df = df[df["formular"].eq("stimmrechte") & df["meldepflichtiger"].fillna("").ne("")].copy()
    df["schluessel"] = df["meldepflichtiger"].map(_schluessel)
    df["schwellendatum"] = pd.to_datetime(df["schwellendatum"], errors="coerce")
    df["summe"] = df["summe"].fillna(df["aktien"])
    letzte = df.sort_values(["schwellendatum", "veroeffentlicht"]).groupby(["firma", "schluessel"]).tail(1)
    # Anzeigename: kürzeste Schreibweise des Halters (meist die ohne Ort und Land)
    namen = df.assign(laenge=df["meldepflichtiger"].str.len()).sort_values("laenge") \
        .groupby("schluessel")["meldepflichtiger"].first()
    letzte["halter"] = letzte["schluessel"].map(namen)
    # Konzernkette: Wer je am selben Tag denselben Bestand gemeldet hat wie ein anderer (Mutter, Tochter,
    # Familie), gehört zur selben Kette. Je Kette zählt der neueste Stand; ältere Meldungen mit anderem Wert sind
    # überholt (vor dem Schwellenfilter: Parsifal 3,05 % ist überholt, weil David Zorub für dieselbe Kette 2,92 %
    # meldet). Gleicher Wert an verschiedenen Tagen reicht nicht: runde Werte wie 25,1 % kommen oft zufällig vor
    kette = {}
    def wurzel(k):
        while kette.get(k, k) != k:
            k = kette[k]
        return k
    for (firma, *_), h in df[df["aktien"] > 0].groupby(["firma", "schwellendatum", "aktien", "instrumente"])["schluessel"]:
        for k in h.iloc[1:]:
            kette[wurzel((firma, k))] = wurzel((firma, h.iloc[0]))
    letzte["kette"] = [wurzel(k) for k in zip(letzte["firma"], letzte["schluessel"])]
    neuester = letzte.sort_values("schwellendatum").groupby("kette")[["aktien", "instrumente"]].transform("last") \
        .reindex(letzte.index)
    letzte = letzte[letzte["aktien"].eq(neuester["aktien"]) & letzte["instrumente"].eq(neuester["instrumente"])]
    letzte = letzte[(letzte["aktien"] >= 3) | (letzte["summe"] >= 5)]
    # Stände vor 2018 nicht zeigen: ungeprüft und oft überholt (Ausstiege fehlen im EQS-Archiv)
    letzte = letzte[letzte["schwellendatum"] >= "2018-01-01"]
    # Umfirmierung: Ein Halter mit gleichem Namensanfang meldet später genau diesen Stand als seinen vorherigen
    # (PFC S.r.l. 15,01 % → PFC S.p.A. meldet 2025 „vorher 15,01 %“) → alter Name ist überholt
    nachfolger = df[["firma", "schluessel", "schwellendatum", "aktien_vorher", "instrumente_vorher"]].rename(
        columns={"schluessel": "neu", "schwellendatum": "spaeter", "aktien_vorher": "aktien",
                 "instrumente_vorher": "instrumente"})
    treffer = letzte.reset_index().merge(nachfolger, on=["firma", "aktien", "instrumente"])
    treffer = treffer[(treffer["spaeter"] > treffer["schwellendatum"]) & treffer["neu"].ne(treffer["schluessel"])
                      & treffer["neu"].str[:4].eq(treffer["schluessel"].str[:4])]  # sonst Zufallstreffer
    letzte = letzte.drop(treffer["index"].unique())
    if geprueft is not None and not geprueft.empty:
        g = geprueft.assign(stand=pd.to_datetime(geprueft["stand"]), geprueft=pd.to_datetime(geprueft["geprueft"]))
        for r in g[g["halter"].eq("*")].itertuples():
            letzte = letzte[~(letzte["firma"].eq(r.firma) & (letzte["schwellendatum"] < r.stand))]
        einzeln = g[g["halter"].ne("*")].assign(schluessel=lambda x: x["halter"].map(_schluessel))
        weg = set(zip(einzeln["firma"], einzeln["schluessel"]))
        letzte = letzte[[k not in weg for k in zip(letzte["firma"], letzte["schluessel"])]]
        neu = einzeln[einzeln["aktien"].notna()].rename(columns={"stand": "schwellendatum", "quelle": "url"})
        letzte = pd.concat([letzte, neu.assign(summe=neu["aktien"], kette=neu["halter"])])
    if "geprueft" not in letzte:
        letzte["geprueft"] = pd.NaT
    # Eine Zeile je Kette und Bestand, neuester Stand vorn
    letzte = letzte.sort_values("schwellendatum", ascending=False).groupby(
        ["firma", "kette", "aktien", "instrumente"], dropna=False, as_index=False).agg(
        halter=("halter", "first"), weitere=("halter", lambda h: ", ".join(h.iloc[1:])),
        schwellendatum=("schwellendatum", "first"), summe=("summe", "first"), url=("url", "first"),
        geprueft=("geprueft", "first"))
    return (letzte.sort_values(["firma", "aktien", "summe"], ascending=[True, False, False])
            [["firma", "halter", "weitere", "aktien", "instrumente", "summe", "schwellendatum", "url", "geprueft"]]
            .reset_index(drop=True))


# Eigene Aktien (§ 40 Abs. 1 Satz 2 WpHG): Die Firma meldet, wenn ihr Bestand eigener Aktien 3, 5 oder 10 % berührt.
# Diese Mitteilungen stehen in stimmrechte.csv als formular="anderes"; gelesen werden sie hier in eine eigene Datei.
EIGENE_URL = r"eigene[nr]?-aktien|own-shares"


def eigene_aktien_lesen(url: str, html: str | None = None) -> dict:
    """Eine Mitteilung über eigene Aktien → schwellendatum, anteil, anteil_vorher, gesamt (Aktien insgesamt)."""
    soup = BeautifulSoup(html or eqs._holen(url), "lxml")
    for t in soup(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    zeilen = [_reparieren(z) for z in soup.get_text("\n", strip=True).split("\n")]
    anfang = next((i for i, z in enumerate(zeilen) if z.startswith(("Für den Inhalt der Mitteilung",
                                                                    "The issuer is solely responsible"))), -1)
    if anfang < 0:
        raise eqs.Gedrosselt(f"Meldung ohne Inhalt: {url}")
    zeilen = zeilen[anfang:]
    datum = zeilen[_abschnitt(zeilen, "3. ") + 1]
    neu = next(i for i, z in enumerate(zeilen) if z in ("Neu", "Resulting situation"))
    vorher = next((i for i, z in enumerate(zeilen) if z in ("Letzte Veröffentlichung", "Previous publication")), -1)
    return {"url": url,
            "schwellendatum": pd.to_datetime(datum, dayfirst=True, errors="coerce"),
            "anteil": _prozent(zeilen[neu + 1]),
            "anteil_vorher": _prozent(zeilen[vorher + 1]) if vorher > 0 else None,
            "gesamt": int(re.sub(r"\D", "", zeilen[neu + 2]) or 0) or None}


def eigene_aktien(df: pd.DataFrame) -> pd.DataFrame:
    """Letzter Stand eigener Aktien je Firma (nach Schwellendatum, nur Mitteilungen ab 2018).
    Nur wer zuletzt mindestens 3 % gemeldet hat: Darunter muss die Firma Änderungen nicht mehr melden.
    Spalten: firma, anteil, schwellendatum, url."""
    df = df.assign(schwellendatum=pd.to_datetime(df["schwellendatum"], errors="coerce")).dropna(subset=["anteil"])
    df = df[df["schwellendatum"] >= "2018-01-01"]
    letzte = df.sort_values("schwellendatum").groupby("firma").tail(1)
    return letzte[letzte["anteil"] >= 3][["firma", "anteil", "schwellendatum", "url"]]
