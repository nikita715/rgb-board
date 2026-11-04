import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"

DEFAULTS = {
    "matrix": {
        "rows": 32,
        "cols": 64,
        "brightness": 15,
        "gpio_slowdown": 3,
        "hardware_mapping": "adafruit-hat",
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8080,
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
        "done_seconds": 4,
        "sleep_minutes": 10,
    },
}


def load(path=ROOT / "config.toml"):
    config = {section: dict(values) for section, values in DEFAULTS.items()}
    if path.exists():
        with path.open("rb") as f:
            for section, values in tomllib.load(f).items():
                config.setdefault(section, {}).update(values)
    return config
