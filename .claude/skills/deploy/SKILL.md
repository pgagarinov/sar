---
name: deploy
description: "Clone and configure all 3 repos from GitHub"
user_invocable: true
---

# /deploy — Deploy All 3 Repos

Deploy the supervisor harness, research loop, and RAG search system as sibling directories.

## Configuration

Read `.env` from the workspace root for repo locations and GitHub details:
- `SUPERVISOR_REPO` — path for the supervisor harness
- `RESEARCH_LOOP_REPO` — path for the research loop
- `RAG_SYSTEM_REPO` — path for the RAG search system
- `GITHUB_OWNER` — GitHub org/user
- `SUPERVISOR_REPO_NAME`, `RESEARCH_LOOP_REPO_NAME`, `RAG_SYSTEM_REPO_NAME` — repo names

## Steps

1. **Read `.env`** from the workspace root. Parse all variables.

2. **Check for existing repos** at the configured paths. If any exist, STOP and tell the user to run `/delete` first. Do NOT delete them yourself.

3. **Clone all 3 repos** from GitHub:
   ```bash
   gh repo clone ${GITHUB_OWNER}/${SUPERVISOR_REPO_NAME} ${SUPERVISOR_REPO}
   gh repo clone ${GITHUB_OWNER}/${RESEARCH_LOOP_REPO_NAME} ${RESEARCH_LOOP_REPO}
   gh repo clone ${GITHUB_OWNER}/${RAG_SYSTEM_REPO_NAME} ${RAG_SYSTEM_REPO}
   ```

4. **Configure cross-repo references** in the supervisor's `harness.toml`:
   - Set `supervised.repo` to the relative path from supervisor to research loop
   - The research loop's agents already reference `../rag-search-system` — verify this matches `RAG_SYSTEM_REPO` relative to `RESEARCH_LOOP_REPO`

5. **Install dependencies** in each repo:
   ```bash
   cd ${SUPERVISOR_REPO} && pixi install
   cd ${RESEARCH_LOOP_REPO} && pixi install
   cd ${RAG_SYSTEM_REPO} && pixi install
   ```

6. **Report** which repos were cloned and installed, and any issues.

## Success Criteria

- All 3 repos cloned to configured paths
- `pixi install` succeeds in each
- Cross-repo path references are correct
