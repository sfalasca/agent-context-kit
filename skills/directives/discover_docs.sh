#!/usr/bin/env bash
# Discover all directive docs and CLAUDE.md in the current project, PLUS this skill's own
# bundled default docs (in a docs/ folder next to this script) — those apply everywhere the
# directives skill is available, not just in projects that vendor their own copies.
# Outputs a plain structured list — no file content.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== CLAUDE.md ==="
if [[ -f "./CLAUDE.md" ]]; then
  echo "./CLAUDE.md"
else
  echo "(none found)"
fi

echo ""
echo "=== Skill-bundled docs (read-only defaults; add/update never target these) ==="
if [[ -d "$SKILL_DIR/docs" ]]; then
  find "$SKILL_DIR/docs" -type f -name '*.md' | sort
else
  echo "(none found)"
fi

echo ""
echo "=== Project docs ==="
found=0
while IFS= read -r -d '' f; do
  echo "$f"
  found=1
done < <(find . \
  \( -path './.git' -o -path './node_modules' \) -prune \
  -o -path '*/docs/*.md' -print0 2>/dev/null | sort -z)

if [[ $found -eq 0 ]]; then
  echo "(none found)"
fi
