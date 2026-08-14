---
description: Prefer running real tools (linters, static analyzers, sanitizers, tests) over LLM judgment, and write project-specific tools when none exist
scope: root
covers: [tooling, linting, static-analysis, sanitizers, scripts, verification]
---

# Prefer running code over LLM judgment

- Whenever a question can be answered by running something deterministic — a compiler, linter, type
  checker, static analyzer, sanitizer, formatter, test — run it. Do not answer by reading code and
  reasoning about whether it's correct/safe/well-formatted when a tool can just check.
- Before writing a new script or tool, or doing something manually that could be scripted, run
  `/scripts context "<task description>"` to check whether one already exists. Prefer running an
  existing script over reimplementing the same logic inline.
- This applies recursively: if the same kind of manual check would plausibly be needed again and
  `/scripts context` found nothing, use `/scripts add <path> "<intent>"` to scaffold it properly (in
  a `scripts/`/`tools/` directory, run via the project's container runtime per
  [[container-only-development]]) rather than writing it ad hoc or repeating the manual process by
  hand each time.
- Any script written this way must implement `--help` properly (fast, side-effect-free, exits `0`,
  real description/usage) — this is what makes it discoverable by `/scripts context` later, not
  just usable now. See the `scripts` skill for the exact requirement.
- LLM-based review is a complement for things tools genuinely cannot check (intent, naming quality,
  architectural fit) — not a substitute for a tool that already exists or could easily be written.
