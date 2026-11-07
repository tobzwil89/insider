"""Aktiengeschäfte aus einem fertigen Datensatz: ganzer Senat und die House-Meldungen, die pipeline/kongress.py nicht
liest (älteres Formular bis Mitte 2022, Papier-Scans). Nur lokal.

    python3 -m pipeline.kongress_datensatz   → daten/kongress_datensatz.csv (Spalten wie daten/kongress.csv
                                               + kammer, bioguide, url)

Quelle: Hugging Face „austin-starks/congressional-stock-trades“ (Tabelle political_trades, Parquet je Jahr, ~20 h
aktuell). Der Datensatz liest die amtlichen Meldungen (Senat: efdsearch.senate.gov, elektronisch als HTML-Tabelle;
Papier und Scans per Texterkennung und zweitem Lesen vom Seitenbild, nur veröffentlicht, wenn beide übereinstimmen) und
gibt jedem Geschäft die bioguide-Kennung. Wir müssen dafür nicht selbst die Nutzungserklärung von efdsearch abgeben.
Geprüft 07.11.2026 an unseren eigenen House-Daten ab Mitte 2022: 1.976 von 1.989 Meldungen gleich viele Geschäfte,
Datum und Art 100 %, Kürzel 99,2 %, Betrag 99,5 % gleich. Vom House kommen nur Meldungen, die unser Leser nicht mit
status `ok` gelesen hat (daten/kongress_fortschritt.csv), die übrigen bleiben aus der eigenen Quelle.
Rechtlich wie die House-Daten: 5 U.S.C. § 13107(c) (früher app. § 105(c)) beschränkt die kommerzielle Nutzung, egal aus
welcher Quelle → steht in .gitignore, vor dem Livegang klären. Die Datensatz-Lizenz („other“) räumt keine Rechte ein.
"""

import io

import pandas as pd
import requests

from pipeline import DATEN

DATEI = DATEN / "kongress_datensatz.csv"
HF = "https://huggingface.co/datasets/austin-starks/congressional-stock-trades"
BAUM = "https://huggingface.co/api/datasets/austin-starks/congressional-stock-trades/tree/main/data/political_trades"
INHABER = {"self": "selbst", "spouse": "Ehepartner", "joint": "gemeinsam", "dependent_child": "Kind",
           "not_indicated": "nicht angegeben"}
ART = {"purchase": "Kauf", "sale": "Verkauf", "exchange": "Tausch", "unmarked": "unklar"}
KAMMER = {"house": "rep", "senate": "sen"}
# Anlageart wie im House-Formular (seiten.ANLAGEART); Scans und Papier haben keine → über die Kürzelprüfung
ANLAGEART = {"Stock": "ST", "Stock Option": "OP", "Corporate Bond": "CS", "Municipal Security": "GS",
             "Non-Public Stock": "PS", "Cryptocurrency": "CT", "Commodities/Futures Contract": "OT", "Other": "OT"}


def umwandeln(t: pd.DataFrame) -> pd.DataFrame:
    """political_trades → Spalten von daten/kongress.csv."""
    kuerzel = t["printedTicker"].fillna(t["resolvedTicker"]).fillna("").str.upper()
    boerse = t["resolutionStatus"].isin(["printed", "resolved"]) & kuerzel.ne("")
    art = t["action"].map(ART).fillna(t["action"])
    anlageart = t["assetTypeCode"].fillna(t["assetTypeLabel"].map(ANLAGEART)).fillna(boerse.map({True: "ST", False: "OT"}))
    return pd.DataFrame({
        "doc_id": t["docId"].astype(str), "jahr": pd.to_datetime(t["filingDate"]).dt.year, "name": t["displayName"],
        "nachname": t["filerLast"], "vorname": t["filerFirst"], "bezirk": "",
        "eingereicht": pd.to_datetime(t["filingDate"]).dt.date,
        "inhaber": t["owner"].map(INHABER).fillna("nicht angegeben"),
        # Formularcode wie „[ST]“ steht bei manchen im Namen
        "wertpapier": t["assetDescription"].fillna("").str.replace(r"\s*\[[A-Z]{2}\]", "", regex=True).str.strip(),
        "kuerzel": kuerzel, "anlageart": anlageart,
        "art": art.where(~(t["partialSale"].fillna(False).astype(bool) & art.eq("Verkauf")), "Teilverkauf"),
        "datum": pd.to_datetime(t["transactionDate"]).dt.date,
        "gemeldet": pd.to_datetime(t["notificationDate"]).dt.date,
        "betrag_von": t["amountLow"], "betrag_bis": t["amountHigh"],
        "status": t["filingStatus"].fillna("New"), "unterkonto": "", "beschreibung": t["comment"].fillna(""),
        "kommentar": "", "kammer": t["chamber"].map(KAMMER), "bioguide": t["memberId"].fillna(""),
        "url": t["sourceUrl"]})


def laden() -> pd.DataFrame:
    fs = DATEN / "kongress_fortschritt.csv"
    selbst_gelesen = set(pd.read_csv(fs, dtype=str).query("status == 'ok'")["doc_id"]) if fs.exists() else set()
    dateien = [x["path"] for x in requests.get(BAUM, timeout=60).json() if x["path"].endswith(".parquet")]
    teile = []
    for p in sorted(dateien):
        r = requests.get(f"{HF}/resolve/main/{p}", timeout=120)
        r.raise_for_status()
        t = pd.read_parquet(io.BytesIO(r.content))
        teile.append(t[(t["chamber"] == "senate") | ~t["docId"].astype(str).isin(selbst_gelesen)])
    df = umwandeln(pd.concat(teile, ignore_index=True)).sort_values(["eingereicht", "doc_id"])
    df.to_csv(DATEI, index=False)
    return df


if __name__ == "__main__":
    d = laden()
    for k, g in d.groupby("kammer"):
        print(f"{k}: {len(g)} Geschäfte, {g['bioguide'].nunique()} Personen, {g['doc_id'].nunique()} Meldungen, "
              f"{g['eingereicht'].min()} bis {g['eingereicht'].max()}; Aktien mit Kürzel: "
              f"{(g['anlageart'].eq('ST') & g['kuerzel'].ne('')).sum()}, ohne bioguide: {g['bioguide'].eq('').sum()}")
