#!/bin/sh
# Controls the RGB board from Claude Code: board.sh <command> [value]
#   clawd | clock | weather | serial | off   switch the panel mode
#   brightness <0-100>                       set the brightness
#   claude on|off                            show / ignore Claude Code activity
#   status (default)                         print the board status

URL="${RGB_BOARD_URL:-http://192.168.0.103:8080}"
case "${1:-status}" in
  clawd|clock|weather|serial|off|status) path="/$1" ;;
  brightness) path="/brightness?value=$2" ;;
  claude)
    case "$2" in
      on) path="/claude/enabled?value=1" ;;
      off) path="/claude/enabled?value=0" ;;
      *) echo "usage: claude on|off"; exit 1 ;;
    esac ;;
  *) echo "unknown command '$1'; use clawd, clock, weather, serial, off, brightness <0-100>, claude on|off, status"; exit 1 ;;
esac
curl -s -m 3 "$URL$path" || echo "board at $URL is not reachable"
