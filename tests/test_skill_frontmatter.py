"""Every SKILL.md in skills/ must validate against the open Agent Skills spec
(https://agentskills.io/specification) -- see docs/skill-content-portability.md for why.
"""

import re
import unittest

import yaml

from util import REPO_ROOT

SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")


def load_frontmatter(skill_md):
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{skill_md}: does not start with a YAML frontmatter block")
    end = text.index("\n---\n", 4)
    return yaml.safe_load(text[4 : end + 1])


class SkillFrontmatterTest(unittest.TestCase):
    def test_discovers_skills(self):
        skill_mds = sorted(REPO_ROOT.glob("skills/*/SKILL.md"))
        self.assertGreaterEqual(len(skill_mds), 3, skill_mds)

    def test_every_skill_md_is_spec_compliant(self):
        for skill_md in sorted(REPO_ROOT.glob("skills/*/SKILL.md")):
            with self.subTest(skill=str(skill_md.relative_to(REPO_ROOT))):
                fm = load_frontmatter(skill_md)

                extra = set(fm.keys()) - SPEC_FIELDS
                self.assertFalse(extra, f"non-spec top-level frontmatter fields: {extra}")

                name = fm.get("name")
                self.assertIsInstance(name, str)
                self.assertTrue(1 <= len(name) <= 64)
                self.assertTrue(NAME_RE.fullmatch(name), name)
                self.assertEqual(name, skill_md.parent.name)

                description = fm.get("description")
                self.assertIsInstance(description, str)
                self.assertTrue(1 <= len(description) <= 1024)

                compatibility = fm.get("compatibility")
                if compatibility is not None:
                    self.assertIsInstance(compatibility, str)
                    self.assertTrue(1 <= len(compatibility) <= 500)

                allowed_tools = fm.get("allowed-tools")
                if allowed_tools is not None:
                    self.assertIsInstance(allowed_tools, str)
                    self.assertNotIn(",", allowed_tools)

                metadata = fm.get("metadata")
                if metadata is not None:
                    self.assertIsInstance(metadata, dict)
                    for key, value in metadata.items():
                        self.assertIsInstance(key, str)
                        self.assertIsInstance(value, str)


if __name__ == "__main__":
    unittest.main()
