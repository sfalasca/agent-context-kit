---
description: How to set up the containerized dev environment once a project stack is chosen
scope: root
covers: [docker, podman, environment, setup, onboarding, containers, monorepo, subprojects]
---

# Setting up the container dev environment

Do not build a placeholder/scaffold container environment speculatively, before a language/stack is
chosen. Once the stack is picked (or if it already exists), build the real `Containerfile`/
`compose.yaml` following this checklist. See [[container-only-development]] for the rule this
implements.

1. **Pick a base image** for the chosen stack, pinned to a specific version (not `latest`).
2. **Write a multi-stage `Containerfile`** (name it `Containerfile`, not `Dockerfile`, so it's
   runtime-neutral — both `docker build` and `podman build` accept either name, but `Containerfile`
   signals intent):
   - A `tools` stage installs everything needed to lint/type-check/statically-analyze/sanitize/test
     the project. This is the single source of truth for those tool versions. Bundle all of these
     tools into this one stage by default. Only split a specific tool into its own extra
     stage/image when it has a genuine hard conflict with the rest (incompatible runtime version,
     needs a different OS/arch for a sanitizer, etc.) — treat that as the exception, not the
     default. Splitting every tool into its own container adds per-tool startup/pull overhead,
     which works against the fail-fast ordering the verification hierarchy depends on.
   - A `checks` stage is `FROM` the `tools` stage, unchanged — stays lean and reproducible, since
     its output is what "working" gets judged by (see [[hierarchical-verification]]).
   - A `dev` stage is also `FROM` the `tools` stage, adding only interactive extras on top (shells,
     debuggers, editor/LSP support). It is *not* a separately provisioned image — building it on
     top of `tools` means dev automatically has every checks tool, at the exact same version, with
     nothing installed twice.
3. **Write a `compose.yaml`** with two services, `dev` and `checks`, built from the two stages above:
   - `dev`: mounts source **read-write**. For humans/agents working interactively — editing, running
     the app, and also running autofix/format commands (`--fix`, `--write`, etc.) using the same
     tool binaries as `checks`. Agents should be told to use fix commands in `dev` whenever a check
     fails for a fixable reason (formatting, simple lint violations), rather than hand-editing to
     satisfy a linter. Default command should drop into a shell; specific tasks are invoked
     explicitly, not baked into the entrypoint.
   - `checks`: mounts source **read-only**. Runs lint, type-check, static analysis, sanitizers,
     tests. The read-only mount is a structural guarantee that a verification run can never mutate
     source, even by accident (e.g. a stray `--fix` flag). Running `fix` is *not* part of the
     verification hierarchy — it never counts as "passing checks." After a `fix` run, re-run
     `checks` to confirm the result actually satisfies the hierarchy before declaring anything
     working.
   - Mount build/test output and any dependency-cache directories (`node_modules`, `.venv`,
     `target/`, etc.) to a location outside the source tree — a separate named volume or a sibling
     host directory — per [[out-of-tree-artifacts]]. Never let either write inside the source mount.

### Mounting and per-worktree isolation

Work happens in git worktrees (see [[git-worktree-oneflow]]), often several at once (different
agents on different worktrees). Containers must not cross worktree boundaries:

- Bind-mount only the **current worktree's own directory** into `dev`/`checks` (e.g. at
  `/workspace`) — never the whole `*-worktrees` parent directory. Since `compose.yaml` is a tracked
  file, every worktree checkout already has its own copy, and a relative bind mount (`.:/workspace`)
  resolves relative to wherever it's invoked from — so running the wrapper script from inside a
  given worktree naturally mounts just that worktree.
- Scope the compose project per worktree (e.g. `COMPOSE_PROJECT_NAME` derived from the worktree
  slug) so each worktree gets its own container instances, not a shared one. Sharing containers
  across worktrees reintroduces exactly the coupling worktrees exist to remove: one agent's hung
  process or resource-heavy check run would affect every other agent's session.
- The dependency-cache volume (package manager caches, not source) *can* be shared across
  worktrees — key it by a hash of the lockfile/manifest rather than by worktree slug, so agents
  aren't each redownloading the same packages, without reintroducing any shared mutable source
  state.
- For rootless Podman (and Docker with user namespace remap), map the container user to the host
  user (`--userns=keep-id` for Podman, or `user: "${UID}:${GID}"` in compose for Docker) so files
  written from inside a container come out owned by the host user, not root.
- Prefer bind-mounting the live tree over copying it into the image/container for either service —
  copying buys isolation that isn't needed for a local dev/verification loop and costs latency,
  which fights the fail-fast goal.

### Multiple projects in one repository

A repository may contain several projects (related or unrelated), with the hierarchy defined by
folder structure. These may need different images. Handle this the same way the `directives` skill
already scopes docs to subsystems — by folder, nearest-wins:

- A subproject that needs its own image gets its own `Containerfile`/`compose.yaml` inside its own
  folder, plus its own `docs/<subproject>/setting-up-container-dev-environment.md` with
  `scope: <subproject-path>` describing anything that deviates from the root checklist. Don't try
  to make one root `compose.yaml` cover every stack in the repo.
- The wrapper script resolves the **nearest** compose file by walking up from the current working
  directory, the same way directive-doc lookup resolves the nearest applicable doc. Running it from
  inside a subproject picks that subproject's environment automatically — no central registry of
  every subproject to maintain.
- Only share a common `tools` base stage across subprojects when they're actually related (same
  stack/toolchain) — a repo-root `tools` stage each subproject's `Containerfile` builds `FROM` avoids
  reinstalling the same linters everywhere. Genuinely unrelated subprojects (different languages)
  just get fully independent `Containerfile`s — don't force a shared base where there's nothing to
  share.
- Tradeoff: nearest-wins means there's no single place listing every image in the repo — discovery
  relies on something like `find . -name Containerfile` rather than a manifest. Accept this unless a
  concrete need for a central registry shows up.

4. **Write a runtime-detecting wrapper script**, e.g. `scripts/dev`, that picks `docker compose` or
   `podman compose`/`podman-compose` depending on what's installed, so nobody has to hardcode one.
   This is the concrete instance of "write a project-specific tool" from [[tools-over-judgment]].
5. **Wire the verification hierarchy through the wrapper**: lint, build, unit tests, static
   analysis/sanitizers, integration tests should each be a command runnable via `scripts/dev <cmd>`,
   in the order defined in [[hierarchical-verification]] — so "does it work" always means "did
   `scripts/dev` run these and pass," never a manual read of the code.
6. **Update this repo's directive docs** if the concrete setup deviates from any assumption made
   here (e.g. a stack that has no viable rootless-Podman story) — flag it rather than silently
   working around it.

Do this work in its own worktree/branch per [[git-worktree-oneflow]], same as any other change.
