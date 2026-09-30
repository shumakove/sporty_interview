# Specification Issues & Open Questions

Contradictions, gaps and ambiguities found while reviewing the
[Feature Specification](spec/) and the [assignment domain context](assignment/06-domain-context.md).

Each item states the **working assumption** used for testing until the spec is clarified.
Where the application's behaviour differs from the assumption, it is reported as a defect
in the execution results rather than here.

## Summary

| ID     | Type          | Area                  | Title                                                     | Test impact |
|--------|---------------|-----------------------|-----------------------------------------------------------|-------------|
| SPEC-1 | Contradiction | Stake validation      | Minimum stake: €1.00 vs €1.01                             | High        |
| SPEC-2 | Gap           | Receipt / API         | Bet ID and placement timestamp are not in the API response | Medium      |
| SPEC-3 | Contradiction | Match list / API      | Kickoff "date/time" in UI, date-only in API               | Medium      |
| SPEC-4 | Contradiction | Receipt               | Selection on receipt: required in spec, absent in domain context | Low   |
| SPEC-5 | Gap           | Place bet / 409       | No UI behaviour defined for "bet already in progress"     | Medium      |
| SPEC-6 | Gap           | Payout / balance      | Rounding rules for payout are undefined                   | Medium      |
| SPEC-7 | Ambiguity     | API errors            | 400 vs 422 boundary for invalid stake values              | Low         |
| SPEC-8 | Gap           | Filters               | No error copy or timezone defined for filters             | Low         |
| SPEC-9 | Duplication   | Match list            | "New selection replaces previous" stated twice            | None        |

---

## SPEC-1 — Minimum stake: €1.00 vs €1.01

**Type:** Contradiction · **Test impact:** High

| Source                                                     | Value     |
|------------------------------------------------------------|-----------|
| [§3 Business Rules](spec/03-business-rules.md) — "Stake min (per bet)" | **€1.00** |
| [§4.4 UI Error Messaging](spec/04-validation-rules.md#44-ui-error-messaging-minimum-expected-copy) — `Minimum stake is €1.00` | **€1.00** |
| [§4.1 Stake Validation](spec/04-validation-rules.md#41-stake-validation-ui-and-api) — "Minimum €1.01 (positive values)" | **€1.01** |

**Why it matters:** decides whether a €1.00 stake is accepted or rejected, the most
common boundary case for stake. Inconsistent UI and API behaviour here breaks bets or lets
through ones that should be rejected.

**Working assumption:** **€1.00 is the minimum and is accepted**; €0.99 is rejected. Two of
three sources, including the user-facing message, say €1.00; §4.1 looks like a typo.

**Question:** Confirm the minimum stake is €1.00 inclusive and fix §4.1.

## SPEC-2 — Bet ID and placement timestamp are not in the API response

**Type:** Gap · **Test impact:** Medium

- [§2.4 Success Receipt](spec/02-functional-requirements.md#24-success-receipt) requires
  **Bet ID** and **Placement timestamp**.
- [§5.3 `POST /api/place-bet`](spec/05-backend-api.md#post-apiplace-bet) 200 response has
  neither `betId` nor a timestamp field.

**Why it matters:** if the UI generates them client-side, the Bet ID is not a server
reference and can't be used for support, reconciliation or disputes. The timestamp could
reflect the client clock rather than the actual placement time.

**Working assumption:** the receipt shows a non-empty Bet ID and a timestamp close to the
moment of placement. Uniqueness and server origin are not verifiable from the spec.

**Question:** Where do the Bet ID and timestamp come from? Should the API return them?

## SPEC-3 — Kickoff "date/time" in UI, date-only in API

**Type:** Contradiction · **Test impact:** Medium

- [§2.1 Match List](spec/02-functional-requirements.md#21-match-list): each match shows a
  "kickoff date/time label".
- [§5.3 `GET /api/matches`](spec/05-backend-api.md#get-apimatches): `kickoffDate: string (YYYY-MM-DD)`
  has no time component.

**Why it matters:** the rule "upcoming matches only" can't be enforced precisely for
matches that kick off today without a time. A match that has already started may still be
bettable, which contradicts "no live betting".

**Working assumption:** the UI shows the date; a displayed time, if any, isn't validated
against the API.

**Question:** Should the API expose a full kickoff timestamp (with timezone)? How are
today's matches handled after kickoff?

## SPEC-4 — Selection on receipt: required in spec, absent in domain context

**Type:** Contradiction · **Test impact:** Low

- [§2.4 Success Receipt](spec/02-functional-requirements.md#24-success-receipt) lists
  **Selection** among the required fields.
- [Domain Context — Bet Receipt](assignment/06-domain-context.md) lists bet ID, match,
  stake, odds, potential payout and timestamp, without selection.

**Working assumption:** the feature spec is authoritative, so the receipt must show the
selection. It is also the only field that tells the user which outcome they backed.

## SPEC-5 — No UI behaviour defined for "bet already in progress" (409)

**Type:** Gap · **Test impact:** Medium

- [§5.3](spec/05-backend-api.md#post-apiplace-bet) defines `409 bet already in progress (same user)`.
- [§2.3 Place Bet Interaction](spec/02-functional-requirements.md#23-place-bet-interaction)
  only says the button enters `Placing...`. It doesn't say whether the button is disabled,
  and doesn't say what the UI shows on a 409.
- [§2.5 Error Modal](spec/02-functional-requirements.md#25-error-modal): `Rebet` "retries
  placement". It isn't specified whether a retry after a timeout or unknown outcome can
  create a duplicate bet.

**Why it matters:** double submission and retries are classic sources of duplicate bets
and double balance deduction, which means direct financial impact.

**Working assumption:** the button is not clickable while `Placing...` is shown; exactly
one bet is placed and the stake is deducted exactly once per confirmed placement.

**Question:** Expected UI on 409? Is placement idempotent (e.g. via an idempotency key)?

## SPEC-6 — Rounding rules for payout are undefined

**Type:** Gap · **Test impact:** Medium

- [Domain Context — Payout](assignment/06-domain-context.md): `payout = stake × odds`.
- Stake has 2 decimal places and odds may have 2 or more
  ([§3](spec/03-business-rules.md): 1.01–1000.00), so the product can have more than 2 decimals.
- No rounding mode is specified (half-up, half-even, truncate), nor whether it happens on
  the client or the server.

**Why it matters:** differences of €0.01 between the bet slip, the receipt and the API
`payout` are visible to users and cause disputes. Floating-point arithmetic makes this
likely.

**Working assumption:** payout is rounded to 2 decimals, half-up, and is **identical**
across the bet slip, the receipt and the API response.

## SPEC-7 — 400 vs 422 boundary for invalid stake values

**Type:** Ambiguity · **Test impact:** Low

- [§5.3](spec/05-backend-api.md#post-apiplace-bet): `400 malformed payload`,
  `422 semantic validation failures (selection/stake/match)`.
- It isn't specified which of the two a type error returns (e.g. `"stake": "10"`,
  `"stake": null`, `"stake": "abc"`), nor a missing required field.
- "Invalid user context" for `x-user-id` (401) isn't defined: empty string? unknown id?
  format?

**Working assumption:** a body that is not a valid JSON object → 400; well-formed JSON with
wrong or missing field values → 422; missing or empty `x-user-id` → 401. Tests assert on
the 4xx class where the spec is ambiguous and on the exact code only where it is explicit.

## SPEC-8 — No error copy or timezone defined for filters

**Type:** Gap · **Test impact:** Low

- [§2.6 Filters](spec/02-functional-requirements.md#26-filters): the odds filter "must
  reject invalid ranges with clear feedback", but no message text or definition of
  "invalid" is given (min > max? negative? outside 1.01–1000.00?).
- The date filter is inclusive, but no timezone is stated. This matters together with
  SPEC-3.

**Working assumption:** min > max is invalid and shows a visible message; the boundaries
are inclusive on both ends.

## SPEC-9 — "New selection replaces previous" stated twice

**Type:** Duplication · **Test impact:** None

[§2.1 Match List](spec/02-functional-requirements.md#21-match-list) contains both
"Selecting a new odds button replaces the previous selection" and "Clicking new odds
replaces previous selection". This is editorial only; no conflict.
