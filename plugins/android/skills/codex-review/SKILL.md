---
name: codex-review
description: >-
  Review code changes in an Android project (app or library) using the Codex CLI (`codex exec`). Discovers project context at runtime.
disable-model-invocation: true
---

# Code Review with Codex

Review the current changes in the repository using Codex for in-depth analysis.

## Steps to Execute

Follow the **Common Command Instructions** from [review-base.md](review-base.md), with these Codex-specific customizations.

### 1–3. Follow Common Steps

Execute steps 1–3 from the Common Command Instructions section in the template:
- Verify changes exist
- Discover project context (read CLAUDE.md, README, module layout — DO NOT hardcode project details)
- Gather environment context (pwd, branch, main branch)

### 4. Generate Codex-Specific Prompt

Read the guidelines from [review-base.md](review-base.md) and follow Step 4 (Generate Customized Prompt), using this Codex-specific introduction template. Substitute discovered project values — do NOT leave placeholders literal, and do NOT invent project context you did not actually find.

**Codex-Specific Introduction Template:**

```
You are an expert code reviewer analyzing code changes for [PROJECT_NAME] ([PROJECT_TYPE]).

You are running in Codex CLI (`codex exec`) with workspace-write sandbox mode, which gives you access to:
- Bash commands (git, file operations, etc.)
- File reading capabilities
- Full repository access

Project context:
- Working directory: [PROJECT_PATH]
- Current branch: [BRANCH_NAME]
- Main branch: [MAIN_BRANCH]
- Architecture: [ARCHITECTURE_SUMMARY]   (omit this line if not discovered)

Your task is to perform a comprehensive code review covering workspace changes
and branch context as needed. Your separate execution environment allows for
thorough analysis and extensive git operations.
```

**Then complete the prompt by:**
- Replacing `[AVAILABLE_READ_TOOL]` with "bash cat command or file reading" in git analysis instructions
- Including all template sections as per Common Command Instructions Step 4
- Emphasizing Codex's strengths: separate environment, extensive git access, methodical review
- Tailoring review criteria to the discovered project type (app vs. library)

### 5. Execute Codex Review

Run the Codex CLI with the fully customized prompt. Write the prompt to a temporary
file and feed it through stdin — do NOT inline it as a shell argument, since the
prompt contains quotes, backticks and newlines that the shell would reinterpret.

```bash
PROMPT_FILE=$(mktemp -t codex-review-prompt)
OUTPUT_FILE=$(mktemp -t codex-review-output)

# Write the fully customized prompt from step 4 into "$PROMPT_FILE" first.

codex exec \
  -C "<absolute-path-to-project-root>" \
  -s workspace-write \
  -o "$OUTPUT_FILE" \
  - < "$PROMPT_FILE"
```

Flag mapping from the parameters this skill used before:

| Purpose | Flag |
| --- | --- |
| Working root | `-C <dir>` |
| Sandbox policy | `-s workspace-write` |
| Prompt | `-` (read from stdin) |
| Final message only | `-o <file>` |

Read `"$OUTPUT_FILE"` to obtain the review result — it holds the agent's final
message without the interleaved progress log that goes to stdout. If `codex exec`
exits non-zero, report the failure instead of presenting partial findings.

**Requires Codex CLI 0.154.0 or later.** This skill previously called an
`mcp__codex__codex` MCP tool, which no longer exists: the `codex mcp-server` entry
point was removed in Codex 0.154.0, and `codex mcp` is now a manager for *external*
MCP servers rather than a way to expose Codex itself as one.

### 6. Present Findings

Present the results directly to the user with clear sections as specified in the template's Expected Output Format.

## Usage

Simply type `/codex-review` in Claude Code to trigger this review workflow.

## Comparison with /agent-review

- **`/codex-review`**: Shells out to the Codex CLI (`codex exec`, separate execution environment)
    - Separate execution context
    - May have different resource allocation
    - Requires the `codex` CLI (0.154.0+) to be installed and authenticated

- **`/agent-review`**: Uses Claude Code's Task agent (subagent within current session)
    - No external CLI dependencies
    - Integrated with current Claude Code session

Both use the same review criteria from [review-base.md](review-base.md).
