#!/usr/bin/env python3
"""Discover all how-to docs and AGENTS.md in the current project.
Unlike the `directives` skill, this skill ships no bundled defaults -- how-tos
(deploy, generate a token, compile, rotate credentials, run a database migration, ...) are
inherently project-specific, so there is nothing generic to fall back to.
Outputs a plain structured list -- no file content.
"""

import argparse
import os
import sys
from pathlib import Path

PRUNE_TOP_LEVEL = {".git", "node_modules"}


def find_how_to_docs(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        if Path(dirpath) == root:
            dirnames[:] = [d for d in dirnames if d not in PRUNE_TOP_LEVEL]
        for name in filenames:
            if not name.endswith(".md"):
                continue
            path = Path(dirpath) / name
            if "how-tos" in path.parts[:-1]:
                yield path


def print_list(items):
    items = list(items)
    if items:
        for item in items:
            print(item)
    else:
        print("(none found)")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover how-to docs (**/how-tos/*.md) and AGENTS.md in the current "
        "project. Prints a plain path listing, no file content."
    )
    parser.parse_args()

    print("=== AGENTS.md ===")
    agents_md = Path("AGENTS.md")
    print(agents_md if agents_md.is_file() else "(none found)")

    print()
    print("=== How-to docs ===")
    print_list(sorted(find_how_to_docs(Path("."))))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        _devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(_devnull, sys.stdout.fileno())
        raise SystemExit(1)
