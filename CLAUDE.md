# CLAUDE.md — SAR Integration Hub

See `README.md` for the system overview, architecture diagram, repo table, and quick start.

## Maintenance

When changing architecture, skills, repo structure, or test counts, update `README.md` to match. The README is the human-facing overview; this file is the AI-facing operational guide.

## Design Principles

These principles apply to ALL code, prompts, tests, and skills across ALL repos in this system:

- **NO STUBS** — every function must have a real, working implementation
- **NO FAILOVERS** — if something fails, fix it, don't work around it
- **NO DRY RUNS** — always run real evaluations and real tests, never simulate
- **NO HALF-DONE IMPLEMENTATIONS** — every change must be complete and tested
- **NO SHORTCUTS** — follow the full discipline every time
- **ALL OPERATIONS GO THROUGH SKILLS** — never run direct commands on another repo's internals. Each repo exposes its operations as skills (`claude -p /skill`) or pixi tasks (`pixi run task`). The integration hub orchestrates by calling these interfaces, never by reaching into `.supervisor/`, `results.tsv`, or other internal state directly.
- **PROMPT EDITS ONLY VIA HARNESS** — `.claude/` files in any repo are NEVER edited directly. Use the prompt-edit pixi tasks (`pixi run prompt-edit`, `pixi run target-prompt-edit`). These log, diff, and auto-commit every change.

## System Architecture

### Two-Level Research

Both the supervisor and the researcher do research — at different scopes:

| Layer | Improves | By editing | Metric source |
|-------|----------|-----------|---------------|
| **Supervisor** | Researcher's methodology | Researcher's `.claude/` (SKILL.md, agents, rules) via `pixi run prompt-edit` | harness.toml `[reports.metric]` |
| **Researcher** | Target's quality | Target's `src/` code AND target's `.claude/` (skills, agents, rules) via `pixi run target-prompt-edit` | Eval report from target |

### Separation of Concerns

**The supervisor does NOT know what the target is.** It is domain-agnostic. It sees only:
- A scalar metric (from harness.toml) with a direction (maximize/minimize)
- The researcher's prompt assets
- The researcher's behavior patterns (from stream-json log analysis)

The supervisor improves researcher methodology — experiment discipline, stagnation recovery, keep/discard logic, agent dispatch efficiency. Never the target's domain.

**The integration hub does NOT know about researcher internals.** It monitors only the supervisor process. Each layer interacts only with its immediate child.

### Parallel Experiments

Both levels support parallel experiments with structural isolation (no coordination needed):

**Supervisor → multiple researcher variants (Level 1):**
- Each experiment gets an isolated research-loop worktree with its own SKILL.md variant
- `pixi run experiment start --id exp-X --variant experiments/variants/X.md`
- Isolated PID/state/log files per experiment
- `pixi run experiment list/compare` for monitoring

**Researcher → multiple target variants (Level 2):**
- Each variant gets a target worktree: `git worktree add ../sar-rag-target--{variant_id}`
- Isolated temp files via env vars: `CHROMA_PERSIST_DIR`, `RAG_REPORT_PATH`
- Target's `src/rag/paths.py` reads these env vars (infrastructure file, never edited by researcher)

## Repos and Their Interfaces

### sar-harness-core — Shared Library

Python package providing infrastructure used by supervisor and researcher. No skills, no CLI.

**Exports:** `capture_code_state`, `restore_code_state`, `safe_revert`, `resolve_snapshot`, `list_assets`, `read_asset`, `edit_asset`, `diff_text`, `extract_metric`, `report_summary`, `metric_trend`, `git_command`, `git_status`, `commit_claude_changes`

**Key principle:** All prompt editing across the system goes through `harness_core.prompt_editor`. This ensures every `.claude/` change is logged, diffed, and auto-committed.

### sar-supervisor — Outer Researcher

Monitors and steers the research loop. Domain-agnostic.

**Skills:**
| Skill | Purpose |
|-------|---------|
| `/start` | Launch researcher, begin active supervision (single or parallel experiment mode) |
| `/stop` | Stop researcher, capture final snapshot |
| `/clean` | Remove supervisor state, logs, temp files |
| `/edit-prompts` | Read/edit/diff researcher's `.claude/` files via `pixi run prompt-read/edit/diff` |

**Key pixi tasks:**
| Task | Purpose |
|------|---------|
| `loop` | Start researcher + monitor in blocking loop (stop hook fires every ~120s) |
| `start` | Start researcher as background process |
| `stop` | Stop researcher process |
| `status` | Check if researcher is running |
| `snapshot` | Capture current state (log, reports, prompt assets, git state) |
| `history` | Show snapshot history with metric progression |
| `monitor` | Follow log analysis in real-time |
| `prompt-list/read/edit/diff/history` | Manage researcher's `.claude/` files |
| `experiment start/stop/list/compare` | Manage parallel researcher experiments |
| `restore` | Restore supervised repo to a previous snapshot |
| `revert-safe` | Checkpoint + revert supervised repo code |

**Rules:** autonomous-operation, no-direct-supervised-repo, no-raw-revert, prompt-edits

**Stop hook:** `.claude/hooks/stop-check.sh` — sleeps 120s, then runs Haiku-based log analysis. Returns metric trend, deviation detection, and action guidance (CONTINUE/INVESTIGATE/PIVOT) to the supervisor Claude session.

**Configuration:** `harness.toml` — supervised repo path, skill/agent names, report paths, metric field + direction, phase markers, revert paths, stop hook timing, experiment settings.

### sar-research-loop — Inner Researcher

Autonomous autoresearch loop. Domain-specific. Dispatches evaluator and improver agents.

**Skills:**
| Skill | Purpose |
|-------|---------|
| `/start` | Run the autonomous experiment loop (dispatch evaluator → hypothesize → dispatch improver → keep/discard) |
| `/clean` | Remove results.tsv + experiment worktrees/temp files |
| `/edit-target-prompts` | Read/edit/diff target's `.claude/` files via `pixi run target-prompt-read/edit/diff` |

**Agents:**
| Agent | Purpose |
|-------|---------|
| `evaluator` | Run target eval, report FULL metrics verbatim. Strictly read-only — never modifies code. |
| `improver` | Make ONE targeted code change + commit. Reads eval report, applies hypothesis. |

**Key pixi tasks:**
| Task | Purpose |
|------|---------|
| `target-prompt-list/read/edit/diff` | Manage target's `.claude/` files |

**Experiment protocol:** The orchestrator (SKILL.md) is a PURE DISPATCHER — it only dispatches agents, logs results, and decides keep/discard. It never reads source files, runs bash commands to inspect code, or analyzes reports directly. All context flows through agent dispatches.

**Multi-variant support:** When `EXPERIMENT_ID` env var is set, creates isolated target worktrees with per-variant `CHROMA_PERSIST_DIR` and `RAG_REPORT_PATH`.

### sar-rag-target — The Target

The RAG search system being improved. Domain-specific.

**Skills:**
| Skill | Purpose |
|-------|---------|
| `/run` | Clean ChromaDB, run eval pipeline, report metrics |
| `/reset` | Revert all code changes, clean cached state, verify baseline |
| `/search` | Interactive RAG retrieval over FluxAPI docs |

**Agents:** `chunker`, `reranker`, `retriever` (used by `/search` skill)

**Infrastructure:** `src/rag/paths.py` — reads `CHROMA_PERSIST_DIR` and `RAG_REPORT_PATH` from env vars. This file is read-only infrastructure, never edited by the researcher. It sits at the base of the git history below all experiment commits.

**Pipeline:** `config.py` → `chunker.py` → `indexer.py` → `retriever.py` → `reranker.py` → `pipeline.py` → `evaluator.py`

## How Operations Work

### Starting a research cycle
```
sar-supervisor:  claude -p /start   # launches researcher, begins active supervision
```
The supervisor's `/start` skill runs `pixi run loop --no-clean`. The stop hook fires every ~120s with analysis. The supervisor acts as an autonomous researcher — editing the researcher's prompts when stalled, pivoting strategies, running parallel experiments.

### Stopping
```
sar-supervisor:  claude -p /stop    # stops researcher, captures final snapshot
```

### Cleaning for a fresh run
```
sar-supervisor:    claude -p /clean    # stops loop, cleans state
sar-research-loop: claude -p /clean    # removes results.tsv + experiment artifacts
sar-rag-target:    claude -p /reset    # reverts code, cleans index
```

### Running parallel experiments (supervisor level)
```bash
# In sar-supervisor:
cat experiments/variants/A.md | pixi run prompt-edit skill
pixi run experiment start --id exp-A

cat experiments/variants/B.md | pixi run prompt-edit skill
pixi run experiment start --id exp-B

pixi run experiment list      # monitor
pixi run experiment compare   # compare metrics
pixi run experiment stop --id exp-B   # stop loser
```

### Editing prompts across layers
```bash
# Supervisor edits researcher's prompts:
pixi run prompt-read skill                    # in sar-supervisor
echo "new content" | pixi run prompt-edit skill

# Researcher edits target's prompts:
pixi run target-prompt-read skill             # in sar-research-loop
echo "new content" | pixi run target-prompt-edit skill
```

Both use `harness_core.prompt_editor` — logged, diffed, auto-committed.

## Operator Model

This system is operated by **AI**, not by the user.

- The **researcher** is an autonomous agent improving the target. It runs forever, dispatching evaluator/improver agents, keeping improvements and discarding regressions.
- The **supervisor** is an autonomous outer researcher. It monitors the researcher via stop hooks, reads snapshots, edits the researcher's prompt assets, and decides when to stop/restart/pivot. It improves researcher methodology, not the target.
- The **user** intervenes only for exceptional debugging or changing the overall objective.

## Integration Hub Skills

### /deploy
Clones all 4 SAR repos from GitHub, installs dependencies (harness-core first since others depend on it), and verifies cross-repo paths resolve correctly.

### /delete
Removes all deployed repos and cleans temp files. Only removes configured paths — never touches the integration hub itself.

### /start-supervisor
Launches the supervisor as a real Claude session via `claude -p /start` and monitors the supervisor process. Does NOT monitor the researcher or target directly — only the supervisor.

### /test
Full end-to-end test suite (18 tests):
- **Phase 1**: Infrastructure verification (13 tests) — harness-core tests, RAG eval, research loop assets, supervisor discovery, cross-repo paths, package names, Python versions, harness-core imports, RAG target skills, prompt-read content, namespace isolation
- **Phase 2**: Clean state via skills (1 check) — reset target, clean loop, clean supervisor
- **Phase 3**: Live E2E via supervisor (4 tests) — start loop, poll results, verify snapshots, check metric non-regression, verify history has metrics

## Technical Standards

- **Package management:** pixi only. Never pip, conda, or poetry directly.
- **Python:** 3.14 for harness-core, supervisor, research-loop. 3.13 for rag-target (chromadb compatibility).
- **Testing:** pytest via `pixi run -e dev test`. All config in pyproject.toml.
- **Paths:** pathlib.Path, never string concatenation.
- **Formatting:** f-strings, type hints on all signatures, UPPER_SNAKE_CASE constants.
- **Files:** Under 500 lines. No silent exception handling. No silent fallbacks.
