---
name: alpha-fix-forward
description: >
  Alpha-phase failure-handling posture: never roll back. Every failure
  class (data / deploy / migration / backfill / bot-review / schema
  regression) gets a fix-forward response. Backups and prior revisions
  exist only for disaster recovery, not as first-line ops tools. Use
  when something breaks in an alpha-phase project and the reflex is to
  revert — check this skill first.
argument-hint: [incident-or-regression-name]
---

# Alpha fix-forward — universal never-rollback rule

You are operating on an alpha-phase project. The operating
posture for ALL failure modes is **fix-forward**. Do not propose,
execute, or silently apply rollback patterns. When a project is
in alpha, rollback introduces more drift than it resolves.

## Why this rule exists

Alpha has three properties that flip the rollback calculus:

1. **Data is disposable.** Local and alpha databases can be
   reseeded, dropped, and rebuilt freely. Production data that
   the live app manipulates is not yet load-bearing for real
   users or revenue.
2. **Plan decisions are load-bearing.** The master plan,
   architectural choices, and dependency versions were picked
   deliberately and documented. Rolling back one component to
   accommodate a transient data error creates silent drift
   away from a deliberated state.
3. **Fix-forward builds velocity.** Each forward fix adds a
   new durable capability / guard / test. Each rollback is a
   throwaway — it gets you "unstuck" but teaches nothing and
   leaves the project fragile at the same point next time.

## Failure classes covered

This skill applies to all of these, without exception:

| Failure class | Wrong impulse | Right action |
|---|---|---|
| **Dep upgrade surfaces bug** | Downgrade the dep | Forward-fix the code path (cast, adapter, schema tweak) |
| **DB schema mismatch after migration** | Restore from pre-migration backup | Patch schema.sql + apply forward migration |
| **Seed data quirk** | Revert seed version | Adjust seed SQL, reseed, continue |
| **Deploy fails startup** | Swap traffic back to old revision | Fix the config / mount / env var; Cloud Run holds old revision automatically during the window |
| **Post-deploy probe fails** | `gcloud run services update-traffic --to-revisions=<old>=100` | Narrow fix-forward PR addressing the specific probe failure |
| **Backfill/migration Cloud Run Job fails** | Rollback the schema | Investigate the job image, fix, re-run |
| **Bot review hits a snag** | Revert the PR | Resolve the thread or use admin-bypass per the admin-override-audit pattern |
| **Major version upgrade surfaces drift** | Roll back the upgrade | Accept the drift, document the deliberate deviation in an ADR, forward-plan to realign |

## What backups and old revisions ARE for (alpha)

Backups and prior revisions exist for **disaster recovery only**:

- Catastrophic data loss (e.g., accidental `DROP TABLE` on a
  populated live table that no seed can recreate).
- Confirmed security compromise requiring immediate containment
  via known-clean state.
- Irrecoverable corruption where forward schema repair is
  mathematically impossible (rare; requires explicit owner
  authorization before use).

They are NOT for:

- "This deploy is behaving slightly differently than expected —
  let me roll back."
- "CI caught a regression — let me roll the dep."
- "The new revision's metrics dipped — let me swap traffic."
- "Bot review keeps flagging this — let me revert the PR."

Every one of the above gets a fix-forward response instead.

## Alpha→beta transition

This rule is **alpha-specific**. When the project graduates to
beta:

- Data becomes real (users have invested behavior in it).
- User-visible regressions carry cost (churn, trust loss).
- The rollback calculus inverts — in beta, a quick revert may
  be cheaper than a slow forward fix.

At that point, a separate `beta-deploy-strategy` posture takes
over (canary, blue-green, automated rollback on SLO-breach).
Until that transition happens, this alpha rule holds.

## Operational pattern when a failure surfaces

1. **Describe the failure specifically.** Not "the deploy
   broke", but "the post-deploy probe returned HTTP 500 from
   endpoint /api/X with body text Y at timestamp Z".
2. **Identify the minimum forward fix.** The smallest code /
   config / schema / data change that addresses THIS specific
   failure signature.
3. **Ship that fix as a focused PR.** Don't bundle it with
   unrelated work. Don't revert the change that surfaced the
   issue. Don't "temporarily disable" the failing path.
4. **Verify with an automated probe.** If the failure was a
   post-deploy probe, the fix PR should land with the probe
   still gating. Don't disable the probe to "buy time" — the
   probe caught this failure; keep it live.
5. **Document.** If the failure pattern is novel, fold the
   lesson into durable guidance (operations doc, ADR, persistent
   memory). Don't let the next-person hit the same thing.

## Recognizing when the user is about to violate the rule

Watch for these phrases in owner or teammate communication:

- "Let's roll back while we figure this out"
- "Just revert the PR and we'll try again later"
- "Downgrade the dep until we can investigate"
- "Restore from the backup real quick"
- "Swap traffic to the old revision until we fix this"

Respond by naming the skill + quoting the relevant row from
the failure-classes table + proposing a concrete forward fix.
If the owner overrides ("I know, but just do it"), that's an
explicit alpha-rule suspension — document it as a one-off, do
the rollback, and capture why.

## Non-goals

This skill is not a substitute for:

- Actual root-cause analysis (fix-forward requires knowing
  what to fix)
- Post-incident documentation (the forward fix still needs a
  post-mortem)
- Pre-production gates (fix-forward works because something
  else — Cloud Run's startup probe, a post-deploy content
  probe, a smoke-test job — caught the regression before users
  hit it; those gates are what make fix-forward safe)

## Real-world attribution

Extracted from a 2026-04 Go + Flutter + Cloud Run + Cloud SQL
project in active alpha. Owner reinforced the rule twice during
one session (once generically, once on a specific curation-
backfill failure-mode discussion), which motivated turning the
rule from per-session behavior into a durable skill. Prior
version of the rule covered only data/schema; the universal
expansion across all failure classes is the current form.
