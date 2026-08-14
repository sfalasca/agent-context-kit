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
  6. LLM-based review (most expensive, used last, as a complement not a replacement for 1-5) — use
     whatever code-review tooling/skill the environment provides for the normal review pass, plus a
     separate pass that checks the change for consistency with this project's directives (see the
     `directives` skill) — a normal code-review pass doesn't know a project's specific conventions,
     so it won't catch a change that works but violates one. If no review tooling is configured, do
     both passes directly rather than skipping this step. If review tooling is normally interactive,
     unattended runs must still apply both passes headlessly rather than skipping this step.
- This ordering exists to get the fastest possible signal on failure — do not run an expensive step
  before a cheap one that would have caught the same class of problem sooner.
- "Working" is never declared from code reading or reasoning alone. A change is only reported as
  done/working after the relevant levels of this hierarchy have actually been run and passed, inside
  a container per [[container-only-development]], using real tools per [[tools-over-judgment]].
- If a project doesn't yet have one of these levels wired up (e.g. no static analysis configured),
  that's a gap to flag or fill (see [[tools-over-judgment]] on writing project-specific tools) — not
  a reason to skip straight to LLM-based review as if it were sufficient.
