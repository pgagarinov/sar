---
name: test-integration
description: "Verify all 3 repos work together end-to-end"
user_invocable: true
---

# /test-integration — Integration Test

Verify that the supervisor harness, research loop, and RAG search system are correctly deployed and work together.

## Configuration

Read `.env` from the workspace root for repo paths.

## Test Steps

Run each test and report PASS/FAIL. Continue even if a test fails.

### Test 1: RAG System — eval produces report
```bash
cd ${RAG_SYSTEM_REPO} && rm -rf /tmp/fluxapi-chroma && pixi run eval
```
- PASS if `/tmp/rag-eval-report.json` exists and contains `precision_at_5` field
- Report the metric values

### Test 2: RAG System — tests pass
```bash
cd ${RAG_SYSTEM_REPO} && pixi run -e dev test
```
- PASS if all tests pass

### Test 3: Research Loop — skill and agents exist
Check that these files exist in `${RESEARCH_LOOP_REPO}`:
- `.claude/skills/improve-rag/SKILL.md`
- `.claude/agents/evaluator.md`
- `.claude/agents/improver.md`
- PASS if all exist

### Test 4: Research Loop — can access RAG system
```bash
ls ${RAG_SYSTEM_REPO}/src/rag/retriever.py
ls ${RAG_SYSTEM_REPO}/corpus/eval_set.json
```
- PASS if files are accessible from the research loop's perspective

### Test 5: Supervisor — prompt-list discovers assets
```bash
cd ${SUPERVISOR_REPO} && pixi run prompt-list
```
- PASS if it lists `improve-rag` skill and `evaluator`/`improver` agents

### Test 6: Supervisor — dry-run start
```bash
cd ${SUPERVISOR_REPO} && pixi run start -- --dry-run
```
- PASS if it outputs a valid launch command without errors

### Test 7: Cross-repo paths are consistent
- Verify that `${SUPERVISOR_REPO}/harness.toml` `supervised.repo` resolves to `${RESEARCH_LOOP_REPO}`
- Verify that `${RESEARCH_LOOP_REPO}/.claude/agents/evaluator.md` references a path that resolves to `${RAG_SYSTEM_REPO}`
- PASS if paths are consistent

## Summary

Print a summary table:
```
Test 1: RAG eval report      PASS/FAIL  (precision_at_5=X.XX)
Test 2: RAG tests             PASS/FAIL  (N passed)
Test 3: Research loop assets   PASS/FAIL
Test 4: Cross-repo access     PASS/FAIL
Test 5: Supervisor prompt-list PASS/FAIL
Test 6: Supervisor dry-run     PASS/FAIL
Test 7: Path consistency       PASS/FAIL
```

Exit with the count of failures.
