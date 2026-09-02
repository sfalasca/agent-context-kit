"""Exercises `npx skills add` (https://github.com/vercel-labs/skills), the primary multi-agent
installer for this repo -- see docs/install-conventions.md. Needs network access to fetch the
`skills` package and touches $HOME for the global-scope case, so this only runs inside the
container this repo's test harness provides (see Containerfile / `python3 scripts/dev test`).
"""

import os
import tempfile
import unittest
from pathlib import Path

from util import REPO_ROOT, run

SKILL_NAMES = {"directives", "how-tos", "scripts", "context-refactor"}


@unittest.skipUnless(
    os.environ.get("AGENT_CONTEXT_KIT_IN_CONTAINER") == "1",
    "needs network access and touches $HOME -- only safe inside the isolated container this "
    "repo's test harness runs in. Run via `python3 scripts/dev test`.",
)
class NpxSkillsAddTest(unittest.TestCase):
    def test_lists_all_skills(self):
        result = run(["npx", "--yes", "skills@latest", "add", REPO_ROOT, "--list"], timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in SKILL_NAMES:
            self.assertIn(name, result.stdout)

    def test_project_scope_install(self):
        with tempfile.TemporaryDirectory() as project:
            result = run(
                [
                    "npx", "--yes", "skills@latest", "add", REPO_ROOT,
                    "--skill", "*", "--agent", "claude-code", "-y",
                ],
                cwd=Path(project),
                timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in SKILL_NAMES:
                skill_md = Path(project) / ".claude" / "skills" / name / "SKILL.md"
                self.assertTrue(skill_md.is_file(), skill_md)

    def test_global_scope_install(self):
        home = Path(os.environ["HOME"])
        result = run(
            [
                "npx", "--yes", "skills@latest", "add", REPO_ROOT,
                "--skill", "*", "--agent", "claude-code", "-g", "-y",
            ],
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in SKILL_NAMES:
            skill_md = home / ".claude" / "skills" / name / "SKILL.md"
            self.assertTrue(skill_md.is_file(), skill_md)


if __name__ == "__main__":
    unittest.main()
