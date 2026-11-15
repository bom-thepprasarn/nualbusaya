from pathlib import Path
import re
import unittest
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'index.html').read_text(encoding='utf-8')

class OutcallTests(unittest.TestCase):
    def test_service_information_does_not_invent_prices_or_areas(self):
        banner=re.search(r'<aside class="outcall-service".*?</aside>',HTML,re.S)[0]
        self.assertIn('รับนวดนอกสถานที่',banner)
        self.assertIn('สอบถามพื้นที่ให้บริการ คิว และราคา',banner)
        self.assertNotIn('บาท',banner)
        self.assertNotIn('กิโลเมตร',banner)
        self.assertIn('href="https://line.me/R/ti/p/@288ojpuq"',banner)
        self.assertIn('href="tel:+66967781585"',banner)

    def test_popup_is_separate_and_accessible(self):
        dialog=re.search(r'<dialog[^>]*id="outcall-dialog".*?</dialog>',HTML,re.S)[0]
        self.assertIn('aria-labelledby="outcall-title"',dialog)
        self.assertIn('aria-describedby="outcall-description"',dialog)
        self.assertIn('aria-label="ปิดข้อมูลนวดนอกสถานที่"',dialog)
        self.assertIn('id="outcall-title"',dialog)
        self.assertIn('id="outcall-description"',dialog)
        self.assertEqual(HTML.count('id="outcall-dialog"'),1)
        self.assertEqual(HTML.count('id="website-offer"'),1)

if __name__=='__main__':unittest.main(verbosity=2)
