// Firmenseite (docs/firma/<TICKER>/index.html, von pipeline/seiten.py erzeugt): Zahlen und Tabellen
// stehen schon im HTML. Hier wird nur das Kursdiagramm mit den Insider-Geschäften gezeichnet.

const monat = (text) => new Date(text).toLocaleDateString("de-DE", { month: "short", year: "2-digit", timeZone: "UTC" });

function zeigeKurs(f, monate) {
  const behaelter = document.getElementById("kurs");
  if (!f.kurse.length) { behaelter.replaceChildren(el("p", { class: "leer" }, "Keine Kursdaten verfügbar.")); return; }
  const ende = new Date(f.kurse[f.kurse.length - 1][0]);
  const start = new Date(ende); start.setUTCMonth(start.getUTCMonth() - monate);
  const kurse = f.kurse.filter(([d]) => new Date(d) >= start);
  const daten = kurse.map(([d]) => d);

  // Insider-Geschäfte dem ersten Handelstag am oder nach dem Geschäftsdatum zuordnen
  const jeTag = new Map();
  for (const m of f.marker) {
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
  const abstand = Math.max(1, Math.round(Math.min(monate, daten.length / 21) / 6));
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

(async () => {
  const f = JSON.parse(document.getElementById("daten").textContent);
  try {
    f.kurse = await ladeJson(`../../data/kurse/${encodeURIComponent(f.ticker)}.json`);
  } catch (fehler) {
    console.error(fehler);
    f.kurse = [];
  }
  zeigeKurs(f, 60);
  document.querySelectorAll("#zeitraum button").forEach((knopf) => knopf.addEventListener("click", () => {
    document.querySelectorAll("#zeitraum button").forEach((k) => k.setAttribute("aria-pressed", k === knopf));
    zeigeKurs(f, +knopf.dataset.monate);
  }));
})();
