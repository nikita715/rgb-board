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

## API (port 8080)

| Endpoint | |
|---|---|
| `/clock`, `/weather`, `/serial` | switch mode (`serial` alternates clock and weather) |
| `/print?text=hello` | static text |
| `/brightness?value=0..100` | brightness |
| `/off` | stop and clear |
| `/status` | current mode and brightness |
