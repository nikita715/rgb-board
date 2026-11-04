"""What Claude Code is doing right now, as reported by the plugin hooks."""
import threading
import time

TOOL_KINDS = {
    "read": {"Read", "Grep", "Glob", "LS", "NotebookRead"},
    "edit": {"Edit", "Write", "MultiEdit", "NotebookEdit"},
    "bash": {"Bash", "PowerShell", "BashOutput", "KillShell", "Monitor"},
    "web": {"WebFetch", "WebSearch"},
    "agent": {"Agent", "Task", "Workflow", "SendMessage"},
}


def tool_kind(name):
    """Groups a tool name into one of the TOOL_KINDS animations, or None (plain thinking)."""
    for kind, names in TOOL_KINDS.items():
        if name in names:
            return kind
    return None


class Session:
    """The state Clawd shows. "done" turns into "idle" by itself, and with no hook
    events for sleep_minutes Clawd falls asleep (also covers interrupted turns,
    which send no Stop event)."""

    def __init__(self, done_seconds, sleep_minutes):
        self.done_seconds = done_seconds
        self.sleep_seconds = sleep_minutes * 60
        self.lock = threading.Lock()
        self.state, self.tool = "idle", None
        self.since = self.last_event = time.monotonic()

    def set(self, state, tool=None):
        now = time.monotonic()
        with self.lock:
            if (state, tool) != self.current_locked(now)[:2]:
                self.state, self.tool, self.since = state, tool, now
            self.last_event = now

    def current(self):
        """(state, tool kind, monotonic time the state started)."""
        with self.lock:
            return self.current_locked(time.monotonic())

    def current_locked(self, now):
        state, tool, since = self.state, self.tool, self.since
        if state == "done" and now - since > self.done_seconds:
            state, tool, since = "idle", None, since + self.done_seconds
        if state != "sleep" and now - self.last_event > self.sleep_seconds:
            state, tool, since = "sleep", None, self.last_event + self.sleep_seconds
        return state, tool, since
