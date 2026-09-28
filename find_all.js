const fs = require('fs');
const src = fs.readFileSync('index.html', 'utf8');
const lines = src.split('\n');
lines.forEach((l, i) => {
  if (/<header>|<\/header>|<h1>|hleft|barTog.*title|clearSearch.*input|si\.addEventListener|pointerdown|const drag|window\.addEventListener\('pointermove'|window\.addEventListener\('pointerup'|endDrag/.test(l))
    console.log((i + 1) + '|' + JSON.stringify(l).slice(0, 260));
});
