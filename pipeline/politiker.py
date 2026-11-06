"""US-Abgeordnete: Meldungen (pipeline/kongress.py) den Personen zuordnen und je Person auswerten.

Personendaten aus dem Projekt „congress-legislators“ (github.com/unitedstates/congress-legislators, gemeinfrei):
je Amtszeit Kammer, Bundesstaat, Wahlbezirk, Partei, dazu die amtliche Bioguide-ID. Zuordnung einer Meldung über
Bundesstaat + Wahlbezirk („CA11“) + Datum der Meldung (Amtszeit, plus ein Jahr Nachlauf für späte Meldungen) und
Nachname; passt kein Nachname, aber genau eine Person (Rufname: „Rick“ statt „Richard“), gilt diese.

Betrag: Gemeldet werden nur Spannen (1.001–15.000 $ …). Für Summen gilt die Mitte der Spanne, bei „über X“ X;
so rechnen auch Quiver und Capitol Trades (deren Werte sind ebenfalls Schätzungen).
Überrendite seit dem Geschäft: Aktie minus S&P 500 (^GSPC) vom Schlusskurs am Geschäftstag bis zum letzten Kurs.
"""

import re
import time
import unicodedata

import pandas as pd
import requests

from pipeline import DATEN, kongress

QUELLE = "https://unitedstates.github.io/congress-legislators/legislators-{}.json"
ABGEORDNETE = DATEN / "abgeordnete.csv"
KURSE = DATEN / "kurse_us.parquet"
INDEX = "^GSPC"
PARTEI = {"Democrat": "Demokraten", "Republican": "Republikaner", "Independent": "Unabhängig"}


def abgeordnete_laden(ab: str = "2011-01-01") -> pd.DataFrame:
    """Alle Amtszeiten ab `ab` nach daten/abgeordnete.csv (eine Zeile je Amtszeit, ~1.300 Zeilen)."""
    zeilen = []
    for teil in ["current", "historical"]:
        for p in requests.get(QUELLE.format(teil), timeout=120).json():
            for t in p["terms"]:
                if t["end"] < ab:
                    continue
                zeilen.append({"bioguide": p["id"]["bioguide"], "vorname": p["name"]["first"],
                               "nachname": p["name"]["last"],
                               "name": p["name"].get("official_full") or f"{p['name']['first']} {p['name']['last']}",
                               "kammer": t["type"], "bundesstaat": t["state"], "bezirk": t.get("district"),
                               "partei": t.get("party", ""), "start": t["start"], "ende": t["end"]})
    df = pd.DataFrame(zeilen)
    df.to_csv(ABGEORDNETE, index=False)
    return df


def _falten(text: str) -> set:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode().lower()
    return set(re.findall(r"[a-z]+", text)) - {"jr", "sr", "ii", "iii", "iv"}


def zuordnen(meldungen: pd.DataFrame, abgeordnete: pd.DataFrame) -> pd.DataFrame:
    """Hängt bioguide, politiker (Name), partei, kammer an jede Zeile (Repräsentantenhaus: Spalte bezirk 'CA11')."""
    a = abgeordnete[abgeordnete["kammer"] == "rep"].copy()
    a["start"], a["ende"] = pd.to_datetime(a["start"]), pd.to_datetime(a["ende"]) + pd.Timedelta(days=365)
    a["bez"] = a["bundesstaat"] + a["bezirk"].fillna(0).astype(int).astype(str).str.zfill(2)
    treffer = {}
    for (nachname, bezirk, tag), _ in meldungen.groupby(["nachname", "bezirk", "eingereicht"], dropna=False):
        bez = re.sub(r"^([A-Z]{2})(\d)$", r"\g<1>0\2", str(bezirk))  # „CA1“ → „CA01“
        im_amt = a[(a["start"] <= tag) & (a["ende"] >= tag)]
        gleich = im_amt["nachname"].map(lambda n: bool(_falten(n) & _falten(nachname)))
        bezirk_k = im_amt[im_amt["bez"] == bez]
        # 1. Nachname im Bezirk, 2. Nachname im Bundesstaat (alter Bezirk nach Neuzuschnitt, z. B. McCormick
        # meldet 2026 noch GA06), 3. die einzige Person im Bezirk (Rufname weicht ab)
        wahl = im_amt[gleich & (im_amt["bez"] == bez)]
        if wahl.empty:
            wahl = im_amt[gleich & (im_amt["bundesstaat"] == bez[:2])]
            if wahl["bioguide"].nunique() > 1:
                continue
        if wahl.empty and bezirk_k["bioguide"].nunique() == 1:
            wahl = bezirk_k
        if wahl.empty:
            continue
        z = wahl.sort_values("start").iloc[-1]
        treffer[(nachname, bezirk, tag)] = (z["bioguide"], z["name"], PARTEI.get(z["partei"], z["partei"]))
    werte = [treffer.get(key, ("", "", "")) for key in zip(meldungen["nachname"], meldungen["bezirk"], meldungen["eingereicht"])]
    return meldungen.assign(bioguide=[w[0] for w in werte], politiker=[w[1] for w in werte],
                            partei=[w[2] for w in werte])


def yahoo(kuerzel: str) -> str | None:
    """Kürzel aus der Meldung → Yahoo-Symbol (BRK.B → BRK-B); Vorzugsaktien mit $ und Leeres → None."""
    k = str(kuerzel).strip().upper()
    if not k or "$" in k or " " in k or len(k) > 6:
        return None
    return k.replace(".", "-").replace("/", "-")


def kurse(symbole: list, start, block: int = 50, pause: float = 5) -> pd.DataFrame:
    """US-Schlusskurse mit lokalem Speicher daten/kurse_us.parquet (nur lokal, braucht pyarrow).
    Yahoo sperrt eine IP nach zu vielen großen Abfragen für Stunden („Too Many Requests“), deshalb: fehlende Symbole
    in kleinen Blöcken mit Pause, danach je Lauf nur die letzten Tage. Kommt ein ganzer Block leer zurück, gilt das als
    Sperre: Abbruch, beim nächsten Lauf weiter. Symbole ohne Daten (z. B. alte Kürzel) bleiben als leere Spalte gespeichert
    und werden nicht erneut abgefragt (zum Neuladen die Datei löschen)."""
    from pipeline.kurse import lade_kurse
    speicher = pd.read_parquet(KURSE) if KURSE.exists() else pd.DataFrame()

    def holen(liste, ab) -> pd.DataFrame | None:
        try:
            k = lade_kurse(liste, ab)
        except RuntimeError:
            return None
        return None if k.dropna(axis=1, how="all").empty else k.reindex(columns=liste)

    gesperrt = False
    if not speicher.empty and speicher.index.max() < pd.Timestamp.today().normalize() - pd.Timedelta(days=1):
        mit_daten = [s for s in speicher.columns if speicher[s].notna().any()]
        for i in range(0, len(mit_daten), 200):
            neu = holen(mit_daten[i:i + 200], speicher.index.max() - pd.Timedelta(days=7))
            if neu is None:
                gesperrt = True
                break
            speicher = neu.combine_first(speicher)
            time.sleep(pause)
    fehlend = [s for s in dict.fromkeys(symbole) if s not in speicher.columns]
    for i in range(0, 0 if gesperrt else len(fehlend), block):
        neu = holen(fehlend[i:i + block], start)
        if neu is None:
            print(f"  Yahoo liefert nichts mehr (Sperre?), noch {len(fehlend) - i} Symbole offen, nächster Lauf macht weiter")
            break
        speicher = speicher.join(neu, how="outer") if not speicher.empty else neu
        speicher.to_parquet(KURSE)
        time.sleep(pause)
    if not speicher.empty:
        speicher.to_parquet(KURSE)
    return speicher


def mitte(von, bis) -> float | None:
    if pd.isna(von):
        return None
    return float(von) if pd.isna(bis) else (float(von) + float(bis)) / 2


def ueberrendite_seit(kurse: pd.DataFrame, symbol: str | None, tag) -> float | None:
    if not symbol or symbol not in kurse or INDEX not in kurse or pd.isna(tag):
        return None
    paar = kurse[[symbol, INDEX]].dropna()
    t0 = paar.index.searchsorted(tag)
    if t0 >= len(paar) - 1:
        return None
    start, ende = paar.iloc[t0], paar.iloc[-1]
    return (ende[symbol] / start[symbol] - 1) - (ende[INDEX] / start[INDEX] - 1)


def adresse(name: str) -> str:
    text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


GLEICHES_GESCHAEFT = ["bioguide", "kuerzel", "wertpapier", "art", "datum", "inhaber"]


def korrekturen(m: pd.DataFrame) -> pd.DataFrame:
    """Status „Amended“ ersetzt frühere Zeilen desselben Geschäfts aus anderen Meldungen, „Deleted“ löscht sie
    (und fällt selbst weg). Gleiches Geschäft = gleiche Person, Wertpapier, Art, Tag, Inhaber."""
    korr = m[m["status"].isin(["Amended", "Deleted"])]
    if korr.empty:
        return m
    letzte = korr.groupby(GLEICHES_GESCHAEFT)["eingereicht"].max().to_dict()
    schluessel = list(zip(*(m[s] for s in GLEICHES_GESCHAEFT)))
    ersetzt = [k in letzte and tag < letzte[k] for k, tag in zip(schluessel, m["eingereicht"])]
    return m[~pd.Series(ersetzt, index=m.index) & m["status"].ne("Deleted")]


def politiker(meldungen: pd.DataFrame, kurse: pd.DataFrame) -> list:
    """meldungen: zuordnen(…). Je Person ein dict für seiten.politikerseite, neuestes Geschäft zuerst."""
    m = korrekturen(meldungen[meldungen["bioguide"] != ""]).copy()
    m["betrag"] = [mitte(v, b) for v, b in zip(m["betrag_von"], m["betrag_bis"])]
    m["symbol"] = m["kuerzel"].map(yahoo)
    m["url"] = [kongress.pdf_url(j, d) for j, d in zip(m["jahr"], m["doc_id"])]
    aktie = m["anlageart"].eq("ST") & m["art"].ne("Tausch")
    m["seit"] = [ueberrendite_seit(kurse, s, d) if a else None for s, d, a in zip(m["symbol"], m["datum"], aktie)]
    liste = []
    for bg, g in m.groupby("bioguide"):
        g = g.sort_values(["eingereicht", "datum"], ascending=False)
        liste.append({"bioguide": bg, "name": g["politiker"].iloc[0], "partei": g["partei"].iloc[0],
                      "bezirk": g["bezirk"].iloc[0], "geschaefte": g, "letztes": g["datum"].max(),
                      "meldungen": g["doc_id"].nunique()})
    vergeben = {}
    for p in liste:
        a = adresse(p["name"])
        vergeben[a] = vergeben.get(a, 0) + 1
        p["adresse"] = a if vergeben[a] == 1 else f"{a}-{vergeben[a]}"
    return sorted(liste, key=lambda p: p["letztes"], reverse=True)
