from decimal import Decimal

from selenium.webdriver.support import expected_conditions as EC

from app.models import parse_money
from app.pages.base_page import BasePage, by_id


class ReceiptModal(BasePage):
    """Success modal shown after a bet is placed."""

    ROOT = by_id("modal-success")
    BET_ID = by_id("modal-success-bet-id")
    MATCH = by_id("modal-success-match")
    STAKE = by_id("modal-success-stake")
    ODDS = by_id("modal-success-odds")
    PAYOUT = by_id("modal-success-payout")
    PLACED_AT = by_id("modal-success-placed-at")
    CLOSE = by_id("modal-success-close")

    @property
    def bet_id(self) -> str:
        return self.text(self.BET_ID)

    @property
    def match(self) -> str:
        return self.text(self.MATCH)

    @property
    def stake(self) -> Decimal:
        return parse_money(self.text(self.STAKE))

    @property
    def odds(self) -> Decimal:
        return Decimal(self.text(self.ODDS))

    @property
    def payout(self) -> Decimal:
        return parse_money(self.text(self.PAYOUT))

    @property
    def placed_at(self) -> str:
        return self.text(self.PLACED_AT)

    def close(self) -> None:
        self.click(self.CLOSE)
        self.wait.until(EC.invisibility_of_element_located(self.ROOT))


class ErrorModal(BasePage):
    """Failure modal with Rebet / Close actions."""

    ROOT = by_id("modal-error")
    MESSAGE = by_id("modal-error-message")
    REBET = by_id("modal-error-rebet")
    CLOSE = by_id("modal-error-close")
    CLOSE_X = by_id("modal-error-close-x")

    @property
    def message(self) -> str:
        return self.text(self.MESSAGE)

    def rebet(self) -> None:
        self.click(self.REBET)

    def close(self) -> None:
        self.click(self.CLOSE)
        self.wait.until(EC.invisibility_of_element_located(self.ROOT))
