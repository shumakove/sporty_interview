# Single Bet Placement — QA Assignment

## How I did this assesment step-by-step
- I downloaded 2 pdf files
- Created a project asked AI to transform PDF fils into pdf spec format, so I can see assignment and spec separately
- The I compared what was done and if there are no mistakes
- I read a specs, and prepared some plan notes on paper, found some spec issues. 
- I wrote a checklist what I want to test
- I have described a draft steps
- Marked what I will test with code and what I will test manually
- Prepared prompts for AI to make my thoughts more presentable
- I have defined a strategy what I will cover with UI(webdriver) and what will be in API tests
- Transformed it into strategy
- After I had all tests I transormed it into beautefill md format
- I authorized in web and tried ti see how this scenario will work in rea flow, found all locators I need
- I made a simple POM based framework 
- I made simple API layer with minimum functionalities

## Time
I spent for it 3.5 hours, actually because I was stuk with bugs.

## Deliverables

| Part | File |
|------|------|
| A1. Test plan | [Test_plan.md](Test_plan.md) |
| A2. Execution results / bug reports | [bugs.md](bugs.md) |
| B. Automation framework + 2 tests | [src/](src/), [tests/](tests/) |
| C. Strategy & recommendations | [STRATEGY.md](STRATEGY.md) |

Supporting notes: [spec issues & assumptions](docs/spec-issues.md), [app notes & locators](docs/app-notes.md).

## Project structure

```
src/app/
  config.py            # settings from .env
  models.py            # Selection enum, money parsing
  api/client.py        # BettingApiClient (requests)
  pages/               # Page Objects (Selenium)
    base_page.py       #   explicit waits, common actions
    betting_page.py    #   header, match list, bet slip
    modals.py          #   receipt and error modals
tests/
  conftest.py          # fixtures: settings, api, driver, balance reset, test match
  ui/test_place_bet.py                  # TC-01, E2E
  api/test_insufficient_balance.py      # TC-02, API
```

The framework code in `src/` knows nothing about tests. Tests only describe the scenario and the checks.

## Setup

Requirements: Python 3.10+, uv, Google Chrome, requests. The chromedriver is downloaded automatically by Selenium Manager.

```bash
uv sync
cp .env.example .env   # then set USER_ID
```

| Variable | Default | Meaning |
|----------|---------|---------|
| `USER_ID` | — | Required. Your user id |
| `BASE_URL` | `https://qae-assignment-tau.vercel.app` | App under test |
| `HEADLESS` | `false` | Run Chrome without a window |
| `UI_TIMEOUT` | `10` | Explicit wait timeout, seconds |

## Run

```bash
uv run pytest              # all tests
uv run pytest -m api       # API only
uv run pytest -m ui        # UI only
HEADLESS=true uv run pytest
```

Allure results are written to `allure-results/` on every run. To view them (needs the [Allure CLI](https://allurereport.org/docs/install/) and Java):

```bash
allure serve allure-results
```

A failed UI test also saves a screenshot to `artifacts/`.

> **Both tests currently fail on purpose.** They catch real defects: TC-01 → BUG-01 and receipt issues, TC-02 → BUG-02. See [bugs.md](bugs.md).

## Postman / Bruno collection

[postman/betting-api.postman_collection.json](postman/betting-api.postman_collection.json) has 45 API checks grouped by scenario: TC-02, TC-03, TC-04, TC-06, validation, protocol and reset. Import it into Postman or Bruno, set the `userId` collection variable and run the folders in order, starting with `00 Setup`. As with the pytest suite, checks follow the spec, so requests that reproduce known bugs fail.

From the command line:

```bash
npx newman run postman/betting-api.postman_collection.json --env-var userId=<your-user-id>
```

## Tooling choices

- **uv:** dependency management with a lockfile, and a single command to set up the project.
- **Allure:** readable reports with steps, API request/response attachments and failure screenshots.
- **python-dotenv:** keeps the user id out of the code.
