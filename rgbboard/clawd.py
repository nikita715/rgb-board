"""Clawd, the Claude Code mascot: one animation per Claude Code state.

The panel is 64x32: Clawd stands on the left (x 2..37), juggled balls fly over
its head, and the clock and weather sit in the right corners (Renderer.corner).
"""
import math
import random

from PIL import Image, ImageDraw

ORANGE = (217, 119, 87)  # #D97757
BLACK = (0, 0, 0)
BALLS = [(255, 255, 255), (90, 200, 250), (255, 196, 0)]

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
WIDTH = len(BODY[0]) * SX
X, Y = 2, 6    # sprite position: 6px of sky left above the head for the balls
WORK_ROTATION_SECONDS = 5  # "working" switches to a random animation this often (clawd_work.py)


def sprite(eyes=True, look=0, legs="stand", arms_up=()):
    grid = [list(row) for row in BODY]
    for side in arms_up:
        for col in ARMS[side]:
            grid[2][col] = " "
            grid[1][col] = "#"
    if eyes:
        for col, row in EYES:
            grid[row][col + look] = " "
    for col in LEGS[legs]:
        grid[4][col] = "#"
    return grid


def frame(size, x=X, y=Y, balls=(), **sprite_args):
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    # Balls first: the body hides the ones passing behind it.
    for (bx, by), color in zip(balls, BALLS):
        draw.rectangle((bx, by, bx + 1, by + 1), fill=color)
    for row, line in enumerate(sprite(**sprite_args)):
        for col, ch in enumerate(line):
            if ch == "#":
                x0, y0 = x + col * SX, y + row * SY
                draw.rectangle((x0, y0, x0 + SX - 1, y0 + SY - 1), fill=ORANGE)
    return image


def ball(u):
    """Position on the juggling loop, u in [0, 1): an arc over the head from the
    right hand to the left one, then back low behind the body."""
    cx, cy, rx, ry = X + WIDTH // 2 - 1, Y + 11, WIDTH // 2 - 1, Y + 10
    if u < 0.75:
        angle = math.pi * u / 0.75
        return round(cx + rx * math.cos(angle)), round(cy - ry * math.sin(angle))
    return round(cx - rx + 2 * rx * (u - 0.75) / 0.25), cy


class Animation:
    """An intro played once, then a loop. Frames are (image, seconds)."""

    def __init__(self, intro, loop):
        self.intro = intro
        self.loop = loop
        self.intro_seconds = sum(s for _, s in intro)
        self.loop_seconds = sum(s for _, s in loop)

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


class Rotation:
    """Switches to a random animation every `period` seconds, never the same one twice in a row.

    Like Animation, it's asked for the frame t seconds into the state; t going back
    means the state started again, which also picks a new animation."""

    def __init__(self, animations, period, rng=None):
        self.animations = list(animations)
        self.period = period
        self.rng = rng or random.Random()
        self.intro_seconds = 0
        self.slot = None
        self.current = None
        self.last_t = 0.0

    def at(self, t):
        slot = int(t // self.period)
        if slot != self.slot or t < self.last_t:
            choices = [a for a in self.animations if a is not self.current] or self.animations
            self.current = self.rng.choice(choices)
            self.slot = slot
        self.last_t = t
        image, left = self.current.at(t - slot * self.period)
        return image, min(left, (slot + 1) * self.period - t)


def animations(size):
    """state -> Animation, for the states in session.STATES."""
    f = lambda **kw: frame(size, **kw)
    blink = (f(eyes=False), 0.15)
    idle = [(f(), 3), blink, (f(), 2), (f(look=1), 1.2), (f(), 2.5), (f(look=-1), 1.2), (f(), 1.5), blink,
            (f(), 0.3), blink]

    wave = [(f(arms_up=("left",)), 0.3), (f(), 0.3)] * 4

    steps = 12
    juggle = [(f(balls=[ball((i / steps + k / 3) % 1) for k in range(3)],
                 arms_up=("right",) if i % 4 < 2 else ("left",)), 0.09)
              for i in range(steps)]

    jump = [(f(), 0.2), (f(y=Y - 3, arms_up=("left", "right")), 0.1), (f(y=Y - 5, arms_up=("left", "right")), 0.2),
            (f(y=Y - 3, arms_up=("left", "right")), 0.1), (f(), 0.15)]

    crawl = [(f(x=x, legs="step" if i % 2 else "stand"), 0.07) for i, x in enumerate(range(X, -WIDTH - 1, -2))]
    gone = [(Image.new("RGB", size), 1)]

    from rgbboard import clawd_work  # imports this module
    working = [Animation([], juggle)] + [Animation([], variant(size)) for variant in clawd_work.VARIANTS]

    return {
        "idle": Animation([], idle),
        "start": Animation(wave, idle),
        "working": Rotation(working, WORK_ROTATION_SECONDS),
        "attention": Animation([], jump),
        "end": Animation(crawl, gone),
    }
