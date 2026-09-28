const fs = require('fs');
const p = 'index.html';
let src = fs.readFileSync(p, 'utf8');
const btnStart = '<button id="barTog"';
const first = src.indexOf(btnStart);
const second = src.indexOf(btnStart, first + 1);
console.log('first at', first, 'second at', second);
if (second < 0) { console.log('only one button, nothing to do'); process.exit(0); }
// remove the SECOND occurrence (the stale one inside .hleft): find its matching </button>
const btnEnd = src.indexOf('</button>', second) + '</button>'.length;
console.log('removing:', JSON.stringify(src.slice(second - 40, btnEnd + 20)));
src = src.slice(0, second) + src.slice(btnEnd);
fs.writeFileSync(p, src);
console.log('done, barTog count now:', (src.match(/id="barTog"/g) || []).length);
