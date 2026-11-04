#!/bin/sh
# Sends a Claude Code session state to the RGB board: notify.sh <start|thinking|tool|waiting|done|end>
#
# Fire-and-forget: curl runs in the background with a 1s timeout and all output
# discarded, so the hook never slows Claude down, never fails, and adds nothing
# to Claude's context. Board address: RGB_BOARD_URL (default below).
#
# For "tool" (PreToolUse) the hook input JSON on stdin carries the tool name,
# which picks Clawd's animation (reading, typing, terminal, web, agents).

URL="${RGB_BOARD_URL:-http://192.168.0.103:8080}"
QUERY="state=$1"
if [ "$1" = tool ]; then
  TOOL=$(sed -n 's/.*"tool_name" *: *"\([A-Za-z0-9_-]*\)".*/\1/p' | head -n 1)
  QUERY="$QUERY&tool=$TOOL"
fi
curl -s -m 1 "$URL/claude?$QUERY" </dev/null >/dev/null 2>&1 &
exit 0
