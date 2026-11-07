/* ==========================================================================
   2026 U.S. Midterm Election results · sadh.app/election2026
   Vanilla JS · Zero external runtime dependencies
   ========================================================================== */

(function () {
  "use strict";

  const NS = "http://www.w3.org/2000/svg";

  const ICONS = {
    expand: `<svg class="ico" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 2.5h3.5V6M6 13.5H2.5V10M13.5 2.5L9.2 6.8M2.5 13.5l4.3-4.3"/></svg>`,
    star: `<svg class="ico-star" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 1.3l2.02 4.1 4.53.66-3.28 3.19.77 4.51L8 11.63l-4.04 2.13.77-4.51L1.45 6.06l4.53-.66L8 1.3z"/></svg>`,
    clock: `<svg class="ico-star" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="8" cy="8" r="6"/><path d="M8 4.8V8l2.2 1.4" stroke-linecap="round"/></svg>`,
    check: `<svg class="ico-star" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8.5l3.2 3.2L13 4.8"/></svg>`,
    cross: `<svg class="ico-star" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M4.2 4.2l7.6 7.6M11.8 4.2l-7.6 7.6"/></svg>`
  };

  function svgStarPath(cx, cy, rOuter, rInner) {
    const pts = [];
    for (let i = 0; i < 10; i++) {
      const ang = -Math.PI / 2 + (i * Math.PI) / 5;
      const r = i % 2 === 0 ? rOuter : rInner;
      pts.push(`${(cx + r * Math.cos(ang)).toFixed(2)},${(cy + r * Math.sin(ang)).toFixed(2)}`);
    }
    return `M${pts.join("L")}Z`;
  }

  const STATE_GRID = [
    ["AK", 1, 1], ["ME", 12, 1],
    ["VT", 10, 2], ["NH", 11, 2],
    ["WA", 2, 3], ["ID", 3, 3], ["MT", 4, 3], ["ND", 5, 3], ["MN", 6, 3], ["WI", 7, 3], ["MI", 8, 3], ["NY", 10, 3], ["MA", 11, 3], ["RI", 12, 3],
    ["OR", 2, 4], ["NV", 3, 4], ["WY", 4, 4], ["SD", 5, 4], ["IA", 6, 4], ["IL", 7, 4], ["IN", 8, 4], ["OH", 9, 4], ["PA", 10, 4], ["NJ", 11, 4], ["CT", 12, 4],
    ["CA", 2, 5], ["UT", 3, 5], ["CO", 4, 5], ["NE", 5, 5], ["MO", 6, 5], ["KY", 7, 5], ["WV", 8, 5], ["VA", 9, 5], ["MD", 10, 5], ["DE", 11, 5],
    ["AZ", 3, 6], ["NM", 4, 6], ["KS", 5, 6], ["AR", 6, 6], ["TN", 7, 6], ["NC", 8, 6], ["SC", 9, 6],
    ["OK", 5, 7], ["LA", 6, 7], ["MS", 7, 7], ["AL", 8, 7], ["GA", 9, 7],
    ["HI", 1, 8], ["TX", 5, 8], ["FL", 10, 8]
  ];

  const STATE_NAMES = {
    AL:"Alabama", AK:"Alaska", AZ:"Arizona", AR:"Arkansas", CA:"California", CO:"Colorado",
    CT:"Connecticut", DE:"Delaware", FL:"Florida", GA:"Georgia", HI:"Hawaii", ID:"Idaho",
    IL:"Illinois", IN:"Indiana", IA:"Iowa", KS:"Kansas", KY:"Kentucky", LA:"Louisiana",
    ME:"Maine", MD:"Maryland", MA:"Massachusetts", MI:"Michigan", MN:"Minnesota", MS:"Mississippi",
    MO:"Missouri", MT:"Montana", NE:"Nebraska", NV:"Nevada", NH:"New Hampshire", NJ:"New Jersey",
    NM:"New Mexico", NY:"New York", NC:"North Carolina", ND:"North Dakota", OH:"Ohio", OK:"Oklahoma",
    OR:"Oregon", PA:"Pennsylvania", RI:"Rhode Island", SC:"South Carolina", SD:"South Dakota",
    TN:"Tennessee", TX:"Texas", UT:"Utah", VT:"Vermont", VA:"Virginia", WA:"Washington",
    WV:"West Virginia", WI:"Wisconsin", WY:"Wyoming"
  };

  const SHORT_LABELS = {
    "Economy & Cost of Living": "Economy",
    "State of Democracy": "Democracy",
    "Foreign Policy (Iran)": "Foreign policy",
    "First-time midterm voters": "First-time voters",
    "Didn't vote in 2024": "Didn't vote '24",
    "Didn’t vote in 2024": "Didn't vote '24",
    "Voted Trump in 2024": "Trump '24 voters",
    "Voted Harris in 2024": "Harris '24 voters",
    "Policies on transgender people": "Transgender policy",
    "Artificial intelligence": "AI",
    "Government corruption": "Corruption",
    "Small town / rural": "Rural"
  };
  function shortLabel(t, narrow) { return narrow && SHORT_LABELS[t] ? SHORT_LABELS[t] : t; }

  function S(tag, attrs, parent) {
    const el = document.createElementNS(NS, tag);
    for (const k in attrs) {
      if (attrs[k] !== undefined && attrs[k] !== null && attrs[k] !== "") {
        el.setAttribute(k, attrs[k]);
      }
    }
    if (parent) parent.appendChild(el);
    return el;
  }

  function H(tag, attrs, parent, html) {
    const el = document.createElement(tag);
    for (const k in attrs) {
      if (attrs[k] !== undefined && attrs[k] !== null) el.setAttribute(k, attrs[k]);
    }
    if (html !== undefined && html !== null) el.innerHTML = html;
    if (parent) parent.appendChild(el);
    return el;
  }

  function esc(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function fmtMargin(m, called) {
    if (m === null || m === undefined) return "n/a";
    const abs = Math.abs(m);
    const party = m >= 0 ? "D" : "R";
    const txt = abs < 0.08 ? `${party}+<0.1` : `${party}+${abs.toFixed(1)}`;
    return called === false ? `${txt}*` : txt;
  }

  function fmtSwing(sw) {
    if (sw === null || sw === undefined) return "n/a";
    const abs = Math.abs(sw).toFixed(1);
    return sw >= 0 ? `D+${abs}` : `R+${abs}`;
  }

  async function loadData() {
    if (window.ELECTION_DATA) return window.ELECTION_DATA;
    const res = await fetch("./data.json");
    return res.json();
  }

  /* ------------------------------------------------------------------------
     Floating Dark Tooltip (#tip)
     ------------------------------------------------------------------------ */
  const tip = document.getElementById("tip");

  function showTip(html, ev) {
    if (!tip) return;
    tip.innerHTML = html;
    tip.style.opacity = "1";
    moveTip(ev);
  }

  function moveTip(ev) {
    if (!tip) return;
    const x = ev.clientX;
    const y = ev.clientY;
    const w = tip.offsetWidth || 220;
    const h = tip.offsetHeight || 80;
    let l = x + 14;
    let t = y + 14;
    if (l + w > window.innerWidth - 10) l = x - w - 14;
    if (t + h > window.innerHeight - 10) t = y - h - 14;
    tip.style.left = Math.max(8, l) + "px";
    tip.style.top = Math.max(8, t) + "px";
  }

  function hideTip() {
    if (tip) tip.style.opacity = "0";
  }

  function bindTip(el, fn) {
    el.addEventListener("mouseenter", (e) => showTip(fn(), e));
    el.addEventListener("mousemove", moveTip);
    el.addEventListener("mouseleave", hideTip);
  }

  function bindStaticTips(root = document) {
    root.querySelectorAll("[data-tip]").forEach((el) => {
      if (el.dataset.tipBound) return;
      el.dataset.tipBound = "1";
      bindTip(el, () => `<div>${esc(el.dataset.tip)}</div>`);
      el.addEventListener("focus", () => {
        const r = el.getBoundingClientRect();
        showTip(`<div>${esc(el.dataset.tip)}</div>`, { clientX: r.left + r.width / 2, clientY: r.bottom });
      });
      el.addEventListener("blur", hideTip);
    });
  }

  document.addEventListener("scroll", hideTip, { passive: true });

  /* ------------------------------------------------------------------------
     Theme Popover Controller
     ------------------------------------------------------------------------ */
  function initThemeControls(onSchemeChange) {
    const meta = document.querySelector('meta[name="color-scheme"]');
    const opts = document.querySelectorAll(".theme-opt[data-scheme]");
    const sysSpan = document.getElementById("sys-current-label");
    const mql = window.matchMedia("(prefers-color-scheme: dark)");

    function getStored() {
      try { return localStorage.getItem("color-scheme"); } catch (e) { return null; }
    }

    function syncUI() {
      const stored = getStored();
      const sysMode = mql.matches ? "dark" : "light";
      if (sysSpan) sysSpan.textContent = `Currently ${sysMode}`;
      const activeVal = stored === "light" || stored === "dark" ? stored : "system";
      opts.forEach((btn) => {
        btn.setAttribute("aria-pressed", btn.dataset.scheme === activeVal ? "true" : "false");
      });
      if (onSchemeChange) onSchemeChange();
    }

    opts.forEach((btn) => {
      btn.addEventListener("click", () => {
        const choice = btn.dataset.scheme;
        if (choice === "system") {
          try { localStorage.removeItem("color-scheme"); } catch (e) {}
          meta.content = "light dark";
        } else {
          try { localStorage.setItem("color-scheme", choice); } catch (e) {}
          meta.content = choice;
        }
        syncUI();
      });
    });

    mql.addEventListener("change", () => syncUI());
    window.addEventListener("storage", (e) => {
      if (e.key === "color-scheme") {
        meta.content = e.newValue ?? "light dark";
        syncUI();
      }
    });
    syncUI();
  }

  /* ------------------------------------------------------------------------
     Maximize Any Box Controller (<dialog closedby="any">)
     ------------------------------------------------------------------------ */
  function initMaximizeBoxes(redrawResponsive) {
    const dialog = document.getElementById("box-zoom-dialog");
    const stage = document.getElementById("box-zoom-stage");
    const titleEl = document.getElementById("box-zoom-title");
    if (!dialog || !stage) return;

    let activeBox = null;
    let placeholder = null;
    let activeBtn = null;

    // Fallback for browsers without native dialog closedby="any"
    if (!("closedBy" in HTMLDialogElement.prototype)) {
      const isOutside = (e) => {
        const r = dialog.getBoundingClientRect();
        return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
      };
      let pressedOutside = false;
      dialog.addEventListener("pointerdown", (e) => {
        pressedOutside = e.target === dialog && isOutside(e);
      });
      dialog.addEventListener("pointerup", (e) => {
        if (pressedOutside && e.target === dialog && isOutside(e)) dialog.close();
        pressedOutside = false;
      });
    }

    document.querySelectorAll(".viz-box[data-maximizable]").forEach((box) => {
      const head = box.querySelector(".fig-head");
      if (!head) return;
      const label = box.dataset.zoomTitle || "Chart";
      const btn = H(
        "button",
        {
          type: "button",
          class: "expand-btn",
          "aria-label": `Expand ${label}`
        },
        head,
        ICONS.expand
      );
      bindTip(btn, () => `<div>Expand: <b>${esc(label)}</b></div>`);

      btn.addEventListener("click", () => {
        if (activeBox) return;
        hideTip();
        activeBox = box;
        activeBtn = btn;
        placeholder = document.createElement("div");
        placeholder.style.minBlockSize = `${box.offsetHeight}px`;
        box.replaceWith(placeholder);

        box.classList.add("is-maximized");
        stage.appendChild(box);
        if (tip) dialog.appendChild(tip);
        if (titleEl) titleEl.textContent = label;

        dialog.showModal();
        requestAnimationFrame(() => {
          if (redrawResponsive) redrawResponsive();
        });
      });
    });

    dialog.addEventListener("close", () => {
      dialog.returnValue = "";
      hideTip();
      if (tip && tip.parentElement !== document.body) {
        document.body.appendChild(tip);
      }
      if (activeBox && placeholder) {
        activeBox.classList.remove("is-maximized");
        placeholder.replaceWith(activeBox);
        const btnToFocus = activeBtn;
        activeBox = null;
        placeholder = null;
        activeBtn = null;
        requestAnimationFrame(() => {
          if (redrawResponsive) redrawResponsive();
          if (btnToFocus) btnToFocus.focus({ preventScroll: true });
        });
      }
    });
  }

  /* ------------------------------------------------------------------------
     Main Application Init
     ------------------------------------------------------------------------ */
  function initApp(data) {
    const senBySt = new Map(data.senate.races.map((r) => [r.st, r]));
    const senHoldBySt = new Map(data.senate.holdovers.map((h) => [h.st, h]));
    const govBySt = new Map(data.governors.races.map((r) => [r.st, r]));
    const govHoldBySt = new Map(data.governors.holdovers.map((h) => [h.st, h]));
    const pres24 = data.pres2024_d || {};
    const evMap = data.electoral_votes || {};
    const natVote = data.house.national_vote || { D_votes: 59215990, R_votes: 46888635, margin: 11.62, d_leading: 24, r_leading: 29, flips_projected: 31 };

    // Normalize 435 districts
    const DISTRICTS = (data.house.districts || []).map((raw) => {
      const cands = raw.c.map(([p, n, v, pct, inc, w]) => ({
        p, n, v, pct, inc: inc === 1, w: w === 1
      }));
      const win = cands.find((x) => x.w);
      const lead = win || cands[0];
      const topD = cands.find((x) => x.p === "D");
      const topR = cands.find((x) => x.p === "R");
      const same = cands.length > 1 && cands[0].p === cands[1].p;
      const uncontested = cands.length === 1;
      const margin = topD && topR
        ? topD.pct - topR.pct
        : lead.p === "D" ? 100 : lead.p === "R" ? -100 : 0;
      return {
        id: raw.id,
        st: raw.st,
        n: raw.n,
        pin: raw.pin,
        flip: raw.flip,
        tv: raw.tv,
        c: cands,
        called: Boolean(win),
        lead,
        margin,
        same,
        uncontested,
        el: null
      };
    });
    const distById = new Map(DISTRICTS.map((d) => [d.id, d]));

    const houseBySt = new Map();
    data.house.flips.forEach((f) => {
      if (!houseBySt.has(f.st)) houseBySt.set(f.st, []);
      houseBySt.get(f.st).push(f);
    });

    const measBySt = new Map();
    data.measures.forEach((m) => {
      if (!measBySt.has(m.st)) measBySt.set(m.st, []);
      measBySt.get(m.st).push(m);
    });

    const state = {
      arrowOffice: "senate",
      scatterMode: "senate",
      hgridFilter: "all",
      houseFilter: "all",
      mapMode: "senate",
      selectedSt: null,
      uncalledShowAll: false,
      exitState: "US",
      exitCat: "all",
      measureTopic: "all",
      tableChamber: "senate",
      tableFilter: "all",
      tableQuery: "",
      sim: {
        akSen: "D",
        msSen: "D",
        akGov: "D",
        ksGov: "D",
        orGov: "D",
        houseDem: 258
      }
    };

    /* ----------------------------------------------------------------------
       0. Stacked Balance of Power + 5-Stat Strip + Narrative Prose
       ---------------------------------------------------------------------- */
    function renderMetaText() {
      let lbl = (data.meta.as_of_label || "").split(" (")[0].replace(" · ", ", ");
      const t = data.meta.as_of ? new Date(data.meta.as_of) : null;
      if (t && !isNaN(t)) {
        const part = (o) => new Intl.DateTimeFormat("en-US", { timeZone: "America/Los_Angeles", ...o }).format(t);
        const hm = part({ hour: "numeric", minute: "2-digit" }).replace(/\s?AM$/, " a.m.").replace(/\s?PM$/, " p.m.");
        lbl = `${part({ month: "short" })}. ${part({ day: "numeric" })}, ${part({ year: "numeric" })}, ${hm} PT`;
      }
      document.querySelectorAll("[data-asof]").forEach((el) => { el.textContent = lbl; });
      const setCnt = (sel, n, tip) => {
        const b = document.querySelector(sel);
        if (!b) return;
        const c = b.querySelector(".cnt");
        if (c) c.textContent = n;
        if (tip) b.dataset.tip = tip;
      };
      const fl = data.house.flips || [];
      const nFlip = DISTRICTS.filter((d) => d.flip).length;
      const nUnc = DISTRICTS.filter((d) => !d.called).length;
      setCnt('[data-hf="flip"]', nFlip, `${nFlip} seats projected to change party`);
      setCnt('[data-hf="unc"]', nUnc, `${nUnc} districts still counting votes`);
      setCnt('[data-house-filter="all"]', fl.length);
      setCnt('[data-house-filter="called"]', fl.filter((f) => f.called).length, `${fl.filter((f) => f.called).length} called Democratic pickups`);
      setCnt('[data-house-filter="uncalled"]', fl.filter((f) => !f.called).length, `${fl.filter((f) => !f.called).length} uncalled GOP-held seats where a Democrat leads`);
      setCnt('[data-house-filter="incumbent"]', fl.filter((f) => f.type === "incumbent").length);
      setCnt('[data-map-mode="house"]', fl.length);
      const races = { sen: new Map(data.senate.races.map((r) => [r.st, r])), gov: new Map(data.governors.races.map((r) => [r.st, r])) };
      document.querySelectorAll("[data-v]").forEach((el) => {
        const [o, st, f] = el.dataset.v.split(":");
        const r = races[o] && races[o].get(st);
        if (!r) return;
        const m = r.margin;
        let t = null;
        if (f === "wpct" || f === "rpct") t = r[f] != null ? `${Number(r[f]).toFixed(1)}%` : null;
        else if (f === "margin") t = m != null ? fmtMargin(m, true) : null;
        else if (f === "mabs") t = m != null ? `+${Math.abs(m).toFixed(1)}` : null;
        else if (f === "mabsn") t = m != null ? Math.abs(m).toFixed(1) : null;
        if (t) el.textContent = t;
      });
      {
        const gc = data.governors.races.filter((r) => r.called !== false);
        const gD = data.governors.not_up.D + gc.filter((r) => r.wp !== "R").length;
        const gR = data.governors.not_up.R + gc.filter((r) => r.wp === "R").length;
        document.querySelectorAll("[data-gov-tally]").forEach((el) => { el.textContent = `${gD}–${gR}`; });
        document.querySelectorAll("[data-gov-unc]").forEach((el) => { el.textContent = String(data.governors.races.length - gc.length); });
      }
      const uc = document.getElementById("uncalled-prose");
      if (uc) {
        const hU = DISTRICTS.filter((d) => !d.called).length;
        const sU = data.senate.races.filter((r) => r.called === false);
        const gU = data.governors.races.filter((r) => r.called === false);
        const n = (k, one, many) => `${k} ${k === 1 ? one : many}`;
        uc.textContent = `${n(hU, "House seat", "House seats")}, ${n(sU.length, "Senate contest", "Senate contests")} and ${n(gU.length, "governorship", "governorships")} remain uncalled. California and Washington tabulate mail ballots for days after Election Day; Alaska runs its ranked-choice rounds in mid-November; Mississippi holds no runoff, so its plurality leader wins.`;
      }
    }
    renderMetaText();

    function renderHeroBOP() {
      const bopEl = document.getElementById("bop");
      const lgEl = document.getElementById("boplg");
      const statsEl = document.getElementById("stats");
      if (!bopEl) return;

      bopEl.innerHTML = "";

      const hUnc = DISTRICTS.filter((d) => !d.called);
      const hDl = hUnc.filter((d) => d.lead.p === "D").length;
      const hRl = hUnc.length - hDl;

      const tally = (races, notUp) => {
        const called = races.filter((r) => r.called !== false);
        const unc = races.filter((r) => r.called === false);
        return {
          D: notUp.D + called.filter((r) => r.wp === "D" || r.wp === "I").length,
          R: notUp.R + called.filter((r) => r.wp === "R").length,
          Dl: unc.filter((r) => r.wp !== "R" && r.wpct !== r.rpct).length,
          Rl: unc.filter((r) => r.wp === "R" && r.wpct !== r.rpct).length,
          tied: unc.filter((r) => r.wpct === r.rpct).length,
          unc: unc.length
        };
      };
      const sT = tally(data.senate.races, data.senate.not_up);
      const gT = tally(data.governors.races, data.governors.not_up);
      const rows = [
        { ch: "House", D: data.house.called.D, R: data.house.called.R, Dl: hDl, Unc: 0, Rl: hRl, tot: 435, mk: 218, mkl: "218 for majority", ct: `${hUnc.length} uncalled` },
        { ch: "Senate", D: sT.D, R: sT.R, Dl: sT.Dl, Unc: sT.tied, Rl: sT.Rl, tot: 100, mk: 51, mkl: "51 for majority", ct: `incl. ${data.senate.not_up.D} D, ${data.senate.not_up.R} R not up` },
        { ch: "Governors", D: gT.D, R: gT.R, Dl: gT.Dl, Unc: gT.tied, Rl: gT.Rl, tot: 50, mk: 26, mkl: "26 for majority", ct: `${gT.unc} uncalled` }
      ];

      rows.forEach((r) => {
        const row = H("div", { class: "row" }, bopEl);
        H(
          "div",
          { class: "bignums" },
          row,
          `<div>
             <div class="v D">${r.D}</div>
             <div class="l">Democrats${r.Dl ? ` · +${r.Dl} leading` : ""}</div>
           </div>
           <div class="mid">${r.ch}<div class="l">${r.ct}</div></div>
           <div class="r">
             <div class="v R">${r.R}</div>
             <div class="l">Republicans${r.Rl ? ` · +${r.Rl} leading` : ""}</div>
           </div>`
        );

        const bar = H(
          "div",
          {
            class: "bar",
            role: "img",
            "aria-label": `${r.ch}: Democrats ${r.D}, Republicans ${r.R}, ${r.tot - r.D - r.R} uncalled`
          },
          row
        );

        const segs = [
          [r.D, "background:var(--D)", "Democrats won", ""],
          [r.Dl, "", "Democrats leading", "hatchD"],
          [r.Unc, "", r.uncNote || "Too close to call", "unc"],
          [r.Rl, "", "Republicans leading", "hatchR"],
          [r.R, "background:var(--R)", "Republicans won", ""]
        ];

        segs.forEach(([n, st, lab, cls]) => {
          if (n <= 0) return;
          const sp = H("span", { style: `flex:${n} 0 0;${st}`, class: cls }, bar);
          bindTip(sp, () => `<div class="h">${r.ch}</div><div class="r"><span>${esc(lab)}</span><span class="w">${n}</span></div>`);
        });

        const pct = (100 * r.mk) / r.tot;
        H("div", { class: "mk", style: `inset-inline-start:${pct.toFixed(2)}%` }, bar);
        H("div", { class: "mkl", style: `inset-inline-start:${pct.toFixed(2)}%` }, bar, r.mkl);
      });

      if (lgEl) {
        lgEl.innerHTML = `
          <span><i style="background:var(--D)"></i>Democrat</span>
          <span><i class="hatchD"></i>Democrat leading</span>
          <span><i class="unc"></i>Uncalled / runoff</span>
          <span><i class="hatchR"></i>Republican leading</span>
          <span><i style="background:var(--R)"></i>Republican</span>
        `;
      }

      const allStatewide = [...data.senate.races, ...data.governors.races].filter((x) => x.swing !== null && x.swing !== undefined);
      const shiftedDem = allStatewide.filter((x) => x.swing > 0).length;

      if (statsEl) {
        const senFl = data.senate.races.filter((r) => r.flip && r.wp === "D");
        const senFlR = data.senate.races.filter((r) => r.flip && r.wp === "R");
        const govFl = data.governors.races.filter((r) => r.flip && r.wp === "D");
        const govFlR = data.governors.races.filter((r) => r.flip && r.wp === "R");
        const senUnc = data.senate.races.filter((r) => r.called === false).length;
        const signed = (n) => (n >= 0 ? `+${n}` : `${n}`);
        const items = [
          [fmtMargin(natVote.margin, true), `House two-party vote counted so far (2024 president: R+1.5)`],
          [signed(senFl.length - senFlR.length), `Senate seats gained by Democrats${senUnc ? `, ${senUnc} still uncalled` : ""}`],
          [`+${natVote.flips_projected}`, `House seats flipped so far; NBC projects ~${data.house.projection.D} D seats`],
          [signed(govFl.length - govFlR.length), `Governorships gained${govFl.length ? `: ${govFl.map((r) => r.st).join(", ")}` : ""}`],
          [`${shiftedDem}/${allStatewide.length}`, `Senate & governor races that shifted toward Democrats from 2024`]
        ];
        statsEl.innerHTML = items
          .map(([v, l]) => `<div class="stat"><div class="v">${esc(v)}</div><div class="l">${esc(l)}</div></div>`)
          .join("");
      }

      // Narrative paragraphs
      const senSw = data.senate.races.filter((r) => r.swing !== null && r.swing !== undefined);
      const govSw = data.governors.races.filter((r) => r.swing !== null && r.swing !== undefined);
      const avgSenSw = senSw.reduce((s, r) => s + r.swing, 0) / senSw.length;
      const avgGovSw = govSw.reduce((s, r) => s + r.swing, 0) / govSw.length;
      const txS = data.senate.races.find((r) => r.st === "TX"), ksS = data.senate.races.find((r) => r.st === "KS"), scS = data.senate.races.find((r) => r.st === "SC");
      const swingProse = document.getElementById("swing-prose");
      if (swingProse) {
        swingProse.innerHTML = `Compared with the 2024 presidential vote in the same state, Democratic Senate candidates ran an average of <b>${avgSenSw.toFixed(1)} points</b> ahead of Kamala Harris, and gubernatorial candidates ran <b>${avgGovSw.toFixed(1)} points</b> ahead. ${senSw.filter((r) => r.swing > 0).length} of ${senSw.length} Senate races with a comparable count and ${govSw.filter((r) => r.swing > 0).length} of ${govSw.length} governor races moved toward Democrats. In Texas, James Talarico turned a ${fmtSwing(txS.pres24)} Trump state into a ${fmtSwing(txS.margin)} Senate win, while Kansas (${fmtSwing(ksS.pres24)} to ${fmtSwing(ksS.margin)}) and South Carolina (${fmtSwing(scS.pres24)} to ${fmtSwing(scS.margin)}) flipped as well.`;
      }

      const totVotesM = ((natVote.D_votes + natVote.R_votes) / 1e6).toFixed(0);
      const houseProse = document.getElementById("house-prose");
      if (houseProse) {
        houseProse.innerHTML = `With ${totVotesM} million two-party House votes counted, Democrats lead the national House vote by <b>${natVote.margin.toFixed(1)} points</b>, a ${(natVote.margin - (pres24.US ?? -1.47)).toFixed(1)}-point swing from Donald Trump's 1.5-point popular-vote win in 2024. Democrats hold <b>236</b> called seats to Republicans' <b>146</b>, with 53 districts uncalled, and NBC's Decision Desk projects <b>258 Democratic seats</b> (CBS range: 251–268). Speaker Mike Johnson said Wednesday he will not stay on as Republican leader.`;
      }
    }
    renderHeroBOP();

    /* ----------------------------------------------------------------------
       1. Horizontal Arrow Swing Chart + Quadrant Scatterplot
       ---------------------------------------------------------------------- */
    function drawArrowSwing() {
      const box = document.getElementById("swing-arrow-chart");
      const titleEl = document.getElementById("swing-arrow-title");
      if (!box) return;
      box.innerHTML = "";

      const raw = state.arrowOffice === "senate" ? data.senate.races : data.governors.races;
      const rs = raw
        .filter((r) => r.pres24 !== undefined && r.margin !== null)
        .slice()
        .sort((a, b) => a.pres24 - b.pres24);

      const avg = rs.reduce((s, r) => s + r.swing, 0) / rs.length;
      if (titleEl) {
        titleEl.textContent = `${state.arrowOffice === "senate" ? "Senate" : "Governor"} races: 2026 margin vs. Trump's 2024 margin in the same state (average swing ${fmtSwing(avg)})`;
      }

      const W = box.clientWidth || 960;
      const narrow = W < 620;
      const lw = narrow ? 54 : 142;
      const rw = narrow ? 50 : 72;
      const rh = 23;
      const top = 48;
      const H0 = top + rs.length * rh + 10;

      const svg = S("svg", {
        width: W,
        height: H0,
        viewBox: `0 0 ${W} ${H0}`,
        role: "img",
        "aria-label": "Horizontal arrow chart of 2024-to-2026 swing by state"
      }, box);

      const lo = -60, hi = 50;
      const x = (v) => lw + ((Math.max(lo, Math.min(hi, v)) - lo) / (hi - lo)) * (W - lw - rw);

      for (let v = lo; v <= hi; v += 20) {
        S("line", { class: v === 0 ? "zero" : "gr", x1: x(v), x2: x(v), y1: top - 8, y2: H0 - 6 }, svg);
        if (!narrow || v % 40 === 0 || v === 0) {
          const t = S("text", { x: x(v), y: top - 14, "text-anchor": "middle", class: "ax-num" }, svg);
          t.textContent = v === 0 ? "Even" : (v > 0 ? "D+" : "R+") + Math.abs(v);
        }
      }

      const tR = S("text", { x: x(lo), y: 13, "text-anchor": "start", fill: "var(--R)", "font-weight": "600" }, svg);
      tR.textContent = narrow ? "← More R" : "← More Republican";
      const tD = S("text", { x: x(hi), y: 13, "text-anchor": "end", fill: "var(--D)", "font-weight": "600" }, svg);
      tD.textContent = narrow ? "More D →" : "More Democratic →";
      S("text", { x: W - 4, y: top - 14, "text-anchor": "end", class: "ax-num" }, svg).textContent = "Swing";

      const defs = S("defs", {}, svg);
      ["D", "R"].forEach((p) => {
        const m = S("marker", {
          id: `arrow-${p}`,
          viewBox: "0 0 10 10",
          refX: 8,
          refY: 5,
          markerWidth: 6,
          markerHeight: 6,
          orient: "auto-start-reverse"
        }, defs);
        S("path", { d: "M0,1 L9,5 L0,9 z", fill: `var(--${p})` }, m);
      });

      rs.forEach((r, i) => {
        const y = top + i * rh + rh / 2;
        const g = S("g", { style: "cursor:pointer" }, svg);
        S("rect", { x: 0, y: y - rh / 2, width: W, height: rh, fill: "transparent" }, g);

        const nm = S("text", {
          x: lw - 10,
          y: y + 4,
          "text-anchor": "end",
          class: r.flip ? "lblb" : "lbl"
        }, g);
        const stLabel = narrow ? r.st : STATE_NAMES[r.st] || r.name;
        nm.textContent = stLabel + (r.flip ? " ★" : "") + (r.called ? "" : " *");

        const dir = r.swing >= 0 ? "D" : "R";
        const x1 = x(r.pres24);
        const x2 = x(r.margin);
        const dist = Math.abs(x2 - x1);

        S("line", {
          x1,
          x2: x2 + (dist > 8 ? (dir === "D" ? -5 : 5) : 0),
          y1: y,
          y2: y,
          stroke: `var(--${dir})`,
          "stroke-width": 2,
          "marker-end": dist > 8 ? `url(#arrow-${dir})` : ""
        }, g);

        S("circle", { cx: x1, cy: y, r: 4.5, fill: "var(--bg)", stroke: "var(--mut)", "stroke-width": 1.5 }, g);
        S("circle", {
          cx: x2,
          cy: y,
          r: r.flip ? 5.6 : 4.8,
          fill: `var(--${r.margin >= 0 ? "D" : "R"})`,
          stroke: r.flip ? "var(--ink)" : "var(--bg)",
          "stroke-width": r.flip ? 1.8 : 1.8
        }, g);

        const sw = S("text", {
          x: W - 4,
          y: y + 4,
          "text-anchor": "end",
          "font-family": "var(--mono)",
          "font-size": "11.5",
          fill: `var(--${dir})`
        }, g);
        sw.textContent = (r.swing > 0 ? "+" : "") + r.swing.toFixed(1);

        bindTip(g, () => `
          <div class="h">${esc(r.name)}${r.flip ? " · ★ Flipped" : ""}${r.called ? "" : " · Uncalled"}</div>
          <div class="r"><span><i style="background:var(--${r.wp})"></i>${esc(r.win)}</span><span class="w">${r.wpct.toFixed(1)}%</span></div>
          <div class="r"><span><i style="background:var(--${r.rp === "I" ? "I" : r.rp})"></i>${esc(r.ru)}</span><span>${r.rpct !== null ? r.rpct.toFixed(1) + "%" : "n/a"}</span></div>
          <div class="m">2024 pres. ${fmtMargin(r.pres24, true)} → 2026 ${fmtMargin(r.margin, r.called)} · swing ${fmtSwing(r.swing)}</div>
        `);

        g.addEventListener("click", () => {
          selectState(r.st);
        });
      });
    }

    document.querySelectorAll("[data-arrow-office]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.arrowOffice = btn.dataset.arrowOffice;
        document.querySelectorAll("[data-arrow-office]").forEach((b) => {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        drawArrowSwing();
      });
    });

    function renderSwingScatter() {
      const scatterSvg = document.getElementById("swing-scatter-svg");
      const swingListEl = document.getElementById("swing-top-list");
      if (!scatterSvg || !swingListEl) return;

      const pts = [];
      if (state.scatterMode === "senate" || state.scatterMode === "both") {
        data.senate.races.forEach((r) => {
          if (r.pres24 !== undefined) pts.push({ ...r, office: "Sen.", x: r.pres24, y: r.margin });
        });
      }
      if (state.scatterMode === "governors" || state.scatterMode === "both") {
        data.governors.races.forEach((r) => {
          if (r.pres24 !== undefined) pts.push({ ...r, office: "Gov.", x: r.pres24, y: r.margin });
        });
      }

      const W = 560, Hh = 380, padL = 48, padR = 20, padT = 20, padB = 40;
      const xMin = -50, xMax = 35, yMin = -56, yMax = 52;
      const sx = (v) => padL + ((v - xMin) / (xMax - xMin)) * (W - padL - padR);
      const sy = (v) => padT + ((yMax - v) / (yMax - yMin)) * (Hh - padT - padB);

      const x0 = sx(0), y0 = sy(0);
      const sortedSwings = pts.map((p) => p.swing).sort((a, b) => a - b);
      const medSwing = sortedSwings[Math.floor(sortedSwings.length / 2)] || 16;
      const labelStates = new Set(["TX", "NC", "GA", "IA", "KS", "SC", "OH", "PA", "AL", "MS", "VT", "FL", "ME", "NJ", "NH", "NV"]);

      scatterSvg.innerHTML = `
        <rect x="${padL}" y="${padT}" width="${(x0 - padL).toFixed(1)}" height="${(y0 - padT).toFixed(1)}" fill="var(--dem-soft)" fill-opacity="0.65" />
        <text x="${padL + 8}" y="${padT + 15}" font-family="var(--mono)" font-size="9.5" font-weight="600" fill="var(--D)">TRUMP '24 → DEM '26 WINNER</text>

        ${[-40, -20, 0, 20].map((t) => `
          <line x1="${sx(t).toFixed(1)}" y1="${padT}" x2="${sx(t).toFixed(1)}" y2="${Hh - padB}" class="${t === 0 ? "zero" : "gr"}" />
          <text x="${sx(t).toFixed(1)}" y="${Hh - padB + 15}" text-anchor="middle" font-family="var(--mono)" font-size="10">${t === 0 ? "Even" : t > 0 ? `D+${t}` : `R+${Math.abs(t)}`}</text>
        `).join("")}

        ${[-40, -20, 0, 20, 40].map((t) => `
          <line x1="${padL}" y1="${sy(t).toFixed(1)}" x2="${W - padR}" y2="${sy(t).toFixed(1)}" class="${t === 0 ? "zero" : "gr"}" />
          <text x="${padL - 6}" y="${(sy(t) + 3.5).toFixed(1)}" text-anchor="end" font-family="var(--mono)" font-size="10">${t === 0 ? "Even" : t > 0 ? `D+${t}` : `R+${Math.abs(t)}`}</text>
        `).join("")}

        <line x1="${sx(-50).toFixed(1)}" y1="${sy(-50).toFixed(1)}" x2="${sx(35).toFixed(1)}" y2="${sy(35).toFixed(1)}" stroke="var(--mut)" stroke-width="1.2" stroke-dasharray="4 3" />
        <text x="${sx(22).toFixed(1)}" y="${(sy(22) + 14).toFixed(1)}" font-family="var(--mono)" font-size="9.5" fill="var(--mut)">Same as 2024</text>

        <line x1="${sx(-50).toFixed(1)}" y1="${sy(-50 + medSwing).toFixed(1)}" x2="${sx(Math.min(35, 52 - medSwing)).toFixed(1)}" y2="${sy(Math.min(35 + medSwing, 52)).toFixed(1)}" stroke="var(--D)" stroke-width="1.2" stroke-dasharray="2 2" />
        <text x="${sx(-46).toFixed(1)}" y="${(sy(-46 + medSwing) - 6).toFixed(1)}" font-family="var(--mono)" font-size="9.5" fill="var(--D)">Median (${fmtSwing(medSwing)})</text>

        <text x="${(padL + W - padR) / 2}" y="${Hh - 5}" text-anchor="middle" font-family="var(--sans)" font-size="11.5" fill="var(--ink2)">2024 presidential margin (← Trump · Harris →)</text>

        ${pts.map((p, idx) => {
          const cx = sx(p.x), cy = sy(p.y);
          const fill = !p.called ? "var(--N)" : p.y >= 0 ? "var(--D)" : "var(--R)";
          const showLbl = labelStates.has(p.st) && (state.scatterMode !== "both" || p.office === "Sen.");
          return `
            <g class="scatter-pt" data-idx="${idx}" style="cursor:pointer">
              ${p.flip ? `<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="7.2" fill="var(--ink)" />` : ""}
              <circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${p.flip ? 5.6 : 4.8}" fill="${fill}" stroke="var(--bg)" stroke-width="1.5" />
              ${showLbl ? `<text x="${(cx + 8).toFixed(1)}" y="${(cy + 3.5).toFixed(1)}" font-family="var(--mono)" font-size="9.5" font-weight="600" fill="var(--ink)">${p.st}</text>` : ""}
            </g>
          `;
        }).join("")}
      `;

      scatterSvg.querySelectorAll(".scatter-pt").forEach((g) => {
        const p = pts[Number(g.dataset.idx)];
        bindTip(g, () => `
          <div class="h">${esc(p.name)} · ${p.office}${p.flip ? " · ★ Flipped" : ""}</div>
          <div class="r"><span>2024 president</span><span class="w">${fmtMargin(p.x, true)}</span></div>
          <div class="r"><span>2026 ${p.office}</span><span class="w">${fmtMargin(p.y, p.called)}</span></div>
          <div class="m">Shift ${fmtSwing(p.swing)} · ${esc(p.win)} vs. ${esc(p.ru)}</div>
        `);
        g.addEventListener("click", () => {
          selectState(p.st);
          document.getElementById("map").scrollIntoView({ behavior: "smooth", block: "nearest" });
        });
      });

      const topSwings = pts.slice().sort((a, b) => b.swing - a.swing).slice(0, 14);
      swingListEl.innerHTML = `
        <table class="compact-table">
          <thead><tr><th>Race</th><th>State</th><th class="num">2026</th><th class="num">Shift</th></tr></thead>
          <tbody>
            ${topSwings.map((p) => `
              <tr>
                <td style="font-family:var(--mono);font-size:12px;color:var(--mut)">${p.office}</td>
                <td><b>${esc(p.name)}</b>${p.flip ? ` <span style="color:var(--D)">${ICONS.star}</span>` : ""}</td>
                <td class="num">${fmtMargin(p.y, p.called)}</td>
                <td class="num" style="color:var(--D);font-weight:600">${fmtSwing(p.swing)}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
    }

    document.querySelectorAll("[data-scatter-mode]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.scatterMode = btn.dataset.scatterMode;
        document.querySelectorAll("[data-scatter-mode]").forEach((b) => {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        renderSwingScatter();
      });
    });

    /* ----------------------------------------------------------------------
       2. All 435 House Districts + State House Bubble Scatter + Flips Table
       ---------------------------------------------------------------------- */
    function districtShadeVar(d) {
      const p = d.lead.p === "D" || d.lead.p === "R" ? d.lead.p : "I";
      if (p === "I") return "var(--I)";
      if (d.same || d.uncontested) return `var(--${p}3)`;
      const a = Math.abs(d.margin);
      return `var(--${p}${a < 3 ? "1" : a < 10 ? "2" : a < 20 ? "3" : "4"})`;
    }

    function buildHouse435Grid() {
      const g = document.getElementById("hgrid");
      const lg = document.getElementById("hgrid-legend");
      if (!g) return;
      g.innerHTML = "";

      const bySt = {};
      DISTRICTS.forEach((d) => {
        (bySt[d.st] = bySt[d.st] || []).push(d);
      });

      Object.keys(bySt)
        .sort((a, b) => STATE_NAMES[a].localeCompare(STATE_NAMES[b]))
        .forEach((st) => {
          const ds = bySt[st].sort((a, b) => a.n - b.n);
          const dn = ds.filter((d) => d.called && d.lead.p === "D").length;
          const rn = ds.filter((d) => d.called && d.lead.p === "R").length;
          const uncN = ds.length - dn - rn;

          const wrap = H("div", { class: "st-group" }, g);
          H("div", { class: "nm" }, wrap, `${esc(STATE_NAMES[st])}<span>${dn}D ${rn}R${uncN ? ` ${uncN}?` : ""}</span>`);
          const sq = H("div", { class: "sq" }, wrap);

          ds.forEach((d) => {
            const c = districtShadeVar(d);
            const cell = H("div", {
              class: `d${d.flip ? " flip" : ""}${d.called ? "" : " u"}`,
              tabindex: "0",
              "aria-label": `${d.id}: ${d.lead.n} (${d.lead.p})`,
              style: `--c:${c};background:${d.called ? c : `color-mix(in srgb, ${c} 44%, var(--bg))`}`
            }, sq);
            d.el = cell;

            bindTip(cell, () => {
              const rows = d.c.slice(0, 3).map((cand) => `
                <div class="r">
                  <span><i style="background:var(--${cand.p})"></i>${esc(cand.n)}${cand.inc ? " (inc.)" : ""}</span>
                  <span class="${cand.w ? "w" : ""}">${cand.pct.toFixed(1)}%${cand.w ? " ✓" : ""}</span>
                </div>
              `).join("");
              return `
                <div class="h">${esc(d.id)}${d.flip ? ` · ★ Flipped to ${d.lead.p}` : ""}</div>
                ${rows}
                <div class="m">${d.called ? "Projected winner" : "Uncalled"} · ${d.uncontested ? "Uncontested" : `${d.pin}% in`}${!d.same && !d.uncontested ? ` · ${fmtMargin(d.margin, d.called)}` : ""}</div>
              `;
            });
          });
        });

      if (lg) {
        lg.innerHTML = `
          <span>${["D4", "D3", "D2", "D1"].map((k) => `<i style="background:var(--${k});margin-inline-end:2px"></i>`).join("")} Democrat 20+, 10–20, 3–10, &lt;3</span>
          <span>${["R1", "R2", "R3", "R4"].map((k) => `<i style="background:var(--${k});margin-inline-end:2px"></i>`).join("")} Republican &lt;3 … 20+</span>
          <span><i class="flip-swatch"></i>Flipped</span>
          <span><i style="box-shadow:inset 0 0 0 1.5px var(--D3);background:color-mix(in srgb,var(--D3) 44%,var(--bg))"></i>Uncalled</span>
        `;
      }
    }

    /* Hex cartogram of all 435 districts */
    const HEX = data.house.hex || {};
    const CD24 = data.house.pres2024_cd || {};
    state.hexMode = "swing";
    function hexComparable(d) {
      return CD24[d.id] && !d.same && !d.uncontested && d.st !== "AK" &&
        d.c.some((c) => c.p === "D") && d.c.some((c) => c.p === "R");
    }
    function hexFill(d) {
      if (state.hexMode === "margin") return districtShadeVar(d);
      if (!hexComparable(d)) return "var(--grid)";
      const sw = d.margin - CD24[d.id][0];
      if (sw < 0) return "var(--R2)";
      return `var(--D${sw < 5 ? "1" : sw < 15 ? "2" : sw < 25 ? "3" : "4"})`;
    }
    function drawHexMap() {
      const box = document.getElementById("hexmap");
      if (!box || !Object.keys(HEX).length) return;
      box.innerHTML = "";
      const ent = Object.entries(HEX).filter(([k]) => distById.has(k));
      const cs = ent.map(([, v]) => v[0] + 0.5 * (v[1] & 1));
      const rs = ent.map(([, v]) => v[1]);
      const c0 = Math.min(...cs), c1 = Math.max(...cs), r0 = Math.min(...rs), r1 = Math.max(...rs);
      const W = Math.min(box.clientWidth || 900, 1120);
      const sq3 = Math.sqrt(3);
      const sz = (W - 8) / ((c1 - c0 + 1) * sq3);
      const Hh = Math.ceil((r1 - r0) * 1.5 * sz + 2 * sz + 6);
      const svg = S("svg", { width: W, height: Hh, viewBox: `0 0 ${W} ${Hh}`, role: "img",
        "aria-label": "Hexagon map of all 435 House districts colored by " + (state.hexMode === "swing" ? "swing from 2024" : "2026 margin") }, box);
      const cx = (v) => 4 + ((v[0] + 0.5 * (v[1] & 1)) - c0) * sq3 * sz + sq3 * sz / 2;
      const cy = (v) => (v[1] - r0) * 1.5 * sz + sz + 2;
      const corner = (x, y, i, s) => { const a = Math.PI / 180 * (60 * i - 90); return [x + s * Math.cos(a), y + s * Math.sin(a)]; };
      const at = {};
      ent.forEach(([k, v]) => { at[v[0] + "," + v[1]] = distById.get(k).st; });
      const nbKey = (v, i) => {
        const D = (v[1] & 1) ? [[1, -1], [1, 0], [1, 1], [0, 1], [-1, 0], [0, -1]] : [[0, -1], [1, 0], [0, 1], [-1, 1], [-1, 0], [-1, -1]];
        return (v[0] + D[i][0]) + "," + (v[1] + D[i][1]);
      };
      const gH = S("g", {}, svg), gF = S("g", { "pointer-events": "none" }, svg), gEh = S("g", { "pointer-events": "none" }, svg),
        gE = S("g", { "pointer-events": "none" }, svg), gL = S("g", { "pointer-events": "none" }, svg);
      const bw = Math.max(1.8, sz * 0.17);
      const defs = S("defs", {}, svg);
      const pat = S("pattern", { id: "hex-flip-stripes", patternUnits: "userSpaceOnUse", width: Math.max(4, sz * 0.42), height: Math.max(4, sz * 0.42), patternTransform: "rotate(45)" }, defs);
      S("rect", { x: 0, y: 0, width: Math.max(1.4, sz * 0.15), height: Math.max(4, sz * 0.42), style: "fill:var(--bg);fill-opacity:0.88" }, pat);
      ent.forEach(([k, v]) => {
        const d = distById.get(k), x = cx(v), y = cy(v);
        const pts = [0, 1, 2, 3, 4, 5].map((i) => corner(x, y, i, sz * 0.97).join(",")).join(" ");
        const fill = hexFill(d);
        const dim = state.selectedSt && state.selectedSt !== d.st;
        const h = S("polygon", { points: pts, "data-st": d.st, style: `fill:${d.called ? fill : `color-mix(in srgb, ${fill} 55%, var(--bg))`};stroke:var(--bg);stroke-width:0.6;cursor:pointer;opacity:${dim ? 0.22 : 1}`, tabindex: "0", "aria-label": d.id }, gH);
        h.addEventListener("click", () => selectState(state.selectedSt === d.st ? null : d.st));
        if (d.flip) S("polygon", { points: [0, 1, 2, 3, 4, 5].map((i) => corner(x, y, i, sz * 0.97).join(",")).join(" "), fill: "url(#hex-flip-stripes)", opacity: dim ? 0.22 : 1 }, gF);
        for (let i = 0; i < 6; i++) {
          if (at[nbKey(v, i)] === d.st) continue;
          const a = corner(x, y, i, sz), b = corner(x, y, (i + 1) % 6, sz);
          S("line", { x1: a[0], y1: a[1], x2: b[0], y2: b[1], style: `stroke:var(--bg);stroke-width:${bw + 2.6};stroke-linecap:round` }, gEh);
          S("line", { x1: a[0], y1: a[1], x2: b[0], y2: b[1], style: `stroke:var(--ink);stroke-width:${bw};stroke-linecap:round` }, gE);
        }
        bindTip(h, () => {
          const rows = d.c.slice(0, 2).map((c) => `<div class="r"><span><i style="background:var(--${c.p})"></i>${esc(c.n)}${c.inc ? " (inc.)" : ""}</span><span class="${c.w ? "w" : ""}">${c.pct.toFixed(1)}%</span></div>`).join("");
          const b = CD24[d.id];
          const cmp = hexComparable(d)
            ? `Trump-Harris 2024 ${fmtSwing(b[0])}${b.length > 1 ? ` (old lines ${fmtSwing(b[1])})` : ""} → 2026 ${fmtSwing(d.margin)} · swing ${fmtSwing(d.margin - b[0])}`
            : "No 2024 comparison";
          return `<div class="h">${esc(d.id)}${d.flip ? " · flipped" : ""}${d.called ? "" : " · uncalled"}</div>${rows}<div class="m">${cmp}</div>`;
        });
      });
      const byS = {};
      ent.forEach(([k, v]) => { const st = distById.get(k).st; (byS[st] = byS[st] || []).push([cx(v), cy(v)]); });
      Object.entries(byS).forEach(([st, a]) => {
        if (sz < 10 && a.length < 4) return;
        const x = a.reduce((t, p) => t + p[0], 0) / a.length, y = a.reduce((t, p) => t + p[1], 0) / a.length;
        const t = S("text", { x, y: y + 4, "text-anchor": "middle", style: `font:600 ${sz < 10 ? 8.5 : Math.min(12, sz * 0.9)}px var(--sans);fill:var(--ink);stroke:var(--bg);stroke-width:3;paint-order:stroke;stroke-linejoin:round` }, gL);
        t.textContent = st;
      });
      const title = document.getElementById("hexmap-title");
      if (title) title.textContent = state.hexMode === "swing" ? "House districts: swing from 2024" : "House districts: 2026 margin";
      const lg = document.getElementById("hexmap-legend");
      const flipKey = `<span><i class="flip-swatch"></i>Flipped</span>`;
      if (lg) lg.innerHTML = state.hexMode === "swing"
        ? `<span><i style="background:var(--R2)"></i>Moved right</span><span><i style="background:var(--D1)"></i>D +0–5</span><span><i style="background:var(--D2)"></i>+5–15</span><span><i style="background:var(--D3)"></i>+15–25</span><span><i style="background:var(--D4)"></i>+25 or more</span><span><i style="background:var(--grid)"></i>No comparison</span>${flipKey}`
        : `<span>${["D4", "D3", "D2", "D1"].map((k) => `<i style="background:var(--${k});margin-inline-end:2px"></i>`).join("")} Democrat 20+ … &lt;3</span><span>${["R1", "R2", "R3", "R4"].map((k) => `<i style="background:var(--${k});margin-inline-end:2px"></i>`).join("")} Republican &lt;3 … 20+</span>${flipKey}<span>Faded: uncalled</span>`;
    }
    document.querySelectorAll("#hexmap-mode .chip").forEach((b) => {
      b.addEventListener("click", () => {
        state.hexMode = b.dataset.hm;
        document.querySelectorAll("#hexmap-mode .chip").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
        drawHexMap();
      });
    });

    /* ----------------------------------------------------------------------
       Dot-density map: one dot per N votes (scripts/build_dots.py → dots/)
       ---------------------------------------------------------------------- */
    const DOT = { meta: null, bins: {}, layer: "house", scale: 1000, raf: 0, loading: null, paths: null, played: {},
      user: null /* {z, ox, oy}: wheel/pinch zoom on top of the base view */, base: null, cur: null };
    const DOT_MAX_Z = 400;
    const DOT_LAYER_NAME = { house: "House", senate: "Senate", governor: "Governor" };
    function dotBase() {
      const s = document.querySelector('script[src*="app.js"]');
      return s ? s.src.replace(/app\.js.*$/, "dots/") : "dots/";
    }
    function loadDotMeta() {
      if (!DOT.loading) DOT.loading = fetch(dotBase() + "meta.json", { cache: "no-cache" }).then((r) => {
        if (!r.ok) throw new Error("meta.json " + r.status);
        return r.json();
      }).then((m) => {
        DOT.meta = m;
        DOT.paths = {};
        Object.entries(m.outline).forEach(([st, d]) => { DOT.paths[st] = new Path2D(d); });
        return m;
      }).catch((e) => { DOT.loading = null; throw e; });      // let the next attempt retry
      return DOT.loading;
    }
    function loadDotBin(layer, scale) {
      const k = layer + "-" + scale;
      const ver = encodeURIComponent((DOT.meta && DOT.meta.as_of) || "");   // pairs each file with this meta
      if (!DOT.bins[k]) DOT.bins[k] = fetch(dotBase() + k + ".bin?v=" + ver).then((r) => {
        if (!r.ok) throw new Error(k + ".bin " + r.status);
        return r.arrayBuffer();
      }).then((buf) => {
        const n = Math.floor(buf.byteLength / 9), q = DOT.meta.quant || 4096;
        const xy = new Uint32Array(buf, 0, n * 2);
        const ps = new Uint8Array(buf, n * 8, n);
        const x = new Float32Array(n), y = new Float32Array(n), p = new Uint8Array(n), st = new Uint8Array(n);
        for (let i = 0; i < n; i++) { x[i] = xy[2 * i] / q; y[i] = xy[2 * i + 1] / q; p[i] = ps[i] >> 6; st[i] = ps[i] & 63; }
        return { n, x, y, p, st };
      }).catch((e) => { delete DOT.bins[k]; throw e; });
      return DOT.bins[k];
    }
    const fmtM = (v) => v >= 1e6 ? (v / 1e6).toFixed(1) + "M" : v >= 1e3 ? Math.round(v / 1e3) + "K" : String(v);
    function drawDotMap(animate) {
      const box = document.getElementById("dotmap");
      if (!box || !DOT.meta) return;
      const layer = DOT.layer, scale = DOT.scale, m = DOT.meta, L = m.layers[layer];
      const sel = state.selectedSt && m.bbox && m.bbox[state.selectedSt] ? state.selectedSt : null;
      DOT.drawnSel = sel;
      const back = document.getElementById("dotmap-back");
      if (back) back.hidden = !sel;
      const cityBtn = document.getElementById("dotmap-cities");
      if (cityBtn) { cityBtn.hidden = !(sel || (DOT.user && DOT.user.z > 1.02)); cityBtn.setAttribute("aria-pressed", String(DOT.showCities !== false)); }
      loadDotBin(layer, scale).then((d) => {
        if (layer !== DOT.layer || scale !== DOT.scale || sel !== DOT.drawnSel) return;
        cancelAnimationFrame(DOT.raf);
        const cv = box.querySelector("canvas");
        const W = Math.max(280, box.clientWidth || 900);
        const [FW, FH] = m.frame;
        // view: frame coords -> CSS px. Whole country fits the width; a selected state fills it.
        let k, ox = 0, oy = 0, H;
        if (!sel) { k = W / FW; H = Math.round(FH * k); }
        else {
          const [x0, y0, x1, y1] = m.bbox[sel];
          const pad = Math.max(x1 - x0, y1 - y0) * 0.06 + 2;
          const bw = x1 - x0 + 2 * pad, bh = y1 - y0 + 2 * pad;
          const maxH = Math.max(320, Math.min(window.innerHeight * 0.8, W * 0.9));
          k = Math.min(W / bw, maxH / bh, 60);
          H = Math.max(260, Math.round(Math.min(maxH, bh * k)));
          ox = (W - (x1 - x0) * k) / 2 - x0 * k;
          oy = (H - (y1 - y0) * k) / 2 - y0 * k;
        }
        // the base view (whole country or one state) plus whatever the viewer has zoomed/panned
        const baseKey = `${sel || "US"}:${W}`;
        if (DOT.base !== baseKey) { DOT.base = baseKey; DOT.user = null; }
        const extent = sel ? m.bbox[sel] : [0, 0, FW, FH];
        if (!DOT.user) DOT.user = { z: 1, ox, oy };
        else {
          // keep the map under the viewport: the visible center must stay inside the base extent
          const kz = k * DOT.user.z;
          DOT.user.ox = Math.min(W / 2 - extent[0] * kz, Math.max(W / 2 - extent[2] * kz, DOT.user.ox));
          DOT.user.oy = Math.min(H / 2 - extent[1] * kz, Math.max(H / 2 - extent[3] * kz, DOT.user.oy));
        }
        k *= DOT.user.z; ox = DOT.user.ox; oy = DOT.user.oy;
        DOT.view = { k, ox, oy, W, H };
        const zoomed = DOT.user.z > 1.02;
        const zb = document.getElementById("dotmap-zoom");
        if (zb) zb.hidden = !zoomed;
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
        cv.style.width = W + "px"; cv.style.height = H + "px";
        const ctx = cv.getContext("2d");
        const col = ["--D", "--R", "--I"].map(cssColor);
        const cBg = cssColor("--bg"), cAlt = cssColor("--alt"), cLine = cssColor("--mut"), cGrid = cssColor("--line"), cInk = cssColor("--ink");
        const has = new Set(Object.keys(L.by_state));
        const selIdx = sel ? m.states.indexOf(sel) : -1;
        // zoomed in, show only the selected state's own map (lower 48, or the Alaska / Hawaii inset)
        const grp = (st) => (st === "AK" || st === "HI" ? st : "L48");
        const shown = (st) => !sel || grp(st) === grp(sel);
        const hideIdx = new Uint8Array(m.states.length);
        m.states.forEach((st, i) => { hideIdx[i] = shown(st) ? 0 : 1; });
        // dot size in CSS px: area grows with votes per dot; zoomed-in views get bigger dots
        // small and translucent, so dense mixed areas blend toward purple instead of one side painting over the other
        const base = scale === 1000 ? 0.42 : scale === 10000 ? 1.3 : 3.0;
        const r = (sel || zoomed) ? base * Math.min(scale === 1000 ? 3.2 : 2.2, Math.max(1, Math.sqrt(k) * 0.75))
                                  : base * Math.max(scale === 1000 ? 0.42 : 0.6, Math.min(1.35, k));
        const alpha = scale === 1000 ? ((sel || zoomed) ? 0.55 : 0.62) : scale === 10000 ? 0.7 : 0.8;
        const toView = () => ctx.setTransform(dpr * k, 0, 0, dpr * k, dpr * ox, dpr * oy);
        function ground() {
          ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
          ctx.clearRect(0, 0, W, H);
          toView();
          Object.entries(DOT.paths).forEach(([st, p]) => {
            if (!shown(st)) return;
            ctx.fillStyle = has.has(st) ? cAlt : cBg;
            ctx.globalAlpha = sel && sel !== st ? 0.55 : 1;
            ctx.fill(p);
          });
          ctx.globalAlpha = 1;
        }
        function outlines() {
          toView();
          ctx.lineJoin = "round";
          Object.entries(DOT.paths).forEach(([st, p]) => {
            if (!shown(st)) return;
            ctx.globalAlpha = sel && sel !== st ? 0.5 : 0.9;
            ctx.strokeStyle = has.has(st) ? cLine : cGrid;
            ctx.lineWidth = (sel === st ? 1.8 : sel ? 1 : 0.6) / k;
            ctx.stroke(p);
          });
          ctx.globalAlpha = 1;
        }
        // dots are pre-shuffled; draw them in that order so neither party paints over the other
        function dots(i0, i1) {
          ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
          const sq = scale === 1000, a = alpha;
          let lastP = -1, lastA = -1;
          for (let i = i0; i < i1; i++) {
            const x = d.x[i] * k + ox, y = d.y[i] * k + oy;
            if (x < -4 || y < -4 || x > W + 4 || y > H + 4 || hideIdx[d.st[i]]) continue;
            const pi = d.p[i], al = selIdx >= 0 && d.st[i] !== selIdx ? 0.12 : a;
            if (pi !== lastP) { ctx.fillStyle = col[pi]; lastP = pi; }
            if (al !== lastA) { ctx.globalAlpha = al; lastA = al; }
            if (sq) ctx.fillRect(x - r, y - r, 2 * r, 2 * r);
            else { ctx.beginPath(); ctx.arc(x, y, r, 0, 6.2832); ctx.fill(); }
          }
          ctx.globalAlpha = 1;
        }
        // city labels for the selected state (NBC's picks): biggest first, skip any that would collide
        function cities() {
          if (DOT.showCities === false || !(sel || zoomed)) return;
          const list = [];
          const nbc = new Set();
          if (sel && m.cities && m.cities[sel]) m.cities[sel].forEach((c) => { list.push(c); nbc.add(c[0]); });
          // Census places: label when the place has enough people for this zoom level (k is px per frame unit)
          const need = Math.max(15000, 2.2e6 / k);
          (m.places || []).forEach(([name, fx, fy, people, st]) => {
            if (people < need || nbc.has(name)) return;
            const x = fx * k + ox, y = fy * k + oy;
            if (x < -40 || y < -20 || x > W + 40 || y > H + 20) return;
            if (sel && !shown(st)) return;
            list.push([name, fx, fy, people >= 1e6 ? 1 : 2, "R"]);
          });
          if (!list.length) return;
          ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
          const ff = getComputedStyle(document.body).fontFamily;
          const boxes = [];
          list.forEach(([name, fx, fy, tier, pos]) => {
            const x = fx * k + ox, y = fy * k + oy;
            if (x < -40 || y < -20 || x > W + 40 || y > H + 20) return;
            const fs = W < 520 ? (tier === 0 ? 12 : 11) : (tier === 0 ? 14 : tier === 1 ? 13 : 12);
            ctx.font = `${tier === 0 ? 700 : 600} ${fs}px ${ff}`;
            const tw = ctx.measureText(name).width, g = 7;
            let tx = x + g, ty = y, align = "left", base = "middle";
            if (pos === "L") { tx = x - g; align = "right"; }
            else if (pos === "T") { tx = x; ty = y - g; align = "center"; base = "bottom"; }
            else if (pos === "B") { tx = x; ty = y + g; align = "center"; base = "top"; }
            const bx0 = align === "left" ? tx : align === "right" ? tx - tw : tx - tw / 2;
            const by0 = base === "middle" ? ty - fs / 2 : base === "bottom" ? ty - fs : ty;
            const bb = [bx0 - 3, by0 - 2, bx0 + tw + 3, by0 + fs + 2];
            if (bb[0] < 2 || bb[2] > W - 2 || bb[1] < 2 || bb[3] > H - 2) return;
            if (boxes.some((o) => !(bb[2] < o[0] || bb[0] > o[2] || bb[3] < o[1] || bb[1] > o[3]))) return;
            boxes.push(bb, [x - 4, y - 4, x + 4, y + 4]);
            ctx.beginPath(); ctx.arc(x, y, tier === 0 ? 3.6 : 3, 0, 6.2832);
            ctx.fillStyle = cBg; ctx.fill(); ctx.lineWidth = 1.6; ctx.strokeStyle = cInk; ctx.stroke();
            ctx.textAlign = align; ctx.textBaseline = base;
            ctx.lineJoin = "round"; ctx.lineWidth = 4; ctx.strokeStyle = cBg; ctx.strokeText(name, tx, ty);
            ctx.fillStyle = cInk; ctx.fillText(name, tx, ty);
          });
        }
        DOT.cur = d;
        ground(); dots(0, d.n); outlines(); cities();
        // hit-testing for tooltip / click
        const tipFor = (st) => {
          const v = L.by_state[st];
          if (!v) return `<div class="h">${esc(STATE_NAMES[st])}</div><div class="m">No ${DOT_LAYER_NAME[layer]} race in 2026</div>`;
          const t = v[0] + v[1] + v[2];
          const row = (pi, lab) => v[pi] ? `<div class="r"><span><i style="background:var(--${["D", "R", "I"][pi]})"></i>${lab}</span><span>${v[pi].toLocaleString()} · ${(100 * v[pi] / t).toFixed(1)}%</span></div>` : "";
          return `<div class="h">${esc(STATE_NAMES[st])} · ${DOT_LAYER_NAME[layer]}</div>${row(0, "Democrats")}${row(1, "Republicans")}${row(2, "Other")}<div class="m">≈ ${Math.round(t / scale).toLocaleString()} dots · click to open</div>`;
        };
        // national view: hover for totals, click to pick a state. Inside a state or zoomed in: a grab
        // hand, drag to pan, and no hover card or click-to-leave (Esc / the chips do that), so the
        // gestures never fight each other
        const explore = !sel && !zoomed;
        cv.style.cursor = explore ? "default" : "grab";
        cv.style.touchAction = explore ? "pan-y" : "none";
        cv.onmousemove = (ev) => {
          if (!explore || DOT.dragging) { hideTip(); return; }
          const st = dotStateAt(ev, cv);
          if (!st) { hideTip(); cv.style.cursor = "default"; return; }
          cv.style.cursor = "pointer";
          showTip(tipFor(st), ev);
        };
        cv.onmouseleave = hideTip;
        cv.onclick = (ev) => {
          if (DOT.dragged) { DOT.dragged = false; return; }
          if (zoomed) return;
          const st = dotStateAt(ev, cv);
          hideTip();
          if (explore) { if (st) selectState(st); }
          else if (st && st !== state.selectedSt) selectState(st);
        };
        // legend + title
        const dd = L.dots[String(scale)];
        const lg = document.getElementById("dotmap-legend");
        const v = sel ? (L.by_state[sel] || [0, 0, 0]) : L.votes;
        const nd = sel ? Math.round((v[0] + v[1] + v[2]) / scale) : dd.n;
        const tail = sel ? (L.by_state[sel] ? `≈ ${nd.toLocaleString()} dots in ${esc(STATE_NAMES[sel])}` : `No ${DOT_LAYER_NAME[layer]} race in ${esc(STATE_NAMES[sel])}`)
          : `${dd.n.toLocaleString()} dots · ${has.size} ${has.size === 50 ? "states" : "states with a race"} · click a state · ${navigator.platform && /Mac/.test(navigator.platform) ? "⌘" : "Ctrl"}+scroll, pinch or double-click to zoom`;
        if (lg) lg.innerHTML = `<span><i style="background:var(--D)"></i>Democrat ${fmtM(v[0])}</span><span><i style="background:var(--R)"></i>Republican ${fmtM(v[1])}</span>${v[2] ? `<span><i style="background:var(--I)"></i>Other ${fmtM(v[2])}</span>` : ""}<span style="color:var(--mut)">${tail}</span>`;
        const ti = document.getElementById("dotmap-title");
        if (ti) ti.textContent = sel ? `Every ${DOT_LAYER_NAME[layer]} vote in ${STATE_NAMES[sel]}, as dots` : `Every ${DOT_LAYER_NAME[layer]} vote, as dots`;
        const asof = document.getElementById("dotmap-asof");
        if (asof && m.as_of) {
          const dt = new Date(m.as_of);
          if (isNaN(dt)) asof.textContent = m.as_of;
          else {
            const pt = Object.fromEntries(new Intl.DateTimeFormat("en-US", { timeZone: "America/Los_Angeles", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).formatToParts(dt).map((x) => [x.type, x.value]));
            asof.textContent = `as of ${pt.month}. ${pt.day}, ${pt.hour}:${pt.minute} ${pt.dayPeriod === "PM" ? "p.m." : "a.m."} PT`;
          }
        }
      }).catch((e) => {
        const lg = document.getElementById("dotmap-legend");
        if (lg) lg.innerHTML = `<span style="color:var(--mut)">The dot data didn't load (${esc(String(e.message || e))}). Click a race or dot size to try again.</span>`;
      });
    }
    // canvas can't parse light-dark()/var(); resolve through a probe element
    function cssColor(v) {
      let pr = document.getElementById("dot-color-probe");
      if (!pr) { pr = document.createElement("span"); pr.id = "dot-color-probe"; pr.style.display = "none"; document.getElementById("dotmap").appendChild(pr); }
      pr.style.color = `var(${v})`;
      return getComputedStyle(pr).color;
    }
    function dotStateAt(ev, cv) {
      if (!DOT.paths || !DOT.view) return null;
      const b = cv.getBoundingClientRect(), V = DOT.view;
      const x = (ev.clientX - b.left - V.ox) / V.k, y = (ev.clientY - b.top - V.oy) / V.k;
      const ctx = cv.getContext("2d");
      ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
      let hit = null;
      const g = (st) => (st === "AK" || st === "HI" ? st : "L48"), sel = DOT.drawnSel;
      for (const [st, p] of Object.entries(DOT.paths)) { if ((!sel || g(st) === g(sel)) && ctx.isPointInPath(p, x, y)) { hit = st; break; } }
      ctx.restore();
      return hit;
    }
    function setDotChips() {
      document.querySelectorAll("#dotmap-layer .chip").forEach((x) => x.setAttribute("aria-pressed", String(x.dataset.dl === DOT.layer)));
      document.querySelectorAll("#dotmap-scale .chip").forEach((x) => x.setAttribute("aria-pressed", String(+x.dataset.ds === DOT.scale)));
    }
    document.querySelectorAll("#dotmap-layer .chip").forEach((b) => b.addEventListener("click", () => { DOT.layer = b.dataset.dl; setDotChips(); drawDotMap(true); }));
    document.querySelectorAll("#dotmap-scale .chip").forEach((b) => b.addEventListener("click", () => { DOT.scale = +b.dataset.ds; setDotChips(); drawDotMap(true); }));
    const dotBack = document.getElementById("dotmap-back");
    if (dotBack) dotBack.addEventListener("click", () => selectState(null));
    (function dotZoomControls() {
      const box = document.getElementById("dotmap");
      if (!box) return;
      const cv = box.querySelector("canvas");
      let raf = 0;
      const redraw = () => { if (!raf) raf = requestAnimationFrame(() => { raf = 0; drawDotMap(false); }); };
      function zoomAt(f, mx, my) {
        const u = DOT.user; if (!u || !DOT.view) return;
        const z = Math.min(DOT_MAX_Z, Math.max(1, u.z * f)); f = z / u.z;
        if (f === 1) return;
        u.z = z; u.ox = mx - (mx - u.ox) * f; u.oy = my - (my - u.oy) * f;
        if (z === 1) DOT.user = null;                   // back to the base view exactly
        redraw();
      }
      cv.addEventListener("wheel", (ev) => {
        if (!DOT.view) return;
        const inside = DOT.drawnSel || (DOT.user && DOT.user.z > 1.02);
        if (!inside && !ev.ctrlKey && !ev.metaKey) return;      // let the page scroll past the national map
        ev.preventDefault();
        const b = cv.getBoundingClientRect();
        const f = Math.exp(-(ev.deltaMode === 1 ? ev.deltaY * 16 : ev.deltaY) * 0.0022);
        zoomAt(f, ev.clientX - b.left, ev.clientY - b.top);
      }, { passive: false });
      cv.addEventListener("dblclick", (ev) => {
        ev.preventDefault();
        const b = cv.getBoundingClientRect();
        zoomAt(2, ev.clientX - b.left, ev.clientY - b.top);
      });
      // drag to pan, pinch to zoom (pointer events)
      const pts = new Map(); let last = null, pinch = null;
      cv.addEventListener("pointerdown", (ev) => {
        pts.set(ev.pointerId, [ev.clientX, ev.clientY]); cv.setPointerCapture(ev.pointerId); last = [ev.clientX, ev.clientY]; DOT.moved = 0; pinch = null;
        if (DOT.drawnSel || (DOT.user && DOT.user.z > 1.02)) { DOT.dragging = true; cv.style.cursor = "grabbing"; hideTip(); }
      });
      cv.addEventListener("pointermove", (ev) => {
        if (!pts.has(ev.pointerId)) return;
        pts.set(ev.pointerId, [ev.clientX, ev.clientY]);
        if (pts.size === 2) {
          const [a, c] = [...pts.values()];
          const dist = Math.hypot(a[0] - c[0], a[1] - c[1]), cx = (a[0] + c[0]) / 2, cy = (a[1] + c[1]) / 2;
          const b = cv.getBoundingClientRect();
          if (pinch) { zoomAt(dist / pinch.d, cx - b.left, cy - b.top); if (DOT.user) { DOT.user.ox += cx - pinch.cx; DOT.user.oy += cy - pinch.cy; } }
          pinch = { d: dist, cx, cy }; DOT.moved = 99;
          return;
        }
        if (!last || !DOT.user) return;
        const dx = ev.clientX - last[0], dy = ev.clientY - last[1];
        last = [ev.clientX, ev.clientY];
        DOT.moved = (DOT.moved || 0) + Math.abs(dx) + Math.abs(dy);
        if (DOT.user.z > 1) { DOT.user.ox += dx; DOT.user.oy += dy; hideTip(); redraw(); }
      });
      const up = (ev) => { pts.delete(ev.pointerId); if (!pts.size) { last = null; pinch = null; DOT.dragged = (DOT.moved || 0) > 4; DOT.dragging = false; if (cv.style.cursor === "grabbing") cv.style.cursor = "grab"; } };
      cv.addEventListener("pointerup", up); cv.addEventListener("pointercancel", up);
      const zb = document.getElementById("dotmap-zoom");
      if (zb) zb.addEventListener("click", () => { DOT.user = null; drawDotMap(false); });
      document.querySelectorAll("[data-dz]").forEach((b) => b.addEventListener("click", () => {
        const V = DOT.view; if (!V) return;
        zoomAt(b.dataset.dz === "in" ? 2 : 0.5, V.W / 2, V.H / 2);
      }));
    })();
    const dotCities = document.getElementById("dotmap-cities");
    if (dotCities) dotCities.addEventListener("click", () => { DOT.showCities = DOT.showCities === false; drawDotMap(false); });
    (function lazyDots() {
      const box = document.getElementById("dotmap");
      if (!box) return;
      const go = () => loadDotMeta().then(() => drawDotMap(true)).catch((e) => { box.innerHTML = `<p class="src">Dot map data did not load (${esc(String(e))}).</p>`; });
      if (!("IntersectionObserver" in window)) return go();
      const io = new IntersectionObserver((ents) => { if (ents.some((e) => e.isIntersecting)) { io.disconnect(); go(); } }, { rootMargin: "300px" });
      io.observe(box);
    })();

    function filterHouse435() {
      const f = state.hgridFilter;
      DISTRICTS.forEach((d) => {
        if (!d.el) return;
        const match =
          f === "all" ||
          (f === "flip" && d.flip) ||
          (f === "unc" && !d.called) ||
          (f === "close" && !d.same && !d.uncontested && Math.abs(d.margin) < 3);
        d.el.classList.toggle("dim", !match);
      });
    }

    document.querySelectorAll("#hgrid-filters .chip").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.hgridFilter = btn.dataset.hf;
        document.querySelectorAll("#hgrid-filters .chip").forEach((b) => {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        filterHouse435();
      });
    });

    function drawHouseScatter() {
      const box = document.getElementById("house-state-scatter");
      if (!box) return;
      box.innerHTML = "";

      const by = {};
      DISTRICTS.forEach((d) => {
        const s = by[d.st] || (by[d.st] = { st: d.st, D: 0, R: 0, n: 0, unc: 0 });
        d.c.forEach((c) => {
          if (c.p === "D") s.D += c.v;
          else if (c.p === "R") s.R += c.v;
        });
        s.n++;
        if (!(d.c.some((c) => c.p === "D") && d.c.some((c) => c.p === "R"))) s.unc++;
      });

      const pts = Object.values(by)
        .filter((s) => s.st !== "LA" && s.st !== "AK" && s.D > 0 && s.R > 0 && pres24[s.st] !== undefined && s.unc / s.n < 0.5)
        .map((s) => ({
          ...s,
          x: pres24[s.st],
          y: (100 * (s.D - s.R)) / (s.D + s.R),
          v: s.D + s.R
        }));

      const W = box.clientWidth || 500;
      const Hh = Math.min(480, Math.max(330, Math.round(W * 0.68)));
      const m = { l: 46, r: 16, t: 16, b: 42 };
      const svg = S("svg", {
        width: W,
        height: Hh,
        viewBox: `0 0 ${W} ${Hh}`,
        role: "img",
        "aria-label": "Scatterplot of 2026 House vote margin vs 2024 presidential margin by state"
      }, box);

      const lo = -50, hi = 50;
      const X = (v) => m.l + ((v - lo) / (hi - lo)) * (W - m.l - m.r);
      const Y = (v) => Hh - m.b - ((v - lo) / (hi - lo)) * (Hh - m.t - m.b);

      for (let v = lo; v <= hi; v += 25) {
        S("line", { class: v === 0 ? "zero" : "gr", x1: X(v), x2: X(v), y1: m.t, y2: Hh - m.b }, svg);
        S("line", { class: v === 0 ? "zero" : "gr", x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v) }, svg);
        S("text", { x: X(v), y: Hh - m.b + 16, "text-anchor": "middle", class: "ax-num" }, svg).textContent = v === 0 ? "Even" : (v > 0 ? "D+" : "R+") + Math.abs(v);
        S("text", { x: m.l - 6, y: Y(v) + 4, "text-anchor": "end", class: "ax-num" }, svg).textContent = v === 0 ? "Even" : (v > 0 ? "D+" : "R+") + Math.abs(v);
      }

      S("text", { x: (m.l + W - m.r) / 2, y: Hh - 6, "text-anchor": "middle", fill: "var(--ink2)" }, svg).textContent = "2024 presidential margin →";
      S("line", { x1: X(lo), y1: Y(lo), x2: X(hi), y2: Y(hi), stroke: "var(--mut)", "stroke-dasharray": "4 4", "stroke-width": 1 }, svg);
      S("text", { x: X(30), y: Y(30) + 15, "text-anchor": "middle", class: "ax-num" }, svg).textContent = "Same as 2024";

      const sh = natVote.margin - (pres24.US ?? -1.47);
      S("line", { x1: X(lo), y1: Y(lo + sh), x2: X(hi - sh), y2: Y(hi), stroke: "var(--D)", "stroke-width": 1.4, opacity: 0.6 }, svg);
      S("text", { x: X(hi - sh) - 4, y: Y(hi) + 13, "text-anchor": "end", class: "ax-num", fill: "var(--D)" }, svg).textContent = `National swing (${fmtSwing(sh)})`;

      const maxv = Math.max(...pts.map((p) => p.v));
      const rr = (v) => 3.2 + 10.5 * Math.sqrt(v / maxv);

      pts.sort((a, b) => b.v - a.v).forEach((p) => {
        const c = S("circle", {
          cx: X(p.x),
          cy: Y(Math.max(lo, Math.min(hi, p.y))),
          r: rr(p.v),
          fill: `var(--${p.y >= 0 ? "D" : "R"})`,
          "fill-opacity": 0.78,
          stroke: "var(--bg)",
          "stroke-width": 1.4,
          style: "cursor:pointer"
        }, svg);
        bindTip(c, () => `
          <div class="h">${esc(STATE_NAMES[p.st])}</div>
          <div class="r"><span>2024 president</span><span class="w">${fmtMargin(p.x, true)}</span></div>
          <div class="r"><span>2026 House vote</span><span class="w">${fmtMargin(p.y, true)}</span></div>
          <div class="m">Shift ${fmtSwing(p.y - p.x)} · ${(p.v / 1e6).toFixed(2)}M votes · ${p.n} seats</div>
        `);
      });

      const lab = new Set(["TX", "FL", "CA", "NY", "OH", "KS", "NC", "UT", "NE", "WY", "WV", "MI", "PA", "IA"]);
      pts.filter((p) => lab.has(p.st)).forEach((p) => {
        S("text", {
          x: X(p.x) + rr(p.v) + 3,
          y: Y(p.y) + 4,
          class: "ax-num",
          fill: "var(--ink2)",
          "pointer-events": "none"
        }, svg).textContent = p.st;
      });
    }

    function renderHouseFlipsTable() {
      const tb = document.getElementById("house-flips-table");
      if (!tb) return;

      const filtered = data.house.flips.filter((f) => {
        if (state.houseFilter === "called") return f.called;
        if (state.houseFilter === "uncalled") return !f.called;
        if (state.houseFilter === "incumbent") return f.type === "incumbent";
        return true;
      });

      tb.innerHTML = `
        <thead>
          <tr><th>District</th><th>Democrat</th><th>Defeated / Prior</th><th class="num">Margin</th><th class="num">In</th></tr>
        </thead>
        <tbody>
          ${filtered.map((f) => {
            const dd = distById.get(f.d);
            const mg = dd && dd.c.length > 1 ? dd.c[0].pct - dd.c[1].pct : null;
            return `
              <tr>
                <td class="mono" style="font-size:12.5px"><b>${esc(f.d)}</b>${f.called ? ` <span style="color:var(--D)">${ICONS.star}</span>` : ` <span style="color:var(--mut);font-size:11px">leads</span>`}</td>
                <td><span class="pill D">D</span> ${esc(f.winner)}</td>
                <td>${esc(f.loser)}</td>
                <td class="num" style="color:var(--D);font-weight:600">${mg !== null ? `+${mg.toFixed(1)}` : "n/a"}</td>
                <td class="num">${dd ? `${dd.pin}%` : "n/a"}</td>
              </tr>
            `;
          }).join("")}
        </tbody>
      `;
    }

    document.querySelectorAll("[data-house-filter]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.houseFilter = btn.dataset.houseFilter;
        document.querySelectorAll("[data-house-filter]").forEach((b) => {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        renderHouseFlipsTable();
      });
    });

    buildHouse435Grid();
    renderHouseFlipsTable();

    /* ----------------------------------------------------------------------
       3. Senate 100-Seat Hemicycle (Crisp White ★ Inside Flips) & Ladder
       ---------------------------------------------------------------------- */
    function renderHemicycle() {
      const svg = document.getElementById("senate-hemicycle");
      if (!svg) return;
      const rowCounts = [19, 23, 27, 31];
      const radii = [88, 117, 146, 175];
      const cx = 220, cy = 200;

      const seats = [];
      for (let i = 0; i < 34; i++) seats.push({ cat: "dem-notup", label: "Democratic Caucus · Seat not up in 2026" });
      data.senate.races.filter((r) => r.called && !r.flip && r.wp === "D")
        .forEach((r) => seats.push({ cat: "dem-hold", label: `${r.name}: ${r.win} (${fmtMargin(r.margin, true)}) · Dem Hold` }));
      data.senate.races.filter((r) => r.called && r.flip)
        .forEach((r) => seats.push({ cat: "dem-flip", label: `${r.name}: ${r.win} (${fmtMargin(r.margin, true)}) · ★ Dem Flip` }));
      data.senate.races.filter((r) => !r.called)
        .forEach((r) => seats.push({ cat: "uncalled", label: `${r.name}: Uncalled (${r.win} ${r.wpct}% vs. ${r.ru} ${r.rpct}%)` }));
      data.senate.races.filter((r) => r.called && r.wp === "R")
        .forEach((r) => seats.push({ cat: "rep-hold", label: `${r.name}: ${r.win} (${fmtMargin(r.margin, true)}) · GOP Hold` }));
      for (let i = 0; i < 31; i++) seats.push({ cat: "rep-notup", label: "Republican · Seat not up in 2026" });

      const coords = [];
      rowCounts.forEach((count, rIdx) => {
        const rad = radii[rIdx];
        for (let i = 0; i < count; i++) {
          const angle = Math.PI - (i / (count - 1)) * Math.PI;
          coords.push({ angle, x: cx + rad * Math.cos(angle), y: cy - rad * Math.sin(angle) });
        }
      });
      coords.sort((a, b) => b.angle - a.angle);

      svg.innerHTML = `
        <line x1="${cx}" y1="12" x2="${cx}" y2="${cy - 64}" stroke="var(--ink)" stroke-width="1.4" stroke-dasharray="4 3" />
        <text x="${cx}" y="10" text-anchor="middle" font-family="var(--mono)" font-size="9.5" fill="var(--mut)">50 / 50</text>
        ${coords.map((pt, idx) => {
          const seat = seats[idx];
          const x = pt.x.toFixed(1), y = pt.y.toFixed(1);
          if (seat.cat === "dem-flip") {
            return `<g class="hemi-seat" data-idx="${idx}" style="cursor:pointer">
              <circle cx="${x}" cy="${y}" r="8.1" fill="var(--D)" stroke="var(--ink)" stroke-width="1.6" />
              <path d="${svgStarPath(pt.x, pt.y, 4.4, 1.85)}" fill="#ffe169" pointer-events="none" />
            </g>`;
          }
          const attrs =
            seat.cat === "dem-notup" ? `r="6.5" fill="var(--D)" fill-opacity="0.42"` :
            seat.cat === "dem-hold" ? `r="6.8" fill="var(--D)"` :
            seat.cat === "uncalled" ? `r="6.8" fill="var(--alt)" stroke="var(--ink)" stroke-width="1.6" stroke-dasharray="2.2 1.6"` :
            seat.cat === "rep-hold" ? `r="6.8" fill="var(--R)"` :
            `r="6.5" fill="var(--R)" fill-opacity="0.42"`;
          return `<g class="hemi-seat" data-idx="${idx}" style="cursor:pointer"><circle cx="${x}" cy="${y}" ${attrs} /></g>`;
        }).join("")}
        <text x="${cx}" y="${cy - 28}" text-anchor="middle" font-family="var(--serif)" font-weight="700" font-size="32" fill="var(--D)">54 D</text>
        <text x="${cx}" y="${cy - 9}" text-anchor="middle" font-family="var(--mono)" font-size="10.5" fill="var(--mut)">44 R · 2 UNCALLED</text>
      `;

      svg.querySelectorAll(".hemi-seat").forEach((g) => {
        const s = seats[Number(g.dataset.idx)];
        bindTip(g, () => `<div class="h">Seat ${Number(g.dataset.idx) + 1}</div><div>${esc(s.label)}</div>`);
      });
    }
    renderHemicycle();

    function renderMarginLadder() {
      const container = document.getElementById("senate-margin-ladder");
      if (!container) return;
      const comp = data.senate.races.filter((r) => Math.abs(r.margin) <= 20).sort((a, b) => b.margin - a.margin);
      const maxScale = 22;

      container.innerHTML = comp.map((r, idx) => {
        const pctWidth = Math.min(50, (Math.abs(r.margin) / maxScale) * 50);
        const isDem = r.margin >= 0;
        const left = isDem ? 50 : 50 - pctWidth;
        const color = !r.called ? "var(--N)" : r.flip ? "var(--D)" : isDem ? "var(--D3)" : "var(--R)";
        const tag = r.flip ? ` <span style="color:var(--D)">${ICONS.star}</span>` : !r.called ? ` <span style="color:var(--mut)">${ICONS.clock}</span>` : "";
        return `
          <div class="ladder-row" data-idx="${idx}">
            <div class="ladder-st"><span class="mono" style="font-size:11.5px;color:var(--mut)">${esc(r.st)}</span> ${esc(r.win.split(" ").pop())}${tag}</div>
            <div class="ladder-track">
              <div class="ladder-zero"></div>
              <div class="ladder-fill ${r.flip ? "is-flip" : ""}" style="inset-inline-start:${left.toFixed(1)}%;inline-size:${Math.max(1.5, pctWidth).toFixed(1)}%;background:${color}"></div>
            </div>
            <div class="ladder-val" style="color:${!r.called ? "var(--mut)" : isDem ? "var(--D)" : "var(--R)"}">${fmtMargin(r.margin, r.called)}</div>
          </div>
        `;
      }).join("");

      container.querySelectorAll(".ladder-row").forEach((row) => {
        const r = comp[Number(row.dataset.idx)];
        bindTip(row, () => `
          <div class="h">${esc(r.name)}${r.flip ? " · ★ Flipped" : ""}</div>
          <div class="r"><span><i style="background:var(--${r.wp})"></i>${esc(r.win)}</span><span class="w">${r.wpct.toFixed(1)}%</span></div>
          <div class="r"><span><i style="background:var(--${r.rp === "I" ? "I" : r.rp})"></i>${esc(r.ru)}</span><span>${r.rpct.toFixed(1)}%</span></div>
          <div class="m">2024 pres. ${fmtMargin(r.pres24, true)} · Shift ${fmtSwing(r.swing)}</div>
        `);
        row.addEventListener("click", () => selectState(r.st));
      });
    }
    renderMarginLadder();

    /* ----------------------------------------------------------------------
       4. Same-Ballot Ticket-Splitting Dumbbell Chart
       ---------------------------------------------------------------------- */
    function renderTicketSplitting() {
      const wrap = document.getElementById("ticket-split-chart");
      if (!wrap) return;
      const pairs = [];
      data.senate.races.forEach((s) => {
        const g = govBySt.get(s.st);
        if (g && s.margin !== null && g.margin !== null) {
          pairs.push({
            st: s.st,
            name: STATE_NAMES[s.st],
            s,
            g,
            sen: s.margin,
            gov: g.margin,
            gap: Math.abs(s.margin - g.margin),
            splitWinner: (s.margin >= 0) !== (g.margin >= 0)
          });
        }
      });

      const top = pairs.sort((a, b) => b.gap - a.gap).slice(0, 16);
      const scale = 36;
      const pos = (v) => Math.min(98, Math.max(2, 50 + (v / scale) * 50));

      wrap.innerHTML = top.map((p, idx) => {
        const pSen = pos(p.sen);
        const pGov = pos(p.gov);
        const left = Math.min(pSen, pGov);
        const width = Math.abs(pSen - pGov);
        const senCol = p.sen >= 0 ? "var(--D)" : "var(--R)";
        const govCol = p.gov >= 0 ? "var(--D)" : "var(--R)";
        return `
          <div class="db-row" data-idx="${idx}">
            <div style="font-weight:600;color:var(--ink);white-space:nowrap;overflow:clip;text-overflow:ellipsis">
              ${esc(p.name)}${p.splitWinner ? ` <span class="badge badge-flip" style="font-size:9.5px;padding:1px 5px">Split</span>` : ""}
            </div>
            <div class="db-track">
              <div class="db-zero"></div>
              <div class="db-conn" style="inset-inline-start:${left.toFixed(1)}%;inline-size:${width.toFixed(1)}%"></div>
              <div class="db-pt sen" style="inset-inline-start:${pSen.toFixed(1)}%;background:${senCol}"></div>
              <div class="db-pt gov" style="inset-inline-start:${pGov.toFixed(1)}%;background:${govCol}"></div>
            </div>
            <div style="font-family:var(--mono);font-size:12px;text-align:end;font-weight:600;color:var(--ink)">${p.gap.toFixed(1)} pts</div>
          </div>
        `;
      }).join("");

      wrap.querySelectorAll(".db-row").forEach((row) => {
        const p = top[Number(row.dataset.idx)];
        bindTip(row, () => `
          <div class="h">${esc(p.name)} · ${p.gap.toFixed(1)}-pt gap</div>
          <div class="r"><span>● Senate (${esc(p.s.win.split(" ").pop())})</span><span class="w">${fmtMargin(p.sen, p.s.called)}</span></div>
          <div class="r"><span>◆ Governor (${esc(p.g.win.replace(" (inc.)", "").split(" ").pop())})</span><span class="w">${fmtMargin(p.gov, p.g.called)}</span></div>
        `);
        row.addEventListener("click", () => selectState(p.st));
      });
    }
    renderTicketSplitting();

    /* ----------------------------------------------------------------------
       5. 50-State Cartogram + State Detail Briefing
       ---------------------------------------------------------------------- */
    const cartogramEl = document.getElementById("cartogram-grid");
    const mapLegendEl = document.getElementById("map-legend");
    const inspectorEl = document.getElementById("state-inspector");

    function getStateSwing(st) {
      const s = senBySt.get(st);
      if (s && s.swing !== null && s.swing !== undefined) return { sw: s.swing, office: "Sen." };
      const g = govBySt.get(st);
      if (g && g.swing !== null && g.swing !== undefined) return { sw: g.swing, office: "Gov." };
      return null;
    }

    function getTileMeta(st, mode) {
      if (mode === "senate") {
        const r = senBySt.get(st);
        if (!r) {
          const h = senHoldBySt.get(st);
          return { tone: "tone-dim", sub: h ? h.del : "n/a", flip: false, arrow: "", label: `${STATE_NAMES[st]}: No 2026 Senate race (${h ? h.del : ""})` };
        }
        if (!r.called) return { tone: "tone-uncalled", sub: fmtMargin(r.margin, false), flip: false, arrow: "", label: `${r.name}: Uncalled (${r.win} ${r.wpct}% vs. ${r.ru} ${r.rpct}%)` };
        if (r.flip) return { tone: "tone-dem-flip", sub: fmtMargin(r.margin, true), flip: true, arrow: "", label: `${r.name}: ★ Dem Flip, ${r.win} (${fmtMargin(r.margin, true)})` };
        return { tone: r.wp === "D" ? "tone-dem-solid" : "tone-rep-solid", sub: fmtMargin(r.margin, true), flip: false, arrow: "", label: `${r.name}: ${r.win} (${r.wp}) ${fmtMargin(r.margin, true)}` };
      }

      if (mode === "governors") {
        const g = govBySt.get(st);
        if (!g) {
          const h = govHoldBySt.get(st);
          return { tone: "tone-dim", sub: h ? `Hold ${h.p}` : "n/a", flip: false, arrow: "", label: `${STATE_NAMES[st]}: No 2026 Governor race` };
        }
        if (!g.called) return { tone: "tone-uncalled", sub: fmtMargin(g.margin, false), flip: false, arrow: "", label: `${g.name}: Uncalled, ${g.win} leads` };
        if (g.flip) return { tone: "tone-dem-flip", sub: fmtMargin(g.margin, true), flip: true, arrow: "", label: `${g.name}: ★ Dem Flip, ${g.win} (${fmtMargin(g.margin, true)})` };
        return { tone: g.wp === "D" ? "tone-dem-solid" : "tone-rep-solid", sub: fmtMargin(g.margin, true), flip: false, arrow: "", label: `${g.name}: ${g.win} (${g.wp}) ${fmtMargin(g.margin, true)}` };
      }

      if (mode === "house") {
        const list = houseBySt.get(st) || [];
        if (!list.length) return { tone: "tone-dim", sub: "0", flip: false, arrow: "", label: `${STATE_NAMES[st]}: 0 House pickups` };
        const tone = list.length >= 3 ? "tone-house-3" : list.length === 2 ? "tone-house-2" : "tone-house-1";
        return { tone, sub: `+${list.length} D`, flip: list.length >= 3, arrow: "", label: `${STATE_NAMES[st]}: ${list.length} Democratic House pickup(s)` };
      }

      if (mode === "swing") {
        const swObj = getStateSwing(st);
        if (!swObj) return { tone: "tone-dim", sub: "No race", flip: false, arrow: "", label: `${STATE_NAMES[st]}: No statewide contest` };
        const sw = swObj.sw;
        const isDem = sw >= 0;
        // Straight arrow from a shared origin edge; length scales 0-30 pts across the tile, with a floor so small shifts stay readable
        const color = isDem ? "var(--D)" : "var(--R)";
        const len = 12 + Math.min(1, Math.abs(sw) / 30) * 30;
        const x1 = isDem ? 44 : 2;
        const x2 = isDem ? x1 - len : x1 + len;
        const hd = isDem ? 6 : -6;
        const arrowSvg = `<svg viewBox="0 0 46 12" class="tile-arrow" preserveAspectRatio="xMinYMid meet" aria-hidden="true">
          <line x1="${x1}" y1="6" x2="${(x2 + hd * 0.6).toFixed(1)}" y2="6" stroke="${color}" stroke-width="2.4" stroke-linecap="round"/>
          <polygon points="${x2.toFixed(1)},6 ${(x2 + hd).toFixed(1)},1.8 ${(x2 + hd).toFixed(1)},10.2" fill="${color}"/>
        </svg>`;
        return { tone: isDem ? "tone-shift-dem" : "tone-shift-rep", sub: fmtSwing(sw), flip: false, arrow: arrowSvg, label: `${STATE_NAMES[st]}: ${fmtSwing(sw)} shift from 2024 (${swObj.office})` };
      }

      const s = senBySt.get(st);
      const g = govBySt.get(st);
      const hCount = (houseBySt.get(st) || []).length;
      const flips = (s && s.flip ? 1 : 0) + (g && g.flip ? 1 : 0) + hCount;
      if (flips >= 3) return { tone: "tone-dem-flip", sub: `${flips} flips`, flip: true, arrow: "", label: `${STATE_NAMES[st]}: ${flips} Democratic pickups` };
      if (flips >= 1) return { tone: "tone-dem-solid", sub: `${flips} ${flips === 1 ? "flip" : "flips"}`, flip: false, arrow: "", label: `${STATE_NAMES[st]}: ${flips} Democratic pickup(s)` };
      return { tone: "tone-dim", sub: "0", flip: false, arrow: "", label: `${STATE_NAMES[st]}: 0 chamber flips` };
    }

    function renderMapLegend() {
      if (!mapLegendEl) return;
      if (state.mapMode === "house") {
        mapLegendEl.innerHTML = `
          <span><span class="swatch-flip-demo">${ICONS.star}</span>3–5 Dem pickups (NC, PA, IA)</span>
          <span><i style="background:var(--D3)"></i>2 pickups</span>
          <span><i style="background:var(--D1)"></i>1 pickup</span>
          <span><i style="background:var(--alt);border:1px solid var(--line)"></i>0 pickups</span>
        `;
      } else if (state.mapMode === "swing") {
        mapLegendEl.innerHTML = `
          <span><i style="background:var(--dem-soft);border:1px solid var(--D)"></i>Shifted Democratic vs. '24</span>
          <span><i style="background:var(--rep-soft);border:1px solid var(--R)"></i>Shifted Republican vs. '24 (VT Gov.)</span>
          <span><i style="background:var(--alt);border:1px solid var(--line)"></i>No statewide race</span>
        `;
      } else {
        mapLegendEl.innerHTML = `
          <span><span class="swatch-flip-demo">${ICONS.star}</span>Dem Flip</span>
          <span><i style="background:var(--D)"></i>Dem Hold</span>
          <span><i style="background:var(--R)"></i>GOP Hold</span>
          <span><i style="background:repeating-linear-gradient(135deg,var(--alt) 0 3px,var(--bg) 3px 6px);border:1px dashed var(--ink2)"></i>Uncalled</span>
          <span><i style="background:var(--alt);border:1px solid var(--line)"></i>Not Up</span>
        `;
      }
    }

    function renderInspector(st) {
      if (!inspectorEl) return;
      if (!st) {
        const senFl = data.senate.races.filter((r) => r.flip).map((r) => r.st);
        const govFl = data.governors.races.filter((r) => r.flip).map((r) => r.st);
        inspectorEl.innerHTML = `
          <div class="inspector-eyebrow">Nationwide</div>
          <h3 class="inspector-title"><span>All states</span></h3>
          <div class="inspector-block"><h4>U.S. Senate</h4><div class="cand-line"><span>Democrats ${data.senate.after.D} · Republicans ${data.senate.after.R}</span><span class="mono">${data.senate.after.uncalled} uncalled</span></div><div class="cand-line" style="font-size:12.5px;color:var(--mut)"><span>Democratic flips: ${senFl.join(", ")}</span></div></div>
          <div class="inspector-block"><h4>Governors</h4><div class="cand-line" style="font-size:12.5px;color:var(--mut)"><span>Democratic flips: ${govFl.join(", ")}</span></div></div>
          <div class="inspector-block"><h4>U.S. House</h4><div class="cand-line"><span>Democrats ${natVote.d_called ?? 236} · Republicans ${natVote.r_called ?? 146}</span><span class="mono">${fmtMargin(natVote.margin, true)} vote</span></div></div>
          <p style="font-family:var(--sans);font-size:13px;color:var(--mut);margin:12px 0 0">Select a state to see its races. Select it again or press Esc to clear.</p>
        `;
        return;
      }
      const s = senBySt.get(st);
      const sh = senHoldBySt.get(st);
      const g = govBySt.get(st);
      const gh = govHoldBySt.get(st);
      const hList = houseBySt.get(st) || [];
      const mList = measBySt.get(st) || [];
      const p24 = pres24[st];
      const ev = evMap[st] || "n/a";

      const p24Html = p24 !== undefined
        ? `<div style="font-family:var(--mono);font-size:11.5px;color:var(--mut);margin-block-end:8px">
            2024 Pres.: <strong style="color:${p24 >= 0 ? "var(--D)" : "var(--R)"}">${fmtMargin(p24, true)}</strong> · EV: <strong>${ev}</strong>
           </div>`
        : "";

      let senHtml = "";
      if (s) {
        const badge = !s.called
          ? `<span class="badge badge-uncalled">${ICONS.clock} Uncalled</span>`
          : s.flip
            ? `<span class="badge badge-flip">${ICONS.star} Dem Flip</span>`
            : `<span class="badge ${s.wp === "D" ? "badge-dem" : "badge-rep"}">${s.wp === "D" ? "Dem" : "GOP"} Hold</span>`;
        senHtml = `
          <div class="inspector-block">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-block-end:5px">
              <h4 style="margin:0">U.S. Senate</h4>${badge}
            </div>
            <div class="cand-line"><span><strong>${esc(s.win)}</strong> (${esc(s.wp)})${s.called ? ` ${ICONS.check}` : ""}</span><strong class="mono">${s.wpct.toFixed(1)}%</strong></div>
            <div class="cand-bar"><span style="inline-size:${s.wpct}%;background:var(--${s.wp})"></span></div>
            <div class="cand-line"><span>${esc(s.ru)} (${esc(s.rp)})</span><span class="mono">${s.rpct !== null ? s.rpct.toFixed(1) + "%" : "n/a"}</span></div>
            <div class="cand-bar"><span style="inline-size:${s.rpct || 0}%;background:var(--${s.rp === "I" ? "I" : s.rp})"></span></div>
            <p class="inspector-note">${esc(s.note)}${s.swing !== null ? ` · Shift vs. '24: <strong class="mono">${fmtSwing(s.swing)}</strong>` : ""}</p>
          </div>
        `;
      } else if (sh) {
        senHtml = `<div class="inspector-block"><h4>U.S. Senate · Not Up</h4><p class="inspector-note" style="margin:0">Delegation (<strong class="mono">${esc(sh.del)}</strong>): ${esc(sh.sens)}</p></div>`;
      }

      let govHtml = "";
      if (g) {
        const badge = !g.called
          ? `<span class="badge badge-uncalled">${ICONS.clock} Uncalled</span>`
          : g.flip
            ? `<span class="badge badge-flip">${ICONS.star} Dem Flip</span>`
            : `<span class="badge ${g.wp === "D" ? "badge-dem" : "badge-rep"}">${g.wp === "D" ? "Dem" : "GOP"} Hold</span>`;
        govHtml = `
          <div class="inspector-block">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-block-end:5px">
              <h4 style="margin:0">Governor</h4>${badge}
            </div>
            <div class="cand-line"><span><strong>${esc(g.win)}</strong> (${esc(g.wp)})${g.called ? ` ${ICONS.check}` : ""}</span><strong class="mono">${g.wpct.toFixed(1)}%</strong></div>
            <div class="cand-bar"><span style="inline-size:${g.wpct}%;background:var(--${g.wp})"></span></div>
            <div class="cand-line"><span>${esc(g.ru)} (${esc(g.rp)})</span><span class="mono">${g.rpct !== null ? g.rpct.toFixed(1) + "%" : "n/a"}</span></div>
            <div class="cand-bar"><span style="inline-size:${g.rpct || 0}%;background:var(--${g.rp})"></span></div>
            <p class="inspector-note">${esc(g.note)}${g.swing !== null ? ` · Shift vs. '24: <strong class="mono">${fmtSwing(g.swing)}</strong>` : ""}</p>
          </div>
        `;
      } else if (gh) {
        govHtml = `<div class="inspector-block"><h4>Governor · Not Up</h4><p class="inspector-note" style="margin:0">${esc(gh.gov)}</p></div>`;
      }

      const houseHtml = hList.length
        ? `<div class="inspector-block"><h4>House Pickups &amp; Leads (${hList.length})</h4>${hList.map((h) => `<div class="cand-line" style="font-size:12.5px"><span><strong class="mono">${esc(h.d)}</strong>: ${esc(h.winner)} (D)</span><span class="mono" style="font-size:11.5px;color:var(--mut)">${h.called ? `${ICONS.star} Flipped` : `${ICONS.clock} Leads`}</span></div>`).join("")}</div>`
        : "";

      const measHtml = mList.length
        ? `<div class="inspector-block"><h4>Ballot Measures (${mList.length})</h4>${mList.map((m) => `<div class="cand-line" style="font-size:12.5px"><span><strong>${esc(m.m)}</strong> (${esc(m.topic)})</span><span class="badge ${m.res === "passed" ? "badge-pass" : m.res === "failed" ? "badge-fail" : "badge-uncalled"}">${m.res === "passed" ? ICONS.check : m.res === "failed" ? ICONS.cross : ICONS.clock} ${m.yes.toFixed(1)}%</span></div>`).join("")}</div>`
        : "";

      inspectorEl.innerHTML = `
        <div class="inspector-eyebrow" style="display:flex;justify-content:space-between;align-items:center">State Detail<button type="button" class="chip" data-clear-state style="font-size:11.5px;padding:2px 10px">Clear ×</button></div>
        <h3 class="inspector-title"><span>${esc(STATE_NAMES[st])}</span><span style="font-family:var(--mono);font-size:13px;color:var(--mut)">${esc(st)}</span></h3>
        ${p24Html}${senHtml}${govHtml}${houseHtml}${measHtml}
      `;
    }

    function selectState(st) {
      state.selectedSt = st;
      if (cartogramEl) {
        cartogramEl.querySelectorAll(".state-tile").forEach((b) => {
          b.setAttribute("aria-selected", b.dataset.st === st ? "true" : "false");
        });
      }
      renderInspector(st);
      drawHexMap();
      drawDotMap(false);
      const clr = inspectorEl && inspectorEl.querySelector("[data-clear-state]");
      if (clr) clr.addEventListener("click", () => selectState(null));
    }

    function renderCartogram() {
      if (!cartogramEl) return;
      renderMapLegend();
      cartogramEl.innerHTML = STATE_GRID.map(([st, col, row]) => {
        const meta = getTileMeta(st, state.mapMode);
        const sel = state.selectedSt === st ? "true" : "false";
        return `
          <button type="button"
            class="state-tile ${meta.tone}"
            style="grid-column:${col};grid-row:${row}"
            data-st="${st}"
            aria-selected="${sel}"
            aria-label="${esc(meta.label)}">
            ${meta.flip ? `<span class="flip-star" aria-hidden="true">${ICONS.star}</span>` : ""}
            <span class="st-code">${st}</span>
            ${meta.arrow}
            <span class="st-sub">${esc(meta.sub)}</span>
          </button>
        `;
      }).join("");

      cartogramEl.querySelectorAll(".state-tile").forEach((btn) => {
        const st = btn.dataset.st;
        bindTip(btn, () => `<div class="h">${esc(STATE_NAMES[st])}</div><div>${esc(getTileMeta(st, state.mapMode).label)}</div>`);
        btn.addEventListener("click", () => selectState(state.selectedSt === st ? null : st));
      });
    }

    document.querySelectorAll("[data-map-mode]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.mapMode = btn.dataset.mapMode;
        document.querySelectorAll("[data-map-mode]").forEach((b) => {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        renderCartogram();
      });
    });

    renderCartogram();
    selectState(state.selectedSt);
    document.addEventListener("keydown", (e) => {
      if (e.key !== "Escape" || document.querySelector("dialog[open]")) return;
      if (DOT.user && DOT.user.z > 1.02) { DOT.user = null; drawDotMap(false); return; }   // first Esc: reset the zoom
      if (state.selectedSt) selectState(null);                                               // second: leave the state
    });

    /* ----------------------------------------------------------------------
       6. Closest Uncalled Races Table + Uncalled Simulator
       ---------------------------------------------------------------------- */
    function renderUncalledTable() {
      const tb = document.getElementById("uncalled-table");
      const moreBtn = document.getElementById("uncalled-more-btn");
      if (!tb) return;

      const list = [];
      data.senate.races.filter((r) => !r.called).forEach((r) => {
        list.push({
          race: `${r.name} Senate`,
          a: { n: r.win, p: r.wp },
          b: { n: r.ru, p: r.rp },
          gap: Math.abs(r.wpct - r.rpct),
          pin: r.pct_in
        });
      });
      data.governors.races.filter((r) => !r.called).forEach((r) => {
        list.push({
          race: `${r.name} Governor`,
          a: { n: r.win, p: r.wp },
          b: { n: r.ru, p: r.rp },
          gap: Math.abs(r.wpct - r.rpct),
          pin: r.pct_in
        });
      });
      DISTRICTS.filter((d) => !d.called && !d.same).forEach((d) => {
        const a = d.c[0], b = d.c[1] || {};
        list.push({
          race: d.id,
          a: { n: a.n, p: a.p },
          b: { n: b.n || "n/a", p: b.p || "I" },
          gap: Math.abs(a.pct - (b.pct || 0)),
          pin: d.pin
        });
      });

      list.sort((x, y) => x.gap - y.gap);
      const shown = state.uncalledShowAll ? list : list.slice(0, 16);

      tb.innerHTML = `
        <thead><tr><th>Contest</th><th>Leader</th><th>Trailing</th><th class="num">Gap</th><th>Counted</th></tr></thead>
        <tbody>
          ${shown.map((r) => `
            <tr>
              <td><b>${esc(r.race)}</b></td>
              <td><span class="pill ${r.a.p}">${r.a.p}</span> ${esc(r.a.n)}</td>
              <td><span class="pill ${r.b.p}">${r.b.p}</span> ${esc(r.b.n)}</td>
              <td class="num">${r.gap < 0.05 ? "&lt;0.1" : r.gap.toFixed(1)}</td>
              <td style="min-inline-size:95px">
                ${r.pin != null ? `<div class="mbar" style="min-inline-size:58px;display:inline-block;vertical-align:middle;margin-inline-end:6px"><i style="inset-inline-start:0;inline-size:${r.pin}%;background:var(--N)"></i></div><span style="font-family:var(--mono);font-size:11px;color:var(--mut)">${r.pin}%</span>` : "n/a"}
              </td>
            </tr>
          `).join("")}
        </tbody>
      `;

      if (moreBtn) {
        moreBtn.style.display = list.length > 16 ? "" : "none";
        moreBtn.textContent = state.uncalledShowAll ? "Show closest 16" : `Show all ${list.length} uncalled races`;
      }
    }

    const uncMoreBtn = document.getElementById("uncalled-more-btn");
    if (uncMoreBtn) {
      uncMoreBtn.addEventListener("click", () => {
        state.uncalledShowAll = !state.uncalledShowAll;
        renderUncalledTable();
      });
    }
    renderUncalledTable();

    function renderSimulator() {
      const senD = 54 + (state.sim.akSen === "D" ? 1 : 0) + (state.sim.msSen === "D" ? 1 : 0);
      const senR = 100 - senD;
      const houseD = state.sim.houseDem;
      const houseR = 435 - houseD;
      const govD = 27 + (state.sim.akGov === "D" ? 1 : 0) + (state.sim.ksGov === "D" ? 1 : 0) + (state.sim.orGov === "D" ? 1 : 0);
      const govR = 50 - govD;

      const senEl = document.getElementById("sim-sen-out");
      const hseEl = document.getElementById("sim-house-out");
      const govEl = document.getElementById("sim-gov-out");
      const noteEl = document.getElementById("sim-governance-note");
      if (senEl) senEl.innerHTML = `<strong style="font-family:var(--serif);font-size:24px;color:var(--D)">${senD} D</strong> – ${senR} R`;
      if (hseEl) hseEl.innerHTML = `<strong style="font-family:var(--serif);font-size:24px;color:var(--D)">${houseD} D</strong> – ${houseR} R`;
      if (govEl) govEl.innerHTML = `<strong style="font-family:var(--serif);font-size:24px;color:var(--D)">${govD} D</strong> – ${govR} R`;
      if (noteEl) {
        const cushion = senD - 51;
        noteEl.textContent = `At ${senD}–${senR} in the Senate, Democrats can afford ${cushion} floor defections on judicial confirmations and committee subpoenas (VP Vance breaks 50–50 ties for Republicans), while remaining short of the 60-vote cloture mark.`;
      }
    }

    document.querySelectorAll("[data-sim-key]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const k = btn.dataset.simKey;
        const v = btn.dataset.simVal;
        state.sim[k] = v;
        document.querySelectorAll(`[data-sim-key="${k}"]`).forEach((b) => {
          b.setAttribute("aria-pressed", b.dataset.simVal === v ? "true" : "false");
        });
        renderSimulator();
      });
    });

    const houseSlider = document.getElementById("sim-house-slider");
    const houseSliderVal = document.getElementById("sim-house-slider-val");
    if (houseSlider) {
      houseSlider.addEventListener("input", () => {
        state.sim.houseDem = Number(houseSlider.value);
        if (houseSliderVal) houseSliderVal.textContent = `${state.sim.houseDem} D`;
        renderSimulator();
      });
    }
    renderSimulator();

    /* ----------------------------------------------------------------------
       7. The Electorate: 6 Stat Tiles + National & 45-State Group Dot Plot + Issues + Trust
       ---------------------------------------------------------------------- */
    function renderExitTiles() {
      const box = document.getElementById("exit-tiles");
      if (!box || !data.exit_poll.referendum_tiles) return;
      box.innerHTML = data.exit_poll.referendum_tiles.map((t) => {
        const bars = t.split.map(([l, v, col]) => {
          const bg = col === "ink" ? "var(--ink)" : col === "soft" ? "var(--line2)" : "var(--line)";
          return `<i style="flex:${v} 0 0;background:${bg}"></i>`;
        }).join("");
        const labels = t.split.map(([l, v]) => `<span>${esc(l)} ${v}%</span>`).join("");
        return `
          <div class="tile">
            <div class="v">${t.v}%</div>
            <div class="q">${esc(t.q)}</div>
            <div class="sb">${bars}</div>
            <div class="sbl">${labels}</div>
          </div>
        `;
      }).join("");
    }
    renderExitTiles();

    // Populate Per-State Exit Poll Dropdown (Nationwide + 45 NBC/SSRS States)
    const exitSelect = document.getElementById("exit-state-select");
    const stateEpMap = data.exit_poll.by_state || {};
    const natBenchByKey = new Map(data.exit_poll.groups.map((g) => [`${g.set}|${g.k}`, g]));

    if (exitSelect) {
      const allSts = Object.keys(stateEpMap).sort((a, b) => STATE_NAMES[a].localeCompare(STATE_NAMES[b]));
      exitSelect.innerHTML =
        `<option value="US" selected>Nationwide</option>` +
        allSts.map((st) => `<option value="${st}">${esc(STATE_NAMES[st])}</option>`).join("");

      exitSelect.addEventListener("change", () => {
        state.exitState = exitSelect.value;
        drawExitGroups();
      });
    }

    function filterCategoryMatch(setName) {
      if (state.exitCat === "all") return true;
      if (state.exitCat === "demog") return setName === "Gender" || setName === "Age" || setName === "Race";
      if (state.exitCat === "ses") return setName === "Education" || setName === "Area" || setName === "Income";
      if (state.exitCat === "party") return setName === "Party";
      return true;
    }

    function drawExitGroups() {
      const box = document.getElementById("exit-groups-dotplot");
      const subEl = document.getElementById("exit-groups-sub");
      const benchLg = document.getElementById("exit-bench-legend");
      if (!box) return;
      box.innerHTML = "";

      const isUS = state.exitState === "US" || !stateEpMap[state.exitState];
      const stObj = isUS ? null : stateEpMap[state.exitState];
      const srcGroups = (isUS ? data.exit_poll.groups : stObj.groups).filter((g) => filterCategoryMatch(g.set));

      if (subEl) {
        subEl.textContent = isUS
          ? "National U.S. House exit poll · Dot size shows share of electorate."
          : `${STATE_NAMES[state.exitState]} · ${stObj.office} exit poll (${stObj.dem} D vs. ${stObj.rep} R) · Hollow ring shows national benchmark.`;
      }
      if (benchLg) {
        benchLg.style.display = isUS ? "none" : "flex";
      }

      const sets = [];
      srcGroups.forEach((g) => {
        let s = sets.find((x) => x.k === g.set);
        if (!s) sets.push((s = { k: g.set, a: [] }));
        s.a.push(g);
      });

      const W = box.clientWidth || 500;
      const lw = W < 420 ? 126 : 154;
      const rh = 22;
      const sh = 25;
      let totalRows = 0;
      sets.forEach((s) => (totalRows += s.a.length));
      const Ht = 26 + sets.length * sh + totalRows * rh + 8;

      const svg = S("svg", {
        width: W,
        height: Ht,
        viewBox: `0 0 ${W} ${Ht}`,
        role: "img",
        "aria-label": "Dot plot of Democratic margin by demographic group"
      }, box);

      const lo = -100, hi = 100;
      const X = (v) => lw + ((v - lo) / (hi - lo)) * (W - lw - 48);

      [-100, -50, 0, 50, 100].forEach((v) => {
        S("line", { class: v === 0 ? "zero" : "gr", x1: X(v), x2: X(v), y1: 18, y2: Ht - 4 }, svg);
        S("text", { x: X(v), y: 12, "text-anchor": "middle", class: "ax-num" }, svg).textContent = v === 0 ? "Even" : (v > 0 ? "D+" : "R+") + Math.abs(v);
      });

      let y = 24;
      sets.forEach((s) => {
        S("text", {
          x: 0,
          y: y + 15,
          fill: "var(--ink)",
          "font-family": "var(--mono)",
          "font-weight": "600",
          "font-size": "10.5",
          "letter-spacing": "0.8"
        }, svg).textContent = s.k.toUpperCase();
        y += sh;

        s.a.forEach((g) => {
          const m = g.D - g.R;
          const cy = y + rh / 2 - 3;
          const gg = S("g", { style: "cursor:pointer" }, svg);
          S("rect", { x: 0, y: cy - rh / 2, width: W, height: rh, fill: "transparent" }, gg);
          S("text", { x: lw - 10, y: cy + 4, "text-anchor": "end", class: "lbl" }, gg).textContent = shortLabel(g.k, W < 420);

          const col = m >= 0 ? "D" : "R";
          S("line", { x1: X(0), x2: X(m), y1: cy, y2: cy, stroke: `var(--${col})`, "stroke-width": 2, opacity: 0.38 }, gg);

          const natG = !isUS ? natBenchByKey.get(`${g.set}|${g.k}`) : null;
          if (natG) {
            const natM = natG.D - natG.R;
            S("circle", { cx: X(natM), cy, r: 3.4, fill: "var(--bg)", stroke: "var(--mut)", "stroke-width": 1.4 }, gg);
          }

          S("circle", {
            cx: X(m),
            cy,
            r: 3 + Math.sqrt(Math.max(1, g.share)) * 0.92,
            fill: `var(--${col})`,
            stroke: "var(--bg)",
            "stroke-width": 1.5
          }, gg);

          S("text", {
            x: W - 2,
            y: cy + 4,
            "text-anchor": "end",
            "font-family": "var(--mono)",
            "font-size": "11",
            fill: `var(--${col})`
          }, gg).textContent = (m >= 0 ? "D+" : "R+") + Math.abs(m);

          bindTip(gg, () => {
            const dLbl = isUS ? "Democrat" : `${stObj.dem} (D)`;
            const rLbl = isUS ? "Republican" : `${stObj.rep} (R)`;
            const benchTxt = natG ? ` · National House: ${natG.D >= natG.R ? "D+" : "R+"}${Math.abs(natG.D - natG.R)}` : (g.shift24 ? ` · Shift vs. '24: ${g.shift24}` : "");
            return `
              <div class="h">${esc(g.k)}${isUS ? "" : ` · ${esc(STATE_NAMES[state.exitState])}`}</div>
              <div class="r"><span><i style="background:var(--D)"></i>${esc(dLbl)}</span><span class="w">${g.D}%</span></div>
              <div class="r"><span><i style="background:var(--R)"></i>${esc(rLbl)}</span><span class="w">${g.R}%</span></div>
              <div class="m">${g.share}% of voters${esc(benchTxt)}</div>
            `;
          });

          y += rh;
        });
      });
    }

    document.querySelectorAll("[data-exit-cat]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.exitCat = btn.dataset.exitCat;
        document.querySelectorAll("[data-exit-cat]").forEach((b) => {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        drawExitGroups();
      });
    });

    function drawExitIssues() {
      const box = document.getElementById("exit-issues-svg");
      if (!box) return;
      box.innerHTML = "";
      const is = data.exit_poll.issues;
      const W = box.clientWidth || 480;
      const lw = W < 420 ? 112 : 172;
      const rh = 34;
      const Ht = is.length * rh + 22;
      const svg = S("svg", { width: W, height: Ht, viewBox: `0 0 ${W} ${Ht}`, role: "img", "aria-label": "Most important issue share and House vote" }, box);

      const bw = (W - lw) * 0.28;
      const mx = lw + bw + 40;
      const mw = Math.max(76, W - mx - 6);

      S("text", { x: lw, y: 12 }, svg).textContent = "Share of voters";
      S("text", { x: mx, y: 12 }, svg).textContent = "Their vote, D vs R";

      is.forEach((s, i) => {
        const y = 20 + i * rh;
        const g = S("g", { style: "cursor:pointer" }, svg);
        S("rect", { x: 0, y, width: W, height: rh, fill: "transparent" }, g);
        S("text", { x: lw - 10, y: y + rh / 2 + 4, "text-anchor": "end", class: "lbl" }, g).textContent = shortLabel(s.k, W < 420);
        S("rect", { x: lw, y: y + 8, width: Math.max(2, (bw * s.share) / 40), height: rh - 16, rx: 3, fill: "var(--ink2)" }, g);
        S("text", { x: lw + (bw * s.share) / 40 + 5, y: y + rh / 2 + 4, class: "lbl", "font-family": "var(--mono)" }, g).textContent = `${s.share}%`;

        const tot = s.D + s.R;
        const dW = (mw * s.D) / tot;
        const rW = (mw * s.R) / tot;
        S("rect", { x: mx, y: y + 8, width: Math.max(0, dW - 1), height: rh - 16, fill: "var(--D)", rx: 2 }, g);
        S("rect", { x: mx + dW + 1, y: y + 8, width: Math.max(0, rW - 1), height: rh - 16, fill: "var(--R)", rx: 2 }, g);
        S("line", { x1: mx + mw / 2, x2: mx + mw / 2, y1: y + 4, y2: y + rh - 4, stroke: "var(--ink)", "stroke-width": 1.5 }, g);

        bindTip(g, () => `
          <div class="h">${esc(s.k)}</div>
          <div class="r"><span>Named as top issue</span><span class="w">${s.share}%</span></div>
          <div class="r"><span><i style="background:var(--D)"></i>Voted Democrat</span><span>${s.D}%</span></div>
          <div class="r"><span><i style="background:var(--R)"></i>Voted Republican</span><span>${s.R}%</span></div>
        `);
      });
    }

    function drawExitTrust() {
      const box = document.getElementById("exit-trust-svg");
      const list = data.exit_poll.party_trust || [];
      if (!box || !list.length) return;
      box.innerHTML = "";

      const W = box.clientWidth || 480;
      const lw = W < 420 ? 142 : 196;
      const rh = 28;
      const Ht = list.length * rh + 6;
      const svg = S("svg", { width: W, height: Ht, viewBox: `0 0 ${W} ${Ht}`, role: "img", "aria-label": "Party better able to handle each issue" }, box);
      const bw = W - lw - 4;

      list.forEach((item, i) => {
        const y = i * rh;
        const g = S("g", { style: "cursor:pointer" }, svg);
        S("rect", { x: 0, y, width: W, height: rh, fill: "transparent" }, g);
        S("text", { x: lw - 10, y: y + rh / 2 + 4, "text-anchor": "end", class: "lbl" }, g).textContent = shortLabel(item.k, W < 420);

        const t = item.D + item.neither + item.R;
        let curX = lw;
        [
          [item.D, "var(--D)", "#ffffff"],
          [item.neither, "var(--line2)", "var(--ink)"],
          [item.R, "var(--R)", "#ffffff"]
        ].forEach(([val, fill, txtCol]) => {
          const w = (bw * val) / t;
          S("rect", { x: curX, y: y + 6, width: Math.max(0, w - 2), height: rh - 12, fill, rx: 2 }, g);
          if (w > 26) {
            S("text", {
              x: curX + w / 2 - 1,
              y: y + rh / 2 + 4,
              "text-anchor": "middle",
              "font-size": "11",
              "font-family": "var(--mono)",
              fill: txtCol
            }, g).textContent = val;
          }
          curX += w;
        });

        bindTip(g, () => `
          <div class="h">${esc(item.k)}</div>
          <div class="r"><span><i style="background:var(--D)"></i>Democratic Party</span><span class="w">${item.D}%</span></div>
          <div class="r"><span>Neither</span><span>${item.neither}%</span></div>
          <div class="r"><span><i style="background:var(--R)"></i>Republican Party</span><span class="w">${item.R}%</span></div>
        `);
      });
    }

    /* ----------------------------------------------------------------------
       8. Statewide Ballot Measures (33 Measures)
       ---------------------------------------------------------------------- */
    function renderMeasures() {
      const box = document.getElementById("measures-container");
      if (!box) return;
      const filtered = data.measures.filter((m) => state.measureTopic === "all" || m.topic === state.measureTopic);
      const byTopic = {};
      filtered.forEach((m) => (byTopic[m.topic] = byTopic[m.topic] || []).push(m));

      box.innerHTML = Object.entries(byTopic).map(([topic, ms]) => `
        <div class="mtopic">${esc(topic)}</div>
        <table class="compact-table">
          <tbody>
            ${ms.map((m) => {
              const barCol = m.res === "passed" ? "var(--pass)" : m.res === "failed" ? "var(--fail)" : "var(--N)";
              return `
                <tr>
                  <td class="mono" style="inline-size:50px;font-size:12.5px"><b>${esc(m.st)}</b></td>
                  <td>${esc(m.desc)} <span style="color:var(--mut);font-size:12px">· ${esc(m.m)}</span></td>
                  <td class="meas-bar" style="inline-size:32%;min-inline-size:110px">
                    <div class="mbar"><i style="inset-inline-start:0;inline-size:${m.yes}%;background:${barCol}"></i><span class="tick"></span></div>
                  </td>
                  <td class="num" style="inline-size:56px">${m.yes.toFixed(1)}%</td>
                  <td style="inline-size:82px;text-align:end"><span class="res ${m.res}">${m.res === "uncalled" ? "counting" : m.res}</span></td>
                </tr>
              `;
            }).join("")}
          </tbody>
        </table>
      `).join("");
    }

    document.querySelectorAll("[data-measure-topic]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.measureTopic = btn.dataset.measureTopic;
        document.querySelectorAll("[data-measure-topic]").forEach((b) => {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        renderMeasures();
      });
    });
    renderMeasures();

    /* ----------------------------------------------------------------------
       9. Historical Midterms (1994–2026) & 2028 Electoral Map + Trifectas
       ---------------------------------------------------------------------- */
    function renderHistoryAnd2028() {
      const histEl = document.getElementById("history-grid");
      if (histEl && data.historical_midterms) {
        const fmtSigned = (n) => (n > 0 ? `+${n}` : `${n}`);
        histEl.innerHTML = `
          <div class="hist-row head">
            <span>Year</span><span>President</span><span class="hist-hide-sm" style="text-align:end">Net App.</span><span>House Seat Change</span><span style="text-align:end">Sen.</span><span class="hist-hide-sm" style="text-align:end">Gov.</span>
          </div>
          ${data.historical_midterms.map((r) => {
            const w = Math.min(100, (Math.abs(r.house_chg) / 65) * 100);
            const barCol = r.house_chg < 0 ? "var(--R)" : "var(--pass)";
            return `
              <div class="hist-row ${r.highlight ? "highlight" : ""}">
                <span style="font-family:var(--mono);font-weight:600">${r.year}${r.highlight ? "*" : ""}</span>
                <span>${esc(r.pres)}</span>
                <span class="hist-hide-sm" style="font-family:var(--mono);text-align:end;color:${r.net_app < 0 ? "var(--R)" : "var(--pass)"}">${fmtSigned(r.net_app)}</span>
                <div style="display:flex;align-items:center;gap:8px">
                  <div style="flex:1;block-size:11px;background:var(--alt);border-radius:2px;overflow:clip">
                    <div style="block-size:100%;inline-size:${w.toFixed(1)}%;background:${barCol}"></div>
                  </div>
                  <span style="font-family:var(--mono);min-inline-size:34px;text-align:end;font-weight:600">${fmtSigned(r.house_chg)}</span>
                </div>
                <span style="font-family:var(--mono);text-align:end;font-weight:600">${fmtSigned(r.sen_chg)}</span>
                <span class="hist-hide-sm" style="font-family:var(--mono);text-align:end">${fmtSigned(r.gov_chg)}</span>
              </div>
            `;
          }).join("")}
        `;
      }

      const evSvg = document.getElementById("ev2028-svg");
      if (evSvg) {
        const b1 = 226, b2 = 93, b3 = 78, b4 = 141;
        const W = 800;
        const px = (ev) => (ev / 538) * W;
        evSvg.innerHTML = `
          <rect x="0" y="18" width="${px(b1).toFixed(1)}" height="24" rx="2" fill="var(--D4)" />
          <rect x="${px(b1).toFixed(1)}" y="18" width="${px(b2).toFixed(1)}" height="24" fill="var(--D3)" />
          <rect x="${px(b1 + b2).toFixed(1)}" y="18" width="${px(b3).toFixed(1)}" height="24" fill="var(--D1)" />
          <rect x="${px(b1 + b2 + b3).toFixed(1)}" y="18" width="${px(b4).toFixed(1)}" height="24" rx="2" fill="var(--R)" />
          <line x1="${px(270).toFixed(1)}" y1="6" x2="${px(270).toFixed(1)}" y2="52" stroke="var(--ink)" stroke-width="2" />
          <text x="${px(270).toFixed(1)}" y="66" text-anchor="middle" font-family="var(--mono)" font-size="10.5" font-weight="600" fill="var(--ink)">270 TO WIN IN 2028</text>
          <text x="${(px(b1) / 2).toFixed(1)}" y="34" text-anchor="middle" font-family="var(--mono)" font-size="10.5" font-weight="600" fill="#fff">Harris '24 (226)</text>
          <text x="${(px(b1) + px(b2) / 2).toFixed(1)}" y="34" text-anchor="middle" font-family="var(--mono)" font-size="10" font-weight="600" fill="#fff">7 Swing States (93)</text>
          <text x="${(px(b1 + b2) + px(b3) / 2).toFixed(1)}" y="34" text-anchor="middle" font-family="var(--mono)" font-size="9.5" font-weight="600" fill="var(--ink)">TX/OH/SC/IA/KS (78)</text>
          <text x="${(px(b1 + b2 + b3) + px(b4) / 2).toFixed(1)}" y="34" text-anchor="middle" font-family="var(--mono)" font-size="10.5" font-weight="600" fill="#fff">GOP Held (141)</text>
        `;
      }

      const triEl = document.getElementById("trifecta-grid");
      if (triEl && data.trifecta_shifts) {
        triEl.innerHTML = data.trifecta_shifts.map((t) => {
          const broken = t.change.includes("broken");
          return `
            <article class="tri-card ${broken ? "broken" : ""}">
              <div style="display:flex;justify-content:space-between;align-items:center;gap:6px;margin-block-end:4px">
                <strong style="font-size:13.5px;color:var(--ink)">${esc(t.name)} (${t.ev} EV)</strong>
                <span class="badge ${broken ? "badge-flip" : "badge-dem"}">${esc(t.change)}</span>
              </div>
              <p style="font-size:12.5px;color:var(--mut);margin:0;line-height:1.42">${esc(t.detail)}</p>
            </article>
          `;
        }).join("");
      }
    }
    renderHistoryAnd2028();

    /* ----------------------------------------------------------------------
       10. Complete 71-Contest Reference Table
       ---------------------------------------------------------------------- */
    const tbodyEl = document.getElementById("ledger-tbody");
    const captionEl = document.getElementById("ledger-caption");
    const searchEl = document.getElementById("ledger-search");

    function renderLedgerTable() {
      if (!tbodyEl || !captionEl) return;
      const raw =
        state.tableChamber === "senate"
          ? data.senate.races.map((r) => ({ ...r, officeLabel: "Senate" }))
          : state.tableChamber === "governors"
            ? data.governors.races.map((r) => ({ ...r, officeLabel: "Governor" }))
            : [
                ...data.senate.races.map((r) => ({ ...r, officeLabel: "Senate" })),
                ...data.governors.races.map((r) => ({ ...r, officeLabel: "Governor" }))
              ];

      const q = state.tableQuery.trim().toLowerCase();
      const rows = raw.filter((r) => {
        if (state.tableFilter === "flips" && !r.flip) return false;
        if (state.tableFilter === "uncalled" && r.called) return false;
        if (state.tableFilter === "close" && Math.abs(r.margin) >= 10) return false;
        if (q) {
          const hay = `${r.name} ${r.st} ${r.officeLabel} ${r.win} ${r.ru} ${r.note}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      }).sort((a, b) => a.name.localeCompare(b.name) || a.officeLabel.localeCompare(b.officeLabel));

      const titlePrefix =
        state.tableChamber === "senate" ? "2026 U.S. Senate" :
        state.tableChamber === "governors" ? "2026 Governors" : "All 2026 Statewide Contests";
      captionEl.textContent = `${titlePrefix} · ${rows.length} of ${raw.length} contests`;

      tbodyEl.innerHTML = rows.map((r) => {
        const statusBadge = !r.called
          ? `<span class="badge badge-uncalled">${ICONS.clock} Uncalled</span>`
          : r.flip
            ? `<span class="badge badge-flip">${ICONS.star} ${r.wp === "D" ? "Dem" : "GOP"} Flip</span>`
            : `<span class="badge ${r.wp === "D" ? "badge-dem" : "badge-rep"}">${r.wp === "D" ? "Dem" : "GOP"} Hold</span>`;
        const mCol = !r.called ? "var(--mut)" : r.margin >= 0 ? "var(--D)" : "var(--R)";
        const stCell = state.tableChamber === "both" ? `${esc(r.name)} · <span style="font-weight:400;color:var(--mut)">${r.officeLabel}</span>` : esc(r.name);
        return `
          <tr>
            <th scope="row">${stCell}</th>
            <td>${statusBadge}</td>
            <td><span class="pill ${r.wp}">${r.wp}</span> <strong>${esc(r.win)}</strong> · <span class="mono" style="font-size:12.5px">${r.wpct.toFixed(1)}%</span></td>
            <td><span class="pill ${r.rp === "I" ? "I" : r.rp}">${r.rp}</span> ${esc(r.ru)} · <span class="mono" style="font-size:12.5px">${r.rpct !== null ? r.rpct.toFixed(1) + "%" : "n/a"}</span></td>
            <td style="font-family:var(--mono);font-weight:600;color:${mCol}">${fmtMargin(r.margin, r.called)}</td>
            <td style="font-family:var(--mono);color:var(--mut)">${fmtMargin(r.pres24, true)}</td>
            <td style="color:var(--mut);max-inline-size:34ch">${esc(r.note)}</td>
          </tr>
        `;
      }).join("");
    }

    document.querySelectorAll("[data-table-chamber]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.tableChamber = btn.dataset.tableChamber;
        document.querySelectorAll("[data-table-chamber]").forEach((b) => {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        renderLedgerTable();
      });
    });

    document.querySelectorAll("[data-table-filter]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.tableFilter = btn.dataset.tableFilter;
        document.querySelectorAll("[data-table-filter]").forEach((b) => {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        renderLedgerTable();
      });
    });

    if (searchEl) {
      searchEl.addEventListener("input", () => {
        state.tableQuery = searchEl.value;
        renderLedgerTable();
      });
    }
    renderLedgerTable();

    /* ----------------------------------------------------------------------
       Width-Responsive SVG Redraw Hook (Window Resize & Maximize Dialog)
       ---------------------------------------------------------------------- */
    function redrawResponsiveCharts() {
      drawArrowSwing();
      drawHexMap();
      drawDotMap(false);
      renderSwingScatter();
      drawHouseScatter();
      drawExitGroups();
      drawExitIssues();
      drawExitTrust();
    }

    redrawResponsiveCharts();
    initMaximizeBoxes(redrawResponsiveCharts);
    initThemeControls(() => drawDotMap(false));
    bindStaticTips();

    let resizeTimer;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(redrawResponsiveCharts, 120);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    loadData().then(initApp).catch((err) => console.error("Failed to initialize election briefing:", err));
  });
})();
