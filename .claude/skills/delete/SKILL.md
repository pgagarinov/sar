---
name: delete
description: "Delete all 3 deployed repos and clean temp files"
user_invocable: true
---

# /delete — Clean All Deployed Repos

Remove all 3 deployed repos and clean temporary files so the next `/deploy` starts fresh.

## Configuration

Read `.env` from the workspace root for repo paths.

## Steps

1. **Read `.env`** and resolve all repo paths.

2. **Remove deployed repos** (if they exist):
   ```bash
   rm -rf ${SUPERVISOR_REPO}
   rm -rf ${RESEARCH_LOOP_REPO}
   rm -rf ${RAG_SYSTEM_REPO}
   ```

3. **Clean temporary files**:
   ```bash
   rm -rf /tmp/fluxapi-chroma
   rm -f /tmp/rag-eval-report.json
   rm -f /tmp/cc-rag-supervisor.log
   ```

4. **Report** what was removed.

## Safety

- Only removes directories at the configured paths — never removes this integration repo
- Verifies each path exists before removing
- Reports each removal
