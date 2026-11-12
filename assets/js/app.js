/* SmokeTrail — scroll story camera, labels and calculator. No dependencies. */
(function () {
  'use strict';

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------- theme ---------------- */
  var THEMES = ['system', 'light', 'dark'];
  var themeBtn = document.getElementById('theme-btn');
  function applyTheme(t) {
    if (t === 'system') document.documentElement.removeAttribute('data-theme');
    else document.documentElement.setAttribute('data-theme', t);
    if (themeBtn) {
      themeBtn.querySelector('.cur').textContent = t.charAt(0).toUpperCase() + t.slice(1);
      themeBtn.setAttribute('aria-label', 'Colour theme: ' + t + '. Click to change.');
    }
  }
  var theme = 'system';
  try { theme = localStorage.getItem('smoketrail-theme') || 'system'; } catch (e) { /* storage unavailable */ }
  if (THEMES.indexOf(theme) < 0) theme = 'system';
  applyTheme(theme);
  if (themeBtn) themeBtn.addEventListener('click', function () {
    theme = THEMES[(THEMES.indexOf(theme) + 1) % THEMES.length];
    applyTheme(theme);
    try { localStorage.setItem('smoketrail-theme', theme); } catch (e) { /* ignore */ }
  });

  /* ---------------- stages ----------------
     box: [x, y, w, h] in world units; m: optional box for narrow screens.
     labels: [x, y, html, position, minor?] */
  var CHIPS = [
    [292, 404, '<b>1–3</b> Smoker', 'up'], [1010, 330, '<b>4</b> Wind', 'up'], [1600, 118, '<b>5</b> Rain', 'up'],
    [1760, 362, '<b>6</b> Clothes', 'up'], [2200, 300, '<b>7</b> Indoors', 'up'], [2632, 530, '<b>8</b> Butts', 'up'],
    [2985, 470, '<b>9</b> Soil', 'up'], [3420, 600, '<b>10</b> Water', 'down']
  ];
  var STAGES = [
    { n: 'Overview', box: [0, 236, 3600, 460], m: [120, 250, 1150, 380], chips: true, vy: 0.64 },
    { n: 'Ignition', box: [140, 330, 280, 220], lens: 'cig', labels: [[318.5, 415, 'Burning coal', 'up']] },
    { n: 'Inhalation', box: [190, 350, 160, 200], lens: 'lung', labels: [[260, 420, 'Lungs', 'left']] },
    { n: 'Exhalation', box: [200, 300, 400, 250], lens: 'size', labels: [[290, 380, 'Exhaled smoke', 'up'], [322, 408, 'Sidestream', 'down']] },
    { n: 'Wind', box: [210, 230, 1060, 340], m: [220, 300, 980, 270], labels: [
      [360, 540, '1 m<small>+72.7 µg/m³</small>', 'down'], [560, 540, '3 m<small>+11.3</small>', 'down'],
      [860, 540, '6 m<small>+4.1</small>', 'down'], [1160, 540, '9 m<small>+2.6</small>', 'down'], [700, 252, 'Wind', 'up', true]] },
    { n: 'Rain', box: [1260, 90, 680, 470], lens: 'drop', labels: [[1600, 150, 'Below-cloud scavenging', 'up']] },
    { n: 'Clothes & hair', box: [1640, 330, 240, 220], labels: [[1749, 368, 'Hair', 'left'], [1778, 432, 'Coat and skin', 'right']] },
    { n: 'Thirdhand smoke', box: [1940, 236, 520, 316], lens: 'ths', labels: [[2090, 400, 'Curtains', 'left'], [2200, 462, 'Sofa and dust', 'up'], [2228, 512, 'Child', 'down'], [2384, 528, 'Pets', 'down', true]] },
    { n: 'Butts', box: [2470, 440, 380, 160], lens: 'butt', labels: [[2632, 530, 'Littered butt', 'up'], [2762, 536, 'Storm drain', 'up']] },
    { n: 'Soil & plants', box: [2860, 430, 380, 260], labels: [[2962, 470, 'Herbs take up nicotine', 'up'], [3040, 610, 'Leachate', 'right'], [2900, 660, 'Water table', 'down', true]] },
    { n: 'Water', box: [2680, 460, 940, 330], m: [2900, 470, 700, 300], labels: [[3060, 598, 'Storm sewer', 'up'], [3480, 572, 'Stream or lake', 'up'], [2700, 712, 'Groundwater flow', 'down']] },
    { n: 'Bystanders', box: [180, 300, 2300, 260], m: [180, 320, 520, 230], vy: 0.6, labels: [[260, 362, 'Smoker', 'up'], [560, 362, 'Bystander', 'up'], [1760, 362, 'Passer-by', 'up', true], [2228, 494, 'Child at home', 'up', true]] },
    { n: 'Switzerland', box: [0, 236, 3600, 460], m: [120, 250, 1150, 380], chips: true, vy: 0.64 }
  ];

  var scene = document.getElementById('scene');
  var world = document.getElementById('world');
  var cam = document.getElementById('cam');
  var lens = document.getElementById('lens');
  var labelsEl = document.getElementById('labels');
  var hudNo = document.getElementById('hud-no');
  var hudName = document.getElementById('hud-name');
  var nav = document.getElementById('trailnav');
  var steps = Array.prototype.slice.call(document.querySelectorAll('.step[data-stage]'));
  var shows = Array.prototype.slice.call(world.querySelectorAll('[data-stages]')).map(function (el) {
    return { el: el, st: el.getAttribute('data-stages').split(/\s+/).map(Number) };
  });
  var lensGroups = Array.prototype.slice.call(lens.querySelectorAll('.lens-g'));
  var cur = -1;
  var camNow = null;
  var labelTimer = null;

  function isNarrow() { return window.innerWidth < 960; }

  function fit(i) {
    var st = STAGES[i];
    var W = scene.clientWidth, H = scene.clientHeight;
    var top = 44, bottom = nav.offsetHeight + 10;
    var ax = 0, ay = top, aw = W, ah = Math.max(80, H - top - bottom);
    var narrow = W < 620;
    if (st.lens && lens.offsetWidth) {
      var lw = lens.offsetWidth;
      if (!isNarrow() && W - lw - 40 > W * 0.42) { aw = W - lw - 48; }
      else if (isNarrow()) { ay = top; ah = Math.max(80, H - top - bottom); aw = Math.max(W * 0.5, W - lw - 16); }
    }
    var b = (narrow && st.m) ? st.m : st.box;
    var s = Math.min(aw / b[2], ah / b[3]);
    var vy = (st.vy && aw / b[2] < ah / b[3]) ? st.vy : 0.5;
    var ty = ay + ah * vy - (b[1] + b[3] / 2) * s;
    // never leave empty space above the sky's top edge of the box
    return { s: s, tx: ax + aw / 2 - (b[0] + b[2] / 2) * s, ty: ty };
  }

  function applyCam(c) {
    camNow = c;
    cam.style.transform = 'translate(' + c.tx.toFixed(2) + 'px,' + c.ty.toFixed(2) + 'px) scale(' + c.s.toFixed(5) + ')';
  }

  function placeLabels(i, c) {
    var st = STAGES[i];
    var list = st.chips ? CHIPS : (st.labels || []);
    labelsEl.innerHTML = '';
    list.forEach(function (l) {
      var d = document.createElement('div');
      d.className = 'lbl ' + (l[3] || 'up') + (st.chips ? ' chip' : '') + (l[4] ? ' minor' : '');
      d.innerHTML = l[2];
      d.style.left = (l[0] * c.s + c.tx).toFixed(1) + 'px';
      d.style.top = (l[1] * c.s + c.ty).toFixed(1) + 'px';
      labelsEl.appendChild(d);
    });
    // hide labels that fall outside the visible scene or under the lens
    var sr = scene.getBoundingClientRect();
    var lr = lens.classList.contains('on') ? lens.getBoundingClientRect() : null;
    Array.prototype.forEach.call(labelsEl.children, function (d) {
      var r = d.getBoundingClientRect();
      var out = r.left < sr.left + 4 || r.right > sr.right - 4 || r.top < sr.top + 40 || r.bottom > sr.bottom - nav.offsetHeight;
      var under = lr && !(r.right < lr.left || r.left > lr.right || r.bottom < lr.top || r.top > lr.bottom);
      if (out || under) d.style.display = 'none';
    });
  }

  function showLabels(i, c, delay) {
    clearTimeout(labelTimer);
    Array.prototype.forEach.call(labelsEl.children, function (d) { d.classList.remove('on'); });
    labelTimer = setTimeout(function () {
      placeLabels(i, c);
      requestAnimationFrame(function () {
        Array.prototype.forEach.call(labelsEl.children, function (d) { d.classList.add('on'); });
      });
    }, delay);
  }

  function setStage(i, force) {
    if (i === cur && !force) return;
    var prev = cur;
    cur = i;
    var st = STAGES[i];
    world.setAttribute('data-stage', i);
    shows.forEach(function (s) { s.el.classList.toggle('show', s.st.indexOf(i) >= 0); });
    lens.classList.toggle('on', !!st.lens);
    lensGroups.forEach(function (g) { g.classList.toggle('on', g.getAttribute('data-lens') === st.lens); });
    var c = fit(i);
    applyCam(c);
    hudNo.textContent = i === 0 ? 'Start' : (i <= 12 ? 'Stop ' + i : '');
    hudName.textContent = st.n;
    Array.prototype.forEach.call(nav.querySelectorAll('button'), function (b, k) {
      if (k === i) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current');
      b.classList.toggle('past', k < i);
    });
    steps.forEach(function (s, k) { s.classList.toggle('active', k === i); });
    showLabels(i, c, (reduce || prev === -1 || force) ? 0 : 1100);
  }

  /* nav dots */
  var ol = nav.querySelector('ol');
  STAGES.forEach(function (st, i) {
    var li = document.createElement('li');
    var b = document.createElement('button');
    b.type = 'button';
    b.title = (i === 0 ? 'Start' : 'Stop ' + i) + ': ' + st.n;
    b.setAttribute('aria-label', b.title);
    b.innerHTML = '<span></span>';
    b.addEventListener('click', function () { goTo(i); });
    li.appendChild(b);
    ol.appendChild(li);
  });

  function headerH() { var h = document.querySelector('.topbar'); return h ? h.offsetHeight : 56; }

  function goTo(i) {
    var el = steps[i];
    if (!el) return;
    var r = el.getBoundingClientRect();
    var off = isNarrow() ? headerH() + scene.offsetHeight + 4 : headerH() + window.innerHeight * 0.18;
    window.scrollTo({ top: r.top + window.pageYOffset - off + 2, behavior: reduce ? 'auto' : 'smooth' });
  }

  /* which step is being read */
  var ticking = false;
  function readingLine() {
    if (isNarrow()) {
      var sb = scene.getBoundingClientRect().bottom;
      return sb + (window.innerHeight - sb) * 0.3;
    }
    return window.innerHeight * 0.5;
  }
  function onScroll() {
    ticking = false;
    var line = readingLine();
    var idx = 0;
    for (var k = 0; k < steps.length; k++) {
      if (steps[k].getBoundingClientRect().top <= line) idx = k;
    }
    setStage(+steps[idx].getAttribute('data-stage'));
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
  }, { passive: true });
  var rz;
  window.addEventListener('resize', function () {
    clearTimeout(rz);
    rz = setTimeout(function () { if (cur >= 0) setStage(cur, true); }, 120);
  });

  /* pause animation when the scene is off screen */
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (en) {
      en.forEach(function (e) { world.classList.toggle('paused', !e.isIntersecting); lens.classList.toggle('paused', !e.isIntersecting); });
    }).observe(scene);
  }

  /* reduced motion: freeze particles at spread-out positions instead of a pile at the source */
  if (reduce) {
    Array.prototype.forEach.call(document.querySelectorAll('.puff'), function (p, k) {
      var fr = 0.25 + ((k * 0.618) % 1) * 0.6;
      var dx = parseFloat(p.getAttribute('data-dx')) * fr, dy = parseFloat(p.getAttribute('data-dy')) * fr;
      var s = 0.4 + (parseFloat(p.getAttribute('data-s')) - 0.4) * fr;
      p.style.transform = 'translate(' + dx + 'px,' + dy + 'px) scale(' + s + ')';
    });
  }

  /* first frame without a camera flight */
  cam.style.transition = 'none';
  onScroll();
  if (cur < 0) setStage(0);
  requestAnimationFrame(function () { requestAnimationFrame(function () { cam.style.transition = ''; }); });

  /* ---------------- calculator ---------------- */
  var form = document.getElementById('calc-form');
  if (!form) return;
  var inCpd = document.getElementById('in-cpd'), inDays = document.getElementById('in-days'), inPpl = document.getElementById('in-ppl');
  var outTotal = document.getElementById('out-total');
  var note = document.getElementById('preset-note');
  var inputsBox = document.getElementById('calc-inputs');
  var presetBtns = Array.prototype.slice.call(form.querySelectorAll('[data-preset]'));
  var PRESETS = {
    one: { cpd: 1, days: 1, ppl: 1, note: '' },
    year: { cpd: 20, days: 365, ppl: 1, note: '' },
    twenty: { cpd: 20, days: 7300, ppl: 1, note: '' },
    ch: { total: 7.96e9, note: 'Switzerland preset: 7.96 billion cigarettes taxed in 2024. Change any field to use your own numbers.' }
  };
  var mode = 'year';

  function nf(x, d) { return x.toLocaleString('en-US', { maximumFractionDigits: d, minimumFractionDigits: 0 }); }
  function sig(x) {
    if (x === 0) return '0';
    var a = Math.abs(x);
    if (a >= 100) return nf(Math.round(x), 0);
    if (a >= 10) return nf(x, 1);
    if (a >= 1) return nf(x, 2);
    return nf(x, 3);
  }
  function pair(lo, hi, f) {
    var a = f(lo), b = f(hi);
    return a === b ? a : a + '–' + b;
  }
  function fmtMass(lo, hi) {
    var U = [['ng', 1], ['µg', 1e3], ['mg', 1e6], ['g', 1e9], ['kg', 1e12], ['t', 1e15]];
    var u = U[0];
    for (var k = 0; k < U.length; k++) if (hi >= U[k][1]) u = U[k];
    return pair(lo / u[1], hi / u[1], sig) + ' ' + u[0];
  }
  function fmtCount(lo, hi) {
    var U = [['', 1], [' million', 1e6], [' billion', 1e9], [' trillion', 1e12]];
    var u = U[0];
    for (var k = 0; k < U.length; k++) if (hi >= U[k][1] * (k ? 1 : 0)) u = U[k];
    if (u[1] === 1) return hi < 100 ? pair(lo, hi, sig) : pair(lo, hi, function (v) { return nf(Math.round(v), 0); });
    return pair(lo / u[1], hi / u[1], sig) + u[0];
  }
  function fmtVol(lo, hi) {
    var main;
    if (hi < 1000) main = pair(lo, hi, sig) + ' L';
    else if (hi < 1e9) main = pair(lo / 1000, hi / 1000, sig) + ' m³';
    else if (hi < 1e12) main = pair(lo / 1e9, hi / 1e9, sig) + ' million m³';
    else main = pair(lo / 1e12, hi / 1e12, sig) + ' km³';
    var poolsHi = hi / 1000 / 2500;
    var extra = poolsHi >= 1 ? '<small>≈ ' + fmtCount(lo / 1000 / 2500, poolsHi) + ' Olympic pools (2,500 m³ each) <span class="derived">derived</span></small>' : '';
    return main + extra;
  }

  function total() {
    if (mode === 'ch') return PRESETS.ch.total;
    var c = Math.max(0, parseFloat(inCpd.value) || 0), d = Math.max(0, parseFloat(inDays.value) || 0), p = Math.max(0, parseFloat(inPpl.value) || 0);
    return c * d * p;
  }

  function update() {
    var N = total();
    outTotal.value = fmtCount(N, N);
    outTotal.textContent = fmtCount(N, N);
    Array.prototype.forEach.call(document.querySelectorAll('#calc-results td.val'), function (td) {
      var lo = parseFloat(td.getAttribute('data-lo')) * N, hi = parseFloat(td.getAttribute('data-hi')) * N;
      var u = td.getAttribute('data-u');
      td.innerHTML = u === 'mass' ? fmtMass(lo, hi) : u === 'vol' ? fmtVol(lo, hi) : fmtCount(lo, hi);
    });
    note.textContent = PRESETS[mode] ? PRESETS[mode].note : '';
    note.hidden = !note.textContent;
    inputsBox.classList.toggle('dim', mode === 'ch');
    presetBtns.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-preset') === mode ? 'true' : 'false'); });
  }

  presetBtns.forEach(function (b) {
    b.addEventListener('click', function () {
      mode = b.getAttribute('data-preset');
      var p = PRESETS[mode];
      if (p.cpd !== undefined) { inCpd.value = p.cpd; inDays.value = p.days; inPpl.value = p.ppl; }
      update();
    });
  });
  [inCpd, inDays, inPpl].forEach(function (inp) {
    inp.addEventListener('input', function () { mode = 'custom'; update(); });
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  update();
})();
