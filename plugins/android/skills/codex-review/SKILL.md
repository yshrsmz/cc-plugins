---
name: codex-review
description: Review uncommitted or branch-local Android code changes via the Codex MCP server. Independent execution environment with its own rate limits.
disable-model-invocation: true
---

# Codex Review

Review code changes in the current repo by handing them off to Codex MCP.

## Workflow

Follow the shared steps in [review-base.md](review-base.md). This skill's specifics:

1. Run the shared steps 1–3 (verify, gather context, build brief). Codex has `workspace-write` sandbox access, so **list the git commands in the prompt and let Codex run them** — you don't need to embed the output.
2. Call Codex MCP:
   - tool: `mcp__codex__codex`
   - `cwd`: absolute path to the project root
   - `sandbox`: `workspace-write`
   - `prompt`: the brief from step 1
3. Pass Codex's findings back to the user as-is — it already uses the four-bucket format.

## codex-review vs agent-review

- `/codex-review`: runs in the Codex MCP sandbox. Separate environment, independent rate limits.
- `/agent-review`: runs as an in-session Task subagent. No MCP needed.

Pick whichever is available or cheaper. Both follow the same workflow.
