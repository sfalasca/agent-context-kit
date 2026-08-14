---
description: Tasks are tracked as structured markdown files in tasks/ folders, managed via the project-management skill
scope: root
covers: [tasks, project-management, workflow, tracking]
---

# Task management

Non-trivial work is tracked as a task file, managed by the `project-management` skill — not ad hoc
notes or memory. Before starting non-trivial work, run `/project-management context "<task>"` to
check for existing relevant tasks; when done, run `/project-management close <path>`.

- **Flat by default**: a task is one file, `tasks/<slug>.md`, with `status`/`created`/`updated`/
  `tags` frontmatter. Most tasks stay this shape.
- **Folder, only once broken into subtasks**: `tasks/<slug>/_task.md` (parent) plus
  `tasks/<slug>/chunk-N-<description>.md` per subtask.
- **No status-based folders** (`active/`, `done/`, etc.) — status lives in frontmatter, not file
  location.
- `tasks/*/state.md` is transient scratch state for resuming interrupted chunked work — not
  committed (see `.gitignore`).

See the `project-management` skill (`.claude/skills/project-management/SKILL.md`) for the full
frontmatter spec and all modes (`add`, `update`, `status`, `close`, `break`, `maintain`, `suggest`,
`context`). This is a separate concern from [[git-worktree-oneflow]] (which branch/worktree work
happens in) and from the `directives` skill (which conventions apply) — `project-management` does
not know about or depend on either.
