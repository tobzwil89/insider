"""Entwurf des Sonntags-Reports aus den eigenen Daten (docs/data).

Aufruf: python3 sonntags_report.py [JJJJ-MM-TT]
Ohne Datum gilt heute als Stichtag. Betrachtet werden die 7 Tage davor (Mitteilungsdatum).
Ergebnis: newsletter/JJJJ-MM-TT.md, ein Entwurf zum Überarbeiten, nicht zum ungeprüften Versand.
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

DATEN = Path(__file__).parent / "docs" / "data"
ZIEL = Path(__file__).parent / "newsletter"


def lade(name):
    return json.loads((DATEN / name).read_text(encoding="utf-8"))


def euro(betrag):
    return f"{betrag:,.0f} €".replace(",", ".")


def kurs(preis, waehrung):
    return f"{preis:.2f} {waehrung}".replace(".", ",").replace("EUR", "€")


def prozent(wert):
    return f"{wert * 100:+.1f} %".replace(".", ",")


def main():
    stichtag = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    von = (stichtag - timedelta(days=7)).isoformat()
    bis = stichtag.isoformat()

    meldungen = [m for m in lade("neueste.json") if von <= m["mitteilungsdatum"] < bis]
    kaeufe = sorted((m for m in meldungen if m["art"] == "Kauf"), key=lambda m: -m["volumen"])
    verkaeufe = sorted((m for m in meldungen if m["art"] == "Verkauf"), key=lambda m: -m["volumen"])
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

    z += ["", "---", "Quelle: Meldungen nach Art. 19 MAR (BaFin). Keine Anlageberatung.", ""]

    ZIEL.mkdir(exist_ok=True)
    datei = ZIEL / f"{bis}.md"
    datei.write_text("\n".join(z), encoding="utf-8")
    print(f"Entwurf geschrieben: {datei}")


if __name__ == "__main__":
    main()
