---
description: Install this repo's skills (directives, how-tos, scripts, context-refactor) into an agent, at user or project scope
scope: root
covers: [install, npx, skills, claude-code, plugin, marketplace, user-level, project-level, setup]
---

# Install these skills into an agent

See `docs/install-conventions.md` for why `npx skills add` is the primary installer.

## 1. Primary path: any agent, via `npx skills`

```bash
npx skills add <this-repo-url-or-owner/repo>
```

Add `-g`/`--global` for a user-level install (available to every project), or omit it for the
default project-scoped install (committed with that project). Add `--copy` if symlinks aren't
viable for your setup. See the full option list:

```bash
npx skills add --help
```

This is discovery-based — it works because this repo already lays skills out as
`skills/<name>/SKILL.md`, nothing repo-specific required. It supports dozens of agents beyond
Claude Code; see [the `npx skills` supported-agents table](https://github.com/vercel-labs/skills#supported-agents)
for the full list and each agent's install path.

## 2. Claude Code plugin marketplace

This repo also self-hosts a Claude Code plugin marketplace at
`.claude-plugin/marketplace.json`:

```
/plugin marketplace add <owner>/agent-context-kit
/plugin install agent-context-kit@agent-context-kit
```

Skills installed this way are namespaced under the plugin name — invoked as
`/agent-context-kit:directives`, `/agent-context-kit:how-tos`, `/agent-context-kit:scripts`,
`/agent-context-kit:context-refactor`, not the bare `/directives`/`/how-tos`/`/scripts`/
`/context-refactor` names the step 1 route uses. Pick one install route per agent setup.

## 3. After installing: wire the `AGENTS.md` reminder blocks

Installing the skills makes them available; it doesn't make an agent proactively call `context`
mode before relevant work. Each of `directives`/`how-tos`/`scripts` documents an instruction block
under a "## AGENTS.md instruction" heading in its own `SKILL.md` — copy that block into the
project's `AGENTS.md` (create the file if it doesn't exist yet). `AGENTS.md` is the canonical
file, not `CLAUDE.md`. If Claude Code is one of the agents in play, also give the project's
`CLAUDE.md` a single `@AGENTS.md` import line (Claude Code resolves that as an include) rather
than duplicating the block — other agents that support the emerging `AGENTS.md` cross-tool
convention read it directly, no import needed. `context-refactor` has no such block — it's invoked
directly when planning a refactor, not gated before every task.

## 4. Verify the install

- `npx skills list` (or `npx skills ls -g` for global) shows what's installed and where, for the
  step 1 route; `/plugin` inside a Claude Code session shows installed plugins for the step 2
  route.
- Confirm each skill's `SKILL.md` is present at the expected path, and that `directives`' bundled
  `docs/` folder came along too (unless you specifically opted out — see
  `docs/install-conventions.md`'s "Bundled opinionated directives must be optional" section).
