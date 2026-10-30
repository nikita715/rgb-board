from flask import Flask, jsonify, request

from rgbboard import modes


def create_app(display, renderer, weather_source, runner):
    app = Flask(__name__)

    mode_args = {
        "clock": (modes.clock, display, renderer),
        "weather": (modes.weather, display, renderer, weather_source),
        "serial": (modes.serial, display, renderer, weather_source),
    }

    def start_mode(name):
        runner.start(name, *mode_args[name])

    @app.route("/clock", endpoint="clock")
    @app.route("/weather", endpoint="weather")
    @app.route("/serial", endpoint="serial")
    def switch_mode():
        start_mode(request.endpoint)
        return jsonify({"status": f"{request.endpoint} started"})

    @app.route("/print")
    def print_text():
        message = request.args.get("text", "")
        runner.start("text", modes.text, display, renderer, message)
        return jsonify({"status": "text started"})

    @app.route("/brightness")
    def brightness():
        try:
            value = int(request.args["value"])
        except (KeyError, ValueError):
            return jsonify({"error": "value must be an integer 0-100"}), 400
        display.set_brightness(value)
        return jsonify({"status": "brightness set", "value": display.brightness})

    @app.route("/off")
    def off():
        runner.stop()
        display.clear()
        return jsonify({"status": "off"})

    @app.route("/status")
    def status():
        return jsonify({"mode": runner.name, "brightness": display.brightness})

    return app, start_mode
