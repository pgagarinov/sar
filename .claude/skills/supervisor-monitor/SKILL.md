---
name: supervisor-monitor
description: "Live tree view of supervisor via /loop — polls every 30s"
user_invocable: true
---

# /supervisor-monitor — Live Monitoring

Sets up a recurring 30-second loop that prints the full supervisor tree.

## Implementation

When the user invokes `/supervisor-monitor`, run:

```
/loop 30s /supervisor-monitor-tick
```

The `/loop` skill handles recurring execution. Interrupt to stop.

## What each tick collects and prints

Each tick must collect ALL data and print the tree in this EXACT format:

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
```

## Data collection commands

### Hub profile
The hub's own `CLAUDE_CONFIG_DIR` from the environment.

### Supervisor profile
```bash
cat <SUPERVISOR_REPO>/.supervisor/start-state.json 2>/dev/null | python3 -c "import sys,json,re; cmd=json.load(sys.stdin).get('command',''); m=re.search(r'CLAUDE_CONFIG_DIR=(\S+)',cmd); print(m.group(1) if m else 'unknown')"
```

### Main researcher
```bash
cd <SUPERVISOR_REPO> && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-status
```

### Main researcher target metrics
```bash
cat /tmp/rag-eval-report.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'P@5={d[\"precision_at_5\"]:.4f}  R@5={d[\"recall_at_5\"]:.4f}')"
```

### Main researcher runs
```bash
# Totals
wc -l <RESEARCH_LOOP_REPO>/results.tsv
grep -c keep <RESEARCH_LOOP_REPO>/results.tsv
grep -c discard <RESEARCH_LOOP_REPO>/results.tsv
# Last 3
tail -3 <RESEARCH_LOOP_REPO>/results.tsv
```

### Researcher variants
```bash
cd <SUPERVISOR_REPO> && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-variant list --json
```

For EACH variant:
```bash
cat <SUPERVISOR_REPO>/.supervisor/start--{rv_id}-state.json 2>/dev/null   # profile
head -3 /tmp/sar-research-loop--{rv_id}/.claude/skills/start/SKILL.md     # variant name from description
tail -3 /tmp/sar-research-loop--{rv_id}/results.tsv                       # runs
wc -l /tmp/sar-research-loop--{rv_id}/results.tsv                         # total
grep -c keep /tmp/sar-research-loop--{rv_id}/results.tsv                  # keeps
grep -c discard /tmp/sar-research-loop--{rv_id}/results.tsv               # discards
```

### Target variants within each researcher variant
```bash
ls -d <RAG_TARGET_REPO>--{rv_id}-tv-* 2>/dev/null
cat /tmp/rag-eval-report--{rv_id}-tv-{N}.json 2>/dev/null
```

## Tree formatting rules

- Hub is the root node
- Supervisor is a child of Hub (shows profile)
- Researcher (main) is a child of Supervisor (shows profile, PID, running status)
- Target is a child of Researcher (shows metrics)
- Runs are indented under Target (show last 3 with commit hash, metric, status, description)
- Researcher Variants are siblings of Researcher (main), each with their own profile and PID
- Target Variants are children of their Researcher Variant
- Use `├──` for non-last children, `└──` for last child
- Use `│` for continuing vertical lines

## Handling missing data

- No researcher state file: show `(not started)`
- No eval report: show `no report yet`
- No results.tsv: show `no runs yet`
- No researcher variants: omit that section entirely
- No target variants within a researcher: just show the single target metrics

## For a one-shot snapshot

Use `/supervisor-list` instead.
