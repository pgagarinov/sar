---
name: supervisor-stop
description: "Stop the running supervisor and all researcher variants"
user_invocable: true
---

# /supervisor-stop — Stop the Supervisor

Stop the supervisor process, any running researcher variants, and the monitoring cron. Capture final state before stopping.

## Configuration

Read `.env` from the workspace root for `SUPERVISOR_REPO` and `CLAUDE_CONFIG_DIRS`.

## Steps

### 1. Cancel monitoring cron

```
CronList → find any supervisor-monitor cron jobs → CronDelete each one
```

### 2. Check current state

```bash
source .env
cd $SUPERVISOR_REPO && CLAUDE_CONFIG_DIRS=$CLAUDE_CONFIG_DIRS pixi run -e dev researcher-status
```

If not running, report `not-running` and stop here.

### 3. List running researcher variants

```bash
cd $SUPERVISOR_REPO && CLAUDE_CONFIG_DIRS=$CLAUDE_CONFIG_DIRS pixi run -e dev researcher-variant list --json
```

If any variants are running, stop each one:

```bash
cd $SUPERVISOR_REPO && CLAUDE_CONFIG_DIRS=$CLAUDE_CONFIG_DIRS pixi run -e dev researcher-variant stop --id <variant_id>
```

### 4. Capture final snapshot

```bash
cd $SUPERVISOR_REPO && CLAUDE_CONFIG_DIRS=$CLAUDE_CONFIG_DIRS pixi run -e dev researcher-snapshot
```

### 5. Stop the supervisor

```bash
cd $SUPERVISOR_REPO && CLAUDE_CONFIG_DIRS=$CLAUDE_CONFIG_DIRS pixi run -e dev researcher-stop
```

### 6. Verify stopped

```bash
cd $SUPERVISOR_REPO && CLAUDE_CONFIG_DIRS=$CLAUDE_CONFIG_DIRS pixi run -e dev researcher-status
```

Report: `stopped` with final PID and profile.

## Important

- ALWAYS cancel the monitoring cron first (step 1)
- ALL commands go through `pixi run` — never run `python -m` directly
- ALWAYS read `.env` for CLAUDE_CONFIG_DIRS — never hardcode profile paths
- Stop researcher variants BEFORE stopping the supervisor to avoid orphaned processes
- Capture a snapshot before stopping so the state is preserved for later analysis

