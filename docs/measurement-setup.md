# Measurement setup — GTM published

Published: 15 November 2026, 22:37 Asia/Bangkok.
Container: GTM-5KD9B98P, version 2 (Live).
Version name: Nualbusaya - GA4 and contact conversions.
Site: https://nualbusaya.com/

## Published configuration

| Tag | Trigger |
| --- | --- |
| GA4 - Google tag - G-2DXDJB8RMT | Initialization - All Pages |
| Google Ads AW-16724394777 | Initialization - All Pages |
| GA4 - contact_click | CE - contact_click (all) |
| Ads - Contact conversions | CE - contact_click (conversion) |
| Conversion Linker - All Pages | All Pages |

GA4 event name: contact_click.
Event parameter: contact_method = {{DLV - contact_method}}.
DLV reads the site's contact_method data-layer value.
Ads conversion ID: 16724394777.
Ads label: {{LT - Ads conversion label}}.

| contact_method | Ads conversion label |
| --- | --- |
| call | 1zfTCJms_7gdEJmG6KY- |
| line | k79fCJys_7gdEJmG6KY- |
| directions | QH-GCJ-s_7gdEJmG6KY- |

Both custom-event triggers listen for contact_click. The Ads trigger additionally requires DLV - contact_method to match ^(call|line|directions)$.
Map/review clicks (method map) go to GA4 but are excluded from Ads contact conversions.
User-provided data capabilities are disabled. No new read-only account links were granted during publish.
The existing site loader and scripts/track.js were retained; no campaign/budget changes were made.

## Verification

- node tests/test_track_runtime.cjs: passed against the current GitHub source snapshot. Classified links: 15 call, 16 line, 3 directions, 6 map. Child-element click pushes exactly one event; unrelated links do not push.
- node --check scripts/track.js: passed.
- Tag Assistant Preview connected to the real domain and detected both destination IDs. GA4 base, Ads base and Conversion Linker each fired once at page load; no console errors were shown in that Preview session.
- GTM Versions UI confirmed version 2 as Live, Latest, published at 22:37 on 15 November 2026, with 5 tags, 2 custom triggers, 2 user variables and 2 settings.
- Contact-click firing on the live site was verified on 22 November 2026 (see "Live click test" below). Receipt inside the GA4 Realtime/DebugView UI and Ads conversion diagnostics was not inspected (the test browser was signed out of Google).

## Live click test (22 Nov 2026)

On https://nualbusaya.com/?nual_qa=1 with navigation suppressed, one call, LINE, directions (`/maps/dir/`) and map (review) link were clicked, and the outgoing requests were read from the page's resource timing:

- Page load: GA4 `page_view` to G-2DXDJB8RMT plus the Ads AW-16724394777 config hits.
- dataLayer received exactly four `contact_click` pushes: call, line, directions, map.
- Google Ads sent one `googleadservices.com/pagead/conversion/16724394777/` hit per conversion method, each with the matching label (call `1zfTCJms…`, line `k79fCJys…`, directions `QH-GCJ-s…`). The map click sent no Ads conversion, as intended.
- GA4 sent `en=contact_click` with `ep.contact_method=map` (a single-event hit); the first four events went out in one batched POST to `/g/collect`.
- Homepage now has no Maps link labelled “นำทาง” with a `?cid=` URL; directions use the `/maps/dir/` link, which classifies correctly.
- These test conversions carry no ad click (no gclid), so they are not attributed to the campaign. They may appear as a few GA4 `contact_click` events on 22 Nov (URL contains `nual_qa=1`).

## Follow-up verification

Use GTM Preview on https://nualbusaya.com/, click call, LINE and directions once each, and confirm GA4 contact_click plus the matching Ads label fire once per event. Review/map clicks must fire GA4 only. Inspect GA4 DebugView/Realtime and Ads diagnostics afterward. Do not treat a tag firing as evidence of an attributed paid-ad conversion.

Change future tagging in GTM and publish a new named version. Avoid adding parallel inline gtag conversion snippets that would duplicate events.
