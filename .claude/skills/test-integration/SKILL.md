---
name: test-integration
description: "Run REAL end-to-end integration tests across all 3 repos"
user_invocable: true
---

# /test-integration — Real Integration Tests

Run REAL tests across all 3 deployed repos. NO dry runs. NO simulations. Every test produces real results.

## Configuration

Read `.env` from the workspace root for repo paths:
- `SUPERVISOR_REPO` — supervisor harness path
- `RESEARCH_LOOP_REPO` — research loop path
- `RAG_SYSTEM_REPO` — RAG search system path

## Phase 1: Infrastructure Tests

Run each test, report PASS/FAIL. Continue even if a test fails.

### Test 1: RAG System — eval produces real report
```bash
cd ${RAG_SYSTEM_REPO} && rm -rf /tmp/fluxapi-chroma && pixi run eval
```
- Read `/tmp/rag-eval-report.json`
- PASS if file exists AND contains `precision_at_5` as a number
- Report ALL metric values

### Test 2: RAG System — unit tests pass
```bash
cd ${RAG_SYSTEM_REPO} && pixi run -e dev test
```
- PASS if all tests pass
- Report count

### Test 3: Research Loop — skill and agents exist and are non-empty
Check these files exist in `${RESEARCH_LOOP_REPO}` and are > 100 bytes:
- `.claude/skills/improve-rag/SKILL.md`
- `.claude/agents/evaluator.md`
- `.claude/agents/improver.md`

### Test 4: Supervisor — discovers research loop assets
```bash
cd ${SUPERVISOR_REPO} && pixi run prompt-list
```
- PASS if output lists `skill`, `evaluator`, `improver`

### Test 5: Cross-repo paths resolve correctly
- Verify `${SUPERVISOR_REPO}/harness.toml` `supervised.repo` resolves to `${RESEARCH_LOOP_REPO}`
- Verify `${RESEARCH_LOOP_REPO}/.claude/agents/evaluator.md` references `../rag-search-system`
- Verify that `../rag-search-system` relative to `${RESEARCH_LOOP_REPO}` resolves to `${RAG_SYSTEM_REPO}`

## Phase 2: Live Research Loop Test (REAL ITERATIONS)

This is the critical test. Run the actual research loop for 2-3 iterations to verify the full chain works.

### Test 6: Run 2-3 research loop iterations

1. Record baseline metric:
   ```bash
   cd ${RAG_SYSTEM_REPO} && rm -rf /tmp/fluxapi-chroma && pixi run eval
   ```
   Read `precision_at_5` from `/tmp/rag-eval-report.json`. This is the baseline.

2. Record baseline git state:
   ```bash
   cd ${RAG_SYSTEM_REPO} && git log --oneline -1
   ```

3. Launch the research loop for a LIMITED run:
   ```bash
   cd ${RESEARCH_LOOP_REPO} && claude -p "/improve-rag" --dangerously-skip-permissions --max-turns 30
   ```
   This gives the loop enough turns to complete 2-3 experiment iterations (each iteration = evaluator dispatch + improver dispatch + evaluator dispatch + keep/discard).

4. After it completes, verify results:
   - Check `${RESEARCH_LOOP_REPO}/results.tsv` exists and has entries
   - Read the entries — each should have commit, precision, status, description
   - Check `${RAG_SYSTEM_REPO}` git log — should show experiment commits (if any were kept)
   - Run eval one final time to get the current metric

5. PASS criteria:
   - results.tsv has at least 1 entry
   - Each entry has all 4 fields (commit, precision, status, description)
   - Final eval produces a valid report
   - No crashes or errors in the loop

### Test 7: Verify keep/discard worked correctly

Read results.tsv from Test 6:
- For each "keep" entry: verify that commit exists in git log
- For each "discard" entry: verify that commit does NOT exist in git log (was reset)
- PASS if all keep/discard states are consistent with git history

## Phase 3: Supervisor Integration Test

### Test 8: Supervisor can snapshot the state
```bash
cd ${SUPERVISOR_REPO} && pixi run snapshot --label "integration-test"
```
- PASS if snapshot directory is created in `.supervisor/snapshots/`
- Report snapshot path

## Summary

Print a final summary:
```
=== INTEGRATION TEST RESULTS ===
Phase 1: Infrastructure
  Test 1: RAG eval report         PASS/FAIL  (precision_at_5=X.XX)
  Test 2: RAG unit tests          PASS/FAIL  (N passed)
  Test 3: Research loop assets    PASS/FAIL
  Test 4: Supervisor prompt-list  PASS/FAIL
  Test 5: Cross-repo paths       PASS/FAIL

Phase 2: Live Research Loop
  Test 6: Research iterations     PASS/FAIL  (N iterations, baseline=X.XX → final=Y.YY)
  Test 7: Keep/discard integrity  PASS/FAIL  (N kept, M discarded)

Phase 3: Supervisor
  Test 8: Snapshot creation       PASS/FAIL

Total: X/8 passed
```
