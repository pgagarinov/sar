# Supervisor Monitor Agent

Collect SAR supervisor stats and print a tree. Run bash commands, format the output. Print ONLY the tree — no commentary, no preamble.

## Paths

```
SUP=/Users/peter/_Git/_Claude/_KL/sar-supervisor
RES=/Users/peter/_Git/_Claude/_KL/sar-research-loop
TGT=/Users/peter/_Git/_Claude/_KL/sar-rag-target
```

## Data to collect

Run ALL of these:

1. Researcher status:
   ```bash
   cd $SUP && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-status 2>&1
   ```

2. Supervisor profile (from state file):
   ```bash
   cat $SUP/.supervisor/start-state.json 2>/dev/null
   ```
   Extract `CLAUDE_CONFIG_DIR=<profile>` from the command field.

3. Target metrics:
   ```bash
   cat /tmp/rag-eval-report.json 2>/dev/null
   ```

4. Main researcher runs:
   ```bash
   wc -l $RES/results.tsv 2>/dev/null
   grep -c keep $RES/results.tsv 2>/dev/null
   grep -c discard $RES/results.tsv 2>/dev/null
   tail -3 $RES/results.tsv 2>/dev/null
   ```

5. Researcher variants:
   ```bash
   cd $SUP && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-variant list --json 2>&1
   ```

6. For EACH variant `{rv_id}` from step 5:
   ```bash
   cat $SUP/.supervisor/start--{rv_id}-state.json 2>/dev/null
   head -3 /tmp/sar-research-loop--{rv_id}/.claude/skills/start/SKILL.md 2>/dev/null
   wc -l /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
   grep -c keep /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
   grep -c discard /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
   tail -3 /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
   ls -d $TGT--{rv_id}-tv-* 2>/dev/null
   cat /tmp/rag-eval-report--{rv_id}-tv-*.json 2>/dev/null
   ```

## Output format

Print the tree in this EXACT format:

```
Hub: <CLAUDE_CONFIG_DIR from environment>
└── Supervisor: <supervisor profile>
    │
    ├── Researcher (main): <main profile>
    │   PID: 95600  running
    │   │
    │   └── Target: P@5=0.65  R@5=0.575
    │       Runs (last 3 of 5: 2 keep, 3 discard):
    │         #3  112ba8b  0.65  baseline
    │         #4  1cc81ef  0.35  discard  chunk overlap
    │         #5  eca93b6  0.60  discard  swap RRF
    │
    ├── Researcher Variant rv-001 (precision-safe): <rv-001 profile>
    │   PID: 96001  running
    │   │
    │   ├── Target Variant rv-001-tv-1: P@5=0.70  R@5=0.62
    │   └── Target Variant rv-001-tv-2: P@5=0.68  R@5=0.64
    │   Runs (last 3 of 8: 3 keep, 5 discard):
    │     #6  ccc9012  0.68  keep     BM25 stop words
    │     #7  ddd3456  0.62  discard  heading-aware
    │     #8  eee7890  0.64  keep     overlap 300
    │
    └── Researcher Variant rv-002 (evaluator-direct): <rv-002 profile>
        PID: 96002  stopped
        │
        └── Target Variant rv-002-tv-1: P@5=0.55  R@5=0.50
        Runs (2: 0 keep, 2 discard):
          #1  fff1234  0.65  baseline
          #2  ggg5678  0.55  discard  alternate eval
```

## Rules

- The main researcher IS a variant — always show it as "Researcher (main)". Never say "no variants" if main is running or has runs.
- Additional researcher variants (rv-*) are siblings of main under the Supervisor node.
- Use `├──` for non-last children, `└──` for last child, `│` for continuing lines.
- If no eval report: show "no report yet" for that target.
- If no results.tsv: show "no runs yet".
- If main is not running AND no variants exist AND no results.tsv: show "(all stopped)" under Supervisor.
- Truncate run descriptions to 60 chars. Show commit hash as first 7 chars.
- Print ONLY the tree. No preamble, no explanation, no "here is the tree".
