# No Test Skips, No Silent Catches

Tests must either PASS or FAIL. Never skip. Never silently swallow exceptions.

## No Skips

- Do not use `pytest.skip()`, `@pytest.mark.skip`, or `skipIf`
- If a test cannot run because an environment variable is missing, it must FAIL with a clear error message explaining what is required
- If a test cannot run because a dependency is missing, it must FAIL

## No Silent Exception Handling in Tests

- Never use `except` to catch and ignore exceptions in test code
- If a `try` block catches an exception, the test must FAIL — re-raise or call `self.fail()`
- `try/finally` for cleanup is fine — the `finally` block runs regardless of pass/fail
- Never use `except Exception: pass` or `except: continue` in test helpers

## Why

Skipped tests hide problems. A suite reporting "50 passed, 12 skipped" may have 12 broken tests. Silent catches are worse — they make failures invisible. Every test must either pass cleanly or fail loudly.
