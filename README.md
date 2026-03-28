# SAR — Supervised Agentic Research

Integration hub for the SAR multi-repo system. Deploys, tests, and manages five interconnected repositories that implement the [Karpathy autonomous experiment loop](https://x.com/kaborojevic/status/1879189693837881833) pattern for iterative AI-driven improvement.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    sar-integration (this repo)                   │
│              /deploy  /delete  /test-integration                │
└──────────────────────────┬──────────────────────────────────────┘
                           │ orchestrates
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      sar-supervisor                              │
│  Outer researcher: monitors, snapshots, edits prompts           │
│  Skills: /start  /stop  /clean  /edit-prompts                   │
│  CLI: pixi run loop | stop | snapshot | prompt-list | ...       │
└──────────────────────────┬──────────────────────────────────────┘
                           │ launches & monitors
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    sar-research-loop                              │
│  Inner worker: autonomous evaluate → hypothesize → improve loop │
│  Skills: /start  /clean                                         │
│  Agents: evaluator, improver                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │ modifies & evaluates
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      sar-rag-target                               │
│  Target system: RAG search over FluxAPI docs                    │
│  Skills: /run  /reset  /search                                  │
│  Agents: retriever, reranker, chunker                           │
│  Metric: precision_at_5 (maximize)                              │
└─────────────────────────────────────────────────────────────────┘

Supporting library (no skills):
┌─────────────────────────────────────────────────────────────────┐
│                    sar-harness-core                               │
│  Shared: checkpointing, prompt editing, metrics, git utilities  │
│  Used by: sar-supervisor                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Repos

| Repo | Role | Skills |
|------|------|--------|
| **sar-supervisor** | Monitors and steers the research loop | `/start`, `/stop`, `/clean`, `/edit-prompts` |
| **sar-research-loop** | Autonomous autoresearch improving the target | `/start`, `/clean` |
| **sar-rag-target** | The RAG system being improved | `/run`, `/reset`, `/search` |
| **sar-harness-core** | Shared Python library (checkpointing, prompt editing, metrics) | *(no skills)* |
| **sar-integration** | This repo — deploy, test, manage | `/deploy`, `/delete`, `/test-integration` |

## Quick Start

```bash
# 1. Clone this integration hub
git clone <this-repo> sar-integration
cd sar-integration

# 2. Install
pixi install

# 3. Deploy all repos (clones and configures the 4 SAR repos)
claude -p /deploy

# 4. Run integration tests (11 tests: infra, clean state, live E2E)
claude -p /test-integration
```

## Skills

### /deploy
Clones all 4 SAR repos, installs dependencies (harness-core first), and verifies cross-repo paths resolve.

### /delete
Removes all deployed repos and cleans temp files (`/tmp/fluxapi-chroma`, `/tmp/rag-eval-report.json`, etc.).

### /test-integration
Runs a full end-to-end test suite:
- **Phase 1** (7 tests): Infrastructure — harness-core tests, RAG eval, research loop assets, supervisor discovery, cross-repo paths
- **Phase 2**: Clean state — reset target, clean loop, clean supervisor
- **Phase 3** (4 tests): Live E2E — start supervisor loop, poll until results, verify snapshots, check keep/discard integrity, compare final metric to baseline

## Design Principles

- **NO STUBS** — every function must have a real, working implementation
- **NO FAILOVERS** — if something fails, fix it, don't work around it
- **NO DRY RUNS** — always run real evaluations and real tests, never simulate
- **ALL OPERATIONS GO THROUGH SKILLS** — never run direct commands on another repo's internals
