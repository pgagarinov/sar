# Design Principles

These apply to ALL code, prompts, tests, and skills across ALL repos in this system:

- **NO STUBS** — every function must have a real, working implementation
- **NO FAILOVERS** — if something fails, fix it, don't work around it
- **NO DRY RUNS** — always run real evaluations and real tests, never simulate
- **NO HALF-DONE IMPLEMENTATIONS** — every change must be complete and tested
- **NO SHORTCUTS** — follow the full discipline every time
- **ALL OPERATIONS GO THROUGH SKILLS** — never run direct commands on another repo's internals. Each repo exposes its operations as skills (`claude -p /skill`) or pixi tasks (`pixi run task`). The integration hub orchestrates by calling these interfaces, never by reaching into `.supervisor/`, `results.tsv`, or other internal state directly.
- **PROMPT EDITS ONLY VIA HARNESS** — `.claude/` files in any repo are NEVER edited directly. Use the prompt-edit pixi tasks (`pixi run prompt-edit`, `pixi run target-prompt-edit`). These log, diff, and auto-commit every change.
- **WIRING vs RESEARCH RESULTS** — Rules, hooks, config, and infrastructure code are **wiring** — they define how the system operates and never contain domain-specific research results. SKILL.md content, lessons learned, technique inventories, and current-state sections are **research results** — they are written by the supervisor per research phase. Never mix research results into wiring files (rules, settings.json, hooks, Python infrastructure). Never hardcode research results into committed code.
- **LESSONS LEARNED, NOT BLACKLISTS** — Never permanently ban a technique. A technique that failed alone may succeed in combination. Instead, record WHY it failed (the structural assumption it violated) so future attempts can address the root cause.
