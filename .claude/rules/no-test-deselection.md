# No Test Deselection

All tests run by default. Never deselect tests via `-m "not X"` in pytest addopts or pixi tasks.

- `pixi run -e dev test` must run ALL tests — unit, integration, and E2E.
- Do not create separate `test-e2e`, `test-unit`, or `test-fast` tasks.
- Do not use pytest markers to exclude tests from the default run.
- Markers are for categorization and reporting, not for deselection.
- If a test requires environment variables (CLAUDE_CONFIG_DIRS, TARGET_PATH, etc.), it must fail loudly when they are missing — not be deselected.
- If a test is too slow, make it faster. Do not hide it behind a marker.

## Why

Deselected tests are invisible. A suite that reports "55 passed, 36 deselected" hides 36 tests that may be broken. The only way to know all tests work is to run all tests.
