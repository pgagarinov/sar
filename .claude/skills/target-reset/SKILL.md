---
name: target-reset
description: "Reset the target to its initial baseline state"
user_invocable: true
---

# /target-reset — Reset the Target

Invoke the target's own `/reset` skill to revert all code changes, clean cached state, and verify the baseline.

## Configuration

Read `.env` from the workspace root for `RAG_TARGET_REPO`.

## Steps

```bash
cd <RAG_TARGET_REPO> && claude -p /reset --dangerously-skip-permissions
```

The target's `/reset` skill handles: git checkout, git clean, ChromaDB cleanup, eval report cleanup, and baseline verification.

## What this skill does NOT do

- Does not reset the supervisor or researcher — only the target
- Does not read or interpret the target's metrics — just invokes the skill
