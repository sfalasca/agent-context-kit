---
description: All work happens in a git worktree, using the OneFlow branching model
scope: root
covers: [git, branching, worktree, workflow, oneflow, merge, release, hotfix]
---

# Git worktrees + OneFlow branching

## Worktrees

- Work is never done directly in the primary checkout. Every unit of work (feature, fix, refactor)
  gets its own `git worktree add` checkout on its own branch.
- Worktrees live in a sibling directory next to the primary checkout, named `<repo>-worktrees/<slug>`
  (e.g. a repo checked out at `/path/to/harness` gets worktrees under
  `/path/to/harness-worktrees/<slug>`), one per branch:
  ```
  git worktree add ../<repo>-worktrees/add-docker-dev-environment -b add/docker-dev-environment
  ```
- Once a branch is merged into `main`, remove its worktree and delete the branch:
  ```
  git worktree remove ../<repo>-worktrees/<slug>
  git branch -d <branch>
  ```
- This is also why build artifacts must stay out-of-tree (see [[out-of-tree-artifacts]]): multiple
  worktrees exist side by side, sharing the same `.git`.

## Branching model: OneFlow

Full reference: https://www.endoflineblog.com/oneflow-a-git-branching-model-and-workflow

Rules as applied in this project:

- There is exactly one permanent, long-lived branch: `main` (or `master`, whichever the repo already
  uses — do not introduce a second permanent branch like `develop`).
- Feature/fix branches are cut from `main`, live in a worktree, and are short-lived.
- Before integrating a feature branch, rebase it onto the current tip of `main`.
- Integrate with `git merge --ff-only` after the rebase — no merge commits, no squash-merging.
  A feature branch that won't fast-forward has not been rebased onto the current tip yet; rebase
  again rather than falling back to a merge commit.
- Release branches (`release/x.y`) are only created when a release needs to stabilize while `main`
  keeps moving — not for every change.
- Hotfixes branch from the release tag, merge back into both `main` and the relevant release branch.
- Releases are marked with tags on `main` (or on the release branch at the point it ships).
- Never rewrite history on `main`. Rebasing is only for feature branches, before they're integrated.
