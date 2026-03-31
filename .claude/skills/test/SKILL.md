---
name: test
description: "Run REAL end-to-end integration tests for the SAR system"
user_invocable: true
---

# /test — SAR End-to-End Tests

Test the full SAR pipeline. NO dry runs. NO simulations. NO shortcuts. ALL operations go through each repo's own skills or pixi tasks.

## Configuration

Read `.env` from the workspace root for repo paths:
- `SUPERVISOR_REPO`, `RESEARCH_LOOP_REPO`, `RAG_TARGET_REPO`, `HARNESS_CORE_REPO`

## Execution Model

Run EACH test phase as a separate subagent. This isolates failures and keeps context clean.

## Phase 1: Infrastructure Verification

Dispatch a subagent for Phase 1:

```
Agent(subagent_type="general-purpose", prompt="Run SAR infrastructure tests. Read .env from the workspace root to get repo paths. Then run these tests sequentially, reporting PASS/FAIL for each:

Test 1: harness-core tests
  cd <HARNESS_CORE_REPO> && pixi install -e dev && pixi run -e dev test
  PASS if all tests pass.

Test 2: RAG target eval produces real metrics
  cd <RAG_TARGET_REPO> && rm -rf /tmp/rag-index-cache && pixi run eval
  PASS if /tmp/rag-eval-report.json exists and contains mrr.
  Record the baseline precision value.

Test 3: RAG target unit tests pass
  cd <RAG_TARGET_REPO> && pixi install -e dev && pixi run -e dev test
  PASS if all tests pass.

Test 4: Research loop assets exist
  Check these files exist in <RESEARCH_LOOP_REPO> and are > 100 bytes:
  .claude/skills/start/SKILL.md
  .claude/agents/evaluator.md
  .claude/agents/improver.md

Test 5: Supervisor discovers research loop assets
  cd <SUPERVISOR_REPO> && pixi run researcher-dot-claude-list
  PASS if output lists skill, evaluator, and improver.

Test 6: Supervisor has /start, /stop, /clean skills
  Check these files exist in <SUPERVISOR_REPO>:
  .claude/skills/start/SKILL.md
  .claude/skills/stop/SKILL.md
  .claude/skills/clean/SKILL.md

Test 7: Cross-repo paths resolve
  Read <SUPERVISOR_REPO>/harness.toml, check supervised.repo resolves to <RESEARCH_LOOP_REPO>.
  Check <RESEARCH_LOOP_REPO>/.claude/agents/evaluator.md references sar-rag-target.

Test 12: Package names
  Verify all 4 repos have correct SAR package names:
  grep '^name = .sar-' in <HARNESS_CORE_REPO>/pyproject.toml
  grep '^name = .sar-' in <SUPERVISOR_REPO>/pyproject.toml
  grep '^name = .sar-' in <RESEARCH_LOOP_REPO>/pyproject.toml
  grep '^name = .sar-' in <RAG_TARGET_REPO>/pyproject.toml
  PASS if all 4 match the pattern name = \"sar-...\"

Test 13: Python versions
  Check requires-python in each repo's pyproject.toml:
  <HARNESS_CORE_REPO>: must contain 3.14
  <SUPERVISOR_REPO>: must contain 3.14
  <RESEARCH_LOOP_REPO>: must contain 3.14
  <RAG_TARGET_REPO>: must contain 3.13
  PASS if all versions match expected.

Test 14: Harness-core import
  cd <SUPERVISOR_REPO> && pixi run python -c 'from harness_core import capture_code_state, extract_metric, metric_trend'
  PASS if exit code is 0.

Test 15: RAG target skills
  Check these files exist in <RAG_TARGET_REPO> and are > 100 bytes:
  .claude/skills/run/SKILL.md
  .claude/skills/reset/SKILL.md
  PASS if both exist and are > 100 bytes.

Test 16: Prompt-read content
  cd <SUPERVISOR_REPO> && pixi run researcher-dot-claude-read skill
  cd <SUPERVISOR_REPO> && pixi run researcher-dot-claude-read evaluator
  cd <SUPERVISOR_REPO> && pixi run researcher-dot-claude-read improver
  PASS if all three return non-empty content (at least 50 characters each).

Test 17: Variant namespace isolation
  Generate two researcher variant IDs: test-iso-aaa and test-iso-bbb.
  Verify the following paths would NOT collide:
  - ../sar-rag-target--test-iso-aaa vs ../sar-rag-target--test-iso-bbb
  - /tmp/rag-index-cache--test-iso-aaa-v1 vs /tmp/rag-index-cache--test-iso-bbb-v1
  - /tmp/rag-eval-report--test-iso-aaa-v1.json vs /tmp/rag-eval-report--test-iso-bbb-v1.json
  PASS if all three pairs are distinct strings (trivially true by construction, but verify the naming convention produces non-overlapping paths).

Report a summary table with PASS/FAIL for each test and the baseline precision value.")
```

## Phase 2: Clean State via Skills

Before the live test, ensure all repos are in a clean state by calling their skills.

Dispatch a subagent for Phase 2 cleanup:

```
Agent(subagent_type="general-purpose", prompt="Clean all SAR repos for a fresh test run. Read .env from workspace root for paths.

Step 1: Reset RAG target to seed
  cd <RAG_TARGET_REPO> && git reset --hard seed && git tag -f baseline seed && rm -rf /tmp/rag-index-cache && rm -f /tmp/rag-eval-report.json
  Then verify: pixi run eval
  Report the baseline mrr.

Step 2: Clean research loop
  cd <RESEARCH_LOOP_REPO> && rm -f results.tsv

Step 3: Clean supervisor
  cd <SUPERVISOR_REPO> && pixi run researcher-stop 2>/dev/null; pixi run clean --include-log --include-snapshots 2>/dev/null; rm -rf .supervisor

Report what was cleaned and the verified baseline metric.")
```

## Phase 3: Live E2E Test via Supervisor

This is the critical test. The supervisor launches the research loop, which improves the RAG target.

Dispatch a subagent for Phase 3:

```
Agent(subagent_type="general-purpose", prompt="Run the live SAR E2E test via the supervisor. Read .env from workspace root for paths.

IMPORTANT: This test runs REAL Claude sessions. It will take several minutes.

Step 1: Record baseline
  cd <RAG_TARGET_REPO> && git log --oneline -1
  Read /tmp/rag-eval-report.json for baseline mrr.

Step 2: Start supervisor loop
  cd <SUPERVISOR_REPO> && pixi run researcher-loop --no-clean > /tmp/sar-supervisor-loop.log 2>&1 &
  Record the PID.

Step 3: Poll for results
  Every 30 seconds, check:
  - cd <SUPERVISOR_REPO> && pixi run researcher-status (is it running?)
  - cat <RESEARCH_LOOP_REPO>/results.tsv (how many iterations?)

  Continue until:
  - results.tsv has >= 2 non-header entries, OR
  - 15 minutes have elapsed

  Then stop: cd <SUPERVISOR_REPO> && pixi run researcher-stop

Step 4: Verify run duration
  Read the supervisor state file at <SUPERVISOR_REPO>/.supervisor/start-state.json (or use pixi run researcher-status --json).
  Check started_at timestamp — the run must have lasted >= 5 minutes of actual runtime.
  If the run lasted < 5 minutes, report WARNING (not failure) — it may have completed quickly.

Step 5: Verify results
  Test 8 - Supervisor ran: PASS if results.tsv has >= 1 non-header entry

  Test 9 - Snapshots captured:
    cd <SUPERVISOR_REPO> && pixi run researcher-history
    PASS if history shows at least 1 snapshot with a metric value.

  Test 10 - Keep/discard integrity:
    Read results.tsv. For each entry:
    - If status=keep: verify that commit hash appears in cd <RAG_TARGET_REPO> && git log --oneline
    - If status=discard: verify that commit hash does NOT appear in git log
    PASS if all entries are consistent.

  Test 11 - Final metric vs baseline:
    cd <RAG_TARGET_REPO> && rm -rf /tmp/rag-index-cache && pixi run eval
    Read /tmp/rag-eval-report.json.
    Compare final mrr to the Phase 1 baseline.
    PASS if final precision >= baseline precision (non-regression).
    Report: baseline precision -> final precision, number of kept/discarded.

  Test 11a - History has metrics:
    cd <SUPERVISOR_REPO> && pixi run researcher-history --json
    Parse the JSON output. Check that at least 1 snapshot has a non-null primary_metric.
    PASS if >= 1 snapshot has non-null primary_metric.

Report a summary table with PASS/FAIL for tests 8-11, 11a.")
```

## Phase 4: Summary

After all subagents complete, print the combined summary:

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
  Test 12: Package names          PASS/FAIL
  Test 13: Python versions        PASS/FAIL
  Test 14: Harness-core import    PASS/FAIL
  Test 15: RAG target skills      PASS/FAIL
  Test 16: Prompt-read content    PASS/FAIL
  Test 17: Variant namespace isolation  PASS/FAIL

Phase 2: Clean State
  All repos cleaned               PASS/FAIL

Phase 3: E2E via Supervisor
  Test 8:  Supervisor loop ran     PASS/FAIL  (N iterations)
  Test 9:  Snapshots captured      PASS/FAIL
  Test 10: Keep/discard integrity  PASS/FAIL
  Test 11: Metric non-regression   PASS/FAIL  (X.XX → Y.YY)
  Test 11a: History has metrics    PASS/FAIL

Total: X/18 passed
  Phase 1: Tests 1-7, 12-17 (13 tests)
  Phase 2: Clean state (1 check)
  Phase 3: Tests 8-11, 11a (4 tests)
```

If any test fails, report the failure details and suggest fixes.
