# Test Output Capture

When running tests, always save the full output to a file, then analyze results from that file. This avoids rerunning tests multiple times.

```bash
pixi run -e dev test 2>&1 | tee /tmp/pytest_output.txt
```

Then read `/tmp/pytest_output.txt` to analyze failures instead of rerunning.
