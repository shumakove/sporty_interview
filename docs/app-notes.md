# Application Notes

Observations from a first look at https://qae-assignment-tau.vercel.app/ (app version 1.0.0): the rendered page, the API and the OpenAPI schema. No bets were placed.

## UI structure and locators

The app is a React SPA. Most elements have stable `id` attributes, so no XPath or CSS-class locators are needed.

| Area | Element | Locator |
|------|---------|---------|
| Header | Balance pill (`Balance: €125.50`) | `#header-balance` |
| Match list | Match card | `#match-card-{matchId}` |
| Match list | Odds buttons `1` / `X` / `2` | `#odds-{matchId}-home` / `-draw` / `-away` |
| Match list | Status badge (`PAST` / `TODAY` / `UPCOMING`) | `#match-card-{matchId} .badge` |
| Bet slip | Balance (only while the slip is empty) | `#bet-slip-balance` |
| Bet slip | Selection count | `#bet-slip-count` |
| Bet slip | Remove All (only while a selection exists) | `#bet-slip-remove-all` |
| Bet slip | Per-selection remove | `#bet-slip-selection-remove` |
| Bet slip | Stake input | `#bet-slip-stake-input` |
| Bet slip | Total Stake / Potential Payout | `#bet-slip-total-stake` / `#bet-slip-potential-payout` |
| Bet slip | Place Bet (`Placing...` while in progress) | `#bet-slip-place-bet` |
| Success modal | Root, Bet ID, match, stake, odds, payout, time | `#modal-success`, `#modal-success-bet-id`, `-match`, `-stake`, `-odds`, `-payout`, `-placed-at` |
| Success modal | Close / X | `#modal-success-close` / `#modal-success-close-x` |
| Error modal | Root, message, Rebet, Close, X | `#modal-error`, `#modal-error-message`, `#modal-error-rebet`, `#modal-error-close`, `#modal-error-close-x` |
| Filters | Date / odds toggles | `#date-filter-toggle` / `#odds-filter-toggle` |

## Behaviour relevant to testing

- **Match data:** 103 matches with dates from 2026-02-27 to 2026-12-28. On 2026-09-30, 79 are marked `PAST` and still show clickable odds. Tests must pick an `UPCOMING` match, e.g. the first one from `GET /api/matches` with `kickoffDate` ≥ today.
- **Placement delay:** the UI waits a random 1–4 s before sending `POST /api/place-bet`. UI tests need an explicit wait for the modal, not a fixed sleep.
- **Stake input:** a text field that strips non-digits, turns `,` into `.` and cuts input to 2 decimals. `1.001` can't be typed; it becomes `1.00`.
- **Bet slip balance:** shown only while the slip is empty. With a selection, its place is taken by `Remove All`.
- **Receipt time format:** `Today, HH:MM`.
- **OpenAPI:** `stake` has `minimum: 1`, `maximum: 100`, which confirms €1.00 as the minimum (SPEC-1). Error bodies look like `{ "error": "insufficient_balance", "message": "Insufficient balance" }`.

## To verify during execution

The client code suggests the issues below. Each one must be reproduced through the UI or API with evidence before it goes into the bug report.

| # | Suspected issue | Scenario that covers it |
|---|-----------------|-------------------------|
| 1 | Receipt shows `Away vs Home` instead of `Home vs Away` | TC-01, TC-03 |
| 2 | Receipt payout is `stake × 2` instead of `stake × odds` | TC-01, TC-03 |
| 3 | Receipt has no Selection field (spec §2.4) | TC-01, TC-03 |
| 4 | Balance in the UI is not refreshed after a successful bet (loaded only on page load) | TC-01, TC-02 |
| 5 | Because of #4, the UI's insufficient-balance check uses a stale balance | TC-02 |
| 6 | Bet ID (`#B-xxxxx`) and timestamp are generated on the client (SPEC-2) | TC-01 |
| 7 | `PAST` matches can be bet on | Exploratory |
| 8 | Odds filter excludes matches whose odds equal the min value, so the range isn't inclusive | Exploratory |
