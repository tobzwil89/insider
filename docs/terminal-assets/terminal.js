// Rhodus KI-Terminal (Vorschau): der Film. Kein Backend, alles ist inszenierte Animation.
// Ein Zeitstrahl (Einheit = Sekunden beim automatischen Abspielen), den das Scrollen vor- und zurückspult.
(function () {
  'use strict';
  const $ = s => document.querySelector(s);
  const $$ = s => [...document.querySelectorAll(s)];

  // ---------- Warteliste: sendet direkt an das Kit-Formular (ID in data-kit), ohne Kits Skript zu laden ----------
  $$('form.warteliste').forEach(formular => formular.addEventListener('submit', async e => {
    e.preventDefault();
    const meldung = formular.nextElementSibling, d = formular.dataset;
    if (!d.kit) { meldung.textContent = d.geschlossen; return; }
    try {
      const antwort = await (await fetch(`https://app.kit.com/forms/${d.kit}/subscriptions`, {
        method: 'POST', headers: { Accept: 'application/json' }, body: new FormData(formular),
      })).json();
      meldung.textContent = antwort.status === 'success' ? d.ok : d.fehler;
      if (antwort.status === 'success') formular.reset();
    } catch { meldung.textContent = d.offline; }
  }));

  // ---------- Karten für Szene 2 bauen (in jedem Modus) ----------
  const linien = (...klassen) => klassen.map(k => `<div class="l ${k}"></div>`).join('');
  const reihe = (marke) => `<div class="k-reihe"><div class="k-marke ${marke}"></div><div>${linien('w80', '', 'w60')}</div></div>`;
  const INHALT = {
    pdf: linien('dick w60', '', '', 'w80', '', '', 'w40'),
    chart: '<svg viewBox="0 0 100 50" preserveAspectRatio="none"><polyline points="0,38 12,34 22,40 34,26 46,30 58,16 70,22 82,10 100,14"/></svg>' + linien('w60', 'w40'),
    reddit: reihe('') + reihe('') + reihe(''),
    x: reihe('rund') + reihe('rund'),
    news: '<div class="k-bild"></div>' + linien('dick', 'dick w60', '', 'w80'),
  };
  const tunnel = $('.tunnel');
  const karten = tunnel.dataset.karten.split('|').map((eintrag, i) => {
    const art = eintrag.slice(0, eintrag.indexOf(':')), titel = eintrag.slice(eintrag.indexOf(':') + 1);
    const karte = document.createElement('div');
    karte.className = 'karte' + (art === 'pdf' || art === 'news' ? ' hell' : '');
    karte.innerHTML = '<div class="k-kopf"><i></i><span></span></div>' + INHALT[art];
    karte.querySelector('.k-kopf span').textContent = titel;
    // Verteilung nach dem goldenen Winkel: Karten liegen rund um die Mitte, nie zwei an derselben Stelle
    const winkel = i * 137.5 * Math.PI / 180;
    karte.style.setProperty('--x', (Math.cos(winkel) * (28 + (i % 3) * 8)).toFixed(1) + 'vw');
    karte.style.setProperty('--y', (Math.sin(winkel) * (24 + (i % 2) * 9)).toFixed(1) + 'vh');
    karte.style.setProperty('--dreh', (i % 2 ? -1 : 1) * (3 + (i % 5) * 2) + 'deg');
    tunnel.appendChild(karte);
    return karte;
  });

  // ---------- Film oder ruhige Fassung? ----------
  if (matchMedia('(prefers-reduced-motion: reduce)').matches || !window.gsap || !window.ScrollTrigger) return; // Szenen bleiben untereinander stehen

  document.documentElement.classList.add('film-an');
  gsap.registerPlugin(ScrollTrigger);
  ScrollTrigger.config({ ignoreMobileResize: true });
  const schmal = window.innerWidth < 768;
  const buehne = $('.buehne');
  const GOLD = '#d9b770', CREME = '#f3eee2';
  const DAUER = 77; // Sekunden. Wer das ändert: Höhe von .film in terminal.css mitziehen (ca. 24vh je Sekunde)

  // Text in Wörter teilen (Elemente wie <em> bleiben ein Wort)
  function woerter(el) {
    const teile = [];
    [...el.childNodes].forEach(knoten => {
      if (knoten.nodeType === 3) {
        knoten.textContent.split(/(\s+)/).forEach(stueck => {
          if (!stueck.trim()) { el.insertBefore(document.createTextNode(stueck), knoten); return; }
          const wort = document.createElement('span');
          wort.className = 'wort';
          wort.textContent = stueck;
          el.insertBefore(wort, knoten);
          teile.push(wort);
        });
        knoten.remove();
      } else {
        knoten.classList.add('wort');
        teile.push(knoten);
      }
    });
    return teile;
  }

  const tl = gsap.timeline({
    defaults: { ease: 'power2.out' },
    scrollTrigger: {
      trigger: '.film', start: 'top top', end: 'bottom bottom', scrub: 0.5,
      onUpdate: st => gsap.set('.fortschritt i', { scaleX: st.progress }),
    },
  });

  // ----- Bausteine -----
  const rein = (el, t) => tl.fromTo(el, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5 }, t);
  const raus = (el, t) => tl.to(el, { autoAlpha: 0, duration: 0.5, ease: 'power2.in' }, t);
  const hoch = (el, t, extra) => tl.fromTo(el, { autoAlpha: 0, y: 24 }, Object.assign({ autoAlpha: 1, y: 0, duration: 0.6 }, extra), t);
  const zeile = (el, t0, t1) => { hoch(el, t0); if (t1) tl.to(el, { autoAlpha: 0, duration: 0.4 }, t1); };
  const sprich = (el, t, takt = 0.15) => tl.from(woerter(el), { autoAlpha: 0, yPercent: 50, stagger: takt, duration: 0.4 }, t);

  // Tippen: Text erscheint Buchstabe für Buchstabe
  function tippe(el, t, dauer) {
    const text = el.textContent, z = { n: 0 };
    el.textContent = '';
    tl.to(z, { n: text.length, duration: dauer, ease: 'none', onUpdate: () => { el.textContent = text.slice(0, Math.round(z.n)); } }, t);
  }
  // Zahl zählt hoch (Zielwert in data-wert, Nachkommastellen in data-stellen)
  function zaehle(el, t, dauer = 1.1) {
    const ziel = +el.dataset.wert, stellen = +(el.dataset.stellen || 0), z = { v: 0 };
    const text = v => v.toLocaleString(document.documentElement.lang, { minimumFractionDigits: stellen, maximumFractionDigits: stellen });
    el.textContent = text(0);
    tl.to(z, { v: ziel, duration: dauer, ease: 'power1.out', onUpdate: () => { el.textContent = text(z.v); } }, t);
  }
  // Kamera: Ein „Brett“ ist eine feste Zeichenfläche in der Bühnenmitte. blick() liefert Maßstab und Verschiebung,
  // damit das ganze Brett (ohne ziel) oder ein Teil davon die Bühne füllt.
  function blick(brett, ziel, wAnteil = 0.88, hAnteil = 0.56, max = 2.4) {
    const mass = () => {
      const W = buehne.clientWidth, H = buehne.clientHeight, z = ziel || brett;
      const s = Math.min(W * wAnteil / z.offsetWidth, H * hAnteil / z.offsetHeight, max);
      const dx = ziel ? ziel.offsetLeft + ziel.offsetWidth / 2 - brett.offsetWidth / 2 : 0;
      const dy = ziel ? ziel.offsetTop + ziel.offsetHeight / 2 - brett.offsetHeight / 2 : 0;
      return { s, x: -dx * s, y: -dy * s + H * 0.05 };
    };
    return { scale: () => mass().s, x: () => mass().x, y: () => mass().y };
  }
  const ganz = brett => blick(brett, null, 0.92, 0.62, 1.15);
  const fahrt = (brett, ziel, t, opt = []) => tl.to(brett, Object.assign(ziel ? blick(brett, ziel, ...opt) : ganz(brett), { duration: 0.9, ease: 'power2.inOut' }), t);
  gsap.set('.brett', { xPercent: -50, yPercent: -50 });
  $$('.brett').forEach(brett => tl.set(brett, ganz(brett), 0));

  // ----- Szene 1: Haken (0 – 4,8) -----
  const wA = woerter($('.satz-a')), wB = woerter($('.satz-b'));
  gsap.from(wA, { autoAlpha: 0, yPercent: 60, stagger: 0.16, duration: 0.6, ease: 'power3.out', delay: 0.2 }); // beim Laden, nicht am Scrollen
  gsap.set('.satz', { yPercent: -50 });
  tl.to('.satz-a', { autoAlpha: 0, y: -50, duration: 0.6, ease: 'power2.in' }, 0.8)
    .from(wB, { autoAlpha: 0, yPercent: 60, stagger: 0.22, duration: 0.5 }, 1.4)
    .to('.satz-b', { scale: 1.8, autoAlpha: 0, duration: 0.8, ease: 'power2.in' }, 4.0)
    .set('.s1', { autoAlpha: 0 }, 4.8);

  // ----- Szene 2: Chaos, Karten fliegen aus der Tiefe vorbei (4,2 – 10,5) -----
  const T2 = 4.2, D2 = 6.4, ANTEIL = 0.55;
  tl.set('.s2', { autoAlpha: 1 }, T2);
  karten.forEach((karte, i) => {
    const start = T2 + (i / karten.length) * (1 - ANTEIL) * D2, d = ANTEIL * D2;
    gsap.set(karte, { xPercent: -50, yPercent: -50 });
    tl.fromTo(karte, { z: schmal ? -1200 : -1700 }, { z: schmal ? 350 : 500, duration: d, ease: 'none' }, start) // Handy: flacherer Tunnel
      .fromTo(karte, { autoAlpha: 0 }, { autoAlpha: 1, duration: d * 0.18, ease: 'none' }, start)
      .to(karte, { autoAlpha: 0, duration: d * 0.16, ease: 'none' }, start + d * 0.82);
  });
  gsap.set('.s2 .zeile', { xPercent: -50 });
  zeile('.s2 .zeile', 4.9, 9.5);
  tl.to('.tunnel', { scale: 0.15, autoAlpha: 0, duration: 0.8, ease: 'power2.in' }, 9.7) // Tabs werden in die Mitte gesogen
    .set('.s2', { autoAlpha: 0 }, 10.5);

  // ----- Szene 3: Wende, Monogramm (10,1 – 13,8) -----
  tl.set('.s3', { autoAlpha: 1 }, 10.1)
    .fromTo('.monogramm', { autoAlpha: 0, scale: 0.5 }, { autoAlpha: 1, scale: 1, duration: 0.9, ease: 'back.out(1.4)' }, 10.3);
  sprich($('.s3 .zeile'), 11.0, 0.12);
  raus('.s3', 13.2);

  // ----- Szene 4: Der Prompt (13,6 – 22,9) -----
  tl.set('.s4', { autoAlpha: 1 }, 13.6)
    .fromTo('.fenster', { autoAlpha: 0, y: 140, rotationX: 20, scale: 0.9 }, { autoAlpha: 1, y: 0, rotationX: 0, scale: 1, duration: 1.2 }, 13.6);
  zeile('.s4 .zeile', 14.2, 16.0);
  gsap.set('.caret', { autoAlpha: 0 });
  tl.fromTo('.zeiger', { left: '88%', top: '96%', autoAlpha: 0 }, { left: '30%', top: '50%', autoAlpha: 1, duration: 1.1, ease: 'power2.inOut' }, 14.8)
    // Klick ins Feld
    .to('.zeiger svg', { scale: 0.82, duration: 0.1, repeat: 1, yoyo: true }, 15.9)
    .fromTo('.klick', { scale: 0.2, autoAlpha: 0.9 }, { scale: 1, autoAlpha: 0, duration: 0.5 }, 15.95)
    .to('.s4 .feld', { borderColor: GOLD, duration: 0.2 }, 16.0)
    .to('.s4 .caret', { autoAlpha: 1, duration: 0.1 }, 16.0)
    // weicher Zoom auf die Stelle, an der getippt wird
    .to('.fenster', { scale: schmal ? 1.06 : 1.3, duration: 0.9, ease: 'power2.inOut' }, 16.0)
    .to('.zeiger', { left: '62%', top: '74%', duration: 0.9, ease: 'power2.inOut' }, 16.3)
    .to('.platzhalter', { autoAlpha: 0, duration: 0.1 }, 16.6);
  tippe($('.s4 .tipp'), 16.6, 2.8);
  tl.to('.s4 .taste', { backgroundColor: GOLD, color: '#0c1611', borderColor: GOLD, scale: 0.9, duration: 0.12 }, 19.8)
    .to('.s4 .taste', { scale: 1, duration: 0.15 }, 19.95)
    .to('.s4 .caret', { autoAlpha: 0, duration: 0.1 }, 20.0)
    .to('.fenster', { scale: 1, duration: 0.8, ease: 'power2.inOut' }, 20.1)
    .to('.zeiger', { autoAlpha: 0, duration: 0.3 }, 20.1)
    .from('.agent', { autoAlpha: 0, y: 16, stagger: 0.18, duration: 0.4 }, 20.6);
  raus('.s4', 22.4);

  // ----- Szene 5: Agenten denken (22,9 – 42,3). Kamera fährt von Karte zu Karte, Sentiment bekommt am meisten Zeit -----
  const b5 = $('.b5'), k5 = $$('.akarte'), z5 = $$('.s5 .zeile');
  const fokus = (aktiv, t, rest = schmal ? 0.05 : 0.2) => k5.forEach(k => tl.to(k, { opacity: !aktiv || k === aktiv ? 1 : rest, duration: 0.5 }, t));
  rein('.s5', 22.9);
  tl.from(k5, { y: 40, autoAlpha: 0, stagger: 0.12, duration: 0.5 }, 23.0);
  zeile(z5[0], 23.1, 24.3);

  // Fundamental: Kennzahlen zählen hoch
  fahrt(b5, $('.fundamental'), 24.5); fokus($('.fundamental'), 24.5);
  zeile(z5[1], 24.7, 27.3);
  $$('.fundamental .zahl').forEach((zahl, i) => zaehle(zahl, 25.1 + i * 0.4, 0.9));

  // Charttechnik: Kurslinie zeichnet sich, dann die Markierung
  fahrt(b5, $('.chart'), 27.6); fokus($('.chart'), 27.6);
  zeile(z5[2], 27.8, 30.9);
  tl.fromTo('.kurs svg', { clipPath: 'inset(-10% 100% -10% 0%)' }, { clipPath: 'inset(-10% -5% -10% 0%)', duration: 1.8, ease: 'power1.inOut' }, 28.3) // Linie wird von links aufgedeckt
    .from('.hoch, .hoch-name', { autoAlpha: 0, duration: 0.4 }, 29.3)
    .from('.chart-marke', { autoAlpha: 0, scale: 0.6, duration: 0.4, ease: 'back.out(2)' }, 30.1);

  // Sentiment Reddit/X: Erwähnungen laufen ein, der Stimmungsbalken füllt sich
  fahrt(b5, $('.sentiment'), 31.2, [0.92, 0.6]); fokus($('.sentiment'), 31.2, 0.05); // die anderen fast ausblenden, sie lägen sonst unter der Zeile
  zeile(z5[3], 31.4, 37.5);
  zaehle($('.s-gross .zahl'), 31.9, 3.6);
  tl.from('.s-klein', { autoAlpha: 0, duration: 0.4 }, 32.2)
    .from('.beitraege li', { autoAlpha: 0, x: 60, stagger: 1.0, duration: 0.5 }, 32.3)
    .fromTo('.balken i', { scaleX: 0 }, { scaleX: 0.61, duration: 3.0, ease: 'power1.inOut' }, 33.0)
    .from('.s-anteil', { autoAlpha: 0, duration: 0.4 }, 33.0)
    .from('.beitraege .ton', { autoAlpha: 0, scale: 0.6, stagger: 1.0, duration: 0.3, ease: 'back.out(2)' }, 32.8);
  zaehle($('.s-anteil .zahl'), 33.0, 3.0);

  // Nachrichten: Schlagzeilen werden eingeordnet
  fahrt(b5, $('.news'), 37.8); fokus($('.news'), 37.8);
  zeile(z5[4], 38.0, 41.1);
  tl.from('.schlagzeilen li', { autoAlpha: 0, y: 16, stagger: 0.4, duration: 0.4 }, 38.4)
    .from('.schlagzeilen b', { autoAlpha: 0, scale: 0.6, stagger: 0.5, duration: 0.3, ease: 'back.out(2)' }, 39.3);
  fahrt(b5, null, 41.2); fokus(null, 41.2);
  raus('.s5', 42.2);

  // ----- Szene 6: Debatte (42,4 – 51,8). Kamera schwenkt zum Sprecher -----
  const b6 = $('.b6'), bulle = $('.bulle'), baer = $('.baer');
  rein('.s6', 42.4);
  zeile('.s6 .zeile', 42.6);
  fahrt(b6, bulle, 43.3, [0.8, 0.5, 1.5]);
  tl.to(baer, { opacity: 0.2, duration: 0.5 }, 43.3);
  sprich($('.bulle .zitat'), 43.9, 0.16);
  fahrt(b6, baer, 46.7, [0.8, 0.5, 1.5]);
  tl.to(bulle, { opacity: 0.2, duration: 0.5 }, 46.7).to(baer, { opacity: 1, duration: 0.5 }, 46.7);
  tl.set(woerter($('.baer .zitat')), { autoAlpha: 0 }, 0)
    .to('.baer .zitat .wort', { autoAlpha: 1, stagger: 0.14, duration: 0.4 }, 47.3);
  fahrt(b6, null, 50.6);
  tl.to(bulle, { opacity: 1, duration: 0.5 }, 50.6);
  raus('.s6', 51.7);

  // ----- Szene 7: Du fragst dazwischen (51,9 – 59,8) -----
  rein('.s7', 51.9);
  zeile('.s7 .zeile', 52.1);
  tl.from('.b7 .feld, .b7 .feld-label', { autoAlpha: 0, y: 30, duration: 0.5 }, 52.1)
    .set('.s7 .feld', { borderColor: GOLD }, 0)
    .to('.s7 .caret', { autoAlpha: 1, duration: 0.1 }, 52.5);
  tippe($('.s7 .tipp'), 52.7, 2.8);
  tl.to('.s7 .taste', { backgroundColor: GOLD, color: '#0c1611', borderColor: GOLD, scale: 0.9, duration: 0.12 }, 55.7)
    .to('.s7 .taste', { scale: 1, duration: 0.15 }, 55.85)
    .to('.s7 .caret', { autoAlpha: 0, duration: 0.1 }, 55.9)
    .from('.risiko', { autoAlpha: 0, y: 40, duration: 0.5 }, 56.1);
  sprich($('.risiko .zitat'), 56.5);
  raus('.s7', 59.7);

  // ----- Szene 8: Der Report entsteht (59,9 – 68,6) -----
  rein('.s8', 59.9);
  zeile('.s8 .zeile', 60.1);
  tl.from('.blatt', { y: 80, duration: 0.8 }, 59.9)
    .from('.kapitel-liste li', { autoAlpha: 0, x: 20, stagger: 0.08, duration: 0.3 }, 60.3);
  $$('.absatz').forEach((absatz, i) => {
    const t = 61.0 + i * 1.1;
    tl.from(absatz, { autoAlpha: 0, x: 140, y: -30, rotation: 3, duration: 0.6 }, t) // Absatz fliegt ins Dokument
      .to($$('.kapitel-liste li')[i], { color: CREME, '--haken': 1, duration: 0.3 }, t + 0.5); // Kapitel hakt sich ab
  });
  tl.from('.stempel', { autoAlpha: 0, scale: 1.6, duration: 0.4, ease: 'power3.in' }, 66.7)
    .from('.stempel-klein', { autoAlpha: 0, duration: 0.4 }, 67.1);
  raus('.s8', 68.5);

  // ----- Szene 9: Alles an einem Ort (68,7 – 74,2). Netz mit Rhodus in der Mitte -----
  const b9 = $('.b9'), netzSvg = $('.netz-linien'), knoten = $$('.netz li');
  const BW = b9.offsetWidth, BH = b9.offsetHeight, mx = BW / 2, my = BH / 2;
  netzSvg.setAttribute('viewBox', `0 0 ${BW} ${BH}`);
  knoten.forEach((k, i) => {
    const w = (-90 + i * 360 / knoten.length) * Math.PI / 180;
    const x = mx + Math.cos(w) * BW * (schmal ? 0.34 : 0.38);
    const y = my + Math.sin(w) * BH * 0.4 + (schmal && i ? (i % 2 ? 16 : -16) : 0); // Handy: Nachbarn versetzen, damit sie sich nicht überdecken
    k.style.left = x + 'px'; k.style.top = y + 'px';
    const linie = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    const abstand = 78 / Math.hypot(x - mx, y - my); // Linie beginnt erst am Rand des Monogramms
    linie.setAttribute('x1', mx + (x - mx) * abstand); linie.setAttribute('y1', my + (y - my) * abstand);
    linie.setAttribute('x2', x); linie.setAttribute('y2', y);
    linie.setAttribute('pathLength', 1);
    if (k.classList.contains('gold')) linie.classList.add('gold');
    netzSvg.appendChild(linie);
  });
  gsap.set(knoten, { xPercent: -50, yPercent: -50 });
  rein('.s9', 68.7);
  zeile('.s9 .zeile', 69.3);
  tl.fromTo('.netz-mitte', { autoAlpha: 0, scale: 0.5 }, { autoAlpha: 1, scale: 1, duration: 0.7, ease: 'back.out(1.4)' }, 68.8)
    .fromTo('.netz-linien line', { strokeDashoffset: 1 }, { strokeDashoffset: 0, stagger: 0.14, duration: 0.6, ease: 'power1.inOut' }, 69.4)
    .from(knoten, { autoAlpha: 0, scale: 0.6, stagger: 0.14, duration: 0.4, ease: 'back.out(2)' }, 69.8);
  raus('.s9', 73.9);

  // ----- Szene 10: Warteliste (74,2 – 77) -----
  rein('.s10', 74.2);
  tl.from('.s10 .cta-marke', { autoAlpha: 0, y: 20, duration: 0.4 }, 74.3);
  sprich($('.s10 h2'), 74.5, 0.14);
  tl.from('.s10 form', { autoAlpha: 0, y: 24, duration: 0.5 }, 75.3)
    .set({}, {}, DAUER);

  // Alle Maße gelten für die Fensterbreite beim Laden. Ändert sie sich deutlich (Fenster gezogen, Handy gedreht): neu laden.
  const breite0 = window.innerWidth;
  window.addEventListener('resize', () => { if (Math.abs(window.innerWidth - breite0) > 40) location.reload(); });

  // ---------- „Film abspielen“: scrollt gleichmäßig durch den Film ----------
  const knopf = $('.abspielen'), knopfText = knopf.querySelector('span');
  let lauf = null;
  function stopp() {
    if (lauf) lauf.kill();
    lauf = null;
    knopfText.textContent = knopf.dataset.start;
  }
  function spielen() {
    const st = tl.scrollTrigger;
    const von = window.scrollY >= st.end - 2 ? st.start : Math.max(window.scrollY, st.start); // am Ende: von vorn
    const pos = { y: von };
    knopfText.textContent = knopf.dataset.stopp;
    lauf = gsap.to(pos, {
      y: st.end, ease: 'none', duration: DAUER * (st.end - von) / (st.end - st.start),
      onUpdate: () => window.scrollTo(0, pos.y), onComplete: stopp,
    });
  }
  knopf.addEventListener('click', () => (lauf ? stopp() : spielen()));
  ['wheel', 'touchstart'].forEach(e => window.addEventListener(e, ev => { if (lauf && !knopf.contains(ev.target)) stopp(); }, { passive: true }));
})();
