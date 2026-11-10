"""Wal-Bewegungen: große Überweisungen von Bitcoin, Ethereum, XRP und den Reddit-Coins auf Ethereum, dazu die
Start-Prüfung neuer Solana-Memecoins (pipeline/memecoins.py). Läuft in der Action „Wale“ nach jedem Lauf von
„Daten aktualisieren“ (alle 30 Min.) und macht dort weiter, wo der letzte Lauf aufgehört hat (daten/wale/stand.json).

Kein Kaufsignal: Die Rückschau (sentiment-probe, 10.11.2026) fand vor Reddit-Schüben keine auffälligen Börsenflüsse.
Die Funktion zeigt, was große Adressen tun, nicht, was der Kurs tun wird.

Quellen ohne Konto: Ethereum rpc.mevblocker.io, Bitcoin mempool.space (Blockhöhe) + blockchain.info (ganzer Block),
XRP xrplcluster.com, Kurse CoinGecko. Adressnamen: daten/wale/adressen.csv aus eth-labels (MIT, von Etherscan
abgeschrieben → vor dem Start klären) und xrpscan „well-known“; Bitcoin ohne Namen (einzige offene Liste, Dune
Spellbook, verbietet bis 03.03.2027 die Nutzung für Datenplattformen).

Typ: rein = an eine Börse (möglicher Verkauf), raus = von einer Börse (Abzug), wal = keine Börse beteiligt.
Börse → Börse wird weggelassen.

    python3 wale_laden.py              ein Lauf → docs/data/wale.json (48 h), daten/wale/tagesfluss.csv (dauerhaft)
    python3 wale_laden.py --adressen   Adressnamen neu bauen (selten, z. B. vierteljährlich)
"""
import argparse
import io
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

from pipeline import AUSGABE, DATEN, HEADER, memecoins

ORDNER = DATEN / "wale"
STAND, FLUSS, ADRESSEN = ORDNER / "stand.json", ORDNER / "tagesfluss.csv", ORDNER / "adressen.csv"
JSON = AUSGABE / "wale.json"
ETH_RPC = "https://rpc.mevblocker.io"  # liefert auch eth_getLogs über viele Blöcke
# Ganze Blöcke reihum: jeder Knoten sperrt nach ~120 schnellen Abrufen (Cloudflare 429)
ETH_BLOECKE = ["https://ethereum-rpc.publicnode.com", "https://eth.drpc.org", "https://rpc.mevblocker.io"]
XRP_SERVER = ["https://xrplcluster.com", "https://s1.ripple.com:51234", "https://s2.ripple.com:51234"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
GROSS, KLEIN = 5_000_000, 250_000  # USD-Schwelle: BTC/ETH/XRP bzw. kleinere Token
FENSTER = timedelta(hours=48)
HOECHSTENS = {"eth": 900, "btc": 8, "xrp": 900}  # XRP ~515 Ledger je 30 Min., ~0,5 s je Ledger  # je Lauf; liegt der Stand weiter zurück, wird übersprungen
NATIV = {"BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple"}
TOKEN = {  # Reddit-Coins, die auf Ethereum leben: Kürzel → (Vertrag, CoinGecko-ID)
    "AAVE": ("0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9", "aave"),
    "AMP": ("0xff20817765cb7f73d4bde2e66e067e58d11095c2", "amp-token"),
    "ARB": ("0xb50721bcf8d664c30412cfbc6cf7a15145234ad1", "arbitrum"),
    "CYBER": ("0x14778860e937f509e651192a90589de711fb88a9", "cyberconnect"),
    "ENS": ("0xc18360217d8f7ab5e7c516566761ea12ce7f9d72", "ethereum-name-service"),
    "FET": ("0xaea46a60368a7bd060eec7df8cba43b7ef41ad85", "fetch-ai"),
    "FLOKI": ("0xcf0c122c6b73ff809c693db761e7baebe62b6a2e", "floki"),
    "GRT": ("0xc944e90c64b2c07662a292be6244bdf05cda44a7", "the-graph"),
    "LINK": ("0x514910771af9ca656af840dff83e8264ecf986ca", "chainlink"),
    "MAGIC": ("0xb0c7a3ba49c7a6eaba6cd4a96c55a1391070ac9a", "magic"),
    "ONDO": ("0xfaba6f8e4a5e8ab82f62fe7c39859fa577269be3", "ondo-finance"),
    "PEPE": ("0x6982508145454ce325ddbe47a25d4ec3d2311933", "pepe"),
    "POL": ("0x455e53cbb86018ac2b8092fdcd39d8444affc3f6", "polygon-ecosystem-token"),
    "QNT": ("0x4a220e6096b25eadb88358cb44068a3248254675", "quant-network"),
    "RED": ("0xc43c6bfeda065fe2c4c11765bf838789bd0bb5de", "redstone-oracles"),
    "SHIB": ("0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce", "shiba-inu"),
    "TURBO": ("0xa35923162c49cf95e6bf26623385eb431ad920d3", "turbo"),
    "UNI": ("0x1f9840a85d5af5bf1d1762f925bdaddc4201f984", "uniswap"),
    "WLD": ("0x163f8c2467924be0ae7b5347228cabf260318753", "worldcoin-wld"),
    "WLFI": ("0xda5e1988097297dcdc1f90d4dfe7909e847cbef6", "world-liberty-financial"),
}
VERTRAG = {v: k for k, (v, _) in TOKEN.items()}
BOERSEN = ["Binance", "Coinbase", "Kraken", "OKX", "OKEx", "Bitfinex", "KuCoin", "Bybit", "Gate.io", "Huobi", "HTX",
           "Bitget", "Crypto.com", "Upbit", "Bithumb", "Gemini", "Bitstamp", "MEXC", "Bitvavo", "Robinhood", "Poloniex",
           "Bittrex", "Bitpanda", "Deribit", "FTX", "WhiteBIT", "HitBTC", "Korbit", "Coinone", "BtcTurk", "bitFlyer",
           "Uphold", "BTC Markets", "Bitso", "Bitrue", "LBank", "BingX", "CoinDCX", "WazirX", "Coincheck"]
PROTOKOLLE = {"dex", "defi", "bridge", "layer-2", "uniswap", "sushiswap", "balancer", "bancor", "curve-finance",
              "curve-fi", "pancakeswap", "kyberswap", "1inch", "0x-protocol", "cow-protocol", "paraswap", "aave", "compound",
              "lido", "maker", "sky", "yearn", "pendle", "mev-bot", "wrapped-ether"}
IST_BOERSE = re.compile(r"^(" + "|".join(re.escape(b) for b in BOERSEN) + r")\b", re.I)


class ZuVieleTreffer(Exception):
    """eth_getLogs mit mehr als 10.000 Treffern; args[0] = letzter Block, den der Knoten vorschlägt."""


def rpc(url, methode, params, versuche=4):
    fehler = None
    for i in range(versuche):
        try:
            r = requests.post(url, json={"jsonrpc": "2.0", "id": 1, "method": methode, "params": params},
                              headers=HEADER, timeout=90).json()
            if "result" in r:
                return r["result"]
            fehler = r.get("error")
            if isinstance(fehler, dict) and fehler.get("code") == -32005 and "to" in (fehler.get("data") or {}):
                raise ZuVieleTreffer(int(fehler["data"]["to"], 16))
        except (requests.RequestException, ValueError) as e:
            fehler = e
        time.sleep(2 * (i + 1))
    raise RuntimeError(f"{methode}: {fehler}")


def xrp(methode, params, start=0):
    """XRP-Server haben ein eigenes Format (params als Liste mit einem Objekt). Jeder Server sperrt schon bei wenigen
    gleichzeitigen Abrufen („tooBusy“) → Last reihum verteilen, bei Fehler den nächsten Server nehmen."""
    for i in range(6):
        server = XRP_SERVER[(start + i) % len(XRP_SERVER)]
        try:
            r = requests.post(server, json={"method": methode, "params": [params]}, headers=HEADER, timeout=90).json()
            if r.get("result", {}).get("status") == "success":
                return r["result"]
        except (requests.RequestException, ValueError):
            pass
        time.sleep(1 + i)
    raise RuntimeError(f"xrp {methode}")


# --- Adressnamen -----------------------------------------------------------------------------------

def adressen_bauen():
    """eth-labels (Ethereum: Börsen + Protokolle) + xrpscan well-known (XRP, alle Namen) → daten/wale/adressen.csv."""
    roh = requests.get("https://raw.githubusercontent.com/dawsbot/eth-labels/v1/data/csv/accounts.csv",
                       headers=HEADER, timeout=300).text
    e = pd.read_csv(io.StringIO(roh), dtype=str)
    e = e[(e.chainId == "1") & e.nameTag.fillna("").str.match(IST_BOERSE)]
    e = e[~e.nameTag.str.contains("Exploit|Hack|Phish|Token|Charity|Bridge|Contract|Deployer|Validator|Staking|Pool",
                                  case=False)]
    eth = pd.DataFrame({"kette": "eth", "adresse": e.address.str.lower(), "name": e.nameTag})
    # Protokolle (dezentrale Börsen, Kreditmärkte, Brücken), damit ein Tausch nicht als anonymer Wal erscheint
    alle = pd.read_csv(io.StringIO(roh), dtype=str)
    pr = alle[(alle.chainId == "1") & alle.label.isin(PROTOKOLLE) & alle.nameTag.notna()]
    eth = pd.concat([eth, pd.DataFrame({"kette": "eth", "adresse": pr.address.str.lower(), "name": pr.nameTag})])
    x = requests.get("https://api.xrpscan.com/api/v1/names/well-known", headers=HEADER, timeout=120).json()
    xr = pd.DataFrame([{"kette": "xrp", "adresse": a["account"], "name": a["name"]} for a in x if a.get("account")])
    df = pd.concat([eth, xr]).drop_duplicates(["kette", "adresse"])
    df["boerse"] = df.name.str.match(IST_BOERSE)
    ORDNER.mkdir(parents=True, exist_ok=True)
    df.to_csv(ADRESSEN, index=False)
    b = df.groupby("kette").boerse.agg(["size", "sum"])
    print(f"Adressen: Ethereum {b.loc['eth', 'size']} ({b.loc['eth', 'sum']} Börsen), XRP {b.loc['xrp', 'size']} ({b.loc['xrp', 'sum']} Börsen)")


def namen():
    df = pd.read_csv(ADRESSEN, dtype={"boerse": bool})
    return {(r.kette, r.adresse): (r.name, r.boerse) for r in df.itertuples()}


def kurse():
    ids = list(NATIV.values()) + [g for _, g in TOKEN.values()]
    r = {}
    for i in range(4):  # CoinGecko drosselt geteilte IPs (GitHub) gelegentlich
        try:
            r = requests.get("https://api.coingecko.com/api/v3/simple/price",
                             params={"ids": ",".join(ids), "vs_currencies": "usd"}, headers=HEADER, timeout=60).json()
            if "bitcoin" in r:
                break
        except (requests.RequestException, ValueError):
            pass
        time.sleep(15 * (i + 1))
    p = {k: r.get(g, {}).get("usd") for k, g in NATIV.items()} | {k: r.get(g, {}).get("usd") for k, (_, g) in TOKEN.items()}
    return {k: v for k, v in p.items() if v}


def zeile(zeit, kette, kuerzel, menge, usd, von, an, tx, nm):
    """Eine Überweisung mit Namen und Typ, oder None bei Börse → Börse."""
    sl = (lambda a: a.lower()) if kette == "eth" else (lambda a: a)
    nv, bv = nm.get((kette, sl(von)), ("", False))
    na, ba = nm.get((kette, sl(an)), ("", False))
    if bv and ba:
        return None
    return {"zeit": zeit, "kette": kette, "kuerzel": kuerzel, "menge": round(menge, 4), "usd": round(usd),
            "von": von, "von_name": nv, "an": an, "an_name": na,
            "typ": "rein" if ba else "raus" if bv else "wal", "tx": tx}


# --- Ketten ----------------------------------------------------------------------------------------

def ethereum(stand, p, nm):
    ende = int(rpc(ETH_RPC, "eth_blockNumber", []), 16)
    start = max(stand.get("eth", ende - 150) + 1, ende - HOECHSTENS["eth"])
    if start > ende:
        return [], ende
    bloecke = list(range(start, ende + 1))
    def block(b):  # Knoten nach Blocknummer, bei Fehler der nächste
        for i in range(len(ETH_BLOECKE)):
            try:
                return rpc(ETH_BLOECKE[(b + i) % len(ETH_BLOECKE)], "eth_getBlockByNumber", [hex(b), True], versuche=2)
            except RuntimeError:
                continue
        raise RuntimeError(f"Block {b} bei keinem Knoten")
    with ThreadPoolExecutor(len(ETH_BLOECKE)) as pool:  # ganze Blöcke: native ETH und Zeitstempel für die Token
        daten = list(pool.map(block, bloecke))
    zeit = {int(d["number"], 16): datetime.fromtimestamp(int(d["timestamp"], 16), timezone.utc) for d in daten}
    raus = []
    for d in daten:
        for t in d["transactions"]:
            menge = int(t["value"], 16) / 1e18
            if menge * p["ETH"] >= GROSS and t.get("to"):
                raus.append(zeile(zeit[int(d["number"], 16)], "eth", "ETH", menge, menge * p["ETH"], t["from"], t["to"],
                                  t["hash"], nm))
    stand.setdefault("dezimal", {})
    for k, (v, _) in TOKEN.items():
        if k not in stand["dezimal"]:
            stand["dezimal"][k] = int(rpc(ETH_RPC, "eth_call", [{"to": v, "data": "0x313ce567"}, "latest"]), 16)
    b = start
    while b <= ende:  # alle Token in einem Abruf; an Spam-Tagen den vom Knoten vorgeschlagenen Bereich nehmen
        bis = ende
        while True:
            try:
                logs = rpc(ETH_RPC, "eth_getLogs", [{"address": [v for v, _ in TOKEN.values()], "topics": [TRANSFER],
                                                     "fromBlock": hex(b), "toBlock": hex(bis)}])
                break
            except ZuVieleTreffer as z:
                bis = max(b, min(z.args[0], bis - 1))
        for l in logs:
            k = VERTRAG.get(l["address"].lower())
            if not k or k not in p or len(l["topics"]) < 3 or l["data"] in ("0x", ""):
                continue
            menge = int(l["data"][:66], 16) / 10 ** stand["dezimal"][k]
            if menge * p[k] >= KLEIN:
                raus.append(zeile(zeit[int(l["blockNumber"], 16)], "eth", k, menge, menge * p[k],
                                  "0x" + l["topics"][1][-40:], "0x" + l["topics"][2][-40:], l["transactionHash"], nm))
        b = bis + 1
    return [z for z in raus if z], ende


def bitcoin(stand, p, nm):
    spitze = int(requests.get("https://mempool.space/api/blocks/tip/height", headers=HEADER, timeout=60).text)
    start = max(stand.get("btc", spitze - 1) + 1, spitze - HOECHSTENS["btc"] + 1)
    raus = []
    for h in range(start, spitze + 1):
        kennung = requests.get(f"https://mempool.space/api/block-height/{h}", headers=HEADER, timeout=60).text.strip()
        blk = requests.get(f"https://blockchain.info/rawblock/{kennung}", headers=HEADER, timeout=180).json()
        zeit = datetime.fromtimestamp(blk["time"], timezone.utc)
        for t in blk["tx"]:
            ein = [i["prev_out"] for i in t["inputs"] if i.get("prev_out") and i["prev_out"].get("addr")]
            if not ein:
                continue  # Coinbase (neu geschürfte Coins)
            von = max(ein, key=lambda o: o["value"])["addr"]
            eigene = {o["addr"] for o in ein}
            for o in t["out"]:
                menge = o["value"] / 1e8
                if o.get("addr") and o["addr"] not in eigene and menge * p["BTC"] >= GROSS:
                    raus.append(zeile(zeit, "btc", "BTC", menge, menge * p["BTC"], von, o["addr"], t["hash"], nm))
    return [z for z in raus if z], spitze


def xrp_ledger(stand, p, nm):
    spitze = int(xrp("ledger", {"ledger_index": "validated"})["ledger"]["ledger_index"])
    start = max(stand.get("xrp", spitze - 500) + 1, spitze - HOECHSTENS["xrp"] + 1)
    with ThreadPoolExecutor(len(XRP_SERVER)) as pool:  # je Server ein Faden
        ledger = list(pool.map(lambda i: xrp("ledger", {"ledger_index": i, "transactions": True, "expand": True},
                                             start=i)["ledger"], range(start, spitze + 1)))
    raus = []
    for l in ledger:
        zeit = datetime.fromtimestamp(int(l["close_time"]) + 946684800, timezone.utc)  # Ripple-Epoche 01.01.2000
        for t in l.get("transactions", []):
            meta = t.get("metaData") or t.get("meta") or {}
            menge = meta.get("delivered_amount")
            if t.get("TransactionType") != "Payment" or not isinstance(menge, str) or meta.get("TransactionResult") != "tesSUCCESS":
                continue  # nur XRP selbst (Token kommen als Objekt)
            menge = int(menge) / 1e6
            if menge * p["XRP"] >= GROSS:
                raus.append(zeile(zeit, "xrp", "XRP", menge, menge * p["XRP"], t["Account"], t["Destination"], t["hash"], nm))
    return [z for z in raus if z], spitze


# --- Ablage ----------------------------------------------------------------------------------------

def speichern(neu, jetzt):
    """48-h-Fenster für die Website, Tagessummen dauerhaft (je Lauf addiert; Läufe überlappen nicht)."""
    alt = json.loads(JSON.read_text()).get("ueberweisungen", []) if JSON.exists() else []
    df = pd.DataFrame(alt + [z | {"zeit": z["zeit"].isoformat(timespec="seconds")} for z in neu])
    if not df.empty:
        df = df.drop_duplicates(["tx", "von", "an", "usd"])
        df = df[pd.to_datetime(df.zeit, utc=True) >= jetzt - FENSTER].sort_values("zeit", ascending=False)
    if neu:
        n = pd.DataFrame(neu)
        n["tag"] = pd.to_datetime(n.zeit, utc=True).dt.strftime("%Y-%m-%d")
        summe = n.pivot_table(index=["tag", "kuerzel"], columns="typ", values="usd", aggfunc="sum", fill_value=0)
        summe = summe.reindex(columns=["rein", "raus", "wal"], fill_value=0)
        summe["anzahl"] = n.groupby(["tag", "kuerzel"]).size()
        if FLUSS.exists():
            summe = summe.add(pd.read_csv(FLUSS).set_index(["tag", "kuerzel"]), fill_value=0)
        summe.astype(int).sort_index().to_csv(FLUSS)
    fluss = pd.read_csv(FLUSS) if FLUSS.exists() else pd.DataFrame(columns=["tag", "kuerzel", "rein", "raus", "wal", "anzahl"])
    fluss = fluss[fluss.tag >= (jetzt - timedelta(days=7)).strftime("%Y-%m-%d")]
    mc = pd.read_csv(memecoins.DATEI) if memecoins.DATEI.exists() else pd.DataFrame()
    if not mc.empty:
        mc = mc[pd.to_datetime(mc.gesehen, utc=True) >= jetzt - FENSTER].drop(columns=["dev"])
    AUSGABE.mkdir(parents=True, exist_ok=True)
    JSON.write_text(json.dumps({
        "stand": jetzt.isoformat(timespec="minutes"),
        "schwelle_usd": {"gross": GROSS, "token": KLEIN},
        "ueberweisungen": df.to_dict("records"),
        "fluss_7_tage": fluss.to_dict("records"),
        "memecoins": json.loads(mc.to_json(orient="records")) if not mc.empty else [],
    }, ensure_ascii=False, separators=(",", ":")))


def lauf():
    jetzt = datetime.now(timezone.utc)
    stand = json.loads(STAND.read_text()) if STAND.exists() else {}
    p, nm, alle = kurse(), namen(), []
    for name, funktion in (("eth", ethereum), ("btc", bitcoin), ("xrp", xrp_ledger)):
        try:  # eine Kette fällt aus → die anderen laufen weiter, Stand dieser Kette bleibt stehen
            neu, stand[name] = funktion(stand, p, nm)
            alle += neu
            print(f"{name}: {len(neu)} große Überweisungen bis {stand[name]}")
        except Exception as e:
            print(f"{name}: Fehler {type(e).__name__}: {e}")
    STAND.write_text(json.dumps(stand, indent=1))
    try:
        memecoins.sammeln()
    except Exception as e:
        print(f"memecoins: Fehler {type(e).__name__}: {e}")
    speichern(alle, jetzt)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--adressen", action="store_true")
    adressen_bauen() if a.parse_args().adressen else lauf()
