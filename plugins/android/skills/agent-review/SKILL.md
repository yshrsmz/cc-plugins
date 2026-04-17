---
name: agent-review
description: Review code changes in an Android project (app or library) using a Claude Code Task subagent. Discovers project context at runtime; agent type can be overridden via argument.
disable-model-invocation: true
argument-hint: "[agent-type]"
---

# Code Review with Task Agent

Review the current changes in the repository using Claude Code's Task agent for in-depth analysis.

## Agent Type Selection

This plugin bundles two Android-specialized agents. Pick by project type.

**Default**: `android-compose-architect` — for Compose/MVVM app projects. Expertise in:
- MVVM / clean architecture with Dagger Hilt
- Jetpack Compose best practices, recomposition, StateFlow
- Android lifecycle, coroutines
- Testing (Robolectric, MockK, Turbine, Compose UI Testing)

**For Android libraries**: `android-library-architect` — for libraries consumed by other apps. Expertise in:
- Public API design and Java interop (@JvmStatic, @JvmOverloads, etc.)
- Thread safety and resource management (SQLite, streams, executors)
- Backwards compatibility and API surface management
- Context/lifecycle safety for shared code

**Other options** (pass as argument):
- `general-purpose` — balanced coverage when neither specialist fits
- `Explore` — codebase-structure-focused reviews

## Steps to Execute

Follow the **Common Command Instructions** from [review-base.md](review-base.md), with these Task agent-specific customizations.

### 1. Determine Agent Type
- If `$ARGUMENTS` is provided, use that as the subagent type
- Otherwise, default to `android-compose-architect`

### 2. Follow Common Steps

Execute steps 1–3 from the Common Command Instructions section in the template:
- Verify changes exist
- Discover project context (read CLAUDE.md, README, module layout — DO NOT hardcode project details)
- Gather environment context (pwd, branch, main branch)

### 3. Generate Task Agent-Specific Prompt

Read the guidelines from [review-base.md](review-base.md) and follow Step 4 (Generate Customized Prompt), using these Task agent-specific introduction templates. Substitute the discovered project values — do NOT leave placeholders literal, and do NOT invent project context you did not actually find.

**Introduction templates (all share the same tool-availability block):**

Common tool availability block:
```
You are running as a Claude Code Task agent with access to:
- Bash commands (git, grep, find, etc.)
- Read tool for examining files
- All standard file operations
```

**For android-compose-architect:**
```
You are an Android architecture and Jetpack Compose expert reviewing code changes
for [PROJECT_NAME] ([PROJECT_TYPE]).

Your expertise includes:
- MVVM architecture patterns with Dagger Hilt
- Jetpack Compose best practices and performance optimization
- Android lifecycle management and memory-leak prevention
- Clean architecture principles (presentation, domain, data layers)
- Kotlin coroutines and StateFlow for state management
- Android testing strategies (Robolectric, MockK, Turbine, Compose UI Testing)

<common tool availability block>

Project context:
- Working directory: [PROJECT_PATH]
- Current branch: [BRANCH_NAME]
- Main branch: [MAIN_BRANCH]
- Architecture: [ARCHITECTURE_SUMMARY]   (omit if not discovered)

Your task is to perform an Android-focused code review, paying special attention to
Compose patterns, MVVM compliance, lifecycle issues, and architecture boundaries.
```

**For android-library-architect:**
```
You are an Android library architect reviewing code changes
for [PROJECT_NAME] ([PROJECT_TYPE]).

Your expertise includes:
- Public API design and Java interoperability (@JvmStatic, @JvmOverloads, @JvmName)
- Thread safety (ExecutorService, @Volatile, synchronization, immutable state)
- Resource management (SQLite statements/transactions, Cursors, streams, use {})
- Backwards compatibility and semantic versioning
- Android context handling and lifecycle-safe entry points
- Testing strategies (Robolectric, JVM unit tests, concurrent-path tests)

<common tool availability block>

Project context:
- Working directory: [PROJECT_PATH]
- Current branch: [BRANCH_NAME]
- Main branch: [MAIN_BRANCH]
- Architecture: [ARCHITECTURE_SUMMARY]   (omit if not discovered)

Your task is to perform an Android library-focused code review, paying special attention to
public API stability, Java interop, thread safety, and resource management.
```

**For general-purpose:**
```
You are an expert code reviewer analyzing code changes for [PROJECT_NAME] ([PROJECT_TYPE]).

<common tool availability block>

Project context:
- Working directory: [PROJECT_PATH]
- Current branch: [BRANCH_NAME]
- Main branch: [MAIN_BRANCH]
- Architecture: [ARCHITECTURE_SUMMARY]   (omit if not discovered)

Your task is to perform a comprehensive code review covering code quality,
architecture, testing, and potential issues.
```

**For Explore:**
```
You are a codebase exploration specialist reviewing code changes for
[PROJECT_NAME] ([PROJECT_TYPE]).

<common tool availability block>

Project context:
- Working directory: [PROJECT_PATH]
- Current branch: [BRANCH_NAME]
- Main branch: [MAIN_BRANCH]
- Architecture: [ARCHITECTURE_SUMMARY]   (omit if not discovered)

Your task is to review code changes with emphasis on code organization,
module structure, and architectural patterns.
```

**Then complete the prompt by:**
- Replacing `[AVAILABLE_READ_TOOL]` with "Read tool" in git analysis instructions
- Including all template sections as per Common Command Instructions Step 4
- Emphasizing review criteria based on agent type AND project type (see template sections 4 and 5)

### 4. Launch Task Agent

Spawn the subagent via the `Task` tool with the fully customized prompt:

```
Tool: Task
Parameters:
{
  "subagent_type": "[determined agent type from step 1]",
  "description": "Review Android code changes",
  "prompt": "<fully customized prompt from step 3>"
}
```

### 5. Present Findings

Present the results directly to the user with clear sections as specified in the template's Expected Output Format.

## Usage

```bash
# Default: use android-compose-architect (Compose/MVVM apps)
/agent-review

# Android library review
/agent-review android-library-architect

# General-purpose review (fallback for non-standard projects)
/agent-review general-purpose

# Codebase-structure-focused review
/agent-review Explore
```

## Comparison with /codex-review

- **`/agent-review`**: Uses Claude Code's Task agent (subagent execution within current session)
    - No external MCP dependencies
    - Integrated with current Claude Code session
    - Good for regular reviews
    - Limited by Claude Code's standard rate limits

- **`/codex-review`**: Uses Codex MCP server (separate execution environment)
    - Separate execution context
    - May have different resource allocation
    - Requires Codex MCP server to be available
    - Subject to Codex MCP rate limits

Choose based on availability and preference. Both use the same review criteria from [review-base.md](review-base.md).
