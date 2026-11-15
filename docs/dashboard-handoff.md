# Data Studio dashboard handoff

Updated 16 November 2026 (Asia/Bangkok).

## Continue the existing report

- Report: [NUALBUSAYA | Marketing & Website Performance](https://datastudio.google.com/reporting/698087ba-3708-4bb8-a5f5-d4eefcf170b1/page/vgdDG)
- Edit: https://datastudio.google.com/reporting/698087ba-3708-4bb8-a5f5-d4eefcf170b1/page/vgdDG/edit
- The report is a native Google Data Studio cloud document, not an asset generated from this repository. Sign in with the same authorized owner account on the next workstation. This commit does not export or back up the report itself.
- Continue this named report. An earlier empty Untitled Report was created before connecting data; it is not the working dashboard.
- Do not make the report public or widen sharing without the owner's instruction.

## Work completed in the browser

- Created and named the report, connected the shop's GA4 property (nualbusaya.com).
- Selected responsive layout.
- Added a Total users scorecard.
- Added daily Total users time series.
- Added channel bar chart: Session default channel group / Total users.
- Added activity table: Event name / Event count.
- Added Thai headings and a data interpretation note.
- Attempted theme customization (warm ivory, muted plum, rounded cards). Visual inspection showed further refinement is still required; do not describe the current draft as finished.
- A date selector exists. The attempt to select This month was not verified as a persistent default; confirm its saved settings.
- Google Ads authorization was started. The owner completed a sign-in challenge and the normal tab returned to the OAuth callback. The connector UI still requested authorization before the session ended, so Ads data source connection is NOT confirmed.

## What remains

1. Open the existing report and confirm its saved state. Last browser action was reloading the editor; browser tools then became unavailable.
2. Complete/refresh the official Google Ads connector, selecting only the Nualbusaya account already used for the shop. Do not select hotel accounts, alter campaigns, budgets or billing.
3. Add Ads spend, clicks, conversions, cost/conversion, daily performance and a campaign table. Label the currency from the actual account. Use Ads-native metrics together; do not join GA4 and Ads totals on campaign name and accidentally multiply rows.
4. Finish professional layout: balanced KPI row, readable Thai labels, compact spacing, plum/gold chart palette, clear distinction between website activity and attributed ad conversions.
5. Inspect GA4 custom definitions. Register event-scoped contact_method if absent and authorized/needed, then refresh source fields after available. Build contact_click charts filtered by method call, line and directions; exclude map/review clicks from contact-lead totals. Do not invent historical breakdowns while that dimension is unavailable.
6. Confirm actual incoming contact events and Ads conversions. See measurement-setup.md for verified setup and limitations.
7. Update the note that currently says Ads is awaiting identity verification once the source is truly connected.
8. Verify date controls, chart sources, filters, desktop/mobile layout, empty-data handling and saved view mode. Data collection began 15 Nov 2026; blank data must not be replaced with sample numbers.
9. Share the final report URL with the owner and record completed checks and remaining limitations here.

## Data integrity

- contact_click measures a click, not a completed call, LINE conversation, booking, store visit or revenue.
- Do not label raw clicks as customers or sales.
- Website tracking was published as GTM version 2 on 15 Nov 2026. See [measurement setup](measurement-setup.md).
- The draft's zero/no-data display does not independently prove the absence of visitors; processing time, source configuration and date range still require checking.
- No finished dashboard QA, paid-ad attribution or downstream conversion receipt has been confirmed.
- Never commit OAuth callback URLs, tokens, passwords, private account details, spend exports or customer data to this public website repository.

## Prompt for the next agent

Continue the existing native Data Studio report linked above. Read this file and docs/measurement-setup.md first. Finish the official Google Ads connection, dashboard design and honest click/conversion reporting. Verify saved state and desktop/mobile behavior. Do not create another report, fabricate data, change Ads spending, or publish private business data to this repository. The owner requested a professional dashboard and has authorized continuing the implementation.
