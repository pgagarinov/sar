---
name: supervisor-start
description: "Start the supervisor and poll its status"
user_invocable: true
---

# /supervisor-start — Launch and Poll the Supervisor

Start the supervisor using the same pattern the supervisor uses to manage the researcher: spawn as a background process via the harness, then poll.

## Configuration

Read `.env` from the workspace root for `SUPERVISOR_REPO`.

## Steps

### 1. Pre-flight

```bash
cd <SUPERVISOR_REPO> && pixi run researcher-status
```

If already running, report its state and stop here.

### 2. Start

```bash
cd <SUPERVISOR_REPO> && pixi run researcher-start --no-clean
```

Returns PID immediately. Report the PID and log path.

### 3. Poll

Every 30 seconds, run `pixi run researcher-status` and show the active profile:

```bash
cd <SUPERVISOR_REPO> && pixi run researcher-status
cd <SUPERVISOR_REPO> && cat .supervisor/start-state.json 2>/dev/null | python3 -c "import sys,json,re; cmd=json.load(sys.stdin).get('command',''); m=re.search(r'CLAUDE_CONFIG_DIR=(\S+)',cmd); print(f'Profile: {m.group(1)}' if m else 'Profile: unknown')"
```

Report: `[HH:MM:SS] profile=~/.claude-XX supervisor: running=True pid=XXXXX`

**Continue polling until the supervisor process exits or the user interrupts.** Do not ask whether to continue.

### 4. When supervisor exits

Report final state. The user decides whether to restart.

## Important

- ALL commands go through `pixi run` — never run `python -m` directly
- Do NOT ask "want me to keep polling?" — continue until stopped
