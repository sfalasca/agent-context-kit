"""Shared helpers for tests/. Not a test module itself (no Test* classes)."""

import subprocess
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent


def run(args, cwd: Optional[Path] = None, timeout: float = 15, env: Optional[dict] = None):
    """Run a subprocess, capturing text output. Never raises on nonzero exit."""
    return subprocess.run(
        [str(a) for a in args],
        cwd=str(cwd) if cwd is not None else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def init_git_repo(path: Path) -> None:
    """Initialize a git repo at path with one commit, quietly."""
    run(["git", "init", "-q", "-b", "main"], cwd=path)
    run(["git", "config", "user.email", "test@example.com"], cwd=path)
    run(["git", "config", "user.name", "Test"], cwd=path)
    (path / ".keep").write_text("")
    run(["git", "add", "."], cwd=path)
    run(["git", "commit", "-q", "-m", "initial"], cwd=path)
