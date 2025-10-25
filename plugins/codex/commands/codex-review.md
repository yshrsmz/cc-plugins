# Code Review with Codex

Review the current changes in the repository using Codex for in-depth analysis.

## Steps to Execute

1. **Verify Changes Exist**: Run `git status` to confirm there are changes to review

2. **Optional - Read Additional Context**: If relevant to the changes, read project-specific documentation:
   - `docs/mvi-architecture.md` - MVI architecture details (if exists)
   - `.spec-workflow/` - Current specification documents (if any exist)
   - `build-logic/README.md` - Build system documentation (if exists)
   - Any task-specific documentation from `.spec-workflow/specs/` related to the changes

3. **Review with Codex**: Use the `mcp__codex__codex` tool to analyze the changes.

   **Example Tool Invocation**:
   ```
   Tool: mcp__codex__codex
   Parameters:
   {
     "cwd": "/Users/a12897/repos/github.com/yshrsmz/since-android",  // Current working directory
     "sandbox": "workspace-write",  // Allows running git commands
     "prompt": "<see Codex Review Prompt template below>"
   }
   ```

   Note:
   - We use `workspace-write` mode to allow Codex to run git commands for analyzing changes
   - The `cwd` parameter should be set to the current project root directory

4. **Present Findings**: After Codex completes the review, present the results directly to the user with clear sections formatted as shown in the example output below

## Codex Review Prompt

When calling the codex tool, use this prompt structure:

```
You are reviewing code changes for the SinceTimer Android project.

IMPORTANT: First, run git commands to understand what changed:
- `git status` - to see which files have changes (staged and unstaged)
- `git diff` - to review unstaged changes
- `git diff --cached` - to review staged changes
- `git diff --stat` and `git diff --cached --stat` - for change summaries

Then, read any relevant project-specific documentation for additional context:
- docs/mvi-architecture.md - MVI architecture patterns (if changes involve MVI)
- .spec-workflow/ - Check for active specifications related to these changes
- build-logic/README.md - Build system conventions (if changes involve build config)

Review ALL changes (both staged and unstaged) and analyze them for:

1. **Code Quality**:
   - Adherence to Kotlin coding standards
   - Named parameters usage (mandatory for multi-param calls)
   - No fully qualified names (proper imports required)
   - Code readability and maintainability

2. **Architecture**:
   - MVI pattern compliance (Store/Reducer/Processor)
   - Clean architecture principles
   - Module boundaries and dependencies
   - Proper separation of concerns

3. **Android Best Practices**:
   - Jetpack Compose usage (if applicable)
   - Room database patterns
   - Coroutines and Flow usage
   - View binding patterns

4. **Testing**:
   - Test coverage for new/changed code (MANDATORY: all new behavior must have tests)
   - Test quality and assertions
   - Use of test utilities from :core:testing
   - MockK and Turbine usage
   - Error states and edge cases covered

5. **Potential Issues**:
   - Performance concerns
   - Memory leaks
   - Threading issues
   - Resource management

6. **Security**:
   - No hardcoded secrets
   - Proper data handling
   - Input validation

7. **Documentation**:
   - Code comments where necessary
   - KDoc for public APIs
   - README updates if needed

Please provide:
- ✅ What's done well
- ⚠️ Issues that should be fixed
- 💡 Suggestions for improvement
- 🔴 Critical problems that must be addressed

Be specific with file paths and line references where possible.
```

## Expected Output

The command should produce a review that includes:

1. **Changes Summary**: List of files changed (from git status/diff --stat)
   - Staged changes
   - Unstaged changes

2. **Review Results**: Codex analysis with clear sections:
   - ✅ What's done well
   - ⚠️ Issues that should be fixed
   - 💡 Suggestions for improvement
   - 🔴 Critical problems that must be addressed

3. **Actionable Feedback**: Specific file paths and line references for each finding

4. **Critical Issues**: Highlighted problems that must be addressed before merging

**Example Output Format**:
```
## Changes Summary
Staged:
- app/src/main/java/com/example/ui/TimerDetailScreen.kt (+156, -89)
- domain/src/main/java/com/example/domain/GetTimerUseCase.kt (+12, -5)
- data/repository/src/main/java/com/example/data/TimerRepository.kt (+8, -3)

Unstaged:
- app/src/test/java/com/example/ui/TimerDetailScreenTest.kt (+45, -0)

Note: Changes span multiple modules (UI, domain, data) - verify clean architecture boundaries.

## Review Results

✅ What's done well
- Clean separation of concerns across modules (app, domain, data)
- Named parameters used consistently at TimerDetailScreen.kt:42, 67, 91
- Proper MVI state management in TimerDetailScreen.kt:25-35

⚠️ Issues that should be fixed
- TimerRepository.kt:45: Missing error handling for database operation
- GetTimerUseCase.kt:23: Consider adding input validation

💡 Suggestions for improvement
- TimerDetailScreen.kt:120: Extract complex composable into separate function
- Consider adding integration test for cross-module flow

🔴 Critical problems
- TimerDetailScreenTest.kt: Missing test coverage for error states
  (Note: All new/changed behavior must have corresponding tests)
```

## Usage

Simply type `/codex-review` in Claude Code to trigger this review workflow.
