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

## How Operations Should Work

To clean everything before a fresh run:
```
sar-supervisor:    claude -p /clean    # stops loop, cleans state
sar-research-loop: claude -p /clean    # removes results.tsv
sar-rag-target:    claude -p /reset    # reverts code, cleans index
```

To start a research cycle:
```
sar-supervisor:    claude -p /start    # launches research loop, begins monitoring
```

To stop:
```
sar-supervisor:    claude -p /stop     # stops loop, captures final snapshot
```

The integration hub's `/test-integration` skill orchestrates all of this through the supervisor's entry points and records run history so the outer researcher can compare runs and decide what to edit next.

## Operator Model

This loop is operated by **AI**, not by the user.

- The **inner worker** is the autonomous agent doing the actual work (`claude -p /start` running inside sar-research-loop).
- The **outer researcher** is another AI agent (in the sar-supervisor repo) that reads snapshots, edits prompt assets, and decides when to stop/restart.
- The **user** should not be manually performing the monitoring/edit/restart cycle except for exceptional debugging or changing the overall objective.

**The outer researcher MUST NOT run any commands directly in the supervised repo.** All interaction goes through the harness CLI (`pixi run ...`) or the `/edit-prompts` skill.

## Integration Hub Skills

### /deploy
Clones all 4 SAR repos from GitHub, installs dependencies (harness-core first since others depend on it), and verifies cross-repo paths resolve correctly.

### /delete
Removes all deployed repos and cleans temp files. Only removes configured paths — never touches the integration hub itself.

### /test-integration
Full end-to-end test suite:
- **Phase 1**: Infrastructure verification (7 tests) — harness-core tests, RAG eval, research loop assets, supervisor discovery, cross-repo paths
- **Phase 2**: Clean state via skills — reset target, clean loop, clean supervisor
- **Phase 3**: Live E2E via supervisor (4 tests) — start loop, poll results, verify snapshots, check metric improvement
