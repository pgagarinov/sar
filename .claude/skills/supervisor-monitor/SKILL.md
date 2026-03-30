---
name: supervisor-monitor
description: "Live tree view of supervisor via cron — agent collects stats every 30s"
user_invocable: true
---

# /supervisor-monitor — Live Monitoring

Sets up a recurring cron that dispatches an agent every 30 seconds to collect stats and print the tree.

## Implementation

When the user invokes `/supervisor-monitor`:

1. Create a cron job that fires every minute:
   ```
   CronCreate(cron="*/1 * * * *", prompt="/supervisor-monitor-tick", recurring=true)
   ```

2. Run the first tick immediately (don't wait for cron).

3. Report the cron job ID so the user can cancel with `CronDelete`.

## What each tick does

Each tick dispatches an **agent** (subagent_type="general-purpose") with the prompt below. The agent does ALL the data collection and returns ONLY the formatted tree. No intermediate output reaches the user — just the final tree.

### Agent prompt for each tick

```
Collect SAR supervisor stats and print a tree. Run these bash commands, then format the output. Print ONLY the tree — no commentary.

Paths:
  SUP=/Users/peter/_Git/_Claude/_KL/sar-supervisor
  RES=/Users/peter/_Git/_Claude/_KL/sar-research-loop
  TGT=/Users/peter/_Git/_Claude/_KL/sar-rag-target

Commands to run:
1. cd $SUP && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-status 2>&1
2. cat $SUP/.supervisor/start-state.json 2>/dev/null
3. cat /tmp/rag-eval-report.json 2>/dev/null
4. tail -3 $RES/results.tsv 2>/dev/null
5. wc -l $RES/results.tsv 2>/dev/null; grep -c keep $RES/results.tsv 2>/dev/null; grep -c discard $RES/results.tsv 2>/dev/null
6. cd $SUP && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-variant list --json 2>&1
7. For each variant from step 6:
   - cat $SUP/.supervisor/start--{rv_id}-state.json 2>/dev/null
   - head -3 /tmp/sar-research-loop--{rv_id}/.claude/skills/start/SKILL.md 2>/dev/null
   - tail -3 /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
   - wc -l /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
   - grep -c keep /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
   - grep -c discard /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
   - ls -d $TGT--{rv_id}-tv-* 2>/dev/null
   - cat /tmp/rag-eval-report--{rv_id}-tv-*.json 2>/dev/null

Print the tree in this EXACT format (example with main + 2 variants):

Hub: <CLAUDE_CONFIG_DIR>
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

Rules:
- The main researcher IS a variant — always show it as "Researcher (main)" in the tree. Never say "no variants" if main is running.
- Additional researcher variants (rv-*) are siblings of main under the Supervisor node.
- Use ├── for non-last children, └── for last child, │ for continuing lines.
- If no eval report exists: show "no report yet" for that target.
- If no results.tsv: show "no runs yet".
- If main researcher is not running and no variants exist, show "(all stopped)" under Supervisor.
- Truncate run descriptions to 60 chars. Show commit hash as first 7 chars.
- Print ONLY the tree. No preamble, no commentary, no "here is the tree".
```

## For a one-shot snapshot

Use `/supervisor-list` instead.
