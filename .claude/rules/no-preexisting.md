# No Pre-Existing Issues — Fix Everything

## HARD RULE

"Pre-existing" is not a valid category. It is not an excuse to stop. If a test fails, fix it — regardless of when the failure was introduced.

## What This Means

- Never classify failures as "pre-existing" and move on.
- After fixing your regressions, keep going. If other failures remain, start fixing those too.
- Do not report "0 new regressions" as success. Success is 0 failures total.
- Do not ask "shall I commit?" while tests still fail. Commit the progress, then continue fixing.
- Every test failure is work to be done, not a status to be reported.

## No Excuses

The difficulty of fixing a test does not change the requirement. These are NOT valid reasons to skip a failure:

- "It requires real API calls" — then debug the real API calls.
- "It spawns real Claude sessions" — then debug the real Claude sessions.
- "It depends on the full system working" — then make the full system work.
- "It's an integration/E2E test, not a unit test" — the test type is irrelevant. Failed is failed.
- "It was already broken before my changes" — irrelevant. Fix it now.

## When to Stop

Stop only when:
- All tests pass, OR
- You hit a blocker that requires user input (missing data, credentials, design decision), OR
- The user explicitly tells you to stop
