"""Telegram-Nachricht bei neuen Cluster-Käufen.

Braucht zwei Umgebungsvariablen (in GitHub als Secrets): TELEGRAM_TOKEN und TELEGRAM_CHAT_ID.
Fehlen sie, passiert nichts. Bereits gemeldete Cluster stehen in daten/gemeldete_cluster.txt.
Beim allerersten Lauf werden alle vorhandenen Cluster nur vermerkt, nicht gesendet.

Einrichtung:
    python3 -m pipeline.telegram --chat-id TOKEN   zeigt die Chat-ID (vorher dem Bot schreiben)
    python3 -m pipeline.telegram --test            sendet eine Testnachricht
"""

import html
import os
import sys

import pandas as pd
import requests

from pipeline import DATEN

DATEI = DATEN / "gemeldete_cluster.txt"
WEBSITE = "https://insider.tobiaszwilling.me"
NUR_LETZTE_TAGE = 14  # ältere Cluster nicht mehr melden, z. B. nach spät nachgereichten Meldungen


def _senden(text: str) -> None:
    antwort = requests.post(
        f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}/sendMessage", timeout=30,
        json={"chat_id": os.environ["TELEGRAM_CHAT_ID"], "text": text, "parse_mode": "HTML",
              "disable_web_page_preview": True})
    if not antwort.ok:
        raise RuntimeError(f"Telegram: {antwort.status_code} {antwort.text[:200]}")


def _betrag(x: float) -> str:
    return f"{x:,.0f} €".replace(",", ".")


def nachricht(c: pd.Series, ticker: str | None) -> str:
    zeilen = [
        f"🔔 <b>Cluster-Kauf: {html.escape(c['emittent'])}</b>",
        f"{len(c['personen'])} Führungskräfte kauften vom {c['von']:%d.%m.} bis {c['bis']:%d.%m.%Y} "
        f"für zusammen {_betrag(c['volumen'])}.",
        "Personen: " + html.escape("; ".join(c["personen"])),
        f'<a href="{WEBSITE}/firma/{ticker}/">Zur Firmenseite</a>' if ticker else WEBSITE,
        "<i>Keine Anlageberatung.</i>",
    ]
    return "\n".join(zeilen)


def melde_neue_cluster(cluster: pd.DataFrame, isin_zu_ticker: dict) -> int:
    """Sendet je neuem Cluster eine Nachricht. Gibt die Zahl gesendeter Nachrichten zurück."""
    if not os.environ.get("TELEGRAM_TOKEN") or not os.environ.get("TELEGRAM_CHAT_ID"):
        print("Telegram: kein Token gesetzt, übersprungen")
        return 0
    if not DATEI.exists():
        DATEI.write_text("".join(f"{i}\n" for i in cluster["id"]))
        print(f"Telegram: erster Lauf, {len(cluster)} vorhandene Cluster vermerkt, nichts gesendet")
        return 0
    gemeldet = set(DATEI.read_text().split())
    grenze = pd.Timestamp.now().normalize() - pd.Timedelta(days=NUR_LETZTE_TAGE)
    neu = cluster[~cluster["id"].isin(gemeldet) & (cluster["bekannt_seit"] >= grenze)]
    gesendet = 0
    for _, c in neu.iterrows():
        try:
            _senden(nachricht(c, isin_zu_ticker.get(c["isin"])))
        except Exception as fehler:  # beim nächsten Lauf erneut versuchen, Pipeline läuft weiter
            print(f"Telegram: {fehler}")
            continue
        with DATEI.open("a") as f:
            f.write(f"{c['id']}\n")
        gesendet += 1
    print(f"Telegram: {gesendet} Cluster gemeldet")
    return gesendet


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--chat-id":
        token = sys.argv[2]
        bot = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=30).json()
        if not bot.get("ok"):
            sys.exit(f"Telegram lehnt das Token ab: {bot.get('description')}. Token neu kopieren.")
        print(f"Token gehört zum Bot @{bot['result']['username']}")
        updates = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=30).json()
        if not updates.get("ok"):
            sys.exit(f"Telegram-Fehler: {updates.get('description')}")
        chats = {}
        for u in updates["result"]:
            nachricht = u.get("message") or u.get("edited_message") or u.get("my_chat_member") or {}
            if "chat" in nachricht:
                chats[nachricht["chat"]["id"]] = nachricht["chat"].get("first_name") or nachricht["chat"].get("title", "")
        print(f"Chat-ID(s): {chats}" if chats else
              f"Keine Nachrichten gefunden. Öffne in Telegram genau @{bot['result']['username']}, "
              "schreib ihm etwas und starte das hier erneut.")
    elif sys.argv[1:] == ["--test"]:
        _senden("✅ Insider-Monitor: Testnachricht")
        print("gesendet")
    else:
        print(__doc__)
