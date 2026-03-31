# SAR — Supervised Agentic Research

Integration hub for the SAR multi-repo system. Deploys, tests, and manages five interconnected repositories that implement the [Karpathy autonomous experiment loop](https://x.com/kaborojevic/status/1879189693837881833) pattern for iterative AI-driven improvement.

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    sar-integration (this repo)                        │
│  /deploy  /delete  /test  /supervisor-start  /supervisor-stop         │
│  /supervisor-list  /supervisor-monitor  /setup-env                   │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ orchestrates
                            v
┌──────────────────────────────────────────────────────────────────────┐
│                       sar-supervisor                                  │
│  Outer researcher: monitors, snapshots, edits researcher prompts     │
│  Domain-agnostic — does NOT know what the target is                  │
│  Skills: /start  /stop  /clean  /edit-prompts                        │
│  CLI: pixi run researcher-loop | researcher-variant start | ...      │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ launches & monitors
                            v
┌──────────────────────────────────────────────────────────────────────┐
│                     sar-research-loop                                  │
│  Inner researcher: autonomous evaluate -> hypothesize -> improve loop │
│  Skills: /start  /clean  /edit-target-prompts                        │
│  Agents: evaluator, improver                                         │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ modifies & evaluates
                            v
┌──────────────────────────────────────────────────────────────────────┐
│                       sar-rag-target                                  │
│  Target system: RAG search over QASPER scientific papers             │
│  Skills: /run (single entry point)  /reset                           │
│  Metric: mrr (maximize)                                              │
└──────────────────────────────────────────────────────────────────────┘

Shared library (used by supervisor + research-loop):
┌──────────────────────────────────────────────────────────────────────┐
│                     sar-harness-core                                  │
│  Checkpointing, prompt editing, metrics, git utilities               │
└──────────────────────────────────────────────────────────────────────┘
```

## Repos

| Repo | Role | Skills |
|------|------|--------|
| **sar-supervisor** | Outer researcher: monitors, edits researcher prompts | `/start`, `/stop`, `/clean`, `/edit-prompts` |
| **sar-research-loop** | Inner researcher: autonomous research loop | `/start`, `/clean`, `/edit-target-prompts` |
| **sar-rag-target** | Target being improved (RAG search) | `/run`, `/reset` |
| **sar-harness-core** | Shared Python library | *(no skills)* |
| **sar-integration** | This repo — deploy, test, manage | `/deploy`, `/delete`, `/test`, `/supervisor-start` |

## Quick Start

```bash
# 1. Clone this integration hub
git clone <this-repo> sar-integration && cd sar-integration

# 2. Install
pixi install

# 3. Deploy all repos (clones and configures the 4 SAR repos)
claude -p /deploy

# 4. Run integration tests (18 tests: infra, clean state, live E2E)
claude -p /test

# 5. Start the supervisor (launches the full research loop)
claude -p /supervisor-start
```

## Key Ideas

- **Two-level research** — supervisor improves researcher methodology; researcher improves target quality
- **Separation of concerns** — supervisor is domain-agnostic; each layer interacts only with its immediate child
- **Parallel variants** — both levels support isolated parallel variants via `git clone --local` (separate `.git`, zero shared state)
- **Profile rotation** — each level uses a different `CLAUDE_CONFIG_DIR` (I+1 pattern) to spread API quota
- **Merge strategies** — winner-takes-all, cherry-pick, or branch-and-continue to reconcile parallel results
- **Prompt edits via harness** — all `.claude/` file edits go through `harness_core.prompt_editor` (logged, diffed, auto-committed)
- **AI-operated** — the system runs autonomously; user intervenes only for debugging or changing objectives

See [`CLAUDE.md`](CLAUDE.md) for detailed operational rules, separation of concerns, per-repo interfaces (pixi tasks, agents, rules, hooks), operations guide, and technical standards.
