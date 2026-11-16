"""Contract checks for content, SEO, tracking and local assets (stdlib only)."""
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NEW = (ROOT / 'index.html').read_text(encoding='utf-8')
OLD = (ROOT / 'tests/fixtures/before-services.txt').read_text(encoding='utf-8')
EXPECTED = {
    'thai-massage': ['300', '450', '600'],
    'foot-massage': ['350', '550', '700'],
    'head-neck-shoulder': ['400', '650', '700'],
    'deep-tissue': ['400', '650', '750'],
    'oil-massage': ['400', '650', '800'],
    'thai-oil': ['400', '650', '700'],
    'aromatherapy': ['500', '750', '1,000'],
}

class Elements(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

def articles(source):
    return {m[1]: m[2] for m in re.finditer(
        r'<article[^>]+\sid="([^"]+)"[^>]*>(.*?)</article>', source, re.S)}

class RedesignTests(unittest.TestCase):
    def test_exact_prices_and_existing_thai_descriptions(self):
        before, after = articles(OLD), articles(NEW)
        self.assertEqual(set(after), set(EXPECTED))
        for key, prices in EXPECTED.items():
            self.assertEqual(re.findall(r'<b>([\d,]+)</b>', after[key]), prices)
            desc = re.search(r'<p>(.*?)</p>', before[key], re.S)[1]
            self.assertIn('<p class="service-description">' + desc + '</p>', after[key])
            for minutes in (60, 90, 120):
                self.assertIn(str(minutes) + ' นาที', after[key])
            old_names = re.search(r'<h3>(.*?)</h3>', before[key], re.S)[1]
            english = re.search(r'<span class="en">(.*?)</span>', old_names)[1]
            self.assertIn(english, after[key])

    def test_every_service_has_image_and_existing_contact_destinations(self):
        for key, card in articles(NEW).items():
            elements = Elements(card).elements
            images = [a for t, a in elements if t == 'img']
            self.assertEqual(len(images), 1)
            image = images[0]
            self.assertTrue(image['alt'])
            self.assertEqual(image['loading'], 'lazy')
            self.assertTrue(int(image['width']) > 0 and int(image['height']) > 0)
            links = [a for t, a in elements if t == 'a']
            self.assertEqual({a['href'] for a in links}, {
                'https://line.me/R/ti/p/@288ojpuq', 'tel:+66967781585', '/' + key + '/'})
            self.assertTrue((ROOT / key / 'index.html').is_file(), key)
            links = [a for a in links if a.get('class') != 'service-more']
            self.assertTrue(all(a.get('aria-label') for a in links))
            self.assertTrue(all('noopener' in a.get('rel', '')
                                for a in links if a.get('target') == '_blank'))

    def test_tag_manager_installed_once_on_every_page(self):
        for name in ('index.html', '404.html'):
            source = (ROOT / name).read_text(encoding='utf-8')
            head, body = source.split('</head>')
            self.assertEqual(source.count("'GTM-5KD9B98P'"), 1, name)
            self.assertIn('<script id="gtm-loader">', head)
            self.assertIn('track.js" defer></script>', head)
            self.assertIn('googletagmanager.com/ns.html?id=GTM-5KD9B98P', body)
        self.assertTrue((ROOT / 'scripts/track.js').is_file())

    def test_existing_metadata_and_inline_tracking_scripts_are_preserved(self):
        old_head, new_head = OLD.split('</head>')[0], NEW.split('</head>')[0]
        for tag in ('title',):
            self.assertEqual(re.findall(fr'<{tag}.*?</{tag}>', old_head, re.S),
                             re.findall(fr'<{tag}.*?</{tag}>', new_head, re.S))
        self.assertEqual(re.findall(r'<meta\b[^>]*>', old_head),
                         re.findall(r'<meta\b[^>]*>', new_head))
        # Preserve the unrelated promotion script; Places review loading was
        # deliberately replaced with owner-approved, static local review data.
        self.assertEqual(re.findall(r'<script>(.*?)</script>', OLD, re.S)[0],
                         re.findall(r'<script>(.*?)</script>', NEW, re.S)[0])
        for tag, attrs in Elements(OLD).elements:
            if tag == 'script' and 'src' in attrs and attrs['src'] != 'config.js':
                self.assertIn((tag, attrs), Elements(NEW).elements)
        schema_pattern = r'<script type="application/ld\+json">(.*?)</script>'
        self.assertEqual(json.loads(re.search(schema_pattern, OLD, re.S)[1]),
                         json.loads(re.search(schema_pattern, NEW, re.S)[1]))
        old_links = [a for t, a in Elements(old_head).elements if t == 'link']
        new_links = [a for t, a in Elements(new_head).elements if t == 'link']
        self.assertTrue(all(a in new_links for a in old_links))

    def test_navigation_ids_and_existing_outbound_urls_are_preserved(self):
        old_el, new_el = Elements(OLD).elements, Elements(NEW).elements
        old_ids = {a['id'] for _, a in old_el if 'id' in a}
        ids = [a['id'] for _, a in new_el if 'id' in a]
        self.assertEqual(len(ids), len(set(ids)))
        # The obsolete, hidden API attribution is replaced by the dated manual disclosure.
        self.assertTrue((old_ids - {'rv-attr'}) <= set(ids))
        old_urls = {a['href'] for t, a in old_el if t == 'a'}
        new_urls = {a['href'] for t, a in new_el if t == 'a'}
        # Owner replaced this gallery link with the new hotel-entrance photo.
        self.assertTrue((old_urls - {'img/shop-sign-luka-house.jpg'}) <= new_urls)
        for url in new_urls:
            if url.startswith('#'):
                self.assertIn(url[1:], ids)

    def test_local_assets_exist_and_service_images_are_lightweight(self):
        for tag, attrs in Elements(NEW).elements:
            src = attrs.get('src') or (attrs.get('href') if tag == 'link' else None)
            if src and not src.startswith(('http:', 'https:', 'tel:', '#', 'data:')):
                self.assertTrue((ROOT / src.lstrip('/')).is_file(), src)
        for key in EXPECTED:
            path = ROOT / 'img/services' / (key + '.svg')
            tree = ET.parse(path)
            self.assertEqual(tree.getroot().attrib['viewBox'], '0 0 360 220')
            self.assertLess(path.stat().st_size, 6000)
            self.assertNotIn('<script', path.read_text())

    def test_footer_line_icon_and_promotion_are_intact(self):
        footer = NEW.split('<footer>')[1].split('</footer>')[0]
        self.assertRegex(footer, r'class="social-icon social-line"[^>]*href="https://line.me/R/ti/p/@288ojpuq"')
        self.assertIn('aria-label="LINE ของร้านนวลบุษยา"', footer)
        self.assertIn('src="img/line-icon.png"', footer)
        self.assertIn('id="offer-open"', NEW)
        self.assertIn('โปรนวด 2 ชั่วโมง', NEW)
        self.assertIn('ทุกบริการ <strong>ยกเว้นนวดไทย</strong>', NEW)
        self.assertIn('นวดไทยเริ่มต้น 300 บาท / 60 นาที', NEW)

    def test_no_change_outside_scoped_section_head_and_footer(self):
        def normalize(source):
            source = re.sub(r'<!-- Google Tag Manager( \(noscript\))? -->.*?<!-- End Google Tag Manager( \(noscript\))? -->\s*', '', source, flags=re.S)
            source = re.sub(r'  <section id="menu"[^>]*>.*?  </section>', 'SERVICES', source, flags=re.S)
            source = re.sub(r'  <section id="photos"[^>]*>.*?  </section>', 'PHOTOS', source, flags=re.S)
            source = re.sub(r'  <section id="reviews"[^>]*>.*?  </section>', 'REVIEWS', source, flags=re.S)
            source = re.sub(r'<script src="config.js"></script>\s*<script>.*?</script>', '', source, flags=re.S)
            source = re.sub(r'<link rel="stylesheet" href="styles/reviews.css">\s*', '', source)
            source = re.sub(r'<script src="scripts/reviews.js" defer></script>\s*', '', source)
            source = re.sub(r'<link rel="stylesheet" href="styles/outcall.css">\s*', '', source)
            source = re.sub(r'<script src="scripts/outcall.js" defer></script>\s*', '', source)
            source = re.sub(r'<dialog class="offer-dialog" id="outcall-dialog".*?</dialog>', '', source, flags=re.S)
            source = re.sub(r'\n      // Notify the summary only after an actual Places API response\.\n      window\.NUAL_REVIEW_DATA = .*?;\n      window\.dispatchEvent\(new CustomEvent\("nual:reviews-updated", \{ detail: window\.NUAL_REVIEW_DATA \}\)\);', '', source)
            source = re.sub(r'<link rel="stylesheet" href="styles/services.css">\s*', '', source)
            source = re.sub(r'<script src="scripts/services.js" defer></script>\s*', '', source)
            source = re.sub(r'<a class="social-icon social-line".*?</a>',
                '<a href="https://line.me/R/ti/p/@288ojpuq" target="_blank" rel="noopener">LINE</a>', source)
            return re.sub(r'\s+', ' ', source).strip()
        self.assertEqual(normalize(NEW), normalize(OLD))

    def test_entrance_and_parking_photos_follow_owner_instructions(self):
        photos = NEW.split('<section id="photos">')[1].split('</section>')[0]
        self.assertIn('src="img/luka-house-entrance-sign.jpg"', photos)
        self.assertIn('src="img/shop-entrance-luka-house.jpg"', photos)
        self.assertIn('หลังจอดรถ มองเข้ามาที่ตัวอาคารจะเห็นร้านนวลบุษยา', photos)
        self.assertNotIn('src="img/shop-sign-luka-house.jpg"', photos)

if __name__ == '__main__':
    unittest.main(verbosity=2)
