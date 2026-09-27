import json, re, sys, itertools
sys.stdout.reconfigure(encoding='utf-8')
code_re = re.compile(r'\((\d{3,4}-\d{3,4})\)')
tag_re = re.compile(r'<[^>]+>')
ou_re = re.compile(r'(?:^|\s)או(?:\s|$)')

def clean(s):
    t = tag_re.sub('', s).replace('&nbsp;', ' ').strip()
    return re.sub(r'\s+', ' ', t)

def parse(raw_list):
    """Parse shura token list into DNF: list of AND-groups (each a list of (code,name))."""
    seq = []  # ('c', code, name) | ('or',) | ('and',)
    for s in raw_list or []:
        t = clean(s)
        if t == 'או':
            seq.append(('or',)); continue
        if t == '+':
            seq.append(('plus',)); continue
        ms = list(code_re.finditer(s))
        if not ms:
            continue
        bolds = [clean(b) for b in re.findall(r'<b>(.*?)</b>', s)]
        prev = 0
        for i, m in enumerate(ms):
            between = clean(s[prev:m.start()])
            if i > 0 and ou_re.search(between):
                seq.append(('or',))
            # inline 'וגם' (or plain adjacency) = implicit AND: no token needed
            seq.append(('c', m.group(1), bolds[i] if i < len(bolds) else ''))
            prev = m.end()
    # split by PLUS into blocks, each block split by OR into alternatives
    segs, cur = [], []
    for it in seq:
        if it[0] == 'plus':
            segs.append(cur); cur = []
        else:
            cur.append(it)
    segs.append(cur)
    alt_lists = []
    for seg in segs:
        alts, a = [], []
        for it in seg:
            if it[0] == 'or':
                if a: alts.append(a); a = []
            else:
                a.append((it[1], it[2]))
        if a: alts.append(a)
        if alts: alt_lists.append(alts)
    if not alt_lists:
        return [], {}
    names = {}
    for alts in alt_lists:
        for a in alts:
            for code, nm in a:
                if nm and code not in names:
                    names[code] = nm
    # DNF via cartesian product
    groups = []
    for combo in itertools.product(*alt_lists):
        g = []
        for alt in combo:
            g.extend(alt)
        # dedupe preserve order
        seen, u = set(), []
        for code, nm in g:
            if code not in seen:
                seen.add(code); u.append(code)
        if u and u not in groups:
            groups.append(u)
    return groups, names

pr = json.load(open('prereqs.json', encoding='utf-8'))
data = json.load(open('data.json', encoding='utf-8'))
by_show = {c['id']: c for c in data['courses']}
ext = dict(data.get('extNames', {}))
n_pre = n_co = 0
for kursid, v in pr.items():
    show = v.get('show')
    if show not in by_show:
        continue
    gpre, n1 = parse(v.get('raw_pre'))
    gco, n2 = parse(v.get('raw_par'))
    by_show[show]['reqPre'] = gpre
    by_show[show]['reqCo'] = gco
    for d_ in (n1, n2):
        for k, nm in d_.items():
            ext.setdefault(k, nm)
    n_pre += 1 if gpre else 0
    n_co += 1 if gco else 0
# ensure every course has the fields
for c in data['courses']:
    c.setdefault('reqPre', [])
    c.setdefault('reqCo', [])
data['extNames'] = ext
json.dump(data, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('courses with pre-groups:', n_pre, 'with co-groups:', n_co, 'ext names:', len(ext))
# sanity: מבוא להסתברות
c = by_show.get('0366-2010', {})
print('2010 pre:', c.get('reqPre'))
print('2010 co:', c.get('reqCo'))
