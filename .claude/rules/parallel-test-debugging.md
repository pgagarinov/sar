# Parallel Test Debugging

When fixing multiple test failures, work on different tests in parallel:

- While an E2E test runs in the background (10-30 min), work on other failing tests simultaneously.
- Use background commands (`run_in_background`) for slow tests and continue debugging fast tests in the foreground.
- Never block on a single slow test when there are other failures to investigate.
- Run individual tests with `-k test_name` — never rerun the full suite until individual tests are green.

## Example workflow

```
1. Launch test_19 in background (20 min E2E)
2. While waiting: debug test_30, write unit test, fix production code
3. While waiting: debug test_32, write unit test, fix production code
4. Check test_19 result
5. Only after all individual tests pass: run full suite once
```
