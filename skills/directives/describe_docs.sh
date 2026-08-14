#!/usr/bin/env bash
# For each directive doc — project docs AND this skill's own bundled default docs — extract and
# print the frontmatter only. Does NOT read the body — keeps context lean.
# Only treats --- on line 1 as the YAML frontmatter opener.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

found=0

print_frontmatter() {
  local f="$1"
  local frontmatter
  frontmatter=$(awk '
    NR == 1 { if ($0 != "---") exit; next }
    /^---$/ { exit }
    { print }
  ' "$f")

  echo "$f"
  if [[ -n "$frontmatter" ]]; then
    while IFS= read -r line; do
      echo "  $line"
    done <<< "$frontmatter"
  else
    echo "  (no frontmatter)"
  fi
  echo ""
  found=1
}

echo "=== Skill-bundled docs (generic defaults; a project doc on the same topic takes precedence) ==="
if [[ -d "$SKILL_DIR/docs" ]]; then
  while IFS= read -r -d '' f; do
    print_frontmatter "$f"
  done < <(find "$SKILL_DIR/docs" -type f -name '*.md' -print0 | sort -z)
fi

echo "=== Project docs (override bundled defaults on the same topic) ==="
while IFS= read -r -d '' f; do
  print_frontmatter "$f"
done < <(find . \
  \( -path './.git' -o -path './node_modules' \) -prune \
  -o -path '*/docs/*.md' -print0 2>/dev/null | sort -z)

if [[ $found -eq 0 ]]; then
  echo "(no directive docs found)"
fi
