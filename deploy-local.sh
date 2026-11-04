#!/usr/bin/env bash

set -e
test config.toml || echo 'WARNING: config.toml is missing, using defaults (no weather API key)'
sudo install -m 644 deploy/rgb-board.service /etc/systemd/system/rgb-board.service
sudo systemctl daemon-reload
sudo systemctl enable rgb-board >/dev/null 2>&1
sudo systemctl restart rgb-board
sleep 2
systemctl --no-pager --lines=10 status rgb-board