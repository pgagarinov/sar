---
name: supervisor-stop
description: "Stop the running supervisor"
user_invocable: true
---

# /supervisor-stop — Stop the Supervisor

## Configuration

Read `.env` from the workspace root for `SUPERVISOR_REPO`.

## Steps

```bash
cd <SUPERVISOR_REPO> && pixi run researcher-stop
```

Report: `stopped` or `not-running`.
