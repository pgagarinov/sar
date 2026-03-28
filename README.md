# SAR — Supervised Agentic Research

Integration hub for the SAR multi-repo system. Deploys, tests, and manages five interconnected repositories that implement the [Karpathy autonomous experiment loop](https://x.com/kaborojevic/status/1879189693837881833) pattern for iterative AI-driven improvement.

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    sar-integration (this repo)                        │
│           /deploy  /delete  /test  /start-supervisor                 │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ orchestrates
                            v
┌──────────────────────────────────────────────────────────────────────┐
│                       sar-supervisor                                  │
│  Outer researcher: monitors, snapshots, edits researcher prompts     │
│  Domain-agnostic — does NOT know what the target is                  │
│  Skills: /start  /stop  /clean  /edit-prompts                        │
│  CLI: pixi run loop | experiment start | prompt-edit | ...           │
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
│  Target system: RAG search over FluxAPI docs                         │
│  Skills: /run  /reset  /search                                       │
│  Agents: retriever, reranker, chunker                                │
│  Metric: precision_at_5 (maximize)                                   │
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
| **sar-research-loop** | Inner researcher: autonomous experiment loop | `/start`, `/clean`, `/edit-target-prompts` |
| **sar-rag-target** | Target being improved (RAG search) | `/run`, `/reset`, `/search` |
| **sar-harness-core** | Shared Python library | *(no skills)* |
| **sar-integration** | This repo — deploy, test, manage | `/deploy`, `/delete`, `/test`, `/start-supervisor` |

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
claude -p /start-supervisor
```

## Key Ideas

- **Two-level research** — supervisor improves researcher methodology; researcher improves target quality
- **Separation of concerns** — supervisor is domain-agnostic; each layer interacts only with its immediate child
- **Parallel experiments** — both levels support isolated parallel variants via git worktrees + env vars
- **Prompt edits via harness** — all `.claude/` file edits go through `harness_core.prompt_editor` (logged, diffed, auto-committed)
- **AI-operated** — the system runs autonomously; user intervenes only for debugging or changing objectives

See [`CLAUDE.md`](CLAUDE.md) for detailed operational rules, separation of concerns, per-repo interfaces (pixi tasks, agents, rules, hooks), operations guide, and technical standards.
