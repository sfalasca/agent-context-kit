import tempfile
import unittest
from pathlib import Path

from util import REPO_ROOT, init_git_repo, run

DISCOVER = REPO_ROOT / "skills" / "directives" / "scripts" / "discover_docs.py"
DESCRIBE = REPO_ROOT / "skills" / "directives" / "scripts" / "describe_docs.py"
CHECK_WORKTREE = REPO_ROOT / "skills" / "directives" / "scripts" / "check_worktree.py"


class TmpProjectTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.project = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()


class DiscoverDocsTest(TmpProjectTestCase):
    def test_finds_bundled_and_project_docs_and_agents_md(self):
        (self.project / "docs").mkdir()
        (self.project / "docs" / "example.md").write_text(
            "---\ndescription: x\nscope: root\ncovers: [a]\n---\nbody\n"
        )
        (self.project / "AGENTS.md").write_text("# hi\n")

        result = run(["python3", DISCOVER], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("=== AGENTS.md ===\nAGENTS.md", result.stdout)
        self.assertIn("container-only-development.md", result.stdout)
        self.assertIn("docs/example.md", result.stdout)

    def test_no_docs_reports_none_found(self):
        result = run(["python3", DISCOVER], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("(none found)", result.stdout)

    def test_opt_out_marker_skips_bundled_docs(self):
        (self.project / ".no-bundled-directives").touch()
        result = run(["python3", DISCOVER], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("skipped: .no-bundled-directives marker present", result.stdout)
        self.assertNotIn("container-only-development.md", result.stdout)


class DescribeDocsTest(TmpProjectTestCase):
    def test_extracts_frontmatter_only(self):
        (self.project / "docs").mkdir()
        (self.project / "docs" / "example.md").write_text(
            "---\ndescription: x\nscope: root\ncovers: [a]\n---\nbody text not printed\n"
        )
        result = run(["python3", DESCRIBE], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("description: x", result.stdout)
        self.assertIn("scope: root", result.stdout)
        self.assertNotIn("body text not printed", result.stdout)

    def test_missing_frontmatter_reported(self):
        (self.project / "docs").mkdir()
        (self.project / "docs" / "nofm.md").write_text("just a heading\n\nno frontmatter here\n")
        result = run(["python3", DESCRIBE], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("(no frontmatter)", result.stdout)

    def test_opt_out_marker_skips_bundled_docs(self):
        (self.project / ".no-bundled-directives").touch()
        result = run(["python3", DESCRIBE], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("skipped: .no-bundled-directives marker present", result.stdout)
        self.assertNotIn("container-only-development", result.stdout)


class CheckWorktreeTest(TmpProjectTestCase):
    def test_passes_silently_outside_git(self):
        result = run(["python3", CHECK_WORKTREE], cwd=self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_refuses_primary_checkout(self):
        init_git_repo(self.project)
        result = run(["python3", CHECK_WORKTREE], cwd=self.project)
        self.assertEqual(result.returncode, 1)
        self.assertIn("refusing to mutate directive docs in the primary checkout", result.stderr)

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
            self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
