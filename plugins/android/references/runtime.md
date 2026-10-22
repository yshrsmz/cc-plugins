# Claude Code / Codex runtime

Read this file before executing the skill. Keep the shared review template, project discovery, review criteria, and output format on both hosts.

- Claude Code: use `Agent` / `Task`, `Read`, and the shell tools named in the skill. `$ARGUMENTS` means the invocation's arguments.
- Codex: use the available subagent, file, and shell tools. Read arguments from the user's skill invocation, not a `$ARGUMENTS` shell variable. Use a question tool or ask in chat when information is missing. Wait for the answer before dependent actions.
- Read applicable `AGENTS.md`, `CLAUDE.md`, and referenced rule files. When `CLAUDE.md` imports `AGENTS.md`, read the shared file too.
- Invoke skills with `/android:<skill-name>` in Claude Code; in Codex select the installed skill or explicitly name it in the request.

## Android review agents

Claude Code registers [android-compose-architect](../agents/android-compose-architect.md) and [android-library-architect](../agents/android-library-architect.md) as named agents. Codex does not register these Markdown definitions automatically. For `agent-review` in Codex, read the chosen definition and pass its entire body after the YAML frontmatter to a general-purpose subagent together with the fully customized review prompt. Use the session's model and permissions; do not translate `opus` or Claude's `tools` into Codex settings. Require a read-only review. Map `general-purpose` to an available general-purpose agent and `Explore` to an explorer or general-purpose agent. For another explicit agent name, verify that the host provides it before using it.

Wait for the subagent's completed result before presenting findings. If delegation is unavailable, report that prerequisite. `codex-review` always runs a separate `codex exec` process, including when called from Codex; it must still collect the output and handle failure as documented.

## Firebase MCP

`crashlytics-triage` requires an already connected Firebase MCP server exposing the Crashlytics tools. Discover tools by their capabilities and actual server prefix. Use `ToolSearch` if available in Claude Code or the host's tool discovery facility in Codex. Never assume the Claude `mcp__plugin_firebase_firebase__` prefix exists in Codex.

Claude Code can resolve the `firebase` plugin dependency after the Firebase marketplace is registered. Codex's manifest does not declare that Claude-specific dependency. If tools are missing in Codex, ask the user to connect and authenticate the Firebase MCP server in their Codex environment, then restart or refresh the session. Do not run Claude plugin installation commands in Codex or improvise with REST calls. Reuse the user's existing Firebase configuration; this plugin does not install a server or package on their behalf.
