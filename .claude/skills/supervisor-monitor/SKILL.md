---
name: supervisor-monitor
description: "Live tree view of supervisor via cron — agent collects stats every 30s"
user_invocable: true
---

# /supervisor-monitor — Live Monitoring

Sets up a recurring cron that dispatches the `supervisor-monitor` agent every minute to collect stats and print the tree.

## Implementation

When the user invokes `/supervisor-monitor`:

1. Create a cron job:
   ```
   CronCreate(cron="*/1 * * * *", prompt="/supervisor-monitor-tick", recurring=true)
   ```

2. Run the first tick immediately by dispatching the agent:
   ```
   Agent(subagent_type="supervisor-monitor", prompt="Collect stats and print tree now.")
   ```

3. Report the cron job ID so the user can cancel with `CronDelete`.

## What each tick does

Each tick dispatches the `supervisor-monitor` agent. The agent:
- Runs all data collection commands (researcher status, metrics, runs, variants)
- Formats and prints the tree
- Returns ONLY the tree — no intermediate output reaches the user

## For a one-shot snapshot

Use `/supervisor-list` instead, or dispatch the agent directly:
```
Agent(subagent_type="supervisor-monitor", prompt="Collect stats and print tree now.")
```
