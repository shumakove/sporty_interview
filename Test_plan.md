# Test Plan — Single Bet Placement

## Scope

Single bet placement on desktop web, as described in documentation: match list, bet slip, placement, receipt and the backend API.
The plan is based on the spec only.

## Prioritization approach

Money comes first, then security and limits. Each risk was rated on two axes: **impact** (what it costs the user or the business if something will be broken) and **likelihood** (how often user would hit it).

- **Critical:** high impact that any user can hit in normal use: the core flow, overdrawing the balance, betting on the wrong outcome.
- **High:** serious impact but lower likelihood: boundary off-by-one errors, double submission.
- **Medium:** serious impact, but only reachable by calling the API directly. The reason it's not a hight, usually API is closed for external networks.

Scenarios are ordered by priority, so the top 3 are the ones executed. 
## Summary

| ID | Title | Priority | Type | Executed |
|----|-------|----------|------|----------|
| TC-01 | Place a single bet end-to-end | Critical | Happy path | Yes |
| TC-02 | Stake exceeding available balance is rejected | Critical | Negative | Yes |
| TC-03 | Placed bet matches the selected outcome (1/X/2 → HOME/DRAW/AWAY) | Critical | Functional | Yes |
| TC-04 | Stake min/max boundaries are enforced | High | Boundary | No |
| TC-05 | Double submission places only one bet and deducts stake once | High | Negative | No |
| TC-06 | User context integrity: unauthorized requests rejected, balances isolated | Medium | Security | No |


---

## TC-01 — Place a single bet end-to-end

**Priority:** Critical
**Risk Rationale:** This is the core flow of the feature. If a bet can't be placed, or the receipt and balance don't match what the user saw on the bet slip, the product is broken for every user. The case also covers money correctness on the happy path: the stake is deducted once, and payout = stake × odds is the same on the bet slip and the receipt.

**Preconditions:**
- Balance reset to €125.50 via `POST /api/reset-balance`.
- App opened with `?user-id=<user-id>`.
- Use a match with the `UPCOMING` badge. The list also contains `PAST` matches, which are out of scope for pre-match betting.

**Steps:**
1. Before selecting anything, note the balance in the header and in the bet slip. The bet slip replaces its balance with `Remove All` once a selection is added.
2. In an upcoming match, click the `1` (home) odds button. Note the teams and the odds value.
3. Enter stake `10` in the bet slip's `Stake` field.
4. Check `Total Stake` and `Potential Payout` on the bet slip.
5. Click `Place Bet` and wait for the result. The `Placing...` state can take a few seconds.
6. When the `Bet Placed Successfully!` receipt appears, compare its values with those noted in steps 2–4.
7. Close the receipt.

**Expected Result:**
- Step 1: the header and the bet slip show the same balance, €125.50.
- Step 2: the selection appears in the bet slip with the same match, outcome and odds; the bet count is 1.
- Step 4: `Total Stake` is €10.00; `Potential Payout` = 10 × odds (e.g. odds 2.45 → €24.50).
- Step 5: the button switches to `Placing...` and then resolves to a single success outcome.
- Step 6: the receipt shows a Bet ID, the match (home team first), the selection, stake €10.00, the odds, the payout and a timestamp. All values match steps 2–4.
- Step 7: the balance is €115.50 in both the header and the bet slip, and the bet slip has no active selection.

---

## TC-02 — Stake exceeding available balance is rejected

**Priority:** Critical
**Risk Rationale:** If a stake above the available balance is accepted, the user's balance goes negative. That is a direct financial loss, and any user with a low balance can hit it in normal use. The max stake (€100) is lower than the starting balance (€125.50), so this state is only reachable after a previous bet. That makes it easy to miss in development testing.

**Preconditions:**
- Balance reset to €125.50 via `POST /api/reset-balance`.
- App opened with `?user-id=<user-id>`.

**Steps:**
1. Select any outcome, enter stake `100` and place the bet. Close the receipt.
2. Select any outcome and enter stake `25.51`.
3. Try to click `Place Bet`.
4. Send the same bet via the API: `POST /api/place-bet` with `stake: 25.51`, a valid `matchId` and `selection`.
5. Check the balance (`GET /api/balance` and the UI header).
6. In the UI, change the stake to `25.50` and place the bet.

**Expected Result:**
- Step 1: the bet is placed and the balance is €25.50.
- Steps 2–3: `Insufficient balance` is shown and the bet is not placed.
- Step 4: the API rejects the request with a 4xx error and no bet is created.
- Step 5: the balance is still €25.50 in the API and in the UI.
- Step 6: a stake equal to the full balance is accepted and the balance becomes €0.00.

---

## TC-03 — Placed bet matches the selected outcome (1/X/2 → HOME/DRAW/AWAY)

**Priority:** Critical
**Risk Rationale:** If the 1/X/2 buttons map to the wrong selection, the user ends up backing an outcome they didn't choose. That leads to settlement disputes and refunds. A broken mapping hits every bet on that outcome, so it isn't an edge case. The spec stresses the home/away convention all the way to the receipt, which suggests an area that is easy to get wrong.

**Preconditions:**
- Balance reset to €125.50 via `POST /api/reset-balance`.
- App opened with `?user-id=<user-id>`, browser DevTools → Network tab open.
- Pick a match where the three odds are all different, so a wrong mapping can't hide behind equal values. Note its `homeTeam`, `awayTeam` and `odds` from `GET /api/matches`.

**Steps:**
1. Click `1` on the chosen match, enter stake `2` and place the bet. Check the `place-bet` request/response in Network, then the receipt. Close the receipt.
2. Repeat with `X`.
3. Repeat with `2`.

**Expected Result:**

| Button | Request `selection` | Odds in response and receipt | Receipt |
|--------|---------------------|------------------------------|---------|
| `1` | `HOME` | `odds.home` | Home team first; selection shows the home win |
| `X` | `DRAW` | `odds.draw` | Home team first; selection shows the draw |
| `2` | `AWAY` | `odds.away` | Home team first; selection shows the away win |

- The UI match row and the receipt list the teams in the same order as the API (`homeTeam` vs `awayTeam`).
- Payout on each receipt = €2 × the odds of the selected outcome.
- The final balance is €119.50 (3 × €2 deducted).

---

## TC-04 — Stake min/max boundaries are enforced

**Priority:** High
**Risk Rationale:** Stake limits are €1.00–€100.00 with up to 2 decimals. An off-by-one error lets bets slightly outside the limits through, or blocks valid ones. The loss per bet is small and few users stake exactly at a boundary, so this is High rather than Critical. The spec contradicts itself on the minimum (€1.00 vs €1.01, see SPEC-1), which makes an implementation mistake more likely.

**Preconditions:**
- Balance reset to €125.50 via `POST /api/reset-balance` **before each check** (UI and API separately), so a rejection can't be caused by insufficient balance.
- App opened with `?user-id=<user-id>`.
- Working assumption for the minimum: €1.00 inclusive (SPEC-1).

**Steps:**
For each stake value in the table:
1. Reset the balance.
2. In the UI, select any outcome, enter the stake and try to place the bet.
3. Reset the balance.
4. Send the same stake via `POST /api/place-bet` with a valid `matchId` and `selection`.

**Expected Result:**

| Stake | Boundary | UI | API |
|-------|----------|----|-----|
| `0.99` | just below min | Blocked, `Minimum stake is €1.00` | 4xx, balance unchanged |
| `1.00` | min | Bet placed, balance −€1.00 | 200, `stake: 1` |
| `100.00` | max | Bet placed, balance −€100.00 | 200, `stake: 100` |
| `100.01` | just above max | Blocked, `Maximum stake is €100.00` | 4xx, balance unchanged |
| `1.001` | precision | Input not accepted or blocked | 4xx, balance unchanged |

- Every rejection shows the message for the right rule (min/max), not `Insufficient balance`.
- UI and API agree on every value: nothing the UI blocks is accepted by the API.

---

## TC-05 — Double submission places only one bet and deducts stake once

**Priority:** High
**Risk Rationale:** A double click, or a retry while the bet is `Placing...`, could create two bets and deduct the stake twice. The money impact is serious, but it needs a specific action from the user (double click, slow network, `Rebet` after a timeout), which is why it is High. The spec defines a 409 response but no UI behaviour for it (SPEC-5).

**Preconditions:**
- Balance reset to €125.50 via `POST /api/reset-balance`.
- App opened with `?user-id=<user-id>`, browser DevTools → Network tab open.

**Steps:**
1. **UI:** select any outcome, enter stake `10` and double-click `Place Bet` as fast as possible.
2. Check the Network tab and the balance after the flow resolves.
3. Reset the balance.
4. **API:** send two identical `POST /api/place-bet` requests (stake `10`) for the same user at the same time, e.g. two `curl` calls started in parallel.
5. Check `GET /api/balance`.

**Expected Result:**
- Step 1: after the first click the button shows `Placing...` and ignores further clicks.
- Step 2: exactly one `place-bet` request is sent, one receipt is shown and the balance is €115.50.
- Step 4: one request returns 200; the other returns 409 (bet already in progress).
- Step 5: the balance is €115.50, deducted only once.

> **Note:** two sequential bets are valid. The 409 applies only while the first request is still in progress. If both API calls return 200, check that they actually overlapped before raising a bug; manual timing is unreliable, so this check is a better fit for automation.

---

## TC-06 — User context integrity: unauthorized requests rejected, balances isolated

**Priority:** Medium
**Risk Rationale:** The API identifies the user only by the `x-user-id` header. If requests without a valid user context are accepted, or one user's bet changes another user's balance, money moves on the wrong account. This is not reachable through the normal UI, only by calling the API directly, which lowers the likelihood.

**Preconditions:**
- Two valid user ids: A = `<user-id>` and B = a second id issued for the environment.

> **Note after execution:** the original assumption that the API accepts any non-empty id (SPEC-7) is wrong. Unknown ids are rejected with `{"error":"invalid_user_id"}`. With only one issued id, steps 3–4 (isolation) are blocked; steps 1–2 were checked and pass.
- Balances of A and B reset to €125.50 via `POST /api/reset-balance`.

**Steps:**
1. Call `GET /api/balance` and `POST /api/place-bet` without the `x-user-id` header.
2. Repeat with an empty `x-user-id` header.
3. As user A, place a bet with stake `10` via `POST /api/place-bet`.
4. Call `GET /api/balance` as A and as B.

**Expected Result:**
- Steps 1–2: 401 for every request; no bet is created.
- Step 3: 200, returned `balance` is €115.50.
- Step 4: A's balance is €115.50, B's balance is still €125.50.

## Not in scope / deprioritized

| Risk | Why not in the plan |
|------|---------------------|
| Server-side validation when the UI is bypassed (invalid `selection`, unknown `matchId`, malformed body) | Partly covered by the API checks in TC-02 and TC-04; the rest is a good fit for the API automation test. |
| Payout rounding for stakes/odds with more decimals | The spec defines no rounding rule (SPEC-6), so there is no expected result to test against. Raised as a question instead. |
| Error modal (`Rebet` / `Close` / `X`) | Needs a server failure to trigger, which can't be caused reliably from the UI. Better covered with a mocked API response. |
| Date and odds filters | No money moves; wrong filtering only affects match discovery. |
| Balance reset consistency | A test utility rather than a user feature; it's used as a precondition in every scenario, so a failure would surface right away. |
