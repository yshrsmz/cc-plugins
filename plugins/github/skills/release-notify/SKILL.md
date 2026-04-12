---
name: release-notify
description: After a release, comment on related GitHub issues to notify users. Extracts addressed issues from the release changelog or PR, then posts appropriate comments on each. Trigger when the user asks to "notify issues about release", "comment on released issues", or "post release comments".
---

# Release Notify

Post comments on GitHub issues that were addressed in a release.

## Workflow

1. **Identify the release** — Determine the version from:
   - Release-please PR body (`gh pr view <number> --json body`)
   - CHANGELOG.md entries
   - Or ask the user which version

2. **Extract addressed issues** — Parse the changelog/PR for issue references. Categorize each:
   - **Fixed**: Issue is directly resolved (e.g. `Closes #123`, `fix:` commits)
   - **Improved**: Issue may be improved but not fully resolved (e.g. related refactoring)
   - **Unrelated**: Internal changes (deps updates, CI, etc.) — skip these

3. **Draft comments** — For each issue, draft a comment based on its category:

   **Fixed:**
   ```
   Fixed in <version> via #<PR>. <one-line description of the fix>.
   ```

   **Improved:**
   ```
   <version> includes <description of changes> which may help with this issue.
   Please try <version> and let us know if the issue persists.
   ```

4. **Post comments** — Use `gh issue comment <number> --body "<message>"` for each.

5. **Report** — Summarize what was posted.

## Guidelines

- Use past tense for fixed issues ("Fixed in"), present for improved ("includes")
- Do not say "when it's released" if the version is already released
- Skip deps-only updates and internal CI changes
- For issues labeled "need more info", ask the reporter to verify with the new version
- Keep comments concise — 1-3 sentences max
- Do not close issues via comments; let the PR linkage or maintainer handle that
