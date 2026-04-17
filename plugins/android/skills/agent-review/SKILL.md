---
name: agent-review
description: Review uncommitted or branch-local Android code changes via a specialized Task subagent. Defaults to android-compose-architect; override via argument.
disable-model-invocation: true
argument-hint: "[agent-type]"
---

# Agent Review

Review code changes in the current repo by handing them off to a Task subagent.

## Agent selection

Bundled with this plugin:

- **`android-compose-architect`** (default) — Compose / MVVM / Hilt apps. Deep on state management, recomposition, lifecycle.
- **`android-library-architect`** — Android libraries consumed by other apps. Deep on public API, Java interop, thread safety, resource management.

Override via argument. Other useful options: `general-purpose`, `Explore`.

## Workflow

Follow the shared steps in [review-base.md](review-base.md). This skill's specifics:

1. Pick the agent — `$ARGUMENTS` if given, else `android-compose-architect`.
2. Run the shared steps 1–3 (verify, gather context, build brief). Since the architect agents have only `Read, Grep, Glob`, **you run the git commands and embed their output in the prompt**.
3. Spawn via the Task tool:
   - `subagent_type`: the chosen agent
   - `description`: `"Review Android code changes"`
   - `prompt`: the brief from step 2, with git output embedded
4. Pass the reviewer's findings back to the user as-is — they already use the four-bucket format.

## agent-review vs codex-review

- `/agent-review`: runs in this session. No MCP setup; counts against this session's rate limits.
- `/codex-review`: runs in the Codex MCP sandbox. Needs Codex MCP configured; independent rate limits.

Pick whichever is available or cheaper in the moment. Both follow the same workflow.
