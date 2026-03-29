# Fix Fast-Failing Tests First

When fixing multiple test failures:

1. **Run failing tests with `--durations=0`** to get execution times
2. **Sort by speed** — fix the fastest-failing tests first
3. **Iterate** — after each fix, re-run only the fast tests to confirm, then move to the next

Why: Fast tests give rapid feedback loops. A 0.5s test lets you iterate 10x faster than a 30s test. Fix cheap wins first, then tackle slow tests with confidence that the fast ones are green.

Do NOT run the full suite until all individually-targeted fast tests pass.
