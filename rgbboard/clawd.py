"""Clawd, the Claude Code mascot, animated for the Claude Code indicator."""
from PIL import Image, ImageDraw

ORANGE = (217, 119, 87)  # #D97757
DIM = (70, 38, 28)
YELLOW = (255, 196, 0)
GREEN = (48, 209, 88)

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
X, Y = 2, 4    # sprite position; the right side of the panel holds the state icon


def sprite(eyes=True, legs="stand", arms_up=()):
    grid = [list(row) for row in BODY]
    for side in arms_up:
        for col in ARMS[side]:
            grid[2][col] = " "
            grid[1][col] = "#"
    if eyes is True:
        for col, row in EYES:
            grid[row][col] = " "
    for col in LEGS[legs]:
        grid[4][col] = "#"
    return grid


def frame(size, font, y=Y, icon=None, **sprite_args):
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    for row, line in enumerate(sprite(**sprite_args)):
        for col, ch in enumerate(line):
            if ch == "#":
                x0, y0 = X + col * SX, y + row * SY
                draw.rectangle((x0, y0, x0 + SX - 1, y0 + SY - 1), fill=ORANGE)
    if sprite_args.get("eyes") == "happy":
        # ^ ^ carved over the eye positions
        for col, row in EYES:
            x0, y0 = X + col * SX, y + row * SY
            draw.point([(x0 - 1, y0 + 3), (x0, y0 + 2), (x0 + 1, y0 + 2), (x0 + 2, y0 + 3)], fill=(0, 0, 0))
    if icon:
        icon(draw, font)
    return image


def hello(draw, font):
    draw.text((42, 10), "hi!", font=font, fill=ORANGE)


def dots(active):
    def icon(draw, font):
        for i, x in enumerate((42, 49, 56)):
            draw.rectangle((x, 15, x + 2, 17), fill=ORANGE if i == active else DIM)
    return icon


def bang(draw, font):
    draw.rectangle((50, 6, 52, 19), fill=YELLOW)
    draw.rectangle((50, 23, 52, 25), fill=YELLOW)


def check(draw, font):
    draw.line([(43, 16), (48, 21), (58, 9)], fill=GREEN, width=3)


def animations(size, font):
    """state -> (intro, loop), each a list of (image, seconds). The intro plays once, then the loop repeats."""
    f = lambda **kw: frame(size, font, **kw)
    idle = [(f(), 2.5), (f(eyes=False), 0.15)]
    return {
        "start": (
            [(f(arms_up=("left",), icon=hello), 0.3), (f(icon=hello), 0.3)] * 3,
            idle,
        ),
        "thinking": (
            [],
            [(f(legs="stand" if i % 2 == 0 else "step", icon=dots(i % 3)), 0.25) for i in range(6)],
        ),
        "waiting": (
            [],
            [(f(icon=bang), 0.35), (f(y=1, arms_up=("left", "right")), 0.35)],
        ),
        "done": (
            [(f(y=1, eyes="happy", arms_up=("left", "right"), icon=check), 0.25),
             (f(eyes="happy", icon=check), 0.25)] * 2,
            [(f(eyes="happy", icon=check), 1)],
        ),
    }
