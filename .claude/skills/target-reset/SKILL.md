---
name: target-reset
description: "Reset the target to its initial baseline state"
user_invocable: true
---

# /target-reset — Reset the Target

Reset the target repo to the `baseline` git tag (last infrastructure commit, before any experiments).

## Configuration

Read `.env` from the workspace root for `RAG_TARGET_REPO`.

## Steps

```bash
cd <RAG_TARGET_REPO> && git reset --hard baseline && rm -rf /tmp/fluxapi-chroma && rm -f /tmp/rag-eval-report.json
```

This resets all code to the baseline tag, cleans ChromaDB index, and removes stale eval reports.

## The baseline tag

The `baseline` git tag points to the last infrastructure commit before any experiment commits. It includes:
- Repo rename, Python 3.13, pixi.lock
- /run skill, rules
- paths.py (env var support for parallel experiments)

It does NOT include any experiment results (no BM25, no RRF, no chunking changes).

## What this skill does NOT do

- Does not reset the supervisor or researcher — only the target
- Does not verify by running eval — that is a separate step if needed
