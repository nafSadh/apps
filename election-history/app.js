/* election-history · dot timeline, county shift arrows, House hex timeline */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const fmtM = (v) => (v >= 1e6 ? (v / 1e6).toFixed(1) + "M" : v >= 1e3 ? Math.round(v / 1e3) + "K" : String(v));
  const pct = (a, b) => (b ? (100 * a / b).toFixed(1) : "0.0");
  const STATE_NAMES = { AL: "Alabama", AK: "Alaska", AZ: "Arizona", AR: "Arkansas", CA: "California", CO: "Colorado", CT: "Connecticut", DE: "Delaware", FL: "Florida", GA: "Georgia", HI: "Hawaii", ID: "Idaho", IL: "Illinois", IN: "Indiana", IA: "Iowa", KS: "Kansas", KY: "Kentucky", LA: "Louisiana", ME: "Maine", MD: "Maryland", MA: "Massachusetts", MI: "Michigan", MN: "Minnesota", MS: "Mississippi", MO: "Missouri", MT: "Montana", NE: "Nebraska", NV: "Nevada", NH: "New Hampshire", NJ: "New Jersey", NM: "New Mexico", NY: "New York", NC: "North Carolina", ND: "North Dakota", OH: "Ohio", OK: "Oklahoma", OR: "Oregon", PA: "Pennsylvania", RI: "Rhode Island", SC: "South Carolina", SD: "South Dakota", TN: "Tennessee", TX: "Texas", UT: "Utah", VT: "Vermont", VA: "Virginia", WA: "Washington", WV: "West Virginia", WI: "Wisconsin", WY: "Wyoming" };
  const NOMINEES = { 1976: ["Carter", "Ford"], 1980: ["Carter", "Reagan"], 1984: ["Mondale", "Reagan"], 1988: ["Dukakis", "Bush"], 1992: ["Clinton", "Bush"], 1996: ["Clinton", "Dole"], 2000: ["Gore", "Bush"], 2004: ["Kerry", "Bush"], 2008: ["Obama", "McCain"], 2012: ["Obama", "Romney"], 2016: ["Clinton", "Trump"], 2020: ["Biden", "Trump"], 2024: ["Harris", "Trump"] };
  const PRES_WINNER = { 1976: 0, 1980: 1, 1984: 1, 1988: 1, 1992: 0, 1996: 0, 2000: 1, 2004: 1, 2008: 0, 2012: 0, 2016: 1, 2020: 0, 2024: 1 };
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------------------------------------------------------------- theme + colors
  const meta = $('meta[name="color-scheme"]');
  function applyTheme(v) {
    meta.content = v;
    if (v === "light" || v === "dark") document.documentElement.setAttribute("data-theme", v);
    else document.documentElement.removeAttribute("data-theme");
  }
  try { applyTheme(localStorage.getItem("color-scheme") ?? "light dark"); } catch (e) {}
  $("#theme").addEventListener("click", () => {
    const order = ["light dark", "light", "dark"];
    const next = order[(order.indexOf(meta.content) + 1) % 3];
    applyTheme(next);
    try { localStorage.setItem("color-scheme", next); } catch (e) {}
    redrawAll();
  });
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => redrawAll());
  let probe;
  function cssColor(v) {
    if (!probe) { probe = document.createElement("span"); probe.style.display = "none"; document.body.appendChild(probe); }
    probe.style.color = `var(${v})`;
    return getComputedStyle(probe).color;
  }

  // ---------------------------------------------------------------- tooltip
  const tip = $("#tip");
  function showTip(html, ev) {
    tip.innerHTML = html; tip.style.opacity = "1";
    const w = tip.offsetWidth, h = tip.offsetHeight;
    let x = ev.clientX + 14, y = ev.clientY + 14;
    if (x + w > innerWidth - 8) x = ev.clientX - w - 14;
    if (y + h > innerHeight - 8) y = ev.clientY - h - 14;
    tip.style.left = x + "px"; tip.style.top = y + "px";
  }
  const hideTip = () => { tip.style.opacity = "0"; };

  // ---------------------------------------------------------------- data
  const cache = {};
  const getJSON = (u) => (cache[u] ||= fetch(u).then((r) => { if (!r.ok) throw new Error(u + " " + r.status); return r.json(); }).catch((e) => { delete cache[u]; throw e; }));
  function getDots(race, year, scale) {
    const u = `data/${race}-${year}-${scale}.bin`;
    return (cache[u] ||= fetch(u).then((r) => { if (!r.ok) throw new Error(u + " " + r.status); return r.arrayBuffer(); }).then((buf) => {
      const n = Math.floor(buf.byteLength / 9);
      const xy = new Uint32Array(buf, 0, n * 2), ps = new Uint8Array(buf, n * 8, n);
      const x = new Float32Array(n), y = new Float32Array(n), p = new Uint8Array(n);
      for (let i = 0; i < n; i++) { x[i] = xy[2 * i] / 4096; y[i] = xy[2 * i + 1] / 4096; p[i] = ps[i] >> 6; }
      return { n, x, y, p };
    }).catch((e) => { delete cache[u]; throw e; }));
  }

  // ---------------------------------------------------------------- map view: zoom, pan, ground, labels
  class MapView {
    constructor(el, geo, opts) {
      this.el = el; this.cv = el.querySelector("canvas"); this.geo = geo; this.opts = opts;
      this.paths = Object.fromEntries(Object.entries(geo.outline).map(([s, d]) => [s, new Path2D(d)]));
      this.user = null; this.labels = true; this.raf = 0;
      this.bind();
    }
    get zoomed() { return !!this.user && this.user.z > 1.02; }
    redraw() { if (!this.raf) this.raf = requestAnimationFrame(() => { this.raf = 0; this.draw(); }); }
    draw() {
      const el = this.el, cv = this.cv, [FW, FH] = this.geo.frame;
      const W = Math.max(280, el.clientWidth || 900), H = Math.round(W * FH / FW);
      const dpr = Math.min(devicePixelRatio || 1, 2);
      if (cv.width !== Math.round(W * dpr) || cv.height !== Math.round(H * dpr)) { cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); cv.style.width = W + "px"; cv.style.height = H + "px"; }
      const k0 = W / FW;
      if (!this.user) this.user = { z: 1, ox: 0, oy: 0 };
      const kz = k0 * this.user.z;
      this.user.ox = Math.min(W / 2, Math.max(W / 2 - FW * kz, this.user.ox));
      this.user.oy = Math.min(H / 2, Math.max(H / 2 - FH * kz, this.user.oy));
      const v = this.view = { k: kz, ox: this.user.ox, oy: this.user.oy, W, H, dpr, z: this.user.z };
      const ctx = cv.getContext("2d");
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
      // ground
      ctx.setTransform(dpr * kz, 0, 0, dpr * kz, dpr * v.ox, dpr * v.oy);
      ctx.fillStyle = cssColor("--alt");
      for (const p of Object.values(this.paths)) ctx.fill(p);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      this.opts.layer(ctx, v);
      ctx.setTransform(dpr * kz, 0, 0, dpr * kz, dpr * v.ox, dpr * v.oy);
      ctx.strokeStyle = cssColor("--line2"); ctx.lineWidth = (this.zoomed ? 1 : 0.6) / kz; ctx.lineJoin = "round";
      for (const p of Object.values(this.paths)) ctx.stroke(p);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      if (this.labels && this.zoomed) this.drawLabels(ctx, v);
      cv.style.cursor = this.zoomed ? "grab" : "default";
      cv.style.touchAction = this.zoomed ? "none" : "pan-y";
      const home = this.el.querySelector('[data-z="home"]'); if (home) home.hidden = !this.zoomed;
      if (this.opts.after) this.opts.after(v);
    }
    drawLabels(ctx, v) {
      const ff = getComputedStyle(document.body).fontFamily, ink = cssColor("--ink"), bg = cssColor("--bg");
      const need = Math.max(15000, 2.2e6 / v.k), boxes = [];
      for (const [name, fx, fy, people] of this.geo.places) {
        if (people < need) continue;
        const x = fx * v.k + v.ox, y = fy * v.k + v.oy;
        if (x < 4 || y < 10 || x > v.W - 60 || y > v.H - 6) continue;
        const big = people >= 1e6, fs = big ? 14 : people >= 2e5 ? 13 : 12;
        ctx.font = `${big ? 700 : 600} ${fs}px ${ff}`;
        const tw = ctx.measureText(name).width;
        const bb = [x - 4, y - fs / 2 - 2, x + 8 + tw + 3, y + fs / 2 + 2];
        if (bb[2] > v.W - 2 || boxes.some((o) => !(bb[2] < o[0] || bb[0] > o[2] || bb[3] < o[1] || bb[1] > o[3]))) continue;
        boxes.push(bb);
        ctx.beginPath(); ctx.arc(x, y, 3, 0, 6.2832); ctx.fillStyle = bg; ctx.fill(); ctx.lineWidth = 1.5; ctx.strokeStyle = ink; ctx.stroke();
        ctx.textAlign = "left"; ctx.textBaseline = "middle"; ctx.lineJoin = "round"; ctx.lineWidth = 4; ctx.strokeStyle = bg;
        ctx.strokeText(name, x + 7, y); ctx.fillStyle = ink; ctx.fillText(name, x + 7, y);
      }
    }
    stateAt(ev) {
      const b = this.cv.getBoundingClientRect(), v = this.view; if (!v) return null;
      const x = (ev.clientX - b.left - v.ox) / v.k, y = (ev.clientY - b.top - v.oy) / v.k;
      const ctx = this.cv.getContext("2d"); ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
      let hit = null; for (const [s, p] of Object.entries(this.paths)) if (ctx.isPointInPath(p, x, y)) { hit = s; break; }
      ctx.restore(); return hit;
    }
    zoomAt(f, mx, my) {
      const u = this.user; const z = Math.min(400, Math.max(1, u.z * f)); f = z / u.z; if (f === 1) return;
      u.z = z; u.ox = mx - (mx - u.ox) * f; u.oy = my - (my - u.oy) * f;
      if (z === 1) this.user = null;
      hideTip(); this.redraw();
    }
    fitState(st) {
      const [x0, y0, x1, y1] = this.geo.bbox[st], v = this.view, [FW] = this.geo.frame, k0 = v.W / FW;
      const pad = Math.max(x1 - x0, y1 - y0) * 0.08 + 2;
      const z = Math.min(60, Math.max(1.5, Math.min(v.W / (x1 - x0 + 2 * pad), v.H / (y1 - y0 + 2 * pad)) / k0));
      const kz = k0 * z;
      this.user = { z, ox: v.W / 2 - (x0 + x1) / 2 * kz, oy: v.H / 2 - (y0 + y1) / 2 * kz };
      hideTip(); this.redraw();
    }
    home() { this.user = null; this.redraw(); }
    bind() {
      const cv = this.cv;
      cv.addEventListener("wheel", (ev) => {
        if (!this.zoomed && !ev.ctrlKey && !ev.metaKey) return;          // let the page scroll past the national map
        ev.preventDefault();
        const b = cv.getBoundingClientRect();
        this.zoomAt(Math.exp(-(ev.deltaMode === 1 ? ev.deltaY * 16 : ev.deltaY) * 0.0022), ev.clientX - b.left, ev.clientY - b.top);
      }, { passive: false });
      cv.addEventListener("dblclick", (ev) => { ev.preventDefault(); const b = cv.getBoundingClientRect(); this.zoomAt(2, ev.clientX - b.left, ev.clientY - b.top); });
      const pts = new Map(); let last = null, pinch = null, moved = 0;
      cv.addEventListener("pointerdown", (ev) => {
        pts.set(ev.pointerId, [ev.clientX, ev.clientY]); last = [ev.clientX, ev.clientY]; moved = 0; pinch = null;
        if (this.zoomed) { cv.setPointerCapture(ev.pointerId); cv.style.cursor = "grabbing"; hideTip(); }
      });
      cv.addEventListener("pointermove", (ev) => {
        if (!pts.has(ev.pointerId)) {
          if (!this.zoomed && this.opts.tip && ev.pointerType === "mouse") { const h = this.opts.tip(ev); if (h) showTip(h, ev); else hideTip(); }
          else hideTip();
          return;
        }
        pts.set(ev.pointerId, [ev.clientX, ev.clientY]);
        if (pts.size === 2) {
          const [a, c] = [...pts.values()], d = Math.hypot(a[0] - c[0], a[1] - c[1]), cx = (a[0] + c[0]) / 2, cy = (a[1] + c[1]) / 2, b = cv.getBoundingClientRect();
          if (pinch) { this.zoomAt(d / pinch.d, cx - b.left, cy - b.top); if (this.user) { this.user.ox += cx - pinch.cx; this.user.oy += cy - pinch.cy; } }
          pinch = { d, cx, cy }; moved = 99; return;
        }
        if (!last || !this.zoomed) return;
        const dx = ev.clientX - last[0], dy = ev.clientY - last[1]; last = [ev.clientX, ev.clientY]; moved += Math.abs(dx) + Math.abs(dy);
        this.user.ox += dx; this.user.oy += dy; this.redraw();
      });
      const up = (ev) => {
        const was = pts.has(ev.pointerId); pts.delete(ev.pointerId);
        if (!pts.size) { last = null; pinch = null; cv.style.cursor = this.zoomed ? "grab" : "default"; }
        if (was && ev.type === "pointerup" && moved < 5 && !this.zoomed) { const st = this.stateAt(ev); if (st) this.fitState(st); }
      };
      cv.addEventListener("pointerup", up); cv.addEventListener("pointercancel", up);
      cv.addEventListener("pointerleave", hideTip);
      this.el.querySelectorAll("[data-z]").forEach((b) => b.addEventListener("click", () => {
        const v = this.view; if (!v) return;
        if (b.dataset.z === "home") this.home();
        else { if (!this.user) this.user = { z: 1, ox: 0, oy: 0 }; this.zoomAt(b.dataset.z === "in" ? 2 : 0.5, v.W / 2, v.H / 2); }
      }));
    }
  }

  // ---------------------------------------------------------------- timeline control
  function timeline(root, years, eras, onChange) {
    const input = root.querySelector('input[type="range"]'), ticks = root.querySelector(".tl-ticks"), play = root.querySelector("[data-play]");
    input.max = years.length - 1;
    ticks.innerHTML = years.map((y, i) => `<span data-i="${i}" class="${eras && eras.includes(y) ? "era" : ""}" style="left:${(100 * i / (years.length - 1)).toFixed(3)}%">${years.length > 14 && !(eras && eras.includes(y)) && i !== years.length - 1 ? "’" + String(y).slice(2) : y}</span>`).join("");
    const set = (i) => { input.value = i; ticks.querySelectorAll("span").forEach((s) => s.classList.toggle("on", +s.dataset.i === +i)); onChange(years[+i]); };
    input.addEventListener("input", () => set(+input.value));
    ticks.addEventListener("click", (e) => { const s = e.target.closest("span"); if (s) { stop(); set(+s.dataset.i); } });
    let timer = 0;
    const stop = () => { clearInterval(timer); timer = 0; play.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.5v11l9-5.5z"/></svg>'; play.setAttribute("aria-label", "Play through the years"); };
    play.addEventListener("click", () => {
      if (timer) return stop();
      if (+input.value >= years.length - 1) set(0);
      play.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.5h3v11H4zM9 2.5h3v11H9z"/></svg>'; play.setAttribute("aria-label", "Pause");
      timer = setInterval(() => { const i = +input.value + 1; if (i >= years.length) return stop(); set(i); }, reduceMotion ? 1600 : 1100);
    });
    return { set, get: () => years[+input.value], stop, setYears(ys, er) { stop(); years = ys; eras = er; return timeline(root, ys, er, onChange); } };
  }

  // ---------------------------------------------------------------- 01 · dots
  let geo, pres, house;
  const D = { race: "pres", year: 1976, scale: 1000, data: null, map: null };
  function dotYears() { return D.race === "pres" ? pres.years : house.years; }
  function drawDots(ctx, v) {
    const d = D.data; if (!d) return;
    const col = ["--D", "--R", "--I"].map(cssColor);
    const base = D.scale === 1000 ? 0.42 : D.scale === 10000 ? 1.3 : 3.0;
    const r = v.z > 1.02 ? base * Math.min(D.scale === 1000 ? 3.2 : 2.2, Math.max(1, Math.sqrt(v.k) * 0.75)) : base * Math.max(D.scale === 1000 ? 0.42 : 0.6, Math.min(1.35, v.k));
    const a = D.scale === 1000 ? (v.z > 1.02 ? 0.55 : 0.62) : D.scale === 10000 ? 0.7 : 0.8;
    const sq = D.scale === 1000; ctx.globalAlpha = a; let last = -1;
    for (let i = 0; i < d.n; i++) {
      const x = d.x[i] * v.k + v.ox, y = d.y[i] * v.k + v.oy;
      if (x < -4 || y < -4 || x > v.W + 4 || y > v.H + 4) continue;
      if (d.p[i] !== last) { last = d.p[i]; ctx.fillStyle = col[last]; }
      if (sq) ctx.fillRect(x - r, y - r, 2 * r, 2 * r); else { ctx.beginPath(); ctx.arc(x, y, r, 0, 6.2832); ctx.fill(); }
    }
    ctx.globalAlpha = 1;
  }
  function dotsLegend() {
    const L = $("#dots-legend"), y = D.year;
    if (D.race === "pres") {
      const [dv, rv, ov] = pres.national[y], t = dv + rv + ov, [dn, rn] = NOMINEES[y], w = PRES_WINNER[y];
      L.innerHTML = `<span class="${w === 0 ? "win" : ""}"><i style="background:var(--D)"></i>${dn} ${fmtM(dv)} · ${pct(dv, t)}%</span><span class="${w === 1 ? "win" : ""}"><i style="background:var(--R)"></i>${rn} ${fmtM(rv)} · ${pct(rv, t)}%</span>${ov > t * 0.005 ? `<span><i style="background:var(--I)"></i>Others ${fmtM(ov)} · ${pct(ov, t)}%</span>` : ""}<span class="mut">${D.data ? D.data.n.toLocaleString() : "…"} dots</span>`;
      $("#dots-title").textContent = `Every vote for president, ${y}`;
    } else {
      const s = house.seats[y], dist = house.district[y] || {};
      let dv = 0, rv = 0, ov = 0; for (const r of Object.values(dist)) { dv += r[1]; rv += r[2]; ov += r[3]; }
      const t = dv + rv + ov;
      L.innerHTML = `<span class="${s.D > s.R ? "win" : ""}"><i style="background:var(--D)"></i>Democrats ${fmtM(dv)} · ${pct(dv, t)}% · ${s.D} seats</span><span class="${s.R > s.D ? "win" : ""}"><i style="background:var(--R)"></i>Republicans ${fmtM(rv)} · ${pct(rv, t)}% · ${s.R} seats</span>${ov > t * 0.005 ? `<span><i style="background:var(--I)"></i>Others ${fmtM(ov)}</span>` : ""}<span class="mut">${D.data ? D.data.n.toLocaleString() : "…"} dots</span>`;
      $("#dots-title").textContent = `Every vote for the House, ${y}`;
    }
    $("#dots-note").textContent = (D.race === "pres"
      ? "Each dot is a block of votes for one candidate, placed inside the county where it was cast, near where people live today (Census 2020 block groups). Alaska reports no county results, so its dots are spread over the whole state. "
      : "Each dot is a block of votes for one party's House candidates, placed inside the district that year (its lines as drawn then), near where people live today. Unopposed members in states that don't count those votes (Florida, and Arkansas and Louisiana in some years) add no dots, so those states can look empty. ")
      + "Click a state to zoom in; scroll, pinch or double-click to zoom further and drag to pan. Hold ⌘ or Ctrl to zoom with the wheel from the national view.";
  }
  function loadDots() {
    const key = `${D.race}-${D.year}-${D.scale}`; D.want = key;
    getDots(D.race, D.year, D.scale).then((d) => { if (D.want !== key) return; D.data = d; dotsLegend(); D.map.draw(); })
      .catch((e) => { $("#dots-legend").innerHTML = `<span class="mut">The dot data didn't load (${esc(e.message)}). Pick a year again to retry.</span>`; });
    dotsLegend();
  }
  let dotsTL;
  function setupDots() {
    D.map = new MapView($("#dots-map"), geo, { layer: drawDots, tip: (ev) => {
      const st = D.map.stateAt(ev); if (!st) return null;
      return `<div class="h">${esc(STATE_NAMES[st] || st)}</div><div class="m">Click to zoom in</div>`;
    } });
    const mk = () => timeline($("#dots-tl"), dotYears(), null, (y) => { D.year = y; loadDots(); });
    dotsTL = mk();
    $$("[data-race]").forEach((b) => b.addEventListener("click", () => {
      if (D.race === b.dataset.race) return;
      $$("[data-race]").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      const old = D.year; D.race = b.dataset.race; dotsTL.stop(); dotsTL = mk();
      const ys = dotYears(); const near = ys.reduce((a, y) => (Math.abs(y - old) < Math.abs(a - old) ? y : a), ys[0]);
      dotsTL.set(ys.indexOf(near));
    }));
    $$("[data-scale]").forEach((b) => b.addEventListener("click", () => {
      $$("[data-scale]").forEach((x) => x.setAttribute("aria-pressed", String(x === b))); D.scale = +b.dataset.scale; loadDots();
    }));
    $("#dots-cities").addEventListener("click", (e) => { D.map.labels = !D.map.labels; e.currentTarget.setAttribute("aria-pressed", String(D.map.labels)); D.map.draw(); });
    dotsTL.set(0);
  }

  // ---------------------------------------------------------------- 02 · shift arrows
  const S = { from: 2020, to: 2024, map: null, arrows: null };
  function buildArrows() {
    const yi = (y) => pres.years.indexOf(y), a = yi(S.from), b = yi(S.to), out = [];
    let tot = { tD: 0, tR: 0, fD: 0, fR: 0 }, toD = 0, toR = 0;
    for (const [f, [x, y, , rows]] of Object.entries(pres.counties)) {
      const r0 = rows[a], r1 = rows[b]; if (!r0 || !r1) continue;
      const t0 = r0[0] + r0[1], t1 = r1[0] + r1[1]; if (t0 < 50 || t1 < 50) continue;
      const m0 = (r0[1] - r0[0]) / t0, m1 = (r1[1] - r1[0]) / t1, sh = (m1 - m0) * 100;
      out.push([x, y, sh, t1, f]);
      tot.fD += r0[0]; tot.fR += r0[1]; tot.tD += r1[0]; tot.tR += r1[1];
      if (sh < 0) toD++; else toR++;
    }
    out.sort((p, q) => p[3] - q[3]);
    S.arrows = out; S.tot = tot; S.toD = toD; S.toR = toR;
  }
  function drawArrows(ctx, v) {
    if (!S.arrows) return;
    const cD = cssColor("--D"), cR = cssColor("--R");
    const zoomK = Math.min(5, Math.sqrt(v.z));
    const L = 1.15 * zoomK * Math.min(1.4, v.W / 960);            // px per point of margin shift
    ctx.lineCap = "round";
    for (const [fx, fy, sh, t] of S.arrows) {
      const x = fx * v.k + v.ox, y = fy * v.k + v.oy;
      if (x < -60 || y < -60 || x > v.W + 60 || y > v.H + 60) continue;
      const len = Math.min(90 * zoomK, Math.abs(sh) * L); if (len < 0.8) continue;
      const dir = sh < 0 ? -1 : 1, ang = (dir < 0 ? 180 + 35 : -35) * Math.PI / 180;
      const ex = x + Math.cos(ang) * len, ey = y + Math.sin(ang) * len;
      const w = Math.max(0.6, Math.min(4.5, Math.sqrt(t) / 160)) * Math.min(2, Math.sqrt(zoomK));
      ctx.strokeStyle = dir < 0 ? cD : cR; ctx.fillStyle = ctx.strokeStyle; ctx.globalAlpha = 0.78; ctx.lineWidth = w;
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(ex, ey); ctx.stroke();
      const hl = Math.min(len * 0.45, 3 + w * 2.2), a1 = ang + Math.PI * 0.82, a2 = ang - Math.PI * 0.82;
      ctx.beginPath(); ctx.moveTo(ex + Math.cos(ang) * w * 0.6, ey + Math.sin(ang) * w * 0.6);
      ctx.lineTo(ex + Math.cos(a1) * hl, ey + Math.sin(a1) * hl); ctx.lineTo(ex + Math.cos(a2) * hl, ey + Math.sin(a2) * hl); ctx.closePath(); ctx.fill();
    }
    ctx.globalAlpha = 1;
  }
  function shiftLegend() {
    const t = S.tot, m0 = (t.fR - t.fD) / (t.fR + t.fD) * 100, m1 = (t.tR - t.tD) / (t.tR + t.tD) * 100, sh = m1 - m0;
    const side = (m) => (m < 0 ? `D+${(-m).toFixed(1)}` : `R+${m.toFixed(1)}`);
    $("#shift-title").textContent = `How every county moved, ${S.from} to ${S.to}`;
    $("#shift-legend").innerHTML = `<span>Nation: ${side(m0)} → ${side(m1)}, <b style="color:var(${sh < 0 ? "--D" : "--R"})">${sh < 0 ? "D" : "R"} +${Math.abs(sh).toFixed(1)}</b></span>`
      + `<span class="arrow"><svg width="28" height="14" aria-hidden="true"><path d="M26 11 L6 3" stroke="var(--D)" stroke-width="2.4" stroke-linecap="round"/><path d="M3 2 l6 0 l-2 5z" fill="var(--D)"/></svg>${S.toD.toLocaleString()} counties toward the Democrat</span>`
      + `<span class="arrow"><svg width="28" height="14" aria-hidden="true"><path d="M2 11 L22 3" stroke="var(--R)" stroke-width="2.4" stroke-linecap="round"/><path d="M25 2 l-6 0 l2 5z" fill="var(--R)"/></svg>${S.toR.toLocaleString()} toward the Republican</span>`;
  }
  function setupShift() {
    const opts = pres.years.map((y) => `<option value="${y}">${y}</option>`).join("");
    const fromSel = $("#shift-from"), toSel = $("#shift-to");
    fromSel.innerHTML = opts; toSel.innerHTML = opts; fromSel.value = S.from; toSel.value = S.to;
    const nearest = (ev) => {
      const b = S.map.cv.getBoundingClientRect(), v = S.map.view, mx = ev.clientX - b.left, my = ev.clientY - b.top;
      let best = null, bd = 144;
      for (const a of S.arrows) { const x = a[0] * v.k + v.ox, y = a[1] * v.k + v.oy, d = (x - mx) ** 2 + (y - my) ** 2; if (d < bd) { bd = d; best = a; } }
      return best;
    };
    const tipFor = (ev) => {
      const a = nearest(ev); if (!a) { const st = S.map.stateAt(ev); return st ? `<div class="h">${esc(STATE_NAMES[st] || st)}</div><div class="m">Click to zoom in</div>` : null; }
      const row = pres.counties[a[4]][3], i0 = pres.years.indexOf(S.from), i1 = pres.years.indexOf(S.to);
      const mm = (r) => { const m = (r[1] - r[0]) / (r[0] + r[1]) * 100; return m < 0 ? `D+${(-m).toFixed(1)}` : `R+${m.toFixed(1)}`; };
      const cc = pres.counties[a[4]];
      return `<div class="h">${esc(cc[4] || a[4])}${cc[5] && cc[5] !== "DC" && cc[4] && !cc[4].includes("Alaska") ? ", " + cc[5] : ""}</div><div class="r"><span>${S.from}</span><span>${mm(row[i0])}</span></div><div class="r"><span>${S.to}</span><span>${mm(row[i1])}</span></div><div class="m">Shift ${a[2] < 0 ? "D" : "R"} +${Math.abs(a[2]).toFixed(1)} · ${(row[i1][0] + row[i1][1] + row[i1][2]).toLocaleString()} votes</div>`;
    };
    S.map = new MapView($("#shift-map"), geo, { layer: drawArrows, tip: tipFor });
    S.map.labels = true;
    const go = () => { S.from = +fromSel.value; S.to = +toSel.value; buildArrows(); shiftLegend(); S.map.draw(); };
    fromSel.addEventListener("change", go); toSel.addEventListener("change", go);
    $$("[data-pair]").forEach((b) => b.addEventListener("click", () => { const [a, c] = b.dataset.pair.split(","); fromSel.value = a; toSel.value = c; go(); }));
    go();
  }

  // ---------------------------------------------------------------- 03 · House hex timeline
  const Hs = { year: 1976, mode: "won", base: null };
  const eraOf = (y) => house.eras.find(([a, b]) => a <= y && y <= b)[0];
  function hexShade(rec) {
    const [w, d, r] = rec, t = d + r; if (!t) return w === 0 ? "var(--D3)" : w === 1 ? "var(--R3)" : "var(--I)";
    const m = Math.abs(d - r) / t * 100, i = m < 5 ? 1 : m < 15 ? 2 : m < 30 ? 3 : 4;
    return w === 2 ? "var(--I)" : `var(--${w === 0 ? "D" : "R"}${i})`;
  }
  function shiftShade(sh) {
    if (sh == null) return "var(--N)";
    const a = Math.abs(sh), i = a < 2 ? 1 : a < 6 ? 2 : a < 12 ? 3 : 4;
    return `var(--${sh < 0 ? "D" : "R"}${i})`;
  }
  const margin = (rec) => { const t = rec[1] + rec[2]; return t ? (rec[2] - rec[1]) / t * 100 : (rec[0] === 0 ? -100 : 100); };
  function drawHex() {
    const y = Hs.year, era = eraOf(y), layout = house.hex[String(era)], recs = house.district[y] || {};
    const svg = $("#hexmap"), NS = "http://www.w3.org/2000/svg";
    const cells = Object.entries(layout);
    const cols = Math.max(...cells.map(([, [c]]) => c)) + 2, rows = Math.max(...cells.map(([, [, r]]) => r)) + 2;
    const s = 10, w = Math.sqrt(3) * s, h = 1.5 * s;
    const pos = (c, r) => [c * w + (r & 1 ? w / 2 : 0) + w, r * h + s + 4];
    svg.setAttribute("viewBox", `0 0 ${cols * w + w} ${rows * h + s * 2}`);
    svg.innerHTML = "";
    const defs = document.createElementNS(NS, "defs");
    defs.innerHTML = `<pattern id="flip" patternUnits="userSpaceOnUse" width="4" height="4" patternTransform="rotate(45)"><rect width="4" height="4" fill="transparent"/><rect width="1.6" height="4" fill="var(--bg)" opacity=".85"/></pattern>`;
    svg.appendChild(defs);
    const g = document.createElementNS(NS, "g"); svg.appendChild(g);
    const corner = (x, yy, i, rr) => { const a = Math.PI / 180 * (60 * i - 30); return [x + rr * Math.cos(a), yy + rr * Math.sin(a)]; };
    const at = {};
    const baseRecs = Hs.mode === "shift" && Hs.base ? house.district[Hs.base] || {} : null;
    for (const [k, [c, r]] of cells) {
      at[c + "," + r] = k;
      const [x, yy] = pos(c, r), rec = recs[k];
      let fill = "var(--N)";
      if (rec) fill = baseRecs ? shiftShade(baseRecs[k] && rec[1] + rec[2] && baseRecs[k][1] + baseRecs[k][2] ? margin(rec) - margin(baseRecs[k]) : null) : hexShade(rec);
      const p = document.createElementNS(NS, "polygon");
      p.setAttribute("points", [0, 1, 2, 3, 4, 5].map((i) => corner(x, yy, i, s * 0.98).join(",")).join(" "));
      p.setAttribute("fill", fill); p.dataset.k = k;
      g.appendChild(p);
      const flip = baseRecs ? (rec && baseRecs[k] && rec[0] !== baseRecs[k][0]) : rec && rec[4];
      if (flip) { const f = p.cloneNode(); f.setAttribute("fill", "url(#flip)"); f.style.pointerEvents = "none"; g.appendChild(f); }
    }
    // state borders: edges between hexes of different states (or the outside)
    const nb = (c, r) => (r & 1 ? [[1, 0], [1, 1], [0, 1], [-1, 0], [0, -1], [1, -1]] : [[1, 0], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1]]).map(([a, b]) => [c + a, r + b]);
    let d = "";
    for (const [k, [c, r]] of cells) {
      const st = k.split("-")[0], [x, yy] = pos(c, r), ns = nb(c, r);
      for (let i = 0; i < 6; i++) {
        const o = at[ns[i][0] + "," + ns[i][1]];
        if (o && o.split("-")[0] === st) continue;
        const p0 = corner(x, yy, i, s), p1 = corner(x, yy, (i + 1) % 6, s);
        d += `M${p0[0].toFixed(1)},${p0[1].toFixed(1)}L${p1[0].toFixed(1)},${p1[1].toFixed(1)}`;
      }
    }
    const border = document.createElementNS(NS, "path"); border.setAttribute("d", d); border.setAttribute("class", "st-border"); g.appendChild(border);
    svg.onmousemove = (ev) => {
      const k = ev.target.dataset && ev.target.dataset.k; if (!k) return hideTip();
      const rec = recs[k]; if (!rec) return showTip(`<div class="h">${k}</div><div class="m">No result</div>`, ev);
      const t = rec[1] + rec[2] + rec[3], who = ["Democrat", "Republican", "Independent / other"][rec[0]];
      let extra = "";
      if (baseRecs && baseRecs[k]) { const sh = margin(rec) - margin(baseRecs[k]); extra = `<div class="m">Since ${Hs.base}: ${sh < 0 ? "D" : "R"} +${Math.abs(sh).toFixed(1)}${rec[0] !== baseRecs[k][0] ? " · changed hands" : ""}</div>`; }
      else if (rec[4]) extra = `<div class="m">Changed hands this election</div>`;
      showTip(`<div class="h">${k} · ${y}</div><div class="r"><span>Won by</span><span>${who}</span></div>${t ? `<div class="r"><span>D / R</span><span>${pct(rec[1], t)}% / ${pct(rec[2], t)}%</span></div>` : `<div class="m">Unopposed or votes not counted</div>`}${extra}`, ev);
    };
    svg.onmouseleave = hideTip;
  }
  function seatBar() {
    const y = Hs.year, s = house.seats[y], i = house.years.indexOf(y), prev = i > 0 ? house.seats[house.years[i - 1]] : null;
    const dd = prev ? s.D - prev.D : 0;
    const delta = !prev || !dd ? "" : `<span class="delta ${dd > 0 ? "d" : "r"}">${dd > 0 ? "D" : "R"} +${Math.abs(dd)}</span>`;
    const tot = s.D + s.R + s.O;
    $("#house-bar").innerHTML = `<div class="nums"><span class="d">Democrats ${s.D}${delta}</span><span class="maj">218 for a majority${s.O ? ` · ${s.O} other` : ""}</span><span class="r">${s.R} Republicans</span></div>`
      + `<div class="bar"><span style="flex-basis:${100 * s.D / tot}%;background:var(--D)"></span><span style="flex-basis:${100 * s.O / tot}%;background:var(--I)"></span><span style="flex-basis:${100 * s.R / tot}%;background:var(--R)"></span><i class="mid"></i></div>`;
    $("#house-title").textContent = `The House, ${y}${y === 2026 ? " (leaders in uncalled races)" : ""}`;
  }
  function houseLegend() {
    const ramp = (p) => `<span class="ramp">${[1, 2, 3, 4].map((i) => `<i style="background:var(--${p}${i})"></i>`).join("")}</span>`;
    $("#house-legend").innerHTML = Hs.mode === "shift"
      ? `<span>${ramp("D")} toward Democrats</span><span>${ramp("R")} toward Republicans</span><span class="mut">under 2 · 2–6 · 6–12 · 12+ points</span><span><i class="sw flip"></i> changed hands since ${Hs.base || "then"}</span><span><i class="sw" style="background:var(--N)"></i> no contested vote in one of the years</span>`
      : `<span>${ramp("D")} Democrat</span><span>${ramp("R")} Republican</span><span class="mut">margin under 5 · 5–15 · 15–30 · 30+ points</span><span><i class="sw flip"></i> changed hands</span><span><i class="sw" style="background:var(--I)"></i> independent</span>`;
  }
  function houseNote() {
    houseLegend();
    const y = Hs.year, era = eraOf(y), [a, b] = house.eras.find(([p]) => p === era);
    const span = a === b ? `${a}` : `${a}–${b}`;
    $("#house-note").textContent = `One hexagon per seat, arranged by where each district sat on the map in ${span}. The layout changes when districts are redrawn after each census (1982, 1992, 2002, 2012, 2022) and for 2026, so a hexagon only stands for the same seat within those years. `
      + (Hs.mode === "shift" ? `Shift compares each seat's two-party margin with ${Hs.base}; stripes mark seats that changed hands since then. Seats whose lines moved mid-decade (Texas 2004, Ohio 2022 and others) compare the same seat number on different ground.`
        : `Shade is the winner's margin; stripes mark seats that changed hands from the previous election. Seat counts come from the MIT election returns and can differ by a seat from the official tally (1978 shows 278–157).`);
  }
  let houseTL;
  function setupHouse() {
    const eraStarts = house.eras.map(([a]) => a);
    houseTL = timeline($("#house-tl"), house.years, eraStarts, (y) => { Hs.year = y; syncBase(); seatBar(); drawHex(); houseNote(); });
    $$("[data-hmode]").forEach((b) => b.addEventListener("click", () => {
      $$("[data-hmode]").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      Hs.mode = b.dataset.hmode; $("#house-base-pick").hidden = Hs.mode !== "shift"; syncBase(); drawHex(); houseNote();
    }));
    $("#house-base").addEventListener("change", (e) => { Hs.base = +e.target.value; drawHex(); houseNote(); });
    houseTL.set(0);
  }
  function syncBase() {
    const era = eraOf(Hs.year), [a, b] = house.eras.find(([p]) => p === era);
    const ys = house.years.filter((y) => y >= a && y <= b && y !== Hs.year);
    const sel = $("#house-base");
    sel.innerHTML = ys.length ? ys.map((y) => `<option value="${y}">${y}</option>`).join("") : `<option value="">No other year on these lines</option>`;
    if (!ys.includes(Hs.base)) Hs.base = ys.length ? ys.filter((y) => y < Hs.year).pop() ?? ys[0] : null;
    if (Hs.base) sel.value = Hs.base;
  }

  // ---------------------------------------------------------------- boot
  function redrawAll() { if (D.map) D.map.draw(); if (S.map) S.map.draw(); }
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") { if (D.map && D.map.zoomed) D.map.home(); if (S.map && S.map.zoomed) S.map.home(); } });
  let rt = 0; addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(redrawAll, 120); });
  Promise.all([getJSON("data/geo.json"), getJSON("data/pres.json"), getJSON("data/house.json")]).then(([g, p, h]) => {
    geo = g; pres = p; house = h;
    house.years = house.years.map(Number);
    setupDots(); setupShift(); setupHouse();
  }).catch((e) => {
    document.querySelector("main").insertAdjacentHTML("afterbegin", `<p class="note">The election data didn't load (${esc(e.message)}). Reload to try again.</p>`);
  });
})();
