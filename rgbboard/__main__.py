from rgbboard import config
from rgbboard.display import Display
from rgbboard.modes import ModeRunner
from rgbboard.render import Renderer
from rgbboard.server import create_app
from rgbboard.weather import Weather


def main():
    cfg = config.load()
    # Load fonts before the matrix: it drops root privileges to 'daemon' on init,
    # and daemon can't read files under /home/nikita.
    renderer = Renderer((cfg["matrix"]["cols"], cfg["matrix"]["rows"]), cfg["style"]["color"])
    display = Display(cfg["matrix"])
    weather_source = Weather(**cfg["weather"])
    runner = ModeRunner()

    app, start_mode = create_app(display, renderer, weather_source, runner)
    if cfg["server"]["default_mode"]:
        start_mode(cfg["server"]["default_mode"])
    # load_dotenv=False: after the privilege drop, daemon can't resolve the cwd
    # under /home/nikita, which crashes Flask's .env lookup.
    app.run(
        host=cfg["server"]["host"],
        port=cfg["server"]["port"],
        debug=False,
        use_reloader=False,
        load_dotenv=False,
    )


if __name__ == "__main__":
    main()
