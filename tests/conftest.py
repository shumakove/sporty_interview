from datetime import date
from decimal import Decimal
from pathlib import Path

import allure
import pytest
import requests
from selenium import webdriver
from app.api import BettingApiClient
from app.config import Settings, load_settings
from app.pages import BettingPage

ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"


@pytest.fixture(scope="session")
def settings() -> Settings:
    return load_settings()


def attach_http_exchange(response: requests.Response, *args, **kwargs) -> None:
    """requests hook: attach every API call to the Allure report."""
    request = response.request
    body = request.body.decode() if isinstance(request.body, bytes) else request.body
    allure.attach(
        f"{request.method} {request.url}\n\n{body or ''}\n\n--> {response.status_code}\n{response.text}",
        name=f"{request.method} {request.path_url} [{response.status_code}]",
        attachment_type=allure.attachment_type.TEXT,
    )


@pytest.fixture(scope="session")
def api(settings: Settings) -> BettingApiClient:
    client = BettingApiClient(settings.base_url, settings.user_id)
    client.session.hooks["response"].append(attach_http_exchange)
    return client


@pytest.fixture
def reset_balance(api: BettingApiClient) -> Decimal:
    """Resets the balance and returns the value actually persisted on the server.

    The reset response body is not used: it can disagree with the stored balance
    (reported as a bug), and tests need the real starting point.
    """
    api.reset_balance().raise_for_status()
    return Decimal(str(api.get_balance().json()["balance"]))


@pytest.fixture(scope="session")
def upcoming_match(api: BettingApiClient) -> dict:
    """First match that hasn't kicked off yet. The catalogue also contains past matches."""
    today = date.today().isoformat()
    matches = api.get_matches().json()
    upcoming = [m for m in matches if m["kickoffDate"] >= today]
    if not upcoming:
        pytest.skip("No upcoming matches in the catalogue")
    return upcoming[0]


@pytest.fixture
def driver(settings: Settings, request: pytest.FixtureRequest):
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1440,900")
    if settings.headless:
        options.add_argument("--headless=new")
    # Selenium Manager downloads a matching chromedriver automatically.
    drv = webdriver.Chrome(options=options)
    yield drv
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        png = drv.get_screenshot_as_png()
        allure.attach(png, name="screenshot on failure", attachment_type=allure.attachment_type.PNG)
        ARTIFACTS_DIR.mkdir(exist_ok=True)
        (ARTIFACTS_DIR / f"{request.node.name}.png").write_bytes(png)
    drv.quit()


@pytest.fixture
def betting_page(driver, settings: Settings) -> BettingPage:
    return BettingPage(driver, settings.ui_timeout).open(settings.base_url, settings.user_id)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """Expose the test result to fixtures, so `driver` can screenshot failures."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
