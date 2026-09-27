# TAU Course Roadmap (localhost)

Hebrew-only, RTL, top-down course dependency map for Exact Sciences programs.

## Data sources (the 4 URLs only)
- Dual Math+CS 2025: tcid=7612 shana=2025
- Dual Math+CS 2026: tcid=7612 shana=2026
- CS + AI minor 2026: tcid=8865 shana=2026
- Theoretical Math 2026: tcid=7606 shana=2026

Fetched from GraphQL `https://tochniot.tau.ac.il/graphql`:
- `results(apiUrl:"ydtochnit", filters:{safa,shana,tcid,tab})` -> program tree (rama/kurs)
- `results(apiUrl:"yddrishot", filters:{...,kursid,tcid})` -> prereq text, parsed codes `(XXXX-XXXX)`

## Regenerate data
```
python fetch_all.py
python fetch_prereq.py
python build_data.py
```

## Run (localhost)
```
start_server.bat
```
then open http://localhost:8000

## App
- `index.html` — UI (no build step, no npm)
- `data.json` — 279 courses, 238 edges
- Colors: חובה gray #4B5563, ליבה blue #2563EB, בחירה green #16A34A, סמינר purple #9333EA, סדנה orange #EA580C, שאר רוח yellow #CA8A04
- Edges: solid = קדם (before), dashed = מקביל (parallel)
- Node shows full id e.g. 0368-2160; search matches name or id digits
- Filters: single program select, year 2025/2026, type chips (click to show/hide)
- Layout: always recommended view (ordered by official semester within each year)
