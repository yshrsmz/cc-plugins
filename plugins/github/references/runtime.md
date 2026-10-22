# Claude Code / Codex runtime

Read this file before executing the skill. The workflow, review criteria, output formats, and approval requirements in the skill apply on both hosts.

## Tools and arguments

- Claude Code: use the named `Agent` / `Task`, `AskUserQuestion`, `Read`, `Edit`, `Write`, and shell tools in the skill. `$ARGUMENTS` denotes the skill's supplied arguments.
- Codex: use the available subagent, question, file, and shell tools for those operations. Read arguments from the user's skill invocation; `$ARGUMENTS` is not a shell environment variable. If a question tool is unavailable, ask in chat and wait for the answer before taking an action that needs it. Never treat a displayed option as approval.
- Invoke skills with `/github:<skill-name>` in Claude Code; in Codex select the installed skill from the skill picker or name it explicitly in the request.

## Subagents

- Claude Code: the plugin registers the named agents from `../agents/`. Use the namespaced `subagent_type` given in the skill.
- Codex: those Markdown files are shared instruction sources, not registered Codex custom agents. For `pr-review`, read [pr-review-bugs](../agents/pr-review-bugs.md), [pr-review-rules](../agents/pr-review-rules.md), and [pr-review-quality](../agents/pr-review-quality.md). Pass each definition's entire body after the YAML frontmatter to a separate general-purpose subagent, together with the PR context and the skill's required prompt fields. Do not pass the Claude `model` or `tools` frontmatter as Codex settings. Inherit the session's model and permissions, and explicitly require read-only review.
- For `issue-triage`, use an available explorer or general-purpose subagent in Codex instead of Claude's `Explore`. For changelog research, use general-purpose subagents.
- Start independent tasks in parallel within the host's available concurrency. Batch excess tasks, wait for every result, and release completed agent slots when supported. If delegation is unavailable, report the missing capability instead of claiming a parallel review was performed.

## Project instructions and recording learnings

Read applicable `AGENTS.md` files, plus `CLAUDE.md` and `.claude/rules/` when present, including files they explicitly reference. A `CLAUDE.md` containing `@AGENTS.md` points at the shared instructions; do not stop at the import line. Review explicit rules from all those sources without counting the same rule twice.

When a skill proposes saving a preventive rule, follow the repository's existing ownership of instructions. In Codex, use `AGENTS.md` for shared project guidance and `.agents/skills/<name>/SKILL.md` for a reusable workflow. Do not write Codex guidance only to `.claude/rules/` or Claude auto-memory. In Claude Code, retain the existing `.claude/rules/`, `CLAUDE.md`, and skill conventions, but edit the shared `AGENTS.md` when `CLAUDE.md` imports it. Ask before applying proposed learnings as the skill requires.
