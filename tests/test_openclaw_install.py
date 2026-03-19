from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALL_SCRIPT = REPO_ROOT / "scripts" / "install_openclaw_skill.py"


class OpenClawInstallTests(unittest.TestCase):
    def test_install_and_check_render_openclaw_skill(self) -> None:
        with tempfile.TemporaryDirectory() as workspace_dir, tempfile.TemporaryDirectory() as project_dir:
            workspace_root = Path(workspace_dir)
            project_root = Path(project_dir)

            install_proc = subprocess.run(
                [
                    "python3",
                    str(INSTALL_SCRIPT),
                    "--workspace",
                    str(workspace_root),
                    "--project-dir",
                    str(project_root),
                    "--repo-root",
                    str(REPO_ROOT),
                ],
                cwd=str(REPO_ROOT),
                text=True,
                capture_output=True,
                check=True,
            )
            install_result = json.loads(install_proc.stdout)
            self.assertEqual(install_result["status"], "success")
            self.assertEqual(install_result["skill_name"], "longevity")
            self.assertEqual(
                Path(install_result["skill_file"]).name,
                "SKILL.md",
            )

            skill_file = workspace_root / "skills" / "longevity" / "SKILL.md"
            agents_dir = workspace_root / "skills" / "longevity" / "agents"
            self.assertTrue(skill_file.exists())
            self.assertTrue(agents_dir.exists())
            self.assertTrue((agents_dir / "shiyi.md").exists())

            skill_text = skill_file.read_text(encoding="utf-8")
            self.assertIn(str(REPO_ROOT / "scripts"), skill_text)
            self.assertIn(str(project_root / "data" / "taiyiyuan.db"), skill_text)
            self.assertNotIn("{SCRIPTS_DIR}", skill_text)

            check_proc = subprocess.run(
                [
                    "python3",
                    str(INSTALL_SCRIPT),
                    "--workspace",
                    str(workspace_root),
                    "--project-dir",
                    str(project_root),
                    "--repo-root",
                    str(REPO_ROOT),
                    "--check",
                ],
                cwd=str(REPO_ROOT),
                text=True,
                capture_output=True,
                check=True,
            )
            check_result = json.loads(check_proc.stdout)
            self.assertEqual(check_result["status"], "ok")
            self.assertEqual(check_result["problems"], [])


if __name__ == "__main__":
    unittest.main()
