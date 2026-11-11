#!/usr/bin/env python3
"""Erzeugt klaviertransport-wien-<PLZ>.html aus der Hauptseite klaviertransport-wien.html
und den geprüften JSON-Texten. Aufruf: python3 genklavier.py <repo> <json-ordner> <datum>"""
import sys, os, re, json, html, glob

REPO, JDIR, DATE = sys.argv[1], sys.argv[2], sys.argv[3]
HUB = open(os.path.join(REPO, 'klaviertransport-wien.html'), encoding='utf-8').read()
L = 'style="color:var(--color-accent);font-weight:600;"'
e = lambda t: html.escape(t, quote=False)

NAMES = {}
NB = {}
for f in sorted(glob.glob(os.path.join(REPO, 'umzug-wien-1*.html'))):
    plz = f[-9:-5]
    s = open(f, encoding='utf-8').read()
    m = re.search(r'<div class="nachbar-grid">(.*?)</div>', s, re.S)
    NB[plz] = re.findall(r'umzug-wien-(\d{4})" class="nachbar-link">\d{4} ([^<]+)<', m.group(1))
for plz, lst in NB.items():
    for p, n in lst:
        NAMES[p] = n


def price_table():
    return '''<table class="price-table">
                <thead><tr><th>Stockwerk</th><th>Preis (Richtwert)</th></tr></thead>
                <tbody>
                    <tr><td>1. Stock ohne Lift</td><td class="price">130–170 €</td></tr>
                    <tr><td>2. Stock ohne Lift</td><td class="price">170–230 €</td></tr>
                    <tr><td>3. Stock ohne Lift</td><td class="price">250–340 €</td></tr>
                    <tr><td>Erdgeschoss, mit Lift oder höheres Stockwerk</td><td class="price">Auf Anfrage</td></tr>
                </tbody>
            </table>'''


def build(d):
    plz, bez, inb = d['plz'], d['bezirk'], d['in_bezirk']
    slug = 'klaviertransport-wien-' + plz
    url = 'https://packdas.at/' + slug
    title = 'Klaviertransport %s %s ab 130 € | packdas!' % (bez, plz)
    if len(title) > 60:
        title = 'Klaviertransport %s %s | packdas!' % (bez, plz)
    desc = 'Klaviertransport %s (%s Wien): Klaviere und Pianinos bis 250 kg, Richtwerte ab 130 €. Fotos per WhatsApp schicken, Angebot in wenigen Minuten.' % (inb, plz)
    if len(desc) > 155:
        desc = 'Klaviertransport %s (%s Wien): Klaviere und Pianinos bis 250 kg, Richtwerte ab 130 €. Angebot per WhatsApp.' % (inb, plz)
    assert len(title) <= 60 and len(desc) <= 155, (plz, len(title), len(desc))

    faq = [(x['q'], x['a']) for x in d['faq']]
    faq.append(('Was kostet ein Klaviertransport %s?' % inb,
                'Innerhalb Wiens gelten als Richtwerte: 130–170 € in den 1. Stock ohne Lift, 170–230 € in den 2. Stock ohne Lift und 250–340 € in den 3. Stock ohne Lift. Der genaue Preis hängt von der Strecke, vom Lift, vom Trageweg und vom Klavier ab. Mit Fotos per WhatsApp erhalten Sie in wenigen Minuten ein Angebot.'))

    s = HUB
    hub_title = re.search(r'<title>(.*?)</title>', s).group(1)
    hub_desc = re.search(r'<meta name="description" content="([^"]*)"', s).group(1)
    assert s.count(hub_title) == 2 and s.count(hub_desc) == 2
    s = s.replace(hub_title, e(title)).replace(hub_desc, e(desc))
    assert s.count('https://packdas.at/klaviertransport-wien"') == 3, s.count('https://packdas.at/klaviertransport-wien"')
    s = s.replace('<link rel="canonical" href="https://packdas.at/klaviertransport-wien">', '<link rel="canonical" href="%s">' % url)
    s = s.replace('<meta property="og:url" content="https://packdas.at/klaviertransport-wien">', '<meta property="og:url" content="%s">' % url)

    # Schema: Service + FAQ der Hauptseite ersetzen, Breadcrumb ergänzen
    sv = {"@context": "https://schema.org", "@type": "Service", "name": "Klaviertransport %s" % bez,
          "serviceType": "Klaviertransport",
          "description": "Transport von Pianinos und Standklavieren bis 250 kg sowie E-Pianos in %s Wien-%s. Keine Flügel." % (plz, bez),
          "areaServed": {"@type": "AdministrativeArea", "name": "Wien %s" % bez, "postalCode": plz},
          "url": url,
          "offers": {"@type": "AggregateOffer", "priceCurrency": "EUR", "lowPrice": "130", "highPrice": "340",
                     "description": "Richtwerte innerhalb Wiens, 1. bis 3. Stock ohne Lift"},
          "provider": {"@type": "MovingCompany", "name": "Packdas Umzug & Entrümpelung Wien", "alternateName": "packdas!",
                       "url": "https://packdas.at", "telephone": "+436766064470"}}
    fj = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://packdas.at"},
        {"@type": "ListItem", "position": 2, "name": "Klaviertransport Wien", "item": "https://packdas.at/klaviertransport-wien"},
        {"@type": "ListItem", "position": 3, "name": "Klaviertransport %s" % bez, "item": url}]}
    blocks = list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>\n?', s, re.S))
    out, done = s, False
    for m in reversed(blocks):
        t = json.loads(m.group(1)).get('@type')
        if t in ('Service', 'FAQPage'):
            out = out[:m.start()] + out[m.end():]
    s = out.replace('</head>', ''.join('<script type="application/ld+json">%s</script>\n' % json.dumps(x, ensure_ascii=False) for x in (sv, fj, bc)) + '</head>', 1)

    # Hero
    a = '<div class="breadcrumb"><a href="/">Home</a><span>›</span>Klaviertransport Wien</div>'
    assert s.count(a) == 1
    s = s.replace(a, '<div class="breadcrumb"><a href="/">Home</a><span>›</span><a href="/klaviertransport-wien">Klaviertransport Wien</a><span>›</span>%s</div>' % e(bez))
    s = re.sub(r'<h1>.*?</h1>', '<h1>Klaviertransport %s (%s) mit <span class="accent">packdas!</span></h1>' % (e(bez), plz), s, count=1, flags=re.S)
    hp = re.search(r'(<h1>.*?</h1>\s*)<p>.*?</p>', s, re.S)
    s = s[:hp.start()] + hp.group(1) + '<p>Klaviere und Pianinos bis 250 kg sowie E-Pianos, sicher getragen und transportiert %s.</p>' % e(inb) + s[hp.end():]

    # Inhalt
    nb = NB[plz]
    nbl = '\n'.join('<a href="/klaviertransport-wien-%s" class="nachbar-link">%s %s</a>' % (p, p, e(n)) for p, n in nb)
    cross = []
    for svc, lab in (('umzug', 'Umzug'), ('entruempelung', 'Entrümpelung'), ('kleintransport', 'Kleintransport')):
        if os.path.exists(os.path.join(REPO, '%s-wien-%s.html' % (svc, plz))):
            cross.append('<a href="/%s-wien-%s" %s>%s %s %s</a>' % (svc, plz, L, lab, e(bez), plz))
    crosst = ', '.join(cross[:-1]) + ' und ' + cross[-1] if len(cross) > 1 else cross[0]
    body = '''<section>
        <div class="section-inner content-block reveal">
            <p>%s</p>

            <h2>%s</h2>
%s

            <h2>%s</h2>
            <p>%s</p>
            <ul>
%s
            </ul>

            <h2>Preise für Klaviertransport %s</h2>
            <p>Das sind unsere Richtwerte für einen Klaviertransport innerhalb Wiens:</p>
            %s
            <p>Das sind Preisspannen, keine Fixpreise. Der genaue Preis hängt von der Strecke, vom Lift, vom Trageweg und vom Klavier ab. Schicken Sie uns Fotos vom Klavier und vom Stiegenhaus per WhatsApp, dann nennen wir Ihnen den Preis vorab.</p>
            <p>Wie der Transport abläuft, welche Klaviere wir übernehmen und wie Sie sich vorbereiten, lesen Sie auf der Hauptseite <a href="/klaviertransport-wien" %s>Klaviertransport Wien</a>.</p>

            <h2>Klaviertransport in Nachbarbezirken</h2>
            <p>Wir sind auch in den umliegenden Bezirken für Sie da:</p>
            <div class="nachbar-grid">%s
</div>
            <p style="margin-top:1rem;">Auch %s für Sie da: %s.</p>
        </div>
    </section>
''' % (e(d['intro']), e(d['typisch_titel']), '\n'.join('            <p>%s</p>' % e(p) for p in d['typisch']),
       e(d['worauf_titel']), e(d['worauf']), '\n'.join('            <li>%s</li>' % e(t) for t in d['tipps']),
       e(inb), price_table(), L, nbl, e(inb), crosst)
    fh = '''    <section id="faq">
        <div class="section-inner">
            <div class="section-header reveal">
                <p class="section-label">Häufige Fragen</p>
                <h2 class="section-title">FAQ – Klaviertransport %s</h2>
            </div>
            <div class="reveal">
%s            </div>
        </div>
    </section>

    ''' % (e(bez), ''.join('                <div class="faq-item"><div class="faq-q">%s</div><div class="faq-a"><div class="faq-a-inner">%s</div></div></div>\n' % (e(q), e(a)) for q, a in faq))
    i = s.index('<section>\n        <div class="section-inner content-block reveal">')
    j = s.index('<section class="cta-section" id="kontakt-cta">')
    s = s[:i] + body + fh + s[j:]
    # zweites Hero-Foto ohne Keyword-Zusatz lassen; Klavierfoto-Alt mit Bezirk
    s = s.replace('über eine Einfahrt – Klaviertransport Wien"', 'über eine Einfahrt – Klaviertransport %s"' % e(bez))
    for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        json.loads(x)
    open(os.path.join(REPO, slug + '.html'), 'w', encoding='utf-8').write(s)
    words = len(re.sub(r'<[^>]+>', ' ', s[s.index('<body'):s.index('<footer')]).split())
    return slug, title, len(title), len(desc), words


res = []
for f in sorted(glob.glob(os.path.join(JDIR, '*.json'))):
    res.append(build(json.load(open(f, encoding='utf-8'))))
for r in res:
    print(*r)
print(len(res), 'Seiten')
