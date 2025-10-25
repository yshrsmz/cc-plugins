#!/bin/bash

# SessionStart hook example
# Logs when a Claude Code session starts
# Receives: session_id, source, cwd, transcript_path, permission_mode

# Read the hook data from stdin
HOOK_DATA=$(cat)

# Parse data (in real usage, you might use jq)
SESSION_ID=$(echo "$HOOK_DATA" | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
SOURCE=$(echo "$HOOK_DATA" | grep -o '"source":"[^"]*"' | cut -d'"' -f4)
CWD=$(echo "$HOOK_DATA" | grep -o '"cwd":"[^"]*"' | cut -d'"' -f4)

# Create log directory if it doesn't exist
LOG_DIR="$HOME/.claude/logs"
mkdir -p "$LOG_DIR"

# Log the session start
LOG_FILE="$LOG_DIR/session.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Session started" >> "$LOG_FILE"
echo "  Source: $SOURCE" >> "$LOG_FILE"
echo "  Directory: $CWD" >> "$LOG_FILE"
echo "  Session ID: $SESSION_ID" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Output success message
echo "✓ Session logged to $LOG_FILE"
exit 0
