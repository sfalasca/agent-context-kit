---
description: Assert contracts (preconditions, invariants, postconditions) defensively at lean interfaces, and fail as close to the error's source as possible
scope: root
covers: [assertions, contracts, defensive-programming, preconditions, postconditions, invariants, error-handling, testing, interfaces, fail-fast]
---

# Defensive programming and assertions

- Fail as fast and as close to the error's source as possible. A violated precondition must be
  caught at (or immediately after) the point of violation — never let it propagate silently into
  unrelated code, where it surfaces later as a confusing failure far from its true cause.
- Every function/interface with a non-trivial contract asserts all three parts of that contract, not
  just preconditions:
  - **preconditions** — what must be true of arguments/state on entry, checked before doing any work
  - **invariants** — what must remain true throughout execution (e.g. class/data-structure
    invariants, loop invariants), checked at points where they could plausibly break
  - **postconditions** — what must be true of the result/state before returning, checked before
    control passes back to the caller
  Asserting only preconditions and skipping invariants/postconditions leaves the back half of the
  contract unverified and is a common way defects slip through.
- Prefer lean, narrow interface contracts: fewer parameters, fewer implicit assumptions, fewer
  hidden dependencies on caller state. A smaller contract is both less likely to be violated and
  cheaper to assert against — there is less surface to check and less that can silently go wrong.
  This is the same pressure toward minimal coupling described in
  [[component-hierarchy-and-discovery]], applied at the level of a single function's signature
  rather than a component's dependency graph.
- Assertions and tests are not competing tools for the same job — split the work:
  - **Tests** verify behavior and logic: given valid inputs, does the code produce the right
    outcome, including across edge cases of valid input.
  - **Assertions** verify contract violations: is invalid input/state rejected, at the point where
    it would otherwise cause harm.
  If a test's entire job is confirming that invalid input or state gets rejected, that is a signal
  the check belongs in the code itself as a permanent assertion, not only in a test. An assertion
  runs at every call site, in every environment, for the life of the code; a test only runs the one
  path it was written to exercise. Move the check into the code and let the test become (if kept at
  all) a thin confirmation that the assertion fires — the enforcement itself must live in the
  contract, not only in test coverage of it.
- This complements [[hierarchical-verification]]: assertions are a fail-fast mechanism at the level
  of a single call, running unconditionally at every invocation, while the verification hierarchy is
  the fail-fast mechanism at the level of a whole change (lint, build, test, ...). Neither replaces
  the other — assertions catch contract violations that a test suite may never exercise, while the
  hierarchy catches classes of problems (style, types, regressions) that assertions don't cover.
