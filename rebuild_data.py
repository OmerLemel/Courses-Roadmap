import json, re, sys, itertools
sys.stdout.reconfigure(encoding='utf-8')

def ctype(rama_name):
    n = rama_name or ''
    if 'שאר רוח' in n: return 'שאר רוח'
    if 'סמינר' in n: return 'סמינר'
    if 'סדנה' in n or 'סדנא' in n: return 'סדנה'
    if 'ליבה' in n: return 'ליבה'
    if 'ייעוד' in n: return 'ליבה'
    if 'חובה' in n: return 'חובה'
    if 'בחירה' in n: return 'בחירה'
    return 'בחירה'

def year_info(top, sub):
    y = 0; sem = ''
    if 'א\'' in top or top.strip() == "שנה א'" or 'שנה א' in top: y = 1
    elif 'שנה ב' in top: y = 2
    elif 'שנה ג' in top: y = 3
    elif 'שנים ב' in top: y = 0
    if 'שאר רוח' in top: y = 4
    if "סמסטר א" in sub: sem = 'א'
    elif "סמסטר ב" in sub: sem = 'ב'
    return y, sem

programs = {
  "dual": {"id": "dual", "tcids": {"2025": ["7612"], "2026": ["7612"]},
           "name": "מתמטיקה ומדעי המחשב (דו-חוגי)",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7612",
           "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7612"},
  "csai": {"id": "csai", "tcids": {"2026": ["8865"]},
           "name": "מדעי המחשב עם חטיבת בינה מלאכותית",
           "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=8865"},
  "math": {"id": "math", "tcids": {"2025": ["7606"], "2026": ["7606"]},
           "name": "מתמטיקה עיונית (חד-חוגי)",
           "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7606",
           "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7606"},
  "cs": {"id": "cs", "tcids": {"2025": ["7583"], "2026": ["7583"]},
         "name": "מדעי המחשב (חד-חוגי)",
         "url2025": "https://www.tau.ac.il/study-program?safa=1&shana=2025&tab=programStudy&tcid=7583",
         "url2026": "https://www.tau.ac.il/study-program?safa=1&shana=2026&tab=programStudy&tcid=7583"},
}
filemap = {"dual_2025": "prog_7612_2025.json", "dual_2026": "prog_7612_2026.json",
           "csai_2026": "prog_8865_2026.json",
           "math_2025": "prog_7606_2025.json", "math_2026": "prog_7606_2026.json",
           "cs_2025": "prog_7583_2025.json", "cs_2026": "prog_7583_2026.json"}
prereq = json.load(open('prereqs.json', encoding='utf-8'))

courses = {}
expected = {}  # (show, prog, year) -> raw-derived occ, for the audit below
multi = {}  # (show, prog, year) -> set of distinct derived tuples (cross-listings)
for key, fn in filemap.items():
    prog = key.rsplit('_', 1)[0]; year = key.rsplit('_', 1)[1]
    d = json.load(open(fn, encoding='utf-8'))
    def walk(rs, top='', sub=''):
        for r in rs:
            name = r.get('teurrama', '')
            for k in r.get('kurs', []) or []:
                show = k.get('kursshow', '').strip()
                if not show: continue
                if show in courses:  # prefer non-empty name/credits across occurrences
                    c = courses[show]
                    if not c['name'] and k.get('teurkurs'): c['name'] = k['teurkurs']
                    if not c['credits'] and k.get('shaotuni'): c['credits'] = k['shaotuni']
                else:
                    c = courses[show] = {"id": show, "kursid": k['kursid'], "name": k.get('teurkurs', ''),
                                         "credits": k.get('shaotuni', ''), "programs": {}, "occ": {}}
                c['programs'].setdefault(prog, {})
                t = ctype(name)
                y, sem = year_info(top or name, name)
                c['occ'][f'{prog}_{year}'] = {"type": t, "year": y, "sem": sem,
                                                   "rama": (top + ' / ' + name if top else name)}
                c['programs'][prog][year] = {"type": t, "year": y, "sem": sem,
                                             "rama": (top + ' / ' + name if top else name)}
                expected[(show, prog, year)] = dict(c['programs'][prog][year])
                multi.setdefault((show, prog, year), set()).add((t, y, sem))
            if r.get('rama'):
                walk(r['rama'], top or name, name)
    walk(d['rama'])

show_set = set(courses.keys())
edges = []
for kursid, v in prereq.items():
    tgt = v['show']
    if tgt not in show_set: continue
    for s in v.get('pre', []):
        if s in show_set: edges.append({"from": s, "to": tgt, "kind": "pre"})
    for s in v.get('par', []) or []:
        if s in show_set: edges.append({"from": s, "to": tgt, "kind": "co"})
seen = set(); ue = []
for e in edges:
    k = (e['from'], e['to'], e['kind'])
    if k not in seen: seen.add(k); ue.append(e)
edges = ue
for show, c in courses.items():
    ys = [o['year'] for o in c['occ'].values() if o['year'] in (1, 2, 3)]
    c['year'] = min(ys) if ys else 4

# --- manual semester overrides (teaching schedule beats yedion structure) ---
# Value form: "SEM" (all programs) or {"sem": "SEM", "programs": [...]} (scoped).
covered = set()
try:
    ovr = json.load(open('overrides.json', encoding='utf-8'))
    for show, rule in (ovr.get('sem') or {}).items():
        if isinstance(rule, dict):
            sem, progs = rule.get('sem', ''), rule.get('programs')
        else:
            sem, progs = rule, None
        if sem not in ('א', 'ב', ''):
            print('override: bad semester value for', show, repr(sem))
            continue
        c = courses.get(show)
        if not c:
            print('override: unknown course', show)
            continue
        targets = [p for p in (progs if progs is not None else list(c['programs']))]
        for p in targets:
            if p not in c['programs']:
                print('override: %s not present in program %s' % (show, p))
                continue
            for y in c['programs'][p]:
                c['programs'][p][y]['sem'] = sem
                covered.add((show, p, y))
        for key in list(c['occ']):
            p2 = key.rsplit('_', 1)[0]
            if progs is None or p2 in (progs or []):
                c['occ'][key]['sem'] = sem
    print('overrides applied, covered occurrences:', len(covered))
except FileNotFoundError:
    pass

# --- logic groups (או/וגם) ---
code_re = re.compile(r'\((\d{3,4}-\d{3,4})\)')
tag_re = re.compile(r'<[^>]+>')
ou_re = re.compile(r'(?:^|\s)או(?:\s|$)')
def clean(s):
    t = tag_re.sub('', s).replace('&nbsp;', ' ').strip()
    return re.sub(r'\s+', ' ', t)
def parse(raw_list):
    seq = []
    for s in raw_list or []:
        t = clean(s)
        if t == 'או': seq.append(('or',)); continue
        if t == '+': seq.append(('plus',)); continue
        ms = list(code_re.finditer(s))
        if not ms: continue
        bolds = [clean(b) for b in re.findall(r'<b>(.*?)</b>', s)]
        prev = 0
        for i, m in enumerate(ms):
            between = clean(s[prev:m.start()])
            if i > 0 and ou_re.search(between): seq.append(('or',))
            seq.append(('c', m.group(1), bolds[i] if i < len(bolds) else ''))
            prev = m.end()
    blocks, cur = [], []
    for it in seq:
        if it[0] == 'plus': blocks.append(cur); cur = []
        else: cur.append(it)
    blocks.append(cur)
    alt_lists = []
    for seg in blocks:
        alts, a = [], []
        for it in seg:
            if it[0] == 'or':
                if a: alts.append(a); a = []
            else: a.append((it[1], it[2]))
        if a: alts.append(a)
        if alts: alt_lists.append(alts)
    if not alt_lists: return [], {}
    names = {}
    for alts in alt_lists:
        for a in alts:
            for code, nm in a:
                if nm and code not in names: names[code] = nm
    groups = []
    for combo in itertools.product(*alt_lists):
        g = []
        for alt in combo: g.extend(alt)
        seen2, u = set(), []
        for code, nm in g:
            if code not in seen2: seen2.add(code); u.append(code)
        if u and u not in groups: groups.append(u)
    return groups, names

by_show = {c['id']: c for c in courses.values()}
ext = {}
for kursid, v in prereq.items():
    show = v.get('show')
    if show not in by_show: continue
    gpre, n1 = parse(v.get('raw_pre'))
    gco, n2 = parse(v.get('raw_par'))
    by_show[show]['reqPre'] = gpre
    by_show[show]['reqCo'] = gco
    for dd in (n1, n2):
        for k, nm in dd.items(): ext.setdefault(k, nm)
for c in courses.values():
    c.setdefault('reqPre', []); c.setdefault('reqCo', [])

# --- audit: final placements must equal raw-derived ones, except override-covered semesters ---
bad = 0
checked = 0
for c in courses.values():
    for p, ys in c['programs'].items():
        for y, o in ys.items():
            e = expected.get((c['id'], p, y))
            checked += 1
            if e is None:
                print('AUDIT missing expected occ for', c['id'], p, y)
                bad += 1
                continue
            for f in ('type', 'year', 'sem', 'rama'):
                if o[f] != e[f]:
                    if f == 'sem' and (c['id'], p, y) in covered:
                        continue
                    print('AUDIT DIFF %s %s %s field=%s data=%r raw=%r'
                          % (c['id'], p, y, f, o[f], e[f]))
                    bad += 1
    for key, o in c['occ'].items():
        p2 = key.rsplit('_', 1)[0]
        pv = (c['programs'].get(p2) or {})
        y2 = key.rsplit('_', 1)[1]
        if y2 in pv and o != pv[y2]:
            print('AUDIT occ/programs mismatch for', c['id'], key)
            bad += 1
print('audit: checked %d occurrences, %d divergence(s)%s'
      % (checked, bad, ' -- FAIL' if bad else ' -- OK'))
print('cross-listed courses (same program-year, multiple rama contexts):')
for (show, p, y), vals in sorted(multi.items()):
    if len(vals) > 1:
        print('  WARN %s %s %s contexts=%s' % (show, p, y, sorted(vals)))
if bad:
    sys.exit(1)

data = {"programs": list(programs.values()), "courses": list(courses.values()), "edges": edges,
        "extNames": ext, "meta": {"years": ["2025", "2026"],
        "counts": {"courses": len(courses), "edges": len(edges)}}}
json.dump(data, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('courses', len(courses), 'edges', len(edges),
      'pre', sum(1 for e in edges if e['kind'] == 'pre'),
      'co', sum(1 for e in edges if e['kind'] == 'co'), 'extNames', len(ext))
per = {}
for c in courses.values():
    for p, ys in c['programs'].items():
        for y in ys: per[(p, y)] = per.get((p, y), 0) + 1
print('per program-year:', sorted(per.items()))
