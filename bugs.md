# Bug Reports — Single Bet Placement

**Environment:** https://qae-assignment-tau.vercel.app/ (app v1.0.0), desktop Chrome, user `candidate-MLoeV1nkAvwG`, 2026-09-30.

## Summary

| ID | Title | Severity | Found in |
|----|-------|----------|----------|
| BUG-02 | API accepts stakes above the available balance; balance goes negative | Critical | TC-02 |
| BUG-03 | API accepts a negative stake and increases the balance | Critical | Exploratory |
| BUG-04 | Bets are accepted on past matches | Critical | Exploratory |
| BUG-01 | Balance in the header is not updated after a bet is placed | High | TC-01 |
| BUG-05 | Receipt shows payout as stake × 2 instead of stake × odds | High | TC-01 |
| BUG-06 | Receipt lists the teams in reverse order (away vs home) | High | TC-01 |

---

## BUG-01 — Balance in the header is not updated after a bet is placed

**Severity:** High

**Preconditions:** Balance reset via `POST /api/reset-balance`; app opened with `?user-id=<user-id>`.

**Reproduction Steps:**
1. Note the balance in the header (`Balance: €120.00`).
2. On an upcoming match (Tottenham vs Liverpool), click `1`, enter stake `10`.
3. Click `Place Bet` and wait for the `Bet Placed Successfully!` receipt.
4. Check the header balance, with the receipt open and after closing it.
5. Call `GET /api/balance` for the same user.

**Expected Result:** The header shows the balance reduced by the stake, €110.00, matching the server.

**Actual Result:** The header still shows €120.00. The bet slip balance also stays at €120.00. The server returns `{"balance":110,"currency":"EUR"}`, so the stake was deducted on the backend; only the UI is stale. The correct value appears only after a page reload.

**Business Impact:** Users see more money than they actually have. They can't trust the displayed balance, and the gap grows with every bet in the session. The bet slip validates the stake against this stale value, so together with BUG-02 a user can overdraw through the normal UI: after a €100 bet the UI still shows €120 and lets another €100 through, which the server accepts.

**Evidence:** [evidence/BUG-01-balance-not-updated.png](evidence/BUG-01-balance-not-updated.png): header shows €120.00 after a successful €10 bet, while the API returns €110.

---

## BUG-02 — API accepts stakes above the available balance; balance goes negative

**Severity:** Critical

**Preconditions:** Balance reset via `POST /api/reset-balance` (persisted balance: €120). Header `x-user-id: <user-id>` on every request.

**Reproduction Steps:**
1. `POST /api/place-bet` with `{"matchId": "premier-league-tottenham-liverpool-2026-10-01", "selection": "HOME", "stake": 100}`. Balance is now €20.
2. Send the same request with `"stake": 50`.
3. Send it again with `"stake": 20.02`, then `"stake": 20.01`.
4. Call `GET /api/balance`.

**Expected Result:** Steps 2–3 are rejected with a 4xx and `Insufficient balance` (spec §4.1: stake must not exceed available balance, UI + API). The balance stays at €20.

**Actual Result:** Every request returns `200 Bet placed successfully`, and the balance goes negative: €20 → −€30 → −€50.02 → −€70.03. `GET /api/balance` confirms `{"balance":-70.03,"currency":"EUR"}`. The server has no balance check at all; it isn't an off-by-one error at the boundary.

**Business Impact:** Anyone can bet money they don't have with a single API call, bypassing the UI check. This is a direct and unlimited financial loss for the operator.

**Evidence:** Reproduced with `curl` and by the automated test `tests/api/test_insufficient_balance.py`. Response to step 2:
```json
{"message":"Bet placed successfully","matchId":"premier-league-tottenham-liverpool-2026-10-01","selection":"HOME","stake":50,"odds":2.75,"payout":137.5,"balance":-30,"currency":"USD"}
```

---

## BUG-03 — API accepts a negative stake and increases the balance

**Severity:** Critical

**Preconditions:** Balance reset via `POST /api/reset-balance` (persisted balance: €120). Header `x-user-id: <user-id>`.

**Reproduction Steps:**
1. `POST /api/place-bet` with `{"matchId": "premier-league-tottenham-liverpool-2026-10-01", "selection": "HOME", "stake": -5}`.
2. Call `GET /api/balance`.

**Expected Result:** 422, the same as for `0` or `0.99` (`Stake must be at least 1.00.`). The balance stays at €120.

**Actual Result:** `200 Bet placed successfully` with `"stake":-5, "payout":-13.75, "balance":125`. The balance grows by €5. The minimum check rejects `0` and `0.99` but lets negative values through.

**Business Impact:** Any user can add unlimited money to their balance by repeating the request. This is a direct financial loss for the operator.

**Evidence:** Response to step 1:
```json
{"message":"Bet placed successfully","matchId":"premier-league-tottenham-liverpool-2026-10-01","selection":"HOME","stake":-5,"odds":2.75,"payout":-13.75,"balance":125,"currency":"USD"}
```

---

## BUG-04 — Bets are accepted on past matches

**Severity:** Critical

**Preconditions:** Header `x-user-id: <user-id>`. Match `premier-league-manutd-chelsea` has `kickoffDate: 2026-02-27` and is marked `PAST` in the UI.

**Reproduction Steps:**
1. Open the app. Scroll to Manchester Utd vs Chelsea (`PAST`, Fri 27 Feb) and check that the odds buttons are clickable.
2. `POST /api/place-bet` with `{"matchId": "premier-league-manutd-chelsea", "selection": "HOME", "stake": 1}`.

**Expected Result:** Past matches can't be selected in the UI, and the API rejects the bet. The spec allows upcoming, pre-match events only (§1, §3).

**Actual Result:** The odds buttons of past matches are active in the UI (79 of 103 matches are `PAST`). The API returns `200 Bet placed successfully` and deducts the stake.

**Business Impact:** Users can bet on matches whose result is already known and win every time. This is a direct financial loss for the operator.

**Evidence:** Response to step 2:
```json
{"message":"Bet placed successfully","matchId":"premier-league-manutd-chelsea","selection":"HOME","stake":1,"odds":2.45,"payout":2.45,"balance":119,"currency":"USD"}
```

---

## BUG-05 — Receipt shows payout as stake × 2 instead of stake × odds

**Severity:** High

**Preconditions:** App opened with `?user-id=<user-id>`.

**Reproduction Steps:**
1. On Tottenham vs Liverpool, click `1` (odds 2.75) and enter stake `10`.
2. Note `Potential Payout` on the bet slip: €27.50.
3. Click `Place Bet` and check `Potential Payout` on the receipt.

**Expected Result:** The receipt shows €27.50 (10 × 2.75), the same as the bet slip and the API response (`"payout": 27.5`).

**Actual Result:** The receipt shows €20.00, which is stake × 2 regardless of the odds.

**Business Impact:** The receipt is the user's confirmation of the bet. A wrong payout there leads to disputes and support tickets, and users stop trusting the confirmation.

**Evidence:** [evidence/BUG-05-06-receipt.png](evidence/BUG-05-06-receipt.png): the receipt shows odds 2.75, stake €10.00 and payout €20.00. Also reproduced by `tests/ui/test_place_bet.py`.

---

## BUG-06 — Receipt lists the teams in reverse order (away vs home)

**Severity:** High

**Preconditions:** App opened with `?user-id=<user-id>`.

**Reproduction Steps:**
1. On Tottenham (home) vs Liverpool (away), click `1` and place a bet with stake `10`.
2. Check the `Match` field on the receipt.

**Expected Result:** `Tottenham vs Liverpool`: home team first, as in the match list and the API (domain context: *"This convention carries through to the bet receipt"*).

**Actual Result:** `Liverpool vs Tottenham`.

**Business Impact:** The receipt reads as if the user backed a different team. It causes confusion and disputes, especially together with BUG-05 and the missing selection field on the receipt.

**Evidence:** [evidence/BUG-05-06-receipt.png](evidence/BUG-05-06-receipt.png). Also reproduced by `tests/ui/test_place_bet.py`.
