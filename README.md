# agent-context-kit

Three [Claude Code](https://claude.com/product/claude-code) skills that give a coding agent
persistent, discoverable context about a codebase, instead of re-deriving it every session:

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
(`discover_*.sh`, `describe_*.sh`) that do cheap metadata extraction — frontmatter for docs,
`--help` output for scripts — so the agent doesn't have to read every file's full body just to
figure out what's relevant to the current task.

## Why this exists

Most of what makes an AI coding agent effective on a real, non-trivial codebase isn't the model —
it's whether the codebase is *legible* to the agent: are conventions written down somewhere the
agent will actually look, are operational procedures documented instead of tribal knowledge, is
existing automation discoverable instead of getting silently reimplemented every session. These
three skills are the minimum mechanism to make that true, ported out of a personal
multi-project workspace where they get exercised daily.

## Install

```bash
git clone <this-repo> agent-context-kit
cd agent-context-kit
./install.sh
```

This symlinks each skill folder into `~/.claude/skills/` (so `git pull` here picks up updates with
no re-install step). Pass a different target directory as the first argument, or `--copy` to copy
instead of symlink. See `./install.sh --help`.

## Use in a project

Each skill's `SKILL.md` documents a `CLAUDE.md` instruction block that tells Claude to consult it
before relevant work. Seed a project with both blocks in one step:

```bash
~/.claude/skills/scripts/scripts/sync-into.sh <path-to-project>
```

Idempotent — safe to re-run, and it leaves existing blocks untouched. Pass `--check` to see what's
missing without writing anything.

From there, each skill is invoked as a slash command inside a Claude Code session:

```
/directives context "add a new API endpoint"
/how-tos context "cut a release"
/scripts context "generate a report"
```

or in `add`/`update`/`maintain`/`suggest` modes to create or audit docs and scripts — see each
skill's `SKILL.md` for the full mode list.

## Bundled default directives

The `directives` skill ships a small set of general-purpose engineering directives in
[`skills/directives/docs/`](skills/directives/docs/) — container-only development, out-of-tree
artifacts, git worktree + OneFlow branching, hierarchical verification, task management,
defensive-programming assertions, and a few more. These apply to any project the skill is
installed into, with no per-project setup; a project's own `docs/` takes precedence over a bundled
default on the same topic. Treat them as a starting point, not a fixed list — the `directives`
skill's own `maintain` mode audits and edits them like any other directive doc.

## Worktree isolation

`directives` and `how-tos` both refuse to write (`add`/`update`/`maintain`'s inline fixes) from a
project's primary git checkout — each ships a `check_worktree.sh` preflight that a skill
invocation runs first, and stops if it's not in an isolated worktree. This exists because a
concurrent agent session mutating docs directly in a shared checkout is exactly the kind of
silent-clobber failure these skills are meant to prevent, not cause. Read-only modes (`context`,
`suggest`'s proposal step) are exempt.

## License

MIT — see [LICENSE](LICENSE).
