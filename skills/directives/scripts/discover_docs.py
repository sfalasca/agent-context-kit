#!/usr/bin/env python3
"""Discover all directive docs and AGENTS.md in the current project, PLUS this skill's own
bundled default docs (in a docs/ folder next to this script) -- those apply everywhere the
directives skill is available, not just in projects that vendor their own copies.
Outputs a plain structured list -- no file content.
"""

import argparse
import os
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PRUNE_TOP_LEVEL = {".git", "node_modules"}
OPT_OUT_MARKER = ".no-bundled-directives"


def find_project_docs(root: Path):
    """Every *.md file with a 'docs' ancestor directory, mirroring `-path '*/docs/*.md'`."""
    for dirpath, dirnames, filenames in os.walk(root):
        if Path(dirpath) == root:
            dirnames[:] = [d for d in dirnames if d not in PRUNE_TOP_LEVEL]
        for name in filenames:
            if not name.endswith(".md"):
                continue
            path = Path(dirpath) / name
            if "docs" in path.parts[:-1]:
                yield path


def print_list(items):
    items = list(items)
    if items:
        for item in items:
            # Forward slashes on every OS, so output is OS-invariant.
            print(item.as_posix())
    else:
        print("(none found)")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover directive docs (project docs/*.md plus this skill's bundled "
        "defaults) and AGENTS.md. Prints a plain path listing, no file content."
    )
    parser.parse_args()

    print("=== AGENTS.md ===")
    agents_md = Path("AGENTS.md")
    print(agents_md if agents_md.is_file() else "(none found)")

    print()
    if Path(OPT_OUT_MARKER).is_file():
        print(f"=== Skill-bundled docs (skipped: {OPT_OUT_MARKER} marker present) ===")
    else:
        print("=== Skill-bundled docs (read-only defaults; add/update never target these) ===")
        bundled_dir = SKILL_DIR / "docs"
        bundled = sorted(bundled_dir.glob("*.md")) if bundled_dir.is_dir() else []
        print_list(bundled)

    print()
    print("=== Project docs ===")
    print_list(sorted(find_project_docs(Path("."))))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        _devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(_devnull, sys.stdout.fileno())
        raise SystemExit(1)
