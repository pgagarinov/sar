# No Test Skips

Tests must either PASS or FAIL. Never skip.

- Do not use `pytest.skip()`, `@pytest.mark.skip`, or `skipIf`
- If a test cannot run because an environment variable is missing, it must FAIL with a clear error message explaining what is required
- If a test cannot run because a dependency is missing, it must FAIL
- The E2E marker (`@pytest.mark.e2e`) controls SELECTION (which tests run), not skipping. Deselected tests are not skipped — they are simply not collected.

## Why

Skipped tests hide problems. A test suite that reports "50 passed, 12 skipped" looks healthy but may have 12 broken tests. Fail loudly so the operator knows what to fix.
