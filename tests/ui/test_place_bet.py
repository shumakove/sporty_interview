from decimal import Decimal

import allure
import pytest
from app.api import BettingApiClient
from app.models import Selection
from app.pages import BettingPage

STAKE = Decimal("10.00")


@allure.feature("Bet placement")
@allure.title("TC-01: Place a single bet end-to-end")
@pytest.mark.ui
def test_place_single_bet_end_to_end(
    reset_balance: Decimal,  # requested first: the page must load after the reset
    betting_page: BettingPage,
    upcoming_match: dict,
    api: BettingApiClient,
):
    """TC-01: place a single bet end-to-end.

    Why automated: this is the core revenue flow and the only journey that touches every part of
    the feature (match list, bet slip, placement, receipt, balance). A regression here breaks
    betting for every user, so it's the first check to run on every build.
    """
    match_id = upcoming_match["id"]
    page = betting_page
    initial_balance = reset_balance

    with allure.step("Balance is shown in the header and the empty bet slip"):
        assert page.header_balance == initial_balance
        assert page.slip_balance == initial_balance

    with allure.step("Select the home win on an upcoming match"):
        home, away = page.match_teams(match_id)
        odds = page.displayed_odds(match_id, Selection.HOME)
        assert (home, away) == (upcoming_match["homeTeam"], upcoming_match["awayTeam"])
        assert odds == Decimal(str(upcoming_match["odds"]["home"]))
        page.select_odds(match_id, Selection.HOME)
        assert page.selection_count == 1

    with allure.step(f"Enter stake €{STAKE}; bet slip shows total stake and payout"):
        page.enter_stake(str(STAKE))
        expected_payout = (STAKE * odds).quantize(Decimal("0.01"))
        assert page.total_stake == STAKE
        assert page.potential_payout == expected_payout

    with allure.step("Place the bet; button switches to Placing..."):
        page.place_bet()
        assert page.place_bet_label == "Placing..."

    with allure.step("Read the receipt"):
        receipt = page.wait_for_receipt()
        assert receipt.bet_id
        assert receipt.placed_at
        # Spec §2.4 also requires the selection on the receipt, but the receipt has no such field.
        actual = {
            "receipt match": receipt.match,
            "receipt stake": receipt.stake,
            "receipt odds": receipt.odds,
            "receipt payout": receipt.payout,
        }

    with allure.step("Close the receipt and read the balances"):
        receipt.close()
        assert not page.has_active_selection()
        actual |= {
            "server balance": Decimal(str(api.get_balance().json()["balance"])),
            "header balance": page.header_balance,
            "bet slip balance": page.slip_balance,
        }

    with allure.step("Receipt and balances match what the user saw before placing"):
        # One comparison, so one failure doesn't hide the others.
        expected_balance = initial_balance - STAKE
        assert actual == {
            "receipt match": f"{home} vs {away}",
            "receipt stake": STAKE,
            "receipt odds": odds,
            "receipt payout": expected_payout,
            "server balance": expected_balance,
            "header balance": expected_balance,
            "bet slip balance": expected_balance,
        }
