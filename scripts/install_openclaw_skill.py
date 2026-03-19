#!/usr/bin/env python3
"""
Render and install the Longevity OS skill into a local OpenClaw workspace.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from paths import get_project_root


SKILL_NAME = "longevity"


def _default_workspace_root() -> Path:
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        workspace = config.get("agents", {}).get("defaults", {}).get("workspace")
        if workspace:
            return Path(workspace).expanduser().resolve()
    return (Path.home() / ".openclaw" / "workspace").resolve()


def _placeholders(repo_root: Path, install_root: Path, project_root: Path) -> dict[str, str]:
    return {
        "{SKILL_DIR}": str(repo_root),
        "{AGENTS_DIR}": str((install_root / "agents").resolve()),
        "{MODELING_DIR}": str((repo_root / "modeling").resolve()),
        "{DATA_DIR}": str((repo_root / "data").resolve()),
        "{SCRIPTS_DIR}": str((repo_root / "scripts").resolve()),
        "{PROJECT_DIR}": str(project_root.resolve()),
        "{DATABASE}": str((project_root / "data" / "taiyiyuan.db").resolve()),
        "{REPORTS_DIR}": str((project_root / "reports").resolve()),
        "{PHOTOS_DIR}": str((project_root / "photos").resolve()),
        "{TRIALS_DIR}": str((project_root / "trials").resolve()),
        "{SCHEMA_FILE}": str((repo_root / "data" / "schema.sql").resolve()),
    }


def _render_text(text: str, placeholders: dict[str, str]) -> str:
    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


def _required_agent_files(repo_root: Path) -> list[Path]:
    return sorted((repo_root / "agents").glob("*.md"))


def install_skill(repo_root: Path, workspace_root: Path, project_root: Path) -> dict:
    install_root = workspace_root / "skills" / SKILL_NAME
    agents_root = install_root / "agents"
    install_root.mkdir(parents=True, exist_ok=True)
    agents_root.mkdir(parents=True, exist_ok=True)

    placeholders = _placeholders(repo_root, install_root, project_root)

    skill_source = repo_root / "SKILL.md"
    rendered_skill = _render_text(skill_source.read_text(encoding="utf-8"), placeholders)
    (install_root / "skill.md").write_text(rendered_skill, encoding="utf-8")

    copied_agents = []
    for agent_source in _required_agent_files(repo_root):
        rendered_agent = _render_text(agent_source.read_text(encoding="utf-8"), placeholders)
        target = agents_root / agent_source.name
        target.write_text(rendered_agent, encoding="utf-8")
        copied_agents.append(str(target))

    return {
        "status": "success",
        "repo_root": str(repo_root),
        "workspace_root": str(workspace_root),
        "install_root": str(install_root),
        "skill_file": str(install_root / "skill.md"),
        "agents_dir": str(agents_root),
        "agents_installed": len(copied_agents),
        "project_root": str(project_root),
        "database": placeholders["{DATABASE}"],
    }


def check_install(repo_root: Path, workspace_root: Path, project_root: Path) -> dict:
    install_root = workspace_root / "skills" / SKILL_NAME
    skill_file = install_root / "skill.md"
    agents_root = install_root / "agents"
    expected_agents = _required_agent_files(repo_root)

    problems = []
    if not skill_file.exists():
        problems.append(f"Missing skill file: {skill_file}")
    if not agents_root.exists():
        problems.append(f"Missing agents directory: {agents_root}")

    rendered_paths = _placeholders(repo_root, install_root, project_root)
    if skill_file.exists():
        skill_text = skill_file.read_text(encoding="utf-8")
        if rendered_paths["{SCRIPTS_DIR}"] not in skill_text:
            problems.append("Installed skill.md does not reference the current repo scripts directory")
        if "{SCRIPTS_DIR}" in skill_text:
            problems.append("Installed skill.md still contains unresolved placeholders")

    missing_agents = []
    unresolved_agents = []
    for agent_source in expected_agents:
        target = agents_root / agent_source.name
        if not target.exists():
            missing_agents.append(agent_source.name)
            continue
        text = target.read_text(encoding="utf-8")
        if "{SCRIPTS_DIR}" in text or "{DATABASE}" in text:
            unresolved_agents.append(agent_source.name)

    if missing_agents:
        problems.append(f"Missing agent files: {', '.join(missing_agents)}")
    if unresolved_agents:
        problems.append(f"Unresolved placeholders remain in: {', '.join(unresolved_agents)}")

    return {
        "status": "ok" if not problems else "error",
        "workspace_root": str(workspace_root),
        "install_root": str(install_root),
        "project_root": str(project_root),
        "problems": problems,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the Longevity OS skill into OpenClaw")
    parser.add_argument("--workspace", help="OpenClaw workspace root; defaults from ~/.openclaw/openclaw.json")
    parser.add_argument("--project-dir", help="Runtime project dir to embed in rendered files")
    parser.add_argument("--repo-root", help="Repo root to render from; defaults to this checkout")
    parser.add_argument("--check", action="store_true", help="Verify the current installation instead of writing files")
    parser.add_argument("--clean", action="store_true", help="Remove existing installed agent files before copying")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else REPO_ROOT
    workspace_root = Path(args.workspace).expanduser().resolve() if args.workspace else _default_workspace_root()
    project_root = Path(args.project_dir).expanduser().resolve() if args.project_dir else get_project_root()

    try:
        if args.clean:
            install_root = workspace_root / "skills" / SKILL_NAME
            if install_root.exists():
                shutil.rmtree(install_root)

        result = check_install(repo_root, workspace_root, project_root) if args.check else install_skill(
            repo_root,
            workspace_root,
            project_root,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] in {"success", "ok"} else 1
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
