---
name: supervisor-monitor
description: "Live tree view of all researcher variants and target variants"
user_invocable: true
---

# /supervisor-monitor — Full Tree Monitor

Real-time tree view showing ALL researcher variants, ALL target variants within each, metrics, and target runs.

## Configuration

Read `.env` from the workspace root for `SUPERVISOR_REPO`, `RESEARCH_LOOP_REPO`, `RAG_TARGET_REPO`.

## Data Collection

On each poll cycle, collect ALL of the following:

### 1. Main researcher

```bash
# Status + profile
cd <SUPERVISOR_REPO> && pixi run researcher-status --json

# Full payload (events, dispatches, latest text, metric)
cd <SUPERVISOR_REPO> && pixi run researcher-watch-status --once --json

# Target metrics
cat /tmp/rag-eval-report.json 2>/dev/null

# Target runs (last 5)
tail -5 <RESEARCH_LOOP_REPO>/results.tsv 2>/dev/null

# Count totals
wc -l <RESEARCH_LOOP_REPO>/results.tsv 2>/dev/null
grep -c keep <RESEARCH_LOOP_REPO>/results.tsv 2>/dev/null
grep -c discard <RESEARCH_LOOP_REPO>/results.tsv 2>/dev/null
```

### 2. Researcher variants

```bash
cd <SUPERVISOR_REPO> && pixi run researcher-variant list --json
```

For EACH researcher variant ID:
```bash
# State + profile
cat <SUPERVISOR_REPO>/.supervisor/start--{rv_id}-state.json 2>/dev/null

# Variant name (from SKILL.md description)
head -3 /tmp/sar-research-loop--{rv_id}/.claude/skills/start/SKILL.md 2>/dev/null

# Target metrics
cat /tmp/rag-eval-report--{rv_id}.json 2>/dev/null

# Target runs (last 5)
tail -5 /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null

# Totals
wc -l /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
grep -c keep /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
grep -c discard /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
```

### 3. Target variants within each researcher variant

```bash
# Discover target variant clones
ls -d <RAG_TARGET_REPO>--{rv_id}-tv-* 2>/dev/null

# For each discovered target variant:
cat /tmp/rag-eval-report--{rv_id}-tv-{N}.json 2>/dev/null
```

For the main researcher (no rv_id), check:
```bash
ls -d <RAG_TARGET_REPO>--*-tv-* 2>/dev/null
```

## Output Format

Present as a tree:

```
Hub: ~/.claude-profile-1
└── Supervisor: ~/.claude-profile-2
    │
    ├── Researcher (main): ~/.claude-profile-6
    │   PID: 95600  running  events=80
    │   Latest: "Dispatching improver for BM25..."
    │   │
    │   └── Target: P@5=0.65  R@5=0.575
    │       Runs (last 3 of 5: 2 keep, 3 discard):
    │         #3  112ba8b  0.65  baseline
    │         #4  1cc81ef  0.35  discard  chunk overlap
    │         #5  eca93b6  0.60  discard  swap RRF
    │
    ├── Researcher Variant rv-001 (precision-safe): ~/.claude-profile-9
    │   PID: 96001  running
    │   │
    │   ├── Target Variant rv-001-tv-1: P@5=0.70  R@5=0.62
    │   └── Target Variant rv-001-tv-2: P@5=0.68  R@5=0.64
    │   Runs (last 3 of 8: 3 keep, 5 discard):
    │     #6  ccc9012  0.68  keep     BM25 stop words
    │     #7  ddd3456  0.62  discard  heading-aware
    │     #8  eee7890  0.64  keep     overlap 300
    │
    └── Researcher Variant rv-002 (evaluator-direct): ~/.claude-profile-8
        PID: 96002  stopped
        │
        └── Target Variant rv-002-tv-1: P@5=0.55  R@5=0.50
        Runs (2: 0 keep, 2 discard):
          #1  fff1234  0.65  baseline
          #2  ggg5678  0.55  discard  alternate eval

COMPARISON
  Main:   R@5=0.575  (5 runs)
  rv-001: R@5=0.640  (8 runs)  ← best
  rv-002: R@5=0.500  (2 runs)
```

## Polling

Poll every 30 seconds. Repeat the full data collection and tree display. **Continue until the user interrupts. Do not ask whether to continue.**

If nothing changed since last poll, print a one-line heartbeat:
```
[HH:MM:SS] no changes (main: running, 0 researcher variants)
```

## Handling Missing Data

- If a report JSON does not exist: show "no report yet"
- If results.tsv does not exist: show "no runs yet"
- If no researcher variants: skip that section
- If no target variants within a researcher: just show the single target metrics

## Important

- ALL commands go through `pixi run` for supervisor status — direct file reads are OK for reports and results.tsv
- Use `researcher-loop-once` periodically (not every poll — every 2nd or 3rd cycle) for snapshot archiving
- Do NOT ask "want me to keep polling?"
