import tempfile
import unittest
from pathlib import Path

from util import REPO_ROOT, init_git_repo, run

DISCOVER = REPO_ROOT / "skills" / "how-tos" / "scripts" / "discover_docs.py"
DESCRIBE = REPO_ROOT / "skills" / "how-tos" / "scripts" / "describe_docs.py"
CHECK_WORKTREE = REPO_ROOT / "skills" / "how-tos" / "scripts" / "check_worktree.py"


class TmpProjectTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.project = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()


class DiscoverDocsTest(TmpProjectTestCase):
    def test_finds_project_how_tos_and_agents_md_no_bundled_section(self):
        (self.project / "how-tos").mkdir()
        (self.project / "how-tos" / "deploy.md").write_text(
            "---\ndescription: x\nscope: root\ncovers: [deploy]\n---\nbody\n"
        )
        (self.project / "AGENTS.md").write_text("# hi\n")

        result = run(["python3", DISCOVER], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("=== AGENTS.md ===\nAGENTS.md", result.stdout)
        self.assertIn("how-tos/deploy.md", result.stdout)
        # Unlike directives, how-tos ships no bundled defaults.
        self.assertNotIn("Skill-bundled", result.stdout)

    def test_no_how_tos_reports_none_found(self):
        result = run(["python3", DISCOVER], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("(none found)", result.stdout)


class DescribeDocsTest(TmpProjectTestCase):
    def test_extracts_frontmatter_only(self):
        (self.project / "how-tos").mkdir()
        (self.project / "how-tos" / "deploy.md").write_text(
            "---\ndescription: x\nscope: root\ncovers: [deploy]\n---\nbody text not printed\n"
        )
        result = run(["python3", DESCRIBE], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("description: x", result.stdout)
        self.assertNotIn("body text not printed", result.stdout)

    def test_no_docs_reports_none_found(self):
        result = run(["python3", DESCRIBE], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("(no how-to docs found)", result.stdout)


class CheckWorktreeTest(TmpProjectTestCase):
    def test_passes_silently_outside_git(self):
        result = run(["python3", CHECK_WORKTREE], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_refuses_primary_checkout(self):
        init_git_repo(self.project)
        result = run(["python3", CHECK_WORKTREE], cwd=self.project)
        self.assertEqual(result.returncode, 1)
        self.assertIn("refusing to mutate how-to docs in the primary checkout", result.stderr)

    def test_passes_in_isolated_worktree(self):
        init_git_repo(self.project)
        with tempfile.TemporaryDirectory() as wt_parent:
            wt_path = Path(wt_parent) / "wt"
            add = run(
                ["git", "worktree", "add", "-q", str(wt_path), "-b", "feature"],
                cwd=self.project,
            )
            self.assertEqual(add.returncode, 0, add.stderr)
            result = run(["python3", CHECK_WORKTREE], cwd=wt_path)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
