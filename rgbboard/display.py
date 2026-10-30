import threading

from rgbmatrix import RGBMatrix, RGBMatrixOptions


class Display:
    def __init__(self, matrix_config):
        options = RGBMatrixOptions()
        for key, value in matrix_config.items():
            setattr(options, key, value)
        self.matrix = RGBMatrix(options=options)
        # Draw into an offscreen canvas and swap on vsync to avoid flicker.
        self.canvas = self.matrix.CreateFrameCanvas()
        self.brightness = matrix_config["brightness"]
        self.lock = threading.Lock()

    def show(self, image):
        with self.lock:
            self.canvas.brightness = self.brightness
            self.canvas.SetImage(image.convert("RGB"))
            self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def set_brightness(self, value):
        with self.lock:
            self.brightness = max(0, min(100, value))
            self.matrix.brightness = self.brightness

    def clear(self):
        with self.lock:
            self.canvas.Clear()
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
