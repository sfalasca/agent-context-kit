---
description: SKILL.md frontmatter must validate against the open Agent Skills spec; Claude Code-only extensions live under metadata, not as top-level fields
scope: root
covers: [agent-independence, portability, skill-md, frontmatter, agent-skills-spec, claude-code, allowed-tools]
---

# Skill content portability

`SKILL.md` (name + YAML frontmatter + Markdown body, an optional `scripts/`/`references/`/
`assets/` layout) is not a Claude Code invention — it's the open
[Agent Skills specification](https://agentskills.io/specification), and other agents besides
Claude Code read the same file shape. Frontmatter that only a specific client understands, or
that fails strict YAML parsing, breaks that portability even though Claude Code itself tolerates
it.

## Frontmatter: only spec fields at the top level

The spec defines exactly these frontmatter fields — nothing else belongs at the top level:

| Field           | Required | Notes                                                                 |
| --------------- | -------- | ---------------------------------------------------------------------- |
| `name`          | Yes      | 1–64 chars, lowercase alphanumeric + hyphens, no leading/trailing/double hyphen, must equal the parent directory name |
| `description`   | Yes      | 1–1024 chars; say what the skill does *and* when to use it            |
| `license`       | No       | License name or reference to a bundled license file                   |
| `compatibility` | No       | 1–500 chars; environment requirements (runtime, packages, network)    |
| `metadata`      | No       | Map of string → string; the extension point for client-specific data  |
| `allowed-tools` | No       | **Space-separated string**, e.g. `Read Edit Bash(git:*)` — not a comma list, not a YAML list |

Claude Code adds its own fields on top of the spec (`argument-hint`, `context`, and others).
Those are real and useful, but they are not portable — a non-Claude-Code client parsing this
frontmatter has no idea what to do with a top-level `context: fork`. Put them under `metadata`,
namespaced with a `claude-code-` prefix, instead of as top-level keys:

```yaml
---
name: example
description: What this does and when to use it.
allowed-tools: Read Edit Write Bash
metadata:
  claude-code-argument-hint: <mode> [path] ["intent"]
  claude-code-context: fork
---
```

A client that doesn't understand `metadata.claude-code-*` simply ignores it — that's the whole
point of the field. A client that doesn't understand a stray top-level `context:` key has no such
guarantee.

## `description` must survive real YAML parsing

Every frontmatter value is YAML, not a loosely-scanned string — a colon followed by a space
inside an unquoted scalar (`description: Modes: add, update.`) is a nested-mapping indicator to a
real YAML parser, not literal text, and breaks strict parsing even though Claude Code's own
lenient extractor tolerates it. Wrap any frontmatter value containing `: ` in double quotes.
Validate with a real YAML library before committing, not by eyeballing it — this repo's `tests/`
does this for every `SKILL.md` in `skills/`.

## `compatibility`, not silent assumptions

If a skill's instructions only work as documented inside Claude Code (slash-command dispatch
like `/directives ...`, cross-skill invocation via the `Skill` tool), say so in `compatibility` —
e.g. "Slash-command dispatch and cross-skill invocation via the Skill tool are Claude Code
conventions; other agents can still follow these instructions and run the bundled scripts
directly." Don't just assume every reader is Claude Code.

## Body content and bundled scripts

- Prefer instructions phrased generically ("run `<script>`") over Claude-tool-specific phrasing
  ("use the Bash tool to run `<script>`") where both convey the same thing — a human or another
  agent reading the file directly gets the same information either way.
- Runtime scripts a skill depends on go in a `scripts/` subfolder per the spec's recommended
  layout — the spec makes no distinction between "a skill's own implementation code" and "example
  automation the skill happens to also document as directly runnable"; both are just executable
  code the skill ships, so both belong in `scripts/`. Don't invent a second, undocumented location
  for "this skill's own scripts" as distinct from its `scripts/` folder.
- See [[os-independence]] for the runtime-portability half of this (Python, no bash, no hardcoded
  paths) — this doc covers the packaging/content half.
