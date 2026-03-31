# SAR — Supervised Agentic Research

Integration hub for the SAR multi-repo system. An enhanced version of [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) — adding a supervision layer that monitors the researcher, edits its prompts, runs parallel variants, and merges winners. Five interconnected repositories that implement autonomous AI-driven research with two-level oversight.

## Repos

| Repo | Role | Link |
|------|------|------|
| [**sar-integration**](https://github.com/pgagarinov/sar-integration) | This repo — deploy, test, orchestrate | Hub |
| [**sar-supervisor**](https://github.com/pgagarinov/sar-supervisor) | Outer researcher: monitors, snapshots, edits researcher prompts | Domain-agnostic |
| [**sar-research-loop**](https://github.com/pgagarinov/sar-research-loop) | Inner researcher: autonomous evaluate → hypothesize → improve loop | Domain-specific |
| [**sar-rag-target**](https://github.com/pgagarinov/sar-rag-target) | Target being improved — **seed only**, the researcher evolves it | RAG over QASPER |
| [**sar-harness-core**](https://github.com/pgagarinov/sar-harness-core) | Shared Python library: checkpointing, prompt editing, metrics, git | No skills |

## The Target is a Seed

The target repo (`sar-rag-target`) contains only the **seed state** — a minimal RAG pipeline over 1,169 QASPER scientific papers with baseline NDCG@5 ≈ 0.05. The researcher's job is to improve it autonomously. The seed includes:

- USearch vector index (HNSW, f16) with MLX embeddings on Apple Silicon
- 2,814 evaluation questions with gold evidence labels from QASPER annotators
- Index caching (12s cache hit vs 80s rebuild)
- Simple vector retrieval — no BM25, no reranking, no fancy techniques

Everything above baseline is research output, not committed infrastructure.

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
│  Inner researcher: autonomous evaluate → hypothesize → improve loop  │
│  Skills: /start  /clean  /edit-target-prompts                        │
│  Agents: evaluator, improver                                         │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ modifies & evaluates
                            v
┌──────────────────────────────────────────────────────────────────────┐
│                       sar-rag-target (seed)                           │
│  Target: RAG search over QASPER scientific papers                    │
│  Skills: /run (single entry point)  /reset                           │
│  Metric: ndcg_at_5 (maximize)                                        │
└──────────────────────────────────────────────────────────────────────┘

Shared library (used by supervisor + research-loop):
┌──────────────────────────────────────────────────────────────────────┐
│                     sar-harness-core                                  │
│  Checkpointing, prompt editing, metrics, git utilities               │
└──────────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Clone this integration hub
git clone git@github.com:pgagarinov/sar-integration.git && cd sar-integration

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
