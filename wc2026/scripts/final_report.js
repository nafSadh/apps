// Final-tournament simulation performance report for wc2026.
// Reuses the perf_log.js trick: stub the DOM, eval the app's <script>, call its engine directly.
const fs = require("fs"), path = require("path");
const ROOT = "/Users/nafsadh/src/apps/wc2026";

const els = {};
function fake(id) {
  if (els[id]) return els[id];
  els[id] = new Proxy({
    _h: "", style: {}, classList: { add() {}, remove() {}, toggle() {} }, dataset: {}, value: "all",
    addEventListener() {}, appendChild() {}, insertBefore() {}, setAttribute() {},
    querySelector: () => null, querySelectorAll: () => [], getBoundingClientRect: () => ({}),
    insertAdjacentHTML() {}, onclick: null, disabled: false, textContent: "",
    set innerHTML(v) { this._h = v; }, get innerHTML() { return this._h; }
  }, { get(t, p) { return p in t ? t[p] : fake(id + "x"); }, set(t, p, v) { t[p] = v; return true; } });
  return els[id];
}
global.document = { documentElement: { getAttribute: () => null, setAttribute() {} }, getElementById: id => fake(id), createElement: () => fake("c"), createElementNS: () => fake("s"), addEventListener() {}, querySelector: () => null, querySelectorAll: () => [] };
global.location = { hash: "", search: "" }; global.history = { replaceState() {} };
global.window = { addEventListener() {}, matchMedia: () => ({ matches: false, addEventListener() {} }), innerWidth: 1400, scrollTo() {}, location: global.location, history: global.history };
global.setTimeout = () => {}; global.setInterval = () => {}; global.clearTimeout = () => {}; global.clearInterval = () => {}; global.localStorage = { getItem: () => null, setItem() {} }; global.fetch = () => Promise.reject(0);

const html = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
const js = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).sort((a, b) => b.length - a.length)[0];
eval(js + `
globalThis.__ = (function(){
  function prepKO(){ state.h2hWin="all"; state.formWin="5"; state.squadWin="value";
    state.res=Object.assign({},LOCKED); STATS=computeStats(); PGZ=zscores(potGoalsRaw()); WCFZ=zscores(wcFormRaw(new Set())); }
  function playout(m){ prepKO(); state.method=m; const w={};
    for(const no of KO_ORDER){ if(no===103) continue;
      const p = no<=88 ? parts(no) : [w[FEED[no][0]], w[FEED[no][1]]];
      if(!p[0]||!p[1]) return null;
      w[no] = modelProb(p[0],p[1])>=0.5 ? p[0] : p[1]; }
    return { champion:w[104], final:[w[101],w[102]] }; }
  return { backtest, MSHORT, METHOD_NAME, CONS_METHODS, nm, playout, kowin:()=>KOWIN, T };
})();`);
const A = globalThis.__;
const meta = JSON.parse(fs.readFileSync(path.join(ROOT, "data.json"), "utf8")).meta;

const { rows, tally, models } = A.backtest();
const acc = t => (t.ok + t.miss) ? t.ok / (t.ok + t.miss) : 0;
const pct = x => (100 * x).toFixed(0) + "%";
const order = models.slice().sort((a, b) => acc(tally[b]) - acc(tally[a]));
const flag = c => (A.T[c] && A.T[c][1]) || c;
const name = c => A.nm(c);

// per-stage split
const stageOf = r => !r.ko ? "Group" : (r.f.round === "SF" || r.f.round === "3rd" || r.f.round === "Final") ? "Semis+Finals" : r.f.round;
const STAGES = ["Group", "R32", "R16", "QF", "Semis+Finals"];
const byStage = {}; models.forEach(m => byStage[m] = Object.fromEntries(STAGES.map(s => [s, { ok: 0, miss: 0 }])));
rows.forEach(r => { const s = stageOf(r); models.forEach(m => byStage[m][s][r.cells[m].res === "ok" ? "ok" : "miss"]++); });

// champion calls (favourite-advance playout over the real KO field, pre-KO form)
const calls = {};
order.forEach(m => { calls[m] = A.playout(m); });
const CHAMP = A.kowin()[104], FINALISTS = [A.kowin()[101], A.kowin()[102]].sort();

// consensus per row + misses
const withCons = rows.map(r => {
  let s = 0; A.CONS_METHODS.forEach(m => s += r.cells[m].p); const avg = s / A.CONS_METHODS.length;
  const pick = avg > 0.6 ? "H" : avg < 0.4 ? "A" : "D";
  const conf = pick === "H" ? avg : pick === "A" ? 1 - avg : Math.max(avg, 1 - avg);
  const missCount = models.filter(m => r.cells[m].res === "miss").length;
  return { ...r, consPick: pick, consConf: conf, consMiss: pick !== r.actual, missCount };
});
const misses = withCons.filter(r => r.consMiss).sort((a, b) => b.consConf - a.consConf);
const shocks = withCons.filter(r => r.missCount >= 9).sort((a, b) => b.missCount - a.missCount || b.consConf - a.consConf);
const gameStr = r => { const pen = r.pens ? ` (${r.pens[0]}–${r.pens[1]} pens)` : "";
  return `${flag(r.f.home)} ${name(r.f.home)} ${r.r[0]}–${r.r[1]}${pen} ${name(r.f.away)} ${flag(r.f.away)}`; };
const roundStr = r => r.ko ? r.f.round : "Group";

// ---- markdown ----
let md = `# WC2026 — final simulation report\n\n`;
md += `**🇪🇸 Spain are world champions** — 1–0 over Argentina at MetLife Stadium, Jul 19. `;
md += `This is the final scorecard for every prediction model in [sadh.app/wc2026](https://sadh.app/wc2026), `;
md += `scored across all **${rows.length} matches** (group games by outcome incl. draws; knockouts by who advanced). `;
md += `Walk-forward throughout — every call uses only games played before it. Data as of **${meta.asOf}**.\n\n`;

md += `## Model leaderboard — all ${rows.length} matches\n\n`;
md += `| # | Model | ✓ | ✗ | Hit rate |\n|--:|---|--:|--:|--:|\n`;
order.forEach((m, i) => { const t = tally[m];
  md += `| ${i + 1} | ${A.METHOD_NAME[m]} | ${t.ok} | ${t.miss} | **${pct(acc(t))}** |\n`; });

md += `\n## Accuracy by stage\n\n`;
md += `| Model | Group (72) | R32 (16) | R16 (8) | QF (4) | SF+3rd+F (4) |\n|---|--:|--:|--:|--:|--:|\n`;
order.forEach(m => {
  md += `| ${A.METHOD_NAME[m]} | ` + STAGES.map(s => { const t = byStage[m][s]; return pct(acc(t)); }).join(" | ") + " |\n"; });

md += `\n## Who called the champion?\n\n`;
md += `Each model's bracket, played out favourite-advances from the real Round-of-32 field:\n\n`;
md += `| Model | Predicted final | Predicted champion | Verdict |\n|---|---|---|---|\n`;
order.forEach(m => { const c = calls[m]; if (!c) return;
  const fin = c.final.map(x => `${flag(x)} ${name(x)}`).join(" v ");
  const exactFinal = c.final.slice().sort().join() === FINALISTS.join();
  const v = c.champion === CHAMP ? (exactFinal ? "🎯 exact final **and** champion" : "🏆 champion right") :
            exactFinal ? "◐ exact final, wrong winner" :
            c.final.includes(CHAMP) ? "◔ champion in predicted final" : "✗";
  md += `| ${A.METHOD_NAME[m]} | ${fin} | ${flag(c.champion)} ${name(c.champion)} | ${v} |\n`; });

md += `\n## Biggest consensus misses\n\n`;
md += `Games the 8-model consensus was most confident about — and got wrong:\n\n`;
misses.slice(0, 6).forEach(r => {
  md += `- **${gameStr(r)}** _(${roundStr(r)})_ — consensus ${pct(r.consConf)} the other way; ${r.missCount}/${models.length} models missed\n`; });

md += `\n## Shocks of the tournament\n\n`;
md += `Matches where at least 9 of the ${models.length} models were wrong:\n\n`;
if (!shocks.length) md += `_None — no result blindsided the whole panel._\n`;
shocks.forEach(r => { md += `- **${gameStr(r)}** _(${roundStr(r)})_ — ${r.missCount}/${models.length} models wrong\n`; });

md += `\n---\n_Method: >60% = model predicts that side to win, 40–60% = predicts a draw (group only; knockout ties always pick a side). `;
md += `Generated by \`scripts/final_report\` from the app's own engine — same code that powers the Simulation accuracy tab._\n`;

fs.writeFileSync(path.join(ROOT, "final-report.md"), md);
console.log(md);
