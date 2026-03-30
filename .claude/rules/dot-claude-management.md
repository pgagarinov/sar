# .claude/ File Management

**NEVER use mkdir, Write, Edit, or Bash to create or modify files under `.claude/` in any repo.**

Instead, use the `dot-claude-*` pixi tasks:

## For this repo (self)
- `pixi run dot-claude-list` — list all .claude/ assets
- `pixi run dot-claude-read <path>` — read an asset
- `pixi run dot-claude-edit <path> --sed 's/old/new/g'` — targeted find/replace (logged, diffed, auto-committed)
- `echo "content" | pixi run dot-claude-edit <path>` — full content replacement (logged, diffed, auto-committed)
- `echo "content" | pixi run dot-claude-diff <path>` — preview diff without writing

## For child repos
- `pixi run supervisor-dot-claude-*` — manage supervisor's .claude/
- `pixi run researcher-dot-claude-*` — manage researcher's .claude/

## Prefer --sed for targeted edits
When changing specific strings in an asset, use `--sed` instead of piping the entire file:
```bash
pixi run researcher-dot-claude-edit skill --sed 's|old-pattern|new-pattern|g'
```
This is more precise than reading the file, transforming with external `sed`, and piping back — which loses the sed pattern in the edit log.

## Creating new skills
To create a new skill, pipe its content to `dot-claude-edit` with the relative path:
```bash
echo "skill content" | pixi run dot-claude-edit skills/my-skill/SKILL.md
```

## Why
Every .claude/ change must be logged, diffed, and auto-committed via `harness_core.prompt_editor`. Direct file operations (including sed, awk, and other shell tools) bypass this tracking.
