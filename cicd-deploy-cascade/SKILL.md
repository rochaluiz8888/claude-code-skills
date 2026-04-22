---
name: cicd-deploy-cascade
description: >
  Systematic diagnostic + fix procedure for silent CI/CD deploy-skip
  cascades. Use when a deploy step appears to succeed but prod doesn't
  actually receive the change, when a workflow runs without producing
  the intended artifact, or when "push-to-deploy" silently skips.
  Walks a 6-layer cascade (code → paths-filter → skip-tolerance →
  direct-needs → always()+success-gate → upload-filter) so each layer
  is audited explicitly instead of re-discovered piecewise.
argument-hint: [service-name or workflow-file-path]
---

# CI/CD Deploy Cascade — 6-layer diagnostic pattern

You are operating under the deploy-cascade diagnostic procedure.
This skill systematizes the most common cause of "it looked like
it deployed but didn't" failures across GitHub Actions + GCP
Cloud Run + similar pipelines.

## When this skill triggers

- A deploy step reports "success" in the workflow log but prod
  still serves the old revision.
- A workflow run shows the deploy job as "skipped" despite
  relevant paths changing.
- Post-deploy verification (HTTP probe, content-type check, body
  marker) fails with content from the old revision.
- A fix to a deploy job never actually exercises itself on its
  own merge.
- Prod serves a placeholder / default image / pre-build artifact
  that should have been replaced.

## The 6 layers (audit order)

When diagnosing, walk the layers in order. Each has its own root
cause + signature + fix pattern. Stopping at layer N when the
real bug is at layer N+1 means another silent-skip cycle.

### Layer 1 — Code / build artifact

**Question**: does the deploy job itself produce the artifact
that should ship?

**Common failure**: the deploy job assumes an earlier job built
the artifact into a shared filesystem. But GitHub Actions jobs
do NOT share filesystems. An artifact built in
`build-and-test-mobile` is NOT automatically available to
`deploy-mobile` — each job checks out fresh source.

**Fix pattern**: the deploy job must run its own build step, OR
the build job must upload an artifact and the deploy job must
download it via `actions/upload-artifact` + `download-artifact`.

**Signature**: deploy ships a source-only tarball (no build
output) and the target's Dockerfile falls back to a placeholder
stage or an empty directory.

### Layer 2 — Paths-filter inclusion

**Question**: does the paths-filter (e.g., `dorny/paths-filter`)
include the file being edited in the triggering filter?

**Common failure**: a fix to `ci.yml` itself won't trigger any
path-filtered downstream job if `ci.yml` isn't in any of the
filters. The fix looks reviewable but never exercises on merge.

**Fix pattern**: deliberately add `ci.yml` (and any other
workflow / config file whose fix should self-verify) to the
relevant filter. Be precise about scope — adding `ci.yml` to
`backend:` vs `mobile:` decides whether your workflow fix
over-triggers production backend jobs.

**Signature**: workflow merges on main and `detect-changes`
shows `0` in every output bucket; deploy jobs skip; nothing
happens.

### Layer 3 — Skip-cascade tolerance

**Question**: when a `needs:` dependency skips, does the
downstream also skip?

**Common failure**: GitHub Actions' default `success()` check
treats a skipped `needs:` job as not-success, so dependents
skip too. One mobile-only PR → `build-and-test-backend` skips
per paths-filter → `smoke-test` skips (needs both) →
`deploy-mobile` skips (needs smoke-test). Nothing runs.

**Fix pattern**: add `always()` + explicit tolerance to the
intermediate job:

```yaml
if: always()
  && !contains(needs.*.result, 'failure')
  && !contains(needs.*.result, 'cancelled')
  && (needs.build-backend.result == 'success' || needs.build-mobile.result == 'success')
```

The `always()` makes the job evaluate its `if:` even when a
dep skipped; the explicit clauses gate on at-least-one success
+ no-failures.

**Signature**: one narrow-scope PR (only touches mobile files,
or only backend files) silently skips its own deploy job.

### Layer 4 — Direct `needs:` for outputs access

**Question**: does the job list every ancestor job whose
`outputs.*` it references in its `needs:` list?

**Common failure**: `needs.detect-changes.outputs.mobile` returns
empty unless `detect-changes` is in the job's direct `needs:`
list — even if it's a transitive dep via another job. The
condition silently evaluates to empty → the `if:` predicate
becomes false → job skips.

**Fix pattern**: every deploy job that reads
`needs.<job>.outputs.*` must list `<job>` in its direct
`needs:`. Don't rely on transitive needs.

**Signature**: the workflow's topology "looks right" — every
deploy has `needs: smoke-test` — but one deploy skips while
another with identical paths runs.

### Layer 5 — `always()` + explicit `result == 'success'`

**Question**: when an upstream uses `always()` in its own `if:`,
does the downstream explicitly gate on
`needs.<upstream>.result == 'success'`?

**Common failure**: using `always()` in an upstream propagates a
"conditional-gated" status that GitHub evaluates as non-success
for downstream default-success gates — even when the upstream
concluded success. Downstream skips silently.

**Fix pattern**: every downstream of an `always()` upstream must
use:

```yaml
if: always() && ... && needs.<upstream>.result == 'success'
```

Explicit evaluation bypasses the propagation issue.

**Signature**: upstream shows ✅ success; downstream shows
skipped; no error anywhere; no clue.

### Layer 6 — Source-upload filter

**Question**: when deploying via a "build-from-source" action
(`gcloud run deploy --source`, `cloud build submit`, etc.), does
the upload tarball actually include the built artifact?

**Common failure**: `gcloud run deploy --source=./mobile` uses
`./mobile/.gcloudignore` (NOT `.dockerignore`) to filter the
upload tarball. Without a `.gcloudignore`, gcloud falls back to
`.gitignore` — which typically excludes `build/`, `dist/`,
`node_modules/`, etc. The build output is present on the CI
runner but absent from what actually gets uploaded.

**Fix pattern**: create a service-scoped `.gcloudignore` at the
upload root. Mirror your `.dockerignore` pattern; use `!build/`
or `!dist/` negation to un-exclude build outputs that `.gitignore`
excludes.

**Signature**: CI log shows `flutter build web` / `npm run build`
succeeded; `ls build/` on runner shows files; deployed revision
still shows pre-build placeholder.

## Procedure

1. **Start at layer 1**. Verify the deploy job produces its own
   artifact. Don't trust "the build job did it" — jobs don't
   share filesystems.
2. **Walk through layers 2-6 in order**. Don't skip — each
   layer masks the next. Fixing layer 1 alone doesn't help if
   layer 2 prevents the fix from ever running.
3. **For each layer, document the specific signature found** so
   the next person debugging doesn't have to re-discover.
4. **Ship each layer fix in a separate PR** if the scope is big
   enough — each fix validates on its own merge and builds the
   diagnostic trail in `git log`.
5. **Before declaring the pipeline fixed**, do a deliberately
   self-exercising PR: touch both the workflow file AND a file in
   the paths-filter for the target deploy. Watch the full chain
   run end-to-end.

## Post-fix hardening

Once the 6-layer cascade is cleared, add durable guards so the
patterns don't silently re-drift:

- **Paths-filter intent test**: a unit test that parses ci.yml
  and asserts the paths-filter asymmetry you rely on (e.g.,
  `ci.yml IS in mobile:, IS NOT in backend:`). Wire it into a
  CI step so a future edit to ci.yml can't silently flip the
  asymmetry.
- **Post-deploy probe**: every deploy job must end with a
  probe that fetches a known endpoint (HTTP 200, content-type,
  body marker) and fails the job if the response is wrong.
  This catches content-level regressions (e.g., the placeholder
  slipping through) that workflow-success alone can't.
- **Documentation**: write down the 6-layer cascade in your
  `operations.md` equivalent so future CI work walks the full
  diagnostic path instead of re-learning it layer by layer.

## Real-world attribution

This skill was extracted from a 2026-04-21 → 04-22 episode on a
Go + Flutter + Cloud Run + Cloud SQL project where a
placeholder HTML page served at every path of the production
PWA for ~24h before all 6 layers were identified and fixed as 6
separate PRs. Total engineering cost: ~20 hours across
investigation + fixes + verification. Of that, ~4 hours could
have been saved by walking the layers in order instead of
debugging them piecewise.

## Non-goals

This skill does NOT cover:

- Rollback strategy (most failures caught by this cascade should
  be fix-forward, not rolled back).
- Canary or blue-green deployment topology (separate concern).
- Secret-mount regressions (those are a layer-7-adjacent issue
  documented in other skills / operations docs).
- Cloud Build vs GitHub Actions choice (this skill assumes
  whichever one is active; the cascade logic is the same).
