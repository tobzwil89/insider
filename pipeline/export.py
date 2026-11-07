"""Schreibt die Ergebnisse als JSON nach docs/data/ für die statische Website.

    stand.json            Zeitpunkt der Berechnung, Kennzahlen, Methodenparameter
    neueste.json          die letzten Meldungen aller Emittenten (Teilausführungen zusammengefasst)
    cluster.json          erkannte Cluster-Käufe
    caar.json             AAR/CAAR-Kurven für Käufe und Verkäufe
    ereignisse.json       alle ausgewerteten Ereignisse mit CAR
    firmen.json           Übersicht der Firmen mit eigener Seite
    ranking.json          Insider mit dem besten Timing (Überrendite 3 Monate nach Käufen)
    kurse/<TICKER>.json   je Firma: Schlusskurse als [Datum, Kurs] für das Diagramm
    (neueste.json und ranking.json haben eine Spalte seite = Adresse der Personenseite oder null)

Außerdem (pipeline/seiten.py): docs/firma/<TICKER>/index.html als fertige Seite je Firma (mit Großaktionären
aus daten/stimmrechte.csv),
docs/person/<name>/index.html je Vorstand/Aufsichtsrat (pipeline/personen.py), docs/person/index.html,
docs/sitemap.xml und Versionsnummern (?v=) für CSS/JS.
"""

import json
import math
import re
import shutil

import numpy as np
import pandas as pd

from pipeline import AUSGABE, DATEN, event_study as es, cluster as cl, fonds_us, gurus, personen as ps, politiker as pol, ranking as rk, rueckkaeufe, seiten, spenden, stimmrechte, us_firmen

NEUESTE = 300        # so viele Meldungen im Live-Ticker
KURS_JAHRE = 10      # so weit reicht der Kursverlauf auf den Firmenseiten (ab Beginn der Historie)


def _sauber(x):
    """Macht pandas/numpy-Werte JSON-tauglich (NaN → null, Datum → Text)."""
    if isinstance(x, dict):
        return {k: _sauber(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, np.ndarray)):
        return [_sauber(v) for v in x]
    if isinstance(x, pd.Timestamp):
        return None if pd.isna(x) else (x.strftime("%Y-%m-%d") if x == x.normalize()
                                        else x.strftime("%Y-%m-%d %H:%M:%S"))
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return None if math.isnan(x) else round(float(x), 6)
    if x is pd.NaT:
        return None
    return x


def _schreibe(name: str, inhalt) -> None:
    pfad = AUSGABE / name
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(json.dumps(_sauber(inhalt), ensure_ascii=False, separators=(",", ":")),
                    encoding="utf-8")


def _zeilen(df: pd.DataFrame) -> list:
    return df.to_dict(orient="records")


def meldungen_zusammenfassen(m: pd.DataFrame, weitere: tuple = ()) -> pd.DataFrame:
    """Teilausführungen derselben Person am selben Mitteilungstag zu einer Zeile zusammenfassen.
    weitere: zusätzliche Spalten, die mitkommen (erster Wert)."""
    m = m.assign(stueck=m["volumen"] / m["preis"])
    g = (m.groupby(["isin", "person", "art", "instrument", "mitteilungsdatum"], dropna=False)
         .agg(emittent=("emittent", "first"), position=("position", "first"),
              waehrung=("waehrung", "first"), volumen=("volumen", "sum"), stueck=("stueck", "sum"),
              geschaeftsdatum=("geschaeftsdatum", "min"), aktiviert=("aktiviert", "max"),
              teilausfuehrungen=("person", "size"), **{s: (s, "first") for s in weitere})
         .reset_index())
    # Durchschnittspreis gewichtet nach Stückzahl; ohne Preisangabe bleiben Preis und Volumen leer
    g["preis"] = (g["volumen"] / g["stueck"]).where(g["stueck"] > 0)
    g["volumen"] = g["volumen"].where(g["stueck"] > 0)
    return g.drop(columns="stueck").sort_values("aktiviert", ascending=False, ignore_index=True)


def exportiere(meldungen: pd.DataFrame, firmen: pd.DataFrame, kurse: pd.DataFrame,
               ereignisse: pd.DataFrame, ar: pd.DataFrame, cluster: pd.DataFrame,
               rangliste: pd.DataFrame) -> None:
    mit_seite = firmen[firmen["ticker"] != ""]
    isin_zu_ticker = dict(zip(mit_seite["isin"], mit_seite["ticker"]))
    zusammen = meldungen_zusammenfassen(meldungen)
    zusammen["ticker"] = zusammen["isin"].map(isin_zu_ticker)

    caar = es.zusammenfassung(ar)
    car = es.car_je_ereignis(ar) if not ar.empty else pd.DataFrame(columns=["id", "car", "car_ab_0", "tage_nach"])
    ausgewertet = ereignisse.merge(car, on="id")

    _schreibe("stand.json", {
        "berechnet": pd.Timestamp.now(tz="Europe/Berlin").strftime("%Y-%m-%d %H:%M:%S"),
        "letzte_meldung": meldungen["aktiviert"].max(),
        "meldungen_seit": meldungen["mitteilungsdatum"].min(),
        "anzahl_meldungen": len(meldungen), "anzahl_ereignisse": len(ausgewertet),
        "letzter_kurstag": kurse.index.max(),
        "methode": {"modell": "Marktmodell (DAX bzw. MDAX)", "ereignisfenster": es.EREIGNISFENSTER,
                    "schaetzfenster": es.SCHAETZFENSTER, "min_schaetztage": es.MIN_SCHAETZTAGE,
                    "positionen": sorted(es.POSITIONEN), "cluster_tage": cl.FENSTER_TAGE,
                    "cluster_personen": cl.MIN_PERSONEN, "cluster_volumen": cl.MIN_VOLUMEN,
                    "ranking_tage": rk.TAGE, "ranking_min_kaeufe": rk.MIN_KAEUFE},
    })
    # Personenseiten (nur Vorstand und Aufsichtsrat, pipeline/personen.py); Adressen auch für Links im Ticker und Ranking
    leute = ps.personen(meldungen_zusammenfassen(ps.zuordnen(meldungen, firmen),
                                                 ("traeger", "traeger_position", "ueber")), firmen, kurse, rangliste)
    adressen = {p["schluessel"]: p["adresse"] for p in leute}

    def seite_von(name, position=None):
        return adressen.get(rk.schluessel(name)) if position is None or position in ps.POSITIONEN else None

    _schreibe("neueste.json", _zeilen(zusammen.head(NEUESTE).assign(
        # nur DAX/MDAX: ein gleichnamiger Vorstand einer anderen Firma ist meist eine andere Person
        seite=lambda d: [seite_von(n, p) if isinstance(t, str) else None
                         for n, p, t in zip(d["person"], d["position"], d["ticker"])])))
    _schreibe("cluster.json", _zeilen(cluster.assign(ticker=cluster["isin"].map(isin_zu_ticker))))
    _schreibe("caar.json", {art: _zeilen(teil.drop(columns="art"))
                            for art, teil in caar.groupby("art")} if not caar.empty else {})
    _schreibe("ranking.json", _zeilen(rangliste.assign(seite=[seite_von(n) for n in rangliste["person"]])))
    # Nicht mehr genutzte Dateien früherer Versionen entfernen
    (AUSGABE / "ereignisse.json").unlink(missing_ok=True)
    shutil.rmtree(AUSGABE / "firmen", ignore_errors=True)

    v = seiten.versionen()
    seiten.versionen_eintragen(v)
    rang = rangliste.assign(rang=range(1, len(rangliste) + 1))
    kurs_start = kurse.index.max() - pd.DateOffset(years=KURS_JAHRE)
    aktionaere = stimmrechte.grossaktionaere(pd.read_csv(DATEN / "stimmrechte.csv"),
                                             pd.read_csv(DATEN / "grossaktionaere_geprueft.csv"))
    ea_datei = DATEN / "stimmrechte_eigene_aktien.csv"
    eigene_aktien = stimmrechte.eigene_aktien(pd.read_csv(ea_datei)).set_index("firma").to_dict("index") if ea_datei.exists() else {}
    # Daten für den Aktionärsring: US-Fonds (SEC N-PORT), Norwegischer Staatsfonds, Aktien je Gattung
    fu_datei, nb_datei = DATEN / "fonds_us.csv", DATEN / "norwegen.csv"
    fonds = pd.read_csv(fu_datei) if fu_datei.exists() else pd.DataFrame(columns=["isin", "gesellschaft", "stueck", "stichtag"])
    norwegen = pd.read_csv(nb_datei).set_index("firma").to_dict("index") if nb_datei.exists() else {}
    gattungen = pd.read_csv(DATEN / "aktiengattungen.csv").set_index("isin").to_dict("index")
    st_roh = pd.read_csv(DATEN / "stimmrechte.csv", usecols=["firma", "veroeffentlicht", "gesamtstimmrechte"])
    gesamt = st_roh.dropna(subset=["gesamtstimmrechte"]).sort_values("veroeffentlicht").groupby("firma")["gesamtstimmrechte"].last()
    isins_je_firma = firmen.groupby("name")["isin"].apply(list)

    def ring_daten(name: str, isin: str) -> dict:
        """Alles, was seiten.aktionaersring für eine Seite braucht. Bei Firmen mit Stamm- und Vorzugsaktien
        (daten/aktiengattungen.csv) zeigt der Ring die Gattung der Seite: Stammaktien mit Großaktionären,
        Vorzugsaktien ohne (Stimmrechtsmitteilungen gibt es nur für Stimmrechte). Der Norwegische Staatsfonds nennt
        nur einen Anteil je Firma, nicht je Gattung → dort weggelassen."""
        ga = aktionaere[aktionaere["firma"] == name]
        halter = list(ga["halter"]) + list(ga["weitere"].dropna())
        g = gattungen.get(isin)
        if g is None or g["gattung"] == "einzig":  # eine Gattung (Fresenius/TUI haben zusätzlich eine alte ISIN)
            nb = norwegen.get(name)
            if nb and any(re.search(r"norw|norges", h, re.I) for h in halter):
                nb = None  # schon als Großaktionär gemeldet
            anzahl = g["stueck"] if g is not None else gesamt.get(name)
            return {"aktionaere": ga, "eigene": eigene_aktien.get(name), "norwegen": nb, "gattung": None,
                    "fonds": fonds_us.je_firma(fonds[fonds["isin"].isin(isins_je_firma[name])], halter, anzahl)}
        anzahl = g["stueck"] if pd.notna(g["stueck"]) else None
        eigene = ({"anteil": 100 * g["eigene"] / anzahl, "schwellendatum": g["stand"], "url": g["quelle"]}
                  if anzahl and pd.notna(g.get("eigene")) else None)
        f_gattung = fonds[fonds["isin"] == isin]
        if g["gattung"] == "vorzug":
            return {"aktionaere": ga.iloc[0:0], "eigene": eigene, "norwegen": None, "gattung": "vorzug",
                    "fonds": fonds_us.je_firma(f_gattung, [], anzahl), "stamm_aktionaere": ga}
        return {"aktionaere": ga, "eigene": eigene or eigene_aktien.get(name), "norwegen": None, "gattung": "stamm",
                "fonds": fonds_us.je_firma(f_gattung, halter, anzahl)}
    # Rückkäufe nur für Firmen, deren Historie fertig geladen ist (sonst hieße „keine“ nur „noch nicht geladen“)
    rk_datei, rk_fertig = DATEN / "rueckkaeufe.csv", DATEN / "rueckkaeufe_fortschritt.csv"
    rueck = rueckkaeufe.jahre(pd.read_csv(rk_datei)) if rk_datei.exists() else pd.DataFrame(columns=["firma"])
    rk_fortschritt = pd.read_csv(rk_fertig) if rk_fertig.exists() else pd.DataFrame(columns=["name", "meldungen"])
    rk_geladen = set(rk_fortschritt["name"])
    # Firmen, für die EQS gar keine Meldungen dieser Kategorie führt (z. B. BMW, anderer Verteiler):
    # dort heißt „nichts gefunden“ nur „keine Daten“, nicht „keine Rückkäufe“
    rk_ohne = set(rk_fortschritt.loc[rk_fortschritt["meldungen"].eq(0), "name"]) - set(rueck["firma"])
    # Finanzkennzahlen nur, wenn lokal berechnet (daten/kennzahlen.csv steht in .gitignore → nie in der Action)
    kz_datei = DATEN / "kennzahlen.csv"
    kz = {r["isin"]: r for r in pd.read_csv(kz_datei).to_dict("records")} if kz_datei.exists() else {}
    uebersicht = []
    for ticker, f in mit_seite.groupby("ticker"):
        eigene = zusammen[zusammen["ticker"] == ticker]
        verlauf = kurse[ticker].dropna() if ticker in kurse else pd.Series(dtype=float)
        verlauf = verlauf[verlauf.index >= kurs_start]
        _schreibe(f"kurse/{ticker}.json", [[d, round(float(p), 2)] for d, p in verlauf.items()])
        stamm = {"ticker": ticker, "name": f["name"].iloc[0], "index": f["index"].iloc[0],
                 "benchmark": f["benchmark"].iloc[0], "isins": list(f["isin"])}
        letzter = (verlauf.index[-1], verlauf.iloc[-1]) if len(verlauf) else None
        seiten.schreiben(seiten.DOCS / "firma" / ticker / "index.html", seiten.firmenseite(
            stamm, eigene, ausgewertet[ausgewertet["ticker"] == ticker], rang[rang["ticker"] == ticker], letzter, v,
            aktionaere[aktionaere["firma"] == stamm["name"]],
            rueck[rueck["firma"] == stamm["name"]] if stamm["name"] in rk_geladen else None,
            next((kz[i] for i in stamm["isins"] if i in kz), None), stamm["name"] in rk_ohne,
            ring_daten(stamm["name"], stamm["isins"][0]), adressen))
        uebersicht.append({"ticker": ticker, "name": stamm["name"], "index": stamm["index"],
                           "logo": seiten.logo_datei(stamm["isins"]),
                           "meldungen": len(eigene),
                           "letzte_meldung": eigene["mitteilungsdatum"].max() if len(eigene) else None})
    _schreibe("firmen.json", sorted(uebersicht, key=lambda x: x["name"].lower()))
    # Seiten von Firmen entfernen, die nicht mehr im Index sind
    for ordner in (seiten.DOCS / "firma").iterdir():
        if ordner.name not in set(mit_seite["ticker"]):
            shutil.rmtree(ordner)
    depots = gurus.alle_depots()
    for d in depots:
        seiten.schreiben(seiten.DOCS / "gurus" / seiten.kurzname(d["name"]) / "index.html", seiten.guruseite(d, v))
    if depots:
        seiten.schreiben(seiten.DOCS / "gurus" / "index.html", seiten.gurus_uebersicht(depots, v))
    guru_adressen = ["gurus/"] + [f"gurus/{seiten.kurzname(d['name'])}/" for d in depots] if depots else []
    # Personenseiten jedes Mal ganz neu (Personen ohne Geschäfte mehr im Index fallen so weg)
    shutil.rmtree(seiten.DOCS / "person", ignore_errors=True)
    for p in leute:
        seiten.schreiben(seiten.DOCS / "person" / p["adresse"] / "index.html", seiten.personenseite(p, v))
    if leute:
        seiten.schreiben(seiten.DOCS / "person" / "index.html", seiten.personen_uebersicht(leute, v))
    personen_adressen = ["person/"] + [f"person/{p['adresse']}/" for p in leute] if leute else []
    spenden_alle = spenden.lesen()
    abgeordnete = kongress_exportieren(v, spenden_alle)
    us_adressen = us_exportieren(v, spenden_alle, abgeordnete)
    # Politikerseiten nicht in die Sitemap: sie entstehen nur lokal
    (seiten.DOCS / "sitemap.xml").write_text(seiten.sitemap(sorted(mit_seite["ticker"].unique()),
                                                            guru_adressen + personen_adressen + us_adressen),
                                             encoding="utf-8")


def us_exportieren(v: dict, spenden_alle: pd.DataFrame, abgeordnete: list) -> list:
    """Seiten der US-Firmen (docs/us/) aus daten/us_firmen.csv, staatsauftraege*.csv, spenden*.csv. Die Geschäfte von
    Abgeordneten kommen nur dazu, wenn die Politikerseiten (lokal) gebaut wurden. Gibt die Adressen für die Sitemap."""
    ziel = seiten.DOCS / "us"
    shutil.rmtree(ziel, ignore_errors=True)
    if not (DATEN / "us_firmen.csv").exists():
        return []
    firmen = pd.read_csv(DATEN / "us_firmen.csv")
    sa_datei, zu_datei = DATEN / "staatsauftraege.csv", DATEN / "staatsauftraege_zuordnung.csv"
    sa = pd.read_csv(sa_datei) if sa_datei.exists() else pd.DataFrame(columns=["kuerzel", "geschaeftsjahr", "betrag"])
    zu = pd.read_csv(zu_datei, keep_default_na=False) if zu_datei.exists() else pd.DataFrame(columns=["kuerzel", "empfaenger"])
    empfaenger = dict(zip(zu["kuerzel"], zu["empfaenger"]))
    politiker = {p["bioguide"]: p["adresse"] for p in abgeordnete}
    kongress = None
    if abgeordnete:
        kongress = pd.concat([p["geschaefte"].assign(adresse=p["adresse"]) for p in abgeordnete])
        kongress = kongress[kongress["anlageart"].eq("ST")]
        kongress = kongress.assign(firma=kongress["symbol"].replace(us_firmen.ZWEITE_GATTUNG))
    gj = seiten._us_geschaeftsjahr()
    zeilen = []
    for f in firmen.to_dict("records"):
        auftraege = dict(zip(*(sa.loc[sa["kuerzel"] == f["kuerzel"], s] for s in ["geschaeftsjahr", "betrag"])))
        sp = spenden_alle[spenden_alle["kuerzel"] == f["kuerzel"]]
        k = kongress[kongress["firma"] == f["kuerzel"]] if kongress is not None else None
        seiten.schreiben(ziel / f["kuerzel"] / "index.html", seiten.us_firmenseite(
            f, auftraege, empfaenger.get(f["kuerzel"], ""), sp, k, politiker, v))
        zeilen.append({**f, "auftraege": auftraege.get(gj - 1), "spenden": sp.loc[sp["zyklus"] == 2024, "betrag"].sum(),
                       "kongress": len(k) if k is not None else 0})
    zeilen.sort(key=lambda z: -(z["auftraege"] or 0))
    seiten.schreiben(ziel / "index.html", seiten.us_uebersicht(zeilen, kongress is not None, v))
    print(f"US-Firmen: {len(zeilen)} Seiten, {sum(1 for z in zeilen if z['auftraege'])} mit Staatsaufträgen, "
          f"{sum(1 for z in zeilen if z['spenden'])} mit PAC-Spenden")
    return ["us/"] + [f"us/{z['kuerzel']}/" for z in zeilen]


def kongress_exportieren(v: dict, spenden_alle: pd.DataFrame) -> list:
    """Seiten der US-Abgeordneten (docs/politiker/), nur wenn daten/kongress.csv lokal existiert. Die Datei steht
    vorerst in .gitignore (Nutzungsbeschränkung nach 5 U.S.C. app. § 105(c) erst klären) → die Action baut nichts.
    Gibt die Personen zurück (für die US-Firmenseiten), sonst eine leere Liste."""
    datei = DATEN / "kongress.csv"
    ziel = seiten.DOCS / "politiker"
    shutil.rmtree(ziel, ignore_errors=True)
    if not datei.exists():
        return []
    k = pd.read_csv(datei, dtype=str, keep_default_na=False)
    # Älteres Formular 2014 – Mitte 2022, mit DeepSeek gelesen (kongress_altformat.py), falls vorhanden
    alt_datei, alt_fertig = DATEN / "kongress_alt.csv", DATEN / "kongress_alt_fortschritt.csv"
    if alt_datei.exists():
        k = pd.concat([k, pd.read_csv(alt_datei, dtype=str, keep_default_na=False)], ignore_index=True)
    alt_gelesen = set(pd.read_csv(alt_fertig, dtype=str)["doc_id"]) if alt_fertig.exists() else set()
    for s in ["datum", "gemeldet", "eingereicht"]:
        k[s] = pd.to_datetime(k[s], errors="coerce")
    for s in ["betrag_von", "betrag_bis"]:
        k[s] = pd.to_numeric(k[s], errors="coerce")
    abg = pd.read_csv(pol.ABGEORDNETE, dtype={"bezirk": "Int64"}) if pol.ABGEORDNETE.exists() else pol.abgeordnete_laden()
    z = pol.zuordnen(k, abg)
    symbole = sorted({s for s in z.loc[z["anlageart"].eq("ST"), "kuerzel"].map(pol.yahoo) if s})
    kurse = pol.kurse([pol.INDEX] + symbole, z["datum"].min() - pd.Timedelta(days=10))
    leute = pol.politiker(z, kurse)
    fs = pd.read_csv(DATEN / "kongress_fortschritt.csv", dtype=str, keep_default_na=False)
    fs = fs[fs["status"].isin(["scan", "alt"]) & ~fs["doc_id"].isin(alt_gelesen)].assign(eingereicht=lambda d: pd.to_datetime(d["eingereicht"], errors="coerce"))
    scans = pol.zuordnen(fs, abg).assign(url=lambda d: [pol.kongress.pdf_url(j, i) for j, i in zip(d["jahr"], d["doc_id"])])
    us_namen = dict(pd.read_csv(DATEN / "us_firmen.csv")[["kuerzel", "name"]].values) if (DATEN / "us_firmen.csv").exists() else {}
    for p in leute:
        p["scans"] = scans[scans["bioguide"] == p["bioguide"]].sort_values("eingereicht", ascending=False)
        p["spenden_html"] = seiten.politiker_spenden(spenden_alle[spenden_alle["bioguide"] == p["bioguide"]], us_namen)
        seiten.schreiben(ziel / p["adresse"] / "index.html", seiten.politikerseite(p, v))
    if leute:
        adresse = {p["bioguide"]: p["adresse"] for p in leute}
        alle = pd.concat([p["geschaefte"] for p in leute])
        neueste = alle.sort_values(["eingereicht", "datum"], ascending=False).head(150)
        seiten.schreiben(ziel / "index.html", seiten.politiker_uebersicht(
            leute, neueste.assign(adresse=neueste["bioguide"].map(adresse)), v))
    print(f"Kongress: {len(leute)} Abgeordnete, {len(z)} Transaktionen, Kurse für {kurse.shape[1]} Symbole")
    return leute
