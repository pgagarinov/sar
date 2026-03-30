---
name: supervisor-clean
description: "Remove all supervisor leftovers: clones, logs, state, backups"
user_invocable: true
---

# /supervisor-clean — Remove All Leftovers

Stop everything, then remove all artifacts left by the supervisor, researcher variants, and E2E tests. Does NOT touch canonical repos or the hub itself.

## Configuration

Read `.env` from the workspace root for `SUPERVISOR_REPO`, `RAG_TARGET_REPO`.

## Steps

### 1. Stop everything first

```bash
# Stop any running researcher variants
cd <SUPERVISOR_REPO> && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-variant list --json
```

For each running variant:
```bash
cd <SUPERVISOR_REPO> && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-variant stop --id <variant_id>
cd <SUPERVISOR_REPO> && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-variant discard --id <variant_id>
```

Then stop the main researcher:
```bash
cd <SUPERVISOR_REPO> && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-stop
```

### 2. Remove researcher variant clones

```bash
rm -rf /tmp/sar-research-loop--*
rm -rf <RAG_TARGET_REPO>--*
```

### 3. Remove target merge backups

```bash
rm -rf <RAG_TARGET_REPO>.pre-merge-backup
```

### 4. Remove supervisor state

```bash
rm -rf <SUPERVISOR_REPO>/.supervisor/snapshots
rm -f <SUPERVISOR_REPO>/.supervisor/history.jsonl
rm -f <SUPERVISOR_REPO>/.supervisor/latest_snapshot.json
rm -f <SUPERVISOR_REPO>/.supervisor/status.jsonl
rm -f <SUPERVISOR_REPO>/.supervisor/prompt-edits.jsonl
rm -f <SUPERVISOR_REPO>/.supervisor/parked-*.json
rm -f <SUPERVISOR_REPO>/.supervisor/start-state.json
rm -f <SUPERVISOR_REPO>/.supervisor/start--*-state.json
rm -f <SUPERVISOR_REPO>/.supervisor/merge.lock
rm -f <SUPERVISOR_REPO>/.supervisor/*.pid
```

### 5. Remove logs

```bash
rm -f /tmp/cc-sar-supervisor*.log
```

### 6. Remove target temp files

```bash
rm -rf /tmp/fluxapi-chroma
rm -rf /tmp/fluxapi-chroma--*
rm -f /tmp/rag-eval-report*.json
```

### 7. Remove research loop results

```bash
rm -f <RESEARCH_LOOP_REPO>/results.tsv
```

### 8. Report

List what was removed. Verify:
```bash
echo "=== Remaining ==="
ls <SUPERVISOR_REPO>/.supervisor/ 2>/dev/null || echo "state: clean"
ls -d /tmp/sar-research-loop--* 2>/dev/null || echo "clones: clean"
ls -d <RAG_TARGET_REPO>--* 2>/dev/null || echo "target clones: clean"
ls /tmp/cc-sar-supervisor*.log 2>/dev/null || echo "logs: clean"
```

## Important

- ALWAYS stop before cleaning — never `rm -rf` a directory that a running process is using
- This skill does NOT modify canonical repos (sar-rag-target, sar-research-loop, sar-supervisor code)
- This skill does NOT touch the hub (take3-pe)
- To also reset the target code to the original seed, run `/target-reset` separately
