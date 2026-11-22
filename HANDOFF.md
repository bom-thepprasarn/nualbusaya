# Nualbusaya — handoff to Claude

Updated 16 November 2026 (Asia/Bangkok). Live site: https://nualbusaya.com/ . Repository: `bom-thepprasarn/nualbusaya`, branch `main`, static GitHub Pages; `.nojekyll` is present. The owner has explicitly authorized pushing these changes and deploying them, and will review the real domain.

## Latest requested implementation

- Premium Google Reviews summary: verified overall **5.0 / 5, 26 reviews**, last manually checked **15 Nov 2026** on the real Google Maps listing `https://maps.google.com/?cid=15830764363691679197`.
- Four approved review cards in a native scroll-snap carousel, next/previous controls, touch scrolling, keyboard arrows, no autoplay. Initials only; no customer profile images downloaded or reused.
- `data/google-reviews.json` is the source of truth. First three excerpts/names were checked on Maps and explicitly approved in chat. Fourth review, **Jenkittika ' cola**, was supplied by the owner and explicitly requested for inclusion. Its individual stars could not be independently verified, so **rating is null and no stars are rendered on that card**. Keep the supplied spelling “ราคากันเอฃสุดๆ”.
- First two reviews are marked as excerpts. Direct review permalinks were not retrievable; card links are labelled “เปิด Google Maps” and use the real business profile URL. Do not invent permalinks or reviewer ratings.
- Reviews are static/manual, no Google Places API/key/subscription. The obsolete Places reviews loader was removed. No review/aggregateRating structured data was added. Existing visible shop-photo gallery and Maps embed remain.
- Footer LINE image is now **`img/line-icon.png` with real alpha transparency**, not a checkerboard WebP and not the temporary SVG. User explicitly required PNG. Background was removed using built-in imagegen; interior logo/watermark details were preserved. Linked LINE account stays `https://line.me/R/ti/p/@288ojpuq`.
- Outcall massage: banner in Services & Prices and a second dialog. It appears **60 seconds after the first promotion closes**, once per tab session, waits if the page is in the background, and does not overlap the first dialog. No coverage areas, minimum spend or prices were invented. Enquiries use the existing LINE and telephone.
- Owner renamed the service label to **นวดเน้นเฉพาะจุด** (English label and `#deep-tissue` anchor unchanged). On 16 Nov 2026 the owner instructed that the former Thai term must **never** appear anywhere on the site, in ads or in source, because it is legally problematic. The one customer review that contained it is shown as an excerpt with that phrase replaced by “…”; the rest of the wording stays verbatim. Never re-add the term.
- Existing promotion remains: **นวด 2 ชั่วโมง ลด 100 บาท ทุกบริการ ยกเว้นนวดไทย**, tell staff “มาจากเว็บไซต์”. Standard 21 menu prices remain unchanged.

## Editing and testing

No framework/build/lint pipeline or dependencies. Runtime: `index.html`, `styles/*.css`, `scripts/*.js`, `img/`. Shared wellness palette is in `styles/services.css` root tokens. Reviews use `styles/reviews.css` / `scripts/reviews.js`; outcall uses `styles/outcall.css` / `scripts/outcall.js`.

After changing approved review data, run `python tools/render_reviews.py` to update only the static Reviews section in `index.html`. Then:

```powershell
python -m unittest discover -s tests -p test_*.py -v
node tests/test_outcall_runtime.cjs
node tests/test_track_runtime.cjs
node --check scripts/track.js
node --check scripts/reviews.js
node --check scripts/outcall.js
python -m http.server 8766 --bind 127.0.0.1
```

The fixtures under `tests/fixtures/*.txt` are historical source snapshots for regression comparisons. They deliberately use `.txt` so GitHub Pages does not expose duplicate HTML landing pages. QA screenshots and the local-only test harness are excluded via `.gitignore`; no customer profile-photo assets are needed for tests.

Validation completed before pushing: 15 Python checks; actual outcall script tested with a controlled clock for ordering, full 60-second delay, no overlap, close action, once/session, background deferral and reload persistence; JS syntax; browser carousel next/previous/end controls and keyboard; no page overflow at 320/375/768/1280px; neutral summary fallback; no profile images; unchanged regular prices, canonical/meta and promotion script.

## Remaining operational context

- This chat's final response contains the new commit and deployment result. Check the latest GitHub Actions “pages build and deployment” run before making follow-up changes.
- Google review rating/count require future **manual** re-verification. Update the date honestly; do not call them live/automatically updating.
- Do not rewrite customer quotes when renaming the site's own service labels.
- Google Business Profile still showed the older github.io website link when inspected; this task did not change GBP, Google Ads, DNS or billing. Maps listing address/pin was read, not modified.
- Core Web Vitals field data has not been measured.

## Measurement (added 15 Nov 2026)

- Google Tag Manager container **GTM-5KD9B98P** is installed in the `<head>` (`<script id="gtm-loader">`, kept off the plain `<script>` tag so the promotion-script regression test still sees the promotion first) and as a `<noscript>` iframe after `<body>`, on `index.html` and `404.html`.
- `scripts/track.js` pushes `{event: "contact_click", contact_method, link_url, link_section}` on clicks. Methods: `call` (`tel:`), `line` (`line.me`), `directions` (`/maps/dir/` or a Maps link whose text contains “นำทาง”), `map` (other Maps links such as reviews). No personal data is pushed.
- All tag logic (GA4 tag, GA4 `contact_click` event, Google Ads conversions for call/LINE/directions, Conversion Linker) lives in GTM, not in this repo. Change tags there and publish a new container version. If you add a new contact link, keep its `href` pattern recognisable by `classify()` or extend `classify()` and `tests/test_track_runtime.cjs`.
- Historical marketing/account context belongs in the separate marketing repository. Do not copy billing, account or back-office data into this public website source.

## Data Studio dashboard — continue on another workstation

- Read [docs/dashboard-handoff.md](docs/dashboard-handoff.md) for the saved report links, completed work, exact outstanding steps and verification limits.
- The native report is saved in Google Data Studio; its editable source is not stored in GitHub. GA4 is connected; Google Ads connection and final design/QA are unfinished.
- GTM version 2 was published successfully; [docs/measurement-setup.md](docs/measurement-setup.md) records tags, triggers, runtime tests and remaining end-to-end checks.

## Service pages and English page (added 16 Nov 2026)

- `/thai-massage/`, `/foot-massage/`, `/head-neck-shoulder/`, `/deep-tissue/`, `/oil-massage/`, `/thai-oil/`, `/aromatherapy/`, `/outcall/` and `/en/` are **generated** by `python tools/build_pages.py`, together with `styles/site.css` (copied from the inline CSS in `index.html`) and `sitemap.xml`. Never hand-edit them.
- Names, descriptions and prices are read from the service cards in `index.html`. After changing a price or the homepage CSS, rerun the build; `tests/test_pages.py` fails if generated pages are stale or prices disagree.
- Page copy lives in `COPY` inside `tools/build_pages.py`: relaxation wording only, no health/treatment claims, and never the banned former service term.
- Homepage links: “ดูรายละเอียด…” in each service card, outcall card link, header “English”, footer service links, and hreflang th/en/x-default.

## Header language dropdown and photos (16 Nov 2026)

- Header language switch is a `<details class="lang-menu">` dropdown with SVG flags (`img/flag-th.svg`, `img/flag-gb.svg`) always paired with a text label (ภาษาไทย / English). Emoji flags are not used because they do not render on Windows. Markup comes from `lang_menu()` in `tools/build_pages.py`; styles live in `styles/services.css` (copied into `styles/site.css` on build); `scripts/lang-menu.js` only closes it on outside click / Escape.
- `img/luka-house-entrance-sign.jpg` was replaced with the owner's new photo (orange Luka House sign + arrow + shop standee), 900×1200.
- ~~Pending shop-front photo~~ resolved 22 Nov 2026: the owner supplied real photos (see below).

## 17 Nov 2026 — Canva cream / light-blue theme
- Look follows the owner's Canva template "Spa Website in Cream Light Blue Beige". All visual changes live in `styles/theme.css`, loaded last on every page (homepage `<head>` and `tools/build_pages.py` `head()`). Remove that link to roll back the look. HTML structure, links, prices and tracking hooks are unchanged.
- The free-parking callout is Luka House orange with a gentle shine/glow; the motion is off under `prefers-reduced-motion`.
- Copy tidy-up on the owner's request: hero subtitle "ร้านนวดแถวลำลูกกา ต.บึงคำพร้อย", location heading "แผนที่สำหรับเดินทางมาร้าน", soi name removed everywhere (TH + EN), repeated "ไม่มีวันหยุดประจำสัปดาห์" kept only in the FAQ answer about holidays. Customer review text is untouched (verbatim).
- Not adopted from the template: booking form (no booking system behind it), stock model photos, placeholder text.
- Service illustration SVGs recoloured to the cream / light-blue / olive palette (17 Nov 2026).

## 17 Nov 2026 — minimal pass + language separation
- Homepage trimmed: removed repeated hours/parking/price blocks (facts row, services welcome box, hero trust line/tagline), section English subtitles, and filler intros. Prices, contact buttons, reviews and the parking callout are unchanged.
- Thai pages are Thai-only and `/en/` is English-only (proper nouns like Luka House, LINE, Google Maps excepted; header language switch kept).
- Service English names now live in `data-en` on each homepage card `<h3>`; `tools/build_pages.py` reads them from there for `/en/`.

## 22 Nov 2026 — Thai massage photo card
- The homepage Thai massage card (`#thai-massage`) shows the owner's three LINE-album technique photos instead of the illustration, in a swipeable card with previous/next arrows and a “1 / 3” counter. The bed-only room photo was removed on the owner's request (22 Nov).
- Photos: `img/thai-massage/thai-massage-1..3.jpg`, 900×675 (4:3), EXIF/GPS stripped. The gallery frame is 4:3 with `object-fit: contain` so the whole photo is always visible (the owner asked for no cropping); this card's photo is therefore a little taller than the illustrations on other cards.
- Markup is `[data-service-gallery]` in `index.html`; styles are at the end of `styles/services.css` (rerun `python tools/build_pages.py` so `styles/site.css` stays in sync); arrow logic is the second block in `scripts/services.js`. Without JS the photos still scroll by swipe/trackpad and the arrows stay hidden.
- `/thai-massage/` shows the same gallery under the contact buttons. `tools/build_pages.py` (`gallery_from_card`) copies it from the homepage card on build, so edit photos only in `index.html` and rerun the build. Gallery CSS is generic (`.service-gallery …`); page sizing is `.page-gallery` in the build's generated-pages CSS. Other service cards and pages still use the illustration.
- Foot massage (3 photos; the last is portrait and shows with side bars) and head/neck/shoulder (2 photos) cards got the same gallery on 22 Nov 2026, and their service pages pick it up on build. Add a gallery to another card with `python tools/add_service_gallery.py <slug> "<Thai label>" "path.jpg::alt" ...` (resizes to 900 px, strips EXIF), then `python tools/build_pages.py`, and add the slug/count to the gallery maps in `tests/test_pages.py`, `tests/test_redesign.py` and `GALLERY_LABELS` in `tests/test_reviews.py`.

## 22 Nov 2026 — entrance photo galleries (#photos)
- First card is now a 3-photo gallery captioned “ร้านอยู่ด้านในโรงแรม” (was a single sign photo captioned “สังเกตป้ายโรงแรมลูก้าเฮาส์ แล้วขับรถเข้ามาจอดได้เลย”): `img/entrance/hotel-1..3.jpg` = Luka House building and car park, orange street sign with arrow, street view of the entrance.
- Second card “หลังจอดรถ มองเข้ามาที่ตัวอาคารจะเห็นร้านนวลบุษยา” is now a 2-photo gallery of the real shop front (`img/entrance/shop-1..2.jpg`), replacing `img/shop-entrance-luka-house.jpg`.
- Photos are 720 px max, EXIF stripped, shown uncropped in the card's 3:4 frame. `hotel-1.jpg` (originally landscape) was cropped to 3:4 around the LUKA HOUSE sign on the owner's request so it fills the frame like the others. Same gallery markup and arrows as the service cards; extra sizing is the `.shop-photos .service-gallery…` rules at the end of `styles/services.css`.
- Unused images were deleted on 22 Nov 2026 (recoverable from git history): `img/luka-house-entrance-sign.jpg`, `img/shop-sign-luka-house.jpg`, `img/line-icon.webp`, `img/logo-en.png`, and the replaced illustrations `img/services/{thai-massage,foot-massage,head-neck-shoulder}.svg`. `img/shop-entrance-luka-house.jpg` is kept because the homepage JSON-LD `image` list still points to it.
