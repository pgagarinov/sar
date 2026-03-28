# Supervisor Harness

A generic supervisor for autonomous AI agent loops. Monitors an inner worker, detects stagnation, snapshots state, and enables iterative prompt engineering — applying the [Karpathy autonomous experiment loop](https://x.com/kaborojevic/status/1879189693837881833) pattern to any agentic system with a scalar metric.

**Key capabilities:**
- Launch, monitor, and stop an inner worker process (Claude Code session, autoresearch agent, or any autonomous loop)
- Parse `stream-json` logs to track dispatches, phases, and tool usage
- Snapshot the full context bundle: logs, reports, prompt assets, git working tree
- Detect stagnation via metric trend analysis and Haiku-based log analysis
- Manage prompt assets (skills, agents, rules) with tracked edits and diffs
- Safe revert and restore with automatic checkpointing
- A/B test prompt variants with the experiment framework

## The Universal Pattern

The Karpathy autoresearch loop treats AI training as an autonomous experiment: an agent edits code, runs a time-boxed training cycle, observes a scalar metric, and keeps or discards the change. This harness generalizes that pattern to **any** agentic system.

The insight: the quality of prompt assets is the binding constraint on the quality of any autonomous loop. By treating prompts as engineering artifacts — versioned, diffed, snapshotted, and iterated on with the same rigor as code — you can systematically improve any agent's performance.

| Concept | Claude Code inner loop | Karpathy autoresearch | Generic |
|---------|----------------------|----------------------|---------|
| Editable asset | SKILL.md + agent .md files | `program.md` + `train.py` | Configurable |
| Scalar metric | test failure count (minimize) | val_bpb (minimize) | Configurable field + direction |
| Time-boxed cycle | One inner loop run | 5-min training run | Configurable |
| Keep/discard | Keep prompts that reduce failures | Keep commits that lower val_bpb | Keep changes that improve metric |
| Inner worker | `claude -p /my-skill` | AI agent + `uv run train.py` | Configurable command |
| What supervisor edits | `.claude/skills/*/SKILL.md` | `program.md` | Configurable instruction files |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Outer Researcher (AI)                      │
│  Reads snapshots, edits prompt assets, decides keep/discard     │
│  Runs in THIS repo as a Claude Code session                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │  pixi run loop/stop/snapshot/...
                           │  /edit-prompts
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Supervisor Harness                           │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Launcher  │  │ Monitor  │  │ Snapshot │  │ Prompt Editor │  │
│  │ start/    │  │ log      │  │ code     │  │ read/edit/    │  │
│  │ stop/     │  │ analysis │  │ state    │  │ diff/history  │  │
│  │ restart   │  │ metrics  │  │ history  │  │ auto-commit   │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────┘  │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────┐  │
│  │ Stop Hook│  │ Restore  │  │ Experiment Framework         │  │
│  │ Haiku    │  │ revert-  │  │ variants / run / compare     │  │
│  │ analysis │  │ safe     │  │                              │  │
│  └──────────┘  └──────────┘  └──────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │  launches process, reads log
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Inner Worker (Autonomous Agent)               │
│  Claude Code session, autoresearch agent, or any process        │
│  with a stream-json log and a scalar metric                     │
│  Runs in the SUPERVISED repo                                    │
└─────────────────────────────────────────────────────────────────┘
```

**Three actors:**

1. **Outer researcher** — an AI agent (running in this harness repo) that reads snapshots, analyzes metric trends, hypothesizes why the inner loop stalled, edits prompt assets, and restarts. It never touches the supervised repo directly.
2. **Supervisor harness** — the Python runtime (this project) that launches/stops the inner worker, parses logs, captures snapshots, and provides the CLI. Pure plumbing.
3. **Inner worker** — the autonomous agent doing the actual work in the supervised repo. It produces a stream-json log and a JSON report with a scalar metric.

**Data flow:** inner worker log → harness parser → analysis report → snapshot (with code-state) → history.jsonl → outer researcher reads history, edits prompts, restarts.

## Quick Start

### Prerequisites

- Python 3.11+
- [pixi](https://pixi.sh) package manager
- `claude` CLI (for Claude Code inner loops) or your own inner worker command

### Setup

```bash
# 1. Clone the template
git clone <this-repo> my-supervisor
cd my-supervisor

# 2. Install dependencies
pixi install

# 3. Edit configuration — point to your supervised repo
$EDITOR harness.toml

# 4. Start the supervisor loop
pixi run loop
```

### Minimal `harness.toml`

```toml
[project]
name = "my-supervisor"

[supervised]
repo = "../my-project"              # Path to the supervised repo
default_prompt = "/my-skill"        # Default -p arg to claude
skill_name = "my-skill"             # .claude/skills/<name>/SKILL.md
agents = ["agent-a", "agent-b"]     # .claude/agents/<name>.md

[reports]
primary = "{tmp}/primary-report.json"

[reports.metric]
report = "primary"                  # Which report key has the scalar metric
field = "failed"                    # JSON field to extract
direction = "minimize"              # "minimize" or "maximize"
```

## Configuration Reference

All configuration lives in `harness.toml` at the workspace root. Path templates support `{tmp}` (expands to `/tmp`) and `{name}` (expands to `project.name`).

### `[project]`

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `name` | string | `"supervisor"` | Project name, used in `{name}` path template expansion |

### `[supervised]`

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `repo` | string | `"../supervised-project"` | Path to the supervised repo (absolute or relative to workspace) |
| `default_prompt` | string | `"/default"` | Default `-p` argument passed to `claude` |
| `skill_name` | string | `"default"` | Name of the skill under `.claude/skills/<name>/SKILL.md` |
| `agents` | list[string] | `[]` | Agent names under `.claude/agents/<name>.md` |
| `config_dirs` | list[string] | `["~/.claude"]` | Claude config directories (first = default) |

### `[reports]`

A map of report names to path templates. Each key (except `metric`) defines a report that will be monitored.

```toml
[reports]
primary = "{tmp}/primary-report.json"
secondary = "{tmp}/secondary-report.json"
```

### `[reports.metric]`

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `report` | string | `"primary"` | Which report key contains the scalar metric |
| `field` | string | `"failed"` | JSON field name to extract from the report |
| `direction` | string | `"minimize"` | `"minimize"` or `"maximize"` — determines what "best" means |

### `[log]`

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `path` | string | `"{tmp}/cc-{name}.log"` | Path template for the inner worker's stream-json log |

### `[phases]`

Optional phase sequence for heuristic deviation detection.

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `sequence` | list[string] | `[]` | Expected dispatch phase order (e.g., `["T", "S", "P"]`) |
| `labels` | map[string, string] | `{}` | Human-readable labels for each phase key |
| `markers` | map[string, string] | `{}` | Text markers to detect each phase in the log |

### `[revert]`

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `paths` | list[string] | `["src/", "tests/", "lib/"]` | Paths to revert when using `revert-safe` (not `--full`) |

### `[stop_hook]`

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `sleep_seconds` | int | `120` | Seconds to wait before running stop hook analysis (must stay under 210s hook timeout) |

## CLI Reference

All commands are run via `pixi run <command>` from the workspace root. Every subcommand accepts `--workspace-root`, `--supervised-repo`, `--log-path`, and `--config-dir` as global overrides.

### Lifecycle

| Command | Key Arguments | Purpose |
|---------|--------------|---------|
| `start` | `--prompt`, `--no-clean`, `--dry-run`, `--config-dir` | Launch the inner worker process |
| `stop` | — | Send SIGTERM (then SIGKILL) to the inner worker |
| `restart` | `--prompt` | Stop the current run, clean, and start fresh |
| `loop` | `--prompt`, `--no-clean`, `--no-archive`, `--once`, `--json`, `--interval-seconds`, `--heartbeat-seconds` | Start if needed, then monitor + auto-snapshot on changes. Exits on completion or process stop. |

### Monitoring

| Command | Key Arguments | Purpose |
|---------|--------------|---------|
| `status` | `--json` | Show PID, running state, and current prompt |
| `monitor` | `--follow`, `--json`, `--interval-seconds`, `--heartbeat-seconds` | Parse the log and display analysis (one-shot or continuous) |
| `watch-status` | `--interval-seconds`, `--json`, `--no-log`, `--immediate`, `--once` | Periodic status emitter with metric tracking, writes to `status.jsonl` |

### Data

| Command | Key Arguments | Purpose |
|---------|--------------|---------|
| `snapshot` | `--label` | Capture a full context bundle (log, reports, prompt assets, code-state, git status) |
| `history` | `--limit`, `--json` | Show recent snapshots with timestamps and metric values |
| `clean` | `--include-log`, `--include-snapshots` | Remove temp files (reports, PID, state); optionally log and snapshots |

### Code State

| Command | Key Arguments | Purpose |
|---------|--------------|---------|
| `restore` | `<identifier>`, `--dry-run`, `--no-checkpoint` | Restore supervised repo to a snapshot state. Identifier: snapshot ID prefix, full path, or `best` |
| `revert-safe` | `--label`, `--full` | Checkpoint current state, then revert configured paths (or `--full` working tree) |

### Prompt Management

| Command | Key Arguments | Purpose |
|---------|--------------|---------|
| `prompt-list` | `--json` | List all known prompt assets (skills, agents, rules) with metadata |
| `prompt-read` | `<name>` | Print an asset's full contents. Name from `prompt-list` or relative path under `.claude/` |
| `prompt-edit` | `<name>`, `--json` | Replace asset contents from stdin. Logs change, shows diff, auto-commits in supervised repo |
| `prompt-diff` | `<name>` | Show unified diff between current asset and stdin (dry run, no write) |
| `prompt-history` | `--limit`, `--json` | Show recent prompt edit log with timestamps and line counts |

## Key Concepts

### Snapshot System

Each snapshot captures the full state of the supervisor at a point in time:

- **Log artifact** — copy of the stream-json log
- **Report artifacts** — copies of all configured JSON reports
- **Prompt assets** — copies of SKILL.md and agent definitions
- **Code-state** — `tracked.patch` (binary git diff of all tracked modifications) + `untracked.tar.gz` (archive of untracked files)
- **Metadata** — `snapshot.json` with analysis report, run state, PID, timestamps

Snapshots are stored under `.supervisor/snapshots/<timestamp>[-label]/`. Every snapshot appends a line to `.supervisor/history.jsonl` with the snapshot ID, primary metric value, and path.

### Metric System

The harness extracts a scalar metric from a JSON report file:

1. The inner worker writes a JSON report to the configured path (e.g., `/tmp/primary-report.json`)
2. The harness reads the file, extracts the configured field (e.g., `"failed"`)
3. The value is recorded in `history.jsonl` with each snapshot
4. Trend analysis compares recent values to detect `improving`, `stalled`, `regressing`, or `flat`
5. `restore best` finds the snapshot with the optimal metric value (respecting `direction`)

### Stop Hook

The stop hook (`.claude/hooks/stop-check.sh`) fires periodically during a Claude Code outer researcher session, providing structured decision support:

1. **Wait** — sleeps for `stop_hook.sleep_seconds` (default 120s) to let the inner loop make progress
2. **Analyze** — runs `stop_hook.py` which:
   - Reads process state (PID, running, elapsed time)
   - Extracts metric value and trend from history
   - Counts iterations (agent dispatches)
   - Calls Haiku (via `claude --model haiku`) to analyze new log events for anti-patterns
   - Falls back to heuristic deviation detection if Haiku is unavailable
3. **Output** — returns structured JSON with status, trend, deviations, phase, and action guidance
4. **Autonomy directive** — reminds the outer researcher to act as a researcher, not a passive monitor

Detected anti-patterns include: orchestrator doing work instead of dispatching, using TodoWrite, dispatching wrong agent types, and excessive file reads with few dispatches.

### Prompt Editor

The prompt editor provides tracked, auditable mutation of `.claude/` assets in the supervised repo:

- **Dynamic discovery** — `prompt-list` builds the asset map from `harness.toml` config (skill name, agent names) plus any `rules/*.md` files
- **Edit workflow** — new content piped via stdin → unified diff generated → file written → auto-committed in supervised repo → change logged to `prompt-edits.jsonl`
- **Diff without writing** — `prompt-diff` shows what would change without modifying the file
- **History** — every edit is logged with timestamps, SHA1 hashes, and line counts

### Safe Revert & Restore

The supervised repo's working tree changes represent accumulated worker effort. The harness never discards them without checkpointing first:

- **`revert-safe`** — snapshots current state (including code-state), commits any `.claude/` changes (so they survive the revert), then runs `git checkout` on configured paths. `.claude/` prompt edits are preserved.
- **`revert-safe --full`** — same checkpoint-first pattern, but reverts the entire working tree and cleans untracked files.
- **`restore <id>`** — resolves a snapshot (by ID prefix, path, or `best`), auto-checkpoints, then applies `tracked.patch` and extracts `untracked.tar.gz`. Verifies HEAD matches before applying.
- **`restore best`** — finds the snapshot with the best primary metric value across all history.

### Experiment Framework

When the current approach stalls, run controlled experiments with different prompt strategies:

1. **Write a variant** — create a new SKILL.md in `experiments/variants/` (see `EXAMPLE-variant.md` for the template)
2. **Run the experiment** — `./experiments/run_experiment.sh <variant-file> [budget_minutes]` applies the variant, runs for the time budget, stops, and snapshots
3. **Compare results** — `python experiments/compare_experiments.py` reads `history.jsonl` and prints a sorted comparison table of all experiment-labeled snapshots

Variants are complete SKILL.md files. Each represents a hypothesis about what prompt structure will best address the remaining issues.

## Adapting for Your Project

### Example: Claude Code Inner Loop

Supervise a Claude Code session that runs a test-fix loop:

```toml
[project]
name = "my-test-fixer"

[supervised]
repo = "../my-app"
default_prompt = "/fix-tests"
skill_name = "fix-tests"
agents = ["test-runner", "code-fixer"]

[reports]
primary = "{tmp}/test-report.json"

[reports.metric]
report = "primary"
field = "failed"
direction = "minimize"

[phases]
sequence = ["T", "F"]
labels = { T = "test", F = "fix" }
markers = { T = "Running tests", F = "Fixing code" }
```

The inner loop's SKILL.md dispatches `test-runner` and `code-fixer` agents. The supervisor monitors the `failed` count, snapshots on changes, and the outer researcher edits the SKILL.md when stagnation is detected.

### Example: Karpathy Autoresearch

Supervise a training loop that optimizes validation loss:

```toml
[project]
name = "autoresearch"

[supervised]
repo = "../my-research"
default_prompt = "/train-loop"
skill_name = "train-loop"
agents = ["trainer", "evaluator"]

[reports]
primary = "{tmp}/eval-results.json"

[reports.metric]
report = "primary"
field = "val_bpb"
direction = "minimize"
```

### Example: Custom Research Loop

Any process that writes a JSON report with a scalar metric can be supervised. Configure the report path and metric field, and the harness handles the rest.

## Project Structure

```
supervisor-harness/
  CLAUDE.md                         # Agent-facing instructions (for the outer researcher AI)
  README.md                         # This file (human-facing)
  harness.toml                      # Project configuration
  pyproject.toml                    # Python package + pixi tasks

  src/supervisor_harness/
    __init__.py
    cli.py                          # 17 CLI subcommands (start, stop, loop, monitor, ...)
    config.py                       # RepoPaths, LaunchSpec, path template resolution
    supervisor.py                   # Core: analyze_log, snapshot, restore, revert, start/stop
    stop_hook.py                    # Trend analysis, Haiku log analysis, action guidance
    prompt_editor.py                # Asset discovery, read/edit/diff/history
    stream_json.py                  # Claude stream-json log parser

  experiments/
    variants/                       # SKILL.md strategy variants for A/B testing
      EXAMPLE-variant.md            # Template for new variants
    run_experiment.sh               # Run a single variant with time budget
    compare_experiments.py          # Compare results across variants

  .claude/
    hooks/stop-check.sh             # Stop hook: waits, then runs stop_hook.py
    settings.json                   # Claude Code settings
    skills/edit-prompts/SKILL.md    # /edit-prompts skill for prompt management
    rules/                          # Operational rules for the outer researcher

  .supervisor/                      # Runtime state (gitignored)
    snapshots/                      # Timestamped snapshot directories
    history.jsonl                   # Append-only metric history
    prompt-edits.jsonl              # Prompt edit audit log
    status.jsonl                    # Periodic status log from watch-status

  tests/
    test_harness.py
    fixtures/sample_stream.jsonl
```

## Design Philosophy

1. **Prompts are engineering artifacts.** Version them, diff them, snapshot them, iterate on them with the same rigor as code. The quality of your prompts is the binding constraint on your autonomous loop.

2. **Checkpoint before every destructive operation.** Every revert and restore automatically snapshots first. Code-state capture (patch + untracked archive) means any snapshot can be fully restored later.

3. **The supervisor never touches the supervised repo directly.** All interaction goes through the harness CLI or prompt editor. This separation keeps the supervisor's concerns (monitoring, snapshotting, prompt editing) cleanly isolated from the inner worker's concerns (doing the actual work).

4. **Observe, hypothesize, edit, test, learn.** Each run is an experiment. Each prompt edit is a hypothesis. The history and snapshot system lets you track what you tried, what happened, and what you learned.

5. **Detect stagnation, don't just wait.** The stop hook combines Haiku-based log analysis with heuristic anti-pattern detection and metric trend analysis. When stagnation is detected, the system provides actionable guidance, not just a number.

6. **Safe by default.** No raw `git checkout --` or `git clean -fd` exposed to the operator. Every path that discards work goes through the checkpoint-first pattern.

7. **Configuration over code.** All project-specific values live in `harness.toml`. The same harness codebase works for Claude Code sessions, autoresearch agents, and custom loops — just change the config.
