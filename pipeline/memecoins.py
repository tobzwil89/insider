"""Neue Solana-Memecoins: Wie viel haben Entwickler, Bündel- und Sniper-Käufer beim Start genommen, und was wird daraus?

Vorbild Bubblemaps (Planungs-App #78). Quellen ohne Konto: DexScreener (neue Token-Profile, Marktwert),
solana-rpc.publicnode.com (Transaktionen).
  dev     = Ersteller (Unterzeichner der ersten Transaktion), Kauf im Startblock
  buendel = andere Käufer im selben Block wie der Start (meist dieselbe Person mit mehreren Adressen)
  sniper  = Käufer in den SNIPER_SLOTS Blöcken danach (~2 Sekunden, nur Bots schaffen das)
Anteile in % des Gesamtangebots. Nach 24 h und 7 Tagen wird der Marktwert nachgetragen → hängt ein hoher Anteil
mit späterem Absturz zusammen?

Läuft in der Action „Wale“ über wale_laden.py (alle 30 Min.) → daten/wale/memecoins.csv (30 Tage).
Herkunft: Probe ~/Desktop/Claude/sentiment-probe/memecoins.py (dort auch die Auswertung).
"""
import time
from datetime import datetime, timezone
import pandas as pd
import requests

from pipeline import DATEN

DATEI = DATEN / "wale" / "memecoins.csv"
TAGE_BEHALTEN = 30
RPC = "https://solana-rpc.publicnode.com"
SNIPER_SLOTS = 5
MAX_SEITEN = 100  # je 1.000 Signaturen; ältere/belebtere Token werden als „zu_alt“ markiert
SPALTEN = ["mint", "name", "gesehen", "erstellt", "dev", "dev_pct", "buendel_pct", "buendel_n", "sniper_pct",
           "sniper_n", "mc_start", "liq_start", "mc_24h", "mc_7t", "status"]


def rpc(methode, params):
    for i in range(5):
        try:
            r = requests.post(RPC, json=dict(jsonrpc="2.0", id=1, method=methode, params=params), timeout=60).json()
            if "result" in r:
                return r["result"]
            if r.get("error", {}).get("code") not in (429, -32429):  # echter Fehler: nicht wiederholen
                raise RuntimeError(f"{methode}: {r.get('error')}")
        except (requests.RequestException, ValueError):
            pass
        time.sleep(2 * (i + 1))
    raise RuntimeError(methode)


def dex(mints):
    """Marktwert und Liquidität (größtes Handelspaar) für bis zu 30 Token."""
    r = requests.get(f"https://api.dexscreener.com/tokens/v1/solana/{','.join(mints)}", timeout=60).json()
    raus = {}
    for p in sorted(r, key=lambda p: (p.get("liquidity") or {}).get("usd") or 0):
        raus[p["baseToken"]["address"]] = dict(name=p["baseToken"].get("symbol"), mc=p.get("marketCap") or p.get("fdv"),
                                               liq=(p.get("liquidity") or {}).get("usd"), erstellt=p.get("pairCreatedAt"))
    return raus


def startkaeufe(mint):
    """Ältere Signaturen bis zur ersten durchblättern, dann Käufe in den ersten Blöcken auswerten."""
    vor, alle = None, []
    for _ in range(MAX_SEITEN):
        p = {"limit": 1000} | ({"before": vor} if vor else {})
        seite = rpc("getSignaturesForAddress", [mint, p])
        alle += seite
        if len(seite) < 1000:
            break
        vor = seite[-1]["signature"]
    else:
        return None
    alle = [s for s in alle if s["err"] is None]
    start = alle[-1]["slot"]
    frueh = [s for s in reversed(alle) if s["slot"] <= start + SNIPER_SLOTS][:80]
    dev, menge, kaeufe = None, None, []
    for s in frueh:
        tx = rpc("getTransaction", [s["signature"], {"maxSupportedTransactionVersion": 1, "encoding": "jsonParsed"}])
        if not tx:
            continue
        signer = tx["transaction"]["message"]["accountKeys"][0]["pubkey"]
        if dev is None:  # Starttransaktion: Ersteller, Gesamtangebot = alle Bestände danach (getTokenSupply fehlt beim Knoten)
            dev = signer
            menge = sum(float(b["uiTokenAmount"]["uiAmount"] or 0) for b in tx["meta"]["postTokenBalances"]
                        if b["mint"] == mint)
        def bestand(liste):
            return sum(float(b["uiTokenAmount"]["uiAmount"] or 0) for b in liste
                       if b["mint"] == mint and b.get("owner") == signer)
        plus = bestand(tx["meta"]["postTokenBalances"]) - bestand(tx["meta"]["preTokenBalances"])
        if plus > 0:
            kaeufe.append((s["slot"], signer, plus))
    if not menge:  # Start nicht über eine Bonding Curve (z. B. Token woanders erzeugt, später gelistet)
        return dict(status="anderer_start")
    k = pd.DataFrame(kaeufe, columns=["slot", "signer", "plus"])
    ist_dev, im_start = k.signer == dev, k.slot == start
    pct = lambda x: round(100 * x.plus.sum() / menge, 2)
    return dict(dev=dev, dev_pct=pct(k[ist_dev]), buendel_pct=pct(k[im_start & ~ist_dev]),
                buendel_n=k[im_start & ~ist_dev].signer.nunique(), sniper_pct=pct(k[~im_start & ~ist_dev]),
                sniper_n=k[~im_start & ~ist_dev].signer.nunique())


def sammeln():
    df = pd.read_csv(DATEI) if DATEI.exists() else pd.DataFrame(columns=SPALTEN)
    jetzt = datetime.now(timezone.utc)
    neu = [x["tokenAddress"] for quelle in ("token-profiles/latest/v1", "token-boosts/latest/v1")
           for x in requests.get(f"https://api.dexscreener.com/{quelle}", timeout=60).json()
           if x.get("chainId") == "solana"]
    neu = [m for m in dict.fromkeys(neu) if m not in set(df.mint)]
    info = dex(neu[:30]) if neu else {}
    zeilen = []
    for m in neu[:30]:
        i = info.get(m, {})
        z = dict(mint=m, name=i.get("name"), gesehen=jetzt.isoformat(timespec="minutes"),
                 erstellt=pd.to_datetime(i["erstellt"], unit="ms", utc=True).isoformat(timespec="minutes")
                 if i.get("erstellt") else None, mc_start=i.get("mc"), liq_start=i.get("liq"))
        try:
            s = startkaeufe(m)
            z |= s if s else dict(status="zu_alt")
        except (RuntimeError, IndexError, KeyError, TypeError) as e:
            z["status"] = f"fehler {type(e).__name__}"
        zeilen.append(z)
    if zeilen:
        df = pd.concat([df, pd.DataFrame(zeilen)], ignore_index=True)
    # Marktwert nach 24 h / 7 Tagen nachtragen (0 = kein Handelspaar mehr = tot)
    alter = (jetzt - pd.to_datetime(df.gesehen, utc=True)).dt.total_seconds() / 3600
    for spalte, stunden in (("mc_24h", 24), ("mc_7t", 168)):
        faellig = df.index[df[spalte].isna() & (alter >= stunden)]
        for teil in [faellig[i:i + 30] for i in range(0, len(faellig), 30)]:
            werte = dex(list(df.loc[teil, "mint"]))
            df.loc[teil, spalte] = [(werte.get(m) or {}).get("mc") or 0 for m in df.loc[teil, "mint"]]
    df = df[pd.to_datetime(df.gesehen, utc=True) >= jetzt - pd.Timedelta(days=TAGE_BEHALTEN)]
    DATEI.parent.mkdir(parents=True, exist_ok=True)
    df[SPALTEN].to_csv(DATEI, index=False)
    print(f"{datetime.now():%Y-%m-%d %H:%M} memecoins: {len(zeilen)} neu, {len(df)} gesamt")
