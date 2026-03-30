# .claude/ File Management

**NEVER use mkdir, Write, Edit, or Bash to create or modify files under `.claude/` in any repo.**

Instead, use the `dot-claude-*` pixi tasks:

## For this repo (self)
- `pixi run dot-claude-list` — list all .claude/ assets
- `pixi run dot-claude-read <path>` — read an asset
- `pixi run dot-claude-edit <path> --sed 's/old/new/g'` — targeted find/replace (logged, diffed, auto-committed)
- `echo "content" | pixi run dot-claude-edit <path>` — full content replacement (logged, diffed, auto-committed)
- `echo "content" | pixi run dot-claude-diff <path>` — preview diff without writing
- `pixi run dot-claude-delete <path>` — delete a file under .claude/ (logged, auto-committed)

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

## Agent files MUST have YAML frontmatter

When creating or editing agent files (`.claude/agents/*.md`) in ANY repo, ALWAYS include YAML frontmatter:

```yaml
---
name: agent-name
description: "What this agent does — used by Claude Code for agent discovery"
tools: Bash, Read, Edit, Grep
model: haiku
---
```

Required fields: `name`, `description`. Optional: `tools`, `model`, `maxTurns`. Without frontmatter, the agent will not be discoverable by Claude Code.

## What about sed in skills and agents or other files in .claude?

The `--sed` flag works for ALL `.claude/` files — skills, agents, rules. Use it for targeted edits in any of them:
```bash
pixi run dot-claude-edit agents/my-agent.md --sed 's|old-pattern|new-pattern|g'
pixi run supervisor-dot-claude-edit rules/some-rule.md --sed 's|old|new|g'
```

## Why
Every .claude/ change must be logged, diffed, and auto-committed via `harness_core.prompt_editor`. Direct file operations (including sed, awk, and other shell tools) bypass this tracking.
