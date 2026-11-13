"""Wie stark liegt ein Coin in wenigen Händen? Anteil der zehn größten Adressen (ohne Börsen, Brücken, Staking,
verbrannte Coins) und Sonderrechte des Vertrags (z. B. neue Coins prägen, Überweisungen sperren).

Quelle: FraudCoins-Datensatz (fraudcoins.com/data/), CC BY 4.0, also auch kommerziell frei mit Nennung:
„FraudCoins.com (2026). On-chain holder-concentration dataset. https://fraudcoins.com/data/“
Schlüssel sind CoinGecko-IDs (wie in wale_laden.TOKEN). Messwerte sind Stichtagswerte (gemessen), alle paar Tage neu.
Vertragsrechte kommen dort von GoPlus; null heißt „nicht gemeldet“, nicht „fehlt“.

Wird von wale_laden.py genutzt; lädt höchstens alle 12 Stunden neu (Datei ändert sich täglich).
"""
import json
from datetime import datetime, timedelta, timezone

import requests

from pipeline import DATEN, HEADER

BASIS = "https://fraudcoins.com"
DATEI = DATEN / "wale" / "konzentration.json"
RECHTE = ["isMintable", "ownerChangeBalance", "transferPausable", "isBlacklisted", "canTakeBackOwnership",
          "hiddenOwner", "selfDestruct"]
QUELLE = "FraudCoins.com (2026). On-chain holder-concentration dataset. https://fraudcoins.com/data/ (CC BY 4.0)"


def holen(tokens):
    """tokens: {Kürzel: (Ethereum-Vertrag, CoinGecko-ID)} → {Kürzel: Messwerte}."""
    k = requests.get(f"{BASIS}/concentration.json", headers=HEADER, timeout=120).json()["coins"]
    r = requests.get(f"{BASIS}/dataset/v1/contract-permissions.json", headers=HEADER, timeout=120).json()["tokens"]
    raus = {}
    for kuerzel, (vertrag, gecko) in tokens.items():
        c, p = k.get(gecko), r.get(f"ethereum:{vertrag}")
        if not c and not p:
            continue
        z = {}
        if c:
            z |= {"top10_pct": c.get("top10Pct"), "auffaellig": c.get("flagged"), "schwelle_pct": c.get("flagThreshold"),
                  "gemessen": (c.get("sampledAt") or "")[:10]}
        if p:
            z["sonderrechte"] = [f for f in RECHTE if p.get(f) is True]
        raus[kuerzel] = z
    return raus


def aktuell(tokens):
    """Zwischengespeicherte Werte; nach 12 Stunden neu laden. Bei Fehler bleiben die alten Werte."""
    alt = json.loads(DATEI.read_text()) if DATEI.exists() else {}
    jetzt = datetime.now(timezone.utc)
    if alt and jetzt - datetime.fromisoformat(alt["geladen"]) < timedelta(hours=12):
        return alt["coins"]
    try:
        neu = {"geladen": jetzt.isoformat(timespec="minutes"), "quelle": QUELLE, "coins": holen(tokens)}
        DATEI.parent.mkdir(parents=True, exist_ok=True)
        DATEI.write_text(json.dumps(neu, ensure_ascii=False, indent=1))
        return neu["coins"]
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"konzentration: Fehler {type(e).__name__}: {e}")
        return alt.get("coins", {})
