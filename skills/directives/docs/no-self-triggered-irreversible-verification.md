---
description: Never trigger an irreversible or production-affecting action to verify a fix — use read-only checks or a dry run, and stop to ask when neither exists
scope: root
covers: [verification, deploy, production, irreversible, safety, fail-fast]
---

# No self-triggered irreversible verification

- Verifying a fix must never itself be the first real-world execution of an irreversible or
  production-affecting action (a deploy, a publish, a send, a payment, a live redeploy). This rule
  exists because an agent, without it, triggered a live production redeploy on its own specifically
  to check that a fix worked — treating "does this actually work" as license to run the very action
  being fixed, with no one having approved that action itself.
- Prefer, in order: a read-only check against current state (logs, status endpoints, `git log`),
  then a dry-run/staging equivalent of the action, before ever considering the real action itself.
  See [[hierarchical-verification]] for the same cheapest-first ordering applied to test/build/lint
  — this is the same principle applied to actions with real-world side effects instead of to
  automated checks.
- If neither a read-only check nor a dry run can confirm the fix, and the only way to verify is to
  actually trigger the irreversible/production action: stop and treat that as a decision only a
  human can make, the same way this project treats destructive git operations
  (`git push --force`, `git reset --hard`) or a capability grant like
  `--dangerously-skip-permissions` or a Docker socket mount — explain what verification requires and
  why, and let the user decide, rather than proceeding on the assumption that "it's just to verify"
  makes the action safe.
- This applies regardless of confidence in the fix. "I'm confident this will work" is not a
  substitute for the user's own judgment about whether now is the right time to affect production,
  who should be watching when it happens, or whether a rollback plan exists first.
