---
name: target-reset
description: "Reset the target to its initial seed state"
user_invocable: true
---

# /target-reset — Reset the Target

Reset the target repo to the `seed` git tag (the original initial commit, before any research changes).

## Configuration

Read `.env` from the workspace root for `RAG_TARGET_REPO`.

## Steps

```bash
cd <RAG_TARGET_REPO> && git reset --hard seed && git tag -f baseline seed && rm -rf /tmp/rag-index-cache && rm -f /tmp/rag-eval-report.json
```

This resets all code to the seed, resets the baseline cursor to match, cleans USearch index cache, and removes stale eval reports.

## Two tags in the target

- **`seed`** — IMMUTABLE. Points to the original initial commit. Never moves. This is the starting point for a fresh research cycle.
- **`baseline`** — MOVING CURSOR. Points to the last merged state. Used by `merge_cherry_pick` to find new commits since the last merge. Moves after each merge operation.

`/target-reset` resets both HEAD and baseline to `seed`.

## What this skill does NOT do

- Does not reset the supervisor or researcher — only the target
- Does not verify by running eval — that is a separate step if needed
