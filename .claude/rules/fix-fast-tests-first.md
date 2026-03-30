# Fix Fast-Failing Tests First — Never Run the Full Suite

## HARD RULE

**NEVER run the full test suite unless all individually-targeted tests are green.** Running the full suite to "see what passes" wastes hours and violates every efficiency principle.

## Protocol

1. **Run failing tests with `--durations=0`** to get execution times
2. **Sort by speed** — fix the fastest-failing tests first
3. **Target individual tests** — always use `-k test_name` to run a single test
4. **Fix and verify** — after each fix, re-run only that one test
5. **Move to the next** — only after the individual test passes
6. **Full suite LAST** — run the full suite exactly once, only after every individual test is green

## What This Means in Practice

- `pixi run -e dev test -k test_25 -n0` — YES, run one test
- `pixi run -e dev test --ignore=tests/test_e2e.py` — YES, run only unit tests
- `pixi run -e dev test` — NO, not until every known failure is individually fixed
- `sleep 600 && check results` — NO, do other work instead of blocking

## Why

A full supervisor test run takes 90+ minutes. Running it 3 times to "see what happens" wastes 4+ hours. Targeting individual tests gives feedback in seconds (unit) or minutes (E2E). The full suite is a final verification step, not a debugging tool.
