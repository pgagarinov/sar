---
name: test-integration
description: "Run REAL end-to-end integration tests via the supervisor"
user_invocable: true
---

# /test-integration — Real End-to-End Tests

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
  cd <RAG_TARGET_REPO> && rm -rf /tmp/fluxapi-chroma && pixi run eval
  PASS if /tmp/rag-eval-report.json exists and contains precision_at_5.
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
  cd <SUPERVISOR_REPO> && pixi run prompt-list
  PASS if output lists skill, evaluator, and improver.

Test 6: Supervisor has /start, /stop, /clean skills
  Check these files exist in <SUPERVISOR_REPO>:
  .claude/skills/start/SKILL.md
  .claude/skills/stop/SKILL.md
  .claude/skills/clean/SKILL.md

Test 7: Cross-repo paths resolve
  Read <SUPERVISOR_REPO>/harness.toml, check supervised.repo resolves to <RESEARCH_LOOP_REPO>.
  Check <RESEARCH_LOOP_REPO>/.claude/agents/evaluator.md references sar-rag-target.

Report a summary table with PASS/FAIL for each test and the baseline precision value.")
```

## Phase 2: Clean State via Skills

Before the live test, ensure all repos are in a clean state by calling their skills.

Dispatch a subagent for Phase 2 cleanup:

```
Agent(subagent_type="general-purpose", prompt="Clean all SAR repos for a fresh test run. Read .env from workspace root for paths.

Step 1: Reset RAG target to baseline
  cd <RAG_TARGET_REPO> && git checkout -- . && git clean -fd && rm -rf /tmp/fluxapi-chroma && rm -f /tmp/rag-eval-report.json
  Then verify: pixi run eval
  Report the baseline precision_at_5.

Step 2: Clean research loop
  cd <RESEARCH_LOOP_REPO> && rm -f results.tsv

Step 3: Clean supervisor
  cd <SUPERVISOR_REPO> && pixi run stop 2>/dev/null; pixi run clean --include-log --include-snapshots 2>/dev/null; rm -rf .supervisor

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
  Read /tmp/rag-eval-report.json for baseline precision_at_5.

Step 2: Start supervisor loop
  cd <SUPERVISOR_REPO> && pixi run loop --no-clean > /tmp/sar-supervisor-loop.log 2>&1 &
  Record the PID.

Step 3: Poll for results
  Every 30 seconds, check:
  - cd <SUPERVISOR_REPO> && pixi run status (is it running?)
  - cat <RESEARCH_LOOP_REPO>/results.tsv (how many iterations?)

  Continue until:
  - results.tsv has >= 2 non-header entries, OR
  - 10 minutes have elapsed

  Then stop: cd <SUPERVISOR_REPO> && pixi run stop

Step 4: Verify results
  Test 8 - Supervisor ran: PASS if results.tsv has >= 1 non-header entry

  Test 9 - Snapshots captured:
    cd <SUPERVISOR_REPO> && pixi run history
    PASS if history shows at least 1 snapshot with a metric value.

  Test 10 - Keep/discard integrity:
    Read results.tsv. For each entry:
    - If status=keep: verify that commit hash appears in cd <RAG_TARGET_REPO> && git log --oneline
    - If status=discard: verify that commit hash does NOT appear in git log
    PASS if all entries are consistent.

  Test 11 - Final metric:
    cd <RAG_TARGET_REPO> && rm -rf /tmp/fluxapi-chroma && pixi run eval
    Read /tmp/rag-eval-report.json.
    Report: baseline precision -> final precision, number of kept/discarded.

Report a summary table with PASS/FAIL for tests 8-11.")
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

Phase 2: Clean State
  All repos cleaned               PASS/FAIL

Phase 3: E2E via Supervisor
  Test 8:  Supervisor loop ran     PASS/FAIL  (N iterations)
  Test 9:  Snapshots captured      PASS/FAIL
  Test 10: Keep/discard integrity  PASS/FAIL
  Test 11: Metric improvement      PASS/FAIL  (X.XX → Y.YY)

Total: X/11 passed
```

If any test fails, report the failure details and suggest fixes.
