#!/usr/bin/env python3
"""Discover all scripts in scripts/ folders in the current project, PLUS this skill's own
bundled scripts (in a scripts/ folder next to this script) -- those are available everywhere
the scripts skill is available, not just in projects that vendor their own copies.
Outputs a plain list of paths -- no file content.
"""

import argparse
import os
import sys
from pathlib import Path

BUNDLED_SCRIPTS_DIR = Path(__file__).resolve().parent
PRUNE_TOP_LEVEL = {".git", "node_modules"}


def find_project_scripts(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        if Path(dirpath) == root:
            dirnames[:] = [d for d in dirnames if d not in PRUNE_TOP_LEVEL]
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            path = Path(dirpath) / name
            if "scripts" in path.parts[:-1]:
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
        description="List scripts/-folder scripts in the current project plus this skill's "
        "bundled scripts. Prints a plain path listing, no file content."
    )
    parser.parse_args()

    print("=== Skill-bundled scripts ===")
    bundled_dir = BUNDLED_SCRIPTS_DIR
    bundled = (
        sorted(
            p
            for p in bundled_dir.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        )
        if bundled_dir.is_dir()
        else []
    )
    print_list(bundled)

    print()
    print("=== Project scripts ===")
    print_list(sorted(find_project_scripts(Path("."))))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        _devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(_devnull, sys.stdout.fileno())
        raise SystemExit(1)
