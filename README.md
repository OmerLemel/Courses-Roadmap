# Courses Roadmap — מפת דרכים לקורסים

Live site: **https://omerlemel.github.io/Courses-Roadmap/**

An interactive, top-down prerequisite roadmap for Tel Aviv University exact-sciences
programs (mathematics, computer science). Pick a program and year, and explore which
courses to take, in what order, and what depends on what.

Built for students planning their degree — Hebrew UI, works on desktop and mobile
browsers. No build step, no backend: just static files.

## Features

- **Programs & years** — 4 programs (dual Math+CS, CS+AI track, theoretical Math,
  single-major CS), each with its available yedion years (2025 and/or 2026).
  Data-driven: program buttons and year buttons are generated from the dataset.
- **Dependency graph** — solid orange arrows = prerequisite (must take before),
  dashed blue arrows = co-requirement (can take in parallel). Faint by default;
  clicking a course highlights only its incoming arrows.
- **Course types by color** — חובה (mandatory), ליבה (core), בחירה (elective),
  סמינר (seminar), סדנה (workshop), שאר רוח (general). Click chips to show/hide.
- **או / וגם logic** — prerequisites parsed from the yedion wording, shown grouped
  in the detail panel exactly like TAU's own requirement modal.
- **Search** by name or course number (e.g. `2160` or `0368-2160`).
- **Year/semester layout** — courses placed in שנה א׳/ב׳/ג׳ bands and semester
  sub-sections following the recommended program; chain lanes keep
  prerequisite sequences vertical.
- **Course detail panel** — type, credits, placement, full prerequisite groups with
  names + IDs (red = external course with no box on the map), follow-up courses,
  and links back to the official yedion pages.
- **Card density** — דחוס (compact) / מרווח (spacious), remembered.
- **Dark mode** — toggle in the תצוגה panel, remembered.
- **Pan & zoom** — drag to pan, mouse-wheel to scroll, Ctrl+wheel to zoom,
  double-click to zoom, toolbar with percentage and reset. View stays fenced in.
- **Everything persists** — filters, program, year, density, theme, and sound
  settings survive reloads (localStorage).
- **Overrides** — `overrides.json` holds hand-curated fixes where the teaching
  schedule beats the yedion tree (e.g. a course taught in semester א׳ but filed
  without one). One line per course.
- **Cat break** — a paw button with a random cat picture and a real meow.
  Because roadmap planning deserves joy.

## Project layout

| File | What it is |
|---|---|
| `index.html` | The entire app (markup + CSS + JS, no framework, no build) |
| `data.json` | Generated dataset: programs, courses, edges, external names |
| `prog_<TCID>_<SHANA>.json` | Raw TAU API responses, one per program/year (source of truth) |
| `prereqs.json` | Per-course prerequisite details from TAU (`pre`/`par` codes + raw text) |
| `overrides.json` | Hand-curated semester fixes (see above) |
| `fetch_program.py` | Pulls a program tree + missing prereqs from TAU (see updating) |
| `rebuild_data.py` | Builds `data.json` from the raw files + prereqs + overrides |
| `build_logic.py` | Legacy helper (logic now folded into `rebuild_data.py`) |
| `meow.ogg` | Cat sound (Wikimedia Commons, CC BY-SA) |
| `start_server.bat` | Local dev server (`http://localhost:8000`) |

## Data sources

All course data comes from Tel Aviv University's public yedion API:

- Program trees: `POST https://tochniot.tau.ac.il/graphql`
  `results(apiUrl: "ydtochnit", filters: {safa, shana, tcid, tab})`
- Prerequisite details: same endpoint with
  `results(apiUrl: "yddrishot", filters: {..., kursid, tcid})`

| Program (ID) | tcid | Years in dataset |
|---|---|---|
| Dual Math + CS (דו-חוגי) | 7612 | 2025, 2026 |
| CS + AI track | 8865 | 2026 only (program is new; TAU has no 2025 data) |
| Theoretical Math (חד-חוגי) | 7606 | 2025, 2026 |
| Single-major CS (חד-חוגי) | 7583 | 2025, 2026 |

`data.json` shape (generated, don't hand-edit): `programs[]` (id, name,
per-year tcids + yedion URLs), `courses[]` (id like `0368-2160`, names,
credits, per-program/year `{type, year, sem, rama}`, `reqPre`/`reqCo` logic
groups), `edges[]` (`{from, to, kind: pre|co}`), `extNames` (names of
referenced courses outside the dataset).

## Updating for a new yedion year (maintenance)

When TAU publishes a new year (or a curriculum changes):

1. **Fetch** the program tree, e.g. `python fetch_program.py 7612 2027`
   (use `--skip-prereqs` to skip the prerequisite pass). It writes
   `prog_<TCID>_<SHANA>.json` and tops up `prereqs.json` with unseen courses.
   New programs need one entry in `rebuild_data.py`'s `programs`/`filemap`
   tables (id, Hebrew name, tcids, yedion URLs) — the site buttons pick it up
   automatically.
2. **Rebuild**: `python rebuild_data.py` → regenerates `data.json`.
3. **Sanity-check** the printed counts (courses/edges per program-year should
   look plausible; investigate `unknown course` override warnings).
4. **Test locally** (`start_server.bat`, open `http://localhost:8000`):
   new year button appears, map renders, spot-check a moved course.
5. **Commit + push** — GitHub Pages redeploys by itself in ~1–2 minutes.

## Local development

Amounts to serving static files (browsers block `fetch()` on `file://`):

- Windows: double-click `start_server.bat`, open `http://localhost:8000`
- Anything else: `python -m http.server 8000` in this folder

## License & credits

- Code: MIT — see `LICENSE`. © 2026 עומר למל (Omer Lemel).
- Course data: Tel Aviv University yedion (ידיעון); each course panel links
  back to its official program page.
- Cat picture: random via [cataas.com](https://cataas.com);
  meow sound: Wikimedia Commons (CC BY-SA).
