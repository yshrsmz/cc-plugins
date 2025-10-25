# check PR's Review comments and CI status, resolve any issue

## 1. Identify the PR

If you don't understand which PR you should look into, ask user first.

## 2. Get review comments

Get review comments and inline comments using `gh` commands:

### To get general PR comments:

```bash
gh pr view [PR_NUMBER] --comments
```

### To get inline code review comments:

```bash
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments
```

Example: `gh api repos/yshrsmz/omnitweety-android/pulls/300/comments`

### To get review summaries:

```bash
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/reviews
```

### To format inline comments for better readability:

```bash
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments --jq '.[] | "File: \(.path)\nLine: \(.line)\nAuthor: \(.user.login)\nComment: \(.body)\n---"'
```

### Important notes:

- Check comments from copilot, claude and yshrsmz
- For claude, only check its latest comment as it may produce multiple same reviews
- Copilot may comment multiple times on the same issue after updates

## 3. Fix issues

Fix the issue mentioned if you think that's a legitimate review:

- If not, explain in your response why it doesn't need fixing
- **IMPORTANT**: All issues should be considered. Do not skip issues or suggestions just because
  it's minor, optional or low priority
- Some issues may not need code changes (e.g., if they need to remain public for testing)

## 4. Create commits

You MUST create one commit for each problem you fix.

## 5. Verify changes

Check if the build, test and lint succeeds once you finished fixing:

```bash
./gradlew assembleDebug testDebugUnitTest lint
```

## 6. Push changes

When it's ok, commit the fix and push.
