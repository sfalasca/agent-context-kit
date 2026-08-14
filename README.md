# agent-context-kit

[Project page](https://falasca.engineering/agent-context-kit/)

Three [Agent Skills](https://agentskills.io/specification) that give a coding agent persistent,
discoverable context about a codebase, instead of re-deriving it every session. `SKILL.md` is an
open format — these work with any agent that supports it (Claude Code, Codex, Cursor, OpenCode,
and many more; see [the `npx skills` supported-agents list](https://github.com/vercel-labs/skills#supported-agents)),
not just one vendor's product:

- **`directives`** — conventions and standards, stored as markdown files in a project's `docs/`
  folders. "Commits use imperative mood." "Every service runs in a container." Read before any
  task so the agent doesn't have to guess or re-litigate settled decisions.
- **`how-tos`** — step-by-step operational procedures, stored in `how-tos/` folders. "How to cut a
  release." "How to generate an access token." Read before an operational task instead of
  re-figuring it out from scratch or from memory.
- **`scripts`** — discovery for a project's `scripts/` folders, using each script's own `--help`
  output as the source of truth (not a comment header that can drift). Lets an agent find and run
  existing automation instead of reinventing it inline.

The three compose: a `how-to` step that's automatable should point at a `script` instead of
inlining a command; a `directive` about git conventions governs how both `add` and `maintain`
modes commit their own changes. Each skill also ships small discovery/description scripts
(`discover_*.py`, `describe_*.py`) that do cheap metadata extraction — frontmatter for docs,
`--help` output for scripts — so the agent doesn't have to read every file's full body just to
figure out what's relevant to the current task.

## Why this exists

Most of what makes an AI coding agent effective on a real, non-trivial codebase isn't the model —
it's whether the codebase is *legible* to the agent: are conventions written down somewhere the
agent will actually look, are operational procedures documented instead of tribal knowledge, is
existing automation discoverable instead of getting silently reimplemented every session. These
three skills are the minimum mechanism to make that true, ported out of a personal
multi-project workspace where they get exercised daily.

## Requirements

Python 3.9+ and Git on the host — no bash/WSL/Git Bash required, so this works the same on
Linux, macOS, and Windows.

## Install

### Primary: any agent, via `npx skills`

```bash
npx skills add <this-repo-url-or-owner/repo>
```

[`npx skills`](https://github.com/vercel-labs/skills) is the open-ecosystem installer for the
Agent Skills format — it auto-detects which agents you have installed, and supports both global
(`-g`, e.g. `~/.claude/skills/`) and project-scoped (default, e.g. `.claude/skills/`) installs
across dozens of agents, with symlink or `--copy` semantics. Run `npx skills add --help` for the
full option list, or see [`docs/install-conventions.md`](docs/install-conventions.md) for why this
repo doesn't roll its own multi-agent installer.

### Claude Code plugin marketplace

This repo also self-hosts a Claude Code plugin marketplace
([`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)), independent of and prior
to any community-marketplace listing:

```
/plugin marketplace add <owner>/agent-context-kit
/plugin install agent-context-kit@agent-context-kit
```

**Namespacing caveat**: a plugin install bundles all three skills under this repo's plugin name.
Skills installed this way are invoked as `/agent-context-kit:directives`,
`/agent-context-kit:how-tos`, and `/agent-context-kit:scripts` — not the bare `/directives`,
`/how-tos`, `/scripts` names used by the `npx skills add` and manual-clone routes above. Pick one
install route per agent setup; don't mix bare and namespaced expectations.

## Use in a project

Each skill's `SKILL.md` documents an `AGENTS.md` instruction block under a "## AGENTS.md
instruction" heading — copy it into the project's `AGENTS.md` (create the file if it doesn't
exist yet) so the agent proactively calls `context` mode before relevant work, instead of only
using the skill when explicitly asked. `AGENTS.md` is the canonical file, not `CLAUDE.md`; if the
project's agent is Claude Code, give its `CLAUDE.md` a single `@AGENTS.md` import line instead of
duplicating the block.

From there, each skill is invoked by name inside an agent session — for example, as a slash
command in Claude Code (bare name if installed via `npx skills add`/manual clone, namespaced
`/agent-context-kit:<name>` if installed via the plugin marketplace route above):

```
/directives context "add a new API endpoint"
/how-tos context "cut a release"
/scripts context "generate a report"
```

or in `add`/`update`/`maintain`/`suggest` modes to create or audit docs and scripts — see each
skill's `SKILL.md` for the full mode list. Other agents activate a named skill differently; see
your agent's own docs for the exact invocation syntax.

## Bundled default directives

The `directives` skill ships a small set of general-purpose engineering directives in
[`skills/directives/docs/`](skills/directives/docs/) — hierarchical, fail-fast verification;
out-of-tree build artifacts; and preferring real tools over LLM judgment. These apply to any
project the skill is
installed into, with no per-project setup; a project's own `docs/` takes precedence over a bundled
default on the same topic, and a project can opt out of the bundle entirely (see
[`docs/install-conventions.md`](docs/install-conventions.md)). Treat them as a starting point, not
a fixed list — the `directives` skill's own `maintain` mode audits and edits them like any other
directive doc.

## Development

This repo's own conventions (OS independence, Agent Skills spec compliance, install design) live
in [`docs/`](docs/) — read them before changing anything under `skills/`. Operational procedures
for working on this repo itself (running the test suite, installing these skills for local
testing) live in [`how-tos/`](how-tos/) — this repo dogfoods its own `directives`/`how-tos`
skills on itself; its `AGENTS.md` carries both skills' instruction blocks, and its `CLAUDE.md`
just imports it (`@AGENTS.md`). Tests for every script
in this repo live in [`tests/`](tests/); the shipped skills themselves need only Python 3.9+ and
Git, but running the test suite also needs `pyyaml` (frontmatter validation) on the host, or
`python3 scripts/dev test` to run the full suite — including the `npx skills add` tests that need
Node.js and network access and touch `$HOME`, so they only run inside the pinned container — with
no host setup beyond Docker or Podman.

## Author

Written by [Stefano Falasca](https://falasca.engineering), an embedded software consultant
focused on safety-critical systems and agent-ready verification.

## License

MIT — see [LICENSE](LICENSE).

