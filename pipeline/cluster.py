"""Cluster-Käufe: mehrere Führungskräfte einer Firma kaufen innerhalb weniger Tage.

Regel: mindestens 3 verschiedene Personen (Vorstand, Aufsichtsrat, sonstige Führungsperson)
kaufen Aktien innerhalb von 14 Tagen, gemessen am Geschäftsdatum. Eng verbundene Personen
zählen nicht mit, weil sie oft nur die Holding eines Vorstands sind. Überlappende Fenster
werden zu einem Cluster zusammengefasst. Gilt für alle Emittenten, nicht nur DAX/MDAX.
Unter 50.000 € Gesamtvolumen zählt es nicht: Das sind fast immer Mitarbeiter-Aktienprogramme
(z. B. ProCredit: jeden Monat dieselben 5 Personen mit zusammen rund 17.600 €).
"""

import pandas as pd

FENSTER_TAGE = 14
MIN_PERSONEN = 3
MIN_VOLUMEN = 50_000


def finde_cluster(meldungen: pd.DataFrame) -> pd.DataFrame:
    kaeufe = meldungen[meldungen["instrument"].eq("Aktie") & meldungen["art"].eq("Kauf")
                       & meldungen["position"].ne("in enger Beziehung")]
    cluster = []
    for isin, g in kaeufe.groupby("isin"):
        g = g.sort_values("geschaeftsdatum")
        datum = g["geschaeftsdatum"].to_numpy()
        person = g["person"].to_numpy()
        im_cluster = pd.Series(False, index=g.index)
        for i in range(len(g)):
            fenster = (datum >= datum[i]) & (datum < datum[i] + pd.Timedelta(days=FENSTER_TAGE))
            if len(set(person[fenster])) >= MIN_PERSONEN:
                im_cluster[fenster] = True
        teil = g[im_cluster.to_numpy()]
        if teil.empty:
            continue
        # Neuer Cluster, wenn zwischen zwei Käufen mehr als ein ganzes Fenster liegt
        nummer = (teil["geschaeftsdatum"].diff().dt.days >= FENSTER_TAGE).cumsum()
        for _, c in teil.groupby(nummer):
            if c["volumen"].sum() < MIN_VOLUMEN:
                continue
            cluster.append({
                "id": f"{isin}_{c['geschaeftsdatum'].min():%Y%m%d}",
                "isin": isin, "emittent": c["emittent"].iloc[0],
                "von": c["geschaeftsdatum"].min(), "bis": c["geschaeftsdatum"].max(),
                "bekannt_seit": c["mitteilungsdatum"].max(),
                "personen": sorted(set(c["person"])), "volumen": c["volumen"].sum(),
                "meldungen": len(c),
            })
    spalten = ["id", "isin", "emittent", "von", "bis", "bekannt_seit", "personen", "volumen", "meldungen"]
    return pd.DataFrame(cluster, columns=spalten).sort_values("bekannt_seit", ascending=False,
                                                                ignore_index=True)
