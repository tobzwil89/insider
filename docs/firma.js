// Firmenseite: Kursverlauf mit Insider-Geschäften, CAR je Ereignis, alle Meldungen.

const INDEXNAME = { "^GDAXI": "dem DAX", "^MDAXI": "dem MDAX" };
const monat = (text) => new Date(text).toLocaleDateString("de-DE", { month: "short", year: "2-digit", timeZone: "UTC" });

function zeigeKacheln(f) {
  const [letztesDatum, letzterKurs] = f.kurse[f.kurse.length - 1] || [];
  const aktien = f.meldungen.filter((m) => m.instrument === "Aktie");
  const summe = (art) => aktien.filter((m) => m.art === art);
  const volumen = (liste) => liste.reduce((s, m) => s + (m.volumen || 0), 0);
  const kaeufe = f.ereignisse.filter((e) => e.art === "Kauf");
  const schnitt = kaeufe.length ? kaeufe.reduce((s, e) => s + e.car_ab_0, 0) / kaeufe.length : null;
  document.getElementById("kacheln").replaceChildren(
    kachel("Schlusskurs", letzterKurs == null ? "–" : `${fmt.zahl(letzterKurs, 2)} €`, `am ${fmt.datum(letztesDatum)}`),
    kachel("Insider-Käufe", fmt.zahl(summe("Kauf").length), `zusammen ${fmt.euro(volumen(summe("Kauf")))}`),
    kachel("Insider-Verkäufe", fmt.zahl(summe("Verkauf").length), `zusammen ${fmt.euro(volumen(summe("Verkauf")))}`),
    kachel("Ø Reaktion nach Käufen", fmt.prozent(schnitt), `CAR Tag 0 bis +5, ${kaeufe.length} Ereignisse`),
  );
}

function zeigeKurs(f, monate) {
  const behaelter = document.getElementById("kurs");
  if (!f.kurse.length) { behaelter.replaceChildren(el("p", { class: "leer" }, "Keine Kursdaten verfügbar.")); return; }
  const ende = new Date(f.kurse[f.kurse.length - 1][0]);
  const start = new Date(ende); start.setUTCMonth(start.getUTCMonth() - monate);
  const kurse = f.kurse.filter(([d]) => new Date(d) >= start);
  const daten = kurse.map(([d]) => d);

  // Insider-Geschäfte dem ersten Handelstag am oder nach dem Geschäftsdatum zuordnen
  const jeTag = new Map();
  for (const m of f.meldungen) {
    if (m.instrument !== "Aktie" || !(m.art in FARBE) || !m.geschaeftsdatum) continue;
    const i = daten.findIndex((d) => d >= m.geschaeftsdatum);
    if (i < 0 || m.geschaeftsdatum < daten[0]) continue;
    if (!jeTag.has(i)) jeTag.set(i, []);
    jeTag.get(i).push(m);
  }
  const marker = [];
  for (const [i, liste] of jeTag) {
    for (const art of new Set(liste.map((m) => m.art))) marker.push({ i, y: kurse[i][1], farbe: FARBE[art] });
  }

  const xTicks = [];
  const abstand = Math.max(1, Math.round(monate / 6));
  daten.forEach((d, i) => {
    const neu = i > 0 && d.slice(5, 7) !== daten[i - 1].slice(5, 7);
    if (neu && (+d.slice(5, 7) - 1) % abstand === 0) xTicks.push(i);
  });

  liniendiagramm(behaelter, {
    beschreibung: `Schlusskurs ${f.name} mit Insider-Geschäften`,
    x: daten.map((d) => Date.parse(d)), xTicks, xText: (i) => monat(daten[i]),
    yText: (y) => fmt.zahl(y, Math.max(...kurse.map(([, p]) => p)) < 10 ? 2 : 0), hoehe: 340,
    serien: [{ name: "Schlusskurs", farbe: "var(--kurs)", werte: kurse.map(([, p]) => p) }],
    marker,
    tooltip: (i) => ({
      titel: fmt.datum(daten[i]),
      zeilen: [{ farbe: "var(--kurs)", wert: `${fmt.zahl(kurse[i][1], 2)} €`, text: "Schlusskurs" },
        ...(jeTag.get(i) || []).map((m) => ({ farbe: FARBE[m.art], form: "punkt", wert: fmt.euro(m.volumen, m.waehrung),
          text: `${m.art}: ${m.person}` }))],
    }),
  });
}

function carZelle(x) {
  return el("td", { class: `zahl ${x > 0 ? "positiv" : x < 0 ? "negativ" : ""}` }, fmt.prozent(x));
}

function zeigeEreignisse(f) {
  const ziel = document.getElementById("ereignisse");
  if (!f.ereignisse.length) {
    ziel.append(el("p", { class: "leer" }, "Noch keine auswertbaren Ereignisse. Es braucht mindestens 100 Handelstage Kurshistorie vor der Meldung."));
    return;
  }
  ziel.append(tabelle([["Veröffentlicht"], ["Art"], ["Personen"], ["Volumen", "zahl"], ["CAR −5 bis +5", "zahl"], ["CAR 0 bis +5", "zahl"]],
    f.ereignisse.map((e) => el("tr", {},
      el("td", { class: "datum" }, fmt.datum(e.mitteilungsdatum)),
      el("td", {}, artMarke(e.art)),
      el("td", {}, e.personen.join("; ")),
      el("td", { class: "zahl" }, fmt.euro(e.volumen)),
      carZelle(e.car),
      el("td", { class: `zahl ${e.car_ab_0 > 0 ? "positiv" : e.car_ab_0 < 0 ? "negativ" : ""}` }, fmt.prozent(e.car_ab_0),
        e.tage_nach < 5 ? el("div", { class: "klein" }, `erst bis Tag +${e.tage_nach}`) : null)))));
}

function zeigeMeldungen(f) {
  const ziel = document.getElementById("meldungen");
  if (!f.meldungen.length) { ziel.append(el("p", { class: "leer" }, "Seit Beginn der Aufzeichnung keine Meldungen.")); return; }
  ziel.append(tabelle([["Veröffentlicht"], ["Geschäft"], ["Person"], ["Art"], ["Instrument"], ["Volumen", "zahl"], ["Kurs", "zahl"]],
    f.meldungen.map((m) => el("tr", {},
      el("td", { class: "datum" }, fmt.datum(m.mitteilungsdatum)),
      el("td", { class: "datum" }, fmt.datum(m.geschaeftsdatum)),
      el("td", {}, m.person, el("div", { class: "klein" }, fmt.position(m.position))),
      el("td", {}, artMarke(m.art)),
      el("td", {}, m.instrument),
      el("td", { class: "zahl" }, fmt.euro(m.volumen, m.waehrung)),
      el("td", { class: "zahl" }, m.preis == null ? "–" : fmt.zahl(m.preis, 2))))));
}

(async () => {
  const ticker = new URLSearchParams(location.search).get("t") || "";
  try {
    if (!/^[A-Z0-9.\-]{1,15}$/.test(ticker)) throw new Error("unbekannte Firma");
    const f = await ladeJson(`data/firmen/${ticker}.json`);
    document.title = `${f.name} · Insider-Monitor`;
    document.getElementById("name").textContent = f.name;
    document.getElementById("kennung").textContent = `${f.ticker} · ${f.index} · ISIN ${f.isins.join(", ")}`;
    document.getElementById("benchmark").textContent = INDEXNAME[f.benchmark] || f.benchmark;
    zeigeKacheln(f);
    zeigeKurs(f, 24);
    document.querySelectorAll("#zeitraum button").forEach((knopf) => knopf.addEventListener("click", () => {
      document.querySelectorAll("#zeitraum button").forEach((k) => k.setAttribute("aria-pressed", k === knopf));
      zeigeKurs(f, +knopf.dataset.monate);
    }));
    zeigeEreignisse(f);
    zeigeMeldungen(f);
  } catch (fehler) {
    document.getElementById("name").textContent = "Firma nicht gefunden";
    document.getElementById("kennung").replaceChildren("Zurück zur ", el("a", { href: "./" }, "Übersicht"), ".");
  }
})();
