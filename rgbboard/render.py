import datetime

from PIL import Image, ImageDraw, ImageFont

from rgbboard import pixels
from rgbboard.config import FONTS


class Renderer:
    def __init__(self, size, color):
        self.size = size
        self.color = tuple(color)
        self.text_font = ImageFont.load(str(FONTS / "6x12.pil"))
        self.emoji_font = ImageFont.truetype(str(FONTS / "NotoEmoji-Light.ttf"), 24)

    def blank(self):
        image = Image.new("RGB", self.size)
        return image, ImageDraw.Draw(image)

    @staticmethod
    def clock_text():
        return datetime.datetime.now().strftime("%H:%M")

    def clock(self):
        now = self.clock_text()
        image, draw = self.blank()
        left, top, right, bottom = draw.textbbox((0, 0), now, font=self.text_font)
        x = (self.size[0] - (right - left)) // 2 - left
        y = (self.size[1] - (bottom - top)) // 2 - top
        draw.text((x, y), now, font=self.text_font, fill=self.color)
        return image

    def text(self, text):
        image, draw = self.blank()
        draw.text((0, 10), text, font=self.text_font, fill=self.color)
        return image

    def weather(self, data):
        if data is None:
            return self.text("no data")
        image, draw = self.blank()
        draw.text((5, 1), data.icon, font=self.emoji_font, fill=self.color)
        draw.text((45, 0), data.temp, font=self.text_font, fill=self.color)
        draw.text((45, 19), data.temp_feels, font=self.text_font, fill=self.color)
        return image

    def corner(self, image, data):
        """A copy of image with a small clock top-right and the weather bottom-right."""
        image = image.copy()
        draw = ImageDraw.Draw(image)
        right = self.size[0] - 1
        pixels.text(draw, (right, 1), self.clock_text(), self.color, right=True)
        if data is not None:
            bottom = self.size[1] - 6
            pixels.text(draw, (right, bottom), data.temp, self.color, right=True)
            if data.kind in pixels.WEATHER:
                x = right - pixels.text_width(data.temp) - 1 - pixels.ICON_WIDTH
                pixels.icon(draw, (x, bottom - 1), pixels.WEATHER[data.kind])
        return image
