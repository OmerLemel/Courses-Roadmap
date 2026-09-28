const fs = require('fs');
const lines = fs.readFileSync('index.html', 'utf8').split('\n');
lines.forEach((l, i) => { if (/hleft/.test(l)) console.log((i + 1) + '|' + JSON.stringify(l)); });
