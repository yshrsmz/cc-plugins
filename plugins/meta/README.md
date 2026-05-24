# meta

Meta-workflow skills for working with Claude Code itself — capturing learnings from sessions, authoring rules, and improving the harness around the model.

## Skills

### `session-review`

Reflects on the current Claude Code session, identifies legitimate learnings (project gotchas, user preferences, reusable workflows, mis-attributions), classifies each into the right destination (`CLAUDE.md`, `.claude/rules/`, auto-memory, or a new skill), presents the proposals via `AskUserQuestion`, and applies the approved changes.

Trigger phrases include "review this session", "今回のセッションを振り返って", "capture learnings", "anything to add to CLAUDE.md?", "何か追加するものは?", or any other session retrospective phrasing.

The skill is opinionated about **not padding** — if the session was routine, it will say so and add nothing.

It is a standalone counterpart to the "Rules/Skills/Memory extraction" step in `task.md` Phase 8 (see [yshrsmz/notes](https://github.com/yshrsmz/notes/blob/main/.claude/commands/task.md)) — same intent, but invocable mid-session without needing the surrounding task workflow.

## Installation

Install via the `yshrsmz-cc-plugins` marketplace:

```
/plugin install meta@yshrsmz-cc-plugins
```

## License

Apache-2.0
