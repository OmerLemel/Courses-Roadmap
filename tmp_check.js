const fs = require('fs');
const lines = fs.readFileSync('index.html', 'utf8').split('\n');
lines.forEach((l, i) => {
  if (/id="search"|clearSearch|id="sug"|pointerdown|pointermove|endDrag|drag=null,justDragged|sideClose.*onclick/.test(l))
    console.log((i + 1) + '|' + JSON.stringify(l).slice(0, 300));
});
