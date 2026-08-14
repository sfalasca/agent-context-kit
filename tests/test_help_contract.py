"""Every .py script in this repo must implement --help properly, per this repo's own scripts
skill requirement (see skills/scripts/SKILL.md's "The --help requirement"): always available,
exits 0, prints real output, no side effects, fast. This test discovers every script dynamically
so it automatically covers anything added later — nothing to hand-maintain.
"""

import unittest

from util import REPO_ROOT, run

EXCLUDE_DIR_PARTS = {".git", "__pycache__", "tests", "node_modules"}


def discover_python_scripts():
    scripts = []
    for path in sorted(REPO_ROOT.rglob("*.py")):
        rel = path.relative_to(REPO_ROOT)
        if any(part in EXCLUDE_DIR_PARTS for part in rel.parts):
            continue
        scripts.append(path)
    return scripts


class HelpContractTest(unittest.TestCase):
    def test_discovery_finds_scripts(self):
        # Guards against a discovery bug silently turning this into a no-op test.
        scripts = discover_python_scripts()
        self.assertGreaterEqual(len(scripts), 8, scripts)

    def test_every_script_supports_help(self):
        failures = []
        for script in discover_python_scripts():
            with self.subTest(script=str(script.relative_to(REPO_ROOT))):
                result = run(["python3", script, "--help"], timeout=5)
                if result.returncode != 0:
                    failures.append(
                        f"{script}: --help exited {result.returncode}\n{result.stderr}"
                    )
                elif not result.stdout.strip():
                    failures.append(f"{script}: --help produced no output")
        self.assertFalse(failures, "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
