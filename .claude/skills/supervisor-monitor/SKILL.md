---
name: supervisor-monitor
description: "Live tree view of supervisor via cron — agent collects stats every 30s"
user_invocable: true
---

# /supervisor-monitor — Live Monitoring

Sets up a recurring cron that dispatches the `supervisor-monitor` agent every minute to collect stats as JSON, then renders the tree.

## Implementation

When the user invokes `/supervisor-monitor`:

1. Create a cron job:
   ```
   CronCreate(cron="*/1 * * * *", prompt="/supervisor-monitor-tick", recurring=true)
   ```

2. Run the first tick immediately (see tick logic below).

3. Report the cron job ID so the user can cancel with `CronDelete`.

## What each tick does

1. Dispatch the `supervisor-monitor` agent:
   ```
   Agent(subagent_type="supervisor-monitor", prompt="Collect stats and return JSON.")
   ```
   The agent returns structured JSON (see `.claude/agents/supervisor-monitor.md` for schema).

2. Parse the JSON and render the tree in this EXACT format:

```
Hub: ~/.claude-profile-1
└── Supervisor: ~/.claude-profile-2  (started 17:00, running 1h 15m)
    │
    ├── Researcher (main): ~/.claude-profile-6  (started 17:00, running 1h 15m)
    │   PID: 95600  running
    │   │
    │   └── Target: P@5=0.65  R@5=0.575
    │       Runs (last 3 of 5: 2 keep, 3 discard):
    │         #3  112ba8b  0.65  baseline
    │         #4  1cc81ef  0.35  discard  chunk overlap
    │         #5  eca93b6  0.60  discard  swap RRF
    │
    ├── Researcher Variant rv-001 (precision-safe): ~/.claude-profile-9  (started 17:05, running 1h 10m)
    │   PID: 96001  running
    │   │
    │   ├── Target Variant rv-001-tv-1: P@5=0.70  R@5=0.62
    │   └── Target Variant rv-001-tv-2: P@5=0.68  R@5=0.64
    │   Runs (last 3 of 8: 3 keep, 5 discard):
    │     #6  ccc9012  0.68  keep     BM25 stop words
    │     #7  ddd3456  0.62  discard  heading-aware
    │     #8  eee7890  0.64  keep     overlap 300
    │
    └── Researcher Variant rv-002 (evaluator-direct): ~/.claude-profile-8  (started 17:10, stopped after 25m)
        PID: 96002  stopped
        │
        └── Target Variant rv-002-tv-1: P@5=0.55  R@5=0.50
        Runs (2: 0 keep, 2 discard):
          #1  fff1234  0.65  baseline
          #2  ggg5678  0.55  discard  alternate eval
```

## Tree rendering rules

Given the JSON from the agent:

- **Hub line**: `Hub: {hub_profile}`
- **Supervisor line**: `└── Supervisor: {supervisor_profile}  (started HH:MM, running Xh Ym)` — compute duration from `now - supervisor_started_at`
- **Each researcher** in the `researchers` array becomes a child node:
  - First entry is always `Researcher (main)`
  - Others are `Researcher Variant {id} ({name})`
  - Use `├──` for non-last, `└──` for last
  - Show profile + timing: `(started HH:MM, running Xh Ym)` if running, `(started HH:MM, stopped after Xh Ym)` if stopped
  - Show `PID: {pid}  {running/stopped}`
  - **Target**: `MRR={mrr:.4f}  R@5={recall_at_5:.4f}` or `no report yet` if target is null
  - **Runs**: `Runs (last 3 of {total}: {kept} keep, {discarded} discard):` or `no runs yet` if runs is null
  - Each run: `#{n}  {commit}  {metric}  {status}  {description}`
  - **Target variants**: children of the researcher, show metrics for each

## Duration formatting

Compute `duration = now - started_at` from the JSON:
- Under 1 hour: `Xm` (e.g. `45m`)
- 1+ hours: `Xh Ym` (e.g. `1h 15m`)
- If `started_at` is null: show `(no start time)`

## For a one-shot snapshot

Use `/supervisor-list` instead, or dispatch the agent directly:
```
Agent(subagent_type="supervisor-monitor", prompt="Collect stats and return JSON.")
```
Then render the tree from the returned JSON.
