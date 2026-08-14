#!/usr/bin/env bash
# Discover all scripts in scripts/ folders in the current project, PLUS this skill's own
# bundled scripts (in a scripts/ folder next to this script) — those are available everywhere
# the scripts skill is available, not just in projects that vendor their own copies.
# Outputs a plain list of paths — no file content.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Skill-bundled scripts ==="
if [[ -d "$SKILL_DIR/scripts" ]]; then
  find "$SKILL_DIR/scripts" -type f | sort
else
  echo "(none found)"
fi

echo ""
echo "=== Project scripts ==="
found=0
while IFS= read -r -d '' f; do
  echo "$f"
  found=1
done < <(find . \
  \( -path './.git' -o -path './node_modules' \) -prune \
  -o -path '*/scripts/*' -type f -print0 2>/dev/null | sort -z)

if [[ $found -eq 0 ]]; then
  echo "(none found)"
fi
