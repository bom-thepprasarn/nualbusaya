"""Generate per-service landing pages and the English page from index.html.

Prices, names and descriptions are read from the service cards in index.html,
so a price changed there flows to every generated page on the next build.
Run:  python tools/build_pages.py
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
SITE = "https://nualbusaya.com"
PHONE_TEL = "+66967781585"
PHONE = "096-778-1585"
LINE = "https://line.me/R/ti/p/@288ojpuq"
DIRECTIONS = "https://www.google.com/maps/dir/?api=1&amp;destination=13.9320524,100.7484876"
MAPS = "https://maps.google.com/?cid=15830764363691679197"
GTM = "GTM-5KD9B98P"
TODAY = "2026-11-16"

# Owner-approved wording only; no health or treatment claims.
COPY = {
    "thai-massage": {
        "slug": "thai-massage", "h1": "นวดไทย ลำลูกกา",
        "intro": "นวดไทยแบบดั้งเดิมเพื่อความผ่อนคลาย ใช้การกดและยืดตามแบบนวดไทย ที่ร้านนวลบุษยา ภายในโรงแรม Luka House บึงคำพร้อย ลำลูกกา",
        "points": ["นวดไทยเริ่มต้น 300 บาท / 60 นาที เป็นบริการราคาเริ่มต้นของร้าน",
                   "บอกหมอนวดได้เลยว่าต้องการน้ำหนักมือหนักหรือเบา",
                   "ถ้าต้องการนวดแบบไทยที่ใช้น้ำมันร่วมด้วย เลือกนวดไทยออย"],
        "en_intro": "Traditional Thai massage for relaxation, using the pressing and stretching style of Thai massage.",
        "promo": False,
    },
    "foot-massage": {
        "slug": "foot-massage", "h1": "นวดเท้า ลำลูกกา",
        "intro": "นวดเท้าเพื่อความผ่อนคลาย สำหรับวันที่เดินหรือยืนมาทั้งวัน ที่ร้านนวลบุษยา ภายในโรงแรม Luka House บึงคำพร้อย ลำลูกกา",
        "points": ["เลือกเวลาได้ 60, 90 หรือ 120 นาที",
                   "บอกหมอนวดได้เลยว่าต้องการน้ำหนักมือหนักหรือเบา",
                   "จอดรถในโรงแรมได้ฟรี เดินเข้าร้านได้ทันที"],
        "en_intro": "Foot massage for relaxation after a long day on your feet.",
        "promo": True,
    },
    "head-neck-shoulder": {
        "slug": "head-neck-shoulder", "h1": "นวดศีรษะ คอ บ่า ไหล่ ลำลูกกา",
        "intro": "นวดเฉพาะบริเวณศีรษะ คอ บ่า และไหล่ เพื่อความผ่อนคลาย สำหรับคนที่นั่งทำงานหรือใช้คอมพิวเตอร์ทั้งวัน ที่ร้านนวลบุษยา ลำลูกกา",
        "points": ["เน้นช่วงบนของร่างกาย: ศีรษะ คอ บ่า และไหล่",
                   "บอกหมอนวดได้เลยว่าต้องการน้ำหนักมือหนักหรือเบา",
                   "เลือกเวลาได้ 60, 90 หรือ 120 นาที"],
        "en_intro": "A relaxing massage focused on the head, neck and shoulders.",
        "promo": True,
    },
    "deep-tissue": {
        "slug": "deep-tissue", "h1": "นวดเน้นเฉพาะจุด ลำลูกกา",
        "intro": "นวดเน้นเฉพาะจุดเพื่อความผ่อนคลาย ลงน้ำหนักเฉพาะบริเวณที่คุณต้องการ ที่ร้านนวลบุษยา ภายในโรงแรม Luka House บึงคำพร้อย ลำลูกกา",
        "points": ["บอกหมอนวดได้ว่าอยากให้เน้นบริเวณไหน",
                   "ปรับน้ำหนักมือหนักหรือเบาได้ตามที่ต้องการ",
                   "เลือกเวลาได้ 60, 90 หรือ 120 นาที"],
        "en_intro": "A focused massage for relaxation: tell the therapist which areas to focus on and how firm you like it.",
        "promo": True,
    },
    "oil-massage": {
        "slug": "oil-massage", "h1": "นวดน้ำมัน ลำลูกกา",
        "intro": "นวดน้ำมันด้วยเทคนิคการนวดแบบสากล เพื่อความผ่อนคลาย ที่ร้านนวลบุษยา ภายในโรงแรม Luka House บึงคำพร้อย ลำลูกกา",
        "points": ["การนวดแบบสากลที่ใช้น้ำมัน",
                   "ถ้าต้องการกลิ่นหอมของน้ำมันอโรม่า เลือกนวดอโรม่า",
                   "เลือกเวลาได้ 60, 90 หรือ 120 นาที"],
        "en_intro": "Oil massage using international massage techniques, for relaxation.",
        "promo": True,
    },
    "thai-oil": {
        "slug": "thai-oil", "h1": "นวดไทยออย ลำลูกกา",
        "intro": "นวดด้วยน้ำมัน ผสมผสานเทคนิคการนวดสไตล์ไทย เพื่อความผ่อนคลาย ที่ร้านนวลบุษยา ภายในโรงแรม Luka House บึงคำพร้อย ลำลูกกา",
        "points": ["ท่านวดสไตล์ไทยร่วมกับการใช้น้ำมัน",
                   "บอกหมอนวดได้เลยว่าต้องการน้ำหนักมือหนักหรือเบา",
                   "เลือกเวลาได้ 60, 90 หรือ 120 นาที"],
        "en_intro": "Massage with oil, combined with Thai-style techniques.",
        "promo": True,
    },
    "aromatherapy": {
        "slug": "aromatherapy", "h1": "นวดอโรม่า ลำลูกกา",
        "intro": "นวดด้วยน้ำมันอโรม่าเพื่อความผ่อนคลาย ที่ร้านนวลบุษยา ภายในโรงแรม Luka House บึงคำพร้อย ลำลูกกา",
        "points": ["ใช้น้ำมันอโรม่าระหว่างการนวด",
                   "เลือกเวลาได้ 60, 90 หรือ 120 นาที",
                   "จอดรถในโรงแรมได้ฟรี เปิดทุกวัน 10:00–21:00 น."],
        "en_intro": "Massage with aromatherapy oil, for relaxation.",
        "promo": True,
    },
}


def services():
    out = []
    for m in re.finditer(r'<article class="item service-card" id="([^"]+)".*?</article>', INDEX, re.S):
        key, card = m[1], m[0]
        title = re.search(r'<h3[^>]*>(.*?)<span class="en" lang="en">(.*?)</span></h3>', card, re.S)
        desc = re.search(r'<p class="service-description">(.*?)</p>', card, re.S)[1]
        prices = re.findall(r'<small>(\d+) นาที</small><span class="price-amount"><b>([\d,]+)</b>', card)
        out.append({"key": key, "th": html.unescape(title[1]).strip(), "en": html.unescape(title[2]).strip(),
                    "desc": html.unescape(desc).strip(),
                    "prices": [(int(mn), int(p.replace(",", ""))) for mn, p in prices],
                    **COPY[key]})
    assert len(out) == 7 and all(len(s["prices"]) == 3 for s in out), "service cards changed shape"
    return out


def site_css():
    css = re.search(r"<style>\n(.*?)</style>", INDEX, re.S)[1]
    extra = """
/* generated pages */
.crumbs{font-size:.88rem;color:var(--muted);padding-top:18px}
.crumbs a{color:var(--muted)}
.page-hero{padding:28px 0 8px}
.page-hero h1{font-size:clamp(1.8rem,4vw,2.6rem)}
.page-hero .lead{color:var(--muted);font-size:1.06rem;margin:12px 0 20px;max-width:46em}
.page-grid{display:grid;grid-template-columns:1.2fr 1fr;gap:28px;align-items:start}
@media (max-width:820px){.page-grid{grid-template-columns:1fr}}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:20px 22px}
.panel h2{font-size:1.3rem;margin-bottom:10px}
.price-table{width:100%;border-collapse:collapse;font-size:1rem}
.price-table th,.price-table td{text-align:left;padding:10px 4px;border-bottom:1px solid var(--line)}
.price-table td:last-child,.price-table th:last-child{text-align:right;font-weight:600;color:var(--brown)}
.ticks{margin:8px 0 0;padding-left:1.2em}
.ticks li{margin:4px 0}
.promo-note{background:var(--sage-soft);border-radius:var(--radius);padding:12px 16px;margin-top:14px;font-size:.95rem}
.other-services{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none}
.other-services a{display:inline-block;padding:8px 14px;border:1px solid var(--line);border-radius:999px;background:var(--surface);text-decoration:none;color:var(--brown);font-size:.93rem}
.faq-mini details{border-bottom:1px solid var(--line);padding:10px 0}
.faq-mini summary{cursor:pointer;font-weight:600}
.footer-links{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.9rem}
.footer-links a{color:var(--muted)}
.lang-switch{font-size:.9rem;color:var(--muted)}
"""
    services_css = (ROOT / "styles/services.css").read_text(encoding="utf-8")
    extra += services_css[services_css.index("/* language dropdown"):]
    (ROOT / "styles/site.css").write_text("/* Generated from index.html by tools/build_pages.py; do not edit by hand. */\n" + css + extra, encoding="utf-8")


CARET = '<svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'


def lang_menu(lang, th_href="/", en_href="/en/", root=""):
    """Flag + label dropdown; also used for index.html (root="" keeps relative img paths there)."""
    cur_flag, cur_code = ("th", "TH") if lang == "th" else ("gb", "EN")
    th_cur = ' aria-current="true"' if lang == "th" else ""
    en_cur = ' aria-current="true"' if lang == "en" else ""
    return (f'<details class="lang-menu">\n'
            f'      <summary aria-label="เปลี่ยนภาษา / Change language"><img src="{root}img/flag-{cur_flag}.svg" alt="" width="20" height="14"><span>{cur_code}</span>{CARET}</summary>\n'
            f'      <ul>\n'
            f'        <li><a href="{th_href}" lang="th" hreflang="th"{th_cur}><img src="{root}img/flag-th.svg" alt="" width="20" height="14">ภาษาไทย</a></li>\n'
            f'        <li><a href="{en_href}" lang="en" hreflang="en"{en_cur}><img src="{root}img/flag-gb.svg" alt="" width="20" height="14">English</a></li>\n'
            f'      </ul>\n'
            f'    </details>')


ICON_PIN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 22s7-6.1 7-12a7 7 0 1 0-14 0c0 5.9 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>'


def head(lang, title, desc, path, image, schema, alternates=None):
    url = SITE + path
    alt = ""
    if alternates:
        alt = "".join(f'<link rel="alternate" hreflang="{h}" href="{SITE}{p}">\n' for h, p in alternates)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Google Tag Manager -->
<script id="gtm-loader">(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{GTM}');</script>
<script src="/scripts/track.js" defer></script>
<!-- End Google Tag Manager -->
<script src="/scripts/lang-menu.js" defer></script>
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
{alt}<link rel="icon" type="image/png" sizes="256x256" href="/favicon.png">
<link rel="apple-touch-icon" sizes="256x256" href="/favicon.png">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{SITE}/img/{image}">
<meta property="og:locale" content="{'th_TH' if lang == 'th' else 'en_US'}">
<meta property="og:site_name" content="นวลบุษยา Nualbusaya">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#4e6b55">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;500;600&family=Noto+Serif+Thai:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles/site.css">
<script type="application/ld+json">
{json.dumps(schema, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM}" height="0" width="0" style="display:none;visibility:hidden" title="Google Tag Manager"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
"""


def header(lang, path="/"):
    if lang == "th":
        nav = [("/#menu", "บริการและราคา"), ("/#reviews", "รีวิว"), ("/#faq", "คำถามที่พบบ่อย"), ("/#location", "แผนที่")]
        cta, home = "นำทางมาร้าน", "นวลบุษยา หน้าแรก"
        menu = lang_menu("th", th_href=path, root="/")
    else:
        nav = [("#services", "Services &amp; prices"), ("#visit", "Visit"), ("#faq", "FAQ")]
        cta, home = "Directions", "Nualbusaya home"
        menu = lang_menu("en", root="/")
    links = "\n      ".join(f'<a href="{h}">{t}</a>' for h, t in nav)
    return f"""<header>
  <div class="wrap bar">
    <a class="brand" href="{'/' if lang == 'th' else '/en/'}" aria-label="{home}">
      <img src="/img/icon.png" alt="" width="40" height="40">
      <b>นวลบุษยา</b>
    </a>
    <nav aria-label="{'เมนูหลัก' if lang == 'th' else 'Main menu'}">
      {links}
    </nav>
    <div class="header-actions">
    {menu}
    <a class="btn btn-primary" href="{DIRECTIONS}" target="_blank" rel="noopener" style="padding:9px 16px;font-size:.95rem">{ICON_PIN}{cta}</a>
    </div>
  </div>
</header>
"""


def footer(lang, svc):
    if lang == "th":
        links = "".join(f'<a href="/{s["slug"]}/">{s["th"]}</a>' for s in svc) + '<a href="/outcall/">รับนวดนอกสถานที่</a><a href="/en/" lang="en" hreflang="en">English</a>'
        line = "© 2026 นวลบุษยา Nualbusaya · ร้านนวดลำลูกกา · 63/19 ภายในโรงแรม Luka House ต.บึงคำพร้อย อ.ลำลูกกา จ.ปทุมธานี 12150"
        dock = ("นำทางมาร้าน", "โทร", "LINE")
    else:
        links = '<a href="/" lang="th" hreflang="th">ภาษาไทย</a>'
        line = "© 2026 Nualbusaya · Massage in Lam Luk Ka · 63/19 inside Luka House Hotel, Bueng Kham Phroi, Lam Luk Ka, Pathum Thani 12150"
        dock = ("Directions", "Call", "LINE")
    return f"""<footer>
  <div class="wrap row" style="flex-direction:column;align-items:flex-start;gap:10px">
    <nav class="footer-links" aria-label="{'บริการทั้งหมด' if lang == 'th' else 'Other pages'}">{links}</nav>
    <span>{line}</span>
  </div>
</footer>
<div class="dock" aria-label="{'นำทางและติดต่อร้าน' if lang == 'th' else 'Directions and contact'}">
  <a class="btn btn-primary" href="{DIRECTIONS}" target="_blank" rel="noopener">{dock[0]}</a>
  <a class="btn btn-ghost" href="tel:{PHONE_TEL}">{dock[1]}</a>
  <a class="btn btn-line" href="{LINE}" target="_blank" rel="noopener">{dock[2]}</a>
</div>
</body>
</html>
"""


BUSINESS = {
    "@type": "HealthAndBeautyBusiness", "@id": SITE + "/#business", "name": "นวลบุษยา Nualbusaya",
    "url": SITE + "/", "telephone": "+66967781585",
    "address": {"@type": "PostalAddress", "streetAddress": "63/19 ภายในโรงแรม Luka House ตำบลบึงคำพร้อย",
                "addressLocality": "ลำลูกกา", "addressRegion": "ปทุมธานี", "postalCode": "12150", "addressCountry": "TH"},
}


def contact_buttons(lang="th"):
    t = ("นำทางมาร้าน", f"โทร {PHONE}", "สอบถามคิวทาง LINE") if lang == "th" else ("Directions", f"Call {PHONE}", "Ask on LINE")
    return f"""<div class="btns">
          <a class="btn btn-primary" href="{DIRECTIONS}" target="_blank" rel="noopener">{ICON_PIN}{t[0]}</a>
          <a class="btn btn-ghost" href="tel:{PHONE_TEL}">{t[1]}</a>
          <a class="btn btn-line" href="{LINE}" target="_blank" rel="noopener">{t[2]}</a>
        </div>"""


VISIT_TH = """<ul class="ticks">
            <li>ร้านอยู่ภายในโรงแรม Luka House เลขที่ 63/19 ต.บึงคำพร้อย อ.ลำลูกกา ริมซอยเทศบาลลำลูกกา 6</li>
            <li>ขับรถเข้ามาจอดภายในโรงแรมได้เลย จอดฟรีสำหรับลูกค้า</li>
            <li>เปิดทุกวัน 10:00–21:00 น. ไม่มีวันหยุดประจำสัปดาห์</li>
            <li>หมอนวดประจำร้าน 2 ท่าน แนะนำให้โทรหรือทัก LINE สอบถามคิวก่อนเดินทาง</li>
            <li>ร้านมีใบอนุญาตจากกระทรวงสาธารณสุข หมอนวดมีใบรับรอง</li>
            <li>ชำระเงินด้วยเงินสด โอน หรือพร้อมเพย์</li>
          </ul>"""


def service_page(s, svc):
    path = f"/{s['slug']}/"
    p60 = s["prices"][0][1]
    title = f"{s['h1']} {p60} บาท/60 นาที | นวลบุษยา Luka House"
    desc = f"{s['th']}ที่ร้านนวลบุษยา ในโรงแรม Luka House บึงคำพร้อย ลำลูกกา " + " · ".join(f"{m} นาที {p:,} บาท" for m, p in s["prices"]) + " เปิดทุกวัน 10:00–21:00 น. จอดรถฟรี โทร " + PHONE
    schema = {"@context": "https://schema.org", "@graph": [
        {**BUSINESS},
        {"@type": "Service", "@id": SITE + path + "#service", "name": s["th"], "alternateName": s["en"],
         "serviceType": s["th"], "description": s["intro"], "url": SITE + path,
         "provider": {"@id": SITE + "/#business"}, "areaServed": {"@type": "City", "name": "ลำลูกกา"},
         "offers": [{"@type": "Offer", "name": f"{s['th']} {m} นาที", "price": p, "priceCurrency": "THB", "url": SITE + path}
                    for m, p in s["prices"]]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "นวลบุษยา", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "บริการและราคา", "item": SITE + "/#menu"},
            {"@type": "ListItem", "position": 3, "name": s["th"], "item": SITE + path}]},
    ]}
    rows = "\n".join(f"              <tr><td>{m} นาที</td><td>{p:,} บาท</td></tr>" for m, p in s["prices"])
    points = "\n".join(f"            <li>{html.escape(x)}</li>" for x in s["points"])
    promo = ('<p class="promo-note"><strong>โปรลูกค้าเว็บไซต์:</strong> นวด 2 ชั่วโมง ลด 100 บาท (ทุกบริการ ยกเว้นนวดไทย) แจ้งพนักงานว่า “มาจากเว็บไซต์”</p>'
             if s["promo"] else "")
    others = "".join(f'<li><a href="/{o["slug"]}/">{o["th"]}</a></li>' for o in svc if o["key"] != s["key"]) + '<li><a href="/outcall/">รับนวดนอกสถานที่</a></li>'
    body = f"""<a class="skip-link" href="#top">ข้ามไปเนื้อหาหลัก</a>
{header('th', path)}
<main id="top">
  <div class="wrap crumbs"><a href="/">หน้าแรก</a> › <a href="/#menu">บริการและราคา</a> › {s['th']}</div>
  <section class="page-hero">
    <div class="wrap">
      <div class="eyebrow">ร้านนวด ลำลูกกา · ภายในโรงแรม Luka House</div>
      <h1>{s['h1']}<span class="en" lang="en">{s['en']} · Lam Luk Ka</span></h1>
      <p class="lead">{html.escape(s['intro'])}</p>
      {contact_buttons()}
    </div>
  </section>
  <section style="padding-top:20px">
    <div class="wrap page-grid">
      <div class="panel">
        <h2>ราคา{s['th']}</h2>
        <table class="price-table">
          <thead><tr><th scope="col">ระยะเวลา</th><th scope="col">ราคาต่อท่าน</th></tr></thead>
          <tbody>
{rows}
          </tbody>
        </table>
        {promo}
        <h2 style="margin-top:22px">รายละเอียดบริการ</h2>
        <ul class="ticks">
{points}
        </ul>
      </div>
      <div class="panel">
        <h2>การมาใช้บริการ</h2>
        {VISIT_TH}
        <p style="margin-top:14px"><a href="/#photos">ดูรูปทางเข้าและจุดสังเกตร้าน</a> · <a href="{MAPS}" target="_blank" rel="noopener">เปิดใน Google Maps</a></p>
      </div>
    </div>
  </section>
  <section style="padding-top:0">
    <div class="wrap">
      <div class="panel faq-mini">
        <h2>คำถามเกี่ยวกับ{s['th']}</h2>
        <details><summary>{s['th']}ราคาเท่าไร?</summary><p>{" · ".join(f"{m} นาที {p:,} บาท" for m, p in s["prices"])} ราคาต่อท่าน</p></details>
        <details><summary>ต้องจองคิวก่อนไหม?</summary><p>ร้านมีหมอนวดประจำ 2 ท่าน แนะนำให้โทร {PHONE} หรือทัก LINE @288ojpuq สอบถามคิวก่อนเดินทาง</p></details>
        <details><summary>ร้านอยู่ตรงไหน จอดรถได้ไหม?</summary><p>อยู่ภายในโรงแรม Luka House ต.บึงคำพร้อย อ.ลำลูกกา ขับรถเข้ามาจอดภายในโรงแรมได้ฟรี</p></details>
      </div>
      <h2 style="margin:28px 0 12px;font-size:1.3rem">บริการอื่นของร้าน</h2>
      <ul class="other-services">{others}</ul>
    </div>
  </section>
</main>
"""
    return head("th", title, desc, path, "shop-thai-massage.jpg", schema) + body + footer("th", svc)


def outcall_page(svc):
    path = "/outcall/"
    title = "รับนวดนอกสถานที่ ลำลูกกา | นวลบุษยา Nualbusaya"
    desc = "นวลบุษยา ร้านนวดในโรงแรม Luka House ลำลูกกา รับนวดนอกสถานที่ สอบถามพื้นที่ให้บริการ คิว และราคาทาง LINE @288ojpuq หรือโทร " + PHONE
    schema = {"@context": "https://schema.org", "@graph": [
        {**BUSINESS},
        {"@type": "Service", "name": "รับนวดนอกสถานที่", "alternateName": "Outcall massage", "url": SITE + path,
         "provider": {"@id": SITE + "/#business"}, "areaServed": {"@type": "City", "name": "ลำลูกกา"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "นวลบุษยา", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "รับนวดนอกสถานที่", "item": SITE + path}]},
    ]}
    menu = "".join(f'<li><a href="/{o["slug"]}/">{o["th"]}</a></li>' for o in svc)
    body = f"""<a class="skip-link" href="#top">ข้ามไปเนื้อหาหลัก</a>
{header('th', path)}
<main id="top">
  <div class="wrap crumbs"><a href="/">หน้าแรก</a> › รับนวดนอกสถานที่</div>
  <section class="page-hero">
    <div class="wrap">
      <div class="eyebrow">OUTCALL MASSAGE · ลำลูกกา</div>
      <h1>รับนวดนอกสถานที่ ลำลูกกา<span class="en" lang="en">Outcall massage · Lam Luk Ka</span></h1>
      <p class="lead">นวลบุษยารับนวดนอกสถานที่ พื้นที่ให้บริการ คิว และราคา สอบถามได้ทาง LINE หรือโทร ร้านจะแจ้งรายละเอียดให้ก่อนยืนยันทุกครั้ง</p>
      {contact_buttons()}
    </div>
  </section>
  <section style="padding-top:20px">
    <div class="wrap page-grid">
      <div class="panel">
        <h2>สอบถามอย่างไรให้ได้คำตอบเร็ว</h2>
        <ul class="ticks">
          <li>สถานที่ที่ต้องการให้ไปนวด (ชื่อหมู่บ้าน คอนโด หรือที่พัก)</li>
          <li>วันและเวลาที่สะดวก</li>
          <li>บริการที่ต้องการ และระยะเวลา (60 / 90 / 120 นาที)</li>
          <li>จำนวนคนที่จะนวด</li>
        </ul>
        <p style="margin-top:12px">ส่งรายละเอียดทาง LINE @288ojpuq หรือโทร {PHONE}</p>
      </div>
      <div class="panel">
        <h2>บริการของร้าน</h2>
        <p>ราคานวดที่ร้านดูได้ที่หน้าบริการแต่ละประเภท ส่วนราคานวดนอกสถานที่สอบถามกับร้านโดยตรง</p>
        <ul class="other-services" style="margin-top:12px">{menu}</ul>
      </div>
    </div>
  </section>
</main>
"""
    return head("th", title, desc, path, "shop-thai-massage.jpg", schema) + body + footer("th", svc)


def english_page(svc):
    path = "/en/"
    title = "Massage in Lam Luk Ka · Thai massage from 300 THB | Nualbusaya"
    desc = "Nualbusaya massage shop inside Luka House Hotel, Bueng Kham Phroi, Lam Luk Ka, Pathum Thani. Thai massage from 300 THB / 60 min. Open daily 10:00–21:00. Free parking. Call 096-778-1585."
    schema = {"@context": "https://schema.org", "@graph": [
        {**BUSINESS, "name": "Nualbusaya Massage", "alternateName": "นวลบุษยา",
         "address": {"@type": "PostalAddress", "streetAddress": "63/19 inside Luka House Hotel, Bueng Kham Phroi",
                     "addressLocality": "Lam Luk Ka", "addressRegion": "Pathum Thani", "postalCode": "12150", "addressCountry": "TH"},
         "openingHours": "Mo-Su 10:00-21:00", "priceRange": "฿300–฿1000"},
        {"@type": "WebPage", "url": SITE + path, "inLanguage": "en", "name": title},
    ]}
    cards = []
    for s in svc:
        rows = "".join(f"<tr><td>{m} min</td><td>{p:,} THB</td></tr>" for m, p in s["prices"])
        cards.append(f"""        <div class="panel">
          <h3 style="font-size:1.15rem">{s['en']}<span class="en" lang="th">{s['th']}</span></h3>
          <p style="color:var(--muted);font-size:.95rem;margin:6px 0 8px">{html.escape(s['en_intro'])}</p>
          <table class="price-table"><tbody>{rows}</tbody></table>
        </div>""")
    body = f"""<a class="skip-link" href="#top">Skip to main content</a>
{header('en')}
<main id="top">
  <section class="page-hero">
    <div class="wrap">
      <div class="eyebrow">Massage shop · Lam Luk Ka · inside Luka House Hotel</div>
      <h1>Nualbusaya Massage, Lam Luk Ka<span class="en" lang="th">นวลบุษยา ร้านนวดลำลูกกา</span></h1>
      <p class="lead">A small, quiet massage shop inside Luka House Hotel in Bueng Kham Phroi, Lam Luk Ka. Thai massage from 300 THB for 60 minutes. Open every day 10:00–21:00, with free parking at the hotel.</p>
      {contact_buttons('en')}
    </div>
  </section>
  <section id="services" style="padding-top:20px">
    <div class="wrap">
      <h2>Services &amp; prices<span class="en">Price per person · 60 / 90 / 120 minutes</span></h2>
      <div class="menu" style="margin-top:18px">
{chr(10).join(cards)}
      </div>
      <p class="promo-note"><strong>Website offer:</strong> 100 THB off any 2-hour massage except Thai massage. Tell the staff you found us on the website (“มาจากเว็บไซต์”).</p>
      <p style="margin-top:12px">Outcall massage is also available. Ask on LINE or by phone for areas, availability and prices.</p>
    </div>
  </section>
  <section id="visit" style="padding-top:0">
    <div class="wrap page-grid">
      <div class="panel">
        <h2>Visit us</h2>
        <ul class="ticks">
          <li>63/19 inside Luka House Hotel, Bueng Kham Phroi, Lam Luk Ka, Pathum Thani 12150 (Soi Thetsaban Lam Luk Ka 6)</li>
          <li>Drive in and park inside the hotel. Parking is free for our customers.</li>
          <li>Open daily 10:00–21:00, no weekly holiday</li>
          <li>Licensed by the Ministry of Public Health; our therapists are certified</li>
          <li>Payment: cash, bank transfer or PromptPay</li>
        </ul>
        <p style="margin-top:12px"><a href="{MAPS}" target="_blank" rel="noopener">Open in Google Maps</a></p>
      </div>
      <div class="panel faq-mini" id="faq">
        <h2>FAQ</h2>
        <details><summary>Do I need to book?</summary><p>We have two resident therapists, so please call {PHONE} or message LINE @288ojpuq before you come.</p></details>
        <details><summary>Can I choose the pressure?</summary><p>Yes. Tell your therapist if you prefer firm or light pressure.</p></details>
        <details><summary>Do staff speak English?</summary><p>Please message us on LINE; written messages are the easiest way to arrange your visit.</p></details>
      </div>
    </div>
  </section>
</main>
"""
    return head("en", title, desc, path, "shop-thai-massage.jpg", schema,
                alternates=[("th", "/"), ("en", "/en/"), ("x-default", "/")]) + body + footer("en", svc)


def sitemap(paths):
    urls = "\n".join(f"  <url>\n    <loc>{SITE}{p}</loc>\n    <lastmod>{TODAY}</lastmod>\n  </url>" for p in paths)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n', encoding="utf-8")


def main():
    svc = services()
    site_css()
    paths = ["/"]
    for s in svc:
        out = ROOT / s["slug"] / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(service_page(s, svc), encoding="utf-8")
        paths.append(f"/{s['slug']}/")
    (ROOT / "outcall").mkdir(exist_ok=True)
    (ROOT / "outcall/index.html").write_text(outcall_page(svc), encoding="utf-8")
    (ROOT / "en").mkdir(exist_ok=True)
    (ROOT / "en/index.html").write_text(english_page(svc), encoding="utf-8")
    paths += ["/outcall/", "/en/"]
    sitemap(paths)
    print(f"Generated {len(paths) - 1} pages + styles/site.css + sitemap.xml")


if __name__ == "__main__":
    main()
