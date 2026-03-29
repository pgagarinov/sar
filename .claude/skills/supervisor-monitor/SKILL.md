---
name: supervisor-monitor
description: "Live structured analysis of the researcher via the supervisor"
user_invocable: true
---

# /supervisor-monitor — Live Analysis Stream

Real-time structured analysis of the researcher's behavior, including Haiku-based anti-pattern detection. Uses the supervisor's CLI commands which read the researcher's stream-json log.

## Configuration

Read `.env` from the workspace root for `SUPERVISOR_REPO`.

## Steps

### 1. Show active profiles (all layers use the same CLAUDE_CONFIG_DIR)

```bash
cd <SUPERVISOR_REPO> && python3 -c "
import json, re
d = json.load(open('.supervisor/start-state.json'))
cmd = d.get('command', '')
m = re.search(r'CLAUDE_CONFIG_DIR=(\S+)', cmd)
profile = m.group(1) if m else 'unknown'
print(f'Supervisor profile: {profile}')
print(f'Researcher profile: {profile} (inherited)')
print(f'Target profile:     {profile} (inherited)')
"
```

### 2. One-shot snapshot first

```bash
cd <SUPERVISOR_REPO> && pixi run researcher-loop-once
```

This runs one analysis cycle: parses the log, shows events/dispatches/latest text/reports/repo status, takes a snapshot. Uses the pixi environment so all dependencies (harness_core) are available.

### 3. Continuous polling

Poll every 30 seconds using `pixi run researcher-loop-once`:

```bash
cd <SUPERVISOR_REPO> && pixi run researcher-loop-once
```

Report a structured summary each cycle:
```
[HH:MM:SS] profile=~/.claude-XX events=N dispatches=... metric=X.XX latest=...
```

**Continue polling until the supervisor process exits or the user interrupts.** Do not ask whether to continue — keep going.

### 4. When supervisor exits

Report the final state:
```bash
cd <SUPERVISOR_REPO> && pixi run researcher-status
cd <SUPERVISOR_REPO> && pixi run researcher-history --limit 5
```

## Haiku Integration

The supervisor's stop hook runs Haiku every ~120s to detect anti-patterns in the researcher's log:
- Researcher doing work instead of dispatching agents
- Using TodoWrite
- Wrong subagent type for the current phase
- Rephrasing instead of forwarding verbatim
- Missing expected dispatches

Haiku results appear in the `loop-once` output when the stop hook has fired.

## Important

- ALL commands go through `pixi run` — never run `python -m` directly (dependencies won't resolve)
- Use `researcher-loop-once` for each poll cycle, NOT `researcher-monitor` (which has `--follow` baked in and blocks indefinitely)
- Do NOT ask "want me to keep polling?" — continue until stopped
