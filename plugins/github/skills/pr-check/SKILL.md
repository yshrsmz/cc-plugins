---
name: pr-check
description: >-
  PR のレビューコメントと CI ステータスを確認し、各指摘を独立に評価して修正すべきものは個別コミット・push する。PR 番号を引数に取る。
argument-hint: "[PR number]"
disable-model-invocation: true
---

# PR Check

PR のレビューコメントと CI ステータスを確認し、問題を解決する。

## 1. Identify the PR

If you don't understand which PR you should look into, ask user first.

## 2. Get review comments

Run all of these commands and show their raw output before evaluating anything. Reviews are stored in three separate places, and a comment you never retrieved cannot show up later in the evaluation, so skipping one silently drops findings.

### To get active inline code review comments (excluding minimized):

```bash
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments --paginate --jq '
  [.[] | select(.performed_via_github_app == null or (.performed_via_github_app.name == "GitHub Actions" | not)) | select(has("minimized_reason") | not)]
  | sort_by(.created_at) | reverse
  | .[]
  | "Created: \(.created_at)\nFile: \(.path)\nLine: \(.line // .original_line)\nAuthor: \(.user.login)\nComment: \(.body)\n---"
'
```

### To get active review summaries (excluding minimized):

```bash
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/reviews --paginate --jq '
  [.[] | select((.body // "") != "")]
  | group_by(.user.login)
  | map(sort_by(.submitted_at) | reverse | .[0])
  | sort_by(.submitted_at) | reverse
  | .[]
  | "Submitted: \(.submitted_at)\nReviewer: \(.user.login)\nState: \(.state)\nBody: \(.body)\n---"
'
```

### To get general PR comments:

```bash
gh pr view [PR_NUMBER] --comments
```

### Important filtering rules:

1. **Minimized comments are automatically filtered out** - these are hidden/outdated
2. **Only the LATEST review from each reviewer is shown** - older reviews are ignored
3. **Focus on inline comments for specific actionable issues**
4. **Review summaries provide overall context**
5. **Comments sorted by newest first** - most recent feedback takes priority

### What gets filtered out:

- ✅ Comments with `minimized_reason` field (hidden by GitHub)
- ✅ Old reviews superseded by newer ones from same reviewer
- ✅ Bot comments from GitHub Actions (unless relevant)
- ✅ Empty review bodies

## 2.5. Verify completeness

Before evaluating, complete this checklist and report the results. The counts here are what step 3 is checked against:

### Verification Checklist:

Run these verification commands and report the counts:

```bash
# Count inline comments (non-minimized)
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments --paginate --jq '[.[] | select(has("minimized_reason") | not)] | length'

# List all reviewers who left inline comments
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments --paginate --jq '[.[] | select(has("minimized_reason") | not) | .user.login] | unique'

# Count review summaries
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/reviews --paginate --jq '[.[] | select((.body // "") != "")] | group_by(.user.login) | length'

# List all reviewers who left review summaries
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/reviews --paginate --jq '[.[] | select((.body // "") != "") | .user.login] | unique'
```

### Report format

Create a summary table like this before evaluating:

```
## Comment Retrieval Verification

### Inline Comments Retrieved:
- Total count: X comments
- Reviewers: [list all reviewer names including bots]
- Breakdown by reviewer:
  - Copilot: X comments
  - user1: X comments
  - etc.

### Review Summaries Retrieved:
- Total count: X reviews
- Reviewers: [list all]

### Cross-check with review summaries:
- Review summary claimed: "X comments" ✅/❌ Matches actual count
- All reviewers accounted for: ✅/❌

### Verification Status:
- [ ] Retrieved all inline comments
- [ ] Retrieved all review summaries
- [ ] Counted and verified comment counts
- [ ] Listed all reviewers (humans AND bots)
- [ ] Cross-checked claimed vs actual comment counts
- [ ] Ready to proceed to evaluation

Move on to evaluation once every checkbox is marked.
```

## 3. Evaluate and prioritize issues

Evaluate every review comment counted in step 2.5 yourself, whatever priority the reviewer gave it. The number of comments you evaluate should match the count from step 2.5 (11 inline comments verified means 11 evaluated); a mismatch means one was dropped.

**IMPORTANT**: The category (🔴 critical, ⚠️ issue, 💡 suggestion) is just a label from the reviewer. Your decision must be based ONLY on:
- Actual impact on code quality
- Actual cost to implement
- Actual alignment with project standards

A "suggestion" with high impact and low cost should be fixed. An "issue" that's actually a false positive should be skipped. **Never defer something simply because it's labeled as a "suggestion".**

**DEFERRAL RULE**: You can ONLY defer a finding when it is **explicitly planned in a future task**. Before deciding to defer:
1. Check the project's task tracking (e.g. `.spec-workflow/specs/*/tasks.md`, `openspec/changes/*/tasks.md`, or open issues) for a pending task that would address the finding
2. If a future task exists, cite the task number or issue number when deferring
3. If NO future task exists, you must either **FIX NOW** or **SKIP** (with justification)
4. "Nice-to-have" items without future tasks should be implemented if cost is low

### For EACH review comment, analyze and report:

1. **What the issue is**: Clearly describe the problem or suggestion
2. **Reviewer's category**: What label was assigned (✅ well done, ⚠️ issue, 💡 suggestion, 🔴 critical)
3. **Your independent assessment** (this determines your decision, NOT the category):
  - Code quality impact (readability, maintainability, correctness)
  - Alignment with project patterns and standards (CLAUDE.md, AGENTS.md)
  - Cost vs benefit (effort required vs value gained)
  - Risk of regression or breaking changes
4. **Future task check** (required for deferral): Is there a pending task that addresses this?
5. **Your decision**: Fix now / Defer to Task X / Skip entirely
6. **Reasoning**: Explain WHY based on the assessment above (never cite the category as a reason)

### Example analysis format:

```
## Review Comment #1: Missing test coverage for error states
- **Category**: 🔴 Critical
- **Impact**: High - ensures error handling works correctly
- **Cost**: Medium - need to add 2-3 test cases
- **Alignment**: Follows the project's testing rules
- **Future task**: No
- **Decision**: ✅ FIX NOW
- **Reasoning**: High impact on correctness, aligns with project standards, reasonable effort

## Review Comment #2: Extract a long function into smaller ones
- **Category**: 💡 Suggestion
- **Impact**: Medium - improves readability and reusability
- **Cost**: Low - straightforward refactoring
- **Alignment**: Matches the project's style rules
- **Future task**: No
- **Decision**: ✅ FIX NOW
- **Reasoning**: Good impact/cost ratio, aligns with project patterns, low cost = do it now

## Review Comment #3: Wire up the missing implementation of an interface
- **Category**: 🔴 Critical
- **Impact**: High - required at runtime
- **Cost**: Low - stub implementation needed
- **Alignment**: Required for runtime
- **Future task**: Yes - task 4.2 "Implement the interface" in the change's tasks.md
- **Decision**: ⏭️ DEFER to task 4.2
- **Reasoning**: Explicitly planned in task 4.2, and nothing calls it until a later task

## Review Comment #4: Use named parameters for Java API call
- **Category**: ⚠️ Issue
- **Impact**: N/A - not applicable to Java interop
- **Cost**: N/A - cannot be implemented
- **Alignment**: Named parameters rule applies to Kotlin code only
- **Future task**: N/A
- **Decision**: ❌ SKIP (False Positive)
- **Reasoning**: Java APIs don't support named parameters; this is expected behavior

## Review Comment #5: Add logging for debugging
- **Category**: 💡 Suggestion
- **Impact**: Medium - helps with production debugging
- **Cost**: Low - add a few debug log calls
- **Alignment**: Good practice for observability
- **Future task**: No
- **Decision**: ✅ FIX NOW
- **Reasoning**: Low cost, practical value, no future task = implement now
```

### Present your analysis BEFORE making changes

After evaluating all comments, present your complete analysis to the user with:
- **Count summary**: "Evaluated X findings: Y critical, Z issues, W suggestions"
- Summary table of all issues with your decisions
- Which fixes you'll implement
- Which you'll defer or skip and why

**Verification before proceeding**:
- Confirm: "I have evaluated all [count] inline comments and [count] review summaries verified in step 2.5"
- If counts don't match, stop and go back to retrieve missing comments

**Then wait for user confirmation before proceeding with fixes.**

## 3.5. Propose preventive updates

For each comment decided **FIX NOW** in step 3, assess whether a project rule / skill / doc update could prevent the same mistake from recurring on future edits.

### Scope

- Only **FIX NOW** comments are considered.
- **SKIP** = false positive, **DEFER** = planned work — neither implies a recurring pattern worth preventing. Exclude both.

### Heuristics for proposing an update

Propose an entry only when **all three** are true:

1. The fix revealed a **non-obvious fact** (config schema, library quirk, framework default, project convention).
2. The same oversight would **plausibly recur** when editing a similar file or pattern.
3. There is a **concise rule** that would have steered the AI away from the mistake.

If any of the three is "no", skip that comment.

### Target files

Pick the location that best matches the nature of the rule:

- `.claude/rules/*.md` — reference knowledge loaded automatically via globs (use when the rule applies to a specific file pattern)
- `.claude/skills/*.md` — workflow / procedure that can be invoked (use when the rule is a multi-step process)
- `CLAUDE.md` — project-wide always-on guidance (use sparingly; only for rules that apply everywhere)
- `AGENTS.md` — agent-specific guidance
- Other project-specific standards files (e.g. `CONTRIBUTING.md`, style guides)

### Proposal table format

Present a table of all proposed entries:

```
## Preventive Update Proposals

| # | Review comment summary | Where to record | What to record | Rationale |
|---|---|---|---|---|
| 1 | Global `TooManyFunctions` bump instead of local suppress | `.claude/rules/detekt.md` (globs `detekt-config.yml`, `**/*ViewModel.kt`) | "Suppress TooManyFunctions locally on ViewModels; don't bump the global threshold" | Prevents future contributors from re-bumping the global config |
```

### Decision flow

Ask the user **per-row** whether to add each proposal, using the same UX as the FIX NOW / DEFER / SKIP decision flow in step 3.

- **ADD** — include this preventive update
- **SKIP** — don't add this entry

Proposed updates MUST be **concise and specific**, not generic best-practice dumps. If the rule cannot be expressed in 1–3 sentences, it is too vague to be useful.

### When no updates are proposed

If no comments meet all three heuristics, report:

```
## Preventive Update Proposals

No preventive updates identified.
```

Then proceed to step 4.

### Commit handling

Approved entries land as **separate commits** scoped `docs(claude): ...` (or the project equivalent, e.g. `docs(rules): ...`). Do NOT bundle preventive updates with code fixes — they belong to different concerns and reviewers may want to evaluate them independently.

## 4. Create commits

Create one commit for each problem you fix, unless the repository's conventions say otherwise.

## 5. Verify changes

Once you finish fixing, run the build, tests, and lint that the project's instructions name (CLAUDE.md, rule files, CI config). For example, in an Android project:

```bash
./gradlew assembleDebug testDebugUnitTest lint
```

## 6. Push changes

When it's ok, commit the fix and push.
