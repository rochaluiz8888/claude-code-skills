---
name: leverage-before-severity
description: >
  Default severity ordering (CRITICAL → HIGH → MEDIUM → LOW) is a
  heuristic, not a hard invariant. When a lower-severity PR is pure
  process / tooling improvement AND has measurable multiplier effects
  on the review-cycle cost of subsequent higher-severity PRs, it can
  ship first. Use when sequencing a queue that mixes product / doc
  work with tooling / governance improvements.
argument-hint: [queue-name]
---

# Leverage-before-severity — sequencing override

You are operating under the leverage-before-severity rule. The
usual severity ordering (CRITICAL → HIGH → MEDIUM → LOW) is a
default heuristic. When a lower-severity item has multiplier
effects on the review-cycle cost of subsequent higher-severity
items, the lower can ship first — IF the gain is quantifiable
AND the severity delta doesn't include active prod drift.

## When to invoke this skill

Watch for this specific shape in your queue:

- A **product / doc** PR is next by severity (e.g., MEDIUM
  compliance doc bundle).
- A **tooling / process / governance** PR is lower-severity
  (e.g., LOW bucket — PR-template improvements, CI-gate
  ergonomics, bot-review cadence tuning).
- The tooling PR measurably **cheapens the review cycle** for
  the product PR (e.g., heading-tolerance fix on a merge-
  readiness guard, PR-template auto-scaffolding, paths-filter
  intent test, dependabot grouping).

Without the swap: the product PR ships via the current clunky
flow. With the swap: the product PR benefits from the improved
flow. Each improvement compounds across every subsequent PR.

## Quantifying the leverage

To swap, you must be able to **name the specific savings**:

- "Dim X saves ~5 min per protected-surface PR via auto-
  scaffolding (verified against recent cycle times)."
- "Dim Y prevents the N-retries-per-PR pattern we hit on
  PRs #A, #B, #C."
- "Dim Z removes the bot-stall class of blocker that delayed
  #D by 30 min."

If you can't quantify the savings, don't swap. Default to
severity ordering.

## When NOT to swap

Keep severity ordering when:

- **Active prod drift** at the higher severity (HIGH row
  blocking actual deploys, active security incident, etc.).
  Tooling can wait; active damage can't.
- **Tooling PR spans many sessions** (stale-branch-rot risk
  during review cycles negates the compounding gain).
- **Savings are speculative** (the tooling PR might help, but
  evidence is thin).
- **Severity heuristic is load-bearing for audit reasons** —
  some compliance frameworks require you to document why a
  lower-priority item preceded a higher one. Even if you swap
  for real leverage reasons, the deviation needs documentation.

## The standard swap pattern

1. **Recognize the queue shape**: product PR next by severity,
   tooling PR adjacent with multiplier effects.
2. **Write a short comparison table**: for each proposed
   tooling dim, name the specific cycle-cost savings on the
   upcoming product PR.
3. **Surface to the owner**: this is a sequencing deviation from
   the default. Don't swap silently. A 5-row table like
   "dim / savings / subject-PR-count" is usually enough.
4. **On owner approval**: ship the tooling PR first, then the
   product PR. The product PR's body should note "ships under
   the improved tooling per <owner-decision-date>."
5. **Capture the pattern as memory / ADR** if the swap repeats
   across workstreams — it's a durable project posture, not a
   one-off.

## Anti-patterns

- Swapping because you "want to do the tooling first" (aesthetic
  preference, not measured leverage).
- Swapping when the tooling PR hasn't been scoped yet (the
  leverage is just speculation).
- Bundling tooling into the product PR (defeats per-PR
  scoping + bisect granularity — see `per-commit-omnibus` skill
  for the right alternative).
- Letting the tooling PR expand beyond its minimum viable shape
  (if it grows 3x, the review-cycle savings disappear and you
  just delayed the product PR).

## Relationship to other skills

- **`per-commit-omnibus`**: how to package the tooling PR if it
  has multiple independent dims.
- **`alpha-fix-forward`**: applies to the product PR's failure
  handling, not the sequencing decision.
- Severity-ordering default: keep in your mental model as the
  starting point; only deviate with measurable justification.

## Real-world attribution

Extracted from a 2026-04 session where a 14-dim governance-
tooling omnibus (P6) was sequenced BEFORE a 9-doc compliance
bundle (P4), despite P4 being MEDIUM and P6 being LOW. Savings
quantified on 2 specific dims:

- Heading-tolerance on the merge-readiness guard: saved ~1
  full review cycle on the following PR (which had used a
  synonym heading and would have failed otherwise).
- PR-template 20-pass scaffolding: saved ~3-5 min of hand-
  typing per protected-surface PR × 9 docs = ~30-45 min net.

Plus `manual/**` linkcheck validation landing before the
doc-heavy PR so cross-ref rot gets caught at merge time.

Owner explicitly approved the swap after a comparison table was
surfaced. Captured the pattern as a memory entry so future
sequencing decisions have the rule written down.
