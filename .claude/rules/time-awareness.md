# Time Awareness

Be mindful of time. Every minute spent waiting is a minute not spent fixing.

## Track Time

- Note when you start debugging a failure
- Note when you launch a slow test
- If a test has been running for longer than expected, check once and move on — don't poll in a loop
- After 30 minutes on a single failure with no progress, reassess your approach

## Never Block

- Never `sleep` for more than 30 seconds in the foreground
- Never wait for a slow test to finish before starting work on the next failure
- Launch slow tests in the background, continue working, check result when notified
- If you catch yourself writing `sleep 300 && check`, you are wasting 5 minutes doing nothing

## Budget Your Time

- Unit test fix cycle: target < 2 minutes (write test, fix code, verify)
- E2E test verification: launch in background, check result when done
- If a fix attempt doesn't work in 10 minutes, step back and rethink the approach
- Three failed attempts at the same fix = wrong diagnosis, re-read the error

## What "As Quickly As Possible" Means

- Don't over-engineer the fix. The simplest correct change wins.
- Don't read 10 files when the traceback points to 1 line.
- Don't write a comprehensive unit test suite when one targeted test reproduces the bug.
- Don't run the full test suite when `-k test_name` answers the question.
- Don't refactor surrounding code while fixing a bug.
