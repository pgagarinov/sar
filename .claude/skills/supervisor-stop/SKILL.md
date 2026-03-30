---
name: supervisor-stop
description: "Stop the running supervisor and all researcher variants"
user_invocable: true
---

# /supervisor-stop — Stop the Supervisor

Stop the supervisor process and any running researcher variants. Capture final state before stopping.

## Configuration

Read `.env` from the workspace root for `SUPERVISOR_REPO`.

## Steps

### 1. Check current state

```bash
cd <SUPERVISOR_REPO> && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-status
```

If not running, report `not-running` and stop here.

### 2. List running researcher variants

```bash
cd <SUPERVISOR_REPO> && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-variant list --json
```

If any variants are running, stop each one:

```bash
cd <SUPERVISOR_REPO> && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-variant stop --id <variant_id>
```

### 3. Capture final snapshot

```bash
cd <SUPERVISOR_REPO> && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-snapshot
```

### 4. Stop the supervisor

```bash
cd <SUPERVISOR_REPO> && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-stop
```

### 5. Verify stopped

```bash
cd <SUPERVISOR_REPO> && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-status
```

Report: `stopped` with final PID and profile.

## Important

- ALL commands go through `pixi run` — never run `python -m` directly
- CLAUDE_CONFIG_DIRS must be set for all pixi commands
- Stop researcher variants BEFORE stopping the supervisor to avoid orphaned processes
- Capture a snapshot before stopping so the state is preserved for later analysis
