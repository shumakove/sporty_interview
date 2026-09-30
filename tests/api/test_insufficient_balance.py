from decimal import Decimal

import allure
import pytest

from app.api import BettingApiClient
from app.models import Selection

MAX_STAKE = Decimal("100.00")


def current_balance(api: BettingApiClient) -> Decimal:
    return Decimal(str(api.get_balance().json()["balance"]))


@allure.feature("Stake validation")
@allure.title("TC-02: Stake above the available balance is rejected")
@pytest.mark.api
def test_stake_above_balance_is_rejected(reset_balance: Decimal, upcoming_match: dict, api: BettingApiClient):
    """TC-02: a stake above the available balance is rejected by the API.

    Why automated: overdrawing the balance is a direct money loss, and the UI check alone
    can be bypassed by calling the API. The state needs a previous bet to reach
    (max stake €100 < starting balance), which is quick and repeatable via the API.
    """
    match_id = upcoming_match["id"]

    # A rejection must mean "insufficient balance", not "above max stake", so the balance goes below €100 first.
    with allure.step(f"Place a €{MAX_STAKE} bet to bring the balance below the max stake"):
        response = api.place_bet(match_id, Selection.HOME, float(MAX_STAKE))
        assert response.status_code == 200, response.text
        balance = current_balance(api)
        assert balance == reset_balance - MAX_STAKE

    with allure.step("Stake one cent above the balance is rejected and nothing is deducted"):
        response = api.place_bet(match_id, Selection.HOME, float(balance + Decimal("0.01")))
        assert 400 <= response.status_code < 500, response.text  # 400 vs 422 is ambiguous in the spec (SPEC-7)
        assert response.json()["message"] == "Insufficient balance"
        assert current_balance(api) == balance

    with allure.step("Stake equal to the whole balance is accepted"):
        response = api.place_bet(match_id, Selection.HOME, float(balance))
        assert response.status_code == 200, response.text
        assert current_balance(api) == Decimal("0")
