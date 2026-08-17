#!/usr/bin/env python3
"""For each script -- project scripts AND this skill's own bundled scripts -- run `--help` and
print its output. This is the authoritative metadata source (not a comment header) -- every
script is required to implement --help properly: fast, side-effect-free, exit 0. A timeout
guards against a script that doesn't honor that.
For a scripts folder's README.md, prints only a short summary (first paragraph, capped) --
not the full body, to keep this cheap like describe_docs.py's frontmatter-only extraction.
Full README content is read later, only for folders whose scripts actually match a task.
Also prints an optional "# tags:" header line if present, to help cheap keyword pre-filtering.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

BUNDLED_SCRIPTS_DIR = Path(__file__).resolve().parent
PRUNE_TOP_LEVEL = {".git", "node_modules"}
HELP_TIMEOUT = 5


def find_project_scripts(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        if Path(dirpath) == root:
            dirnames[:] = [d for d in dirnames if d not in PRUNE_TOP_LEVEL]
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            path = Path(dirpath) / name
            if "scripts" in path.parts[:-1]:
                yield path


def read_tags_line(path: Path) -> str:
    try:
        with path.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                stripped = line.strip()
                if stripped.startswith("#") and "tags:" in stripped:
                    return stripped
    except OSError:
        pass
    return ""


README_SUMMARY_LINES = 8


def read_readme_summary(path: Path) -> list:
    """First paragraph of a README, capped at README_SUMMARY_LINES -- a cheap discovery
    signal, not the authoritative content. Mirrors describe_docs.py extracting frontmatter
    only, not the body: full README content is read later, only for folders that actually
    match (see this skill's `context` mode).
    """
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return [f"(could not read: {exc})"]
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    summary = []
    for line in lines[i:]:
        if not line.strip() and summary:
            break
        summary.append(line)
        if len(summary) >= README_SUMMARY_LINES:
            break
    return summary


def describe_one(f: Path) -> None:
    # Forward slashes on every OS, so output (and anything keying off it) is OS-invariant.
    print(f.as_posix())

    if f.name == "README.md":
        summary = read_readme_summary(f)
        if summary:
            for line in summary:
                print(f"  {line}")
        print(
            "  (summary only, not the full README -- read this file directly once its "
            "folder's scripts match; it's often the only place gotchas, prerequisites, or "
            "non-obvious conventions live)"
        )
        print()
        return

    # The executable bit is a POSIX concept; on Windows os.access(..., X_OK) is
    # true for any readable file, so the gate only means something on POSIX.
    if os.name == "posix" and not os.access(f, os.X_OK):
        print("  (not executable -- skipping --help)")
        print()
        return

    tags = read_tags_line(f)
    if tags:
        print(f"  {tags}")

    # Python scripts run through the current interpreter -- shebang lines and the
    # executable bit don't exist on Windows (see docs/os-independence.md). Anything
    # else is invoked directly, as before.
    if f.suffix.lower() == ".py":
        cmd = [sys.executable, str(f), "--help"]
    else:
        cmd = [str(f), "--help"]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=HELP_TIMEOUT
        )
        status = result.returncode
        output = (result.stdout or "") + (result.stderr or "")
    except subprocess.TimeoutExpired:
        status = 124
        output = ""
    except OSError as exc:
        status = 1
        output = str(exc)

    if status != 0:
        print(f"  (--help failed with exit code {status} -- this script violates the --help requirement)")
    elif not output.strip():
        print("  (--help produced no output -- this script violates the --help requirement)")
    else:
        for line in output.splitlines():
            print(f"  {line}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run --help on every scripts/-folder script (project plus this skill's "
        "bundled scripts) and print the output, the authoritative metadata source."
    )
    parser.parse_args()

    found = False

    bundled_dir = BUNDLED_SCRIPTS_DIR
    if bundled_dir.is_dir():
        for f in sorted(
            p for p in bundled_dir.rglob("*") if p.is_file() and "__pycache__" not in p.parts
        ):
            describe_one(f)
            found = True

    for f in sorted(find_project_scripts(Path("."))):
        describe_one(f)
        found = True

    if not found:
        print("(no scripts found)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        _devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(_devnull, sys.stdout.fileno())
        raise SystemExit(1)
