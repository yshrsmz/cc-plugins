#!/bin/bash

# SessionEnd hook example
# Logs when a Claude Code session ends
# Receives: session_id, reason, cwd, transcript_path, permission_mode

# Read the hook data from stdin
HOOK_DATA=$(cat)

# Parse data
SESSION_ID=$(echo "$HOOK_DATA" | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
REASON=$(echo "$HOOK_DATA" | grep -o '"reason":"[^"]*"' | cut -d'"' -f4)

# Log directory
LOG_DIR="$HOME/.claude/logs"
LOG_FILE="$LOG_DIR/session.log"

# Log the session end
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Session ended" >> "$LOG_FILE"
echo "  Reason: $REASON" >> "$LOG_FILE"
echo "  Session ID: $SESSION_ID" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Output success message
echo "✓ Session end logged to $LOG_FILE"
exit 0
