---
description: All development work happens inside a container (Docker or Podman); nothing dev-related is installed on the host machine
scope: root
covers: [docker, podman, environment, tooling, setup, dependencies, containers]
---

# Container-only development

- The host machine never gets language runtimes, compilers, linters, package managers, or project
  dependencies installed on it. The only things required on the host are a container runtime
  (Docker or Podman) and Git.
- Every command that builds, runs, tests, lints, or otherwise touches the project executes inside a
  container (`docker run`/`docker compose ...`, or the Podman equivalent — `podman run`/`podman
  compose ...` or `podman-compose`). This includes one-off commands, not just the "real" build.
- Docker and Podman are treated as interchangeable here: use whichever is available/configured for
  this project. Don't hardcode a preference for one over the other in scripts unless the project
  has already standardized on it — prefer detecting/parameterizing the runtime (e.g. a
  `CONTAINER_RUNTIME` variable or a `docker`-vs-`podman` shim) so tooling works with either.
- Podman's rootless, daemonless model is fine and does not need extra permission beyond what Docker
  would need — treat a rootless Podman container the same as a Docker container for this rule.
- If a task needs a new tool or dependency, it goes into the Containerfile/Dockerfile or compose
  config, never `apt-get install`, `pip install`, `npm install -g`, etc. run directly on the host.
- Editors/IDE tooling that only reads files (e.g. an LSP for autocomplete) is not "development" in
  this sense and is out of scope for this rule — the rule is about anything that builds, runs, or
  verifies the project.
- If no container runtime is available in the execution environment, stop and flag it rather than
  falling back to a host install — do not silently violate this rule to make progress.
- Containers must run as the invoking user's UID/GID (e.g. `docker run --user "$(id -u):$(id -g)"`,
  a matching `USER` in the image, or Podman's rootless UID mapping), not as root. This applies to
  anything that writes into a bind-mounted host directory — build output, caches, generated files,
  test artifacts — not just the process's own runtime privileges.
- Containers must not pollute the host filesystem, and especially must not leave root-owned files
  behind. Any file a container writes into a mounted path should end up owned by the invoking user,
  editable and deletable without `sudo`. If a tool insists on writing as root inside the container,
  fix ownership before the run ends (e.g. `chown` back to the host UID/GID) rather than leaving
  root-owned files for the user to clean up.
