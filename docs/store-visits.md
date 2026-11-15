# Store visits measurement

Updated 16 November 2026. Primary business objective: customers find the shop on Google and visit Luka House directly.

## Website implemented

Navigation is the primary header, hero and mobile action-bar CTA. All three open the existing verified coordinate destination through Google Maps directions. The existing contact_click classifier recognizes /maps/dir/ as directions; no tracking code or GTM changes were made. Telephone and LINE remain available. Opening hours, starting price, free hotel parking and entrance-photo links are prominent. Do not imply a guaranteed available therapist or booking.

## Measurement hierarchy

1. Actual visits: ask arriving customers how they found the shop and record anonymous daily counts.
2. Directions clicks: intent proxy only; never label these as actual store visits.
3. Call/LINE clicks: supporting intent signals, not completed conversations or bookings.

Use data/store-visits-template.csv as a blank daily aggregate template, with one row per date/source. Suggested sources: Google (customer-reported), Facebook, referral, returning, walk-by, unknown. Record actual visitors only, using one primary source per person and no names/phones. Keep filled sales/visitor data in a private Sheet, not this public repo. Google-reported arrivals are not automatically paid-ad-attributed arrivals.

## Dashboard follow-up (not implemented)

The existing native Data Studio report remains unfinished; see dashboard-handoff.md. Prioritize verified direction-click counts, Google Ads costs and conversions by action, then separately display customer-reported arrivals from a private daily Sheet. Do not calculate cost per actual paid-ad arrival unless attribution is supported. Do not relabel contact_click totals (including map) as leads. Register contact_method custom dimension if absent, verify receipt, and filter directions explicitly. No claim of eligibility or activation of Google's modeled Store visits conversion has been made.

The report and Google Ads settings were not modified in this change. Live browser/mobile visual QA is unavailable in this session; HTML regression checks preserved scripts, all service-price markup, reviews and favicon settings.
