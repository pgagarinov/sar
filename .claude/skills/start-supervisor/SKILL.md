---
name: start-supervisor
description: "Start the SAR supervisor via claude -p and monitor it"
user_invocable: true
---

# /start-supervisor — Launch the SAR Supervisor

Start the supervisor as a real Claude session via `claude -p /start`, exactly as a user would. Then monitor the supervisor process.

**Separation of concerns:** The integration hub monitors the **supervisor**. The supervisor monitors the **researcher**. The researcher monitors the **target**. Each layer only interacts with its immediate child.

## Configuration

Read `.env` from the workspace root for repo paths:
- `SUPERVISOR_REPO`

## Steps

### 1. Pre-flight checks

```bash
# Check no supervisor is already running
cd <SUPERVISOR_REPO> && pixi run status
```

If a supervisor is already running, report its state and ask whether to stop it first.

### 2. Launch the supervisor via claude -p

```bash
cd <SUPERVISOR_REPO> && claude -p /start \
  --dangerously-skip-permissions \
  --output-format stream-json \
  --verbose \
  > /tmp/cc-sar-supervisor-observer.log 2>&1 &
```

Record the PID:
```bash
echo $! > /tmp/sar-observer.pid
```

### 3. Monitor the supervisor

Poll every 30 seconds. On each poll:

```bash
# Is the supervisor process alive?
ps -p $(cat /tmp/sar-observer.pid) -o stat= 2>/dev/null

# Check supervisor status (is it running the researcher?)
cd <SUPERVISOR_REPO> && pixi run status

# Check log growth
wc -c /tmp/cc-sar-supervisor-observer.log
```

Report a status line each poll:
```
[HH:MM:SS] supervisor=running log=XXXkb
```

### 4. Detect supervisor-level problems

Watch for:
- **Supervisor process died**: PID no longer running. Read tail of `/tmp/cc-sar-supervisor-observer.log` for errors.
- **Supervisor not starting researcher**: `pixi run status` shows not-running after >2 minutes. Check supervisor log.
- **Supervisor log not growing**: may be stalled or rate-limited.

When a problem is found:
1. Read the supervisor log to understand the root cause
2. If it's a supervisor-level issue (hook failure, config error, etc.), fix it
3. Re-launch if needed

### 5. What this skill does NOT do

- **Never read researcher logs or state** — that's the supervisor's job
- **Never read target code or results** — that's the researcher's job
- **Never diagnose researcher-level or target-level issues** — report the supervisor status only
- Only interact with the supervisor process and its logs
