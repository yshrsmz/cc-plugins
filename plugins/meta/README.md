# meta

Meta-workflow skills for working with Claude Code and Codex — capturing learnings from sessions, authoring rules, and improving the harness around the model.

## Skills

### `session-review`

Reflects on the current Claude Code or Codex session, identifies legitimate learnings (project gotchas, user preferences, reusable workflows, mis-attributions), classifies each into the right destination (`AGENTS.md` in Codex; `CLAUDE.md`, `.claude/rules/`, or auto-memory in Claude Code; or a host-appropriate new skill), presents the proposals via the host's question tool or chat, and applies the approved changes.

Trigger phrases include "review this session", "今回のセッションを振り返って", "capture learnings", "anything to add to CLAUDE.md?", "何か追加するものは?", or any other session retrospective phrasing.

The skill is opinionated about **not padding** — if the session was routine, it will say so and add nothing.

It is a standalone counterpart to the "Rules/Skills/Memory extraction" step in `task.md` Phase 8 (see [yshrsmz/notes](https://github.com/yshrsmz/notes/blob/main/.claude/commands/task.md)) — same intent, but invocable mid-session without needing the surrounding task workflow.

## Installation

Install via the `yshrsmz-cc-plugins` marketplace:

```
/plugin install meta@yshrsmz-cc-plugins
```

### Codex

```bash
codex plugin marketplace add yshrsmz/cc-plugins
codex plugin add meta@yshrsmz-cc-plugins
```

Select `session-review` from the installed skills or name it explicitly in your request. Both hosts use the same skill files. In Codex, project learnings go to `AGENTS.md` or referenced checked-in guidance, and workflows go to `.agents/skills/<name>/SKILL.md`. If `CLAUDE.md` imports `AGENTS.md`, shared learnings update the imported file. Proposals always require your approval.

## License

Apache-2.0
