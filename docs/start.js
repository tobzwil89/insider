// Startseite: Kennzahlen, CAAR-Kurve, Cluster-Käufe, Live-Ticker, Firmenliste.

const NAMEN = { Kauf: "Käufe", Verkauf: "Verkäufe" };

function zeigeKacheln(stand, caar, cluster) {
  const kauf = caar.Kauf || [];
  const bei = (t) => kauf.find((z) => z.t === t);
  const vorher = bei(-1), nachher = bei(5);
  document.getElementById("kacheln").replaceChildren(
    kachel(`Meldungen seit ${fmt.datum(stand.meldungen_seit)}`, fmt.zahl(stand.anzahl_meldungen),
      `davon ${fmt.zahl(stand.anzahl_ereignisse)} Ereignisse im DAX/MDAX ausgewertet`),
    kachel("Kursverlauf vor Insider-Käufen", vorher ? fmt.prozent(vorher.caar) : "–",
      `CAAR Tag −5 bis −1, n = ${vorher ? vorher.n : 0}`),
    kachel("Kursreaktion nach Insider-Käufen", vorher && nachher ? fmt.prozent(nachher.caar - vorher.caar) : "–",
      `CAAR Tag 0 bis +5, n = ${nachher ? nachher.n : 0}`),
    kachel("Cluster-Käufe", fmt.zahl(cluster.length),
      cluster.length ? `zuletzt ${cluster[0].emittent}, ${fmt.datum(cluster[0].bekannt_seit)}` : "noch keine"),
  );
}

function zeigeCaar(caar) {
  const arten = ["Kauf", "Verkauf"].filter((a) => caar[a] && caar[a].length);
  const behaelter = document.getElementById("caar");
  if (!arten.length) { behaelter.append(el("p", { class: "leer" }, "Noch keine ausgewerteten Ereignisse.")); return; }
  const tage = caar[arten[0]].map((z) => z.t);
  const zeile = (art, t) => caar[art].find((z) => z.t === t);
  const nMax = (art) => Math.max(...caar[art].map((z) => z.n));

  document.getElementById("caar-legende").replaceChildren(
    ...arten.map((a) => el("span", {}, el("span", { class: "strich", style: `background:${FARBE[a]}` }),
      `${NAMEN[a]} (n = ${nMax(a)})`)),
    el("span", {}, el("span", { class: "punkt", style: "background:var(--text-3)" }), "Tag signifikant (p < 5 %)"),
    el("span", {}, el("span", { class: "punkt hohl", style: "border-color:var(--text-3)" }), "nicht signifikant"),
  );

  liniendiagramm(behaelter, {
    beschreibung: "CAAR nach Insider-Käufen und -Verkäufen, Tag −5 bis +5",
    x: tage, xTicks: tage.map((_, i) => i), xText: (i) => (tage[i] > 0 ? "+" : "") + tage[i],
    yText: (y) => fmt.prozent(y, Math.abs(y) < 0.01 && y !== 0 ? 1 : 0),
    yNull: true, senkrecht: tage.indexOf(0), endLabel: true, hoehe: 300,
    serien: arten.map((a) => ({
      name: NAMEN[a], farbe: FARBE[a], werte: tage.map((t) => zeile(a, t)?.caar ?? null),
      punkte: tage.map((t, i) => ({ i, gefuellt: (zeile(a, t)?.p_wert ?? 1) < 0.05 })),
    })),
    tooltip: (i) => ({
      titel: `Tag ${tage[i] > 0 ? "+" : ""}${tage[i]}${tage[i] === 0 ? " (Veröffentlichung)" : ""}`,
      zeilen: arten.map((a) => {
        const z = zeile(a, tage[i]);
        return { farbe: FARBE[a], wert: fmt.prozent(z.caar, 2),
          text: `${NAMEN[a]} · Tag ${fmt.prozent(z.aar, 2)}, p = ${fmt.zahl(z.p_wert, 3)}` };
      }),
      fuss: "Wert = CAAR seit Tag −5; dahinter die AAR dieses Tages und ihr p-Wert",
    }),
  });

  const zeilen = arten.flatMap((a) => caar[a].map((z) => el("tr", {},
    el("td", {}, NAMEN[a]), el("td", { class: "zahl" }, z.t),
    el("td", { class: "zahl" }, fmt.prozent(z.aar, 2)), el("td", { class: "zahl" }, fmt.prozent(z.caar, 2)),
    el("td", { class: "zahl" }, fmt.zahl(z.t_stat, 2)), el("td", { class: "zahl" }, fmt.zahl(z.p_wert, 3)),
    el("td", { class: "zahl" }, z.n))));
  document.getElementById("caar-tabelle").append(tabelle(
    [["Art"], ["Tag", "zahl"], ["AAR", "zahl"], ["CAAR", "zahl"], ["t-Wert", "zahl"], ["p-Wert", "zahl"], ["n", "zahl"]], zeilen));
}

function clusterKarte(c) {
  const von = fmt.datum(c.von), bis = fmt.datum(c.bis);
  return el("div", { class: "cluster" },
    el("div", { class: "name" }, firmaLink(c.emittent, c.ticker)),
    el("div", { class: "zeitraum" }, von === bis ? `am ${bis}` : `${von.slice(0, 6)} bis ${bis}`),
    el("div", { class: "betrag" }, fmt.euro(c.volumen)),
    el("div", { class: "personen" }, `${c.personen.length} Personen: ${c.personen.join("; ")}`));
}

function zeigeCluster(cluster) {
  const liste = document.getElementById("cluster");
  const knopf = document.getElementById("cluster-mehr");
  if (!cluster.length) { liste.append(el("p", { class: "leer" }, "Noch keine Cluster-Käufe erkannt.")); return; }
  liste.replaceChildren(...cluster.slice(0, 6).map(clusterKarte));
  if (cluster.length > 6) {
    knopf.hidden = false;
    knopf.addEventListener("click", () => { liste.replaceChildren(...cluster.map(clusterKarte)); knopf.hidden = true; });
  }
}

function zeigeTicker(meldungen) {
  const filter = { art: "", nurIndex: false, nurAktien: true, anzahl: 40 };
  const ziel = document.getElementById("ticker");
  const mehr = document.getElementById("ticker-mehr");

  function aktualisieren() {
    const treffer = meldungen.filter((m) => (!filter.art || m.art === filter.art) &&
      (!filter.nurIndex || m.ticker) && (!filter.nurAktien || m.instrument === "Aktie"));
    const zeilen = treffer.slice(0, filter.anzahl).map((m) => el("tr", {},
      el("td", { class: "datum" }, fmt.datumZeit(m.aktiviert)),
      el("td", {}, firmaLink(m.emittent, m.ticker),
        m.instrument !== "Aktie" ? el("div", { class: "klein" }, m.instrument) : null),
      el("td", {}, m.person, el("div", { class: "klein" }, fmt.position(m.position))),
      el("td", {}, artMarke(m.art)),
      el("td", { class: "zahl" }, fmt.euro(m.volumen, m.waehrung)),
      el("td", { class: "zahl" }, m.preis == null ? "–" : `${fmt.zahl(m.preis, 2)}`)));
    ziel.replaceChildren(treffer.length ? tabelle(
      [["Veröffentlicht"], ["Firma"], ["Person"], ["Art"], ["Volumen", "zahl"], ["Kurs", "zahl"]], zeilen)
      : el("p", { class: "leer" }, "Keine Meldungen für diesen Filter."));
    mehr.hidden = treffer.length <= filter.anzahl;
  }

  document.querySelectorAll("#art-filter button").forEach((knopf) => knopf.addEventListener("click", () => {
    document.querySelectorAll("#art-filter button").forEach((k) => k.setAttribute("aria-pressed", k === knopf));
    filter.art = knopf.dataset.art; filter.anzahl = 40; aktualisieren();
  }));
  document.getElementById("nur-index").addEventListener("change", (e) => { filter.nurIndex = e.target.checked; aktualisieren(); });
  document.getElementById("nur-aktien").addEventListener("change", (e) => { filter.nurAktien = e.target.checked; aktualisieren(); });
  mehr.addEventListener("click", () => { filter.anzahl += 60; aktualisieren(); });
  aktualisieren();
}

function zeigeRanking(ranking) {
  const ziel = document.getElementById("ranking");
  const mehr = document.getElementById("ranking-mehr");
  const liste = ranking.map((r, i) => ({ ...r, rang: i + 1 }));
  if (!liste.length) { ziel.append(el("p", { class: "leer" }, "Noch zu wenige Käufe für ein Ranking.")); return; }
  let anzahl = 20;
  const zeichnen = () => {
    ziel.replaceChildren(rankingTabelle(liste.slice(0, anzahl)));
    mehr.hidden = liste.length <= anzahl;
  };
  mehr.addEventListener("click", () => { anzahl += 50; zeichnen(); });
  zeichnen();
}

function zeigeFirmen(firmen) {
  const ziel = document.getElementById("firmen");
  const suche = document.getElementById("firmen-suche");
  function aktualisieren() {
    const text = suche.value.trim().toLowerCase();
    const treffer = firmen.filter((f) => !text || f.name.toLowerCase().includes(text) || f.ticker.toLowerCase().includes(text));
    ziel.replaceChildren(...treffer.map((f) => el("a", { href: `firma.html?t=${encodeURIComponent(f.ticker)}` },
      el("span", {}, f.name), el("span", { class: "klein" }, `${f.index} · ${f.meldungen}`))));
    if (!treffer.length) ziel.append(el("p", { class: "leer" }, "Keine Firma gefunden."));
  }
  suche.addEventListener("input", aktualisieren);
  aktualisieren();
}

(async () => {
  try {
    const [stand_, caar, cluster, meldungen, firmen, ranking] = await Promise.all(
      ["stand", "caar", "cluster", "neueste", "firmen", "ranking"].map((n) => ladeJson(`data/${n}.json`)));
    document.getElementById("stand").textContent = stand(stand_);
    zeigeKacheln(stand_, caar, cluster);
    zeigeCaar(caar);
    zeigeCluster(cluster);
    zeigeRanking(ranking);
    zeigeTicker(meldungen);
    zeigeFirmen(firmen);
  } catch (fehler) {
    console.error(fehler);
    document.getElementById("stand").textContent = `Daten konnten nicht geladen werden (${fehler.message}).`;
  }
})();
