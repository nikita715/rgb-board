"""Clawd, the Claude Code mascot: one animation per Claude Code state.

The panel is 64x32: Clawd stands on the left (x 2..37), the state icon sits in the
middle of the right column (x 39..63, y 8..23), and the clock and weather go in its
corners (drawn by Renderer.corner).
"""
from PIL import Image, ImageDraw

from rgbboard import pixels

ORANGE = (217, 119, 87)  # #D97757
DIM = (70, 38, 28)
YELLOW = (255, 196, 0)
GREEN = (48, 209, 88)
LIGHT = (190, 190, 200)
CYAN = (90, 200, 250)
BLACK = (0, 0, 0)

# Decoded from the Claude Code logo quadrant characters: 18 x 5 sprite pixels.
BODY = [
    "   ############   ",
    "   ############   ",
    " ################ ",
    "   ############   ",
    "                  ",
]
EYES = [(5, 1), (12, 1)]
LEGS = {"stand": [4, 6, 11, 13], "step": [3, 5, 12, 14]}
ARMS = {"left": (1, 2), "right": (15, 16)}
SX, SY = 2, 5  # terminal quadrants are twice as tall as wide
X, Y = 2, 4    # sprite position


def sprite(eyes=True, look=0, legs="stand", arms_up=()):
    grid = [list(row) for row in BODY]
    for side in arms_up:
        for col in ARMS[side]:
            grid[2][col] = " "
            grid[1][col] = "#"
    if eyes is True:
        for col, row in EYES:
            grid[row][col + look] = " "
    for col in LEGS[legs]:
        grid[4][col] = "#"
    return grid


def frame(size, font, y=Y, icon=None, eyes=True, look=0, **sprite_args):
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    for row, line in enumerate(sprite(eyes=eyes, look=look, **sprite_args)):
        for col, ch in enumerate(line):
            if ch == "#":
                x0, y0 = X + col * SX, y + row * SY
                draw.rectangle((x0, y0, x0 + SX - 1, y0 + SY - 1), fill=ORANGE)
    for col, row in EYES:
        x0, y0 = X + col * SX, y + row * SY
        if eyes == "happy":  # ^ ^
            draw.point([(x0 - 1, y0 + 3), (x0, y0 + 2), (x0 + 1, y0 + 2), (x0 + 2, y0 + 3)], fill=BLACK)
        elif eyes == "closed":  # - -
            draw.line((x0 - 1, y0 + 3, x0 + 2, y0 + 3), fill=BLACK)
    if icon:
        icon(draw, font)
    return image


# --- State icons (right column) ----------------------------------------------

def hello(draw, font):
    draw.text((42, 10), "hi!", font=font, fill=ORANGE)


def dots(step):
    def icon(draw, font):
        for i, x in enumerate((43, 50, 57)):
            draw.rectangle((x, 14, x + 2, 16), fill=ORANGE if i == step % 3 else DIM)
    return icon


def bang(draw, font):
    draw.rectangle((50, 9, 52, 18), fill=YELLOW)
    draw.rectangle((50, 20, 52, 22), fill=YELLOW)


def check(draw, font):
    draw.line([(44, 16), (48, 20), (58, 10)], fill=GREEN, width=3)


def magnifier(step):
    """Read / Grep / Glob: a magnifying glass sweeping side to side."""
    def icon(draw, font):
        cx = 47 + (0, 2, 4, 2)[step % 4]
        draw.ellipse((cx - 4, 9, cx + 4, 17), outline=LIGHT, width=2)
        draw.line((cx + 3, 16, cx + 6, 19), fill=ORANGE, width=2)
    return icon


WORDS = "#### ###### ### ##### ## ####### ### ##### #### ### ###### "


def typing(step):
    """Edit / Write: lines of "text" appearing, with a cursor."""
    def icon(draw, font):
        written = step * 4
        for i, y in enumerate((10, 14, 18)):
            length = max(0, min(20, written - i * 20))
            words = WORDS[i * 7:i * 7 + 20]
            for col in range(length):
                if words[col] == "#":
                    draw.line((41 + col, y, 41 + col, y + 1), fill=LIGHT)
            if 0 < written - i * 20 <= 20 or (i == 2 and written > 60):
                draw.rectangle((41 + length + 1, y - 1, 41 + length + 2, y + 2), fill=ORANGE)
    return icon


def terminal(step):
    """Bash: a prompt with a blinking cursor."""
    def icon(draw, font):
        draw.line([(42, 10), (46, 14), (42, 18)], fill=GREEN, width=2)
        if step % 2 == 0:
            draw.rectangle((49, 17, 56, 18), fill=LIGHT)
    return icon


def globe(step):
    """WebFetch / WebSearch: a spinning globe."""
    def icon(draw, font):
        draw.ellipse((45, 9, 57, 21), outline=CYAN)
        draw.line((45, 15, 57, 15), fill=CYAN)
        w = (0, 2, 4, 6, 4, 2)[step % 6]
        if w:
            draw.ellipse((51 - w, 9, 51 + w, 21), outline=CYAN)
        else:
            draw.line((51, 9, 51, 21), fill=CYAN)
    return icon


def helpers(step):
    """Agent / Task: three tiny Clawds hopping in turn."""
    def icon(draw, font):
        for i, x in enumerate((41, 48, 55)):
            y = 12 if i == step % 3 else 15
            draw.rectangle((x, y, x + 5, y + 2), fill=ORANGE)
            draw.point([(x + 1, y + 1), (x + 4, y + 1)], fill=BLACK)
            draw.point([(x + 1, y + 3), (x + 4, y + 3)], fill=ORANGE)
    return icon


def zzz(step):
    def icon(draw, font):
        for i, (x, y) in enumerate(((42, 18), (48, 13), (54, 8))):
            if i < step % 4:
                pixels.text(draw, (x, y), "z", LIGHT if i == 2 else DIM if i == 0 else ORANGE)
    return icon


TOOL_ICONS = {
    # kind: (icon factory, steps, seconds per frame)
    "read": (magnifier, 4, 0.3),
    "edit": (typing, 17, 0.1),
    "bash": (terminal, 2, 0.45),
    "web": (globe, 6, 0.15),
    "agent": (helpers, 3, 0.3),
}


# --- Animations ---------------------------------------------------------------

class Animation:
    """An intro played once, then a loop. Frames are (image, seconds)."""

    def __init__(self, intro, loop):
        self.intro = intro
        self.loop = loop or intro[-1:]
        self.intro_seconds = sum(s for _, s in intro)
        self.loop_seconds = sum(s for _, s in self.loop)

    def at(self, t):
        """The frame shown t seconds after the start, and seconds until the next one."""
        frames = self.intro
        if t >= self.intro_seconds:
            t = (t - self.intro_seconds) % self.loop_seconds
            frames = self.loop
        for image, seconds in frames:
            if t < seconds:
                return image, seconds - t
            t -= seconds
        return frames[-1][0], 0.05


def animations(size, font):
    """(state, tool kind or None) -> Animation."""
    f = lambda **kw: frame(size, font, **kw)
    blink = (f(eyes=False), 0.15)
    idle = [(f(), 3), blink, (f(), 2), (f(look=1), 1.2), (f(), 2.5), (f(look=-1), 1.2), (f(), 1.5), blink,
            (f(), 0.3), blink]

    def walking(icon, steps, seconds):
        count = steps
        while count * seconds < 0.9:  # long enough for a full step cycle
            count += steps
        legs = lambda i: "stand" if int(i * seconds / 0.25) % 2 == 0 else "step"
        return [(f(legs=legs(i), icon=icon(i % steps)), seconds) for i in range(count)]

    result = {
        ("idle", None): Animation([], idle),
        ("start", None): Animation([(f(arms_up=("left",), icon=hello), 0.3), (f(icon=hello), 0.3)] * 3, idle),
        ("thinking", None): Animation([], walking(dots, 3, 0.25)),
        ("waiting", None): Animation([], [(f(icon=bang), 0.35), (f(y=1, arms_up=("left", "right")), 0.35)]),
        ("done", None): Animation(
            [(f(y=1, eyes="happy", arms_up=("left", "right"), icon=check), 0.25),
             (f(eyes="happy", icon=check), 0.25)] * 2,
            [(f(eyes="happy", icon=check), 1)],
        ),
        ("sleep", None): Animation([], [(f(y=Y + i % 2, eyes="closed", icon=zzz(i)), 0.7) for i in range(4)]),
    }
    result[("tool", None)] = result[("thinking", None)]
    for kind, args in TOOL_ICONS.items():
        result[("tool", kind)] = Animation([], walking(*args))
    return result
