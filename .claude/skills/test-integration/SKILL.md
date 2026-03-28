---
name: test-integration
description: "Run REAL end-to-end integration tests via the supervisor"
user_invocable: true
---

# /test-integration — Real End-to-End Tests

Test the full SAR pipeline. The entry point is the supervisor — everything flows through it, just like production.

NO dry runs. NO simulations. NO shortcuts.

## Configuration

Read `.env` from the workspace root for repo paths.

## Phase 1: Infrastructure Verification

### Test 1: harness-core tests pass
```bash
cd ${HARNESS_CORE_REPO} && pixi install -e dev && pixi run -e dev test
```

### Test 2: RAG target eval produces real metrics
```bash
cd ${RAG_TARGET_REPO} && rm -rf /tmp/fluxapi-chroma && pixi run eval
```
PASS if `/tmp/rag-eval-report.json` has `precision_at_5`. Record as baseline.

### Test 3: RAG target unit tests pass
```bash
cd ${RAG_TARGET_REPO} && pixi install -e dev && pixi run -e dev test
```

### Test 4: Research loop assets exist and are substantial
Files in `${RESEARCH_LOOP_REPO}`: `.claude/skills/improve/SKILL.md`, `.claude/agents/evaluator.md`, `.claude/agents/improver.md` — all > 100 bytes.

### Test 5: Supervisor discovers research loop assets
```bash
cd ${SUPERVISOR_REPO} && pixi run prompt-list
```
PASS if it lists skill + evaluator + improver.

### Test 6: Supervisor has /start and /stop skills
Check `${SUPERVISOR_REPO}/.claude/skills/start/SKILL.md` and `${SUPERVISOR_REPO}/.claude/skills/stop/SKILL.md` exist.

### Test 7: Cross-repo paths resolve
- `${SUPERVISOR_REPO}/harness.toml` `supervised.repo` resolves to `${RESEARCH_LOOP_REPO}`
- Research loop agents reference `${RAG_TARGET_REPO}`

## Phase 2: Live E2E Test via Supervisor

This is the critical test. Everything goes through the supervisor — the same path as production.

### Test 8: Supervisor starts and monitors research loop

1. Record baseline state:
   ```bash
   cd ${RAG_TARGET_REPO} && git log --oneline -1
   ```

2. Start the supervisor loop (it launches the research loop internally):
   ```bash
   cd ${SUPERVISOR_REPO} && pixi run loop --no-clean &
   LOOP_PID=$!
   ```

3. Poll status every 30 seconds until at least 2 experiment iterations have run:
   ```bash
   cd ${SUPERVISOR_REPO} && pixi run status
   ```
   Also check `${RESEARCH_LOOP_REPO}/results.tsv` for iteration count.

4. When results.tsv has >= 2 non-baseline entries (or after 10 minutes max), stop:
   ```bash
   cd ${SUPERVISOR_REPO} && pixi run stop
   ```

5. PASS criteria:
   - Supervisor started successfully (PID exists)
   - results.tsv has at least 2 experiment entries (beyond baseline)
   - Supervisor's `.supervisor/history.jsonl` has entries

### Test 9: Supervisor snapshots captured
```bash
cd ${SUPERVISOR_REPO} && pixi run history
```
PASS if history shows at least 1 snapshot with a metric value.

### Test 10: Keep/discard integrity
Read `${RESEARCH_LOOP_REPO}/results.tsv`:
- For "keep" entries: verify commit exists in `${RAG_TARGET_REPO}` git log
- For "discard" entries: verify commit was reset
PASS if all states match.

### Test 11: Final metric comparison
Run one final eval:
```bash
cd ${RAG_TARGET_REPO} && rm -rf /tmp/fluxapi-chroma && pixi run eval
```
Report: baseline precision → final precision, number of kept improvements.

## Summary

```
=== SAR E2E TEST RESULTS ===
Phase 1: Infrastructure
  Test 1:  harness-core tests      PASS/FAIL
  Test 2:  RAG target eval         PASS/FAIL  (baseline precision=X.XX)
  Test 3:  RAG target tests        PASS/FAIL
  Test 4:  Research loop assets    PASS/FAIL
  Test 5:  Supervisor prompt-list  PASS/FAIL
  Test 6:  Supervisor skills       PASS/FAIL
  Test 7:  Cross-repo paths       PASS/FAIL

Phase 2: E2E via Supervisor
  Test 8:  Supervisor loop ran     PASS/FAIL  (N iterations)
  Test 9:  Snapshots captured      PASS/FAIL
  Test 10: Keep/discard integrity  PASS/FAIL
  Test 11: Metric improvement      PASS/FAIL  (X.XX → Y.YY)

Total: X/11 passed
```
