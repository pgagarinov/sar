# Parallel Test Debugging

## HARD RULE

**NEVER work on one test at a time.** When multiple tests fail, fix them in parallel. Waiting for a slow test while doing nothing is wasted time.

## Protocol

1. **Launch the slowest failing test in the background** — `run_in_background: true`
2. **Immediately start debugging the next failure** — don't wait, don't check, don't sleep
3. **Keep launching and fixing** — you should always be actively working on something
4. **Check background results only when notified** — never poll or sleep-and-check
5. **If blocked on all fronts** — only then wait for results

## What "Parallel" Means Concretely

- 3 failing tests? Launch test A in background, fix test B in foreground, queue test C.
- Test B fixed? Launch its verification in background, start on test C.
- Test A result arrives? Check it. If still failing, diagnose while test C runs.
- At any given moment you should be **actively debugging or writing code**, not sleeping.

## Violations

These are all violations of this rule:
- `sleep 300 && check results` — you just wasted 5 minutes
- Running one E2E test and waiting 20 minutes for it to finish before starting the next fix
- "Let me wait for test_19 to complete" — no, work on test_25 while test_19 runs
- Launching the full test suite to "see what passes" — run individual tests in parallel instead

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
