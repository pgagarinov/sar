# Test Strictness — Never Weaken Tests

- **Never weaken tests.** Never make them less strict. Never relax assertions, tolerances, or coverage.
- **Never simplify tests** to make them pass. Fix the production code instead.
- If a test checks N things, keep checking N things.
- If a test writes data and reads it back, keep that behavior — do not skip the write.
- Keep the level of strictness untouched. If anything, make tests stricter, never looser.
