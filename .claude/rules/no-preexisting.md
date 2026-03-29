# No Pre-Existing Issues — Fix Everything

## HARD RULE

"Pre-existing" is not a valid category. It is not an excuse to stop. If a test fails, fix it — regardless of when the failure was introduced.

## What This Means

- Never classify failures as "pre-existing" and move on.
- After fixing your regressions, keep going. If other failures remain, start fixing those too.
- Do not report "0 new regressions" as success. Success is 0 failures total.
- Do not ask "shall I commit?" while tests still fail. Commit the progress, then continue fixing.
- Every test failure is work to be done, not a status to be reported.

## When to Stop

Stop only when:
- All tests pass, OR
- You hit a blocker that requires user input (missing data, credentials, design decision), OR
- The user explicitly tells you to stop
