"""Sonntags-Report aus den eigenen Daten (docs/data).

Aufruf:
    python3 sonntags_report.py [JJJJ-MM-TT]          Entwurf nach newsletter/JJJJ-MM-TT.md
    python3 sonntags_report.py JJJJ-MM-TT --kit      zusätzlich in Kit anlegen, Versand am Stichtag 08:00 Uhr
    python3 sonntags_report.py JJJJ-MM-TT --entwurf  in Kit nur als Entwurf anlegen (zum Testen)
Ohne Datum gilt heute als Stichtag. Betrachtet werden die 7 Tage davor (Mitteilungsdatum).
Mit --kit wird nichts gemacht, wenn newsletter/JJJJ-MM-TT.md schon existiert (die Datei zeigt: schon geplant).
Kit braucht KIT_API_KEY (v4-Schlüssel), Telegram-Hinweis TELEGRAM_TOKEN und TELEGRAM_CHAT_ID.
"""
import html
import json
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

DATEN = Path(__file__).parent / "docs" / "data"
ZIEL = Path(__file__).parent / "newsletter"
VERSAND_UHRZEIT = 8  # Sonntag, deutsche Zeit


def lade(name):
    return json.loads((DATEN / name).read_text(encoding="utf-8"))


def euro(betrag):
    return f"{betrag:,.0f} €".replace(",", ".")


def kurs(preis, waehrung):
    return f"{preis:.2f} {waehrung}".replace(".", ",").replace("EUR", "€")


def prozent(wert):
    return f"{wert * 100:+.1f} %".replace(".", ",")


def umschichtungen(meldungen):
    """Kauf und Verkauf bei derselben Firma am selben Tag zum (fast) selben Kurs = Aktien wechseln nur
    innerhalb einer Familie oder Holding den Besitzer (z. B. ATOSS 03./04.11.2026). Gibt die Schlüssel
    (isin, geschaeftsdatum) zurück."""
    gruppen = {}
    for m in meldungen:
        gruppen.setdefault((m["isin"], m["geschaeftsdatum"]), []).append(m)
    treffer = set()
    for schluessel, liste in gruppen.items():
        kaeufe = [m["preis"] for m in liste if m["art"] == "Kauf"]
        verkaeufe = [m["preis"] for m in liste if m["art"] == "Verkauf"]
        if any(abs(k - v) <= 0.01 * v for k in kaeufe for v in verkaeufe):
            treffer.add(schluessel)
    return treffer


def report(stichtag):
    von = (stichtag - timedelta(days=7)).isoformat()
    bis = stichtag.isoformat()

    meldungen = [m for m in lade("neueste.json") if von <= m["mitteilungsdatum"] < bis]
    weg = umschichtungen(meldungen)
    echt = [m for m in meldungen if (m["isin"], m["geschaeftsdatum"]) not in weg]
    kaeufe = sorted((m for m in echt if m["art"] == "Kauf"), key=lambda m: -m["volumen"])
    verkaeufe = sorted((m for m in echt if m["art"] == "Verkauf"), key=lambda m: -m["volumen"])
    cluster = [c for c in lade("cluster.json") if von <= c["bekannt_seit"] < bis]
    bilanz = {(r["ticker"], r["person"]): r for r in lade("ranking.json")
              if r["ueberrendite"] > 0 and r["median"] > 0}

    z = [f"# Sonntags-Report vom {stichtag:%d.%m.%Y}", "",
         f"Meldungen vom {date.fromisoformat(von):%d.%m.} bis {stichtag - timedelta(days=1):%d.%m.%Y}: "
         f"{len(kaeufe)} Käufe, {len(verkaeufe)} Verkäufe.", ""]

    z += ["## Die größten Insiderkäufe der Woche", ""]
    for m in kaeufe[:5]:
        z.append(f"- **{m['emittent']}**: {m['person']} ({m['position']}) kauft für {euro(m['volumen'])} "
                 f"zu {kurs(m['preis'], m['waehrung'])} (Geschäft am {date.fromisoformat(m['geschaeftsdatum']):%d.%m.})")
    if not kaeufe:
        z.append("- Keine Käufe gemeldet.")

    z += ["", "## Mehrere Insider kaufen gleichzeitig (Cluster)", ""]
    for c in cluster:
        z.append(f"- **{c['emittent']}**: {len(c['personen'])} Personen, zusammen {euro(c['volumen'])} "
                 f"({', '.join(c['personen'])})")
    if not cluster:
        z.append("- Diese Woche kein neuer Cluster.")

    z += ["", "## Käufer mit guter Bilanz", ""]
    treffer = [(m, bilanz[(m["ticker"], m["person"])]) for m in kaeufe if (m["ticker"], m["person"]) in bilanz]
    for m, r in treffer:
        z.append(f"- **{m['emittent']}**: {m['person']} hatte nach {r['kaeufe']} früheren Käufen im Schnitt "
                 f"{prozent(r['ueberrendite'])} Überrendite in 60 Tagen (Treffer {r['trefferquote'] * 100:.0f} %)")
    if not treffer:
        z.append("- Kein Käufer dieser Woche mit mindestens 3 bewerteten früheren Käufen.")

    z += ["", "## Die größten Verkäufe", ""]
    for m in verkaeufe[:3]:
        z.append(f"- **{m['emittent']}**: {m['person']} ({m['position']}) verkauft für {euro(m['volumen'])}")
    if not verkaeufe:
        z.append("- Keine Verkäufe gemeldet.")

    if weg:
        z += ["", "## Umschichtungen (nicht mitgezählt)", ""]
        for isin, tag in sorted(weg, key=lambda s: s[1]):
            liste = [m for m in meldungen if (m["isin"], m["geschaeftsdatum"]) == (isin, tag)]
            summe = sum(m["volumen"] for m in liste if m["art"] == "Kauf")
            z.append(f"- **{liste[0]['emittent']}**: Käufe und Verkäufe von {euro(summe)} am "
                     f"{date.fromisoformat(tag):%d.%m.} zum selben Kurs. Die Aktien wechseln nur innerhalb "
                     f"der Insider den Besitzer.")

    z += ["", "---", "Quelle: Meldungen nach Art. 19 MAR (BaFin). Keine Anlageberatung.", ""]
    return "\n".join(z)


def als_html(text):
    """Das einfache Markdown oben (#, ##, -, **, ---) in E-Mail-HTML umwandeln."""
    teile, liste = [], False
    for zeile in text.splitlines():
        inhalt = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(zeile[2:] if zeile[:2] == "- " else zeile))
        if zeile.startswith("- "):
            if not liste:
                teile.append("<ul>")
                liste = True
            teile.append(f"<li>{inhalt}</li>")
            continue
        if liste:
            teile.append("</ul>")
            liste = False
        if zeile.startswith("## "):
            teile.append(f"<h2>{inhalt[3:]}</h2>")
        elif zeile.startswith("# "):
            teile.append(f"<h1>{inhalt[2:]}</h1>")
        elif zeile == "---":
            teile.append("<hr>")
        elif zeile:
            teile.append(f"<p>{inhalt}</p>")
    if liste:
        teile.append("</ul>")
    return "\n".join(teile)


def in_kit(stichtag, text, versenden):
    daten = {"subject": f"Sonntags-Report vom {stichtag:%d.%m.%Y}", "content": als_html(text),
             "description": "automatisch aus sonntags_report.py", "public": False}
    if versenden:
        zeit = datetime(stichtag.year, stichtag.month, stichtag.day, VERSAND_UHRZEIT, tzinfo=ZoneInfo("Europe/Berlin"))
        daten["send_at"] = zeit.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")
    antwort = requests.post("https://api.kit.com/v4/broadcasts", json=daten, timeout=30,
                            headers={"X-Kit-Api-Key": os.environ["KIT_API_KEY"]})
    if not antwort.ok:
        raise RuntimeError(f"Kit: {antwort.status_code} {antwort.text[:300]}")
    return antwort.json()["broadcast"]["id"]


def telegram(text):
    if not os.environ.get("TELEGRAM_TOKEN") or not os.environ.get("TELEGRAM_CHAT_ID"):
        print("Telegram: kein Token gesetzt, übersprungen")
        return
    from pipeline.telegram import _senden
    _senden(text)


def main():
    argumente = [a for a in sys.argv[1:] if not a.startswith("--")]
    stichtag = date.fromisoformat(argumente[0]) if argumente else date.today()
    kit, entwurf = "--kit" in sys.argv, "--entwurf" in sys.argv
    datei = ZIEL / f"{stichtag.isoformat()}.md"

    if kit and datei.exists():
        print(f"Schon geplant: {datei.name}")
        return

    text = report(stichtag)
    if kit or entwurf:
        kennung = in_kit(stichtag, text, versenden=kit)
        art = f"geplant für {stichtag:%d.%m.} um {VERSAND_UHRZEIT}:00 Uhr" if kit else "als Entwurf angelegt"
        print(f"Kit: Broadcast {kennung} {art}")
        if kit:
            telegram(f"<b>Sonntags-Report {art}</b>\nPrüfen oder stoppen: "
                     f"https://app.kit.com/campaigns/{kennung}/edit\n\n{html.escape(text[:3000])}")

    ZIEL.mkdir(exist_ok=True)
    datei.write_text(text, encoding="utf-8")
    print(f"Entwurf geschrieben: {datei}")


if __name__ == "__main__":
    main()
