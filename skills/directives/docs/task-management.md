---
description: Tasks are tracked as structured markdown files in tasks/ folders, not ad hoc notes or memory
scope: root
covers: [tasks, workflow, tracking]
---

# Task management

Non-trivial work is tracked as a task file, not ad hoc notes or memory:

- **Flat by default**: a task is one file, `tasks/<slug>.md`, with `status`/`created`/`updated`/
  `tags` frontmatter. Most tasks stay this shape.
- **Folder, only once broken into subtasks**: `tasks/<slug>/_task.md` (parent) plus
  `tasks/<slug>/chunk-N-<description>.md` per subtask.
- **No status-based folders** (`active/`, `done/`, etc.) — status lives in frontmatter, not file
  location.
- `tasks/*/state.md` is transient scratch state for resuming interrupted chunked work — not
  committed (see `.gitignore`).
- Before starting non-trivial work, check `tasks/` for an existing relevant file instead of
  starting from scratch; when the work is done, update its `status` (and move on to closing it per
  whatever convention this project already uses for that, if any).

If this environment provides a dedicated task-management skill/tool, use it to create, update, and
close these files consistently instead of hand-editing frontmatter. This doc's conventions above
are what such a tool should produce either way — they hold regardless of whether one is available.
This is a separate concern from [[git-worktree-oneflow]] (which branch/worktree work happens in)
and from the `directives` skill (which conventions apply) — task tracking does not know about or
depend on either.
