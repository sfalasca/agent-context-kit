# Pinned base images (this repo's own bundled directive: no `latest`).
FROM node:22.20.0-bookworm-slim AS node-tools

FROM python:3.12.7-slim-bookworm AS tools

# Node/npm/npx: needed to run `npx skills add` (tests/test_npx_skills_install.py) -- merged in
# from the pinned official Node image rather than Debian bookworm's apt package (v18, too old
# for the `skills` CLI's node >=22.20 requirement) or a curl-pipe-bash NodeSource install. Copies
# the whole /usr/local tree (not individual files) so npm/npx's internal relative symlinks stay
# intact; this merges into (does not replace) the existing /usr/local, so Python is untouched.
COPY --from=node-tools /usr/local /usr/local

# git: needed by check_worktree.py's own conventions and its tests.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# PyYAML: used only by tests/test_skill_frontmatter.py to validate SKILL.md frontmatter
# against real YAML parsing, per docs/skill-content-portability.md.
RUN pip install --no-cache-dir --root-user-action=ignore pyyaml==6.0.2

WORKDIR /workspace

FROM tools AS checks
# Runs as a non-root user; compose maps this to the invoking host UID/GID so anything the
# container writes (e.g. under the isolated $HOME below) doesn't come out root-owned.
RUN useradd --create-home --uid 1000 tester
ENV HOME=/home/tester
ENV AGENT_CONTEXT_KIT_IN_CONTAINER=1
USER tester
CMD ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"]

FROM tools AS dev
RUN useradd --create-home --uid 1000 tester
USER tester
CMD ["bash"]
