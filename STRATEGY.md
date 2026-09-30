# Strategy & Recommendations

## Why these 2 tests

| Test | Why it was picked |
|------|-------------------|
| **TC-01** UI end-to-end bet placement | Core revenue flow, and the only journey that covers the whole feature: match list, bet slip, placement, receipt, balance. Receipt and balance-display defects are visible only in the UI. |
| **TC-02** API: stake above balance | Direct money loss if broken. The server is the last line of defence, since the UI check can be bypassed with one request. The precondition (a prior bet) is quick and deterministic via the API. |

Other candidates and why they come next rather than now:
- **TC-03** (outcome mapping) is partly covered by TC-01 (home win). Next in line.
- **TC-04** (stake boundaries) is a good parametrized API test, but its money impact is lower than overdrawing.
- **TC-06** (user context) is cheap to automate but has Medium priority.

## Left as manual

- **Error modal (`Rebet` / `Close`).** It needs a server failure, which can't be triggered from outside. Automating it requires API mocking or a fault-injection switch.
- **Double submission in the UI (TC-05).** It depends on click timing. The API race (two parallel requests → 409) should be automated, but it needs a concurrency harness.
- **Exploratory checks, copy and layout.** Human judgement gives more value here than scripts.

## Recommendations

1. **CI.** Run API tests on every PR from branch into main, since they're fast and stable. Run the UI E2E test headless on merge or nightly. Publish the Allure report as a build artifact. There is also an option to use a Docker container for tests, but it is depend on the infrastructure.
2. **Test data.**
   - Don't rely on `reset-balance`: it returns €125.50 but stores €120.
   - Use a separate user id per run, or per test for parallel runs.
   - Pick matches by criteria (upcoming, distinct odds, none equal to 2.00) instead of taking the first upcoming match.
3. **More layers and spec clarifications.**
   - Add contract tests against the OpenAPI schema.
   - Add a component test for the receipt, which is currently built on the client.
   - Close the open spec questions in [docs/spec-issues.md](docs/spec-issues.md): payout rounding, 400 vs 422, UI behaviour on 409, and where the Bet ID comes from.
4. **Build an QA agentic system over the framework.**
   - Decompose Features in specs (or add MCP + skills to transform documentation into specs)
   - Build skills for AI 
   - Build MCP for Playwright(just a suggestion)

