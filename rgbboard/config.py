import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"

DEFAULTS = {
    "matrix": {
        "backend": "rgbmatrix",  # rgbmatrix (GPIO) | led-matrix (through sshcrack/led-matrix)
        "rows": 32,
        "cols": 64,
        "brightness": 15,
        "gpio_slowdown": 3,
        "hardware_mapping": "adafruit-hat",
    },
    "led_matrix": {
        "url": "http://127.0.0.1:8080",
        "brightness": 100,  # on top of led-matrix's own brightness
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8081,  # 8080 belongs to led-matrix
        "default_mode": "clawd",
    },
    "weather": {
        "api_key": "",
        "city": "Saint Petersburg,RU",
        "refresh_seconds": 600,
    },
    "style": {
        "color": [120, 100, 200],
    },
    "claude": {
        "enabled": True,
    },
}


def load(path=ROOT / "config.toml"):
    config = {section: dict(values) for section, values in DEFAULTS.items()}
    if path.exists():
        with path.open("rb") as f:
            for section, values in tomllib.load(f).items():
                config.setdefault(section, {}).update(values)
    return config
