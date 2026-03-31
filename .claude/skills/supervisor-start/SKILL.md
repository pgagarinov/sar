---
name: supervisor-start
description: "Start the supervisor as a background process"
user_invocable: true
---

# /supervisor-start — Launch the Supervisor

Start the supervisor as a background process. Report PID and profile, then stop. Use `/supervisor-monitor` for continuous monitoring.

## Configuration

Read `.env` from the workspace root for `SUPERVISOR_REPO` and `CLAUDE_CONFIG_DIRS`.

## Steps

### 1. Pre-flight

```bash
source .env
cd $SUPERVISOR_REPO && CLAUDE_CONFIG_DIRS=$CLAUDE_CONFIG_DIRS pixi run -e dev researcher-status
```

If already running, report its state and stop here.

### 2. Start

```bash
cd $SUPERVISOR_REPO && CLAUDE_CONFIG_DIRS=$CLAUDE_CONFIG_DIRS pixi run -e dev researcher-start --no-clean
```

### 3. Confirm

Wait 5 seconds, then verify it started:

```bash
cd $SUPERVISOR_REPO && CLAUDE_CONFIG_DIRS=$CLAUDE_CONFIG_DIRS pixi run -e dev researcher-status
cd $SUPERVISOR_REPO && cat .supervisor/start-state.json 2>/dev/null | python3 -c "import sys,json,re; cmd=json.load(sys.stdin).get('command',''); m=re.search(r'CLAUDE_CONFIG_DIR=(\S+)',cmd); print(f'Profile: {m.group(1)}' if m else 'Profile: unknown')"
```

Report: `Started. PID=XXXXX profile=~/.claude-XX log=/tmp/cc-sar-supervisor.log`

## Important

- ALL commands go through `pixi run`
- ALWAYS read `.env` for CLAUDE_CONFIG_DIRS — never hardcode profile paths
- Do NOT poll — that is `/supervisor-monitor`'s job
- Do NOT ask "want me to start monitoring?" — just report the PID and stop

