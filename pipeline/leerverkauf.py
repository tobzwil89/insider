"""Netto-Leerverkaufspositionen (Short-Positionen) einzelner Fonds aus den Registern der Aufsichtsbehörden.

Quelle: QuiVad (www.quivad.com/api), sammelt täglich die Register von 23 Behörden (EU-Leerverkaufsverordnung ab 0,5 %
in Europa, dazu GB, Australien, Japan, USA). Ohne Schlüssel, ohne Konto. Eine Datei mit allen offenen Positionen.

Lizenz: Die Daten bleiben unter den Bedingungen der jeweiligen Behörde (Feld reuse_terms). Weggelassen werden:
  us = FINRA Short Interest („Non-commercial use only“), jp = JPX („No commercial secondary use“).
Australien (ASIC, CC BY 4.0) und GB/Australien kommen nur als Summe je Firma (ohne Fonds).
Vor dem Start klären: Weiterverbreitung über QuiVad statt direkt bei BaFin/ESMA-Registern.

    python3 -m pipeline.leerverkauf   → daten/leerverkauf.csv (alle offenen Positionen, ohne US/JP)
                                        daten/leerverkauf_verlauf.csv (je Tag Summe je eigener Firma, dauerhaft)
                                        docs/data/leerverkauf.json (eigene DAX/MDAX-Firmen mit offenen Positionen)
Läuft nachts in der Action „Stimmrechte laden“.
"""
import gzip
import json
from datetime import datetime, timezone

import pandas as pd
import requests

from pipeline import AUSGABE, DATEN, HEADER

URL = "https://www.quivad.com/api/positions.jsonl.gz"
OHNE = {"us", "jp"}  # Lizenz verbietet kommerzielle Nutzung
DATEI, VERLAUF, JSON = DATEN / "leerverkauf.csv", DATEN / "leerverkauf_verlauf.csv", AUSGABE / "leerverkauf.json"


def laden():
    r = requests.get(URL, headers=HEADER, timeout=180)
    r.raise_for_status()
    zeilen = [json.loads(z) for z in gzip.decompress(r.content).decode().splitlines() if z.strip()]
    df = pd.DataFrame([z for z in zeilen if z["market"] not in OHNE and z["unit"] == "percent"])
    # df["isin"]/df["size"] statt df.isin/df.size: das sind pandas-Methoden
    return pd.DataFrame({"markt": df["market"], "firma": df["company"], "isin": df["isin"], "inhaber": df["holder"],
                         "summe": df["aggregated"], "anteil_pct": df["size"], "gemeldet": df["disclosed_on"],
                         "quivad": df["company_url"]})


def main():
    df = laden()
    if len(df) < 500:  # Sicherung: halbe Datei (Bau läuft gerade) nicht übernehmen
        raise SystemExit(f"Leerverkauf: nur {len(df)} Positionen, alte Daten bleiben")
    df.sort_values(["markt", "firma", "anteil_pct"], ascending=[True, True, False]).to_csv(DATEI, index=False)

    firmen = pd.read_csv(DATEN / "firmen.csv", dtype=str)
    eigen = df.merge(firmen[["isin", "ticker", "name"]], on="isin")
    heute = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    raus = []
    for (isin, ticker, name), g in eigen.groupby(["isin", "ticker", "name"]):
        g = g.sort_values("anteil_pct", ascending=False)
        raus.append({"isin": isin, "ticker": ticker, "name": name, "summe_pct": round(g.anteil_pct.sum(), 2),
                     "fonds": len(g), "quivad": g.quivad.iloc[0],
                     "positionen": g[["inhaber", "anteil_pct", "gemeldet"]].to_dict("records")})
    raus.sort(key=lambda f: -f["summe_pct"])

    v = pd.DataFrame([{"tag": heute, "isin": f["isin"], "summe_pct": f["summe_pct"], "fonds": f["fonds"]} for f in raus],
                     columns=["tag", "isin", "summe_pct", "fonds"])
    if VERLAUF.exists():
        v = pd.concat([pd.read_csv(VERLAUF, dtype={"isin": str}).query("tag != @heute"), v])
    v.sort_values(["tag", "isin"]).to_csv(VERLAUF, index=False)

    AUSGABE.mkdir(parents=True, exist_ok=True)
    JSON.write_text(json.dumps({
        "stand": heute,
        "quelle": "Register der Aufsichtsbehörden (BaFin u. a.), gesammelt von QuiVad (quivad.com)",
        "hinweis": "Nur Positionen ab 0,5 % des Grundkapitals sind meldepflichtig; kleinere fehlen.",
        "firmen": raus,
    }, ensure_ascii=False, separators=(",", ":")))
    print(f"Leerverkauf: {len(df)} offene Positionen in {df.markt.nunique()} Märkten, "
          f"{len(raus)} eigene Firmen mit Short-Positionen")


if __name__ == "__main__":
    main()
