"""What Claude Code is doing right now, as reported by the plugin hooks."""
import threading
import time

# idle: on boot, before any session. The rest come from the hooks:
# start (SessionStart), working (UserPromptSubmit), attention (Notification, Stop), end (SessionEnd).
STATES = ("idle", "start", "working", "attention", "end")


class Session:
    def __init__(self):
        self.lock = threading.Lock()
        self.state = "idle"
        self.since = time.monotonic()

    def set(self, state):
        with self.lock:
            if state != self.state:
                self.state, self.since = state, time.monotonic()

    def current(self):
        """(state, monotonic time the state started)."""
        with self.lock:
            return self.state, self.since
