"""Read, edit, and diff .claude files (skills, agents, rules) in any repo.

Used by pixi tasks to manage .claude/ files in this repo or child repos.
Uses harness_core.prompt_editor — same tooling as the supervisor and researcher.

Usage:
    python -m sar_integration.dot_claude_cli --repo . list
    python -m sar_integration.dot_claude_cli --repo ../sar-supervisor read skill
    echo "content" | python -m sar_integration.dot_claude_cli --repo ../sar-research-loop edit skill
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from harness_core.prompt_editor import (
    diff_text,
    edit_asset,
    list_assets,
    read_asset,
    sed_asset,
)

# Default skill/agent names per repo (used for asset resolution)
REPO_DEFAULTS: dict[str, tuple[str, list[str]]] = {
    ".": ("supervisor-start", []),
    "../sar-supervisor": ("start", ["evaluator", "improver"]),
    "../sar-research-loop": ("start", ["evaluator", "improver"]),
    "../sar-rag-target": ("run", []),
}


def _load_dot_env() -> dict[str, str]:
    """Read .env from cwd if it exists."""
    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        return {}
    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            values[key.strip()] = val.strip()
    return values


def _resolve_repo(repo_arg: str) -> Path:
    """Resolve repo path, checking .env vars first."""
    env_map = {
        "supervisor": "SUPERVISOR_REPO",
        "researcher": "RESEARCH_LOOP_REPO",
        "target": "RAG_TARGET_REPO",
    }
    if repo_arg in env_map:
        # Check os.environ first, then .env file
        env_val = os.environ.get(env_map[repo_arg], "")
        if not env_val:
            dot_env = _load_dot_env()
            env_val = dot_env.get(env_map[repo_arg], "")
        if env_val:
            return Path(env_val).resolve()
    return Path(repo_arg).resolve()


def _get_defaults(repo_path: Path) -> tuple[str, list[str]]:
    """Get skill_name and agent_names for a repo."""
    for key, defaults in REPO_DEFAULTS.items():
        if repo_path == Path(key).resolve():
            return defaults
    return ("start", [])


def _cmd_list(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.repo)
    claude_dir = repo / ".claude"
    skill_name, agent_names = _get_defaults(repo)
    assets = list_assets(claude_dir, skill_name, agent_names)
    if args.json:
        print(json.dumps(assets, indent=2))
        return 0
    for a in assets:
        status = f"{a['lines']}L {a['sha1'][:8]}" if a["exists"] else "MISSING"
        print(f"  {a['name']:30s} {status}")
    return 0


def _cmd_read(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.repo)
    claude_dir = repo / ".claude"
    skill_name, agent_names = _get_defaults(repo)
    content = read_asset(claude_dir, skill_name, agent_names, args.name)
    print(content, end="")
    return 0


def _cmd_edit(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.repo)
    claude_dir = repo / ".claude"
    skill_name, agent_names = _get_defaults(repo)

    if args.sed:
        record = sed_asset(
            claude_dir=claude_dir,
            repo_path=repo,
            skill_name=skill_name,
            agent_names=agent_names,
            name=args.name,
            pattern=args.sed,
        )
    else:
        content = sys.stdin.read()
        if not content:
            print("error: no content on stdin", file=sys.stderr)
            return 1
        record = edit_asset(
            claude_dir=claude_dir,
            repo_path=repo,
            skill_name=skill_name,
            agent_names=agent_names,
            name=args.name,
            new_content=content,
        )
    if not record["changed"]:
        print(f"{args.name}: no changes")
        return 0
    if args.json:
        print(json.dumps(record, indent=2))
    else:
        print(f"{args.name}: changed ({record['old_lines']}L -> {record['new_lines']}L)")
        if record.get("diff"):
            print(record["diff"], end="")
    return 0


def _cmd_diff(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.repo)
    claude_dir = repo / ".claude"
    skill_name, agent_names = _get_defaults(repo)
    content = read_asset(claude_dir, skill_name, agent_names, args.name)
    new_content = sys.stdin.read()
    if not new_content:
        print("error: no content on stdin", file=sys.stderr)
        return 1
    diff = diff_text(content, new_content, label=args.name)
    if diff:
        print(diff, end="")
    else:
        print("no differences")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dot-claude")
    parser.add_argument(
        "--repo", default=".",
        help="Repo path or alias (supervisor, researcher, target, or a path)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_p = subparsers.add_parser("list")
    list_p.add_argument("--json", action="store_true")
    list_p.set_defaults(func=_cmd_list)

    read_p = subparsers.add_parser("read")
    read_p.add_argument("name", help="Asset name or path relative to .claude/")
    read_p.set_defaults(func=_cmd_read)

    edit_p = subparsers.add_parser("edit")
    edit_p.add_argument("name", help="Asset name to edit (content from stdin, or --sed pattern)")
    edit_p.add_argument("--json", action="store_true")
    edit_p.add_argument("--sed", default=None, help="Apply sed substitution: s/pattern/replacement/[g]")
    edit_p.set_defaults(func=_cmd_edit)

    diff_p = subparsers.add_parser("diff")
    diff_p.add_argument("name", help="Asset name to diff (new content from stdin)")
    diff_p.set_defaults(func=_cmd_diff)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
