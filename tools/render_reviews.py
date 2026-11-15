"""Render owner-approved, manually verified local review data to static HTML."""
from datetime import date
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
STAR_PATH = 'm12 2.5 2.94 5.96 6.58.95-4.76 4.64 1.12 6.55L12 17.51l-5.88 3.09 1.12-6.55L2.48 9.41l6.58-.95z'

def stars(rating):
    parts=[]
    for i in range(5):
        percent = (1-max(0,min(1,rating-i)))*100
        parts.append(f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path class="review-star-empty" d="{STAR_PATH}"/><path class="review-star-fill" style="clip-path:inset(0 {percent:g}% 0 0)" d="{STAR_PATH}"/></svg>')
    return ''.join(parts)

def render(data):
    assert data['approvedByOwner'] is True
    assert 0 < data['overallRating'] <= 5
    assert isinstance(data['totalReviewCount'],int) and data['totalReviewCount'] > 0
    assert len(data['reviews']) == 4
    checked=date.fromisoformat(data['lastManuallyVerified'])
    thai_months=['ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.']
    date_label=f'{checked.day} {thai_months[checked.month-1]} {checked.year+543}'
    rating=f'{data["overallRating"]:.1f}'
    url=escape(data['googleMapsUrl'],quote=True)
    cards=[]
    for index,item in enumerate(data['reviews']):
        assert item['text'] and item['reviewerName']
        if item['rating'] is not None:
            assert 0 < item['rating'] <= 5
        star_row = (f'<div class="review-card-stars review-gold-stars" role="img" aria-label="{item["rating"]} จาก 5 ดาว">{stars(item["rating"])}</div>' if item['rating'] is not None else '')
        source=escape(item['originalReviewUrl'] or item['sourceUrl'],quote=True)
        note='ข้อความบางส่วนจากรีวิว' if item['isExcerpt'] else 'รีวิวจาก Google Maps'
        cards.append(f'''        <article class="curated-review-card" data-review-id="{escape(item['id'],quote=True)}" role="group" aria-roledescription="slide" aria-label="รีวิว {index+1} จาก {len(data['reviews'])} โดย {escape(item['reviewerName'],quote=True)}">
          <div class="curated-review-author"><span class="review-initials" aria-hidden="true">{escape(item['initials'])}</span><h3 id="review-{escape(item['id'])}">{escape(item['reviewerName'])}</h3></div>
          {star_row}
          <blockquote><p>{escape(item['text'])}</p></blockquote>
          <p class="review-excerpt-note">{note}</p>
          <a class="review-original-link" href="{source}" target="_blank" rel="noopener">เปิด Google Maps<span aria-hidden="true"> ↗</span></a>
        </article>''')
    return f'''  <section id="reviews" class="wellness-reviews" aria-labelledby="reviews-title">
    <div class="wrap">
      <div class="review-summary-card" data-verified-rating="{rating}" data-review-count="{data['totalReviewCount']}" data-verified-date="{checked.isoformat()}">
        <div class="review-summary-copy">
          <p class="review-eyebrow" lang="en">GOOGLE REVIEWS</p>
          <h2 id="reviews-title">เสียงจากลูกค้าของเรา</h2>
          <p class="review-intro">อ่านประสบการณ์จากลูกค้าที่มาใช้บริการนวลบุษยาบน Google Maps</p>
          <a class="review-google-cta" id="rv-link" href="{url}" target="_blank" rel="noopener">อ่านรีวิวทั้งหมดบน Google<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true" focusable="false"><path d="M5 12h14m-5-5 5 5-5 5"/></svg></a>
        </div>
        <div class="review-summary-panel" aria-live="polite" aria-atomic="true">
          <div id="review-verified-data">
            <div class="review-score-line"><span class="rv-score" id="rv-score">{rating}</span><span class="review-denominator">/ 5</span></div>
            <div class="stars review-gold-stars" id="rv-stars" role="img" aria-label="{rating} จาก 5 ดาว">{stars(data['overallRating'])}</div>
            <p id="rv-count" class="review-count">จาก {data['totalReviewCount']} รีวิว</p>
            <p class="review-source">คะแนนรีวิวจาก Google Maps</p>
            <p class="review-checked" id="review-checked">ตรวจสอบล่าสุดเมื่อ {date_label}</p>
          </div>
          <div id="review-neutral" class="review-neutral" hidden><p>อ่านเสียงจากลูกค้าของเรา</p><span>บน Google Maps</span></div>
        </div>
      </div>
      <div class="review-carousel-controls">
        <p id="review-position" aria-live="polite" aria-atomic="true">รีวิว 1 จาก {len(data['reviews'])}</p>
        <div class="review-carousel-buttons">
          <button type="button" id="review-prev" aria-label="รีวิวก่อนหน้า" aria-controls="rv-grid" disabled><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="m14 6-6 6 6 6"/></svg></button>
          <button type="button" id="review-next" aria-label="รีวิวถัดไป" aria-controls="rv-grid"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="m10 6 6 6-6 6"/></svg></button>
        </div>
      </div>
      <div class="rv-grid curated-review-grid" id="rv-grid" role="region" aria-roledescription="carousel" aria-label="รีวิวที่คัดเลือกจากลูกค้า" tabindex="0">
{chr(10).join(cards)}
      </div>
      <p class="curated-review-disclosure">คัดเลือกรีวิวจาก Google Maps โดยคงถ้อยคำเดิม · คะแนนและจำนวนรีวิวตรวจสอบด้วยตนเองเมื่อ {date_label}</p>
    </div>
  </section>'''

if __name__=='__main__':
    data=json.loads((ROOT/'data/google-reviews.json').read_text(encoding='utf-8'))
    path=ROOT/'index.html'
    html=path.read_text(encoding='utf-8')
    html,count=re.subn(r'  <section id="reviews".*?  </section>',lambda _:render(data),html,flags=re.S)
    assert count==1
    path.write_text(html,encoding='utf-8')
    print('Rendered 4 approved reviews and dated verified summary from local JSON')
