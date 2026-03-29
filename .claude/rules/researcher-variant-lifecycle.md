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

## Invariants

1. A running researcher variant has BOTH a researcher clone AND a target clone
2. A parked researcher variant has ONLY the target clone (researcher clone cleaned to save space)
3. After merge, the canonical target HEAD matches the winning researcher variant's target HEAD
4. After merge, the `baseline` git tag is updated to the new HEAD
5. A backup snapshot exists for every merge (rollback is always possible)
6. After discard, no researcher clone, target clone, or temp files remain for that researcher variant

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
