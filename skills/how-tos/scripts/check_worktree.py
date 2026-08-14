#!/usr/bin/env python3
"""Refuse to proceed if the current directory is the primary checkout rather than an
isolated git worktree. Run before any mode that writes to how-to docs.
Exits 0 (silent) if the check passes, or if the current directory isn't a git repo
at all (nothing to enforce). Exits 1 with a message on stderr if it's the primary
checkout of a repo that has worktrees set up.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def main() -> int:
    argparse.ArgumentParser(
        description="Fail if the current directory is the primary git checkout rather than "
        "an isolated worktree."
    ).parse_args()

    inside = run_git("rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0:
        return 0

    current_toplevel = run_git("rev-parse", "--show-toplevel").stdout.strip()

    worktree_list = run_git("worktree", "list", "--porcelain").stdout
    primary_toplevel = None
    for line in worktree_list.splitlines():
        if line.startswith("worktree "):
            primary_toplevel = line[len("worktree "):]
            break

    if primary_toplevel is not None and current_toplevel == primary_toplevel:
        primary_name = Path(primary_toplevel).name
        print(
            f"error: refusing to mutate how-to docs in the primary checkout "
            f"({primary_toplevel}).",
            file=sys.stderr,
        )
        print(
            "Create/switch to an isolated worktree first (see git-worktree-oneflow), e.g.:",
            file=sys.stderr,
        )
        print(
            f"  git worktree add ../{primary_name}-worktrees/<slug> -b <branch>",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        _devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(_devnull, sys.stdout.fileno())
        raise SystemExit(1)
