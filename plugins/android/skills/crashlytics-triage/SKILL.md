---
name: crashlytics-triage
description: >-
  Investigate Firebase Crashlytics crash reports for an Android app via the Firebase MCP tools: post-release health checks (find new/increased issues since a release, compare against the previous period) and deep dives into a specific crash issue (stack traces, logs, breadcrumbs, suspect commit). Trigger when the user asks to check Crashlytics, "クラッシュ確認して", "クラッシュ増えてない?", asks whether a release introduced new crashes, or wants a specific crash/ANR/non-fatal issue investigated.
---

# Crashlytics Triage

Investigate Crashlytics data for the current Android project. Two modes:

- **Release health check** — "any new or increased crashes since vX.Y.Z?" Compare the window since a release against the prior period, classify issues, and report.
- **Issue deep dive** — "investigate this crash." Pull events for one issue, read stack traces/logs/breadcrumbs, and estimate the causal commit.

## Prerequisites

The Firebase MCP tools (`mcp__*firebase*__crashlytics_*`) must be available. If they are deferred, load everything you need in ONE ToolSearch call:

```
ToolSearch "select:mcp__plugin_firebase_firebase__crashlytics_get_report,mcp__plugin_firebase_firebase__crashlytics_get_issue,mcp__plugin_firebase_firebase__crashlytics_list_events,mcp__plugin_firebase_firebase__crashlytics_batch_get_events"
```

(Adjust the prefix to whatever the connected Firebase MCP server uses.)

If no Firebase MCP server is connected at all, do NOT improvise with REST calls. The android plugin declares a dependency on the `firebase` plugin (from the `firebase` marketplace), but dependency resolution is silently skipped when that marketplace is not registered on the user's machine. Tell the user to run:

```
claude plugin marketplace add firebase/firebase-tools
claude plugin install firebase@firebase
```

then restart the session (or `/reload-plugins`) so the Firebase MCP tools become available.

`crashlytics_get_report`'s own description asks you to read `firebase://guides/crashlytics/reports` first. This skill already covers those prerequisites (exact displayName filters, paired interval timestamps, 90-day limit), so you can skip the guide unless a call fails in a way this skill doesn't explain.

## Step 1: Resolve the App ID

Every Crashlytics call needs a Firebase App ID (`1:NNNN:android:XXXX`).

1. Check project docs/memory first — CLAUDE.md, `.claude/rules/`, or auto-memory often record it.
2. Otherwise resolve it via `firebase_list_apps` / `firebase_get_environment` (load via ToolSearch if needed).
3. Prefer the **release** app (package without a `.debug`/`.dev` suffix). Debug builds have separate, mostly meaningless crash data.

If you had to resolve it via the API, offer to save the ID to project memory so future runs skip this step.

## Step 2: Establish the time window

- "since vX.Y.Z" → get the release date from git: `git log -1 --format='%ci' <tag>` (fall back to the `prepare for release` / version-bump commit if tags are missing). Window = release date → now.
- No version mentioned → default to the last 7 days.
- The API only serves the last 90 days. Always set `intervalStartTime` AND `intervalEndTime` together (ISO 8601).

## Step 3: Pull the data (release health check)

1. **`crashlytics_get_report` report=topVersions** for the window. This gives the exact `displayName` strings (e.g. `2.3.0 (175)`) — filters only accept these verbatim, never construct them yourself. It also shows how far rollout has progressed.
2. **`crashlytics_get_report` report=topIssues** (pageSize 15+) twice:
   - Target window, optionally filtered with `versionDisplayNames` for the release version(s).
   - **Baseline**: an equal-or-longer window immediately before the release, unfiltered. You need this to tell "new" from "pre-existing" and to compare rates. If the response has a `nextPageToken` and a target-window issue has no match in the baseline page, paginate before declaring it new — the match may be below the cut.
3. For each issue note `errorType` (FATAL / ANR / NON_FATAL), `eventsCount` vs `impactedUsersCount` vs `sessionsCount`, `firstSeenVersion`/`lastSeenVersion`, and `signals` (SIGNAL_FRESH / SIGNAL_REGRESSED).

## Step 4: Classify

Sort every notable issue into one of these buckets — the classification is the deliverable:

- **New & real** — `firstSeenVersion` is the new release (or SIGNAL_FRESH) and the stack points at app code or a code path the release touched. FATALs here are the headline.
- **Re-bucketed, not new** — the same underlying error re-appearing under a new issue ID. Two common causes:
  - R8 obfuscation: issues titled with obfuscated names (`fz1`, `hy1` — "X was cancelled" coroutine noise) get new names every release. Match by subtitle/shape, not title.
  - Refactors: the reporting call site moved (class/method renamed), so the old issue's `lastSeenVersion` freezes and a "new" issue appears. Compare per-day event rates old+new vs baseline before calling it an increase.
- **Increased** — existed before, but per-day rate or impacted users clearly up. Always normalize by window length; raw counts across unequal windows mislead.
- **External / low-signal** — crashes inside Play Store, GMS, or ad/consent SDKs with no app frames; single-event issues; events from implausible devices (x86_64 builds of ARM-only phone models, OS versions the model never shipped = emulators/bots). Mention briefly, don't investigate.
- **Fixed / good news** — issues whose `lastSeenVersion` is before the new release, especially ones a recent fix targeted. Confirming a fix landed is as valuable as finding a regression.

## Step 5: Deep dive on the issues that matter

For each new/increased issue worth understanding (and always in issue-deep-dive mode):

1. Fetch the sample: `crashlytics_batch_get_events` with the `sampleEvent` resource name (batch several issues into one call). For more samples or variants, `crashlytics_list_events` with `issueId`, or `crashlytics_get_issue` for issue metadata.
2. Read beyond the stack trace: `logs` (recent logcat), `breadcrumbs` (screen_view trail shows what the user was doing), `device`/`operatingSystem` (emulator? one OEM only?), `processState`.
3. Correlate with the repo:
   - Grep for the crashing class/method to find the code.
   - `git log <prev-release-tag>..<release-tag>` filtered by relevant paths or keywords to find the suspect commit. A `firstSeenVersion` that matches a release containing a related change (dependency bump, migration, refactor of that module) is strong evidence — name the commit in the report.

## Report format

Lead with the verdict, ordered by severity, in prose (not a wall of tables):

1. **New FATALs/ANRs needing action** — what crashes, user impact (users/events), the suspect commit if found, and the Crashlytics console `uri` as a link.
2. **Increased non-fatals** — with the rate comparison that justifies "increased", or the re-bucketing explanation that dismisses it.
3. **Known noise & external** — one or two sentences.
4. **Good news** — fixes confirmed by the data.

Report findings only — don't start fixing code unless asked. Offer to file an issue or start a fix as a follow-up.

## API gotchas

- `versionDisplayNames`, `deviceDisplayNames`, `operatingSystemDisplayNames` must be copied verbatim from a previous API response.
- Issue `title`/`subtitle` may be R8-obfuscated; the sample event's `exceptions` field usually has deobfuscated frames — trust the event, not the issue title.
- `eventsCount` ≫ `impactedUsersCount` means a few users hitting it repeatedly (often a retry loop), which is a different problem than a wide-impact crash. Say which shape it is.
- **Rate limits**: the Crashlytics API has a low per-minute quota — parallel `crashlytics_get_report` calls readily return HTTP 429. Issue report calls sequentially, and on a 429 wait ~30–60s before retrying (if foreground sleep is blocked in your environment, use a background sleep task and wait for its completion). Batch what you can instead: `crashlytics_batch_get_events` takes multiple event names in one call.
