# rgb-board

Clawd (the Claude Code mascot) acting out your Claude Code session, with a clock and weather in the corners, on a 64×32 HUB75 panel driven by a Raspberry Pi 4 through the Amperka RGB matrix driver.

## Layout

- `rgbboard/` — the app (`python3 -m rgbboard`): Flask API + display modes
- `fonts/` — `6x12` bitmap font, Noto Emoji for weather icons
- `config.example.toml` — settings; the real `config.toml` lives only on the Pi
- `deploy/rgb-board.service` — systemd unit
- `deploy.sh` — rsync to the Pi and restart the service
- `.claude-plugin/marketplace.json` + `claude-plugin/` — the Claude Code plugin (the repo root is its marketplace)

## Pi prerequisites

- `rgbmatrix` Python binding (installed by `amperka-rpi-rgb-matrix.sh`)
- `sudo apt install python3-flask python3-requests python3-pil`

## Deploy

```sh
./deploy.sh                                  # default host nikita@192.168.0.103
RGB_BOARD_HOST=nikita@raspberrypi.local ./deploy.sh
```

First time, create `~/matrix/rgb-board/config.toml` on the Pi from `config.example.toml`.

Logs: `ssh nikita@192.168.0.103 journalctl -u rgb-board -f`

## Web panel

Open http://192.168.0.103:80## Claude Code plugin

The default `clawd` mode shows Clawd on the left, a small clock top-right and the weather bottom-right.
`claude-plugin/` is a Claude Code plugin whose hooks tell the board what Claude is doing, and Clawd acts it out:

| Hook | Clawd |
|---|---|
| `SessionStart` | waves, then stands and blinks |
| `UserPromptSubmit` | juggles |
| `Notification`, `Stop` | jumps (your turn) |
| `SessionEnd` | crawls off the left edge |

If another mode is on (text, a drawing, the big clock), Claude takes the panel over and gives it back
once Clawd has crawled away.

```sh
claude plugin marketplace add ~/IdeaProjects/rgb-board
claude plugin install rgb-board@rgb-board-local
```

`/rgb-board:board [clawd|clock|weather|serial|off|brightness N|claude on|off|status]` controls the board
from Claude Code. Toggle the plugin with `/plugin`, or the indicator on the panel side with the switch in the
web panel. Board address: `RGB_BOARD_URL` (default `http://192.168.0.103:8080`). The hooks run curl in the
background with all output discarded, so they cost no tokens and never block Claude.

## API (port 8080)

| Endpoint | |
|---|---|
| `POST /draw` | show an image (PNG body); resized to the panel if needed |
| `/claude?state=start\|working\|attention\|end` | Claude Code indicator |
| `/claude/enabled?value=0\|1` | turn the indicator on/off |
| `/clawd`, `/clock`, `/weather`, `/serial` | switch mode (`serial` alternates clock and weather) |
| `/print?text=hello` | static text |
| `/brightness?value=0..100` | brightness |
| `/off` | stop and clear |
| `/status` | current mode and brightness |
