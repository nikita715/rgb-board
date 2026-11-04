import io
import threading
from pathlib import Path

from flask import Flask, jsonify, request
from PIL import Image

from rgbboard import clawd, modes

# Read at import time: after the matrix drops privileges, files under /home/nikita are unreadable.
INDEX_HTML = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")

CLAUDE_STATES = ("start", "thinking", "waiting", "done", "end")


def create_app(display, renderer, weather_source, runner, claude_config):
    app = Flask(__name__)

    mode_args = {
        "clock": (modes.clock, display, renderer),
        "weather": (modes.weather, display, renderer, weather_source),
        "serial": (modes.serial, display, renderer, weather_source),
    }

    def start_mode(name):
        runner.start(name, *mode_args[name])

    @app.route("/")
    def index():
        return INDEX_HTML

    @app.route("/clock", endpoint="clock")
    @app.route("/weather", endpoint="weather")
    @app.route("/serial", endpoint="serial")
    def switch_mode():
        start_mode(request.endpoint)
        return jsonify({"status": f"{request.endpoint} started"})

    @app.route("/print")
    def print_text():
        message = request.args.get("text", "")
        runner.start("text", modes.still, display, renderer.text(message))
        return jsonify({"status": "text started"})

    @app.post("/draw")
    def draw():
        try:
            image = Image.open(io.BytesIO(request.get_data())).convert("RGB")
        except Exception:
            return jsonify({"error": "body must be an image"}), 400
        if image.size != renderer.size:
            image = image.resize(renderer.size, Image.Resampling.NEAREST)
        # While drawing, frames arrive many times per second: push them straight
        # to the display instead of restarting the mode thread for each one.
        if runner.name == "draw":
            display.show(image)
            # Keep the latest drawing, so the Claude indicator resumes to it.
            runner.args = (display, image)
        else:
            runner.start("draw", modes.still, display, image)
        return jsonify({"status": "drawn"})

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

    # --- Claude Code indicator ------------------------------------------------
    # Driven by the Claude Code plugin hooks. While a session is active the
    # indicator takes over the panel; on "done" (after a pause) and "end" it
    # brings back whatever was shown before.

    animations = clawd.animations(renderer.size, renderer.text_font)
    claude = {"enabled": claude_config["enabled"], "state": None, "resume": None, "generation": 0}
    claude_lock = threading.Lock()

    def claude_resume():
        """Caller holds claude_lock."""
        resume = claude["resume"]
        claude["state"], claude["resume"] = None, None
        if runner.name != "claude":
            return  # switched to another mode by hand meanwhile
        if resume and resume[0]:
            runner.start(*resume)
        else:
            runner.stop()
            display.clear()

    def resume_after_done(generation):
        with claude_lock:
            if claude["generation"] == generation:
                claude_resume()

    @app.route("/claude")
    def claude_state():
        state = request.args.get("state")
        if state not in CLAUDE_STATES:
            return jsonify({"error": f"state must be one of {', '.join(CLAUDE_STATES)}"}), 400
        with claude_lock:
            if not claude["enabled"]:
                return jsonify({"status": "ignored"})
            claude["generation"] += 1
            if state == "end":
                claude_resume()
            elif state != claude["state"] or runner.name != "claude":
                if runner.name != "claude":
                    claude["resume"] = runner.snapshot()
                claude["state"] = state
                runner.start("claude", modes.animate, display, *animations[state])
                if state == "done":
                    timer = threading.Timer(
                        claude_config["done_seconds"], resume_after_done, (claude["generation"],))
                    timer.daemon = True
                    timer.start()
        return jsonify({"status": state})

    @app.route("/claude/enabled")
    def claude_enabled():
        value = request.args.get("value")
        if value not in ("0", "1"):
            return jsonify({"error": "value must be 0 or 1"}), 400
        with claude_lock:
            claude["enabled"] = value == "1"
            if not claude["enabled"]:
                claude_resume()
        return jsonify({"claude_enabled": claude["enabled"]})

    @app.route("/status")
    def status():
        width, height = renderer.size
        return jsonify({
            "mode": runner.name,
            "brightness": display.brightness,
            "width": width,
            "height": height,
            "claude_enabled": claude["enabled"],
            "claude_state": claude["state"],
        })

    return app, start_mode
