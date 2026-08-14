---
description: Install must not assume Claude Code or a single fixed install location, and this skill's opinionated bundled directives must be optional per project
scope: root
covers: [install, agent-independence, user-level, project-level, bundled-directives, opt-out, plugin, marketplace]
---

# Install conventions

## Agent-independent, user-level or project-level

Resolved: [`npx skills add`](https://github.com/vercel-labs/skills) is the primary, supported
installer, not a custom rework. It already satisfies every requirement a custom installer would
have needed to grow:

- **No hardcoded client**: it auto-detects installed agents and supports dozens of them (Claude
  Code, Codex, Cursor, OpenCode, and more), each with its own documented skill-directory
  convention — see its supported-agents table. This repo does not need to know or maintain that
  table itself.
- **User-level and project-level**: `-g`/`--global` targets the per-user location
  (`~/.claude/skills/` for Claude Code, the analogous path for other agents); the default targets
  the current project (`.claude/skills/`, committed with the project). Both are first-class, not
  an afterthought.
- **Symlink or copy**: `--copy` is available for agents/platforms where symlinks aren't viable.
- This works because `npx skills add` discovers skills the same way this repo already structures
  them — a `skills/<name>/SKILL.md` per skill, nothing bespoke required on this repo's side.

A second route exists for Claude Code specifically: this repo self-hosts a Claude Code plugin
marketplace (`.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`). Installing via
`/plugin install agent-context-kit@agent-context-kit` namespaces all three skills under the
plugin name (`/agent-context-kit:directives`, etc.) instead of the bare names `npx skills add`
installs under — see [`how-tos/install-skills.md`](../how-tos/install-skills.md). There is no
repo-maintained installer script; both routes are third-party (`npx skills`) or Claude
Code-native (`/plugin`) tooling, not custom code this repo has to keep working across platforms.

## Bundled opinionated directives must be optional

The `directives` skill ships default directive docs (hierarchical verification, out-of-tree
artifacts, tools-over-judgment, etc. — see `skills/directives/docs/`) that apply automatically
to every project the skill is installed into, with no per-project setup. That's the point of
bundling them, but it also means a project that disagrees with one of these defaults needs a real
way to say so — silently editing the bundled copy isn't an option (see the `directives` skill's
own "Skill-bundled default docs" section: `add`/`update` never touch it).

The opt-out is **project-level**: a `.no-bundled-directives` marker file in a project's root.
`discover_docs.py` and `describe_docs.py` skip the bundled-defaults section entirely when this
file is present, regardless of install route (`npx skills add`, symlink or copy, or the plugin
marketplace). This is the mechanism that actually matters for the common case — one shared skill
instance (symlinked or plugin-installed) reused across many projects, where different projects
need to opt out independently of each other and of how the skill itself was installed.
