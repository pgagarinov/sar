---
name: deploy
description: "Clone and configure all 4 SAR repos from GitHub"
user_invocable: true
---

# /deploy — Deploy All SAR Repos

Clone the supervisor, research loop, RAG target, and harness-core as sibling directories.

## Configuration

Read `.env` from the workspace root. Keys:
- `GITHUB_OWNER` — GitHub org/user
- `SUPERVISOR_REPO` / `SUPERVISOR_REPO_NAME`
- `RESEARCH_LOOP_REPO` / `RESEARCH_LOOP_REPO_NAME`
- `RAG_TARGET_REPO` / `RAG_TARGET_REPO_NAME`
- `HARNESS_CORE_REPO` / `HARNESS_CORE_REPO_NAME`

## Steps

1. **Read `.env`** and parse all variables.

2. **Check for existing repos**. If any configured paths exist, STOP and tell the user to run `/delete` first.

3. **Clone all 4 repos**:
   ```bash
   gh repo clone ${GITHUB_OWNER}/${HARNESS_CORE_REPO_NAME} ${HARNESS_CORE_REPO}
   gh repo clone ${GITHUB_OWNER}/${SUPERVISOR_REPO_NAME} ${SUPERVISOR_REPO}
   gh repo clone ${GITHUB_OWNER}/${RESEARCH_LOOP_REPO_NAME} ${RESEARCH_LOOP_REPO}
   gh repo clone ${GITHUB_OWNER}/${RAG_TARGET_REPO_NAME} ${RAG_TARGET_REPO}
   ```

4. **Install dependencies** (harness-core first since others depend on it):
   ```bash
   cd ${HARNESS_CORE_REPO} && pixi install
   cd ${SUPERVISOR_REPO} && pixi install
   cd ${RESEARCH_LOOP_REPO} && pixi install
   cd ${RAG_TARGET_REPO} && pixi install
   ```

5. **Verify cross-repo paths**:
   - `${SUPERVISOR_REPO}/harness.toml` `supervised.repo` should resolve to `${RESEARCH_LOOP_REPO}`
   - `${RESEARCH_LOOP_REPO}/.claude/agents/evaluator.md` should reference a path resolving to `${RAG_TARGET_REPO}`

6. **Report** which repos were cloned, installed, and any issues.
