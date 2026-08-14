"""This repo dogfoods its own directives/how-tos skills on itself (docs/, how-tos/) -- their
own frontmatter spec (description/scope/covers, all non-empty) applies here too. See
skills/directives/SKILL.md and skills/how-tos/SKILL.md's "frontmatter" sections.
"""

import unittest

import yaml

from util import REPO_ROOT

REQUIRED_FIELDS = {"description", "scope", "covers"}


def load_frontmatter(md_path):
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{md_path}: does not start with a YAML frontmatter block")
    end = text.index("\n---\n", 4)
    return yaml.safe_load(text[4 : end + 1])


class RepoDocsFrontmatterTest(unittest.TestCase):
    def _check_all(self, paths):
        found = list(paths)
        self.assertTrue(found, "no docs discovered -- test is not exercising anything")
        for path in found:
            with self.subTest(doc=str(path.relative_to(REPO_ROOT))):
                fm = load_frontmatter(path)
                missing = REQUIRED_FIELDS - fm.keys()
                self.assertFalse(missing, f"missing frontmatter fields: {missing}")
                for field in REQUIRED_FIELDS:
                    self.assertTrue(str(fm[field]).strip(), f"empty frontmatter field: {field}")

    def test_repo_directive_docs_have_complete_frontmatter(self):
        self._check_all(sorted((REPO_ROOT / "docs").glob("*.md")))

    def test_repo_how_to_docs_have_complete_frontmatter(self):
        self._check_all(sorted((REPO_ROOT / "how-tos").glob("*.md")))


if __name__ == "__main__":
    unittest.main()
