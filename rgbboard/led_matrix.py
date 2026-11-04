"""A display that draws through led-matrix (github.com/sshcrack/led-matrix) instead of GPIO.

Frames go over UDP to the ExternalFrame plugin (led-matrix-plugin/), whose
"external_frame" scene shows them. The panel is taken over through led-matrix's
Scene Lab only while rgbboard has something to show; release() hands it back to
led-matrix's own scenes.
"""
import socket
import struct
import threading
import time

import requests

UDP_PLUGIN_ID = 0x10  # ExternalFrame::UdpPluginId
SCENE = "external_frame"
HEARTBEAT_SECONDS = 15  # Scene Lab drops the takeover after 45s without one
RESEND_SECONDS = 1      # the scene blanks after 5s without frames
RETRY_SECONDS = 5


class LedMatrixDisplay:
    # The panel is shared with led-matrix's scenes: Clawd shows only during a Claude session.
    shared = True

    def __init__(self, url, size, brightness):
        self.url = url.rstrip("/")
        self.size = size
        host = self.url.split("://", 1)[-1].split("/", 1)[0]
        name, _, port = host.partition(":")
        self.address = (name, int(port or 80))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.brightness = max(0, min(100, brightness))
        self.lock = threading.Lock()
        self.session_id = None
        self.next_claim = 0.0
        self.last_frame = None
        self.last_heartbeat = 0.0
        threading.Thread(target=self._keepalive, daemon=True).start()

    def show(self, image):
        frame = self._scaled(image.convert("RGB")).tobytes()
        with self.lock:
            self.last_frame = frame
            self._claim()
            self._send(frame)

    def set_brightness(self, value):
        with self.lock:
            self.brightness = max(0, min(100, value))

    def clear(self):
        self.release()

    def release(self):
        """Hands the panel back to led-matrix."""
        with self.lock:
            self.last_frame = None
            session_id, self.session_id = self.session_id, None
        if session_id is not None:
            self._post("/scene_lab/stop", {"session_id": session_id})

    # Brightness is applied here, on top of led-matrix's own, so it only dims Clawd.
    def _scaled(self, image):
        if self.brightness >= 100:
            return image
        k = self.brightness / 100
        return image.point(lambda v: round(v * k))

    def _send(self, frame):
        header = struct.pack(">BBBI", 0xAD, 0x01, UDP_PLUGIN_ID, len(frame))
        try:
            self.socket.sendto(header + frame, self.address)
        except OSError as e:
            print(f"[led-matrix] UDP send failed: {e}")

    def _claim(self):
        """Caller holds the lock. Starts the Scene Lab takeover if we don't hold one."""
        now = time.monotonic()
        if self.session_id is not None or now < self.next_claim:
            return
        reply = self._post("/scene_lab/start", {"scene": SCENE, "fps": 30})
        if reply is None:
            self.next_claim = now + RETRY_SECONDS
            return
        self.session_id = reply["session_id"]
        self.last_heartbeat = now
        print(f"[led-matrix] took the panel (session {self.session_id})")

    def _keepalive(self):
        while True:
            time.sleep(RESEND_SECONDS)
            with self.lock:
                if self.last_frame is None:
                    continue
                self._send(self.last_frame)
                session_id = self.session_id
                due = time.monotonic() - self.last_heartbeat >= HEARTBEAT_SECONDS
            if session_id is None:
                with self.lock:
                    if self.last_frame is not None:
                        self._claim()
                continue
            if due:
                ok = self._post("/scene_lab/heartbeat", {"session_id": session_id}) is not None
                with self.lock:
                    self.last_heartbeat = time.monotonic()
                    if not ok and self.session_id == session_id:
                        # Expired or taken over from the web UI: claim it again on the next frame.
                        self.session_id = None

    def _post(self, path, body):
        try:
            response = requests.post(self.url + path, json=body, timeout=2)
        except requests.RequestException as e:
            print(f"[led-matrix] {path} failed: {e}")
            return None
        if not response.ok:
            print(f"[led-matrix] {path} -> {response.status_code} {response.text[:200]}")
            return None
        return response.json()
