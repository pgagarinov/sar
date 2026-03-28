---
name: deploy
description: "Clone and configure all 4 SAR repos from GitHub"
user_invocable: true
---

# /deploy — Deploy All SAR Repos

Clone the supervisor, research loop, RAG target, and harness-core as sibling directories.

## Steps

### 1. Ensure .env exists

If `.env` does not exist, create it from `.env.example`:
```bash
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi
```

Then auto-detect Claude config directories and update `CLAUDE_CONFIG_DIRS`:
```bash
DETECTED=$(ls -d ~/.claude-* 2>/dev/null | sort | paste -sd ':' -)
if grep -q '^CLAUDE_CONFIG_DIRS=' .env; then
  sed -i '' "s|^CLAUDE_CONFIG_DIRS=.*|CLAUDE_CONFIG_DIRS=${DETECTED}|" .env
else
  echo "CLAUDE_CONFIG_DIRS=${DETECTED}" >> .env
fi
```

### 2. Read .env

Parse all variables from `.env`:
- `GITHUB_OWNER` — GitHub org/user
- `SUPERVISOR_REPO` / `SUPERVISOR_REPO_NAME`
- `RESEARCH_LOOP_REPO` / `RESEARCH_LOOP_REPO_NAME`
- `RAG_TARGET_REPO` / `RAG_TARGET_REPO_NAME`
- `HARNESS_CORE_REPO` / `HARNESS_CORE_REPO_NAME`

If any required variable is missing, STOP and report which variable is missing and that it should be set in `.env`.

### 3. Check for existing repos

If any configured paths already exist, STOP and tell the user to run `/delete` first.

### 4. Clone all 4 repos

```bash
gh repo clone ${GITHUB_OWNER}/${HARNESS_CORE_REPO_NAME} ${HARNESS_CORE_REPO}
gh repo clone ${GITHUB_OWNER}/${SUPERVISOR_REPO_NAME} ${SUPERVISOR_REPO}
gh repo clone ${GITHUB_OWNER}/${RESEARCH_LOOP_REPO_NAME} ${RESEARCH_LOOP_REPO}
gh repo clone ${GITHUB_OWNER}/${RAG_TARGET_REPO_NAME} ${RAG_TARGET_REPO}
```

### 5. Install dependencies

Harness-core first since others depend on it:
```bash
cd ${HARNESS_CORE_REPO} && pixi install
cd ${SUPERVISOR_REPO} && pixi install
cd ${RESEARCH_LOOP_REPO} && pixi install
cd ${RAG_TARGET_REPO} && pixi install
```

### 6. Verify cross-repo paths

- `${SUPERVISOR_REPO}/harness.toml` `supervised.repo` should resolve to `${RESEARCH_LOOP_REPO}`
- `${RESEARCH_LOOP_REPO}/.claude/agents/evaluator.md` should reference a path resolving to `${RAG_TARGET_REPO}`

### 7. Report

Which repos were cloned, installed, and any issues found.
