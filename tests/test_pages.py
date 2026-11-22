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
BANNED = 'รีด' + 'เส้น'


def page(slug):
    return (ROOT / slug / 'index.html').read_text(encoding='utf-8')


def card_prices(key):
    card = re.search(r'<article class="item service-card" id="%s".*?</article>' % key, INDEX, re.S)[0]
    return [p.replace(',', '') for p in re.findall(r'<b>([\d,]+)</b>', card)]


class PagesTests(unittest.TestCase):
    def test_generated_pages_are_up_to_date(self):
        before = {s: page(s) for s in PAGES}
        subprocess.run([sys.executable, str(ROOT / 'tools/build_pages.py')], check=True, capture_output=True)
        for s in PAGES:
            self.assertEqual(before[s], page(s), f'{s} is stale: run python tools/build_pages.py')

    def test_every_page_has_seo_basics_and_tracking(self):
        for s in PAGES:
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
        galleries = {'thai-massage': 3, 'foot-massage': 3, 'head-neck-shoulder': 2}  # owner photos, 22 Nov 2026
        for slug in SERVICES:
            src = page(slug)
            if slug not in galleries:
                self.assertNotIn('data-service-gallery', src, slug)
                continue
            home = re.findall(r'src="img/(%s/[^"]+)"' % slug, INDEX)
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
        for s in PAGES:
            self.assertIn(f'<loc>https://nualbusaya.com/{s}/</loc>', sitemap)

    def test_homepage_links_every_page(self):
        for s in PAGES:
            self.assertIn(f'href="/{s}/"', INDEX)


if __name__ == '__main__':
    unittest.main(verbosity=2)
