# Researcher Variant and Target Variant Lifecycle

## Researcher Variant States

| State | Process | Researcher clone | Target clone | Can merge? |
|-------|---------|-----------------|-------------|-----------|
| `running` | Active | Exists | Exists, being modified | No (unstable) |
| `parked` | Stopped | Cleaned up | Preserved, snapshot taken | Yes |
| `merged` | Stopped | Cleaned up | Applied to canonical, then cleaned | N/A (done) |
| `discarded` | Stopped | Cleaned up | Cleaned up | N/A (gone) |

## Target Variant States (within a researcher variant)

Target variants are sequential hypothesis tests managed by the researcher. The researcher creates them via `git clone --local` from `CANONICAL_TARGET` and cleans them up when done.

| State | Description |
|-------|------------|
| `active` | Being modified by the improver agent |
| `kept` | Improvement confirmed, becomes the new working copy |
| `discarded` | Regression detected, `git reset --hard HEAD~1` |

## Git Tags in the Target

Two git tags serve different purposes:

| Tag | Moves? | Points to | Used by |
|-----|--------|-----------|---------|
| `seed` | **NEVER** | Original initial commit (`8b64e6b`) | `/target-reset` — go back to the very beginning |
| `baseline` | After each merge | Last merged state | `merge_cherry_pick` — find new commits since last merge |

- `seed` is the immutable starting point. It is set once and never touched by any operation.
- `baseline` is a moving cursor. It advances after WTA, cherry-pick, and B&C merges. Rollback restores it to the pre-merge position.
- `/target-reset` resets HEAD to `seed` AND resets `baseline` back to `seed`.

## Invariants

1. A running researcher variant has BOTH a researcher clone AND a target clone
2. A parked researcher variant has ONLY the target clone (researcher clone cleaned to save space)
3. After merge, the canonical target HEAD matches the winning researcher variant's target HEAD
4. After merge, the `baseline` cursor is updated to the new HEAD
5. The `seed` tag NEVER moves — it always points to the original initial commit
6. A backup snapshot exists for every merge (rollback is always possible)
7. After discard, no researcher clone, target clone, or temp files remain for that researcher variant

## Merge Rules

- Never merge a running researcher variant (park first)
- Always backup canonical target state before any merge
- Always verify target metrics after merge (run `/run` on canonical target)
- If merged target metrics regress: rollback and try a different merge strategy
- Cherry-pick conflicts are skipped (not forced), reported to the supervisor
- Only one merge operation at a time (concurrent merges are undefined behavior)

## Cleanup Order

1. Park (stop process, preserve target clone)
2. Compare metrics across parked researcher variants
3. Merge winner to canonical target
4. Verify merged target metrics
5. Discard remaining parked researcher variants
6. If verification fails: rollback merge, retry with different strategy or different winner
