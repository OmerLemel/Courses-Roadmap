"""Fetch a TAU study-program tree and top up course prerequisites.

Usage:
    python fetch_program.py TCID SHANA [--skip-prereqs]

Example:
    python fetch_program.py 7583 2026
    python fetch_program.py 7606 2025 --skip-prereqs

Writes prog_<TCID>_<SHANA>.json and extends prereqs.json with any
course IDs not seen before. Exits 2 when TAU has no data for the
requested program/year (e.g. a program that did not exist yet).
"""
import json
import re
import sys
import time
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ENDPOINT = 'https://tochniot.tau.ac.il/graphql'
QUERY = ('query results($apiUrl: String!, $filters: JSON!) {'
         ' results(apiUrl: $apiUrl, filters: $filters) { body } }')
CODE_RE = re.compile(r'\((\d{3,4}-\d{3,4})\)')
HEADERS = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0',
           'Origin': 'https://www.tau.ac.il', 'Referer': 'https://www.tau.ac.il/'}


def call(api_url, filters):
    payload = {"operationName": "results",
               "variables": {"apiUrl": api_url, "filters": filters},
               "query": QUERY}
    req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(),
                                 headers=HEADERS)
    resp = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='ignore')
    return json.loads(resp)


def walk_ramas(ramas, func, depth=0):
    for r in ramas or []:
        func(r, depth)
        if r.get('rama'):
            walk_ramas(r['rama'], func, depth + 1)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    tcid, shana = sys.argv[1], sys.argv[2]
    skip_prereqs = '--skip-prereqs' in sys.argv[3:]

    r = call('ydtochnit', {"safa": "1", "shana": shana, "tcid": tcid,
                           "tab": "programStudy"})
    body = r['data']['results']['body']
    if isinstance(body, dict):
        print('No data for tcid=%s shana=%s: %s'
              % (tcid, shana, body.get('Tau', {}).get('errmsg', body)))
        return 2
    prog = body[0]
    fn = 'prog_%s_%s.json' % (tcid, shana)
    json.dump(prog, open(fn, 'w', encoding='utf-8'), ensure_ascii=False)
    print('saved %s: %s | %s' % (fn, prog.get('teurtochnit'), prog.get('teurtoar')))
    total = [0]

    def count(r, depth):
        total[0] += len(r.get('kurs', []) or [])
        print('  ' * depth + r.get('teurrama', ''),
              'nkurs=', len(r.get('kurs', []) or []))
    walk_ramas(prog.get('rama', []), count)
    print('total courses:', total[0])

    if skip_prereqs:
        return 0
    pr = json.load(open('prereqs.json', encoding='utf-8'))
    need = {}

    def collect(r, depth):
        for k in r.get('kurs', []) or []:
            if k.get('drishotkedem') not in ('0', '', None) or \
               k.get('drishotmakbilot') not in ('0', '', None):
                if k['kursid'] not in pr and k['kursid'] not in need:
                    need[k['kursid']] = (k['kursshow'],
                                         k.get('orginaltcid') or tcid)
    walk_ramas(prog.get('rama', []), collect)
    print('new course IDs needing prerequisites:', len(need))
    for i, (kursid, (show, lookup)) in enumerate(need.items()):
        try:
            b = call('yddrishot', {"safa": "1", "shana": shana, "tcid": lookup,
                                   "tab": "programStudy", "kursid": kursid})
            body0 = b['data']['results']['body'][0]
            pres = [e.get('shura', '') for e in body0.get('drishotkedem', []) or []]
            pars = [e.get('shura', '') for e in body0.get('drishotmakbilot', []) or []]
            pr[kursid] = {"show": show,
                          "pre": sorted(set(sum([CODE_RE.findall(s) for s in pres], []))),
                          "par": sorted(set(sum([CODE_RE.findall(s) for s in pars], []))),
                          "raw_pre": pres, "raw_par": pars}
        except Exception as exc:  # keep going; rebuild tolerates missing entries
            pr[kursid] = {"show": show, "pre": [], "par": [],
                          "raw_pre": [], "raw_par": [], "error": str(exc)[:200]}
        time.sleep(0.15)
    json.dump(pr, open('prereqs.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print('prereqs.json now holds %d courses' % len(pr))
    return 0


if __name__ == '__main__':
    sys.exit(main())
