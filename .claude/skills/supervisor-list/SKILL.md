---
name: supervisor-list
description: "Dashboard: supervisor status, experiments, and metric history"
user_invocable: true
---

# /supervisor-list — Supervisor Dashboard

One-shot snapshot of the supervisor and everything it manages.

## Configuration

Read `.env` from the workspace root for `SUPERVISOR_REPO`.

## Steps

Run these commands and present a combined summary:

### 1. Active profiles (supervisor → researcher → target all use the same profile)
```bash
cd <SUPERVISOR_REPO> && python3 -c "
import json, re
try:
    d = json.load(open('.supervisor/start-state.json'))
    cmd = d.get('command', '')
    m = re.search(r'CLAUDE_CONFIG_DIR=(\S+)', cmd)
    profile = m.group(1) if m else 'unknown'
    print(f'Profile: {profile} (supervisor + researcher + target)')
except FileNotFoundError:
    print('Profile: not running')
" 2>/dev/null
```

### 2. Supervisor status
```bash
cd <SUPERVISOR_REPO> && pixi run researcher-status --json
```

### 3. Parallel experiments
```bash
cd <SUPERVISOR_REPO> && pixi run researcher-experiment list --json
```

### 4. Recent metric history
```bash
cd <SUPERVISOR_REPO> && pixi run researcher-history --limit 5 --json
```

## Output

Present a structured dashboard:
```
=== Supervisor ===
Profile: ~/.claude-XX
Status:  running/stopped  PID: XXXXX
Prompt:  /start

=== Experiments ===
(list or "none")

=== Metric History (last 5) ===
timestamp  metric=X.XX  path=...
```

## Important

- ALL commands go through `pixi run` — never run `python -m` directly
- This is a one-shot snapshot, not continuous monitoring (use `/supervisor-monitor` for that)
