#!/usr/bin/env python3
"""SEO-Vergleich vorher/nachher: Design darf nichts davon ändern.

Aufruf:  python3 tools/seo_vergleich.py [git-ref]   (Standard: origin/main)

Vergleicht pro HTML-Seite den Stand im git-ref mit dem Arbeitsstand:
  Titel, Meta-Beschreibung, Robots, Canonical, hreflang, Open-Graph,
  alle Überschriften H1–H6 (Reihenfolge), sichtbarer Text,
  JSON-LD (inhaltlich), Bild-Alt-Texte (je Bild), Links (Ziele), Dateiliste.
Ausgabe: Liste der Abweichungen; Exit-Code 1, wenn es welche gibt.
"""
import json, os, re, subprocess, sys, glob
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = sys.argv[1] if len(sys.argv) > 1 else 'origin/main'

def ws(s):
    return re.sub(r'\s+', ' ', s or '').strip()

def extract(html):
    s = BeautifulSoup(html, 'lxml')
    d = {}
    d['title'] = ws(s.title.string if s.title else '')
    def meta(**kw):
        t = s.find('meta', attrs=kw)
        return ws(t.get('content')) if t else None
    d['description'] = meta(name='description')
    d['robots'] = meta(name='robots')
    d['og'] = sorted((m.get('property'), ws(m.get('content'))) for m in s.find_all('meta', property=re.compile('^og:')))
    d['canonical'] = [l.get('href') for l in s.find_all('link', rel='canonical')]
    d['hreflang'] = sorted((l.get('hreflang'), l.get('href')) for l in s.find_all('link', hreflang=True))
    d['headings'] = [(h.name, ws(h.get_text(' '))) for h in s.find_all(re.compile('^h[1-6]$'))]
    lds = []
    for sc in s.find_all('script', type='application/ld+json'):
        try:
            lds.append(json.dumps(json.loads(sc.string), sort_keys=True, ensure_ascii=False))
        except Exception:
            lds.append('UNGÜLTIG: ' + ws(sc.string)[:80])
    d['jsonld'] = sorted(lds)
    # Alt-Texte: jedes einzelne Bild (src -> alt), Duplikate zusammengefasst
    d['images'] = sorted({(i.get('src'), ws(i.get('alt'))) for i in s.find_all('img')})
    d['links'] = sorted({a.get('href') for a in s.find_all('a', href=True)})
    body = s.body
    for t in body.find_all(['script', 'style', 'noscript']):
        t.decompose()
    # Logo-Umbau (packdas<span>!</span>) erzeugt keinen Textunterschied
    d['text'] = ws(body.get_text(' ')).replace('packdas !', 'packdas!')
    return d

def git_files(ref):
    out = subprocess.run(['git', '-C', ROOT, 'ls-tree', '--name-only', ref], capture_output=True, text=True, check=True).stdout
    return sorted(f for f in out.split() if f.endswith('.html'))

def git_show(ref, f):
    return subprocess.run(['git', '-C', ROOT, 'show', f'{ref}:{f}'], capture_output=True, check=True).stdout.decode('utf-8')

def main():
    before = git_files(REF)
    now = sorted(os.path.basename(f) for f in glob.glob(os.path.join(ROOT, '*.html')))
    problems = []
    if before != now:
        problems.append(f'Dateiliste: fehlt {sorted(set(before)-set(now))}, neu {sorted(set(now)-set(before))}')
    for f in sorted(set(before) & set(now)):
        a = extract(git_show(REF, f))
        b = extract(open(os.path.join(ROOT, f), encoding='utf-8').read())
        for k in a:
            if a[k] != b[k]:
                if k == 'text':
                    # erste Abweichung zeigen
                    i = next((i for i, (x, y) in enumerate(zip(a[k], b[k])) if x != y), min(len(a[k]), len(b[k])))
                    problems.append(f'{f}: TEXT weicht ab bei …{a[k][max(0,i-60):i+60]}… → …{b[k][max(0,i-60):i+60]}…')
                elif isinstance(a[k], list):
                    problems.append(f'{f}: {k.upper()} weg: {[x for x in a[k] if x not in b[k]]} | neu: {[x for x in b[k] if x not in a[k]]}')
                else:
                    problems.append(f'{f}: {k.upper()} {a[k]!r} → {b[k]!r}')
    print(f'Verglichen: {len(set(before)&set(now))} Seiten gegen {REF}')
    for p in problems:
        print('  ✗', p)
    print('ERGEBNIS:', 'alles gleich ✓' if not problems else f'{len(problems)} Abweichung(en)')
    sys.exit(1 if problems else 0)

if __name__ == '__main__':
    main()
