#!/usr/bin/env python3
"""For each directive doc -- project docs AND this skill's own bundled default docs -- extract
and print the frontmatter only. Does NOT read the body -- keeps context lean.
Only treats --- on line 1 as the YAML frontmatter opener.
"""

import argparse
import os
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PRUNE_TOP_LEVEL = {".git", "node_modules"}
OPT_OUT_MARKER = ".no-bundled-directives"


def find_project_docs(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        if Path(dirpath) == root:
            dirnames[:] = [d for d in dirnames if d not in PRUNE_TOP_LEVEL]
        for name in filenames:
            if not name.endswith(".md"):
                continue
            path = Path(dirpath) / name
            if "docs" in path.parts[:-1]:
                yield path


def extract_frontmatter(path: Path) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    if not lines or lines[0] != "---":
        return ""
    body = []
    for line in lines[1:]:
        if line == "---":
            break
        body.append(line)
    return "\n".join(body)


def print_frontmatter(path: Path) -> None:
    # Forward slashes on every OS, so output is OS-invariant.
    print(path.as_posix())
    frontmatter = extract_frontmatter(path)
    if frontmatter:
        for line in frontmatter.splitlines():
            print(f"  {line}")
    else:
        print("  (no frontmatter)")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print frontmatter-only metadata for every directive doc (bundled "
        "defaults plus project docs/*.md), without reading the body."
    )
    parser.parse_args()

    found = False

    if Path(OPT_OUT_MARKER).is_file():
        print(f"=== Skill-bundled docs (skipped: {OPT_OUT_MARKER} marker present) ===")
    else:
        print("=== Skill-bundled docs (generic defaults; a project doc on the same topic takes precedence) ===")
        bundled_dir = SKILL_DIR / "docs"
        if bundled_dir.is_dir():
            for f in sorted(bundled_dir.glob("*.md")):
                print_frontmatter(f)
                found = True

    print("=== Project docs (override bundled defaults on the same topic) ===")
    for f in sorted(find_project_docs(Path("."))):
        print_frontmatter(f)
        found = True

    if not found:
        print("(no directive docs found)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        _devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(_devnull, sys.stdout.fileno())
        raise SystemExit(1)
