---
name: supervisor-list
description: "Dashboard: supervisor status, researcher variants, and metric history"
user_invocable: true
---

# /supervisor-list — Supervisor Dashboard

One-shot snapshot of the supervisor and everything it manages.

## Configuration

Read `.env` from the workspace root for `SUPERVISOR_REPO`.

## Steps

### 1. Profile rotation tree
```bash
cd <SUPERVISOR_REPO> && python3 -c "
import json, re, os, glob
hub_profile = os.environ.get('CLAUDE_CONFIG_DIR', 'unknown')
print(f'Hub: {hub_profile}')
state = '.supervisor/start-state.json'
if os.path.exists(state):
    d = json.load(open(state))
    cmd = d.get('command', '')
    m = re.search(r'CLAUDE_CONFIG_DIR=(\S+)', cmd)
    print(f'  Researcher (main): {m.group(1) if m else \"unknown\"}')
for sf in sorted(glob.glob('.supervisor/start--*-state.json')):
    rv_id = sf.split('start--')[1].replace('-state.json', '')
    d = json.load(open(sf))
    cmd = d.get('command', '')
    m = re.search(r'CLAUDE_CONFIG_DIR=(\S+)', cmd)
    print(f'  Researcher Variant {rv_id}: {m.group(1) if m else \"unknown\"}')
"
```

### 2. Supervisor status
```bash
cd <SUPERVISOR_REPO> && pixi run researcher-status --json
```

### 3. Researcher variants
```bash
cd <SUPERVISOR_REPO> && pixi run researcher-variant list --json
```

### 4. Recent metric history
```bash
cd <SUPERVISOR_REPO> && pixi run researcher-history --limit 5 --json
```

## Output

```
=== Profiles ===
Hub: ~\/.claude-<profile>
  Researcher (main): ~\/.claude-<profile>
  Researcher Variant rv-001: ~\/.claude-<profile>
  Researcher Variant rv-002: ~\/.claude-<profile>

=== Supervisor ===
Status: running  PID: XXXXX

=== Researcher Variants ===
(list with profile per researcher variant, or "none")

=== Metric History (last 5) ===
timestamp  metric=X.XX
```

## Important

- ALL commands go through `pixi run`
- This is a one-shot snapshot (use `/supervisor-monitor` for continuous polling)
