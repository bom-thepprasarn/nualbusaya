"""Replace a homepage service card's illustration with an owner photo gallery.

Usage (photos in the order they should appear; alt text after each "::"):
    python tools/add_service_gallery.py foot-massage "นวดเท้า" \
        "C:/path/a.jpg::หมอนวดนวดเท้าให้ลูกค้า" "C:/path/b.jpg::..."

Photos are resized to at most 900 px and saved without EXIF/GPS to
img/<slug>/<slug>-N.jpg. Then rerun `python tools/build_pages.py` so the
service page and styles/site.css pick up the gallery.
"""
import html
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PREV = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2"><path d="m15 6-6 6 6 6"/></svg>'
NEXT = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 6 6 6-6 6"/></svg>'


def save_photos(slug, sources):
    out_dir = ROOT / "img" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for i, (src, alt) in enumerate(sources, 1):
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        im.thumbnail((900, 900), Image.LANCZOS)
        name = f"{slug}-{i}.jpg"
        im.save(out_dir / name, "JPEG", quality=78, optimize=True, progressive=True)  # no exif => stripped
        saved.append((name, alt, im.width, im.height))
    return saved


def gallery_html(slug, label, number, photos):
    n = len(photos)
    figs = "\n".join(
        f'              <figure class="service-gallery-slide" aria-label="รูปที่ {i} จาก {n}"><img src="img/{slug}/{name}" '
        f'alt="{html.escape(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async"></figure>'
        for i, (name, alt, w, h) in enumerate(photos, 1))
    return f'''          <div class="service-visual service-gallery" data-service-gallery>
            <div class="service-gallery-track" tabindex="0" role="region" aria-roledescription="carousel" aria-label="รูป{label}ที่ร้านนวลบุษยา ปัดหรือกดลูกศรเพื่อดูรูปถัดไป">
{figs}
            </div>
            <button class="service-gallery-btn service-gallery-prev" type="button" aria-label="รูปก่อนหน้า" hidden>{PREV}</button>
            <button class="service-gallery-btn service-gallery-next" type="button" aria-label="รูปถัดไป" hidden>{NEXT}</button>
            <span class="service-gallery-count" aria-hidden="true">1 / {n}</span>
            <span class="service-number" aria-hidden="true">{number}</span>
          </div>'''


def main(slug, label, *specs):
    sources = [tuple(s.split("::", 1)) for s in specs]
    assert sources and all(len(s) == 2 and s[1].strip() for s in sources), "each photo needs path::alt"
    index = ROOT / "index.html"
    src = index.read_text(encoding="utf-8")
    card = re.search(rf'<article class="item service-card" id="{re.escape(slug)}".*?</article>', src, re.S)
    assert card, f"no service card {slug}"
    visual = re.search(r'          <div class="service-visual[^"]*"[^>]*>.*?<span class="service-number" aria-hidden="true">(\d+)</span>\n          </div>',
                       card[0], re.S)
    assert visual, "card visual not found"
    photos = save_photos(slug, sources)
    new_visual = gallery_html(slug, label, visual[1], photos)
    badge = re.search(r'\n\s*<span class="service-badge">.*?</span>', visual[0])
    if badge:  # keep a card badge such as "ขายดี"
        new_visual = new_visual.replace('\n            <span class="service-number"',
                                        badge[0] + '\n            <span class="service-number"', 1)
    new_card = card[0].replace(visual[0], new_visual, 1)
    index.write_text(src.replace(card[0], new_card, 1), encoding="utf-8", newline="\n")
    for name, _, w, h in photos:
        print(f"img/{slug}/{name} {w}x{h}")


if __name__ == "__main__":
    main(*sys.argv[1:])
