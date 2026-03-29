# No Code Deletion

Do NOT delete production code, even if it appears unused or "dead."

- Never remove files, functions, classes, or directories based on grep/reference analysis.
- Code may be called dynamically, referenced from external systems, or kept intentionally for future use.
- "Zero references found" is not sufficient justification for deletion.
- If you believe code is dead, flag it to the user but do not delete it.
