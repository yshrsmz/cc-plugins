# Code Review Prompt Template

This template provides guidelines for generating customized code review prompts for Android projects (apps or libraries). Commands should use this as a reference to build agent-specific prompts, NOT copy it verbatim.

## How to Use This Template

When generating a review prompt:
1. **Read this template** to understand the structure and requirements
2. **Customize for the agent type**:
   - Add agent-specific context (tools available, execution environment)
   - Emphasize relevant expertise (Compose/MVVM for app projects, API design for library projects)
   - Adjust technical depth based on agent capabilities
3. **Include session context**: Working directory, current branch, project specifics (discovered at runtime — never hardcoded)
4. **Adapt review focus**: Prioritize checks based on what the agent does best and what the project actually is

## Common Command Instructions

All review commands (agent-review, codex-review) should follow these common steps:

### Review Scope

The review can examine:
- Current workspace changes (staged and unstaged)
- Entire branch context (all commits since branching from the main branch)
- Committed files for full context when needed

### Step 1: Verify Changes Exist

Run `git status` to confirm there are changes to review.

### Step 2: Discover Project Context (REQUIRED)

Before generating the prompt, gather project-specific context by reading (as available):
- `CLAUDE.md` — project overview, build commands, architecture notes
- `README.md` — high-level project description
- `docs/design-docs/`, `docs/requirements/`, `docs/architecture/` — design and architecture documents
- `build-logic/README.md` — build system conventions (if changes touch build config)
- Top-level `settings.gradle.kts` / `settings.gradle` — module structure
- Any task-specific documentation from `docs/` related to the changes

Use these to determine:
- **Project name** (from CLAUDE.md, README, or directory name)
- **Project type** (Android app vs. Android library vs. multi-module)
- **Architecture style** (MVVM with Hilt, clean architecture, custom patterns, etc.)
- **UI framework** (Jetpack Compose, legacy Views, both)
- **Notable modules / key classes** that reviewers should know about

These values feed into the `[PROJECT_NAME]`, `[PROJECT_TYPE]`, `[ARCHITECTURE_SUMMARY]` placeholders below. Do NOT invent project context — only include what you actually discovered.

### Step 3: Gather Environment Context

Before generating the prompt, gather:
- Current working directory: `pwd`
- Current branch name: `git rev-parse --abbrev-ref HEAD`
- Main branch name: detect via `git symbolic-ref refs/remotes/origin/HEAD` or check for `main`/`master` (fall back to asking the user if ambiguous)

### Step 4: Generate Customized Prompt

**IMPORTANT**: Do NOT simply copy this template. Generate a NEW prompt that:

1. **Includes an agent/backend-specific introduction**
   - State the agent type and expertise
   - Describe the execution environment
   - List available tools and capabilities

2. **Includes actual context values**
   - Replace `[PROJECT_NAME]` with the discovered project name
   - Replace `[PROJECT_TYPE]` with app/library/multi-module as discovered
   - Replace `[PROJECT_PATH]` with actual working directory (from pwd)
   - Replace `[BRANCH_NAME]` with current branch name (from git)
   - Replace `[MAIN_BRANCH]` with the detected main branch name
   - Replace `[ARCHITECTURE_SUMMARY]` with a short 1–3 line description of the architecture/key modules (only include if discovered)

3. **Incorporates template sections** with placeholders replaced:
   - Git analysis instructions (section 2) — replace `[MAIN_BRANCH]` with the actual name
   - Project documentation references (section 3)
   - Review criteria (section 4) — emphasize based on agent type AND project type
   - Agent-specific focus areas (section 5)
   - Output format requirements

4. **Emphasizes the agent/backend's specific strengths**
   - For Task agents: mention available tools (Bash, Read, etc.)
   - For Codex: mention separate execution environment, extensive git access
   - For android-compose-architect: emphasize Compose/MVVM/Hilt expertise
   - For android-library-architect: emphasize public API design, Java interop, thread safety, resource management
   - For general-purpose: balanced coverage

### Prompt Requirements

The generated prompt must be:
- **Complete and standalone** (no references to external templates)
- **Contextual** (includes actual working directory, branch names, discovered project info)
- **Environment-specific** (mentions available tools and execution context)
- **Tailored to agent expertise** (emphasizes relevant knowledge areas)
- **Honest about unknowns** (omit architecture/module claims that were not actually discovered)

## Review Prompt Structure

### 1. Introduction & Context
```
You are [AGENT_TYPE] reviewing code changes for the [PROJECT_NAME] [PROJECT_TYPE].

You are running in [EXECUTION_ENVIRONMENT] with access to:
- [LIST_OF_TOOLS_AVAILABLE]
- [SPECIFIC_CAPABILITIES]

Project context:
- Working directory: [PROJECT_PATH]
- Current branch: [BRANCH_NAME]
- Main branch: [MAIN_BRANCH]
- Architecture: [ARCHITECTURE_SUMMARY]   (omit this line if not discovered)
```

### 2. Git Analysis Instructions
```
IMPORTANT: First, run git commands to understand what changed:

**Step 1: Check current workspace changes**
- `git status` — to see which files have changes (staged and unstaged)
- `git diff` — to review unstaged changes
- `git diff --cached` — to review staged changes
- `git diff --stat` and `git diff --cached --stat` — for change summaries

**Step 2: Check branch context (if necessary)**
- `git log [MAIN_BRANCH]..HEAD --oneline` — to see all commits in the current branch
- `git diff [MAIN_BRANCH]...HEAD --stat` — to see all changes in the branch (summary)
- `git diff [MAIN_BRANCH]...HEAD` — to see full diff of all branch changes

**Step 3: Read files for context (when needed)**
- Use [AVAILABLE_READ_TOOL] to read the committed files for full context
- This is especially important when:
  - Current changes depend on earlier commits in the branch
  - You need to verify architectural consistency across multiple commits
  - The change touches complex areas that need full file context
  - Testing strategy needs to be evaluated across the whole feature
```

### 3. Project Documentation References
```
Read any relevant project-specific documentation for additional context:
- CLAUDE.md — project overview, build commands, git conventions
- docs/design-docs/ — design documents and architecture decisions (if exists)
- docs/requirements/ — active specifications related to these changes (if exists)
- build-logic/README.md — build system conventions (if changes involve build config)
```

### 4. Review Criteria

Customize this section based on agent expertise AND project type (app vs. library). Include all relevant criteria, but emphasize areas where the agent excels and the project demands.

```
Review ALL changes (both staged and unstaged) and analyze them for:

1. **Code Quality**:
   - Adherence to Kotlin coding standards and idioms
   - Named parameters for multi-param calls
   - Proper imports (no fully qualified names in code)
   - Null safety, data classes, extension functions used where appropriate
   - Code readability and maintainability

2. **Architecture**:
   - Project-appropriate pattern compliance (MVVM/Hilt for apps, layered API for libraries)
   - Clean architecture principles where applicable (presentation / domain / data)
   - Module boundaries and dependencies
   - Proper separation of concerns
   - Public vs. internal visibility

3. **Android Best Practices** (include the subset that applies to the project):
   - Jetpack Compose patterns and recomposition considerations (for Compose projects)
   - StateFlow / single-state-in-ViewModel (for MVVM apps)
   - Coroutines and Flow usage
   - Android lifecycle management and memory-leak prevention
   - Context handling (applicationContext vs. Activity context)
   - SQLite patterns — transactions, statement management (for library/data-layer work)
   - Thread safety — ExecutorService, @Volatile, synchronization
   - Resource management — use{} blocks, proper closing

4. **API Design** (for library projects or public-facing modules):
   - Java interoperability (@JvmStatic, @JvmField, @JvmOverloads)
   - Builder pattern consistency
   - Public API surface (avoid exposing internals)
   - Backwards compatibility

5. **Testing**:
   - Test coverage for new/changed code (all new behavior should have tests)
   - Test quality and assertions (JUnit, AssertJ, etc. per project convention)
   - MockK and Turbine usage for Flow testing (where applicable)
   - Robolectric for Android framework tests (where applicable)
   - Error states and edge cases covered

6. **Potential Issues**:
   - Performance concerns
   - Memory leaks
   - Threading issues
   - Resource leaks (database connections, statements, streams)

7. **Security**:
   - No hardcoded secrets
   - Proper data handling
   - Input validation

8. **Documentation**:
   - Code comments where necessary (sparingly — the code should be self-explanatory)
   - KDoc for public APIs
   - README / CHANGELOG updates if needed

Please provide:
- ✅ What's done well
- ⚠️ Issues that should be fixed
- 💡 Suggestions for improvement
- 🔴 Critical problems that must be addressed

Be specific with file paths and line references where possible.
```

### 5. Agent-Specific Focus Areas

**For android-compose-architect:**
- Emphasize: Jetpack Compose best practices, MVVM patterns with Hilt, Android lifecycle, threading
- Deep dive: Compose recomposition, StateFlow state management, navigation patterns
- Catch: Memory leaks in ViewModels, improper Compose usage, lifecycle violations, feature module dependencies

**For android-library-architect:**
- Emphasize: Public API design, Java interop, thread safety, resource management
- Deep dive: API surface stability, backwards compatibility, SQLite/stream/executor correctness
- Catch: Leaked internals, missing @JvmStatic/@JvmOverloads on public entry points, Activity-context leaks, unclosed resources, untested concurrent paths

**For general-purpose:**
- Balanced coverage of all criteria
- Focus on general code quality and architecture
- Standard software engineering best practices

**For Explore agent:**
- Emphasize: Code organization, module structure, architectural patterns
- Deep dive: Codebase navigation, pattern discovery, relationship mapping

## Expected Output Format

The review should include:

1. **Changes Summary**: List of files changed
   - Current workspace changes (staged and unstaged)
   - Branch commits (if reviewed for broader context)
   - Files affected across the entire branch (if applicable)

2. **Review Results**: Analysis with clear sections:
   - ✅ What's done well
   - ⚠️ Issues that should be fixed
   - 💡 Suggestions for improvement
   - 🔴 Critical problems that must be addressed

3. **Actionable Feedback**: Specific file paths and line references for each finding

4. **Critical Issues**: Highlighted problems that must be addressed before merging

**Example Output Format**:
```
## Changes Summary

### Current Workspace
Staged:
- feature/status/src/main/java/com/example/status/ShareTextEditorScreen.kt (+156, -89)
- core/domain/src/main/java/com/example/domain/GetStatusParamsUseCase.kt (+12, -5)

Unstaged:
- feature/status/src/test/java/com/example/status/ShareTextEditorViewModelTest.kt (+45, -0)

### Branch Context (if reviewed)
Commits in branch (3 commits):
- abc1234 feat: Add share text editor screen
- def5678 refactor: Update use case for new requirements
- ghi9012 test: Add tests for share text editor

Files changed in entire branch:
- 8 files changed, 245 insertions(+), 112 deletions(-)

## Review Results

✅ What's done well
- Clean separation of concerns across modules
- Named parameters used consistently at ShareTextEditorScreen.kt:42, 67, 91
- Proper MVVM state management with StateFlow in ShareTextEditorViewModel.kt:25-35

⚠️ Issues that should be fixed
- GetStatusParamsUseCase.kt:23: Consider adding input validation

💡 Suggestions for improvement
- ShareTextEditorScreen.kt:120: Extract complex composable into separate function
- Consider adding integration test for cross-module flow

🔴 Critical problems
- ShareTextEditorViewModelTest.kt: Missing test coverage for error states
```
