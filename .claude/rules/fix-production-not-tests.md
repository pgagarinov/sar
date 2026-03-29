# Fix Production Code, Not Tests

When a test fails:

1. **The eval baseline/metric is the source of truth.** Do not modify it.
2. **Fix the production code** to produce correct output.
3. **NEVER modify test assertions** to work around production bugs.
4. **NEVER adjust tolerances** to hide real bugs.
5. **NEVER add post-processing in tests** to make outputs match — the fix belongs in production code.

## Why

Tests are verification tools. If you modify the test to accommodate wrong output, you have hidden the bug instead of fixing it.
