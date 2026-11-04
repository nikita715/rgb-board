#!/usr/bin/env bash
# Sync the project to the Pi and restart the service.
set -euo pipefail

HOST="${RGB_BOARD_HOST:-nikita@192.168.0.103}"
DIR="matrix/rgb-board"

cd "$(dirname "$0")"

# config.toml lives only on the Pi; it's excluded so --delete doesn't remove it.
rsync -a --delete \
  --exclude .git --exclude .idea --exclude __pycache__ --exclude config.toml --exclude claude-plugin \
  ./ "$HOST:$DIR/"

ssh "$HOST" "
  set -e
  test -f $DIR/config.toml || echo 'WARNING: ~/$DIR/config.toml is missing, using defaults (no weather API key)'
  sudo install -m 644 $DIR/deploy/rgb-board.service /etc/systemd/system/rgb-board.service
  sudo systemctl daemon-reload
  sudo systemctl enable rgb-board >/dev/null 2>&1
  sudo systemctl restart rgb-board
  sleep 2
  systemctl --no-pager --lines=10 status rgb-board
"
