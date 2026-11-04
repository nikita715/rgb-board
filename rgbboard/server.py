import io
import threading
from pathlib import Path

from flask import Flask, jsonify, request
from PIL import Image

from rgbboard import clawd, modes
from rgbboard.session import Session, tool_kind

# Read at import time: after the matrix drops privileges, files under /home/nikita are unreadable.
INDEX_HTML = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")

CLAUDE_STATES = ("start", "thinking", "tool", "waiting", "done", "end", "sleep")


def create_app(display, renderer, weather_source, runner, claude_config):
    app = Flask(__name__)

    session = Session(claude_config["done_seconds"], claude_config["sleep_minutes"])
    animations = clawd.animations(renderer.size, renderer.text_font)

    mode_args = {
        "clawd": (modes.clawd, display, renderer, weather_source, session, animations),
        "clock": (modes.clock, display, renderer),
        "weather": (modes.weather, display, renderer, weather_source),
        "serial": (modes.serial, display, renderer, weather_source),
    }

    def start_mode(name):
        runner.start(name, *mode_args[name])

    @app.route("/")
    def index():
        return INDEX_HTML

    @app.route("/clawd", endpoint="clawd")
    @app.route("/clock", endpoint="clock")
    @app.route("/weather", endpoint="weather")
    @app.route("/serial", endpoint="serial")
    def switch_mode():
        with claude_lock:
            claude["resume"] = None  # picked by hand: Claude events won't switch away from it
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
    # Driven by the Claude Code plugin hooks. Events set what Clawd acts out in the
    # "clawd" mode. If another mode (text, a drawing, the big clock) is on, Claude
    # takes the panel over and gives it back after "done" (with a pause) or "end".

    claude = {"enabled": claude_config["enabled"], "resume": None, "generation": 0}
    claude_lock = threading.Lock()

    def claude_resume():
        """Caller holds claude_lock."""
        resume, claude["resume"] = claude["resume"], None
        if resume is None or runner.name != "clawd":
            return  # nothing taken over, or switched to another mode by hand meanwhile
        if resume[0]:
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
        tool = tool_kind(request.args.get("tool")) if state == "tool" else None
        with claude_lock:
            if not claude["enabled"]:
                return jsonify({"status": "ignored"})
            claude["generation"] += 1
            session.set("idle" if state == "end" else state, tool)
            if state == "end":
                claude_resume()
                return jsonify({"status": state})
            if runner.name != "clawd":
                claude["resume"] = runner.snapshot()
                start_mode("clawd")
            if state == "done" and claude["resume"] is not None:
                timer = threading.Timer(
                    claude_config["done_seconds"], resume_after_done, (claude["generation"],))
                timer.daemon = True
                timer.start()
        return jsonify({"status": state, "tool": tool})

    @app.route("/claude/enabled")
    def claude_enabled():
        value = request.args.get("value")
        if value not in ("0", "1"):
            return jsonify({"error": "value must be 0 or 1"}), 400
        with claude_lock:
            claude["enabled"] = value == "1"
            if not claude["enabled"]:
                session.set("idle")
                claude_resume()
        return jsonify({"claude_enabled": claude["enabled"]})

    @app.route("/status")
    def status():
        width, height = renderer.size
        state, tool, _ = session.current()
        return jsonify({
            "mode": runner.name,
            "brightness": display.brightness,
            "width": width,
            "height": height,
            "claude_enabled": claude["enabled"],
            "claude_state": state,
            "claude_tool": tool,
        })

    return app, start_mode
