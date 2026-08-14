#!/usr/bin/env bash
# tags: [sync, bootstrap, onboarding, claude-md, directives, how-tos]
#
# Seeds a target project's CLAUDE.md with the standard instruction blocks that the
# directives/how-tos skills each document in their own "CLAUDE.md instruction" section.
# Idempotent — safe to re-run.
#
# Does NOT copy any skill code or directive docs into the target project: those are discovered
# automatically by the directives/how-tos/scripts skills wherever they're installed (see each
# skill's "skill-bundled" docs/scripts folder) — there is nothing to vendor per project anymore.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPT_DIR/../.." 2>/dev/null && pwd || true)"

print_help() {
  cat <<'EOF'
sync-into.sh - seed a project's CLAUDE.md and .gitignore with the standard
directives/how-tos instruction blocks. Idempotent (safe to re-run).

Usage:
  sync-into.sh <target-project-path> [--check]

Options:
  --check   Report what is missing without writing anything. Exits 1 if anything is missing,
            0 if the target is already fully synced.
  --help    Show this help and exit (safe to run anywhere, no side effects).

What it does:
  - Ensures <target>/CLAUDE.md contains the "## Directives" block (from the directives skill's
    SKILL.md) and the "## How-Tos" block (from the how-tos skill's SKILL.md). Creates
    CLAUDE.md if it doesn't exist. Blocks already present are left untouched.
EOF
}

for arg in "$@"; do
  if [[ "$arg" == "--help" ]]; then
    print_help
    exit 0
  fi
done

if [[ $# -eq 0 ]]; then
  print_help
  exit 1
fi

TARGET="$1"
CHECK=0
[[ "${2:-}" == "--check" ]] && CHECK=1

if [[ ! -d "$TARGET" ]]; then
  echo "error: target directory does not exist: $TARGET" >&2
  exit 1
fi

# Extract the fenced code block that follows "## CLAUDE.md instruction" in a skill's SKILL.md.
extract_claude_md_block() {
  local skill_md="$1"
  awk '
    /^## CLAUDE\.md instruction/ { found=1; next }
    found && /^```/ { incode = !incode; if (!incode) exit; next }
    found && incode { print }
  ' "$skill_md"
}

missing=0

sync_block() {
  local skill_name="$1"
  local skill_md="$SKILLS_DIR/$skill_name/SKILL.md"
  local claude_md="$TARGET/CLAUDE.md"

  if [[ ! -f "$skill_md" ]]; then
    echo "warning: $skill_name skill not found at $skill_md, skipping" >&2
    return
  fi

  local block
  block="$(extract_claude_md_block "$skill_md")"
  if [[ -z "$block" ]]; then
    echo "warning: no CLAUDE.md instruction block found in $skill_md, skipping" >&2
    return
  fi

  local heading
  heading="$(head -n1 <<< "$block")"

  if [[ -f "$claude_md" ]] && grep -qF "$heading" "$claude_md"; then
    return
  fi

  missing=1
  if [[ $CHECK -eq 1 ]]; then
    echo "would add \"$heading\" block to $claude_md"
    return
  fi

  {
    echo ""
    echo "$block"
  } >> "$claude_md"
  echo "added \"$heading\" block to $claude_md"
}

[[ -f "$TARGET/CLAUDE.md" ]] || { [[ $CHECK -eq 1 ]] && echo "would create $TARGET/CLAUDE.md" || touch "$TARGET/CLAUDE.md"; }

sync_block "directives"
sync_block "how-tos"

if [[ $CHECK -eq 1 && $missing -eq 1 ]]; then
  exit 1
fi
exit 0
