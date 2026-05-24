---
name: session-review
description: >-
  Reflect on the current Claude Code session, identify legitimate learnings worth preserving (project gotchas, user preferences, mis-attributions, reusable workflows), classify each into the right destination (CLAUDE.md, .claude/rules/, auto-memory, or a new skill), present the proposals via AskUserQuestion, and apply approved changes. Trigger when the user asks to "review this session", "振り返って", "capture learnings", "anything to add to CLAUDE.md?", "何か追加するものは?", "session retrospective", or any other phrasing that asks for post-session reflection on what should be captured.
---

# Session Review

Look back over the current conversation, surface the *legitimate* learnings that survive into future sessions, classify each into the destination where it belongs, ask the user which to apply, and write the files.

The single most important property of this skill is **honest filtering**. A bad retrospective floods rules files with one-off context and ephemeral plans; a good one keeps the corpus thin and high-signal. **Empty is a valid result** — if the session was routine, say so and add nothing.

This skill is the standalone counterpart to the "Rules/Skills/Memory extraction" step in `task.md` Phase 8 (see https://github.com/yshrsmz/notes/blob/main/.claude/commands/task.md). Same intent — capture what should outlive the session — but invocable any time, not only at the end of a structured task workflow.

## Workflow

### 1. Scan the session for candidates

Re-read the conversation with these lenses:

- **Surprises**: places where the user corrected you, redirected the approach, or accepted a non-obvious choice without pushback. Both directions matter — corrections AND validated judgment calls.
- **Mis-attributions / mistakes**: places where you cited the wrong source, asserted something the user proved false, or made a wrong assumption that wasted time.
- **Project gotchas**: non-obvious behaviors of the codebase, build tooling, framework, or runtime that surfaced during the work. Things a future contributor would benefit from knowing.
- **User preferences**: workflow choices, style preferences, terminology, decision patterns the user demonstrated.
- **Reusable workflows**: multi-step processes you executed that generalize beyond this one session.

For each candidate, draft a one-sentence summary in your head and ask: *Would future-me, dropped into a fresh conversation, change their behavior because of this?* If no, drop it.

### 2. Classify each surviving candidate

Match each candidate to exactly one destination:

| Destination | What belongs here |
|---|---|
| **`CLAUDE.md`** (project root) | Non-obvious codebase facts: build/runtime quirks, framework version gotchas, file-layout invariants, things `wxt prepare` regenerates, etc. Usually goes under existing sections like "Notes for editing". |
| **`.claude/rules/<topic>.md`** | Project-specific *process* conventions: how to write tests in this repo, when to ask the user, comment style, git/PR rules. Each rule file is one topic. |
| **Auto-memory** (`~/.claude/projects/<encoded-path>/memory/`) | Cross-session learnings: `user` (who they are), `feedback` (what to do/avoid, with **Why** + **How to apply**), `project` (current initiatives), `reference` (external systems). Always update `MEMORY.md` index. |
| **New skill / command** | A reusable, generalizable multi-step workflow that emerged. Rare — most sessions don't yield one. If yes, recommend invoking the `skill-creator` skill rather than hand-authoring a SKILL.md. |

If a candidate doesn't match cleanly to one destination, that's a signal it isn't well-formed enough — go back and either sharpen it or drop it.

#### Quick rules of thumb

- "Don't do X" without a *why* → not capturable yet; ask the user the reason before saving.
- "X exists in file Y" → the code itself is the source of truth; only capture if X is non-obvious from reading Y.
- "User wants the work split into separate PRs" → either a one-off context detail or a `feedback` memory if the pattern recurs.
- Anything already documented elsewhere (existing rule, existing memory, CLAUDE.md, code comment) → skip; don't duplicate.

### 3. Filter aggressively before presenting

After classification, re-examine the list and remove anything that fails *any* of these:

- The candidate would be visible to a careful reader of the existing code/docs.
- The destination already contains a substantively-equivalent entry.
- The candidate is a hypothesis about a future scenario with no current trigger ("if someone ever adds a dark mode…"). YAGNI applies to rules just as much as to code.
- The candidate restates the literal task that just completed — those belong in PR descriptions and commit messages, not memory.

If filtering leaves zero candidates, tell the user honestly: "Nothing this session generated is worth capturing." Don't pad.

### 4. Present via AskUserQuestion

Two equally valid shapes:

**Shape A — granular (preferred when candidates are heterogeneous):** one `multiSelect: true` question where each option is one candidate ("`<destination>`: `<one-line summary>`"). User picks the subset to apply.

**Shape B — all-or-nothing (matches `task.md` Phase 8):** one single-select question with options `すべて作成` / `選択して作成` / `作成しない`. If the user picks `選択して作成`, follow up with Shape A.

Either way, phrase each candidate so the user can decide without re-reading the session. Bad: "Save the feedback about the thing." Good: "Save to `.claude/rules/styling.md`: 'Tailwind v4 requires explicit `cursor-pointer` rule for buttons.'"

With ≥4 candidates, group them by destination across multiple questions in one `AskUserQuestion` call (max 4 questions per call).

### 5. Apply approved changes

For each approved candidate:

- **`CLAUDE.md` / `.claude/rules/*`**: use `Edit` to append to the right section, or `Write` for a new rule file. Follow the existing prose-wrap and bullet conventions in the surrounding file — when in doubt, mirror what's already there.
- **Auto-memory**: write a new file in the project's memory directory using the frontmatter format from the system prompt (`name`, `description`, `metadata.type`). **Always append a one-line entry to `MEMORY.md`** — orphaned memory files are invisible.
- **New skill / command**: invoke `skill-creator` (or the `skill-creator:skill-creator` Skill). Don't try to hand-author a full SKILL.md from scratch — the creator knows the conventions, eval loop, and description-optimization steps.

### 6. Confirm

End with a brief summary: which destinations got updated, the file paths, and (if relevant) any related issues/PRs the user should consider so the loop closes cleanly.

## Anti-patterns to avoid

- **Padding the list to look thorough.** Three real captures beat ten ceremonial ones. The corpus is read every session and bloats fast.
- **Capturing the task description as a "project" memory.** "We fixed the cursor bug" is not a learning — it's already in the commit message.
- **Citing Claude Code default behavior as a project rule.** If you're about to say "per CLAUDE.md…", verify with `grep` first. Conflating sources (project-specific vs. default system-prompt guidance) erodes the user's ability to trust either.
- **Asking the user "is this a learning?" for every line.** Do the filtering yourself; only surface candidates that passed your own bar.
- **Skipping `MEMORY.md` index update** when writing a new memory file. Memory files are discovered only through the index; an orphaned file is invisible.
- **Hand-writing a new SKILL.md instead of invoking `skill-creator`.** The creator handles description optimization, eval setup, and packaging that you'll otherwise skip.

## Example interaction shape

```
User: 今回のセッション振り返って、何か追加するものある？

Claude (this skill):
1. Scans session → finds 4 candidates
2. Filters → 2 survive (Tailwind v4 button gotcha → CLAUDE.md; rule-citation-accuracy → auto-memory)
3. AskUserQuestion (multiSelect) with both proposals
4. User selects both
5. Edit CLAUDE.md, Write memory file, Edit MEMORY.md
6. Summary: "CLAUDE.md updated (Notes for editing). Memory added: feedback_rule_citation_accuracy.md."

Other sessions, when nothing survives:
"This session was a routine bug fix — nothing crossed the bar for capture. Done."
```

## What this skill is NOT for

- Writing a session summary for the user to read. That's just plain-text recap.
- Drafting PR descriptions or commit messages. The PR/commit captures what happened in the code; this skill captures what should outlive the session in rules/memory.
- Logging every preference the user has ever expressed. Auto-memory has its own bar (described in the system prompt); follow that bar.
