# CLAUDE.md — SAR Integration Hub

## Design Principles

These principles apply to ALL code, prompts, tests, and skills across ALL repos in this system:

- **NO STUBS** — every function must have a real, working implementation
- **NO FAILOVERS** — if something fails, fix it, don't work around it
- **NO DRY RUNS** — always run real evaluations and real tests, never simulate
- **NO HALF-DONE IMPLEMENTATIONS** — every change must be complete and tested
- **NO SHORTCUTS** — follow the full discipline every time
- **ALL OPERATIONS GO THROUGH SKILLS** — never run direct commands on another repo's internals. Each repo exposes its operations as skills (`claude -p /skill`) or pixi tasks (`pixi run task`). The integration hub orchestrates by calling these interfaces, never by reaching into `.supervisor/`, `results.tsv`, or other internal state directly.

## Purpose

This is the **integration hub** for the SAR (Supervised Agentic Research) system. It deploys, tests, and manages a multi-repo system:

| Repo | Role | Skills |
|------|------|--------|
| `sar-supervisor` | Monitors and steers the research loop | `/start`, `/stop`, `/clean`, `/edit-prompts` |
| `sar-research-loop` | Autonomous autoresearch improving a target | `/start`, `/clean` |
| `sar-rag-target` | The RAG system being improved | `/run`, `/reset`, `/search` |
| `sar-harness-core` | Shared library (checkpointing, prompt editing, metrics) | *(Python package, no skills)* |

## Architecture

### Two-Level Research

The SAR system is a two-level autonomous research loop:

```
Supervisor (outer researcher)
  └── improves the Researcher's methodology (prompt assets)
        └── Researcher (inner worker)
              └── improves the Target (code changes)
```

Each level does research at its own scope:
- **Supervisor** improves the **researcher** — edits SKILL.md, agent prompts, strategy variants. Domain-agnostic.
- **Researcher** improves the **target** — edits target code via evaluator/improver agents. Domain-specific.

### Separation of Concerns

**The supervisor does NOT know what the target is.** It sees only:
- A scalar metric (configured in harness.toml) with a direction (maximize/minimize)
- The researcher's prompt assets (readable/editable via `pixi run prompt-read/prompt-edit`)
- The researcher's behavior patterns (from stream-json log analysis)

The supervisor improves researcher methodology (experiment discipline, stagnation recovery, keep/discard logic), never the target's domain.

**The integration hub does NOT know about researcher internals.** It monitors only the supervisor process. Each layer interacts only with its immediate child.

### Parallel Experiments

Both levels support parallel experiments:

**Supervisor → multiple researcher variants (Level 1):**
- Each experiment gets an isolated research-loop worktree with its own SKILL.md variant
- `pixi run experiment start --id exp-X` launches a researcher with `EXPERIMENT_ID` env var
- Isolated PID files, state files, and log files per experiment
- `pixi run experiment list/compare` for monitoring

**Researcher → multiple target variants (Level 2):**
- Each variant gets a target worktree: `git worktree add ../sar-rag-target--{variant_id}`
- Isolated temp files via env vars: `CHROMA_PERSIST_DIR`, `RAG_REPORT_PATH`
- Researcher manages its own variants within its experiment namespace

## How Operations Should Work

To clean everything before a fresh run:
```
sar-supervisor:    claude -p /clean    # stops loop, cleans state
sar-research-loop: claude -p /clean    # removes results.tsv
sar-rag-target:    claude -p /reset    # reverts code, cleans index
```

To start a research cycle:
```
sar-supervisor:    claude -p /start    # launches research loop, begins active supervision
```

To stop:
```
sar-supervisor:    claude -p /stop     # stops loop, captures final snapshot
```

## Operator Model

This loop is operated by **AI**, not by the user.

- The **researcher** (inner worker) is the autonomous agent improving the target (`claude -p /start` running inside sar-research-loop).
- The **supervisor** (outer researcher) is another AI agent (in sar-supervisor) that reads snapshots, edits the researcher's prompt assets, and decides when to stop/restart. It improves the researcher's methodology, not the target directly.
- The **user** should not be manually performing the monitoring/edit/restart cycle except for exceptional debugging or changing the overall objective.

**The supervisor MUST NOT run any commands directly in the target repo.** All interaction goes through the harness CLI (`pixi run ...`) or the `/edit-prompts` skill.

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
- **Phase 2**: Clean state via skills — reset target, clean loop, clean supervisor
- **Phase 3**: Live E2E via supervisor (4 tests) — start loop, poll results, verify snapshots, check metric non-regression, verify history has metrics
