"""Clawd at work: the "working" animations, rotated at random (see clawd.Rotation).

Each function returns one loop of (image, seconds) frames. Coordinates assume the
64x32 layout from clawd.py: Clawd on the left, clock and weather in the right corners.
"""
import math
import random

from PIL import Image, ImageDraw

from rgbboard import clawd as C

X, Y, SX, SY = C.X, C.Y, C.SX, C.SY
OR = C.ORANGE
BLACK = (0, 0, 0)
WHITE = (230, 230, 240)
YELLOW = (255, 196, 0)


def scale(color, k):
    return tuple(max(0, min(255, round(v * k))) for v in color)


def canvas(size):
    image = Image.new("RGB", size)
    return image, ImageDraw.Draw(image)


def body(d, x=X, y=Y, color=OR, dy=0, eyes=True, look=0, pupils=None, **sprite_args):
    """Clawd. dy pushes the upper body down a little (bobbing). pupils=(top, bottom)
    draws pixel-level pupils inside the 2x5 eye slots instead: (0, 3) looks up, (2, 5) down."""
    grid = C.sprite(eyes=eyes and pupils is None, look=look, **sprite_args)
    for r, line in enumerate(grid):
        oy = dy if r < 4 else 0
        for c, ch in enumerate(line):
            if ch == "#":
                x0, y0 = x + c * SX, y + r * SY + oy
                d.rectangle((x0, y0, x0 + SX - 1, y0 + SY - 1), fill=color)
    if pupils is not None and eyes:
        top, bottom = pupils
        for col, _ in C.EYES:
            x0 = x + (col + look) * SX
            d.rectangle((x0, y + 5 + dy + top, x0 + 1, y + 5 + dy + bottom - 1), fill=BLACK)


def glyph(d, xy, rows, color):
    x, y = xy
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch == "#":
                d.point((x + c, y + r), fill=color)


def laptop(size):
    """Types on a laptop: eyes down, hands take turns pressing keys."""
    rnd = random.Random(1)
    frames = []
    for i in range(16):
        image, d = canvas(size)
        body(d, pupils=(2, 5))
        arm = X + 1 * SX if i % 2 == 0 else X + 15 * SX
        if i % 8 != 7:  # the pressing arm drops 2px
            d.rectangle((arm, 16, arm + 3, 17), fill=BLACK)
            d.rectangle((arm, 21, arm + 3, 22), fill=OR)
        d.rectangle((10, 17, 29, 27), fill=(105, 105, 120))  # back of the lid
        d.line((10, 17, 29, 17), fill=(160, 160, 175))
        glyph(d, (18, 20), [".#.", "###", ".#."], (255, 170, 140))
        d.rectangle((6, 28, 33, 30), fill=(65, 65, 75))  # base
        d.line((6, 28, 33, 28), fill=(130, 130, 145))
        for _ in range(2):
            d.point((rnd.randint(8, 31), 29), fill=(210, 210, 225))
        frames.append((image, 0.25 if i % 8 == 7 else 0.11))
    return frames


def think(size):
    """Looks up while dots appear over the head."""
    frames = []
    for look in (1, -1):
        for n in range(4):
            image, d = canvas(size)
            body(d, look=look, pupils=(0, 3))
            for k in range(n):
                d.rectangle((13 + 5 * k, 1, 14 + 5 * k, 2), fill=WHITE)
            frames.append((image, 0.6 if n == 3 else 0.4))
        image, d = canvas(size)
        body(d, eyes=False)
        frames.append((image, 0.13))
    return frames


def star(d, cx, cy, plus, diagonal, color):
    for k in range(1, plus + 1):
        for px, py in ((k, 0), (-k, 0), (0, k), (0, -k)):
            d.point((cx + px, cy + py), fill=color)
    for k in range(1, diagonal + 1):
        for px, py in ((k, k), (-k, k), (k, -k), (-k, -k)):
            d.point((cx + px, cy + py), fill=color)
    d.point((cx, cy), fill=WHITE)


def sparkle(size):
    """The Claude star pulses and turns over the head."""
    rays = [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)] + [(2, 0), (0, 2)] * 3 + [(2, 2), (2, 1), (1, 1), (1, 0)]
    frames = []
    for i, (plus, diagonal) in enumerate(rays):
        image, d = canvas(size)
        body(d, pupils=(0, 3), eyes=i != 8)
        star(d, 19, 2, plus, diagonal, (255, 140, 100))
        frames.append((image, 0.13))
    image, d = canvas(size)
    body(d, pupils=(0, 3))
    frames.append((image, 0.4))
    return frames


def orbit(size):
    """A spinner: a light with a tail circles over the head, the eyes follow it."""
    frames = []
    n = 16
    for i in range(n):
        image, d = canvas(size)
        a0 = 2 * math.pi * i / n
        for k in range(4, -1, -1):
            a = a0 - k * 2 * math.pi / n * 0.8
            px, py = round(18.5 + 14 * math.cos(a)), round(2 + 2 * math.sin(a))
            color = (255, 225, 205) if k == 0 else scale(OR, 1 - 0.2 * k)
            d.rectangle((px, py, px + 1, py + 1), fill=color)
        c = math.cos(a0)
        body(d, pupils=(0, 3), look=1 if c > 0.35 else -1 if c < -0.35 else 0)
        frames.append((image, 0.06))
    return frames


def run(size):
    """Runs in place, kicking up dust."""
    frames = []
    for i in range(8):
        image, d = canvas(size)
        for born in (0, 2, 4, 6):
            age = (i - born) % 8
            if age < 4:
                g = 130 - 30 * age
                d.rectangle((6 - 2 * age, 29 - age // 2, 7 - 2 * age, 30 - age // 2), fill=(g, g, g))
        body(d, dy=i % 2, look=1, legs="step" if i % 2 else "stand")
        frames.append((image, 0.08))
    return frames


def hammer(size):
    """Hammers something on the right; sparks fly on the hit."""
    brown, grey = (150, 95, 50), (160, 160, 175)

    def up(d):
        body(d, look=1, arms_up=("right",))
        d.line((36, 13, 36, 5), fill=brown)
        d.rectangle((34, 2, 38, 4), fill=grey)

    def swing(d):
        body(d, look=1)
        d.line((36, 17, 40, 12), fill=brown)
        d.line((39, 10, 42, 14), fill=grey, width=2)

    def down(d, sparks):
        body(d, look=1, dy=1 if sparks else 0)
        d.line((36, 19, 40, 25), fill=brown)
        d.rectangle((39, 26, 43, 30), fill=grey)
        if sparks:
            for p in ((38, 24), (45, 25), (44, 22), (41, 23), (46, 28)):
                d.point(p, fill=YELLOW)

    frames = []
    for draw, seconds in ((up, 0.3), (swing, 0.06), (lambda d: down(d, True), 0.12),
                          (lambda d: down(d, False), 0.18), (swing, 0.08)):
        image, d = canvas(size)
        draw(d)
        frames.append((image, seconds))
    return frames


NOTE = ["..#", "..#", "###", "##."]


def dance(size):
    """Sways with arms up while notes float away."""
    poses = [dict(x=X - 1, arms_up=("left",), legs="step"), dict(),
             dict(x=X + 1, arms_up=("right",), legs="step"), dict()]
    notes = [(0, 1, (90, 200, 250)), (4, 34, (255, 120, 200)), (2, 40, YELLOW)]
    frames = []
    for i in range(16):
        image, d = canvas(size)
        body(d, **poses[(i // 2) % 4])
        for born, nx, color in notes:
            age = (i - born) % 8
            glyph(d, (nx + (age // 3) % 2, 6 - age), NOTE, color)
        frames.append((image, 0.15))
    return frames


def rain(size):
    """Green code rain falls behind Clawd."""
    rnd = random.Random(3)
    columns = [(x, rnd.randrange(40), rnd.randint(3, 7)) for x in range(1, 46, 3)]
    frames = []
    for t in range(40):
        image, d = canvas(size)
        for x, phase, length in columns:
            head = (t + phase) % 40 - 7
            for k in range(length):
                color = (190, 255, 190) if k == 0 else (0, round(40 + 170 * (1 - k / length)), 30)
                d.point((x, head - k), fill=color)
        body(d, eyes=t != 20, pupils=(1, 5))
        frames.append((image, 0.06))
    return frames


VARIANTS = (laptop, think, sparkle, orbit, run, hammer, dance, rain)
