"""Ein Durchlauf der Datenpipeline. Wird von der GitHub Action alle 30 Minuten aufgerufen.

    python3 lauf.py           nur rechnen, wenn die BaFin neue Meldungen hat
    python3 lauf.py --immer   immer neu rechnen (einmal täglich nach Börsenschluss,
                              damit die Ereignisfenster mit neuen Kurstagen wachsen)
"""

import argparse
import sys

import pandas as pd

from pipeline import DATEN, bafin, event_study as es, export
from pipeline.cluster import finde_cluster
from pipeline.kurse import lade_kurse
from pipeline.telegram import melde_neue_cluster


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--immer", action="store_true", help="auch ohne neue Meldungen neu rechnen")
    args = parser.parse_args()

    neu = bafin.aktualisieren()
    print(f"BaFin: {len(neu)} neue Meldungen")
    if neu.empty and not args.immer and (export.AUSGABE / "stand.json").exists():
        return 0

    meldungen = bafin.lade_meldungen()
    firmen = pd.read_csv(DATEN / "firmen.csv", dtype=str, keep_default_na=False)
    ereignisse = es.ereignisse(meldungen, firmen)

    mit_ticker = firmen[firmen["ticker"] != ""]
    start = min(meldungen["mitteilungsdatum"].min() - pd.Timedelta(days=220),
                pd.Timestamp.now() - pd.DateOffset(years=export.KURS_JAHRE, days=10))
    kurse = lade_kurse(list(mit_ticker["ticker"]) + list(mit_ticker["benchmark"]), start)
    print(f"Kurse: {kurse.shape[1]} Reihen bis {kurse.index.max():%d.%m.%Y}")

    ar = es.abnormale_renditen(ereignisse, kurse)
    cluster = finde_cluster(meldungen)
    print(f"Event Study: {ar['id'].nunique()} von {len(ereignisse)} Ereignissen ausgewertet, "
          f"{len(cluster)} Cluster-Käufe")

    export.exportiere(meldungen, firmen, kurse, ereignisse, ar, cluster)
    print("JSON geschrieben nach docs/data/")
    melde_neue_cluster(cluster, dict(zip(mit_ticker["isin"], mit_ticker["ticker"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
