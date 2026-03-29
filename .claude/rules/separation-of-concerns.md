# Separation of Concerns

Each layer in the supervision chain interacts ONLY with its immediate child. No layer reaches past its child into deeper layers.

## The supervisor does NOT know what the target is

It is domain-agnostic. It sees only:
- A scalar metric (from harness.toml) with a direction (maximize/minimize)
- The researcher's prompt assets
- The researcher's behavior patterns (from stream-json log analysis)

The supervisor improves researcher methodology — experiment discipline, stagnation recovery, keep/discard logic, agent dispatch efficiency. Never the target's domain.

## The integration hub does NOT know about researcher internals

It monitors only the supervisor process. It never reads results.tsv, target code, or researcher logs.

## Prompt edits flow through the harness

- Supervisor edits researcher's `.claude/` via `pixi run dot-claude-edit`
- Researcher edits target's `.claude/` via `pixi run target-dot-claude-edit`
- Both use `harness_core.prompt_editor` — logged, diffed, auto-committed
