from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from app.models import Selection, parse_money
from app.pages.base_page import BasePage, Locator, by_id
from app.pages.modals import ErrorModal, ReceiptModal


class BettingPage(BasePage):
    """Main page: header, match list and bet slip."""

    HEADER_BALANCE = by_id("header-balance")
    MATCH_LIST = by_id("match-list")

    SLIP_BALANCE = by_id("bet-slip-balance")
    SLIP_COUNT = by_id("bet-slip-count")
    SLIP_REMOVE_ALL = by_id("bet-slip-remove-all")
    SLIP_REMOVE_SELECTION = by_id("bet-slip-selection-remove")
    STAKE_INPUT = by_id("bet-slip-stake-input")
    STAKE_WARNING = (By.CSS_SELECTOR, "#bet-slip .stakeWarning > span:last-child")
    TOTAL_STAKE = by_id("bet-slip-total-stake")
    POTENTIAL_PAYOUT = by_id("bet-slip-potential-payout")
    PLACE_BET = by_id("bet-slip-place-bet")

    def open(self, base_url: str, user_id: str) -> "BettingPage":
        self.driver.get(f"{base_url}/?user-id={user_id}")
        self.find(self.MATCH_LIST)
        # Balance is loaded asynchronously; wait until it's rendered.
        self.wait.until(lambda _: "€" in self.text(self.HEADER_BALANCE))
        return self

    # Header

    @property
    def header_balance(self) -> Decimal:
        return parse_money(self.text(self.HEADER_BALANCE))

    # Match list

    @staticmethod
    def _odds_button(match_id: str, selection: Selection) -> Locator:
        return by_id(f"odds-{match_id}-{selection.odds_key}")

    def match_teams(self, match_id: str) -> tuple[str, str]:
        """(home, away) as displayed in the match card."""
        card = self.find(by_id(f"match-card-{match_id}"))
        home, away = (el.text.strip() for el in card.find_elements(By.CSS_SELECTOR, ".teamName"))
        return home, away

    def displayed_odds(self, match_id: str, selection: Selection) -> Decimal:
        button = self.find(self._odds_button(match_id, selection))
        return Decimal(button.find_element(By.CSS_SELECTOR, ".oddsButtonValue").text)

    def select_odds(self, match_id: str, selection: Selection) -> "BettingPage":
        self.click(self._odds_button(match_id, selection))
        return self

    # Bet slip

    @property
    def slip_balance(self) -> Decimal:
        """Only rendered while the bet slip is empty."""
        return parse_money(self.text(self.SLIP_BALANCE))

    @property
    def selection_count(self) -> int:
        return int(self.text(self.SLIP_COUNT))

    @property
    def total_stake(self) -> Decimal:
        return parse_money(self.text(self.TOTAL_STAKE))

    @property
    def potential_payout(self) -> Decimal:
        return parse_money(self.text(self.POTENTIAL_PAYOUT))

    @property
    def stake_warning(self) -> str | None:
        return self.text(self.STAKE_WARNING) if self.is_displayed(self.STAKE_WARNING) else None

    @property
    def place_bet_label(self) -> str:
        # textContent, not .text: the button is uppercased via CSS.
        return self.find(self.PLACE_BET).get_attribute("textContent").strip()

    @property
    def is_place_bet_enabled(self) -> bool:
        return self.find(self.PLACE_BET).is_enabled()

    def enter_stake(self, amount: str) -> "BettingPage":
        field = self.find(self.STAKE_INPUT)
        # Controlled React input: clear() doesn't fire onChange, so delete the value key by key.
        field.send_keys(Keys.END + Keys.BACKSPACE * len(field.get_attribute("value") or ""))
        field.send_keys(amount)
        return self

    def remove_all(self) -> "BettingPage":
        self.click(self.SLIP_REMOVE_ALL)
        return self

    def place_bet(self) -> "BettingPage":
        self.click(self.PLACE_BET)
        return self

    def wait_for_receipt(self) -> ReceiptModal:
        self.wait.until(EC.visibility_of_element_located(ReceiptModal.ROOT))
        return ReceiptModal(self.driver, self.timeout)

    def wait_for_error(self) -> ErrorModal:
        self.wait.until(EC.visibility_of_element_located(ErrorModal.ROOT))
        return ErrorModal(self.driver, self.timeout)

    def has_active_selection(self) -> bool:
        return self.selection_count > 0
