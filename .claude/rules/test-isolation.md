# Test Isolation — Tests Must Not Mutate Canonical Repos

## HARD RULE

Tests must NEVER modify files in canonical (non-clone) repos. A test that overwrites a real SKILL.md, commits to a real repo, or mutates real `.claude/` files is not a test — it is production sabotage.

## What This Means

- E2E tests that test edit/write operations must use **clone repos or tmp directories**, never the canonical repo.
- If a test needs to verify `dot-claude-edit`, it must edit a file in a temporary clone, then restore/discard the clone.
- If a test's `finally` block "restores" the original content, it is already too late — a crash, timeout, or interruption leaves the canonical repo corrupted.
- Tests must be safe to kill at any point without leaving damage.

## Violations

These are all violations:
- `_run_cli("edit", "supervisor-start", input_text=test_content)` on the real hub repo
- `echo "test" | pixi run dot-claude-edit skill` in a test against the canonical repo
- Any test that calls `git commit` on a non-clone repo
- Any test that writes to `.claude/` in a canonical repo path

## How to Test Edit Operations Safely

1. Create a temporary directory with a `.claude/` structure
2. Point the CLI at the temp directory via `--repo /tmp/test-repo`
3. Or use the variant clone mechanism — clones are disposable by design
