---
name: cost-conscious-gcp
description: >
  Every spin-up of a billable GCP resource (Cloud SQL clone, Cloud Run
  test service, BigQuery test dataset, GCE test instance, etc.) must
  queue its destroy command in the same session. No idle overnight
  test resources. Use when planning any ad-hoc GCP resource creation,
  especially SQL clones for rehearsal or test instances for load work.
argument-hint: [resource-type]
---

# Cost-conscious GCP — destroy-in-same-session rule

You are operating under the cost-conscious GCP rule. Every
billable GCP resource you spin up for test / rehearsal / one-off
investigation must be destroyed in the same session that created
it, unless the owner explicitly asks to keep it alive for a
time-boxed window.

## Why

Cloud resources bill by wall-clock time, not by work done. A
Cloud SQL clone used for a 15-minute rehearsal costs the same
per hour whether the rehearsal took 15 min or the clone sat
idle for 8 hours afterward. The idle time is waste.

For an alpha project especially:

- **Clones are cheap to recreate.** `gcloud sql instances clone`
  takes ~5-15 min. If you need another rehearsal tomorrow,
  re-clone.
- **Idle clones accumulate.** One "I'll delete it later" clone
  easily becomes three after a busy week.
- **Bill surprises hurt morale.** Alpha teams are cost-sensitive;
  a single unexpected line-item can cost a day of trust.

## Applies to these resource classes

| Resource class | Spin-up tool | Destroy command |
|---|---|---|
| Cloud SQL clone | `gcloud sql instances clone` | `gcloud sql instances delete --quiet` |
| Cloud SQL test instance | `gcloud sql instances create` | same |
| Cloud Run test service | `gcloud run deploy --service=test-*` | `gcloud run services delete` |
| Cloud Run Job (test) | `gcloud run jobs create` | `gcloud run jobs delete` |
| GCE test VM | `gcloud compute instances create` | `gcloud compute instances delete` |
| BigQuery test dataset | `bq mk <dataset>` | `bq rm -r -d <dataset>` |
| GKE test cluster | `gcloud container clusters create` | `gcloud container clusters delete` |
| Dataproc cluster | `gcloud dataproc clusters create` | `gcloud dataproc clusters delete` |
| Artifact Registry test repo | `gcloud artifacts repositories create` | `gcloud artifacts repositories delete` |
| Pub/Sub test topic/sub | `gcloud pubsub topics create` | `gcloud pubsub topics delete` |

## The default pattern

When you spin up a billable resource, queue the destroy in the
SAME session, explicitly:

```bash
# 1. Create the test resource
gcloud sql instances clone insider-db insider-db-upgrade-test --async

# 2. Do the work — run the rehearsal, capture evidence, etc.

# 3. Destroy in the same session
gcloud sql instances delete insider-db-upgrade-test --quiet
```

If the resource has deletion protection, disable it as part of
the destroy step:

```bash
gcloud sql instances patch insider-db-upgrade-test --no-deletion-protection --quiet
gcloud sql instances delete insider-db-upgrade-test --quiet
```

Do NOT write an async destroy with a pop-back trick ("run this
later"). Run it synchronously and confirm it deletes.

## The "keep it alive" exception

Owner may explicitly ask: "Keep that clone alive — I want to
poke at it for a while." Two rules apply:

1. **Time-box it.** Ask "for how long?" and record the
   destroy-by time.
2. **Don't let the window drift.** When the window is up,
   destroy. Do not ask again — execute.

If owner doesn't specify a window, default to 30 minutes OR
the rehearsal's natural end, whichever is shorter.

## Recognizing when the rule is about to be violated

Red-flag phrases in your own planning or owner communication:

- "I'll clean this up later."
- "Keep it around in case we need it."
- "It's small, doesn't cost much."
- "We can delete it tomorrow."
- "Let's keep both alive for comparison."

Each of these is a failed destroy step. When you hear any of
them (in your own planning or the user's), pause and either
execute the destroy now or get an explicit time-box from the
owner.

## Standing audit

Beyond the same-session rule, add a periodic sweep:

- Grep `gcloud sql instances list`, `gcloud run services list`,
  `gcloud compute instances list`, etc. for names matching
  `-test`, `-clone`, `-rehearsal`, `-tmp`, `-wip` suffix.
- For each hit, confirm with owner whether it's still needed;
  if not (default), destroy.
- Runs on a quarterly cadence, OR whenever a billing surprise
  surfaces, OR at any alpha→beta readiness audit.

## Non-goals

This skill does NOT cover:

- Reducing per-resource cost via right-sizing (separate skill).
- Committed-use discount management.
- Autoscaler tuning on production resources.
- Budget-alert workflow configuration.

It is specifically about the ops discipline of "the resource you
create today gets destroyed today."

## Real-world attribution

Extracted from a 2026-04 Go + Flutter + Cloud Run + Cloud SQL
alpha session. Owner flagged the pattern when a Cloud SQL clone
(`insider-db-upgrade-test`) had been correctly destroyed at the
end of its rehearsal — but then explicitly stated the rule as a
standing guardrail: "don't keep insider-db clone alive. We need
to be cost conscious." That converted one-off behavior into a
reusable skill.
