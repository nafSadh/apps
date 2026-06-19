/*
 * perf_log.js — per-match simulation performance log.
 *
 * Re-derives, for every played WC2026 match, how each of the 8 prediction models
 * called it (vs the actual result), straight from the app's own engine in
 * ../index.html and the locked scores in ../data.json — so the log can never drift
 * from what the app shows. Writes a human-readable scripts/perf-log.md and a
 * machine-readable scripts/perf-log.json.
 *
 * Run after locking new results:
 *     python3 update.py --results new.csv --sync-embed   # lock + sync
 *     node perf_log.js                                    # refresh the log
 *
 * Scoring matches the in-app "Simulation accuracy" tab: a model picks a WIN when it
 * favours a side >60%, otherwise a DRAW (40–60%); the outcome is right (✓) or wrong (✗).
 */
const fs = require("fs");
const path = require("path");
const HERE = __dirname, ROOT = path.join(HERE, "..");

// ---- minimal DOM/window stub so the app script evals headlessly ----
const els = {};
function fake(id) {
  if (!els[id]) els[id] = new Proxy({
    _h: "", style: {}, classList: { add() {}, remove() {}, toggle() {} }, dataset: {}, value: "all",
    addEventListener() {}, appendChild() {}, insertBefore() {}, setAttribute() {},
    querySelector: () => null, querySelectorAll: () => [], getBoundingClientRect: () => ({}),
    insertAdjacentHTML() {}, onclick: null, disabled: false, textContent: "",
    set innerHTML(v) { this._h = v; }, get innerHTML() { return this._h; }
  }, { get(t, p) { return p in t ? t[p] : fake(id + "x"); }, set(t, p, v) { t[p] = v; return true; } });
  return els[id];
}
global.document = { documentElement: { getAttribute: () => null, setAttribute() {} }, getElementById: id => fake(id), createElement: () => fake("c"), createElementNS: () => fake("s"), addEventListener() {}, querySelector: () => null, querySelectorAll: () => [] };
global.location = { hash: "" }; global.history = { replaceState() {} };
global.window = { addEventListener() {}, matchMedia: () => ({ matches: false, addEventListener() {} }), innerWidth: 1400, scrollTo() {}, location: global.location, history: global.history };
global.setTimeout = () => {}; global.localStorage = { getItem: () => null, setItem() {} }; global.fetch = () => Promise.reject(0);

const html = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
const js = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).sort((a, b) => b.length - a.length)[0];
eval(js + "\nglobalThis.__ = { backtest, nm, MSHORT, METHOD_NAME };");
const A = globalThis.__;
const meta = JSON.parse(fs.readFileSync(path.join(ROOT, "data.json"), "utf8")).meta;

const { rows, tally, models } = A.backtest();
const acc = t => (t.ok + t.miss) ? t.ok / (t.ok + t.miss) : 0;
const order = models.slice().sort((a, b) => acc(tally[b]) - acc(tally[a]));
const mark = res => res === "ok" ? "✓" : "✗";
const outc = a => a === "H" ? "home win" : a === "A" ? "away win" : "draw";

// ---- markdown ----
let md = `# WC2026 — per-match simulation performance log\n\n`;
md += `_Auto-generated from \`data.json\` by \`scripts/perf_log.js\` · as of **${meta.asOf}** · **${rows.length}** played matches._\n\n`;
md += `A model **picks a win** when it favours a side **>60%**, otherwise a **draw** (40–60%); ✓ = right outcome, ✗ = wrong.\n\n`;
md += `## Leaderboard\n\n| Model | Hit rate | ✓ | ✗ |\n|---|--:|--:|--:|\n`;
order.forEach(m => { const t = tally[m]; md += `| ${A.METHOD_NAME[m]} | ${(acc(t) * 100).toFixed(0)}% | ${t.ok} | ${t.miss} |\n`; });
md += `\n## Per match\n\n| # | Match | Result | ${order.map(m => A.MSHORT[m]).join(" | ")} |\n`;
md += `|---|---|---|${order.map(() => ":-:").join("|")}|\n`;
rows.forEach(r => {
  md += `| M${r.no} | ${A.nm(r.f.home)} – ${A.nm(r.f.away)} | ${r.r[0]}–${r.r[1]}${r.actual === "D" ? " (draw)" : ""} | ${order.map(m => mark(r.cells[m].res)).join(" | ")} |\n`;
});

// ---- json ----
const json = {
  asOf: meta.asOf, version: meta.version, played: rows.length,
  scoring: "pick win >60% / draw 40-60%, vs actual outcome",
  leaderboard: order.map(m => ({ key: m, model: A.METHOD_NAME[m], ok: tally[m].ok, miss: tally[m].miss, hitRate: +acc(tally[m]).toFixed(3) })),
  matches: rows.map(r => ({
    no: r.no, home: A.nm(r.f.home), away: A.nm(r.f.away), score: r.r, actual: outc(r.actual),
    models: Object.fromEntries(order.map(m => [m, { winProb: +r.cells[m].p.toFixed(3), pick: r.cells[m].pick, correct: r.cells[m].res === "ok" }]))
  }))
};

fs.writeFileSync(path.join(HERE, "perf-log.md"), md);
fs.writeFileSync(path.join(HERE, "perf-log.json"), JSON.stringify(json, null, 2) + "\n");
console.log(`wrote perf-log.md + perf-log.json — ${rows.length} matches, leader: ${A.METHOD_NAME[order[0]]} ${(acc(tally[order[0]]) * 100).toFixed(0)}%`);
