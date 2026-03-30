"""E2E tests for hub CLI: real cross-repo .claude/ access."""
import json
import os
import subprocess

import pytest
from pathlib import Path

pytestmark = pytest.mark.e2e

HUB_DIR = Path(__file__).parent.parent.resolve()


def _run_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": str(HUB_DIR / "src")}
    return subprocess.run(
        ["python", "-m", "sar_integration.dot_claude_cli", *args],
        capture_output=True, text=True, timeout=30, env=env, cwd=str(HUB_DIR),
        input=input_text,
    )


class TestListOwnAssets:
    def test_finds_real_skills(self) -> None:
        r = _run_cli("list")
        assert r.returncode == 0, f"Failed: {r.stderr}"
        # The hub's skill_name is "supervisor-start", which maps to asset name "skill"
        assert "skill" in r.stdout.lower()

    def test_finds_real_rules(self) -> None:
        r = _run_cli("list")
        assert r.returncode == 0, f"Failed: {r.stderr}"
        assert "design-principles" in r.stdout or "separation-of-concerns" in r.stdout

    def test_json_output_valid(self) -> None:
        r = _run_cli("list", "--json")
        assert r.returncode == 0, f"Failed: {r.stderr}"
        data = json.loads(r.stdout)
        assert isinstance(data, list)
        assert len(data) > 5, f"Hub should have multiple assets, got {len(data)}"
        for entry in data:
            assert "name" in entry
            assert "exists" in entry
            if entry["exists"]:
                assert "lines" in entry
                assert "sha1" in entry


class TestListSiblingRepos:
    def test_supervisor_assets(self) -> None:
        r = _run_cli("--repo", "supervisor", "list", "--json")
        assert r.returncode == 0, f"Failed: {r.stderr}"
        data = json.loads(r.stdout)
        names = {e["name"] for e in data}
        assert "skill" in names, f"Supervisor should have a 'skill' asset, got {names}"

    def test_researcher_assets(self) -> None:
        r = _run_cli("--repo", "researcher", "list", "--json")
        assert r.returncode == 0, f"Failed: {r.stderr}"
        data = json.loads(r.stdout)
        names = {e["name"] for e in data}
        assert "evaluator" in names, f"Researcher should have 'evaluator' agent, got {names}"
        assert "improver" in names, f"Researcher should have 'improver' agent, got {names}"

    def test_target_assets(self) -> None:
        r = _run_cli("--repo", "target", "list", "--json")
        assert r.returncode == 0, f"Failed: {r.stderr}"
        data = json.loads(r.stdout)
        names = {e["name"] for e in data}
        assert "skill" in names, f"Target should have a 'skill' asset, got {names}"


class TestReadAssets:
    def test_read_own_skill(self) -> None:
        # The hub's skill is accessed via asset name "skill" (maps to skills/supervisor-start/SKILL.md)
        r = _run_cli("read", "skill")
        assert r.returncode == 0, f"Failed: {r.stderr}"
        assert len(r.stdout) > 0, "Skill content should not be empty"

    def test_read_own_rule_by_path(self) -> None:
        # Read a rule using its relative path under .claude/
        r = _run_cli("read", "rules/design-principles.md")
        assert r.returncode == 0, f"Failed: {r.stderr}"
        assert len(r.stdout) > 50, "Rule content should be substantial"
        assert "design" in r.stdout.lower() or "principles" in r.stdout.lower()

    def test_read_supervisor_skill(self) -> None:
        r = _run_cli("--repo", "supervisor", "read", "skill")
        assert r.returncode == 0, f"Failed: {r.stderr}"
        assert len(r.stdout) > 20

    def test_read_researcher_evaluator(self) -> None:
        r = _run_cli("--repo", "researcher", "read", "evaluator")
        assert r.returncode == 0, f"Failed: {r.stderr}"
        assert len(r.stdout) > 20

    def test_read_nonexistent_fails(self) -> None:
        r = _run_cli("read", "nonexistent-asset-xyz-999")
        assert r.returncode != 0


class TestDiff:
    def test_same_content_no_diff(self) -> None:
        read_r = _run_cli("read", "skill")
        assert read_r.returncode == 0, f"Failed to read: {read_r.stderr}"
        r = _run_cli("diff", "skill", input_text=read_r.stdout)
        assert r.returncode == 0, f"Failed: {r.stderr}"
        assert "no differences" in r.stdout.lower() or r.stdout.strip() == ""

    def test_different_content_shows_diff(self) -> None:
        r = _run_cli("diff", "skill", input_text="completely different content\n")
        assert r.returncode == 0, f"Failed: {r.stderr}"
        assert "---" in r.stdout or "+++" in r.stdout or "@@" in r.stdout
