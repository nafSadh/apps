// Loads the puzzle engine straight out of ../index.html so the offline scripts
// exercise exactly the code the page ships — there is no second copy.
const fs = require('fs');
const path = require('path');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const start = html.indexOf('/* ===== ENGINE START =====');
const end = html.indexOf('/* ===== ENGINE END ===== */');
if (start < 0 || end < 0) throw new Error('engine markers not found in index.html');
const src = html.slice(start, end);
module.exports = new Function(src + `
  return { mulberry32, hashSeed, attacks, randomPlacement, growRegions, growIslands, sculptRegions,
           countSolutions, solveOnce, logicSolve, generate, colorName, DIFFS };
`)();
