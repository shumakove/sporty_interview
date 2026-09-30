from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

Locator = tuple[str, str]


def by_id(element_id: str) -> Locator:
    return By.ID, element_id


class BasePage:
    def __init__(self, driver: WebDriver, timeout: float):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def find(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator: Locator) -> None:
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def text(self, locator: Locator) -> str:
        return self.find(locator).text.strip()

    def is_displayed(self, locator: Locator) -> bool:
        elements = self.driver.find_elements(*locator)
        return bool(elements) and elements[0].is_displayed()
