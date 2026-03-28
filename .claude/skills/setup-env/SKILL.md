---
name: setup-env
description: "Create .env from .env.example, auto-detect ~/.claude-* config directories across all repos"
user_invocable: true
---

# /setup-env — Initialize Environment Configuration

Create `.env` files from `.env.example` templates and auto-detect Claude config directories across all SAR repos.

## Steps

### 1. Ensure .env exists in the integration hub

```bash
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
else
  echo ".env already exists"
fi
```

### 2. Scan for Claude config directories

```bash
DETECTED=$(ls -d ~/.claude-* 2>/dev/null | sort | paste -sd ':' -)
echo "Detected: $DETECTED"
```

### 3. Update CLAUDE_CONFIG_DIRS in integration hub .env

```bash
if grep -q '^CLAUDE_CONFIG_DIRS=' .env; then
  sed -i '' "s|^CLAUDE_CONFIG_DIRS=.*|CLAUDE_CONFIG_DIRS=${DETECTED}|" .env
else
  echo "CLAUDE_CONFIG_DIRS=${DETECTED}" >> .env
fi
```

### 4. Propagate to sibling repos

Read `SUPERVISOR_REPO`, `RESEARCH_LOOP_REPO`, `RAG_TARGET_REPO` from `.env`. For each repo that has a `.env.example`:

```bash
for REPO_VAR in SUPERVISOR_REPO RESEARCH_LOOP_REPO; do
  REPO_PATH=$(grep "^${REPO_VAR}=" .env | cut -d= -f2)
  if [ -d "$REPO_PATH" ] && [ -f "$REPO_PATH/.env.example" ]; then
    if [ ! -f "$REPO_PATH/.env" ]; then
      cp "$REPO_PATH/.env.example" "$REPO_PATH/.env"
      echo "Created $REPO_PATH/.env from .env.example"
    fi
    if grep -q '^CLAUDE_CONFIG_DIRS=' "$REPO_PATH/.env"; then
      sed -i '' "s|^CLAUDE_CONFIG_DIRS=.*|CLAUDE_CONFIG_DIRS=${DETECTED}|" "$REPO_PATH/.env"
    else
      echo "CLAUDE_CONFIG_DIRS=${DETECTED}" >> "$REPO_PATH/.env"
    fi
    echo "Updated $REPO_PATH/.env"
  fi
done
```

### 5. Report

```bash
echo "=== CLAUDE_CONFIG_DIRS ==="
echo "$DETECTED"
echo ""
echo "Updated .env files in:"
echo "  - . (integration hub)"
for REPO_VAR in SUPERVISOR_REPO RESEARCH_LOOP_REPO; do
  REPO_PATH=$(grep "^${REPO_VAR}=" .env | cut -d= -f2)
  [ -f "$REPO_PATH/.env" ] && echo "  - $REPO_PATH"
done
```
