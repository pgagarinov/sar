# Test-Driven Bug Fixing

**Applies to:** `tests/test_e2e.py` and all E2E test failures.

## Protocol

When an E2E test fails:

1. **Read the failure** — understand the root cause from the traceback
2. **Write a unit test first** — create a focused unit test in the appropriate `test_*.py` file that reproduces the exact same failure. This test MUST fail before the fix.
3. **Fix the bug** — make the unit test pass
4. **Re-run the unit test** — confirm it passes
5. **Re-run the E2E test** — confirm the original E2E test now passes too
6. **Continue** to the next E2E failure

## Why

- Unit tests are fast (<1s) — iterate on fixes without waiting for Claude sessions
- The unit test documents the bug permanently — prevents regression
- Fixing at the unit level ensures the root cause is addressed, not just the symptom

## Never

- Never fix an E2E failure by modifying the E2E test itself (unless the test is wrong)
- Never skip a failing E2E test without a corresponding unit test
- Never fix the bug without writing the unit test first
