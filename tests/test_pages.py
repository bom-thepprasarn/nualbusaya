"""Checks for generated service pages, outcall page and English page."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / 'index.html').read_text(encoding='utf-8')
SERVICES = ['thai-massage', 'foot-massage', 'head-neck-shoulder', 'deep-tissue',
            'oil-massage', 'thai-oil', 'aromatherapy']
PAGES = SERVICES + ['outcall', 'en']
GUIDE = 'guides/aromatherapy-vs-oil-massage'
ALL_PAGES = PAGES + ['guides', GUIDE]
BANNED = 'รีด' + 'เส้น'


def page(slug):
    return (ROOT / slug / 'index.html').read_text(encoding='utf-8')


def card_prices(key):
    card = re.search(r'<article class="item service-card" id="%s".*?</article>' % key, INDEX, re.S)[0]
    return [p.replace(',', '') for p in re.findall(r'<b>([\d,]+)</b>', card)]


class PagesTests(unittest.TestCase):
    def test_generated_pages_are_up_to_date(self):
        before = {s: page(s) for s in ALL_PAGES}
        subprocess.run([sys.executable, str(ROOT / 'tools/build_pages.py')], check=True, capture_output=True)
        for s in ALL_PAGES:
            self.assertEqual(before[s], page(s), f'{s} is stale: run python tools/build_pages.py')

    def test_every_page_has_seo_basics_and_tracking(self):
        for s in ALL_PAGES:
            src = page(s)
            self.assertIn(f'<link rel="canonical" href="https://nualbusaya.com/{s}/">', src)
            self.assertEqual(src.count("'GTM-5KD9B98P'"), 1, s)
            self.assertIn('googletagmanager.com/ns.html?id=GTM-5KD9B98P', src)
            self.assertIn('/scripts/track.js', src)
            self.assertEqual(len(re.findall(r'<h1[ >]', src)), 1, s)
            title = re.search(r'<title>(.*?)</title>', src)[1]
            self.assertLessEqual(len(title), 70, s)
            json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', src, re.S)[1])
            self.assertNotIn(BANNED, src)
            for href in re.findall(r'href="(/[^"#]*)', src):
                target = ROOT / href.lstrip('/')
                self.assertTrue(target.is_file() or (target / 'index.html').is_file(), f'{s}: {href}')

    def test_service_page_prices_match_homepage_cards(self):
        for s in SERVICES:
            src = page(s)
            table = re.search(r'<table class="price-table">.*?</table>', src, re.S)[0]
            got = [p.replace(',', '') for p in re.findall(r'<td>([\d,]+) บาท</td>', table)]
            self.assertEqual(got, card_prices(s), s)
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', src, re.S)[1])
            service = [n for n in schema['@graph'] if n['@type'] == 'Service'][0]
            self.assertEqual([str(o['price']) for o in service['offers']], card_prices(s))

    def test_service_pages_reuse_homepage_photo_galleries(self):
        galleries = {'thai-massage': 3, 'foot-massage': 3, 'head-neck-shoulder': 2, 'aromatherapy': 2, 'deep-tissue': 2, 'oil-massage': 1, 'thai-oil': 1}  # owner photos, 22 Nov 2026
        for slug in SERVICES:
            src = page(slug)
            if slug not in galleries:
                self.assertNotIn('data-service-gallery', src, slug)
                continue
            card = re.search(r'<article class="item service-card" id="%s".*?</article>' % slug, INDEX, re.S)[0]
            home = re.findall(r'src="img/(%s/[^"]+)"' % slug, card)  # the hero slideshow reuses some photos
            self.assertEqual(len(home), galleries[slug], slug)
            self.assertEqual(re.findall(r'src="/img/(%s/[^"]+)"' % slug, src), home)
            for name in home:
                self.assertTrue((ROOT / 'img' / name).is_file(), name)
            self.assertEqual(src.count('data-service-gallery'), 1, slug)
            self.assertIn('service-gallery-prev', src)
            self.assertIn('service-gallery-next', src)
            self.assertIn('1 / %d' % galleries[slug], src)
            self.assertIn('<script src="/scripts/services.js" defer></script>', src)
        for s in ['outcall', 'en']:
            self.assertNotIn('data-service-gallery', page(s), s)

    def test_expanded_landing_pages_follow_seo_brief(self):
        # SEO brief / content calendar, 22 Nov 2026: expanded pages, FAQ mirrored in FAQPage schema.
        expanded = {'deep-tissue': ('ขายดี', ['thai-massage', 'deep-tissue', 'head-neck-shoulder']),
                    'aromatherapy': ('', ['aromatherapy', 'oil-massage', 'thai-oil'])}
        for slug, (title_word, compared) in expanded.items():
            src = page(slug)
            title = re.search(r'<title>(.*?)</title>', src)[1]
            self.assertLessEqual(len(title), 60, slug)
            self.assertIn(title_word, title)
            desc = re.search(r'<meta name="description" content="([^"]*)"', src)[1]
            self.assertLessEqual(len(desc), 130, slug)
            self.assertIn(card_prices(slug)[0], desc)
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', src, re.S)[1])
            faq = [n for n in schema['@graph'] if n['@type'] == 'FAQPage'][0]['mainEntity']
            visible = re.findall(r'<details><summary>(.*?)</summary><p>(.*?)</p></details>', src)
            self.assertEqual([(q['name'], q['acceptedAnswer']['text']) for q in faq],
                             [(q.replace('&quot;', '"'), a.replace('&quot;', '"')) for q, a in visible], slug)
            for h2 in ('เหมาะกับใคร', 'ขั้นตอนการมาใช้บริการ', 'เทียบกับนวดแบบอื่นของร้าน'):
                self.assertIn(h2, src)
            table = re.search(r'<table class="price-table compare-table">.*?</table>', src, re.S)[0]
            for key in compared:
                self.assertIn(f"{int(card_prices(key)[0]):,} บาท", table)
            self.assertEqual(src.count('class="btn btn-book"'), 3)  # top of page, after the content, phone dock
            self.assertNotIn('รีด' + 'เส้น', src)
        # the promo answer is computed from the 120-minute card price
        p120 = int(card_prices('aromatherapy')[-1])
        self.assertIn(f"จาก {p120:,} บาท เหลือ {p120 - 100:,} บาท", page('aromatherapy'))
        # other service pages keep the short template until their own brief
        self.assertNotIn('FAQPage', page('thai-massage'))

    def test_aroma_vs_oil_article(self):
        # Content calendar week 3 (22 Nov 2026): facts and prices come from the homepage cards only.
        src = page(GUIDE)
        title = re.search(r'<title>(.*?)</title>', src)[1]
        self.assertLessEqual(len(title), 70)
        desc = re.search(r'<meta name="description" content="([^"]*)"', src)[1]
        self.assertLessEqual(len(desc), 130)
        self.assertIn('<meta property="og:type" content="article">', src)
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', src, re.S)[1])
        types = [n['@type'] for n in schema['@graph']]
        for t in ('Article', 'BreadcrumbList', 'FAQPage'):
            self.assertIn(t, types)
        faq = [n for n in schema['@graph'] if n['@type'] == 'FAQPage'][0]['mainEntity']
        visible = re.findall(r'<details><summary>(.*?)</summary><p>(.*?)</p></details>', src)
        self.assertEqual([(q['name'], q['acceptedAnswer']['text']) for q in faq], visible)
        table = re.search(r'<table class="price-table compare-table guide-table">.*?</table>', src, re.S)[0]
        rows = re.findall(r'<tr><td>(\d+) นาที</td><td>([\d,]+) บาท</td><td>([\d,]+) บาท</td><td>([\d,]+) บาท</td></tr>', table)
        cols = [[r[i].replace(',', '') for r in rows] for i in (1, 2, 3)]
        self.assertEqual(cols, [card_prices('aromatherapy'), card_prices('oil-massage'), card_prices('thai-oil')])
        a, o = [int(x) for x in card_prices('aromatherapy')], [int(x) for x in card_prices('oil-massage')]
        self.assertIn(f"60 นาทีต่างกัน {a[0] - o[0]:,} บาท", src)
        self.assertIn(f"จาก {a[-1]:,} บาท เหลือ {a[-1] - 100:,} บาท", src)
        self.assertIn('ไม่ใช่การรักษาโรค', src)
        self.assertEqual(src.count('class="btn btn-book"'), 2)  # after the content, phone dock
        # linked from the services it compares, the guides index, every footer and the homepage
        for s in ('aromatherapy', 'oil-massage', 'thai-oil', 'guides'):
            self.assertIn(f'href="/{GUIDE}/"', page(s), s)
        self.assertIn('href="/guides/"', INDEX)
        self.assertNotIn(f'href="/{GUIDE}/"', page('thai-massage'))

    def test_promotion_excludes_thai_massage(self):
        self.assertNotIn('โปรลูกค้าเว็บไซต์', page('thai-massage'))
        for s in SERVICES[1:]:
            self.assertIn('ยกเว้นนวดไทย', page(s))

    def test_hreflang_pairs(self):
        self.assertIn('hreflang="en" href="https://nualbusaya.com/en/"', INDEX)
        self.assertIn('hreflang="th" href="https://nualbusaya.com/"', page('en'))
        self.assertIn('<html lang="en">', page('en'))

    def test_sitemap_lists_every_page(self):
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertIn('<loc>https://nualbusaya.com/</loc>', sitemap)
        for s in ALL_PAGES:
            self.assertIn(f'<loc>https://nualbusaya.com/{s}/</loc>', sitemap)

    def test_homepage_links_every_page(self):
        for s in PAGES:
            self.assertIn(f'href="/{s}/"', INDEX)


if __name__ == '__main__':
    unittest.main(verbosity=2)
