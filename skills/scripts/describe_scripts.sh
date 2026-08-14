#!/usr/bin/env bash
# For each script — project scripts AND this skill's own bundled scripts — run `--help` and
# print its output. This is the authoritative metadata source (not a comment header) — every
# script is required to implement --help properly: fast, side-effect-free, exit 0. A timeout
# guards against a script that doesn't honor that.
# Also prints an optional "# tags:" header line if present, to help cheap keyword pre-filtering.

set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

found=0

describe_one() {
  local f="$1"
  echo "$f"

  if [[ "$(basename "$f")" == "README.md" ]]; then
    echo "  (folder README — authoritative for gotchas/prerequisites/conventions --help won't cover)"
    while IFS= read -r line; do
      echo "  $line"
    done < "$f"
    echo ""
    found=1
    return
  fi

  if [[ ! -x "$f" ]]; then
    echo "  (not executable — skipping --help)"
    echo ""
    found=1
    return
  fi

  local tags
  tags=$(awk '/^# *tags:/ { print; exit }' "$f")
  if [[ -n "$tags" ]]; then
    echo "  $tags"
  fi

  local help_output status
  help_output=$(timeout 5 "$f" --help 2>&1)
  status=$?
  if [[ $status -ne 0 ]]; then
    echo "  (--help failed with exit code $status — this script violates the --help requirement)"
  elif [[ -z "$help_output" ]]; then
    echo "  (--help produced no output — this script violates the --help requirement)"
  else
    while IFS= read -r line; do
      echo "  $line"
    done <<< "$help_output"
  fi
  echo ""
  found=1
}

if [[ -d "$SKILL_DIR/scripts" ]]; then
  while IFS= read -r -d '' f; do
    describe_one "$f"
  done < <(find "$SKILL_DIR/scripts" -type f -print0 | sort -z)
fi

while IFS= read -r -d '' f; do
  describe_one "$f"
done < <(find . \
  \( -path './.git' -o -path './node_modules' \) -prune \
  -o -path '*/scripts/*' -type f -print0 2>/dev/null | sort -z)

if [[ $found -eq 0 ]]; then
  echo "(no scripts found)"
fi
