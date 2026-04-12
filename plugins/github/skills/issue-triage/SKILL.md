---
name: issue-triage
description: Triage open GitHub issues by fetching the full list, investigating each in parallel with subagents, and producing a prioritized summary table grouped by feasibility (HIGH/MEDIUM/LOW). Trigger when the user asks to "triage issues", "check open issues", "review issues", or "what issues can we work on".
---

# Issue Triage

Fetch all open issues for the current repository, investigate each for feasibility, and produce a prioritized summary.

## Workflow

1. **Fetch issues** — Run `gh issue list --state open --limit 50 --json number,title,labels,createdAt,body` to get all open issues. Exclude automated issues (e.g. Renovate Dependency Dashboard).

2. **Group and investigate in parallel** — Group issues into batches of 3-5 by theme (bugs, features, etc.). Launch subagents (subagent_type: Explore) in parallel, one per batch. Each subagent should:
   - Read relevant source files to assess feasibility
   - Determine difficulty (LOW / MEDIUM / HIGH)
   - Identify key files that would need changes
   - Summarize what the fix/implementation would involve

3. **Produce summary table** — Aggregate results into tables grouped by feasibility:

```
### HIGH feasibility (easy to fix)
| # | Title | Summary |
|---|-------|---------|

### MEDIUM feasibility
| # | Title | Summary |
|---|-------|---------|

### LOW feasibility / needs more info
| # | Title | Summary |
|---|-------|---------|
```

4. **Recommend next steps** — Suggest which issues to tackle first based on impact and difficulty.

## Guidelines

- Maximum 6 parallel subagents to avoid overwhelming context
- Skip issues labeled "need more info" unless they have enough detail to investigate
- For bug reports, try to identify the root cause in code
- For feature requests, assess scope of changes needed
- Report concisely — each issue summary should be 1-2 sentences
