# Explicit Over Implicit

Always follow an explicit principle. Avoid fallbacks, default values, and silent recovery paths.

## Configuration
- Every configuration value must come from an explicit source (`.env`, `harness.toml`, env var). Never invent defaults that hide missing configuration.
- If a required value is missing, fail with a clear error message naming the missing value and where it should be set.
- Do not silently fall back to a "reasonable default" — that hides misconfiguration until production.

## Error Handling
- If something fails, surface the error. Do not catch-and-continue, catch-and-log-and-continue, or return a fallback value.
- No `except Exception: pass`. No `or default_value` on things that should be configured.
- Let errors propagate until they reach a layer that can meaningfully handle them.

## Code Paths
- Do not write code that handles "just in case" scenarios that cannot happen in the current architecture.
- If a function requires a parameter, make it required — do not add `= None` with a fallback path.
- If a path must exist, assert it exists. Do not silently create it.

## Dependencies
- If code depends on another repo's interface, call that interface explicitly. Do not duplicate logic or guess at internal state.
- If a skill or pixi task exists for an operation, use it. Do not reimplement the operation inline.
