# Parallel Test Debugging

## HARD RULE

**NEVER work on one test at a time.** When multiple tests fail, fix them in parallel. Waiting for a slow test while doing nothing is wasted time.

## Protocol

1. **Launch ALL failing tests in the background simultaneously** — use `run_in_background: true` for each one in a single message with multiple tool calls
2. **Immediately start debugging the next failure** — don't wait, don't check, don't sleep
3. **Keep launching and fixing** — you should always be actively working on something
4. **Check background results only when notified** — never poll or sleep-and-check
5. **If blocked on all fronts** — only then wait for results

## What "Parallel" Means Concretely

- 3 failing tests? Launch ALL THREE in background simultaneously, then work on unit tests.
- Test A result arrives? Check it. If still failing, diagnose while B and C still run.
- At any given moment you should be **actively debugging or writing code**, not sleeping.

## Violations

These are all violations of this rule:
- `sleep 300 && check results` — you just wasted 5 minutes
- `sleep 600 && tail -5 /tmp/test19.txt` — you just wasted 10 minutes doing nothing
- `sleep 900 && grep results` — you just wasted 15 minutes staring at a clock
- Running one E2E test and waiting 20 minutes for it to finish before starting the next fix
- "Let me wait for test_19 to complete" — no, work on test_25 while test_19 runs
- "Let me check test_25 progress" followed by `sleep 300` — NO, launch test_25 in background and move on
- Launching the full test suite to "see what passes" — run individual tests in parallel instead
- Running test_30, then after it finishes running test_31, then test_32 — run all three simultaneously

## Example

```
1. Launch test_19 in background (20 min E2E)
2. While running: debug test_30 → write unit test → fix code → verify unit test (2 min)
3. While running: debug test_32 → write unit test → fix code → verify unit test (2 min)
4. While running: launch test_25 in background
5. While running: debug test_31 → write unit test → fix code → verify unit test (2 min)
6. test_19 notification arrives → check result
7. test_25 notification arrives → check result
8. All individual tests green → run full suite once
```
