"""Build a local-only UI harness for verified/neutral review-summary states."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
html = (root/'index.html').read_text(encoding='utf-8')
# The harness lives under qa/: route unchanged production asset paths to root.
html = html.replace('<head>', '<head><base href="/">', 1)
toolbar = '''<aside style="position:fixed;bottom:12px;right:12px;z-index:10000;display:flex;gap:8px;padding:10px;background:white;border:1px solid #62445d;border-radius:8px">
<button onclick="window.NUAL_REVIEW_SUMMARY.update(null)">ทดสอบไม่มีข้อมูลยืนยัน</button>
<button onclick="const c=document.querySelector('.review-summary-card');window.NUAL_REVIEW_SUMMARY.update({verified:true,rating:Number(c.dataset.verifiedRating),count:Number(c.dataset.reviewCount),verifiedAt:c.dataset.verifiedDate+'T00:00:00+07:00',source:'snapshot'})">คืนข้อมูลที่ตรวจสอบแล้ว</button>
</aside>'''
html = html.replace('</body>', toolbar+'</body>')
(root/'qa/reviews-states.html').write_text(html,encoding='utf-8')
scripts = re.findall(r'<script>(.*?)</script>', (root/'index.html').read_text(encoding='utf-8'), re.S)
(root/'tests/inline-scripts.js').write_text('\n'.join(scripts),encoding='utf-8')
print('Built local-only QA state harness and extracted inline scripts')
