---
name: codex-review
description: Review code changes in an Android project (app or library) using the Codex MCP server. Discovers project context at runtime.
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

You are running in Codex MCP with workspace-write sandbox mode, which gives you access to:
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

Call the `mcp__codex__codex` tool with the fully customized prompt:

```
Tool: mcp__codex__codex
Parameters:
{
  "cwd": "<absolute-path-to-project-root>",
  "sandbox": "workspace-write",
  "prompt": "<fully customized prompt from step 4>"
}
```

### 6. Present Findings

Present the results directly to the user with clear sections as specified in the template's Expected Output Format.

## Usage

Simply type `/codex-review` in Claude Code to trigger this review workflow.

## Comparison with /agent-review

- **`/codex-review`**: Uses Codex MCP server (separate execution environment)
    - Separate execution context
    - May have different resource allocation
    - Requires Codex MCP server to be available

- **`/agent-review`**: Uses Claude Code's Task agent (subagent within current session)
    - No external MCP dependencies
    - Integrated with current Claude Code session

Both use the same review criteria from [review-base.md](review-base.md).
