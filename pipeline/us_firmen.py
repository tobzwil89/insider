"""US-Universum (Freigabe Tobias 06.11.2026: über DAX/MDAX hinaus): vorerst die Firmen des S&P 500.

    python3 -m pipeline.us_firmen     → daten/us_firmen.csv (kuerzel, name, sec_name, cik, sektor, branche)

Liste aus Wikipedia („List of S&P 500 companies“, Spalten Symbol, Security, GICS Sector, CIK), dazu der amtliche
Firmenname aus der SEC-Liste company_tickers.json (z. B. „LOCKHEED MARTIN CORP“): Der passt besser zu anderen
Behördendaten (USAspending, FEC) als der Kurzname. Firmen mit zwei Gattungen (GOOGL/GOOG) stehen zweimal in der Liste,
hier je CIK einmal (erstes Kürzel). Vierteljährlich neu laden wie pipeline.firmen.
"""

import io

import pandas as pd
import requests

from pipeline import DATEN, HEADER

DATEI = DATEN / "us_firmen.csv"
WIKIPEDIA = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
SEC = "https://www.sec.gov/files/company_tickers.json"


def laden() -> pd.DataFrame:
    t = pd.read_html(io.StringIO(requests.get(WIKIPEDIA, headers=HEADER, timeout=60).text))[0]
    sec = pd.DataFrame(requests.get(SEC, headers=HEADER, timeout=60).json().values())
    sec_name = dict(zip(sec["cik_str"].astype(int), sec["title"]))
    df = pd.DataFrame({"kuerzel": t["Symbol"].str.replace(".", "-", regex=False), "name": t["Security"],
                       "cik": t["CIK"].astype(int), "sektor": t["GICS Sector"], "branche": t["GICS Sub-Industry"]})
    df["sec_name"] = df["cik"].map(sec_name).fillna(df["name"])
    df = df.drop_duplicates("cik").sort_values("kuerzel")
    df.to_csv(DATEI, index=False)
    return df


if __name__ == "__main__":
    d = laden()
    print(f"{len(d)} Firmen, ohne SEC-Namen: {(d['sec_name'] == d['name']).sum()}")
