from pathlib import Path
from html.parser import HTMLParser
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT/'index.html').read_text(encoding='utf-8')
BASE = (ROOT/'tests/fixtures/before-reviews.txt').read_text(encoding='utf-8')
PROOF = json.loads((ROOT/'docs/reviews-verification.json').read_text(encoding='utf-8'))
DATA = json.loads((ROOT/'data/google-reviews.json').read_text(encoding='utf-8'))
SECTION = re.search(r'  <section id="reviews".*?  </section>', HTML, re.S)[0]

GALLERY_LABELS = {'thai-massage': 'นวดไทย', 'foot-massage': 'นวดเท้า', 'head-neck-shoulder': 'นวดศีรษะ คอ บ่า ไหล่'}


class ReviewsTests(unittest.TestCase):
    def test_verified_snapshot_matches_evidence(self):
        self.assertIn(f'data-verified-rating="{PROOF["rating"]:.1f}"', SECTION)
        self.assertIn(f'data-review-count="{PROOF["reviewCount"]}"', SECTION)
        self.assertIn(f'data-verified-date="{PROOF["checkedDate"]}"', SECTION)
        self.assertIn('>5.0</span>', SECTION)
        self.assertIn('จาก 26 รีวิว', SECTION)
        self.assertIn('ตรวจสอบล่าสุดเมื่อ 15 พ.ย. 2569', SECTION)
        self.assertTrue(PROOF['verification'])
        self.assertEqual(PROOF['source'], 'https://maps.google.com/?cid=15830764363691679197')

    def test_copy_and_cta(self):
        for text in ['รีวิวจาก Google', 'เสียงจากลูกค้าของเรา', 'คะแนนรีวิวจาก Google Maps', 'อ่านรีวิวทั้งหมดบน Google']:
            self.assertIn(text, SECTION)
        self.assertIn('href="'+PROOF['source']+'"', SECTION)
        self.assertIn('target="_blank" rel="noopener"', SECTION)
        stars = re.search(r'id="rv-stars".*?</div>', SECTION, re.S)[0]
        self.assertEqual(stars.count('<svg'), 5)
        self.assertIn('aria-label="5.0 จาก 5 ดาว"', stars)

    def test_no_testimonials_or_review_schema_added(self):
        self.assertEqual(SECTION.count('<article class="curated-review-card"'), 4)
        self.assertNotIn('<img', SECTION)
        self.assertTrue(DATA['approvedByOwner'])
        from html import unescape
        for item in DATA['reviews']:
            self.assertIn(item['text'], unescape(SECTION))
            self.assertIn(item['reviewerName'], unescape(SECTION))
        self.assertNotIn('maps.googleapis.com', HTML)
        self.assertNotIn('fetchFields', HTML)
        self.assertNotIn('photoURI', HTML)
        schema = r'<script type="application/ld\+json">(.*?)</script>'
        self.assertEqual(re.search(schema, HTML, re.S)[1], re.search(schema, BASE, re.S)[1])
        self.assertNotIn('aggregateRating', re.search(schema, HTML, re.S)[1])

    def test_only_reviews_and_requested_line_asset_changed(self):
        def normalize(s):
            s = re.sub(r'<!-- Google Tag Manager( \(noscript\))? -->.*?<!-- End Google Tag Manager( \(noscript\))? -->\s*', '', s, flags=re.S)
            # Owner photo galleries (22 Nov 2026) replace these cards' illustrations.
            s = re.sub(r'<div class="service-visual service-gallery" data-service-gallery>.*?src="img/([a-z-]+)/.*?(<span class="service-number" aria-hidden="true">\d+</span>)',
                       lambda m: '<div class="service-visual"> <img src="img/services/%s.svg" alt="ภาพประกอบ%s" width="720" height="440" loading="lazy" decoding="async"> %s'
                       % (m[1], GALLERY_LABELS[m[1]], m[2]), s, flags=re.S)
            s = re.sub(r'  <section id="reviews".*?  </section>', 'REVIEWS', s, flags=re.S)
            s = re.sub(r'<link rel="stylesheet" href="styles/reviews.css">\s*', '', s)
            s = re.sub(r'<script src="scripts/reviews.js" defer></script>\s*', '', s)
            s = re.sub(r'<link rel="stylesheet" href="styles/outcall.css">\s*', '', s)
            s = re.sub(r'<link rel="stylesheet" href="styles/theme.css">\s*', '', s)
            s = re.sub(r'<script src="scripts/outcall.js" defer></script>\s*', '', s)
            s = re.sub(r'<dialog class="offer-dialog" id="outcall-dialog".*?</dialog>', '', s, flags=re.S)
            s = re.sub(r'<aside class="outcall-service".*?</aside>', '', s, flags=re.S)
            s = re.sub(r'<script src="config.js"></script>\s*<script>.*?</script>', '', s, flags=re.S)
            s = re.sub(r'\n      // Notify the summary only after an actual Places API response\.\n      window\.NUAL_REVIEW_DATA = .*?;\n      window\.dispatchEvent\(new CustomEvent\("nual:reviews-updated", \{ detail: window\.NUAL_REVIEW_DATA \}\)\);', '', s)
            s = re.sub(r'img/line-icon\.(?:webp|svg|png)', 'img/line-icon.ASSET', s)
            return re.sub(r'\s+', ' ', s).strip()
        self.assertEqual(normalize(HTML), normalize(BASE))

    def test_individual_ratings_are_not_invented(self):
        fourth = re.search(r'<article[^>]*data-review-id="jenkittika-cola".*?</article>', SECTION, re.S)[0]
        self.assertIsNone(DATA['reviews'][3]['rating'])
        self.assertNotIn('review-card-stars', fourth)
        self.assertNotIn('5 ดาว', fourth)
        for item in DATA['reviews']:
            self.assertNotIn('photo', item)
            self.assertIsNone(item['originalReviewUrl'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
