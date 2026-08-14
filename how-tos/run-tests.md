---
description: Run this repo's test suite, on the host for a quick pass or in the pinned container for the full suite
scope: root
covers: [testing, tests, unittest, container, docker, podman, ci]
---

# Run the test suite

Every script in this repo is covered by `tests/` (see `tests/test_help_contract.py` for the
`--help` contract enforced on all of them, plus per-skill behavior tests). Some tests need
things a host machine may not have (Node.js) or shouldn't touch directly ($HOME) — those are
container-gated and skipped outside it.

## 1. Quick pass (host, Python only)

Needs Python 3.9+, Git, and `pyyaml` (only for `tests/test_skill_frontmatter.py`'s real YAML
validation of every `SKILL.md`):

```bash
python3 -m unittest discover -s tests -v
```

This runs everything except the container-gated tests below (they report `skipped`, not
`failed` — that's expected and not a problem to chase on the host).

## 2. Full suite (container, includes install verification)

Some tests are unsafe or impossible to run directly on a dev machine:

- `tests/test_npx_skills_install.py` — exercises `npx skills add` end to end (list, project
  scope, global scope), which needs Node.js (not a host requirement otherwise) and network access
  to fetch the `skills` package, and also touches `$HOME` for the global-scope case.

This is gated on `AGENT_CONTEXT_KIT_IN_CONTAINER=1`, set only inside this repo's own container
(see `Containerfile`, `compose.yaml`). Run the same discovery-based suite there instead of
inlining the container invocation by hand — this is what `scripts/dev`, a script in this repo's
own `scripts/` folder, is for:

```bash
python3 scripts/dev test
```

This builds (or rebuilds, if the `Containerfile` changed) the pinned `checks` image — Python
3.12.7 and a real Node 22.20.0 merged in from the official Node image, not Debian bookworm's
apt-packaged Node (too old for the `skills` CLI's `>=22.20` requirement) — and runs the full
`python3 -m unittest discover -s tests -v` inside it, with `/workspace` mounted **read-only** so a
test run can never mutate source.

Requires Docker (with the `compose` plugin) or Podman (with `podman-compose` or the `compose`
plugin) — `scripts/dev` detects whichever is installed, per this repo's own bundled
`container-only-development` directive.

## 3. Confirm before declaring a change "working"

Per this repo's own bundled `hierarchical-verification` directive: a change to any script under
`skills/` or to `scripts/dev` itself is not "done" until step 2 has actually been run
and passed — reasoning about what a script should do, or only running step 1, is not sufficient
when the change could plausibly affect container-only behavior (paths, Node/Python interaction,
`$HOME` handling).
