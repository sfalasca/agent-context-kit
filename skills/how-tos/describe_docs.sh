#!/usr/bin/env bash
# For each how-to doc, extract and print the frontmatter only. Does NOT read the
# body — keeps context lean. Only treats --- on line 1 as the YAML frontmatter opener.
# No bundled-defaults section — see discover_docs.sh for why.

set -euo pipefail

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

echo "=== How-to docs ==="
while IFS= read -r -d '' f; do
  print_frontmatter "$f"
done < <(find . \
  \( -path './.git' -o -path './node_modules' \) -prune \
  -o -path '*/how-tos/*.md' -print0 2>/dev/null | sort -z)

if [[ $found -eq 0 ]]; then
  echo "(no how-to docs found)"
fi
