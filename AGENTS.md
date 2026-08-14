
## Directives

Before starting any task, run `/directives context "<task description>"` to load the relevant
conventions for that task. Do not proceed without doing this first.

## How-Tos

Before starting an operational task (deploy, generate an access token, compile, rotate
credentials, run a database migration, ...), run `/how-tos context "<task description>"` to load
the relevant procedure. Do not proceed without doing this first.

## Scripts

Before writing a new script or tool, or doing something manually that could be scripted, run
`/scripts context "<task description>"` to check whether one already exists. Prefer running an
existing script over reimplementing the same logic inline.
