"""Spenden der Firmen-PACs an Kandidaten für den US-Kongress (Wahlbehörde FEC, Massendateien ohne Schlüssel).

    python3 -m pipeline.spenden      → daten/spenden.csv (kuerzel, zyklus, cand_id, betrag, anzahl),
                                       spenden_kandidaten.csv (cand_id, bioguide, kandidat, partei, amt), spenden_pacs.csv

Ein PAC (Political Action Committee) ist die Spendenkasse eines Konzerns, gespeist von Mitarbeitern; die Firma selbst
darf Kandidaten nicht direkt unterstützen. Dateien je Wahlzyklus (2 Jahre) unter fec.gov/files/bulk-downloads/<Jahr>/:
cm (Komitees, mit „Connected Organization“), cn (Kandidaten), pas2 (Zahlungen von Komitees an Kandidaten).
Gezählt wird Transaktionsart 24K (direkte Spende an das Wahlkampfkomitee eines Kandidaten).
Firma ↔ PAC über den Namen der verbundenen Organisation (gleiche Regel wie bei den Staatsaufträgen), Kandidat ↔
Abgeordnete(r) über die FEC-IDs in congress-legislators. Nutzungsgrenze: Namen privater Einzelspender dürfen nicht
kommerziell genutzt werden (52 U.S.C. 30111(a)(4)); hier stehen nur PACs und Kandidaten.
"""

import io
import re
import sys
import zipfile

import pandas as pd
import requests

from pipeline import DATEN, HEADER
from pipeline.staatsauftraege import ZUSATZ, _woerter

ERGEBNIS = DATEN / "spenden.csv"
KANDIDATEN = DATEN / "spenden_kandidaten.csv"
PACS = DATEN / "spenden_pacs.csv"
BASIS = "https://www.fec.gov/files/bulk-downloads/{jahr}/{name}{yy}.zip"
ZYKLEN = [2022, 2024, 2026]
SPALTEN = {
    "cm": ["CMTE_ID", "CMTE_NM", "TRES_NM", "CMTE_ST1", "CMTE_ST2", "CMTE_CITY", "CMTE_ST", "CMTE_ZIP", "CMTE_DSGN",
           "CMTE_TP", "CMTE_PTY_AFFILIATION", "CMTE_FILING_FREQ", "ORG_TP", "CONNECTED_ORG_NM", "CAND_ID"],
    "cn": ["CAND_ID", "CAND_NAME", "CAND_PTY_AFFILIATION", "CAND_ELECTION_YR", "CAND_OFFICE_ST", "CAND_OFFICE",
           "CAND_OFFICE_DISTRICT", "CAND_ICI", "CAND_STATUS", "CAND_PCC", "CAND_ST1", "CAND_ST2", "CAND_CITY",
           "CAND_ST", "CAND_ZIP"],
    "pas2": ["CMTE_ID", "AMNDT_IND", "RPT_TP", "TRANSACTION_PGI", "IMAGE_NUM", "TRANSACTION_TP", "ENTITY_TP", "NAME",
             "CITY", "STATE", "ZIP_CODE", "EMPLOYER", "OCCUPATION", "TRANSACTION_DT", "TRANSACTION_AMT", "OTHER_ID",
             "CAND_ID", "TRAN_ID", "FILE_NUM", "MEMO_CD", "MEMO_TEXT", "SUB_ID"],
}
AMT = {"H": "Repräsentantenhaus", "S": "Senat", "P": "Präsident"}


def _datei(name: str, jahr: int) -> pd.DataFrame:
    r = requests.get(BASIS.format(jahr=jahr, name=name, yy=str(jahr)[2:]), headers=HEADER, timeout=300)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        roh = z.read(z.namelist()[0]).decode("latin-1")
    return pd.read_csv(io.StringIO(roh), sep="|", header=None, names=SPALTEN[name], dtype=str, keep_default_na=False,
                       index_col=False)


def firmen_pacs(cm: pd.DataFrame, firmen: pd.DataFrame) -> pd.DataFrame:
    """PACs von Firmen (Art Q/N, Organisationstyp C) mit passender verbundener Organisation → Spalte kuerzel."""
    pacs = cm[cm["CMTE_TP"].isin(["Q", "N"]) & cm["ORG_TP"].eq("C") & cm["CONNECTED_ORG_NM"].ne("")]
    pac_woerter = [(p.CMTE_ID, p.CMTE_NM, _woerter(p.CONNECTED_ORG_NM)) for p in pacs.itertuples()]
    zeilen = []
    for f in firmen.itertuples():
        for fw in {frozenset(_woerter(f.sec_name)), frozenset(_woerter(f.name))}:
            zeilen += [{"kuerzel": f.kuerzel, "CMTE_ID": cid, "pac": name} for cid, name, k in pac_woerter
                       if fw and fw <= k and (k - fw) <= ZUSATZ]
    return pd.DataFrame(zeilen, columns=["kuerzel", "CMTE_ID", "pac"]).drop_duplicates(["kuerzel", "CMTE_ID"])


def fec_name(name: str) -> str:
    """'WITTMAN, ROBERT J. MR.' → 'Robert J. Wittman' (Anreden und Titel weg)."""
    nachname, _, vorname = str(name).partition(",")
    vorname = re.sub(r"\b(MR|MRS|MS|DR|REP|SEN|HON|THE|HONORABLE)\b\.?", "", vorname, flags=re.I)
    return re.sub(r"\s+", " ", f"{vorname} {nachname}").strip().title()


def laden() -> pd.DataFrame:
    firmen = pd.read_csv(DATEN / "us_firmen.csv")
    abg = pd.read_csv(DATEN / "abgeordnete.csv", dtype=str, keep_default_na=False)
    fec_zu_bioguide = {fid: b for b, ids in zip(abg["bioguide"], abg["fec"]) for fid in ids.split(";") if fid}
    name_offiziell = dict(zip(abg["bioguide"], abg["name"]))
    teile = []
    for jahr in ZYKLEN:
        cm, cn, pas2 = _datei("cm", jahr), _datei("cn", jahr), _datei("pas2", jahr)
        pacs = firmen_pacs(cm, firmen)
        z = pas2[pas2["TRANSACTION_TP"].eq("24K") & pas2["CAND_ID"].ne("")].merge(pacs, on="CMTE_ID")
        z["betrag"] = pd.to_numeric(z["TRANSACTION_AMT"], errors="coerce")
        g = (z.groupby(["kuerzel", "CAND_ID"]).agg(betrag=("betrag", "sum"), anzahl=("betrag", "size"),
                                                    pac=("pac", "first")).reset_index())
        kand = cn.drop_duplicates("CAND_ID").set_index("CAND_ID")
        g = g.assign(zyklus=jahr, partei=g["CAND_ID"].map(kand["CAND_PTY_AFFILIATION"]),
                     amt=g["CAND_ID"].map(kand["CAND_OFFICE"]).map(AMT),
                     bioguide=g["CAND_ID"].map(fec_zu_bioguide).fillna(""))
        # Offizieller Name, wenn als Abgeordnete(r) bekannt, sonst FEC-Name ohne Anrede („WITTMAN, ROBERT J. MR.“)
        g["kandidat"] = [name_offiziell.get(b) or fec_name(kand["CAND_NAME"].get(c, c))
                         for b, c in zip(g["bioguide"], g["CAND_ID"])]
        print(f"{jahr}: {len(pacs)} Firmen-PACs ({pacs['kuerzel'].nunique()} Firmen), {len(z)} Spenden, "
              f"{g['betrag'].sum() / 1e6:.1f} Mio. $, {(g['bioguide'] != '').mean():.0%} an Abgeordnete mit ID")
        teile.append(g)
    df = pd.concat(teile).rename(columns={"CAND_ID": "cand_id"})
    # Drei Dateien statt einer (Namen nicht in jeder Zeile wiederholen: 6,5 → ~2 MB im Repository)
    df[["kuerzel", "zyklus", "cand_id", "betrag", "anzahl"]].to_csv(ERGEBNIS, index=False)
    (df.sort_values("zyklus").drop_duplicates("cand_id", keep="last")[["cand_id", "bioguide", "kandidat", "partei", "amt"]]
     .to_csv(KANDIDATEN, index=False))
    df.drop_duplicates(["kuerzel", "zyklus", "pac"])[["kuerzel", "zyklus", "pac"]].to_csv(PACS, index=False)
    return df


def lesen() -> pd.DataFrame:
    """Spenden mit Kandidatendaten (bioguide, kandidat, partei, amt), wie laden() sie geliefert hat."""
    if not ERGEBNIS.exists():
        return pd.DataFrame(columns=["kuerzel", "zyklus", "cand_id", "betrag", "anzahl", "bioguide", "kandidat",
                                     "partei", "amt"])
    return pd.read_csv(ERGEBNIS).merge(pd.read_csv(KANDIDATEN, dtype=str, keep_default_na=False), on="cand_id")


if __name__ == "__main__":
    sys.exit(0 if len(laden()) else 1)
