# rgb-board

Clock / weather / text on a 64×32 HUB75 panel driven by a Raspberry Pi 4 through the Amperka RGB matrix driver.

## Layout

- `rgbboard/` — the app (`python3 -m rgbboard`): Flask API + display modes
- `fonts/` — `6x12` bitmap font, Noto Emoji for weather icons
- `config.example.toml` — settings; the real `config.toml` lives only on the Pi
- `deploy/rgb-board.service` — systemd unit
- `deploy.sh` — rsync to the Pi and restart the service

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

Open http://192.168.0.103:8080/ — modes, brightness, text and a 64×32 pixel editor that draws live on the panel.

## Claude Code indicator

`claude-plugin/` is a Claude Code plugin whose hooks show the session state on the panel with an animated Clawd:
start (waves), thinking, waiting for you, done (then back to the previous mode after `done_seconds`).

```sh
claude plugin marketplace add ~/IdeaProjects/rgb-board/claude-plugin
claude plugin install rgb-board@rgb-board-local
```

Toggle in Claude Code with `/plugin`, or on the panel side with the switch in the web panel.
Board address: `RGB_BOARD_URL` (default `http://192.168.0.103:8080`). The hooks run curl in the background
with all output discarded, so they cost no tokens and never block Claude.

## API (port 8080)

| Endpoint | |
|---|---|
| `POST /draw` | show an image (PNG body); resized to the panel if needed |
| `/claude?state=start\|thinking\|waiting\|done\|end` | Claude Code indicator |
| `/claude/enabled?value=0\|1` | turn the indicator on/off |
| `/clock`, `/weather`, `/serial` | switch mode (`serial` alternates clock and weather) |
| `/print?text=hello` | static text |
| `/brightness?value=0..100` | brightness |
| `/off` | stop and clear |
| `/status` | current mode and brightness |
