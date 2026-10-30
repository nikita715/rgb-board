import threading


class ModeRunner:
    """Runs one display mode at a time in a background thread."""

    def __init__(self):
        self.name = None
        self.thread = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

    def start(self, name, func, *args):
        with self.lock:
            self._stop()
            self.stop_event = threading.Event()
            self.thread = threading.Thread(target=func, args=(self.stop_event, *args), daemon=True)
            self.thread.start()
            self.name = name
            print(f"[modes] {name} started")

    def stop(self):
        with self.lock:
            self._stop()

    def _stop(self):
        if self.thread and self.thread.is_alive():
            print(f"[modes] stopping {self.name}")
            self.stop_event.set()
            self.thread.join()
        self.name = None
        self.thread = None


def clock(stop, display, renderer):
    while not stop.is_set():
        display.show(renderer.clock())
        stop.wait(1)


def weather(stop, display, renderer, weather_source):
    while not stop.is_set():
        display.show(renderer.weather(weather_source.get()))
        stop.wait(2)


def serial(stop, display, renderer, weather_source):
    """Alternates clock and weather every 10 seconds."""
    seconds = 0
    while not stop.is_set():
        if (seconds // 10) % 2 == 0:
            display.show(renderer.clock())
        else:
            display.show(renderer.weather(weather_source.get()))
        stop.wait(2)
        seconds += 2


def text(stop, display, renderer, message):
    display.show(renderer.text(message))
    stop.wait()
