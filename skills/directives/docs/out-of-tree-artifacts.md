---
description: Build artifacts and anything derived from source are always produced outside the source tree
scope: root
covers: [build, artifacts, out-of-tree, tooling, tests, worktree]
---

# Out-of-tree build artifacts

- Anything that can be regenerated from the source (compiled binaries, object files, generated code,
  coverage reports, test output, caches, packaged bundles, etc.) is written outside the repository's
  source tree — never interleaved with source files (no `build/` next to `src/`, no `.o`/`.pyc`
  siblings, no `dist/` inside a package directory).
- Configure build systems (CMake, npm/webpack, cargo, tox, etc.) to point their output directory
  outside the repo root — e.g. a sibling directory or a path mounted from outside the tree — rather
  than relying solely on `.gitignore`. `.gitignore` protects commits; it does not protect a
  checked-out working tree from getting polluted.
- This matters especially in setups with multiple concurrent checkouts of the same repo (e.g. git
  worktrees): in-tree artifacts either get duplicated per-checkout or leak across them, both wrong.
- When adding a new build/test tool, check where it writes output by default and redirect it
  explicitly if it defaults to writing inside the tree.
