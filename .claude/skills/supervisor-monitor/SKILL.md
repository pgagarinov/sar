---
name: supervisor-monitor
description: "Live structured analysis of researcher variants via the supervisor"
user_invocable: true
---

# /supervisor-monitor — Live Analysis Stream

Real-time structured analysis of researcher variant behavior, including Haiku-based anti-pattern detection.

## Configuration

Read `.env` from the workspace root for `SUPERVISOR_REPO`.

## Steps

### 1. Show profile rotation tree

For the main researcher:
```bash
cd <SUPERVISOR_REPO> && python3 -c "
import json, re, os
state_file = '.supervisor/start-state.json'
if os.path.exists(state_file):
    d = json.load(open(state_file))
    cmd = d.get('command', '')
    m = re.search(r'CLAUDE_CONFIG_DIR=(\S+)', cmd)
    researcher_profile = m.group(1) if m else 'unknown'
    m2 = re.search(r'TARGET_CLAUDE_CONFIG_DIR=(\S+)', cmd)
    target_profile = m2.group(1) if m2 else 'unknown'
    print(f'Hub: {os.environ.get(\"CLAUDE_CONFIG_DIR\", \"unknown\")}')
    print(f'  Researcher (main): {researcher_profile}')
    print(f'    Target: {target_profile}')
else:
    print('Not running')
"
```

For each researcher variant, read its state file from `.supervisor/start--{rv_id}-state.json` to show its profile.

### 2. One-shot snapshot

```bash
cd <SUPERVISOR_REPO> && pixi run researcher-loop-once
```

### 3. Researcher variant status (if any running)

```bash
cd <SUPERVISOR_REPO> && pixi run researcher-variant list
```

### 4. Continuous polling

Poll every 30 seconds using `pixi run researcher-loop-once`. Report a structured summary each cycle. **Continue polling until stopped. Do not ask whether to continue.**

### 5. When supervisor exits

```bash
cd <SUPERVISOR_REPO> && pixi run researcher-status
cd <SUPERVISOR_REPO> && pixi run researcher-history --limit 5
```

## Haiku Integration

The supervisor's stop hook runs Haiku every ~120s to detect anti-patterns in the researcher's log. Results appear in the `researcher-loop-once` output.

## Important

- ALL commands go through `pixi run` — never run `python -m` directly
- Use `researcher-loop-once` for each poll cycle, NOT `researcher-monitor` (blocks indefinitely)
- Do NOT ask "want me to keep polling?" — continue until stopped
