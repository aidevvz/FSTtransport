#!/usr/bin/env python3
"""Englische Seiten für packdas.at erzeugen (en/*.html).

Aufruf: python3 tools/gen_en.py
Vorlage für Kopf (CSS, Fonts, Tracking) und Skripte ist kleintransport-wien.html.
Inhalte stehen unten in PAGES. Preise/Fakten nur laut projekt-dokumente/seo-regeln-packdas.md.
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = open(os.path.join(ROOT, 'kleintransport-wien.html'), encoding='utf-8').read()
BASE = 'https://packdas.at'
WA = 'https://wa.me/436766064470?text='
GMAPS = 'https://www.google.com/maps?cid=11234201469434106058'
MELDE = 'https://www.oesterreich.gv.at/de/themen/persoenliche_dokumente_und_bestaetigungen/an__abmeldung_des_wohnsitzes/Seite.1180200.html'

def esc(s):
    return html.escape(s, quote=True)

# --- Bausteine aus der Vorlage -------------------------------------------------
STYLE = re.search(r'<style>.*?</style>', TPL, re.S).group(0)
GTAG = re.search(r'<!-- Google tag.*?</script>\s*<script>.*?</script>', TPL, re.S).group(0)
SCRIPT = re.search(r'<script>\s*const nav=.*?</script>', TPL, re.S).group(0)
SVG = {m.group(1): m.group(0) for m in []}
def svg_from(label):
    """Erstes SVG aus der Vorlage, das in einer Zeile mit `label` steht."""
    for line in TPL.splitlines():
        if label in line and '<svg' in line:
            return re.search(r'<svg.*?</svg>', line).group(0)
    return ''
ICON_WA = re.search(r'class="whatsapp-float"[^>]*>(<svg.*?</svg>)', TPL, re.S).group(1)
ICON_MAIL, ICON_PHONE, ICON_CLOCK = re.findall(r'<div class="cta-contact-item">(<svg.*?</svg>)', TPL, re.S)[:3]
ICON_FB, ICON_IG = re.findall(r'aria-label="(?:Facebook|Instagram)">(<svg.*?</svg>)', TPL, re.S)[:2]
AB_ICONS = re.findall(r'<span class="ab-item">(<svg.*?</svg>)', TPL, re.S)
BADGE_ICON = re.search(r'<div class="hero-badge">(<svg.*?</svg>)', TPL, re.S).group(1)
CARD_ICONS = re.findall(r'<div class="service-icon">(<svg.*?</svg>)</div>', TPL, re.S)

def pic(name, alt, w, h, first=False, sizes='(max-width: 768px) 100vw, 600px'):
    load = 'loading="eager" fetchpriority="high"' if first else 'loading="lazy"'
    return (f'<figure class="tile big"><picture><source type="image/webp" '
            f'srcset="/bilder/{name}-sm.webp 600w, /bilder/{name}-lg.webp 1200w" sizes="{sizes}">'
            f'<img src="/bilder/{name}.jpg" alt="{esc(alt)}" width="{w}" height="{h}" {load} decoding="async"></picture></figure>')

EN_PAGES = {'home': '/en/', 'clear': '/en/apartment-clearance-vienna', 'van': '/en/man-with-a-van-vienna'}
DE_OF = {'home': '/', 'clear': '/entruempelung-wien', 'van': '/kleintransport-wien'}

def nav(key):
    items = [('home', 'Moving'), ('clear', 'Clearance'), ('van', 'Man with a Van')]
    lis = ''.join(f'<li><a href="{EN_PAGES[k]}">{t}</a></li>' for k, t in items)
    return f'''    <div class="announcement-bar" role="banner">
        <span class="ab-item">{AB_ICONS[0]}In Vienna since 2020</span>
        <span class="ab-divider"></span>
        <span class="ab-item">{AB_ICONS[1]}24/7 – evenings &amp; weekends too</span>
        <span class="ab-divider"></span>
        <span class="ab-item">{AB_ICONS[2]}We speak English · Deutsch · Polski</span>
    </div>
    <nav class="nav" id="navbar">
        <div class="nav-inner">
            <a href="/en/" class="nav-logo">packdas<span class="logo-mark">!</span></a>
            <ul class="nav-links" id="navLinks">
                {lis}
                <li><a href="{DE_OF[key]}" hreflang="de" lang="de" title="Deutsche Version">DE</a></li>
                <li><a href="#contact" class="nav-cta">Contact</a></li>
            </ul>
            <button class="hamburger" id="hamburger" aria-label="Open menu" aria-expanded="false"><span></span><span></span><span></span></button>
        </div>
    </nav>'''

def wa_btn(text, label='💬 Get a quote on WhatsApp'):
    from urllib.parse import quote
    return (f'<a href="{WA}{quote(text)}" target="_blank" rel="noopener" class="btn btn-primary" '
            f'style="background:#25D366;box-shadow:0 4px 20px rgba(37,211,102,0.3);">{label}</a>')

def cards(items):
    out = []
    for i, (title, text) in enumerate(items):
        out.append(f'''                <div class="service-card reveal">
                    <div class="service-icon">{CARD_ICONS[i % len(CARD_ICONS)]}</div>
                    <h3>{title}</h3>
                    <p>{text}</p>
                </div>''')
    return '\n'.join(out)

def why(items):
    return '\n'.join(f'                <div class="why-item reveal"><div class="why-number">{n}</div><h3>{t}</h3><p>{p}</p></div>' for n, t, p in items)

def faq_html(faqs):
    return '\n'.join(f'                <div class="faq-item"><div class="faq-q">{esc(q)}</div><div class="faq-a"><div class="faq-a-inner">{a}</div></div></div>' for q, a in faqs)

def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)

def footer():
    return f'''    <footer role="contentinfo">
        <div class="footer-inner">
            <div class="footer-brand">
                <a href="/en/" class="nav-logo">packdas<span class="logo-mark">!</span></a>
                <p>Moving, apartment clearance and small moves in Vienna. Available 24/7, all 23 districts. Since 2020.</p>
                <div class="footer-social">
                    <a href="https://www.facebook.com/share/1DLyRE2VRR/?mibextid=wwXIfr" target="_blank" rel="noopener" aria-label="Facebook">{ICON_FB}</a>
                    <a href="https://www.instagram.com/packdas.at?igsh=YTA5YnFiMTFnbDBr&utm_source=qr" target="_blank" rel="noopener" aria-label="Instagram">{ICON_IG}</a>
                </div>
            </div>
            <div>
                <h4>Services</h4>
                <ul>
                    <li><a href="/en/">Moving company Vienna</a></li>
                    <li><a href="/en/apartment-clearance-vienna">Apartment clearance Vienna</a></li>
                    <li><a href="/en/man-with-a-van-vienna">Man with a van Vienna</a></li>
                </ul>
            </div>
            <div>
                <h4>Deutsch</h4>
                <ul>
                    <li><a href="/" hreflang="de" lang="de">Umzugsfirma Wien</a></li>
                    <li><a href="/entruempelung-wien" hreflang="de" lang="de">Entrümpelung Wien</a></li>
                    <li><a href="/kleintransport-wien" hreflang="de" lang="de">Kleintransport Wien</a></li>
                    <li><a href="/ueber-uns" hreflang="de" lang="de">Über uns</a></li>
                </ul>
            </div>
            <div>
                <h4>Legal (German)</h4>
                <ul>
                    <li><a href="/impressum" hreflang="de" lang="de">Imprint (Impressum)</a></li>
                    <li><a href="/datenschutz" hreflang="de" lang="de">Privacy (Datenschutz)</a></li>
                    <li><a href="/agb" hreflang="de" lang="de">Terms (AGB)</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <span>&copy; 2026 packdas! Vienna. All rights reserved.</span>
            <span><a href="/impressum">Impressum</a> · <a href="/datenschutz">Datenschutz</a></span>
        </div>
    </footer>'''

def cta(heading, sub, watext):
    return f'''    <section class="cta-section" id="contact">
        <div class="section-inner"><div class="reveal">
            <p class="section-label" style="color:var(--color-accent-light);">Contact</p>
            <h2>{heading}</h2>
            <p>{sub}</p>
            <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
                {wa_btn(watext, 'Message us on WhatsApp')}
                <a href="tel:+436766064470" class="btn btn-primary">Call us</a>
            </div>
            <div class="cta-contact-row">
                <div class="cta-contact-item">{ICON_MAIL}<a href="mailto:office@packdas.at" style="color:inherit;">office@packdas.at</a></div>
                <div class="cta-contact-item">{ICON_PHONE}+43 676 606 44 70</div>
                <div class="cta-contact-item">{ICON_CLOCK}Mon–Sun 24/7</div>
            </div>
        </div></div>
    </section><a href="{WA}Hi%20packdas!" class="whatsapp-float" target="_blank" rel="noopener">{ICON_WA}WhatsApp</a>'''

def provider():
    return {"@type": "MovingCompany", "name": "packdas!", "url": BASE + "/en/", "telephone": "+436766064470",
            "email": "office@packdas.at", "knowsLanguage": ["en", "de", "pl"],
            "address": {"@type": "PostalAddress", "streetAddress": "Burghardtgasse 21/12", "postalCode": "1200",
                        "addressLocality": "Vienna", "addressCountry": "AT"},
            "sameAs": [GMAPS], "hasMap": GMAPS}

def build(p):
    url = BASE + EN_PAGES[p['key']]
    de = BASE + DE_OF[p['key']]
    ld_service = {"@context": "https://schema.org", "@type": "Service", "name": p['service'], "serviceType": p['service'],
                  "inLanguage": "en", "provider": provider(), "areaServed": {"@type": "City", "name": "Vienna"},
                  "offers": {"@type": "Offer", "price": p['price'], "priceCurrency": "EUR", "description": p['offer']},
                  "url": url, "image": f"{BASE}/bilder/{p['img1'][0]}.jpg"}
    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "en",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in p['faq']]}
    head = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <title>{esc(p['title'])}</title>
    <meta name="description" content="{esc(p['desc'])}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{url}">
    <link rel="alternate" hreflang="en" href="{url}">
    <link rel="alternate" hreflang="de" href="{de}">
    <link rel="alternate" hreflang="x-default" href="{de}">
    <meta property="og:title" content="{esc(p['title'])}">
    <meta property="og:description" content="{esc(p['desc'])}">
    <meta property="og:url" content="{url}">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="en_GB">
    <meta property="og:locale:alternate" content="de_AT">
    <meta property="og:image" content="{BASE}/bilder/{p['img1'][0]}.jpg">
    <script type="application/ld+json">{json.dumps(ld_service, ensure_ascii=False)}</script>
    <script type="application/ld+json">{json.dumps(ld_faq, ensure_ascii=False)}</script>
    <link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" as="image" type="image/webp" imagesrcset="/bilder/{p['img1'][0]}-sm.webp 600w, /bilder/{p['img1'][0]}-lg.webp 1200w" imagesizes="(max-width: 768px) 100vw, 600px" fetchpriority="high">
    {STYLE}
{GTAG}
    <link rel="stylesheet" href="/assets/site.css">
    <!-- design-c -->
</head>
<body>
'''
    hero = f'''    <header class="hero hero-sm"><div class="hero-pattern"></div>
        <div class="hero-content">
            <div class="hero-badge">{BADGE_ICON}{p['badge']}</div>
            <h1>{p['h1']}</h1>
            <p>{p['lead']}</p>
            <div class="hero-actions">
                {wa_btn(p['watext'])}
                <a href="tel:+436766064470" class="btn btn-primary">📞 Call us</a>
            </div>
        </div>
        <div class="hero-bento duo land2">
            {pic(*p['img1'], first=True)}
            {pic(*p['img2'], sizes='(max-width: 768px) 100vw, 430px')}
        </div>
    </header>
'''
    body = head + nav(p['key']) + '\n' + hero + p['sections'] + f'''
    <!-- FAQ -->
    <section>
        <div class="section-inner">
            <div class="section-header reveal" style="text-align:center;">
                <p class="section-label">FAQ</p>
                <h2 class="section-title">{p['faq_title']}</h2>
            </div>
            <div class="content-block reveal">
{faq_html(p['faq'])}
            </div>
        </div>
    </section>
''' + cta(p['cta_h'], p['cta_p'], p['watext']) + '\n' + footer() + SCRIPT + '\n</body>\n</html>\n'
    out = os.path.join(ROOT, 'en', p['file'])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(body)
    print('geschrieben:', out)

# --- Inhalte -------------------------------------------------------------------
WHY_COMMON = [
    ('EN', 'We speak English', 'Message us in English – Kamil, the owner, answers personally. Our team also speaks German and Polish.'),
    ('24/7', 'Evenings &amp; weekends', 'We work 24/7, including Saturdays, Sundays and public holidays – at no extra charge.'),
    ('Own', 'Own team &amp; truck', 'No subcontractors: our own trained team and our own truck do the job.'),
    ('5.0', '5.0 on Google', 'Rated 5.0 from more than 90 Google reviews, over 500 happy customers since 2020.'),
]

def why_section(label, title):
    return f'''    <section class="why-section">
        <div class="section-inner">
            <div class="section-header reveal">
                <p class="section-label">{label}</p>
                <h2 class="section-title">{title}</h2>
            </div>
            <div class="why-grid">
{why(WHY_COMMON)}
            </div>
        </div>
    </section>
'''

def cards_section(label, title, sub, items):
    return f'''    <section>
        <div class="section-inner">
            <div class="section-header reveal">
                <p class="section-label">{label}</p>
                <h2 class="section-title">{title}</h2>
                <p class="section-subtitle">{sub}</p>
            </div>
            <div class="services-grid">
{cards(items)}
            </div>
        </div>
    </section>
'''

def table(head, rows):
    th = ''.join(f'<th>{h}</th>' for h in head)
    trs = '\n'.join('                    <tr>' + ''.join(f'<td{" class=\"price\"" if i == len(r) - 1 else ""}>{c}</td>' for i, c in enumerate(r)) + '</tr>' for r in rows)
    return f'''            <table class="price-table">
                <thead><tr>{th}</tr></thead>
                <tbody>
{trs}
                </tbody>
            </table>'''

AREA = ('<p>We work in all 23 districts of Vienna and in the surrounding area within about 35 minutes of the city, '
        'for example Klosterneuburg, Korneuburg, Mödling, Perchtoldsdorf, Schwechat and Baden. '
        'We don’t offer international moves.</p>')

STEPS = [('Message us', 'Send us photos and both addresses on WhatsApp, in English.'),
         ('Fixed price', 'You get a free fixed-price quote, usually within minutes.'),
         ('Planning', 'We agree on the date and details. A no-parking zone can be arranged on request.'),
         ('Moving day', 'Our team carries, loads and transports your things safely.'),
         ('Done', 'Furniture is reassembled and boxes are in the right rooms.')]

def steps_html(steps):
    return '\n'.join(f'                <div class="process-step reveal"><div class="step-number">{i}</div><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(steps, 1))

HOME = dict(
    key='home', file='index.html', service='Moving company Vienna', price='240', offer='Moves in Vienna from €240',
    title='Movers Vienna – English-Speaking, from €240 | packdas!',
    desc='English-speaking movers in Vienna: own team and truck, furniture assembly included, 24/7 incl. weekends. Fixed price via WhatsApp in minutes. Moves from €240.',
    badge='From €240 · 24/7 · We speak English',
    h1='Moving Company in Vienna – English-speaking movers, fixed price <span class="accent">from €240</span>',
    lead='We move flats, houses and offices in all 23 districts of Vienna and the surrounding area. Send us photos on WhatsApp – in English – and get a fixed price within minutes.',
    watext='Hi packdas! I would like a quote for a move in Vienna.',
    img1=('packdas-team-transporter-wien', 'Three packdas! movers with a hand truck in front of two white vans – moving company Vienna', 1200, 800),
    img2=('packdas-kasten-verladen-transporter', 'Two packdas! movers loading a cabinet into their van', 1400, 933),
    sections=cards_section('Services', 'Everything for your move in Vienna', 'From a studio flat to a full house or office – one team, one fixed price.', [
        ('Flat &amp; house moves', 'Studio, shared flat, family apartment or house: we carry, load, transport and unload.'),
        ('Furniture assembly', 'Taking furniture apart and putting it back together is part of every move – no extra booking needed.'),
        ('Office relocation', 'Offices and organisations: we move desks, cabinets and equipment, also in the evening or at the weekend.'),
        ('No-parking zone', 'No space in front of the building? By arrangement we handle the no-parking zone (application, permit, signs). The cost is shown in your quote.'),
        ('Apartment clearance', 'Leaving Vienna or downsizing? We clear flats, cellars and storage compartments. <a href="/en/apartment-clearance-vienna" style="color:var(--color-accent);">Apartment clearance →</a>'),
        ('Small moves', 'Just a sofa, a fridge or a few boxes? <a href="/en/man-with-a-van-vienna" style="color:var(--color-accent);">Man with a van →</a>'),
    ]) + why_section('Why packdas!', 'Movers who speak your language') + f'''
    <section>
        <div class="section-inner content-block reveal">
            <h2>How much does a move in Vienna cost?</h2>
            <p>A move within Vienna starts at €240. These are typical price ranges; the exact fixed price follows from your photos.</p>
{table(['Type of move', 'Time needed', 'Price (guide)'], [
    ['Studio / single room', '2–3 hours', '€240–340'],
    ['2-room apartment (1 bedroom)', '3–5 hours', '€360–750'],
    ['3-room apartment (2 bedrooms)', '5–7 hours', '€480–900'],
    ['4+ rooms / house', 'Individual', 'On request'],
    ['Office move', 'Individual', 'On request'],
])}
            <p>Where you land within the range depends mostly on how much furniture you have: a 2-room flat with just a sofa and a wardrobe is at the lower end, a fully furnished one at the upper end. Floor, lift and distance matter too. In our experience, an old Viennese building without a lift is the most common reason a move costs more.</p>
            <p>You pay a fixed price, not an hourly rate. Weekends and public holidays cost the same as weekdays.</p>
            <h2>How your move works – 5 steps</h2>
        </div>
    </section>

    <section style="padding-top:0;">
        <div class="section-inner">
            <div class="process-steps">
{steps_html(STEPS)}
            </div>
        </div>
    </section>

    <section>
        <div class="section-inner content-block reveal">
            <h2>Where we work</h2>
            {AREA}
            <h2>New to Vienna? Don’t forget your registration</h2>
            <p>In Austria you must register your new address (Meldezettel) within 3 days of moving in. You can find the details on the <a href="{MELDE}" target="_blank" rel="noopener" style="color:var(--color-accent);">official government page (in German)</a>.</p>
        </div>
    </section>
''',
    faq_title='Questions about moving in Vienna',
    faq=[
        ('Do you speak English?', 'Yes. You can write to us in English on WhatsApp, by email or on the phone. Kamil, the owner, answers personally, and the team on site speaks English, German and Polish.'),
        ('How much does a move in Vienna cost?', 'Moves start at €240. Typical ranges are €240–340 for a studio, €360–750 for a 2-room apartment and €480–900 for a 3-room apartment. Larger flats, houses and offices are priced on request.'),
        ('How do I get a quote?', 'Send us photos of your furniture and both addresses with floor and lift information on WhatsApp. You usually get a fixed-price quote within minutes, free of charge.'),
        ('Is furniture assembly included?', 'Yes. Taking furniture apart and reassembling it is part of our standard moving service.'),
        ('Do you work on weekends?', 'Yes, we work 24/7 including Saturdays, Sundays and public holidays, at no extra charge.'),
        ('Are my belongings insured?', 'Yes. We have transport insurance and business liability insurance.'),
        ('Do you do international moves?', 'No. We move within Vienna and the surrounding area within about 35 minutes of the city.'),
        ('Do I need a no-parking zone?', 'Often it helps, especially in narrow streets. By arrangement we take care of the application, the permit and the signs; the cost is shown in your quote.'),
    ],
    cta_h='Moving in Vienna? Let’s talk.',
    cta_p='Free quote on WhatsApp – fastest with photos. In English, of course.',
)

CLEAR = dict(
    key='clear', file='apartment-clearance-vienna.html', service='Apartment clearance Vienna', price='120', offer='Clearance in Vienna from €120',
    title='Apartment Clearance Vienna | Junk Removal from €120 | packdas!',
    desc='Apartment, cellar and house clearance in Vienna by an English-speaking team: broom-clean handover, eco-friendly disposal, fixed price via WhatsApp. From €120.',
    badge='From €120 · Broom-clean · We speak English',
    h1='Apartment Clearance in Vienna – junk removal at a fixed price <span class="accent">from €120</span>',
    lead='Moving out, leaving Austria or just too much stuff? We clear flats, cellars, attics and offices in Vienna and hand them over broom-clean. Send photos on WhatsApp and get your fixed price.',
    watext='Hi packdas! I would like a quote for an apartment clearance in Vienna.',
    img1=('packdas-kasten-verladen-transporter', 'packdas! team loading a cabinet into their van – apartment clearance Vienna', 1400, 933),
    img2=('packdas-moebelpacker-lkw-wien', 'Two packdas! team members shaking hands in front of their van', 1400, 933),
    sections=cards_section('What we clear', 'Clearance for every situation', 'One fixed price, one team, broom-clean handover.', [
        ('Apartments', 'Whole flats or single rooms – furniture, household items, everything you no longer need.'),
        ('Cellars &amp; storage compartments', 'Cellar compartments, attics and storage compartments cleared and handed over broom-clean.'),
        ('Leaving Vienna', 'Moving abroad and can’t take everything? We clear what stays behind so you can hand back the keys.'),
        ('Offices', 'Old furniture, cabinets and equipment from offices and shops.'),
        ('Eco-friendly disposal', 'We sort and dispose of everything in an environmentally responsible way.'),
        ('Cleaning on request', 'After the clearance the rooms are broom-clean. A final cleaning can be added on request.'),
    ]) + why_section('Why packdas!', 'Clearance without the hassle') + f'''
    <section>
        <div class="section-inner content-block reveal">
            <h2>How much does an apartment clearance in Vienna cost?</h2>
            <p>Clearance in Vienna starts at €120. These are typical price ranges; your fixed price follows from your photos.</p>
{table(['Type of clearance', 'Size', 'Price (guide)'], [
    ['Cellar / storage room', 'up to 15 m²', '€120–220'],
    ['1-room apartment', 'up to 40 m²', '€290–550'],
    ['2–3-room apartment', '40–80 m²', '€450–950'],
    ['Large apartment / house / office', 'Individual', 'On request'],
])}
            <p>The price depends mainly on the amount of small items, whether there is a lift (old buildings without a lift take longer) and whether there is hazardous waste such as paint or chemicals. You pay a fixed price, not per hour or per square metre.</p>
            <h2>Where we work</h2>
            {AREA}
            <p>Moving at the same time? See our <a href="/en/" style="color:var(--color-accent);">moving service in Vienna</a>.</p>
        </div>
    </section>
''',
    faq_title='Questions about apartment clearance',
    faq=[
        ('How much does an apartment clearance in Vienna cost?', 'From €120 for a cellar or storage room. Typical ranges are €290–550 for a 1-room apartment and €450–950 for a 2–3-room apartment. Larger properties are priced on request.'),
        ('How do I get a quote?', 'Send us photos of all rooms and the address with floor and lift information on WhatsApp. You usually get a fixed-price quote within minutes.'),
        ('What happens to the items?', 'We sort everything and dispose of it in an environmentally responsible way.'),
        ('Do you leave the apartment clean?', 'Yes, we hand over the rooms broom-clean. A final cleaning is available on request.'),
        ('Do you speak English?', 'Yes. Write to us in English – Kamil, the owner, answers personally.'),
        ('Can you clear the flat and move me at the same time?', 'Yes. We can combine your move and the clearance of the things you leave behind.'),
    ],
    cta_h='Need a flat cleared? We’re ready.',
    cta_p='Free quote on WhatsApp – fastest with photos of every room.',
)

VAN = dict(
    key='van', file='man-with-a-van-vienna.html', service='Man with a van Vienna', price='90', offer='Small moves in Vienna from €90',
    title='Man with a Van Vienna | Small Moves & Furniture Delivery from €90',
    desc='Man with a van in Vienna: pick-up of willhaben, IKEA and Marketplace furniture, single items and small moves. English-speaking, 24/7, from €90.',
    badge='From €90 · 24/7 · All districts',
    h1='Man with a Van in Vienna – small moves &amp; furniture delivery <span class="accent">from €90</span>',
    lead='Bought a sofa on willhaben or Facebook Marketplace? Need something from IKEA? Moving just a few things? We pick up and deliver across Vienna – also in the evening and at the weekend.',
    watext='Hi packdas! I need a man with a van in Vienna.',
    img1=('packdas-moebelpacker-lkw-wien', 'Two packdas! team members in front of their van – man with a van Vienna', 1400, 933),
    img2=('packdas-team-transporter-wien', 'Three packdas! team members with a hand truck in front of two white vans', 1200, 800),
    sections=cards_section('What we transport', 'Not a full move – just what you need', 'Single items, online purchases and small moves.', [
        ('willhaben &amp; Marketplace', 'Found furniture online? We pick it up from the seller and bring it to you.'),
        ('IKEA &amp; furniture stores', 'No delivery service? We collect your boxes and bring them home.'),
        ('Single furniture items', 'Sofa, wardrobe, bed, desk or dining table – from A to B.'),
        ('Appliances', 'Fridge, washing machine, dishwasher or dryer – transported safely.'),
        ('Bulky items', 'Mattresses, bikes, sports equipment – whatever doesn’t fit in a car.'),
        ('Students &amp; small moves', 'Ideal for moving into a shared flat or student room.'),
    ]) + why_section('Why packdas!', 'The easy way to move a few things') + f'''
    <section>
        <div class="section-inner content-block reveal">
            <h2>How much does a man with a van cost in Vienna?</h2>
            <p style="font-size:1.8rem;font-family:var(--font-display);color:var(--color-accent);margin-bottom:0.5rem;">From €90</p>
            <p>The exact price depends on distance, weight and floor. Send us a photo of the item and both addresses on WhatsApp and you get a fixed price within minutes. For heavy items like fridges or washing machines we recommend our 2-person team.</p>
            <h2>Where we work</h2>
            {AREA}
            <p>Moving a whole apartment? See our <a href="/en/" style="color:var(--color-accent);">moving service in Vienna</a>.</p>
        </div>
    </section>
''',
    faq_title='Questions about small moves',
    faq=[
        ('How much does a man with a van cost in Vienna?', 'From €90, depending on distance, weight and floor. Send a photo on WhatsApp and you get a fixed price within minutes.'),
        ('Can I book you for just one item?', 'Yes. A single armchair, a fridge or a desk – no job is too small.'),
        ('Do you pick up willhaben purchases?', 'Yes. We drive to the seller, load the item and deliver it to you.'),
        ('Can you carry heavy items like washing machines?', 'Yes. For fridges, washing machines and similar items we recommend our 2-person team.'),
        ('Are you available at short notice?', 'Often yes. We are available 24/7, including weekends and public holidays, at no extra charge.'),
        ('Do you speak English?', 'Yes. Write to us in English on WhatsApp – Kamil, the owner, answers personally.'),
        ('Which areas do you cover?', 'All 23 districts of Vienna and the surrounding area within about 35 minutes of the city.'),
    ],
    cta_h='Need a man with a van? We’re ready.',
    cta_p='Free quote on WhatsApp – fastest with a photo.',
)

PAGES = [HOME, CLEAR, VAN]

if __name__ == '__main__':
    for p in PAGES:
        build(p)
