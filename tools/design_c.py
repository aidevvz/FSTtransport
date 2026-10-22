#!/usr/bin/env python3
"""Design C auf Unterseiten anwenden (nur Optik, keine Inhalte).

Aufruf:  python3 tools/design_c.py            (alle Seiten)
         python3 tools/design_c.py datei.html  (einzelne Seiten)

Was das Skript macht – pro Seite:
  1. Google Fonts (DM Serif / Manrope) raus, Inter selbst gehostet (preload) rein
  2. /assets/site.css NACH dem seiteneigenen <style> einbinden (+ Marker <!-- design-c -->)
  3. Logo "packdas!" -> "packdas<span class="logo-mark">!</span>" (Ausrufezeichen in Gold)
  4. Team-Foto-Leiste (team-banner) unter dem Header -> Foto-Raster IM Header
     (sofort sichtbar, auch am Handy), WebP + JPG-Fallback, erstes Foto mit
     fetchpriority=high und preload.
Titel, Meta, Überschriften, Texte, JSON-LD, Alt-Texte und URLs werden nicht angefasst.
Bereits umgebaute Seiten (Marker vorhanden) werden übersprungen.
"""
import re, sys, glob, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = '<!-- design-c -->'

FONTS_OLD = re.compile(
    r'[ \t]*<link rel="preconnect" href="https://fonts.googleapis.com">\s*\n'
    r'[ \t]*<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\s*\n'
    r'[ \t]*<link href="https://fonts.googleapis.com/css2\?[^"]*" rel="stylesheet">\n')
FONT_PRELOAD = '    <link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>\n'

BANNER = re.compile(
    r'</header>\s*<section style="padding:2rem 0 0;">\s*<div class="team-banner">\s*'
    r'(<img [^>]*>)\s*(<img [^>]*>)\s*</div>\s*</section>')

def attr(tag, name):
    m = re.search(r'\b%s="([^"]*)"' % name, tag)
    return m.group(1) if m else None

_dims = {}
def webp_set(jpg):
    """srcset der WebP-Varianten (sm + lg) mit echter Breite."""
    base = jpg[:-4]
    parts = []
    for suf in ('sm', 'lg'):
        p = os.path.join(ROOT, f'{base}-{suf}.webp')
        if not os.path.exists(p):
            raise SystemExit(f'WebP fehlt: {p} – zuerst Bild konvertieren')
        if p not in _dims:
            _dims[p] = Image.open(p).size
        parts.append(f'{base}-{suf}.webp {_dims[p][0]}w')
    return ', '.join(parts)

def tile(img, cls, sizes, first):
    src, alt, w, h = attr(img, 'src'), attr(img, 'alt'), attr(img, 'width'), attr(img, 'height')
    load = 'loading="eager" fetchpriority="high"' if first else 'loading="lazy"'
    return (f'            <figure class="tile {cls}"><picture><source type="image/webp" '
            f'srcset="{webp_set(src)}" sizes="{sizes}"><img src="{src}" alt="{alt}" '
            f'width="{w}" height="{h}" {load} decoding="async"></picture></figure>')

def is_portrait(img):
    return int(attr(img, 'height')) > int(attr(img, 'width'))

def convert(html):
    if MARKER in html:
        return None, 'schon umgebaut'
    notes = []
    # 1 Fonts
    html, n = FONTS_OLD.subn(FONT_PRELOAD, html, count=1)
    if n != 1:
        return None, 'Google-Fonts-Block nicht gefunden'
    # 4 Foto-Raster
    preload = ''
    m = BANNER.search(html)
    if m:
        a, b = m.group(1), m.group(2)
        pa, pb = is_portrait(a), is_portrait(b)
        if pa and pb:
            cls, order = 'duo port2', [(a, 'tall'), (b, 'tall')]
        elif not pa and not pb:
            cls, order = 'duo land2', [(a, 'big'), (b, 'big')]
        else:
            land, port = (b, a) if pa else (a, b)  # Querformat zuerst (groß), Hochformat ganz
            cls, order = 'duo', [(land, 'big'), (port, 'tall')]
        sizes = ['(max-width: 768px) 60vw, 520px', '(max-width: 768px) 40vw, 360px']
        if cls == 'duo port2':
            sizes = ['(max-width: 768px) 50vw, 380px', '(max-width: 768px) 50vw, 380px']
        if cls == 'duo land2':
            sizes = ['(max-width: 768px) 100vw, 600px', '(max-width: 768px) 100vw, 430px']
        tiles = [tile(img, c, sizes[i], i == 0) for i, (img, c) in enumerate(order)]
        block = (f'\n        <div class="hero-bento {cls}">\n' + '\n'.join(tiles) +
                 '\n        </div>\n    </header>')
        html = html[:m.start()] + block + html[m.end():]
        first = order[0][0]
        preload = (f'    <link rel="preload" as="image" type="image/webp" imagesrcset="{webp_set(attr(first, "src"))}" '
                   f'imagesizes="{sizes[0]}" fetchpriority="high">\n')
        html = html.replace(FONT_PRELOAD, FONT_PRELOAD + preload, 1)
        notes.append(cls)
    else:
        notes.append('ohne Foto-Leiste')
    # 2 site.css nach dem letzten </script> bzw. vor </head>
    html, n = re.subn(r'\n</head>', f'\n    <link rel="stylesheet" href="/assets/site.css">\n    {MARKER}\n</head>', html, count=1)
    if n != 1:
        return None, '</head> nicht gefunden'
    # 3 Logo
    html = html.replace('class="nav-logo">packdas!</a>', 'class="nav-logo">packdas<span class="logo-mark">!</span></a>')
    return html, ', '.join(notes)

def main():
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, '*.html')))
    bad = 0
    for f in files:
        with open(f, encoding='utf-8') as fh:
            src = fh.read()
        out, info = convert(src)
        name = os.path.basename(f)
        if out is None:
            if info != 'schon umgebaut':
                bad += 1
            print(f'  {name}: {info}')
            continue
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(out)
        print(f'OK {name}: {info}')
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
