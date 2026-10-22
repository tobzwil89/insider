// Gemeinsame Helfer für alle Seiten: Daten laden, formatieren, Elemente bauen, Liniendiagramm.
// Texte aus den BaFin-Daten werden nur über textContent eingesetzt, nie als HTML.

async function ladeJson(pfad) {
  const antwort = await fetch(pfad, { cache: "no-cache" });
  if (!antwort.ok) throw new Error(`${pfad}: ${antwort.status}`);
  return antwort.json();
}

const fmt = {
  zahl: (x, stellen = 0) => x == null ? "–" :
    x.toLocaleString("de-DE", { minimumFractionDigits: stellen, maximumFractionDigits: stellen }),
  euro(x, waehrung = "EUR") {
    if (x == null) return "–";
    const zeichen = waehrung === "EUR" || !waehrung ? "€" : waehrung;
    if (Math.abs(x) >= 1e6) return `${fmt.zahl(x / 1e6, 1)} Mio. ${zeichen}`;
    if (Math.abs(x) >= 1e4) return `${fmt.zahl(x / 1e3, 0)} Tsd. ${zeichen}`;
    return `${fmt.zahl(x, 0)} ${zeichen}`;
  },
  prozent: (x, stellen = 1, vorzeichen = true) => x == null ? "–" :
    (vorzeichen && x > 0 ? "+" : x < 0 ? "−" : "") + fmt.zahl(Math.abs(x) * 100, stellen) + " %",
  datum(text) {
    if (!text) return "–";
    const [j, m, t] = text.slice(0, 10).split("-");
    return `${t}.${m}.${j}`;
  },
  datumZeit(text) {
    if (!text) return "–";
    return fmt.datum(text) + (text.length > 10 ? ", " + text.slice(11, 16) + " Uhr" : "");
  },
  position: (p) => ({ "in enger Beziehung": "eng verbunden", "Sonstige Führungsperson": "Führungsperson" }[p] || p),
};

// Element bauen: el("td", { class: "zahl" }, "Text", kindElement)
function el(tag, attribute = {}, ...kinder) {
  const knoten = document.createElement(tag);
  for (const [name, wert] of Object.entries(attribute)) {
    if (wert == null || wert === false) continue;
    if (name === "style") knoten.style.cssText = wert;
    else if (name.startsWith("on")) knoten.addEventListener(name.slice(2), wert);
    else knoten.setAttribute(name, wert === true ? "" : wert);
  }
  for (const kind of kinder.flat()) {
    if (kind == null || kind === false) continue;
    knoten.append(kind instanceof Node ? kind : document.createTextNode(String(kind)));
  }
  return knoten;
}

const FARBE = { Kauf: "var(--kauf)", Verkauf: "var(--verkauf)" };
const farbeArt = (art) => FARBE[art] || "var(--sonstiges)";

function artMarke(art) {
  return el("span", { class: "art" }, el("span", { class: "punkt", style: `background:${farbeArt(art)}` }), art);
}

function firmaLink(name, ticker) {
  return ticker ? el("a", { href: `firma.html?t=${encodeURIComponent(ticker)}` }, name) : el("span", {}, name);
}

function stand(s) {
  return `Berechnet ${fmt.datumZeit(s.berechnet)} · letzte BaFin-Meldung ${fmt.datumZeit(s.letzte_meldung)} · ` +
    `Kurse bis ${fmt.datum(s.letzter_kurstag)}`;
}

// Saubere Achsenschritte (1, 2, 2,5, 5 × 10^n)
function schritte(min, max, anzahl = 5) {
  if (min === max) { min -= 1; max += 1; }
  const roh = (max - min) / anzahl;
  const basis = 10 ** Math.floor(Math.log10(roh));
  const schritt = [1, 2, 2.5, 5, 10].map((f) => f * basis).find((s) => s >= roh);
  const ticks = [];
  for (let v = Math.floor(min / schritt) * schritt; v <= max + schritt * 1e-9; v += schritt) ticks.push(+v.toFixed(10));
  if (ticks[ticks.length - 1] < max) ticks.push(ticks[ticks.length - 1] + schritt);
  return ticks;
}

const SVG = "http://www.w3.org/2000/svg";
function svgEl(tag, attribute = {}) {
  const knoten = document.createElementNS(SVG, tag);
  for (const [name, wert] of Object.entries(attribute)) knoten.setAttribute(name, wert);
  return knoten;
}

/* Liniendiagramm mit Fadenkreuz und Tooltip.
   opt.x        Array der x-Werte (Zahlen; Datumsangaben als Zeitstempel)
   opt.serien   [{ name, farbe, werte: [y|null], punkte?: [{ i, gefuellt }] }]
   opt.marker   [{ i, y, farbe }] zusätzliche Punkte (z. B. Insider-Geschäfte)
   opt.xTicks   Array von Indizes, die beschriftet werden
   opt.xText    i → Beschriftung, opt.yText y → Beschriftung
   opt.yNull    Nulllinie zeichnen und einschließen, opt.senkrecht i für eine senkrechte Linie
   opt.endLabel Serienname am Linienende anzeigen
   opt.tooltip  i → { titel, zeilen: [{ farbe, wert, text, form }], fuss } */
function liniendiagramm(behaelter, opt) {
  behaelter.classList.add("diagramm");
  const tip = el("div", { class: "tooltip", hidden: true });

  function zeichnen() {
    behaelter.replaceChildren();
    const breite = behaelter.clientWidth || 600;
    const hoehe = opt.hoehe || 300;
    const rand = { oben: 12, rechts: opt.endLabel ? 74 : 12, unten: 28, links: 52 };
    const n = opt.x.length;
    const alleY = opt.serien.flatMap((s) => s.werte).concat((opt.marker || []).map((m) => m.y))
      .filter((v) => v != null);
    if (opt.yNull) alleY.push(0);
    const yTicks = schritte(Math.min(...alleY), Math.max(...alleY), opt.yAnzahl || 5);
    const yMin = yTicks[0], yMax = yTicks[yTicks.length - 1];
    const xMin = opt.x[0], xMax = opt.x[n - 1];
    const px = (i) => rand.links + (opt.x[i] - xMin) / (xMax - xMin || 1) * (breite - rand.links - rand.rechts);
    const py = (y) => rand.oben + (yMax - y) / (yMax - yMin) * (hoehe - rand.oben - rand.unten);

    const svg = svgEl("svg", { viewBox: `0 0 ${breite} ${hoehe}`, height: hoehe, role: "img",
      "aria-label": opt.beschreibung || "" });
    for (const t of yTicks) {
      svg.append(svgEl("line", { class: t === 0 && opt.yNull ? "null" : "gitter", x1: rand.links,
        x2: breite - rand.rechts, y1: py(t), y2: py(t) }));
      const text = svgEl("text", { x: rand.links - 8, y: py(t) + 4, "text-anchor": "end" });
      text.textContent = opt.yText(t);
      svg.append(text);
    }
    // Beschriftungen ausdünnen, damit sie auch auf schmalen Bildschirmen nicht überlappen
    let letzteX = -Infinity;
    for (const i of opt.xTicks) {
      if (px(i) - letzteX < 64) continue;
      letzteX = px(i);
      const text = svgEl("text", { x: px(i), y: hoehe - 8, "text-anchor": "middle" });
      text.textContent = opt.xText(i);
      svg.append(text);
    }
    if (opt.senkrecht != null) {
      svg.append(svgEl("line", { class: "achse", x1: px(opt.senkrecht), x2: px(opt.senkrecht),
        y1: rand.oben, y2: hoehe - rand.unten }));
    }
    for (const s of opt.serien) {
      let d = "";
      s.werte.forEach((y, i) => { if (y != null) d += `${d && s.werte[i - 1] != null ? "L" : "M"}${px(i)},${py(y)}`; });
      svg.append(svgEl("path", { class: "linie", d, stroke: s.farbe }));
      for (const p of s.punkte || []) {
        svg.append(svgEl("circle", { cx: px(p.i), cy: py(s.werte[p.i]), r: 4,
          fill: p.gefuellt ? s.farbe : "var(--flaeche)", stroke: p.gefuellt ? "var(--flaeche)" : s.farbe,
          "stroke-width": 2 }));
      }
      if (opt.endLabel) {
        const letzter = s.werte.findLastIndex((v) => v != null);
        const text = svgEl("text", { x: px(letzter) + 10, y: py(s.werte[letzter]) + 4, class: "stark" });
        text.textContent = s.name;
        svg.append(text);
      }
    }
    for (const m of opt.marker || []) {
      svg.append(svgEl("circle", { cx: px(m.i), cy: py(m.y), r: 5, fill: m.farbe,
        stroke: "var(--flaeche)", "stroke-width": 2 }));
    }
    const kreuz = svgEl("line", { class: "fadenkreuz", y1: rand.oben, y2: hoehe - rand.unten, visibility: "hidden" });
    svg.append(kreuz);
    behaelter.append(svg, tip);

    function zeige(ereignis) {
      const kasten = svg.getBoundingClientRect();
      const x = (ereignis.clientX - kasten.left) * breite / kasten.width;
      let bester = 0;
      for (let i = 1; i < n; i++) if (Math.abs(px(i) - x) < Math.abs(px(bester) - x)) bester = i;
      kreuz.setAttribute("x1", px(bester)); kreuz.setAttribute("x2", px(bester));
      kreuz.setAttribute("visibility", "visible");
      const inhalt = opt.tooltip(bester);
      tip.replaceChildren(el("div", { class: "titel" }, inhalt.titel),
        ...inhalt.zeilen.map((z) => el("div", { class: "zeile" },
          el("span", { class: z.form === "punkt" ? "punkt" : "strich", style: `background:${z.farbe}` }),
          el("b", {}, z.wert), el("span", {}, z.text))),
        inhalt.fuss ? el("div", { class: "klein" }, inhalt.fuss) : null);
      tip.hidden = false;
      const links = px(bester) * kasten.width / breite;
      const platz = behaelter.clientWidth - tip.offsetWidth - 4;
      tip.style.left = `${Math.max(0, Math.min(links + 14, platz))}px`;
      tip.style.top = `${Math.max(0, (ereignis.clientY - kasten.top) - tip.offsetHeight - 12)}px`;
    }
    svg.addEventListener("pointermove", zeige);
    svg.addEventListener("pointerdown", zeige);
    svg.addEventListener("pointerleave", () => { tip.hidden = true; kreuz.setAttribute("visibility", "hidden"); });
  }

  zeichnen();
  // Beim Neuzeichnen (z. B. anderer Zeitraum) den alten Beobachter ersetzen, sonst kehrt das alte Bild zurück
  if (behaelter.beobachter) behaelter.beobachter.disconnect();
  let letzteBreite = behaelter.clientWidth;
  behaelter.beobachter = new ResizeObserver(() => {
    if (behaelter.clientWidth !== letzteBreite) { letzteBreite = behaelter.clientWidth; zeichnen(); }
  });
  behaelter.beobachter.observe(behaelter);
}

function kachel(label, wert, zusatz) {
  return el("div", { class: "kachel" }, el("div", { class: "label" }, label),
    el("div", { class: "wert" }, wert), el("div", { class: "zusatz" }, zusatz));
}

function tabelle(kopf, zeilen) {
  return el("div", { class: "tabelle-rahmen" }, el("table", {},
    el("thead", {}, el("tr", {}, kopf.map(([text, klasse]) => el("th", { class: klasse }, text)))),
    el("tbody", {}, zeilen)));
}

function rankingTabelle(liste, mitFirma = true) {
  return tabelle([["#", "zahl"], ["Person"], mitFirma ? ["Firma"] : null, ["Käufe", "zahl"],
    ["Typisch (Median)", "zahl"], ["Durchschnitt", "zahl"], ["Besser als Index", "zahl"], ["Zeitraum"]].filter(Boolean),
  liste.map((r) => el("tr", {},
    el("td", { class: "zahl" }, r.rang),
    el("td", {}, r.person, el("div", { class: "klein" }, fmt.position(r.position))),
    mitFirma ? el("td", {}, firmaLink(r.name, r.ticker)) : null,
    el("td", { class: "zahl" }, r.kaeufe),
    el("td", { class: `zahl ${r.median > 0 ? "positiv" : "negativ"}` }, fmt.prozent(r.median)),
    el("td", { class: "zahl" }, fmt.prozent(r.ueberrendite)),
    el("td", { class: "zahl" }, `${fmt.zahl(r.trefferquote * 100)} %`),
    el("td", { class: "datum" }, r.erster_kauf.slice(0, 4) === r.letzter_kauf.slice(0, 4)
      ? r.erster_kauf.slice(0, 4) : `${r.erster_kauf.slice(0, 4)}–${r.letzter_kauf.slice(0, 4)}`))));
}
