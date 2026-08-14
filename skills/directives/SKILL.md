---
name: directives
description: Manage project directive docs in docs/ folders. Use when the user wants to add or update conventions/standards documents, audit the directive system for quality, or find which directives are relevant to a task. Modes: add, update, maintain, context, suggest.
argument-hint: <add|update|maintain|context|suggest> [path] ["intent or task description"]
context: fork
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, Skill
---

You manage a project's directive system — structured markdown files in `docs/` and `**/docs/` folders that encode conventions, standards, and domain knowledge. A single root `CLAUDE.md` tells Claude to use this skill to find relevant directives before doing any work.

## Preflight: worktree isolation

Any mode that writes to directive docs (`add`, `update`, `maintain`'s inline fixes) must not run
directly against the primary checkout. Run this before making any such edit:

```bash
bash ~/.claude/skills/directives/check_worktree.sh
```

If it exits non-zero, stop — do not edit any file. Create or switch to an isolated worktree first
(per the project's git-worktree-oneflow convention), then retry the mode from there. Read-only
modes (`context`, `suggest`'s proposal step) don't need this check.

## Skill-bundled default docs

This skill ships with its own `docs/` folder (next to this file) containing a default set of
directive docs — general engineering conventions (container-only development, out-of-tree
artifacts, git worktrees + OneFlow, tools-over-judgment, hierarchical verification, task
management) that apply to any project, not just one that happens to vendor its own copies.

`discover_docs.sh`/`describe_docs.sh` always include these bundled docs *in addition to* whatever
a project has in its own `docs/` folders — there is nothing to set up per project to benefit from
them. Treat them as read-only defaults: **`add`/`update` only ever create or modify files in the
calling project's own `docs/` folder, never in this skill's bundled `docs/`.** If a bundled default
needs to change, edit it here (in the skill), not by forking a copy into a project.

**Precedence**: when a project's own doc and a bundled default cover the same topic (e.g. both
describe the git integration/merge strategy), the project doc wins — it is the more specific,
deliberately-authored source. Don't silently follow the bundled default if a project doc contradicts
it; flag the contradiction (see `maintain` below) so one of them gets fixed or the project doc
explicitly notes it supersedes the default.

## Directive doc frontmatter

Every directive doc must have YAML frontmatter with exactly these fields:

```yaml
---
description: one-line summary of what this doc covers
scope: root                        # or a subsystem path, e.g. ledger, obsidian-brain
covers: [tag1, tag2, tag3]         # keywords for relevance matching
---
```

## Starting every invocation

Run the discovery script first to understand the project's docs landscape:

```bash
bash ~/.claude/skills/directives/discover_docs.sh
```

## Modes

### `add <path> "<intent>"`

1. Run `check_worktree.sh` (preflight — stop if it fails)
2. Run `discover_docs.sh`
3. Read existing docs in the same folder for tone/format reference
4. Create the new directive doc at `<path>` with correct frontmatter and well-structured content
   - Content should be directive in tone: rules, not descriptions
   - Concise — Claude reads this on every relevant task
5. Ensure root `CLAUDE.md` contains the directives instruction (see below); add it if missing
6. Assess impact and apply codebase changes (see Impact Assessment)

### `update <path> "<intent>"`

1. Run `check_worktree.sh` (preflight — stop if it fails)
2. Run `discover_docs.sh`
3. Read the current doc
4. Update content and amend frontmatter as needed (preserve existing fields, update if stale)
5. Assess impact and apply codebase changes

### `maintain`

A quality audit of the entire directive system. Run `check_worktree.sh` (preflight — stop if it
fails, since this mode fixes things inline), then:

```bash
bash ~/.claude/skills/directives/describe_docs.sh
```

Audit each doc by reading it fully:

- **Frontmatter completeness**: all three fields present and non-empty
- **Description quality**: specific and accurate? Does it reflect what the doc actually says? Rewrite if vague or stale.
- **Covers tags**: accurate and complete? Read the body — are there important topics not represented by any tag? Add missing ones. Remove tags that don't match the content.
- **Scope accuracy**: does the declared scope match where the file lives?
- **Body relevance**: are there sections that contradict current project state, or are clearly outdated? Do NOT silently delete content — flag for human review with a comment or report.
- **Bundled-default conflicts**: for each skill-bundled doc, check whether any project doc covers the same topic (matching `covers` tags is a good starting signal) and whether their guidance actually agrees. Flag any contradiction for human review — do not silently pick a winner.

For root `CLAUDE.md`:
- Check the directives instruction is present; add it if missing

Report a summary: what was changed, what was flagged for human review.

### `context "<task description>"`

Find and return the directives relevant to a task.

1. Run `describe_docs.sh` — frontmatter only, no body
2. Match `covers` tags and `description` text against the task description — be inclusive, not exclusive; err on the side of returning more
3. Read and return the **full content** of matched docs
4. If no docs match, say so clearly — do not fabricate conventions

This mode is intended to be called at the start of any task to replace manual discovery.

### `suggest`

Explore the repository and propose new directive docs that would be useful to add.

1. Run `discover_docs.sh` to see what docs already exist
2. Explore the repository structure:
   - Read `CLAUDE.md` and any existing docs to understand what is already covered
   - Scan top-level directories and their contents (`ls`, `Glob`, `Read` key files like `Makefile`, `pyproject.toml`, `package.json`, CI configs, etc.)
   - Look for undocumented conventions: naming patterns, testing approaches, tooling, deployment steps, data formats, language-specific idioms
3. For each gap found, produce a **proposal** — do not create files yet:
   - Proposed path (e.g. `investments/docs/scraper.md`)
   - One-line description of what it would cover
   - Sample `covers` tags
   - Two or three bullet points of what the directive body would say
4. Present all proposals as a numbered list. Ask the user which ones to create (they can say "all", list numbers, or pick interactively).
5. For each approved proposal, run `add <path> "<intent>"` inline — do not ask for confirmation again.

Focus on gaps where Claude would make wrong decisions without guidance — not on documenting things that are obvious from the code.

---

## CLAUDE.md instruction

The root `CLAUDE.md` should contain this block (add it under a `## Directives` heading if missing):

```
## Directives

Before starting any task, run `/directives context "<task description>"` to load the relevant
conventions for that task. Do not proceed without doing this first.
```

---

## Impact assessment (add / update modes)

Before touching the codebase, estimate scope:

- **Small**: directive only affects naming conventions, comments, formatting, or a clearly bounded set of files (e.g. one module, one subsystem) → apply changes inline; stage for review
- **Large**: directive implies structural changes, touches many files, or introduces new patterns across the whole codebase → branch + chunk

### Git conventions

1. Run `describe_docs.sh` and check for docs with `git` in their `covers` tags
2. If found → read that doc and follow its conventions exactly for branch naming and commits
3. If not found → use these defaults:
   - Branch naming: `add/<description>` for new conventions, `fix/<description>` for corrections
   - Integrate via rebase onto main branch + fast-forward merge; no merge commits
   - Commit messages: imperative mood, subject line under 72 characters, no AI/agent/Claude mentions

### Large refactors

For large changes, apply them incrementally (one coherent chunk per session turn, committing each
as it lands) rather than in one pass. This skill only manages directive docs — tracking the work
itself (task files, resuming interrupted refactors, etc.) is outside its scope; use whatever
task-tracking convention the project has, if any.
