"""Contract checks for content, SEO, tracking and local assets (stdlib only)."""
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

from redesign_norm import undo_redesign
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
            self.assertIn('data-en="' + english + '"', after[key])
            self.assertNotIn('<span class="en"', after[key])

    def test_every_service_has_image_and_existing_contact_destinations(self):
        for key, card in articles(NEW).items():
            elements = Elements(card).elements
            images = [a for t, a in elements if t == 'img']
            # One illustration per card; Thai, foot and head/neck/shoulder cards are owner photo galleries.
            self.assertEqual(len(images), {'thai-massage': 3, 'foot-massage': 3, 'head-neck-shoulder': 2, 'aromatherapy': 2, 'deep-tissue': 2, 'oil-massage': 1, 'thai-oil': 1}.get(key, 1), key)
            for image in images:
                self.assertTrue(image['alt'])
                self.assertEqual(image['loading'], 'lazy')
                self.assertTrue(int(image['width']) > 0 and int(image['height']) > 0)
                self.assertTrue((ROOT / image['src']).is_file(), image['src'])
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
        fonts = lambda links: [a for a in links if 'fonts.googleapis.com/css2' in a.get('href', '')]
        old_links = [a for t, a in Elements(old_head).elements if t == 'link']
        new_links = [a for t, a in Elements(new_head).elements if t == 'link']
        self.assertTrue(all(a in new_links for a in old_links if a not in fonts(old_links)))
        # 22 Nov 2026 Bright Blue redesign adds Chonburi + Inter; every earlier font stays loaded.
        old_fams = re.findall(r'family=([^&]+)', fonts(old_links)[0]['href'])
        new_fams = re.findall(r'family=([^&]+)', fonts(new_links)[0]['href'])
        self.assertTrue(set(old_fams) <= set(new_fams))
        self.assertIn('Chonburi', new_fams)

    def test_navigation_ids_and_existing_outbound_urls_are_preserved(self):
        old_el, new_el = Elements(OLD).elements, Elements(NEW).elements
        old_ids = {a['id'] for _, a in old_el if 'id' in a}
        ids = [a['id'] for _, a in new_el if 'id' in a]
        self.assertEqual(len(ids), len(set(ids)))
        # The obsolete, hidden API attribution is replaced by the dated manual disclosure.
        self.assertTrue((old_ids - {'rv-attr'}) <= set(ids))
        old_urls = {a['href'] for t, a in old_el if t == 'a'}
        new_urls = {a['href'] for t, a in new_el if t == 'a'}
        # Owner replaced these photo links: hotel-entrance photo (16 Nov), then the hotel and
        # shop-front galleries (22 Nov 2026), which show every photo uncropped.
        replaced = {'img/shop-sign-luka-house.jpg', 'img/luka-house-entrance-sign.jpg', 'img/shop-entrance-luka-house.jpg',
                    'img/shop-welcome.jpg', 'img/shop-interior.jpg'}  # now photo galleries (22 Nov 2026)
        self.assertTrue((old_urls - replaced) <= new_urls)
        for url in new_urls:
            if url.startswith('#'):
                self.assertIn(url[1:], ids)

    def test_local_assets_exist_and_service_images_are_lightweight(self):
        for tag, attrs in Elements(NEW).elements:
            src = attrs.get('src') or (attrs.get('href') if tag == 'link' else None)
            if src and not src.startswith(('http:', 'https:', 'tel:', '#', 'data:')):
                self.assertTrue((ROOT / src.lstrip('/')).is_file(), src)
        for key in EXPECTED:
            if f'img/services/{key}.svg' not in NEW:
                continue  # card uses an owner photo gallery instead (illustration deleted 22 Nov 2026)
            path = ROOT / 'img/services' / (key + '.svg')
            tree = ET.parse(path)
            self.assertEqual(tree.getroot().attrib['viewBox'], '0 0 360 220')
            self.assertLess(path.stat().st_size, 6000)
            self.assertNotIn('<script', path.read_text())
        for src in re.findall(r'<figure class="service-gallery-slide"[^>]*><img src="([^"]+)"', NEW):
            self.assertLess((ROOT / src).stat().st_size, 200_000, src)

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
            source = undo_redesign(source)
            source = re.sub(r'<!-- Google Tag Manager( \(noscript\))? -->.*?<!-- End Google Tag Manager( \(noscript\))? -->\s*', '', source, flags=re.S)
            source = re.sub(r'  <section id="menu"[^>]*>.*?  </section>', 'SERVICES', source, flags=re.S)
            source = re.sub(r'  <section id="photos"[^>]*>.*?  </section>', 'PHOTOS', source, flags=re.S)
            source = re.sub(r'<div class="hero-photo[^"]*">.*?</div>', '<div class="hero-photo">HERO</div>', source, flags=re.S)  # owner hero photo, 22 Nov 2026
            source = source.replace('<br><strong>ร้านอยู่ด้านในโรงแรม</strong>', '')  # owner-requested hero note, 22 Nov 2026
            source = re.sub(r'  <section id="reviews"[^>]*>.*?  </section>', 'REVIEWS', source, flags=re.S)
            source = re.sub(r'<script src="config.js"></script>\s*<script>.*?</script>', '', source, flags=re.S)
            source = re.sub(r'<link rel="stylesheet" href="styles/reviews.css">\s*', '', source)
            source = re.sub(r'<script src="scripts/reviews.js" defer></script>\s*', '', source)
            source = re.sub(r'<link rel="stylesheet" href="styles/outcall.css">\s*', '', source)
            source = re.sub(r'<link rel="stylesheet" href="styles/theme.css">\s*', '', source)
            source = re.sub(r'<script src="scripts/outcall.js" defer></script>\s*', '', source)
            source = re.sub(r'<dialog class="offer-dialog" id="outcall-dialog".*?</dialog>', '', source, flags=re.S)
            source = re.sub(r'\n      // Notify the summary only after an actual Places API response\.\n      window\.NUAL_REVIEW_DATA = .*?;\n      window\.dispatchEvent\(new CustomEvent\("nual:reviews-updated", \{ detail: window\.NUAL_REVIEW_DATA \}\)\);', '', source)
            source = re.sub(r'<link rel="stylesheet" href="styles/services.css">\s*', '', source)
            source = re.sub(r'<script src="scripts/services.js" defer></script>\s*', '', source)
            source = re.sub(r'<script src="scripts/lang-menu.js" defer></script>\s*', '', source)
            source = re.sub(r'<a class="social-icon social-line".*?</a>',
                '<a href="https://line.me/R/ti/p/@288ojpuq" target="_blank" rel="noopener">LINE</a>', source)
            return re.sub(r'\s+', ' ', source).strip()
        self.assertEqual(normalize(NEW), normalize(OLD))

    def test_parking_callout_says_shop_is_inside_hotel(self):
        callout = re.search(r'<p class="parking-callout">(.*?)</p>', NEW)[1]
        self.assertEqual(callout, '<strong>ขับรถเข้ามาจอดภายในโรงแรมลูก้าเฮาส์ได้เลย</strong><br>'
                                  '<strong>ร้านอยู่ด้านในโรงแรม</strong><br>จอดฟรีสำหรับลูกค้าร้านนวลบุษยา')

    def test_photo_slideshows_follow_owner_gifs(self):
        # Owner's slideshow GIFs (22 Nov 2026) rebuilt from the real photos with a CSS crossfade:
        # the oil-first GIF in the hero, the earlier GIF moved to the "about" section.
        def slides(cls):
            block = re.search(r'<div class="%s photo-slideshow">(.*?)</div>' % cls, NEW, re.S)[1]
            return [dict(re.findall(r'([\w-]+)="([^"]*)"', m)) for m in re.findall(r'<img ([^>]*)>', block)]
        hero, about = slides('hero-photo'), slides('about-photo')
        self.assertEqual([i['src'] for i in hero], [
            'img/oil-massage/oil-massage-1.jpg', 'img/deep-tissue/deep-tissue-1.jpg',
            'img/deep-tissue/deep-tissue-2.jpg', 'img/thai-oil/thai-oil-1.jpg',
            'img/aromatherapy/aromatherapy-2.jpg'])
        self.assertEqual([i['src'] for i in about], [
            'img/foot-massage/foot-massage-1.jpg', 'img/thai-massage/thai-massage-3.jpg',
            'img/thai-massage/thai-massage-2.jpg', 'img/thai-massage/thai-massage-1.jpg',
            'img/head-neck-shoulder/head-neck-shoulder-1.jpg'])
        for i in hero + about:
            self.assertTrue((ROOT / i['src']).is_file(), i['src'])
            self.assertTrue(i['alt'])
        self.assertEqual(hero[0].get('fetchpriority'), 'high')
        self.assertTrue(all(i.get('loading') == 'lazy' for i in about))
        theme = (ROOT / 'styles/theme.css').read_text(encoding='utf-8')
        self.assertIn('.hero-photo{border-radius:18px;box-shadow:var(--shadow);aspect-ratio:40/27}', theme)
        self.assertIn('.about-photo.photo-slideshow{aspect-ratio:20/13;max-height:none}', theme)
        self.assertIn('animation:hero-fade 20s linear infinite', theme)  # slowed in the redesign
        self.assertIn('@media (prefers-reduced-motion:reduce){.photo-slideshow img{animation:none}}', theme)

    def test_no_photo_appears_in_two_galleries(self):
        # Owner rule (22 Nov 2026): every service / shop-card photo is used once. The hero and about
        # slideshows are the owner's GIFs rebuilt from these same photos, so they are not galleries.
        slides = re.findall(r'<figure class="service-gallery-slide"[^>]*><img src="([^"]+)"', NEW)
        self.assertEqual(len(slides), len(set(slides)), [s for s in slides if slides.count(s) > 1])

    def test_entrance_and_parking_photos_follow_owner_instructions(self):
        photos = NEW.split('<section id="photos">')[1].split('</section>')[0]
        # 22 Nov 2026 owner photos (Downloads/Nualbusaya/บรรยากาศร้านและทางเข้า): four gallery cards.
        cards = re.findall(r'<figure class="shop-gallery-card">(.*?)</figcaption>', photos, re.S)
        expected = [
            (['entrance/hotel-1', 'entrance/hotel-2', 'entrance/hotel-3'], 'ร้านอยู่ด้านในโรงแรม'),
            (['entrance/shop-1', 'entrance/shop-2'], 'หลังจอดรถ มองเข้ามาที่ตัวอาคารจะเห็นร้านนวลบุษยา'),
            (['entrance/front-1', 'shop-welcome'], 'บรรยากาศเป็นกันเองหน้าร้าน'),
            (['entrance/interior-1', 'entrance/interior-2', 'entrance/interior-3', 'shop-interior'], 'มุมพักผ่อนภายในร้าน')]
        self.assertEqual(len(cards), len(expected))
        for card, (names, caption) in zip(cards, expected):
            self.assertEqual(re.findall(r'src="img/([a-z/-]+(?:-\d)?)\.jpg"', card), names)
            self.assertIn('<figcaption>' + caption, card)
            self.assertIn('1 / %d' % len(names), card)
            for name in names:
                self.assertTrue((ROOT / 'img' / (name + '.jpg')).is_file(), name)
        self.assertNotIn('สังเกตป้ายโรงแรมลูก้าเฮาส์ แล้วขับรถเข้ามาจอดได้เลย', photos)
        self.assertNotIn('src="img/shop-entrance-luka-house.jpg"', photos)
        self.assertNotIn('src="img/shop-sign-luka-house.jpg"', photos)

if __name__ == '__main__':
    unittest.main(verbosity=2)
