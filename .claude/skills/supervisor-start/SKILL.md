---
name: supervisor-start
description: "Start the supervisor as a Claude session and poll its status"
user_invocable: true
---

# /supervisor-start — Launch and Poll the Supervisor

Launch the supervisor as a real Claude session via `claude -p /start` with the next profile in the rotation. Then poll its status.

## Configuration

Read `.env` from the workspace root for `SUPERVISOR_REPO` and `CLAUDE_CONFIG_DIRS`.

## Steps

### 1. Pre-flight

```bash
cd <SUPERVISOR_REPO> && pixi run researcher-status
```

If already running, report its state and stop here.

### 2. Compute next profile

```bash
PROFILES=$(grep "^CLAUDE_CONFIG_DIRS=" .env | cut -d= -f2-)
CURRENT=${CLAUDE_CONFIG_DIR}
NEXT_PROFILE=$(python3 -c "
import os
dirs = '${PROFILES}'.split(':')
current = '${CURRENT}'
idx = next((i for i,d in enumerate(dirs) if os.path.expanduser(d) == os.path.expanduser(current)), 0)
print(os.path.expanduser(dirs[(idx+1) % len(dirs)]))
")
echo "Supervisor profile: $NEXT_PROFILE"
```

### 3. Launch supervisor as a real Claude session

```bash
cd <SUPERVISOR_REPO> && CLAUDE_CONFIG_DIR=$NEXT_PROFILE claude -p /start \
  --dangerously-skip-permissions \
  --output-format stream-json \
  --verbose \
  > /tmp/cc-sar-supervisor.log 2>&1 &
echo $! > /tmp/sar-supervisor.pid
```

This creates a real Claude session that reads the supervisor's CLAUDE.md, gets stop hook triggers, makes autonomous decisions, and edits researcher prompts.

### 4. Poll

Every 30 seconds:

```bash
cd <SUPERVISOR_REPO> && pixi run researcher-status
```

Report: `[HH:MM:SS] supervisor-profile=$NEXT_PROFILE researcher: running=True/False pid=XXXXX`

**Continue polling until the supervisor process exits or the user interrupts.** Do not ask whether to continue.

### 5. When supervisor exits

Report final state. The user decides whether to restart.

## Important

- The supervisor is a REAL Claude session, not just a Python harness
- It reads CLAUDE.md, gets stop hooks, makes autonomous decisions
- `pixi run researcher-start` only launches the Python harness — this skill launches the full AI supervisor
- ALL polling goes through `pixi run` commands
