---
name: test-integration
description: "Run REAL end-to-end integration tests across all SAR repos"
user_invocable: true
---

# /test-integration — Real Integration Tests

Run REAL tests across all deployed SAR repos. NO dry runs. NO simulations.

## Configuration

Read `.env` from the workspace root for repo paths.

## Phase 1: Infrastructure Tests

### Test 1: harness-core tests pass
```bash
cd ${HARNESS_CORE_REPO} && pixi install -e dev && pixi run -e dev test
```
PASS if all tests pass.

### Test 2: RAG target eval produces real report
```bash
cd ${RAG_TARGET_REPO} && rm -rf /tmp/fluxapi-chroma && pixi run eval
```
PASS if `/tmp/rag-eval-report.json` exists with `precision_at_5` field. Report metric values.

### Test 3: RAG target unit tests pass
```bash
cd ${RAG_TARGET_REPO} && pixi install -e dev && pixi run -e dev test
```
PASS if all tests pass.

### Test 4: Research loop assets exist and are substantial
Check files in `${RESEARCH_LOOP_REPO}`:
- `.claude/skills/improve-rag/SKILL.md` (> 100 bytes)
- `.claude/agents/evaluator.md` (> 100 bytes)
- `.claude/agents/improver.md` (> 100 bytes)

### Test 5: Supervisor discovers research loop assets
```bash
cd ${SUPERVISOR_REPO} && pixi run prompt-list
```
PASS if it lists skill + evaluator + improver.

### Test 6: Supervisor has start/stop skills
Check files exist:
- `${SUPERVISOR_REPO}/.claude/skills/start-research/SKILL.md`
- `${SUPERVISOR_REPO}/.claude/skills/stop-research/SKILL.md`

### Test 7: Cross-repo paths resolve correctly
- `${SUPERVISOR_REPO}/harness.toml` `supervised.repo` resolves to `${RESEARCH_LOOP_REPO}`
- Research loop agents reference a path resolving to `${RAG_TARGET_REPO}`

## Phase 2: Live Research Loop (REAL ITERATIONS)

This is the critical test. Runs the actual research loop via the supervisor's start-research skill.

### Test 8: Run 2-3 real autoresearch iterations

1. Record baseline:
   ```bash
   cd ${RAG_TARGET_REPO} && rm -rf /tmp/fluxapi-chroma && pixi run eval
   ```
   Read baseline `precision_at_5`.

2. Record baseline git state:
   ```bash
   cd ${RAG_TARGET_REPO} && git log --oneline -1
   ```

3. Launch the research loop directly (limited turns):
   ```bash
   cd ${RESEARCH_LOOP_REPO} && claude -p "/improve-rag" --dangerously-skip-permissions --max-turns 30
   ```
   This gives enough turns for 2-3 experiment iterations.

4. After completion, verify:
   - `${RESEARCH_LOOP_REPO}/results.tsv` exists with entries
   - Each entry has: commit, precision, status, description
   - `${RAG_TARGET_REPO}` git log shows experiment commits (if any kept)
   - Run final eval to get current metric

5. PASS criteria:
   - results.tsv has at least 1 entry
   - Final eval produces a valid report
   - No crashes

### Test 9: Verify keep/discard integrity
Read results.tsv:
- For "keep" entries: verify commit exists in `${RAG_TARGET_REPO}` git log
- For "discard" entries: verify commit was reset
PASS if all states are consistent.

## Phase 3: Supervisor Integration

### Test 10: Supervisor can snapshot
```bash
cd ${SUPERVISOR_REPO} && pixi run snapshot --label integration-test
```
PASS if snapshot directory created.

## Summary

Print:
```
=== SAR INTEGRATION TEST RESULTS ===
Phase 1: Infrastructure
  Test 1:  harness-core tests      PASS/FAIL
  Test 2:  RAG target eval         PASS/FAIL  (precision_at_5=X.XX)
  Test 3:  RAG target tests        PASS/FAIL
  Test 4:  Research loop assets    PASS/FAIL
  Test 5:  Supervisor prompt-list  PASS/FAIL
  Test 6:  Supervisor skills       PASS/FAIL
  Test 7:  Cross-repo paths       PASS/FAIL

Phase 2: Live Research Loop
  Test 8:  Research iterations     PASS/FAIL  (N iterations, baseline→final)
  Test 9:  Keep/discard integrity  PASS/FAIL

Phase 3: Supervisor
  Test 10: Snapshot creation       PASS/FAIL

Total: X/10 passed
```
