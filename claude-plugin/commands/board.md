---
description: Control the RGB board (mode, brightness, Claude indicator)
argument-hint: "[clawd|work [animation]|clock|weather|serial|off|brightness <0-100>|claude on|off|status]"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/board.sh:*)
---
!`"${CLAUDE_PLUGIN_ROOT}/scripts/board.sh" $ARGUMENTS`

Above is the RGB board's reply. Tell the user the result in one short line, in their language. Do nothing else.
