---
name: git-operations
description: Safe git operation guidelines. Use when performing any git operations including commits, branching, merging, rebasing, pushing, pull request creation, or any other git-related tasks.
---

# Git Operations Safety Guidelines

## Git Safety Protocol

- NEVER update the git config
- NEVER run destructive git commands (`push --force`, `reset --hard`, `checkout .`, `restore .`, `clean -f`, `branch -D`) unless the user explicitly requests these actions
- NEVER skip hooks (`--no-verify`, `--no-gpg-sign`, etc.) unless the user explicitly requests it
- NEVER force push to `main`/`master`. Warn the user if they request it
- NEVER run `git rebase -i` or `git add -i` since they require interactive input which is not supported
- NEVER use `--no-edit` with `git rebase` commands, as it is not a valid option for git rebase
- NEVER chain git commands with `&&` or `;`. Always run each git command as a separate invocation
  - Chaining makes it impossible for the user to allow/deny individual operations (e.g., a chain containing `git push` forces the user to deny the entire chain)
  - Separate commands make each operation's intent clear and individually controllable
- NEVER use the `-C` option with git commands (e.g., `git -C /some/path ...`). Always `cd` to the target directory first, or use absolute paths in arguments
  - When the user is prompted to allow a `git -C` command and selects "Yes, and don't ask again for similar commands", it adds `Bash(git -C:*)` to `permissions.allow`, which matches ALL git commands — effectively bypassing permission checks for every git operation

## Commit Rules

- Only create commits when explicitly requested by the user. If unclear, ask first
- ALWAYS create NEW commits rather than amending, unless the user explicitly requests amend
  - When a pre-commit hook fails, the commit did NOT happen. Using `--amend` would modify the PREVIOUS commit, which may destroy work. Instead, fix the issue, re-stage, and create a NEW commit
- When staging files, prefer adding specific files by name rather than using `git add -A` or `git add .`, which can accidentally include sensitive files (`.env`, credentials) or large binaries
- NEVER commit files that likely contain secrets (`.env`, `credentials.json`, etc.). Warn the user if they request it

### Commit Message Format

- Follow [Conventional Commits](https://www.conventionalcommits.org/) format: `<type>(<scope>): <description>`
  - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`
  - Scope is optional but recommended (e.g., `feat(auth): add login endpoint`)
  - Description should be concise, imperative mood, lowercase, no period at the end
- For breaking changes, add `!` after type/scope (e.g., `feat(api)!: change response format`) or add `BREAKING CHANGE:` in the body
- Always pass commit messages via a HEREDOC for proper formatting:

```bash
git commit -m "$(cat <<'EOF'
feat(auth): add OAuth2 login support

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Branch Rules

- Check the current branch before making changes
- Prefer creating feature branches from the main branch for new work
- Use descriptive branch names (e.g., `feature/add-auth`, `fix/login-bug`)

## Push Rules

- Do NOT push to the remote repository unless the user explicitly asks
- Always verify the current branch and its remote tracking status before pushing
- Use `git push -u origin <branch>` for new branches

## Pull Request Rules

- Keep the PR title short (under 70 characters)
- Use the PR description/body for details, not the title
- Include a summary section with bullet points
- Include a test plan section
- Use `gh pr create` with a HEREDOC for the body:

```bash
gh pr create --title "the pr title" --body "$(cat <<'EOF'
## Summary
<1-3 bullet points>

## Test plan
[Bulleted checklist of testing steps]
EOF
)"
```

## Merge Conflict Resolution

- Investigate merge conflicts rather than discarding changes
- Try to identify root causes and fix underlying issues rather than bypassing safety checks
- If a lock file exists, investigate what process holds it rather than deleting it

## General Safety

- Before taking any irreversible git action, consider the blast radius and confirm with the user
- If you discover unexpected state (unfamiliar files, branches, or configuration), investigate before deleting or overwriting, as it may represent the user's in-progress work
