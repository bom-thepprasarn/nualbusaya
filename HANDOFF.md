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
- Owner renamed the business's Thai service label **นวดรีดเส้น → นวดเน้นเฉพาะจุด**. Prices, English label and `#deep-tissue` anchor remain unchanged. Genuine customer review wording, including “นวดไทยรีดเส้น”, must remain verbatim.
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
