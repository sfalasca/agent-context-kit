---
description: Every script this repo ships or uses to test itself runs unmodified on Linux, macOS, and Windows
scope: root
covers: [os-independence, portability, windows, python, bash, scripts, testing]
---

# OS independence

This repo is published for external use — its scripts run on whatever machine the installing
user has, not just this maintainer's Linux/macOS box.

- Every script a skill invokes at runtime (discovery, description, worktree checks) is plain
  Python 3 stdlib only — no bash, no POSIX-only shebangs, no reliance on `~`
  tilde expansion or Unix-only tools (`awk`, `find -path`, `chmod +x` as an execution
  requirement). Python runs identically via `python3 <path>` on Linux, macOS, and Windows;
  bash requires WSL or Git Bash on Windows and simply isn't there by default.
- A script is invoked as `python3 <path-to-script>`, never by relying on the executable bit or a
  shebang line — Windows has no equivalent of either. The executable bit may still be set for
  convenience on POSIX systems, but no invocation instruction may depend on it.
- Path handling uses `pathlib.Path`, not string concatenation with `/`, so paths render correctly
  on Windows too.
- A script's own directory is resolved via `Path(__file__).resolve().parent` (or `.parent.parent`
  for a script nested one level under the skill root in `scripts/`) — never a hardcoded absolute
  path baked into documentation or code. SKILL.md instructions that name a script's location
  describe it as relative to the `SKILL.md` file the agent already read, not as a fixed path like
  `~/.claude/skills/<name>/...` (see [[skill-content-portability]] for why that specific pattern
  matters beyond just OS support).
- This repo doesn't ship its own installer — `npx skills add` and the Claude Code plugin
  marketplace route both handle symlink-vs-copy and Windows fallback themselves (see
  [[install-conventions]]), so this repo has no symlinking code of its own to keep portable.
- This repo's own dev/test tooling (container test harness, `scripts/dev`) follows the same rule:
  no bash-only tooling that a Windows contributor running the containerized checks couldn't also
  run.
- New scripts added to this repo (or to the bundled `directives`/`how-tos`/`scripts` skill
  content) must satisfy this doc before merging — this is what `tests/` enforces automatically
  for the `--help` contract (see [[skill-content-portability]] and the `scripts` skill's own
  `--help` requirement), but cross-platform behavior beyond `--help` still needs a human read.
