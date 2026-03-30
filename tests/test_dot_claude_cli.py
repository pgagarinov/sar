"""Unit tests for dot_claude_cli: env parsing, repo resolution, defaults, argument parsing."""
import pytest
from pathlib import Path


class TestLoadDotEnv:
    def test_parses_kv_skips_comments(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        env_file = tmp_path / ".env"
        env_file.write_text("KEY=VALUE\n# comment\n\nFOO=BAR\n")
        from sar_integration.dot_claude_cli import _load_dot_env
        result = _load_dot_env()
        assert result == {"KEY": "VALUE", "FOO": "BAR"}

    def test_missing_file_returns_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        from sar_integration.dot_claude_cli import _load_dot_env
        assert _load_dot_env() == {}

    def test_strips_whitespace(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        env_file = tmp_path / ".env"
        env_file.write_text("  KEY  =  VALUE  \n")
        from sar_integration.dot_claude_cli import _load_dot_env
        result = _load_dot_env()
        assert result == {"KEY": "VALUE"}

    def test_skips_empty_lines(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        env_file = tmp_path / ".env"
        env_file.write_text("\n\n\nA=1\n\n")
        from sar_integration.dot_claude_cli import _load_dot_env
        result = _load_dot_env()
        assert result == {"A": "1"}


class TestResolveRepo:
    def test_supervisor_alias_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SUPERVISOR_REPO", "/tmp/test-supervisor")
        from sar_integration.dot_claude_cli import _resolve_repo
        result = _resolve_repo("supervisor")
        assert result == Path("/tmp/test-supervisor").resolve()

    def test_researcher_alias_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RESEARCH_LOOP_REPO", "/tmp/test-researcher")
        from sar_integration.dot_claude_cli import _resolve_repo
        result = _resolve_repo("researcher")
        assert result == Path("/tmp/test-researcher").resolve()

    def test_target_alias_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RAG_TARGET_REPO", "/tmp/test-target")
        from sar_integration.dot_claude_cli import _resolve_repo
        result = _resolve_repo("target")
        assert result == Path("/tmp/test-target").resolve()

    def test_alias_falls_back_to_dot_env(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("SUPERVISOR_REPO", raising=False)
        env_file = tmp_path / ".env"
        env_file.write_text("SUPERVISOR_REPO=/tmp/from-dotenv\n")
        from sar_integration.dot_claude_cli import _resolve_repo
        result = _resolve_repo("supervisor")
        assert result == Path("/tmp/from-dotenv").resolve()

    def test_literal_path(self) -> None:
        from sar_integration.dot_claude_cli import _resolve_repo
        result = _resolve_repo("/tmp/some-repo")
        assert result == Path("/tmp/some-repo").resolve()

    def test_relative_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        from sar_integration.dot_claude_cli import _resolve_repo
        result = _resolve_repo(".")
        assert result == tmp_path.resolve()


class TestGetDefaults:
    def test_unknown_repo_returns_start(self) -> None:
        from sar_integration.dot_claude_cli import _get_defaults
        skill, agents = _get_defaults(Path("/fake/unknown-project"))
        assert skill == "start"
        assert agents == []


class TestBuildParser:
    def test_list_subcommand(self) -> None:
        from sar_integration.dot_claude_cli import build_parser
        parser = build_parser()
        ns = parser.parse_args(["list"])
        assert ns.command == "list"
        assert hasattr(ns, "func")

    def test_read_subcommand(self) -> None:
        from sar_integration.dot_claude_cli import build_parser
        parser = build_parser()
        ns = parser.parse_args(["read", "skill"])
        assert ns.command == "read"
        assert ns.name == "skill"

    def test_edit_subcommand(self) -> None:
        from sar_integration.dot_claude_cli import build_parser
        parser = build_parser()
        ns = parser.parse_args(["edit", "skill"])
        assert ns.command == "edit"
        assert ns.name == "skill"
        assert ns.sed is None

    def test_edit_with_sed(self) -> None:
        from sar_integration.dot_claude_cli import build_parser
        parser = build_parser()
        ns = parser.parse_args(["edit", "skill", "--sed", "s/old/new/g"])
        assert ns.sed == "s/old/new/g"

    def test_diff_subcommand(self) -> None:
        from sar_integration.dot_claude_cli import build_parser
        parser = build_parser()
        ns = parser.parse_args(["diff", "skill"])
        assert ns.command == "diff"
        assert ns.name == "skill"

    def test_repo_flag(self) -> None:
        from sar_integration.dot_claude_cli import build_parser
        parser = build_parser()
        ns = parser.parse_args(["--repo", "supervisor", "list"])
        assert ns.repo == "supervisor"
        assert ns.command == "list"

    def test_default_repo_is_dot(self) -> None:
        from sar_integration.dot_claude_cli import build_parser
        parser = build_parser()
        ns = parser.parse_args(["list"])
        assert ns.repo == "."

    def test_list_json_flag(self) -> None:
        from sar_integration.dot_claude_cli import build_parser
        parser = build_parser()
        ns = parser.parse_args(["list", "--json"])
        assert ns.json is True


class TestRepoDefaults:
    def test_known_repos_in_defaults(self) -> None:
        from sar_integration.dot_claude_cli import REPO_DEFAULTS
        assert "." in REPO_DEFAULTS
        assert "../sar-supervisor" in REPO_DEFAULTS
        assert "../sar-research-loop" in REPO_DEFAULTS
        assert "../sar-rag-target" in REPO_DEFAULTS

    def test_hub_defaults(self) -> None:
        from sar_integration.dot_claude_cli import REPO_DEFAULTS
        skill, agents = REPO_DEFAULTS["."]
        assert skill == "supervisor-start"
        assert agents == []

    def test_supervisor_defaults(self) -> None:
        from sar_integration.dot_claude_cli import REPO_DEFAULTS
        skill, agents = REPO_DEFAULTS["../sar-supervisor"]
        assert skill == "start"
        assert "evaluator" in agents
        assert "improver" in agents

    def test_target_defaults(self) -> None:
        from sar_integration.dot_claude_cli import REPO_DEFAULTS
        skill, agents = REPO_DEFAULTS["../sar-rag-target"]
        assert skill == "run"
        assert agents == []
