# Session Logger

An example hook plugin that demonstrates how to use Claude Code's `SessionStart` and `SessionEnd` hooks to log session activity.

## Installation

Add this marketplace to Claude Code:
```bash
/plugin marketplace add yshrsmz/cc-plugins
```

Then install the plugin:
```bash
/plugin install session-logger
```

## What It Does

This plugin demonstrates Claude Code's hook system by logging:
- When sessions start (startup, resume, clear, or compact)
- When sessions end (clear, logout, exit, or other)
- Working directory information
- Session IDs

Logs are written to `~/.claude/logs/session.log`

## Available Hooks Used

### SessionStart
Triggers when:
- Claude Code starts up (`source: "startup"`)
- A session resumes (`source: "resume"`)
- Context is cleared (`source: "clear"`)
- Context is compacted (`source: "compact"`)

### SessionEnd
Triggers when:
- User clears the session (`reason: "clear"`)
- User logs out (`reason: "logout"`)
- User exits via prompt input (`reason: "prompt_input_exit"`)
- Other termination reasons (`reason: "other"`)

## Example Log Output

```
[2025-01-15 10:30:45] Session started
  Source: startup
  Directory: /Users/username/project
  Session ID: abc123

[2025-01-15 11:45:20] Session ended
  Reason: clear
  Session ID: abc123
```

## Customization

Edit the shell scripts to:
- Change log location
- Add more detailed logging
- Send notifications
- Integrate with other tools
- Parse JSON data with `jq` for more robust parsing

## Hook Data Format

Both hooks receive JSON data via stdin with these common fields:
- `session_id` - Unique session identifier
- `cwd` - Current working directory
- `transcript_path` - Path to session transcript
- `permission_mode` - Current permission mode

**SessionStart specific:**
- `source` - How the session started

**SessionEnd specific:**
- `reason` - Why the session ended

## Learning Resource

This plugin serves as a template for understanding:
- How Claude Code hooks work
- Reading hook data from stdin
- Processing JSON in bash scripts
- Writing hook scripts that don't interfere with Claude Code

## Files

- `plugin.json` - Plugin manifest
- `session-start.sh` - SessionStart hook implementation
- `session-end.sh` - SessionEnd hook implementation
- `README.md` - This file

## See Also

Other available Claude Code hooks:
- `PreToolUse` - Before tools execute
- `PostToolUse` - After tools complete
- `UserPromptSubmit` - When user submits prompts
- `Stop` - When agent finishes responding
- `Notification` - When notifications are sent
- `PreCompact` - Before context compaction

Check the [Claude Code Hooks documentation](https://docs.claude.com/en/docs/claude-code/hooks) for more details.
