# Test-Driven Bug Fixing

**Applies to:** ALL bugs — whether found via tests, manual debugging, code review, or production observation.

## HARD RULE

**NEVER fix a bug before writing a failing test for it.** The test comes first. Always.

## Protocol

When you find a bug (any bug, any source):

1. **Read the failure** — understand the root cause
2. **Write a unit test first** — create a focused unit test in the appropriate `test_*.py` file that reproduces the exact same failure. This test MUST fail before the fix.
3. **Fix the bug** — make the unit test pass
4. **Re-run the unit test** — confirm it passes
5. **Re-run the E2E test** — confirm the original E2E test now passes too
6. **Continue** to the next E2E failure

## Why

- Unit tests are fast (<1s) — iterate on fixes without waiting for Claude sessions
- The unit test documents the bug permanently — prevents regression
- Fixing at the unit level ensures the root cause is addressed, not just the symptom
- Writing the test first forces you to understand the bug before fixing it

## Never

- Never fix an E2E failure by modifying the E2E test itself (unless the test is wrong)
- Never skip a failing E2E test without a corresponding unit test
- Never fix the bug without writing the unit test first
- Never open a file and start editing production code when you just discovered a bug — open the test file first
- Never say "let me fix this real quick" — there is no quick fix without a test
