#!/usr/bin/env bash
# Refuse to proceed if the current directory is the primary checkout rather than an
# isolated git worktree. Run before any mode that writes to how-to docs.
# Exits 0 (silent) if the check passes, or if the current directory isn't a git repo
# at all (nothing to enforce). Exits 1 with a message on stderr if it's the primary
# checkout of a repo that has worktrees set up.

set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

current_toplevel="$(git rev-parse --show-toplevel)"
primary_toplevel="$(git worktree list --porcelain | awk '/^worktree / && !found {print $2; found=1}')"

if [[ "$current_toplevel" == "$primary_toplevel" ]]; then
  echo "error: refusing to mutate how-to docs in the primary checkout ($primary_toplevel)." >&2
  echo "Create/switch to an isolated worktree first (see git-worktree-oneflow), e.g.:" >&2
  echo "  git worktree add ../$(basename "$primary_toplevel")-worktrees/<slug> -b <branch>" >&2
  exit 1
fi
