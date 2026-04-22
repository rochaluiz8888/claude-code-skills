---
name: per-commit-omnibus
description: >
  Ship cross-cutting multi-dimension work as a per-commit-scoped
  omnibus PR (one branch, one PR, N commits — one per dimension) with
  merge-commit strategy preserving per-commit bisect + revert
  granularity. Strictly dominates both "single squashed commit
  omnibus" and "N micro-PRs". Use when packaging ergonomic
  improvements, refactors, or any set of independent dimensions
  that benefits from review-cycle efficiency AND granular post-merge
  reversibility.
argument-hint: [workstream-name]
---

# Per-commit-scoped omnibus — "Option D" pattern

You are operating under the per-commit-scoped omnibus pattern
(internally called "Option D" from the decision matrix where it
emerged). This is the default PR shape for any cross-cutting
multi-dimension workstream in a mature repo.

## When this skill triggers

Use per-commit-scoped omnibus when you have:

- **N independent improvements** that share a theme (ergonomics,
  refactor, docs bundle, governance tuning) but don't have
  hard ordering constraints between them.
- **Shared review surface** — if each dim needs the same set of
  reviewers / bots, bundling saves N review cycles.
- **Future-bisect + revert concerns** — you want to be able to
  `git bisect` to a specific dim's commit OR
  `git revert <per-dim-sha>` without dropping the other
  dimensions.

## The four options for packaging

| Option | Shape | Review cost | Bisect | Revert granularity |
|---|---|---|---|---|
| A. Single-commit omnibus | 1 PR, 1 commit | 1× | Hard (N surfaces in 1 merge) | Only full revert |
| B. N micro-PRs | N PRs, 1 commit each | N× | Trivial | Surgical revert |
| C. Themed batches | ~3-4 PRs | ~3-4× | Moderate | Per-batch revert |
| **D. Per-commit-scoped omnibus** | **1 PR, N commits, merge-commit strategy** | **1×** | **Trivial (per-commit granularity)** | **Surgical via git revert on the merge commit's individual commits** |

Option D is strictly dominant over A (same review cost, better
bisect + revert) and over B/C (fewer review cycles for same
granularity).

## The critical invariant: MERGE-COMMIT, NOT SQUASH

**Option D degrades to Option A if you squash-merge.** The
per-commit scoping is the entire point — if the merge commit
collapses the N commits into 1, you've lost the bisect +
revert granularity.

When merging:

```bash
# RIGHT — preserves per-commit history via merge-commit
gh pr merge <N> --merge --admin --delete-branch

# Also right — rebase-merge linearizes but preserves per-commit
gh pr merge <N> --rebase --admin --delete-branch

# WRONG — squash collapses everything
gh pr merge <N> --squash --admin --delete-branch
```

Document this explicitly in the PR body with a warning like:

> **IMPORTANT — merge strategy**: this PR MUST be merged with
> merge-commit or rebase-merge, NOT squash. Squashing collapses
> the per-commit scoping that is the entire point of Option D.

## Branch + commit structure

### Branch

One branch per omnibus workstream. Name pattern suggestion:

```
<workstream>/<short-name>
# or with phase suffix if the omnibus is split
<workstream>/<short-name>-phase-N
```

### Commits — one per dimension

Each dimension is one commit. Structured commit messages:

```
feat(<workstream-dXX>): <dimension short name> — <1-line rationale>

<Longer explanation (2-5 paragraphs) of what changed and why.
Name the specific files + specific concerns.>

<If the dim has an identifier in a project registry or roadmap,
cite it here.>
```

Replace `feat` with `fix`, `docs`, `chore`, etc. as appropriate.

### PR body — 14-dim TOC pattern

The PR body should carry a table of contents mapping commit →
dimension → scope. Reviewers can skip to the dims they care
about without scrolling the full diff.

```markdown
## Commits (N per-commit-scoped)

| # | Commit | Dim | Scope |
|---|---|---|---|
| 1 | `abc1234` | **D01** | <1-line scope> |
| 2 | `def5678` | **D02** | <1-line scope> |
...
```

## When to split an omnibus into phases

Some omnibi are too big to fit in one session. Split into
phases:

- **Phase 1**: 3-6 highest-leverage or lowest-risk dims. Ship
  first so CI cycles validate the pattern.
- **Phase 2+**: remaining dims as additional commits on a new
  branch (phase-2 branch), opened as PR #N+1.

The phased version is still Option D internally — each phase
is a per-commit-scoped omnibus.

## Interactions with review bots

- **CodeRabbit**: likely to post one summary per commit. Big
  omnibus = big review summary. Tune via `.coderabbit.yaml` if
  needed.
- **Copilot pull-request-reviewer**: posts per-finding threads.
  A 14-dim omnibus can get 10-30+ threads. Plan for a
  resolution pass.
- **Merge-readiness validation**: if your repo has a 20-pass-
  packet gate, the packet stays single (not 14 packets) — it
  covers all dims.

## Attribution of Option D vs other options

The Option D decision emerged from a comparative analysis
requested by a project owner who wanted detailed pros/cons
before committing to a PR-shape. The final recommendation
inverted from an earlier memory ("P6 = single-commit omnibus")
once the bisect + revert benefit of per-commit scoping was
articulated — at zero extra review cost.

## Non-goals

- **Stacked PRs / graphite-style**: different pattern. Option D
  is one PR with N commits, not N stacked PRs.
- **Atomic commits in general**: good practice but orthogonal.
  Option D specifically addresses the "N dims of the same
  workstream" packaging problem.
- **Trunk-based-dev with feature flags**: different pattern.
  Option D assumes merge-to-main has review gates.

## Real-world attribution

Extracted from a 2026-04 repo where 14 ergonomic improvements
were packaged as Option D across 2 phases (phase-1 shipped 3
dims as 3 commits + 2 follow-up fix commits = 5-commit merge;
phase-2 shipped 10 dims as 10 commits + review fixes = 14-commit
merge). Both phases merged cleanly with merge-commit strategy;
per-commit history preserved in `git log`.
