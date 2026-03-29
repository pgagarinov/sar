# Profile Rotation

Each layer in the SAR supervision chain uses a different Claude profile (`CLAUDE_CONFIG_DIR`) to spread API quota across accounts and avoid rate-limit cascades.

## The Full Tree

```
Hub (profile[I])
│
├── Supervisor (profile[I+1])
│   │
│   ├── Researcher Variant rv-001 (profile[I+2])
│   │   ├── Target Variant rv-001-tv-1 (profile[I+3])
│   │   └── Target Variant rv-001-tv-2 (profile[I+3])
│   │
│   ├── Researcher Variant rv-002 (profile[I+3])
│   │   └── Target Variant rv-002-tv-1 (profile[I+4])
│   │
│   └── Researcher Variant rv-003 (profile[I+4])
│       └── Target Variant rv-003-tv-1 (profile[I+5])
```

## Assignment Rules

1. **Hub** uses `CLAUDE_CONFIG_DIR` from the user's environment → index I
2. **Supervisor** gets profile[I+1] — set by the hub when launching `claude -p /start`
3. **Researcher Variant N** gets profile[I+2+N] — supervisor's `build_launch_spec(offset=1+variant_index)` computes this
4. **Target Variants within Researcher Variant N** get profile[I+3+N] — passed as `TARGET_CLAUDE_CONFIG_DIR`. All target variants within one researcher variant share this profile.

All indices are `mod len(profiles)`. With 7 profiles and 3 researcher variants:
- Hub: 0, Supervisor: 1
- rv-001: 2, rv-001 targets: 3
- rv-002: 3, rv-002 targets: 4
- rv-003: 4, rv-003 targets: 5

## Why Target Variants Share a Profile

Target variants within one researcher variant are sequential — the researcher dispatches one evaluator at a time. Sharing a profile is safe and avoids exhausting the list.

## Environment Variables

| Var | Set by | Consumed by | Purpose |
|-----|--------|-------------|---------|
| `CLAUDE_CONFIG_DIR` | Parent layer | Claude session | Which profile this session uses |
| `CLAUDE_CONFIG_DIRS` | `.env` / parent | `config.py` | Full list for computing rotation |
| `TARGET_CLAUDE_CONFIG_DIR` | `build_launch_spec` | Evaluator agent | Profile for target's `claude -p /run` |

## Implementation

- `config.py`: `my_profile_index()` finds current index, `next_profile(offset=N)` computes rotation
- `build_launch_spec()`: sets `CLAUDE_CONFIG_DIR` (offset=1) and `TARGET_CLAUDE_CONFIG_DIR` (offset=2)
- `start_researcher_variant()`: per-variant rotation with `offset=1+variant_index`
- Single-profile list: everyone uses the same profile (no rotation, no error)
