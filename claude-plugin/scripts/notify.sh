#!/bin/sh
# Sends a Claude Code session state to the RGB board: notify.sh <start|thinking|waiting|done|end>
#
# Fire-and-forget: curl runs in the background with a 1s timeout and all output
# discarded, so the hook never slows Claude down, never fails, and adds nothing
# to Claude's context. Board address: RGB_BOARD_URL (default below).

URL="${RGB_BOARD_URL:-http://192.168.0.103:8080}"
curl -s -m 1 "$URL/claude?state=$1" </dev/null >/dev/null 2>&1 &
exit 0
