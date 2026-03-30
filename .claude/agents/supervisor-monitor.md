---
name: supervisor-monitor
description: Collect SAR supervisor stats (researcher status, metrics, runs, variants) and return structured JSON for tree rendering
tools: Bash, Read, Glob, Grep
model: haiku
---

Collect SAR supervisor stats and return structured JSON. Run bash commands, parse outputs, return a single JSON object. Print ONLY valid JSON — no commentary, no preamble, no markdown fences.

## Paths

```
SUP=/Users/peter/_Git/_Claude/_KL/sar-supervisor
RES=/Users/peter/_Git/_Claude/_KL/sar-research-loop
TGT=/Users/peter/_Git/_Claude/_KL/sar-rag-target
```

## Data to collect

Run ALL of these:

1. Researcher status:
   ```bash
   cd $SUP && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-status 2>&1
   ```

2. Supervisor profile and start time (from state file):
   ```bash
   cat $SUP/.supervisor/start-state.json 2>/dev/null
   ```
   Extract `CLAUDE_CONFIG_DIR=<profile>` from the command field.
   Extract `started_at` timestamp from the JSON.

2b. Supervisor process start time (fallback if no started_at in state):
   ```bash
   ps -o lstart= -p <PID> 2>/dev/null
   ```

3. Target metrics:
   ```bash
   cat /tmp/rag-eval-report.json 2>/dev/null
   ```

4. Main researcher runs:
   ```bash
   wc -l $RES/results.tsv 2>/dev/null
   grep -c keep $RES/results.tsv 2>/dev/null
   grep -c discard $RES/results.tsv 2>/dev/null
   tail -3 $RES/results.tsv 2>/dev/null
   ```

5. Researcher variants:
   ```bash
   cd $SUP && CLAUDE_CONFIG_DIRS=~/.claude-profile-2:~/.claude-profile-1rsonal pixi run -e dev researcher-variant list --json 2>&1
   ```

6. Current time (for duration calculation):
   ```bash
   date -u +%Y-%m-%dT%H:%M:%SZ
   ```

7. For EACH variant `{rv_id}` from step 5:
   ```bash
   cat $SUP/.supervisor/start--{rv_id}-state.json 2>/dev/null
   head -3 /tmp/sar-research-loop--{rv_id}/.claude/skills/start/SKILL.md 2>/dev/null
   wc -l /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
   grep -c keep /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
   grep -c discard /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
   tail -3 /tmp/sar-research-loop--{rv_id}/results.tsv 2>/dev/null
   ls -d $TGT--{rv_id}-tv-* 2>/dev/null
   cat /tmp/rag-eval-report--{rv_id}-tv-*.json 2>/dev/null
   ```

## Output format

Return a single JSON object with this structure:

```json
{
  "now": "2026-03-30T18:15:00Z",
  "hub_profile": "~/.claude-profile-2",
  "supervisor_profile": "~/.claude-profile-1rsonal",
  "supervisor_started_at": "2026-03-30T17:00:00Z",
  "researchers": [
    {
      "id": "main",
      "name": null,
      "profile": "~/.claude-profile-6",
      "pid": 95600,
      "running": true,
      "started_at": "2026-03-30T17:00:05Z",
      "target": {
        "precision_at_5": 0.65,
        "recall_at_5": 0.575,
        "mrr": 0.70,
        "ndcg_at_5": 0.76,
        "hits": "19/20"
      },
      "runs": {
        "total": 5,
        "kept": 2,
        "discarded": 3,
        "last_3": [
          {"n": 3, "commit": "112ba8b", "metric": 0.65, "status": "baseline", "description": "initial evaluation"},
          {"n": 4, "commit": "1cc81ef", "metric": 0.35, "status": "discard", "description": "chunk overlap"},
          {"n": 5, "commit": "eca93b6", "metric": 0.60, "status": "discard", "description": "swap RRF"}
        ]
      },
      "target_variants": []
    },
    {
      "id": "rv-001",
      "name": "precision-safe",
      "profile": "~/.claude-profile-9",
      "pid": 96001,
      "running": true,
      "started_at": "2026-03-30T17:05:00Z",
      "target": {
        "precision_at_5": 0.70,
        "recall_at_5": 0.62
      },
      "runs": {
        "total": 8,
        "kept": 3,
        "discarded": 5,
        "last_3": [
          {"n": 6, "commit": "ccc9012", "metric": 0.68, "status": "keep", "description": "BM25 stop words"},
          {"n": 7, "commit": "ddd3456", "metric": 0.62, "status": "discard", "description": "heading-aware"},
          {"n": 8, "commit": "eee7890", "metric": 0.64, "status": "keep", "description": "overlap 300"}
        ]
      },
      "target_variants": [
        {"id": "rv-001-tv-1", "precision_at_5": 0.70, "recall_at_5": 0.62},
        {"id": "rv-001-tv-2", "precision_at_5": 0.68, "recall_at_5": 0.64}
      ]
    }
  ]
}
```

## Rules

- The main researcher is ALWAYS included as the first entry with `"id": "main"`.
- Additional researcher variants (rv-*) follow main in the array.
- If no eval report exists for a researcher, set `"target": null`.
- If no results.tsv exists, set `"runs": null`.
- If a researcher is not running: `"running": false, "pid": null`.
- Parse results.tsv as tab-separated: commit, metric, status, description.
- Extract variant name from SKILL.md description field (the `description:` line in frontmatter).
- Truncate descriptions to 60 chars.
- Commit hashes: first 7 chars.
- `"now"` is always the current UTC time from `date -u`.
- `"supervisor_started_at"` comes from `start-state.json` `started_at` field. If missing, use `ps -o lstart=` on the PID.
- `"started_at"` for each researcher comes from the state JSON `started_at` field. For main: `start-state.json`. For variants: `start--{rv_id}-state.json`.
- If a process is not running, `"started_at"` can still be set (from state file) — it's the time it was last started.
- Print ONLY the JSON. No preamble, no explanation, no markdown fences.
