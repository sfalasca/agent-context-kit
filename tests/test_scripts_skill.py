import os
import stat
import tempfile
import unittest
from pathlib import Path

from util import REPO_ROOT, run

DISCOVER = REPO_ROOT / "skills" / "scripts" / "scripts" / "discover_scripts.py"
DESCRIBE = REPO_ROOT / "skills" / "scripts" / "scripts" / "describe_scripts.py"


def make_executable(path: Path, content: str) -> None:
    path.write_text(content)
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


GOOD_SCRIPT = """#!/usr/bin/env python3
# tags: [example, greeting]
import sys
if "--help" in sys.argv:
    print("usage: greet.py --help\\n\\nPrints a greeting.")
    sys.exit(0)
print("hello")
"""

BROKEN_HELP_SCRIPT = """#!/usr/bin/env python3
import sys
sys.exit(1)
"""

SILENT_HELP_SCRIPT = """#!/usr/bin/env python3
"""


class TmpProjectTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.project = Path(self._tmp.name)
        self.scripts_dir = self.project / "scripts"
        self.scripts_dir.mkdir()

    def tearDown(self):
        self._tmp.cleanup()


class DiscoverScriptsTest(TmpProjectTestCase):
    def test_finds_bundled_and_project_scripts(self):
        make_executable(self.scripts_dir / "greet.py", GOOD_SCRIPT)
        result = run(["python3", DISCOVER], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("=== Skill-bundled scripts ===", result.stdout)
        self.assertIn("discover_scripts.py", result.stdout)
        self.assertIn("scripts/greet.py", result.stdout)


class DescribeScriptsTest(TmpProjectTestCase):
    def test_captures_help_output_and_tags(self):
        make_executable(self.scripts_dir / "greet.py", GOOD_SCRIPT)
        result = run(["python3", DESCRIBE], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("tags: [example, greeting]", result.stdout)
        self.assertIn("Prints a greeting.", result.stdout)

    def test_flags_broken_help(self):
        make_executable(self.scripts_dir / "broken.py", BROKEN_HELP_SCRIPT)
        result = run(["python3", DESCRIBE], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("violates the --help requirement", result.stdout)

    def test_flags_silent_help(self):
        make_executable(self.scripts_dir / "silent.py", SILENT_HELP_SCRIPT)
        result = run(["python3", DESCRIBE], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("produced no output", result.stdout)

    @unittest.skipUnless(os.name == "posix", "the executable bit is a POSIX concept")
    def test_skips_non_executable(self):
        (self.scripts_dir / "not_executable.py").write_text(GOOD_SCRIPT)
        result = run(["python3", DESCRIBE], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("not executable", result.stdout)

    def test_readme_short_content_surfaced(self):
        (self.scripts_dir / "README.md").write_text("gotcha: needs FOO env var\n")
        result = run(["python3", DESCRIBE], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("gotcha: needs FOO env var", result.stdout)
        self.assertIn("summary only, not the full README", result.stdout)

    def test_readme_long_content_not_dumped_in_full(self):
        # describe is the cheap metadata pass -- full README content is deferred to context
        # mode's match step, mirroring describe_docs.py's frontmatter-only extraction.
        (self.scripts_dir / "README.md").write_text(
            "intro paragraph\n\n" + "\n".join(f"detail line {i}" for i in range(50))
        )
        result = run(["python3", DESCRIBE], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("intro paragraph", result.stdout)
        self.assertNotIn("detail line 49", result.stdout)


if __name__ == "__main__":
    unittest.main()
