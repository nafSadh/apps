// Engine + level-bank checks.  node games/c-queens/scripts/test.js
// Verifies every shipped board (unique solution, contiguous regions, solvable by
// pure logic, stored solution and tier correct) and exercises the generator.
const fs = require('fs');
const path = require('path');
const E = require('./engine-from-page.js');

let fails = 0;
const ok = (cond, msg) => { if (!cond) { console.log('  FAIL: ' + msg); fails++; } };

function decode(e) {
  const N = e.N, reg = [];
  for (let r = 0; r < N; r++) { reg.push([]); for (let c = 0; c < N; c++) reg[r].push(parseInt(e.r[r * N + c], 36)); }
  return { N, reg, solution: e.s, tier: e.t, given: e.g || [] };
}

function checkPuzzle(p, tag) {
  const { N, reg, solution } = p;
  const given = p.given || [];
  ok(solution.length === N, tag + ': solution length');
  for (const [r, c] of given) ok(solution[r] === c, tag + ': pre-filled queen at row ' + r + ' is on the solution');
  ok(new Set(solution).size === N, tag + ': columns distinct');
  for (let r = 1; r < N; r++) ok(Math.abs(solution[r] - solution[r - 1]) >= 2, tag + ': rows ' + r + ' touch');
  ok(new Set(solution.map((c, r) => reg[r][c])).size === N, tag + ': one queen per region');
  const counts = new Array(N).fill(0);
  for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) { ok(reg[r][c] >= 0 && reg[r][c] < N, tag + ': region id in range'); counts[reg[r][c]]++; }
  for (let g = 0; g < N; g++) {
    ok(counts[g] >= 1, tag + ': region ' + g + ' non-empty');
    let start = null;
    for (let r = 0; r < N && !start; r++) for (let c = 0; c < N; c++) if (reg[r][c] === g) { start = [r, c]; break; }
    const seen = new Set([start[0] * N + start[1]]), stack = [start];
    while (stack.length) {
      const [r, c] = stack.pop();
      for (const [dr, dc] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nr = r + dr, nc = c + dc, k = nr * N + nc;
        if (nr < 0 || nc < 0 || nr >= N || nc >= N || reg[nr][nc] !== g || seen.has(k)) continue;
        seen.add(k); stack.push([nr, nc]);
      }
    }
    ok(seen.size === counts[g], tag + ': region ' + g + ' contiguous');
  }
  ok(E.countSolutions(N, reg, 5, given) === 1, tag + ': unique solution' + (given.length ? ' given the pre-filled queens' : ''));
  ok(JSON.stringify(E.solveOnce(N, reg, given)) === JSON.stringify(solution), tag + ': solver matches stored solution');
  const L = E.logicSolve(N, reg, { given });
  ok(L.solved, tag + ': solvable by logic alone');
  if (L.solved) for (let r = 0; r < N; r++) ok(L.queen[r][solution[r]], tag + ': logic solver row ' + r + ' matches');
  ok(L.tier === p.tier, tag + ': stored tier ' + p.tier + ' matches solver tier ' + L.tier);
}

console.log('--- placement sanity ---');
for (let N = 4; N <= 12; N++) ok(E.randomPlacement(N, E.mulberry32(N * 7919)) !== null, 'placement exists for N=' + N);
ok(E.randomPlacement(3, E.mulberry32(1)) === null, 'N=3 correctly has no placement');

console.log('--- generator, both styles ---');
for (const [N, t, style] of [[5, 2, 'balanced'], [6, 2, 'islands'], [7, 2, 'balanced'], [8, 2, 'islands']]) {
  const T = Date.now();
  const p = E.generate(N, t, E.hashSeed('test-' + N + t + style), 40, style);
  ok(p !== null, 'generated ' + style + ' N=' + N + ' tier ' + t);
  if (p) { ok(p.tier === t, style + ' N=' + N + ' hit tier ' + t + ' (got ' + p.tier + ')'); checkPuzzle(p, style + N); }
  console.log('  ' + style + ' N=' + N + ' tier ' + t + ': ' + (Date.now() - T) + 'ms');
}
ok(JSON.stringify(E.generate(7, 2, 123, 40, 'islands')) === JSON.stringify(E.generate(7, 2, 123, 40, 'islands')), 'generation is deterministic');
{
  const T = Date.now();
  const p = E.generate(11, 2, E.hashSeed('test-given'), 40, 'islands', 1);
  ok(p !== null && p.given.length === 1, 'generated 11×11 with one pre-filled queen');
  if (p) { checkPuzzle(p, 'given11'); ok(E.countSolutions(p.N, p.reg, 3) >= 1, 'board is valid without the given too'); }
  console.log('  11×11 +1 given: ' + (Date.now() - T) + 'ms');
}

console.log('--- hint path ---');
{
  const p = E.generate(8, 2, E.hashSeed('hint'), 40, 'islands');
  const given = [[0, p.solution[0]], [1, p.solution[1]]];
  const L = E.logicSolve(p.N, p.reg, { given, steps: true });
  ok(L.solved, 'solves from a partial position');
  const first = L.steps.find((s) => s.tier > 0);
  ok(!!first && first.text.length > 5, 'hint text present');
  console.log('  sample hint: ' + (first ? first.text : '(none)'));
  let bad = null;
  for (let c = 0; c < p.N && !bad; c++) if (c !== p.solution[0]) bad = [0, c];
  ok(!E.logicSolve(p.N, p.reg, { given: [bad] }).solved, 'a wrong queen never leads to a solution');
}

console.log('--- shipped level bank ---');
const bankPath = path.join(__dirname, '..', 'levels.js');
if (fs.existsSync(bankPath)) {
  const bank = new Function('window', fs.readFileSync(bankPath, 'utf8') + 'return window.CNQ_LEVELS;')({});
  ok(bank.ladder.length > 0 && bank.daily.length > 0, 'bank non-empty');
  ok(bank.ladder.every((e) => e.r.length === e.N * e.N), 'every region string is N×N');
  const T = Date.now();
  bank.ladder.forEach((e, i) => checkPuzzle(decode(e), 'level ' + (i + 1)));
  bank.daily.forEach((e, i) => checkPuzzle(decode(e), 'daily ' + i));
  const tiers = {}, sizes = {};
  bank.ladder.forEach((e) => { tiers[e.t] = (tiers[e.t] || 0) + 1; sizes[e.N] = (sizes[e.N] || 0) + 1; });
  console.log('  ' + bank.ladder.length + ' ladder + ' + bank.daily.length + ' daily verified in ' + (Date.now() - T) + 'ms');
  console.log('  ladder tiers ' + JSON.stringify(tiers) + ', sizes ' + JSON.stringify(sizes));
} else console.log('  (no levels.js yet — run gen.js)');

console.log(fails === 0 ? '\nALL PASS' : '\n' + fails + ' FAILURES');
process.exit(fails ? 1 : 0);
