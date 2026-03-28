---
name: delete
description: "Delete all deployed SAR repos and clean temp files"
user_invocable: true
---

# /delete — Clean All Deployed Repos

Remove all 4 deployed SAR repos and clean temporary files.

## Configuration

Read `.env` from the workspace root.

## Steps

1. **Read `.env`** and resolve all repo paths.

2. **Remove deployed repos** (if they exist):
   ```bash
   rm -rf ${SUPERVISOR_REPO}
   rm -rf ${RESEARCH_LOOP_REPO}
   rm -rf ${RAG_TARGET_REPO}
   rm -rf ${HARNESS_CORE_REPO}
   ```

3. **Clean temporary files**:
   ```bash
   rm -rf /tmp/fluxapi-chroma
   rm -f /tmp/rag-eval-report.json
   rm -f /tmp/cc-rag-supervisor.log
   ```

4. **Report** what was removed.

## Safety

- Only removes directories at the configured `.env` paths
- Never removes this integration repo
- Verifies each path exists before removing
