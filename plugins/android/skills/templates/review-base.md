# Review Base — shared workflow for agent-review and codex-review

Both skills review current Android code changes; only the launch mechanism differs. This file documents the shared steps.

## Why runtime project discovery

These skills ship in the android plugin and run against *any* Android project. Hardcoding one project's architecture (module names, key classes, UI framework) into the prompt would mislead the reviewer when used elsewhere. Discover project context at runtime from the checked-out repo every time — never from memory or plugin-baked assumptions.

## Who runs git?

This matters for how you build the reviewer brief:

- **agent-review**: the bundled architect agents declare `tools: Read, Grep, Glob` — no Bash. *You (the orchestrator) run the git commands and embed the output in the prompt.* The subagent reads files for deeper context using Read / Grep / Glob.
- **codex-review**: Codex runs in a `workspace-write` sandbox and runs git itself. List the commands in the prompt and let it fetch.

## Shared steps

### 1. Verify there's something to review

Run `git status`. If the tree is clean and the branch has no commits ahead of the main branch, tell the user there's nothing to review and stop.

### 2. Gather project context

Minimum — always:
- `pwd`
- Current branch: `git rev-parse --abbrev-ref HEAD`
- Main branch: `git symbolic-ref refs/remotes/origin/HEAD` (falls back to `main` / `master` if unset)

Preferred — read if present and relevant to the changes:
- `CLAUDE.md`, `README.md`, `settings.gradle.kts` / `settings.gradle` for project name, app-vs-library, architecture style, notable modules
- `docs/design-docs/`, `docs/requirements/`, `docs/architecture/`, `build-logic/README.md` only if the diff touches those areas

Include only what you actually found. Don't invent architecture or modules.

### 3. Build the reviewer brief

Keep it compact. The agent already knows Android / Compose / library-design best practices — don't re-teach them. Include:

- **Role** — one sentence on the reviewer's specialization (e.g., "You're an Android Compose / MVVM architect reviewing changes for `<project>`.")
- **Environment / tools** — per "Who runs git?" above
- **Project context** — only the facts you discovered in step 2
- **What to analyze** — the git output (for agent-review) or the git commands to run (for codex-review). See §4.
- **Output format** — the four-bucket format. See §5.

### 4. What to analyze

Collect or list these git commands:

- `git status`, `git diff`, `git diff --cached` — workspace changes
- If the branch is ahead of main: `git log <main>..HEAD --oneline`, `git diff <main>...HEAD --stat`, `git diff <main>...HEAD`

Ask the reviewer to read committed files for fuller context when a small diff touches something complex (architectural consistency, cross-module flows, testing strategy).

### 5. Output format

Findings organized into four buckets, each with file + line citations:

- ✅ done well
- ⚠️ issues to fix
- 💡 suggestions
- 🔴 critical problems

Response starts with a one-line changes summary (files touched, optional commit count).
