---
description: Automated verification is organized hierarchically to fail fast, and is always run before declaring anything working
scope: root
covers: [verification, testing, linting, static-analysis, ci, fail-fast, review, llm-review]
---

# Hierarchical, fail-fast verification

- Automated verification steps are ordered from cheapest/fastest to most expensive, and run in that
  order, stopping at the first failure rather than running everything unconditionally:
  1. formatting / lint
  2. build / compile / type-check
  3. unit tests
  4. static analysis / sanitizers
  5. integration / end-to-end tests
  6. LLM-based review (most expensive, used last, as a complement not a replacement for 1-5) — the
     `code-review` skill (six lenses: reusability, directive consistency, testability, test
     coverage, breaking changes, code quality) is the concrete tool for this step when one is
     available; it's interactive by design, so unattended runs apply its lenses headlessly instead
     of invoking it directly (see `idle_work`'s own per-task execution for how)
- This ordering exists to get the fastest possible signal on failure — do not run an expensive step
  before a cheap one that would have caught the same class of problem sooner.
- "Working" is never declared from code reading or reasoning alone. A change is only reported as
  done/working after the relevant levels of this hierarchy have actually been run and passed, inside
  a container per [[container-only-development]], using real tools per [[tools-over-judgment]].
- If a project doesn't yet have one of these levels wired up (e.g. no static analysis configured),
  that's a gap to flag or fill (see [[tools-over-judgment]] on writing project-specific tools) — not
  a reason to skip straight to LLM-based review as if it were sufficient.
