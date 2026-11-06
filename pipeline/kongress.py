"""Aktiengeschäfte von US-Abgeordneten (STOCK Act): Periodic Transaction Reports (PTR) des Repräsentantenhauses.

Quelle (amtlich, gemeinfrei, ohne Schlüssel): Der Clerk of the House veröffentlicht je Jahr ein Verzeichnis aller
Vermögensmeldungen als Zip (`<Jahr>FD.zip`, täglich neu erzeugt, Tabelle `<Jahr>FD.txt`); Meldungstyp P = PTR.
Jede PTR ist ein PDF unter `ptr-pdfs/<Jahr>/<DocID>.pdf`. Elektronisch eingereichte (DocID beginnt mit 2) haben eine
Textebene, Papiermeldungen (DocID 8…/9…) sind Scans → status „scan“, hier nicht gelesen (später Texterkennung).

Aufbau einer Transaktion im PDF-Text (seit etwa 2020):
    JT Agree Realty Corporation Common          ← Inhaber (SP Ehepartner, JT gemeinsam, DC Kind, leer = selbst)
    Stock (ADC) [ST]                            ← Kürzel in (), Anlageart in [] (ST Aktie, OP Option, GS Anleihe …)
    S (partial) 06/10/2026 07/07/2026 $1,001 - $15,000   ← Art, Geschäftstag, Meldetag, Betragsspanne
    F      S     : New                          ← Filing Status (Kapitälchen gehen beim Auslesen verloren)
    S          O : Morgan Stanley - Select UMA  ← Subholding Of (Unterkonto)
    D          : Purchased 10,000 shares.       ← Description
Ältere PDFs (2014–2019) setzen Zeilen anders um und verdrehen Groß-/Kleinschreibung; sie werden mit denselben
Regeln gelesen, so gut es geht (Kürzel immer in Großbuchstaben). Beträge sind nur als Spanne gemeldet.
"""

import io
import re
import zipfile

import pandas as pd
import pypdf
import requests

BASIS = "https://disclosures-clerk.house.gov/public_disc"
KOPF = {"User-Agent": "Mozilla/5.0 (compatible; Rhodus/1.0; Forschung zu Pflichtmeldungen)"}
ART = {"P": "Kauf", "S": "Verkauf", "S (partial)": "Teilverkauf", "E": "Tausch"}
INHABER = {"SP": "Ehepartner", "JT": "gemeinsam", "DC": "Kind"}

# Art, Geschäftstag, Meldetag, Rest (Betrag); davor kann noch das Ende des Wertpapiernamens stehen
KERN = re.compile(r"(?:^|(?<=[\s\])]))(P|S \(partial\)|S|E)\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}/\d{1,2}/\d{4})\s*(.*)$")
# Markierte Zeile: ein oder zwei Großbuchstaben, dann Doppelpunkt ("F      S     : New", "D          : …")
MARKE = re.compile(r"^([A-Z])(?:\s+([A-Z]))?\s*:\s?(.*)$")
MARKEN = {("F", "S"): "status", ("S", "O"): "unterkonto", ("D", None): "beschreibung", ("C", None): "kommentar",
          ("L", None): "ort"}
UEBERSPRINGEN = {"ID Owner Asset Transaction", "Type", "Date Notification", "Date", "Amount Cap.", "Gains >", "$200?"}
BETRAG = re.compile(r"\$\s?([\d,]+)")
KUERZEL = re.compile(r"\(([A-Za-z][A-Za-z0-9.\-/$ ]{0,9})\)")  # auch Vorzugsaktien wie T$A
ANLAGEART = re.compile(r"\[([A-Za-z]{2})\]")
# Älteres Formular (bis etwa Mitte 2022): Marken als zerlegte Wörter („F ILINg S TATUS“), Kästchen als „fedcb“,
# Beschreibung und nächstes Wertpapier in einer Zeile → regelbasiert nicht sauber trennbar, status „alt“ (später
# eigener Leser, z. B. über Textpositionen oder ein Sprachmodell)
ALTFORMAT = re.compile(r"F\s*ILING\s+S\s*TATUS", re.I)
# Beschreibungen brechen erst bei voller Seitenbreite um: nur nach einer so langen Zeile folgt eine Fortsetzung
VOLLE_ZEILE = 100


def verzeichnis(jahr: int) -> pd.DataFrame:
    """Alle PTR eines Jahres laut Verzeichnis: doc_id, name, bezirk, eingereicht, jahr."""
    r = requests.get(f"{BASIS}/financial-pdfs/{jahr}FD.zip", headers=KOPF, timeout=120)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        text = z.read(f"{jahr}FD.txt").decode("utf-8", "replace")
    df = pd.read_csv(io.StringIO(text), sep="\t", dtype=str, keep_default_na=False)
    df = df[df["FilingType"].str.strip() == "P"]
    name = (df["Prefix"] + " " + df["First"] + " " + df["Last"] + " " + df["Suffix"]).str.replace(r"\s+", " ", regex=True)
    return pd.DataFrame({"doc_id": df["DocID"].str.strip(), "name": name.str.replace("Hon. ", "", regex=False).str.strip(),
                         "nachname": df["Last"].str.strip(), "vorname": df["First"].str.strip(),
                         "bezirk": df["StateDst"].str.strip(),
                         "eingereicht": pd.to_datetime(df["FilingDate"].str.strip(), format="%m/%d/%Y", errors="coerce"),
                         "jahr": jahr})


def pdf_url(jahr: int, doc_id: str) -> str:
    return f"{BASIS}/ptr-pdfs/{jahr}/{doc_id}.pdf"


def pdf_text(inhalt: bytes) -> str:
    # Kapitälchen (Überschriften, Marken wie „Filing Status“) kommen als Nullzeichen heraus → entfernen
    return "\n".join(s.extract_text() or "" for s in pypdf.PdfReader(io.BytesIO(inhalt)).pages).replace("\x00", "")


def _betrag(text: str) -> tuple:
    zahlen = [int(z.replace(",", "")) for z in BETRAG.findall(text)]
    if not zahlen:
        return None, None
    if re.search(r"\bover\b", text, re.I) or len(zahlen) == 1:
        return zahlen[0], None if re.search(r"\bover\b", text, re.I) else zahlen[0]
    return zahlen[0], zahlen[1]


def _name_ergaenzen(t: dict, text: str) -> None:
    """Hängt Text an den Wertpapiernamen und liest Kürzel (…) und Anlageart […] neu."""
    voll = f"{t['wertpapier']} {t['anlageart'] and '[' + t['anlageart'] + ']'} {text}"
    kuerzel, anlageart = KUERZEL.findall(voll), ANLAGEART.findall(voll)
    t["wertpapier"] = re.sub(r"\s+", " ", ANLAGEART.sub("", voll)).strip()
    t["kuerzel"] = kuerzel[-1].upper().replace(" ", "") if kuerzel else ""
    t["anlageart"] = anlageart[-1].upper() if anlageart else ""


def transaktionen(text: str) -> list:
    """Liest alle Transaktionen aus dem Text einer PTR. Jede: inhaber, wertpapier, kuerzel, anlageart, art, datum,
    gemeldet, betrag_von, betrag_bis, status, unterkonto, beschreibung, kommentar."""
    zeilen = [z.strip() for z in text.splitlines()]
    try:
        start = zeilen.index("$200?") + 1
    except ValueError:
        return []
    ergebnis, puffer, offen, letzte_marke, vorige_voll = [], [], None, None, False
    for z in zeilen[start:]:
        war_voll, vorige_voll = vorige_voll, len(z) >= VOLLE_ZEILE
        if z.startswith("* For the complete list") or z.startswith("I CERTIFY"):
            break
        if not z or z in UEBERSPRINGEN or z.startswith("Filing ID #"):
            continue
        if offen and offen.get("betrag_fehlt") and re.fullmatch(r"\$[\d,]+", z):
            offen["betrag_bis"] = int(z[1:].replace(",", ""))
            offen.pop("betrag_fehlt")
            continue
        m = MARKE.match(z)
        if m and offen and (m[1], m[2]) in MARKEN:
            letzte_marke = MARKEN[(m[1], m[2])]
            offen[letzte_marke] = m[3].strip()
            continue
        k = KERN.search(z)
        if k:
            vorne = z[:k.start(1)].strip()
            wertpapier = " ".join(puffer + ([vorne] if vorne else []))
            puffer, letzte_marke = [], None
            inhaber = ""
            teile = wertpapier.split(" ", 1)
            if teile[0] in INHABER:
                inhaber, wertpapier = teile[0], teile[1] if len(teile) > 1 else ""
            von, bis = _betrag(k[4])
            offen = {"inhaber": INHABER.get(inhaber, "selbst"), "wertpapier": "", "kuerzel": "", "anlageart": "",
                     "art": ART[k[1]], "datum": pd.to_datetime(k[2], format="%m/%d/%Y", errors="coerce"),
                     "gemeldet": pd.to_datetime(k[3], format="%m/%d/%Y", errors="coerce"),
                     "betrag_von": von, "betrag_bis": bis, "status": "", "unterkonto": "", "beschreibung": "",
                     "kommentar": "", "ort": ""}
            _name_ergaenzen(offen, wertpapier)
            if k[4].rstrip().endswith("-"):
                offen["betrag_fehlt"] = True
            ergebnis.append(offen)
            continue
        # Rest des Wertpapiernamens, den das PDF erst hinter die Transaktionszeile setzt (Anlageart fehlt noch)
        if offen and letzte_marke is None and not puffer and not offen["anlageart"]:
            _name_ergaenzen(offen, z)
            continue
        # Fortsetzung einer langen Beschreibung, sonst Teil des nächsten Wertpapiernamens
        if offen and letzte_marke == "beschreibung" and war_voll and not puffer:
            offen["beschreibung"] += " " + z
            continue
        letzte_marke = None
        puffer.append(z)
    for t in ergebnis:
        t.pop("betrag_fehlt", None)
        t.pop("ort", None)  # Land des Kontos, nicht gebraucht
    return ergebnis


def lesen(jahr: int, doc_id: str, sitzung: requests.Session | None = None) -> tuple:
    """(status, transaktionen) einer PTR. status: ok, scan (keine Textebene), alt (älteres Formular, noch nicht gelesen), leer (Text, aber nichts erkannt)."""
    if not doc_id.startswith("2"):
        return "scan", []
    r = (sitzung or requests).get(pdf_url(jahr, doc_id), headers=KOPF, timeout=60)
    r.raise_for_status()
    if not r.content.startswith(b"%PDF"):
        raise ValueError(f"kein PDF ({r.status_code})")
    text = pdf_text(r.content)
    if len(text.strip()) < 20:
        return "scan", []
    if ALTFORMAT.search(text):
        return "alt", []
    t = transaktionen(text)
    return ("ok" if t else "leer"), t
