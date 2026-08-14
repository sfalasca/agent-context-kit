#!/usr/bin/env bash
# Discover all how-to docs and CLAUDE.md in the current project.
# Unlike the `directives` skill, this skill ships no bundled defaults — how-tos
# (deploy, generate a token, compile, cut a video, evaluate an agent, ...) are
# inherently project-specific, so there is nothing generic to fall back to.
# Outputs a plain structured list — no file content.

set -euo pipefail

echo "=== CLAUDE.md ==="
if [[ -f "./CLAUDE.md" ]]; then
  echo "./CLAUDE.md"
else
  echo "(none found)"
fi

echo ""
echo "=== How-to docs ==="
found=0
while IFS= read -r -d '' f; do
  echo "$f"
  found=1
done < <(find . \
  \( -path './.git' -o -path './node_modules' \) -prune \
  -o -path '*/how-tos/*.md' -print0 2>/dev/null | sort -z)

if [[ $found -eq 0 ]]; then
  echo "(none found)"
fi
