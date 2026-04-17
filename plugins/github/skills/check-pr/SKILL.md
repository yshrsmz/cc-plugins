---
name: check-pr
description: PR のレビューコメントと CI ステータスを確認し、各指摘を独立に評価して修正すべきものは個別コミット・push する。PR 番号を引数に取る。
argument-hint: "[PR number]"
disable-model-invocation: true
---

# Check PR

PR のレビューコメントと CI ステータスを確認し、問題を解決する。

## 1. Identify the PR

If you don't understand which PR you should look into, ask user first.

## 2. Get review comments - MANDATORY EXECUTION

**CRITICAL**: You MUST actually execute these commands and retrieve ALL comments. Do not skip this step or make assumptions about what comments exist.

**EXECUTION REQUIREMENT**: You MUST run ALL of these commands and display the raw output before proceeding to evaluation.

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
  [.[] | select(has("body") and .body)]
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

## 2.5. Verify completeness - MANDATORY CHECKLIST

**STOP**: Before proceeding to evaluation, you MUST complete this verification checklist and report the results:

### Verification Checklist:

Run these verification commands and report the counts:

```bash
# Count inline comments (non-minimized)
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments --paginate --jq '[.[] | select(has("minimized_reason") | not)] | length'

# List all reviewers who left inline comments
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments --paginate --jq '[.[] | select(has("minimized_reason") | not) | .user.login] | unique'

# Count review summaries
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/reviews --paginate --jq '[.[] | select(has("body") and .body)] | group_by(.user.login) | length'

# List all reviewers who left review summaries
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/reviews --paginate --jq '[.[] | select(has("body") and .body)] | .user.login] | unique'
```

### Report format (MANDATORY):

You MUST create a summary table like this BEFORE evaluation:

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

**DO NOT PROCEED** until all checkboxes are marked.
```

## 3. Evaluate and prioritize issues

**CRITICAL**: You MUST independently evaluate EVERY review comment that was verified in step 2.5, regardless of the reviewer's suggested priority.

**Count verification**: The number of comments you evaluate MUST match the count from step 2.5. If you verified 11 inline comments, you MUST evaluate all 11.

**IMPORTANT**: The category (🔴 critical, ⚠️ issue, 💡 suggestion) is just a label from the reviewer. Your decision must be based ONLY on:
- Actual impact on code quality
- Actual cost to implement
- Actual alignment with project standards

A "suggestion" with high impact and low cost should be fixed. An "issue" that's actually a false positive should be skipped. **Never defer something simply because it's labeled as a "suggestion".**

**DEFERRAL RULE**: You can ONLY defer a finding when it is **explicitly planned in a future task**. Before deciding to defer:
1. Check `.spec-workflow/specs/*/tasks.md` for pending tasks that would address the finding
2. If a future task exists, cite the task number when deferring
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
- **Alignment**: Follows AGENTS.md testing requirements
- **Future task**: No
- **Decision**: ✅ FIX NOW
- **Reasoning**: High impact on correctness, aligns with project standards, reasonable effort

## Review Comment #2: Extract complex composable into separate function
- **Category**: 💡 Suggestion
- **Impact**: Medium - improves readability and reusability
- **Cost**: Low - straightforward refactoring
- **Alignment**: Follows Compose best practices in AGENTS.md
- **Future task**: No
- **Decision**: ✅ FIX NOW
- **Reasoning**: Good impact/cost ratio, aligns with project patterns, low cost = do it now

## Review Comment #3: Add notification helper implementation binding
- **Category**: 🔴 Critical
- **Impact**: High - required for Hilt DI
- **Cost**: Low - stub implementation needed
- **Alignment**: Required for runtime
- **Future task**: Yes - Task 20 "Create ReminderNotificationHelper implementation"
- **Decision**: ⏭️ DEFER to Task 20
- **Reasoning**: Explicitly planned in Task 20, not needed until UI integration (Tasks 27-30)

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
- **Cost**: Low - add a few Timber.d() calls
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
- If counts don't match, STOP and go back to retrieve missing comments

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

You MUST create one commit for each problem you fix.

## 5. Verify changes

Check if the build, test and lint succeeds once you finished fixing:

```bash
./gradlew assembleDebug testDebugUnitTest lint
```

## 6. Push changes

When it's ok, commit the fix and push.
