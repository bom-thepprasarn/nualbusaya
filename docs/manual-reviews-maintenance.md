# Manually curated Google Reviews

This section uses static local data, no Places API, key, subscription, or recurring service.

Source of truth: `data/google-reviews.json`. Run `python tools/render_reviews.py` after an approved manual update to regenerate only the Reviews section of `index.html`.

The overall 5.0 rating and 26-review count were manually checked on the public Nualbusaya listing on 15 November 2026 (Asia/Bangkok). The first three review excerpts and author names were inspected on Google Maps and approved by the owner. The fourth was supplied verbatim and approved by the owner; its individual star rating was not independently confirmed and is therefore omitted. The structured data records this difference in provenance.

The first two cards are explicitly marked as excerpts. Spellings, emojis and meaning are retained. No customer profile images are stored or displayed. Initials are used. Direct review permalinks were not retrievable from the inspected interface; links use the real business profile and are labelled “เปิด Google Maps”, rather than claiming to open a particular review.

For every future edit: inspect the real listing, record the verification date, obtain owner approval for changed review text, preserve attribution and wording, and rerun the tests. Do not add fake reviews, invented star ratings, or self-serving review structured data. If a verified overall rating is unavailable, render the neutral summary state instead.

The carousel supports previous/next buttons, native touch scrolling and keyboard arrows while the track is focused. It has no autoplay and respects reduced-motion preferences.

Outcall service information is owner-authorized. Areas and prices are intentionally unspecified and directed to LINE/telephone enquiries. Its popup waits 60 seconds after the first promotion closes, defers in background tabs, and appears once per tab session.
