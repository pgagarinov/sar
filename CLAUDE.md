# CLAUDE.md — SAR Integration Hub

See `README.md` for the system overview, architecture diagram, repo table, and quick start.

## Maintenance

When changing architecture, skills, repo structure, or test counts, update `README.md` to match. The README is the human-facing overview; this file is the AI-facing operational guide.

## System Architecture

### Two-Level Research

Both the supervisor and the researcher do research — at different scopes:

| Layer | Improves | By editing | Calls child via |
|-------|----------|-----------|----------------|
| **Supervisor** | Researcher's methodology | Researcher's `.claude/` via `pixi run researcher-dot-claude-edit` | `claude -p /start` |
| **Researcher** | Target's quality | Target's `src/` code + `.claude/` via `pixi run target-dot-claude-edit` | `claude -p /run` |

### Skills-Only Interfaces

Each layer calls its child ONLY via `claude -p /<skill>`. No `pixi run eval`, no direct Python calls, no reaching into another repo's internals:
- Integration hub → supervisor: `claude -p /start`, `claude -p /stop`, `claude -p /clean`
- Supervisor → researcher: `claude -p /start`, `claude -p /clean`
- Researcher → target: `claude -p /run` (the ONLY entry point for evaluation)

### Parallel Researcher Variants

Both levels support parallel variants with structural isolation (no coordination needed):

**Supervisor → multiple researcher variants (Level 1):**
- Each variant gets an isolated research-loop worktree with its own SKILL.md variant
- `pixi run researcher-variant start --id rv-X --variant researcher_variants/X.md`
- Isolated PID/state/log files per researcher variant
- `pixi run researcher-variant list/compare` for monitoring

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
| `/start` | Launch researcher, begin active supervision (single or parallel variant mode) |
| `/stop` | Stop researcher, capture final snapshot |
| `/clean` | Remove supervisor state, logs, temp files |
| `/edit-prompts` | Read/edit/diff researcher's `.claude/` files via `pixi run researcher-dot-claude-read/edit/diff` |

**Key pixi tasks:**
| Task | Purpose |
|------|---------|
| `researcher-loop` | Start researcher + monitor in blocking loop (stop hook fires every ~120s) |
| `researcher-start` | Start researcher as background process |
| `researcher-stop` | Stop researcher process |
| `researcher-status` | Check if researcher is running |
| `researcher-snapshot` | Capture current state (log, reports, prompt assets, git state) |
| `researcher-history` | Show snapshot history with metric progression |
| `researcher-monitor` | Follow log analysis in real-time |
| `researcher-dot-claude-list/read/edit/diff/history` | Manage researcher's `.claude/` files |
| `researcher-variant start/stop/list/compare` | Manage parallel researcher variants |
| `researcher-restore` | Restore supervised repo to a previous snapshot |
| `revert-safe` | Checkpoint + revert supervised repo code |

**Rules:** autonomous-operation, no-direct-supervised-repo, no-raw-revert, prompt-edits

**Stop hook:** `.claude/hooks/stop-check.sh` — sleeps 120s, then runs Haiku-based log analysis. Returns metric trend, deviation detection, and action guidance (CONTINUE/INVESTIGATE/PIVOT) to the supervisor Claude session.

**Configuration:** `harness.toml` — supervised repo path, skill/agent names, report paths, metric field + direction, phase markers, revert paths, stop hook timing, variant settings.

### sar-research-loop — Inner Researcher

Autonomous autoresearch loop. Domain-specific. Dispatches evaluator and improver agents.

**Skills:**
| Skill | Purpose |
|-------|---------|
| `/start` | Run the autonomous research loop (dispatch evaluator → hypothesize → dispatch improver → keep/discard) |
| `/clean` | Remove results.tsv + variant clones/temp files |
| `/edit-target-prompts` | Read/edit/diff target's `.claude/` files via `pixi run target-dot-claude-read/edit/diff` |

**Agents:**
| Agent | Purpose |
|-------|---------|
| `evaluator` | Run target eval, report FULL metrics verbatim. Strictly read-only — never modifies code. |
| `improver` | Make ONE targeted code change + commit. Reads eval report, applies hypothesis. |

**Key pixi tasks:**
| Task | Purpose |
|------|---------|
| `target-dot-claude-list/read/edit/diff` | Manage target's `.claude/` files |

**Research protocol:** The orchestrator (SKILL.md) is a PURE DISPATCHER — it only dispatches agents, logs results, and decides keep/discard. It never reads source files, runs bash commands to inspect code, or analyzes reports directly. All context flows through agent dispatches.

**Multi-variant support:** When `RV_ID` env var is set, creates isolated target variant clones with per-variant `CHROMA_PERSIST_DIR` and `RAG_REPORT_PATH`.

### sar-rag-target — The Target

The RAG search system being improved. Domain-specific.

**Skills:**
| Skill | Purpose |
|-------|---------|
| `/run` | Clean ChromaDB, run eval pipeline, report metrics — the ONLY entry point for evaluation |
| `/reset` | Revert all code changes, clean cached state, verify baseline |

**Infrastructure:** `src/rag/paths.py` — reads `CHROMA_PERSIST_DIR` and `RAG_REPORT_PATH` from env vars. This file is read-only infrastructure, never edited by the researcher. It sits at the base of the git history below all commits.

**Pipeline:** `config.py` → `chunker.py` → `indexer.py` → `retriever.py` → `reranker.py` → `pipeline.py` → `evaluator.py`

## How Operations Work

### Starting a research cycle
```
sar-supervisor:  claude -p /start   # launches researcher, begins active supervision
```
The supervisor's `/start` skill runs `pixi run researcher-loop --no-clean`. The stop hook fires every ~120s with analysis. The supervisor acts as an autonomous researcher — editing the researcher's prompts when stalled, pivoting strategies, running parallel variants.

### Stopping
```
sar-supervisor:  claude -p /stop    # stops researcher, captures final snapshot
```

### Cleaning for a fresh run
```
sar-supervisor:    claude -p /clean    # stops loop, cleans state
sar-research-loop: claude -p /clean    # removes results.tsv + variant artifacts
sar-rag-target:    claude -p /reset    # reverts code, cleans index
```

### Running parallel researcher variants (supervisor level)
```bash
# In sar-supervisor:
cat researcher_variants/A.md | pixi run researcher-dot-claude-edit skill
pixi run researcher-variant start --id rv-A

cat researcher_variants/B.md | pixi run researcher-dot-claude-edit skill
pixi run researcher-variant start --id rv-B

pixi run researcher-variant list      # monitor
pixi run researcher-variant compare   # compare metrics
pixi run researcher-variant stop --id rv-B   # stop loser
```

### Editing prompts across layers
```bash
# Supervisor edits researcher's prompts:
pixi run researcher-dot-claude-read skill                    # in sar-supervisor
echo "new content" | pixi run researcher-dot-claude-edit skill

# Researcher edits target's prompts:
pixi run target-dot-claude-read skill             # in sar-research-loop
echo "new content" | pixi run target-dot-claude-edit skill
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

### /supervisor-start
Spawn the supervisor as a background process via `pixi run researcher-start --no-clean`, then poll `pixi run researcher-status` every 30s.

### /supervisor-stop
Stop the supervisor: `pixi run researcher-stop`.

### /supervisor-list
Dashboard: supervisor status + parallel researcher variants + recent metric history. One-shot snapshot.

### /supervisor-monitor
Live structured analysis of the researcher via `pixi run researcher-monitor --follow --json`. Includes Haiku-based anti-pattern detection.

### /test
Full end-to-end test suite (18 tests):
- **Phase 1**: Infrastructure verification (13 tests) — harness-core tests, RAG eval, research loop assets, supervisor discovery, cross-repo paths, package names, Python versions, harness-core imports, RAG target skills, prompt-read content, namespace isolation
- **Phase 2**: Clean state via skills (1 check) — reset target, clean loop, clean supervisor
- **Phase 3**: Live E2E via supervisor (4 tests) — start loop, poll results, verify snapshots, check metric non-regression, verify history has metrics

## Rules

Operational rules are in `.claude/rules/`:
- **design-principles** — NO STUBS, NO FAILOVERS, NO DRY RUNS, skills-only operations, prompt edits via harness
- **separation-of-concerns** — each layer interacts only with its immediate child, supervisor is domain-agnostic
- **explicit-over-implicit** — no fallbacks, no silent defaults, fail loudly on missing config
- **pixi-and-python** — pixi only, type hints, pathlib, f-strings, no silent exceptions
