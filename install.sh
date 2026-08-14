#!/usr/bin/env bash
# tags: [install, setup, claude-code, skills]
#
# Installs this repo's skills (directives, how-tos, scripts) into a Claude Code skills
# directory by symlinking each skill folder in. Symlinks (not copies) so `git pull` in this
# repo picks up updates immediately, with no re-install step.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_TARGET="$HOME/.claude/skills"

print_help() {
  cat <<EOF
install.sh - symlink this repo's skills into a Claude Code skills directory.

Usage:
  install.sh [target-skills-dir] [--copy]

Arguments:
  target-skills-dir   Where to install (default: $DEFAULT_TARGET).

Options:
  --copy    Copy the skill folders instead of symlinking them. Use this if you want an
            independent snapshot that won't change when this repo is updated.
  --help    Show this help and exit (safe to run anywhere, no side effects).

What it does:
  For each skill in $REPO_DIR/skills/ (directives, how-tos, scripts), creates
  <target>/<skill-name> pointing at (or copied from) this repo's copy. Skips any skill
  that's already present at the target, rather than overwriting it.
EOF
}

COPY=0
TARGET="$DEFAULT_TARGET"
for arg in "$@"; do
  case "$arg" in
    --help) print_help; exit 0 ;;
    --copy) COPY=1 ;;
    *) TARGET="$arg" ;;
  esac
done

mkdir -p "$TARGET"

for skill_dir in "$REPO_DIR"/skills/*/; do
  skill_name="$(basename "$skill_dir")"
  dest="$TARGET/$skill_name"

  if [[ -e "$dest" || -L "$dest" ]]; then
    echo "skip: $dest already exists"
    continue
  fi

  if [[ $COPY -eq 1 ]]; then
    cp -r "${skill_dir%/}" "$dest"
    echo "copied $skill_name -> $dest"
  else
    ln -s "${skill_dir%/}" "$dest"
    echo "linked $skill_name -> $dest"
  fi
done

echo ""
echo "Done. Add the CLAUDE.md instruction blocks to a project with:"
echo "  $TARGET/scripts/scripts/sync-into.sh <project-path>"
