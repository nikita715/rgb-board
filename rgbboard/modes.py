import threading


class ModeRunner:
    """Runs one display mode at a time in a background thread."""

    def __init__(self):
        self.name = None
        self.func = None
        self.args = ()
        self.thread = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

    def start(self, name, func, *args):
        with self.lock:
            self._stop()
            self.stop_event = threading.Event()
            self.thread = threading.Thread(target=func, args=(self.stop_event, *args), daemon=True)
            self.thread.start()
            self.name, self.func, self.args = name, func, args
            print(f"[modes] {name} started")

    def stop(self):
        with self.lock:
            self._stop()

    def snapshot(self):
        """The current mode as start() arguments, to bring it back later."""
        return (self.name, self.func, *self.args)

    def _stop(self):
        if self.thread and self.thread.is_alive():
            print(f"[modes] stopping {self.name}")
            self.stop_event.set()
            self.thread.join()
        self.name, self.func, self.args = None, None, ()
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


def still(stop, display, image):
    display.show(image)
    stop.wait()


def animate(stop, display, intro, loop):
    """Plays the intro frames once, then repeats the loop frames. Frames are (image, seconds)."""
    for image, seconds in intro:
        if stop.is_set():
            return
        display.show(image)
        stop.wait(seconds)
    if not loop:
        stop.wait()
        return
    while not stop.is_set():
        for image, seconds in loop:
            if stop.is_set():
                return
            display.show(image)
            stop.wait(seconds)
