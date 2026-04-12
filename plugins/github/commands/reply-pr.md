# Reply to and resolve PR review comments

Reply to review comments with fix details and resolve threads. Run this in the same conversation AFTER `/check-pr` has been executed and fixes have been committed and pushed.

## 1. Identify the PR

If you don't understand which PR you should look into, ask user first.

## 2. Collect check-pr evaluation results from conversation context

Review the conversation history to find the `/check-pr` evaluation results. Extract the following for each evaluated comment:

- **Decision**: FIX NOW / SKIP / DEFER
- **File path and line number**
- **Author**
- **Comment body** (for matching)
- **What was fixed** (for FIX NOW items)
- **Commit hash** that addressed the fix (for FIX NOW items)
- **Skip/Defer reason** (for SKIP/DEFER items)

**CRITICAL**: If `/check-pr` results are NOT found in the current conversation, STOP and ask the user to either:
1. Run `/check-pr` first, or
2. Provide the evaluation details manually

## 3. Fetch review threads with IDs - MANDATORY EXECUTION

You MUST fetch review threads to obtain `comment_id` (for reply API) and `thread_node_id` (for resolve API).

### Fetch review threads via GraphQL:

```bash
gh api graphql --paginate -f query='
  query($owner: String!, $repo: String!, $pr: Int!, $cursor: String) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $pr) {
        reviewThreads(first: 100, after: $cursor) {
          pageInfo { hasNextPage endCursor }
          nodes {
            id
            isResolved
            isOutdated
            comments(first: 1) {
              nodes {
                id
                databaseId
                body
                path
                line
                author { login }
              }
            }
          }
        }
      }
    }
  }
' -f owner='{owner}' -f repo='{repo}' -F pr={PR_NUMBER}
```

### Also fetch inline comments with IDs (for reply API):

```bash
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments --paginate --jq '
  [.[] | select(has("minimized_reason") | not)]
  | .[]
  | {id, node_id, path, line: (.line // .original_line), author: .user.login, body: .body[0:100]}
'
```

## 4. Map evaluation results to threads

For each comment evaluated in `/check-pr`, match it to its corresponding review thread using file path, line number, author, and comment body.

### Present the mapping as a table:

```
## Reply Plan

| # | File | Line | Author | Decision | Commit | Action |
|---|------|------|--------|----------|--------|--------|
| 1 | path/to/file.kt | 42 | reviewer1 | FIX NOW | abc1234 | Reply + Resolve |
| 2 | path/to/file.kt | 100 | reviewer1 | SKIP | - | Reply only |
| 3 | path/to/other.kt | 15 | reviewer2 | DEFER | - | Reply only |
```

### Verify before proceeding:

- [ ] All FIX NOW comments are mapped to a commit hash
- [ ] All threads have valid thread IDs for resolve operations
- [ ] Already-resolved threads are identified (will be skipped)
- [ ] Comment count matches the check-pr evaluation count

**Wait for user confirmation before proceeding.**

## 5. Execute replies and resolve - MANDATORY EXECUTION

Process each comment one at a time based on its decision.

### a. FIX NOW — Reply and resolve:

```bash
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments/{comment_id}/replies \
  -f body='Fixed in {commit_short_hash}.

{1-line summary of what was fixed}'
```

Then resolve the thread:

```bash
gh api graphql -f query='
  mutation($threadId: ID!) {
    resolveReviewThread(input: {threadId: $threadId}) {
      thread { isResolved }
    }
  }
' -f threadId='{thread_node_id}'
```

### b. SKIP — Reply with reason (do NOT resolve):

```bash
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments/{comment_id}/replies \
  -f body='Skipped: {reason why this was skipped}'
```

### c. DEFER — Reply with reason (do NOT resolve):

```bash
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments/{comment_id}/replies \
  -f body='Deferred: {reason and linked task/issue}'
```

### Rules:

- **FIX NOW**: Reply with commit hash and fix summary, then resolve the thread
- **SKIP**: Reply with skip reason. Do NOT resolve — leave for reviewer to close
- **DEFER**: Reply with defer reason and linked task/issue. Do NOT resolve — leave for reviewer to close
- **Already resolved**: Skip entirely (note in summary)
- **Execution order**: Process one comment at a time (reply first, then resolve if FIX NOW)
- **Error handling**: Report failures but continue with remaining comments

## 6. Summary

After all operations complete, present a summary:

```
## Reply & Resolve Summary

- Replied and resolved: X comments (FIX NOW)
- Replied (not resolved): Y comments (SKIP/DEFER)
- Already resolved: Z comments (skipped)
- Failed: W comments (list details if any)
```
