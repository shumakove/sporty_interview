# Domain Context — Betting Concepts

- **Match / Event** — A scheduled football game between two teams (e.g., Manchester Utd vs
  Chelsea). Each match has a competition (league), kickoff date/time, and three possible
  outcomes.
- **Odds** — Decimal numbers representing the payout multiplier for each outcome. Displayed as
  three buttons per match: `1` (home win), `X` (draw), `2` (away win). Higher odds = less likely
  outcome = bigger payout. For example, odds of 2.45 mean a €10 bet returns €24.50.
- **Stake** — The amount of money the user risks on a bet. Entered in euros (€). Must be a
  positive number and cannot exceed the user's current balance.
- **Payout** — The total amount returned to the user if the bet wins. Calculated as
  `stake × odds`. This includes the original stake — so a €10 bet at 2.45 odds returns €24.50
  total (€14.50 profit + €10 stake).
- **Balance** — The user's available funds. Starts at **€125.50**. Decreases by the stake amount
  when a bet is placed. The balance is shared across the header and the bet slip.
- **Bet Slip** — The right-hand panel where the user reviews their selection, enters a stake, and
  places the bet. Only one bet can be active at a time.
- **Bet Receipt** — The success modal shown after a bet is placed. Displays the bet ID, match,
  stake, odds, potential payout, and timestamp. All values should be consistent with what was
  shown before placement.
- **Match Ordering** — Matches are displayed as returned by the API. The "home" team is always
  listed first (left position), the "away" team second (right position). This convention carries
  through to the bet receipt (e.g., "Manchester Utd vs Chelsea" means Manchester Utd is
  home).
