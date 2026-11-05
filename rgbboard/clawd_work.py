"""Clawd at work: the "working" animations, rotated at random (see clawd.Rotation).

Each function returns one loop of (image, seconds) frames. Coordinates assume the
64x32 layout from clawd.py: Clawd on the left, clock and weather in the right corners.
"""
import math
import random

from PIL import Image, ImageDraw

from rgbboard import clawd as C, pixels as P

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


def juggle(size):
    """Juggles three balls over the head."""
    steps = 12
    return [(C.frame(size, balls=[C.ball((i / steps + k / 3) % 1) for k in range(3)],
                     arms_up=("right",) if i % 4 < 2 else ("left",)), 0.09)
            for i in range(steps)]


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


def bezier(d, start, control, end, color, steps=80):
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * control[0] + t ** 2 * end[0]
        y = (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * control[1] + t ** 2 * end[1]
        d.point((round(x), round(y)), fill=color)


def jump_rope(size):
    """Skips rope: the rope swings over the head, down in front and under the feet as he hops."""
    rope = (90, 200, 250)
    # Per frame: lowest point of the rope, whether it passes in front of the body, how high he hops.
    apex = [1, 9, 18, 26, 31, 22, 12, 4]
    front = [False, True, True, True, True, False, False, False]
    lift = [0, 0, 0, 2, 3, 2, 0, 0]
    frames = []
    for k in range(len(apex)):
        image, d = canvas(size)
        y = Y - lift[k]
        hand_y = y + 12
        left, right = (X + 2, hand_y), (X + 33, hand_y)
        control = ((left[0] + right[0]) / 2, 2 * apex[k] - hand_y)  # puts the curve's middle at apex
        if not front[k]:
            bezier(d, left, control, right, rope)
        body(d, y=y, pupils=(2, 5) if front[k] else (0, 5))
        if front[k]:
            bezier(d, left, control, right, rope)
        frames.append((image, 0.09))
    return frames


def spin(size):
    """Arms, legs and eyes come off and circle clockwise around the body, all together."""
    core = [(c, r) for r, line in enumerate(C.BODY) for c, ch in enumerate(line)
            if ch == "#" and not (r == 2 and c in C.ARMS["left"] + C.ARMS["right"])]
    cx, cy, rx, ry = X + 17.5, Y + 10.5, 17, 12  # orbit of the limbs around the body
    ex, ey, erx, ery = X + 17.5, Y + 7, 6, 3     # orbit of the eyes inside the face

    def start_angle(x, y):
        return math.atan2((y - cy) / ry, (x - cx) / rx)

    # Limbs as (start angle, width, height), starting where they normally are.
    limbs = [(math.pi, 4, 5), (0.0, 4, 5)]
    for col in C.LEGS["stand"]:
        limbs.append((start_angle(X + col * SX + 1, Y + 4 * SY + 2), 2, 5))

    frames = []
    n = 16
    for i in range(n):
        image, d = canvas(size)
        turn = 2 * math.pi * i / n  # y points down, so a growing angle turns clockwise
        for c, r in core:
            x0, y0 = X + c * SX, Y + r * SY
            d.rectangle((x0, y0, x0 + SX - 1, y0 + SY - 1), fill=OR)
        for angle, w, h in limbs:
            px = round(cx + rx * math.cos(angle + turn) - w / 2)
            py = round(cy + ry * math.sin(angle + turn) - h / 2)
            d.rectangle((px, py, px + w - 1, py + h - 1), fill=OR)
        for angle in (math.pi, 0.0):
            px = round(ex + erx * math.cos(angle + turn) - 1)
            py = round(ey + ery * math.sin(angle + turn) - 1)
            d.rectangle((px, py, px + 1, py + 2), fill=BLACK)
        frames.append((image, 0.5 if i == 0 else 0.07))
    return frames


PAPER = (235, 235, 240)


def paperwork(size):
    """Pulls papers out of a filing cabinet on the right and tosses them over his head."""
    cabinet, dark, light = (105, 105, 120), (70, 70, 82), (150, 150, 165)
    rnd = random.Random(5)
    period, every, lifetime = 24, 8, 15
    tosses = [(b, rnd.uniform(-2.3, -1.6)) for b in range(4, period, every)]  # (frame thrown, x speed)
    frames = []
    for i in range(period):
        image, d = canvas(size)
        phase = i % every
        drawer_open = phase <= 3
        # The cabinet; the top drawer slides out while he rummages in it.
        d.rectangle((38, 13, 46, 30), fill=cabinet)
        for y in (19, 25):
            d.line((38, y, 46, y), fill=dark)
        drawer = 36 if drawer_open else 38
        d.rectangle((drawer, 14, drawer + 8, 18), fill=light)
        d.point((drawer + 4, 16), fill=dark)
        for y in (22, 28):
            d.point((42, y), fill=dark)
        if phase == 4:  # throws: arm up, paper in hand
            body(d, look=1, pupils=(0, 3), arms_up=("right",))
            d.rectangle((33, 7, 35, 9), fill=PAPER)
        else:
            body(d, look=1, pupils=(0, 3) if phase in (5, 6) else (1, 5))
            if phase <= 2:  # reaches into the drawer
                d.rectangle((36, 17, 38, 19), fill=OR)
            elif phase == 3:  # pulls a sheet out
                d.rectangle((35, 14, 37, 17), fill=PAPER)
                d.rectangle((35, 17, 37, 19), fill=OR)
        for thrown, vx in tosses:
            age = (i - thrown) % period
            if age == 0 or age > lifetime:
                continue
            px = round(34 + vx * age)
            py = round(8 - 3.2 * age + 0.3 * age * age)
            if py > 29:
                continue
            # Flutters: flips between lying flat and edge-on.
            w, h = (3, 2) if age % 2 else (2, 3)
            d.rectangle((px, py, px + w - 1, py + h - 1), fill=PAPER)
        frames.append((image, 0.1))
    return frames


def lerp(keys, i):
    """Position at frame i from keyframes [(frame, x, y), ...], linear in between."""
    for (f0, x0, y0), (f1, x1, y1) in zip(keys, keys[1:]):
        if f0 <= i <= f1:
            u = (i - f0) / (f1 - f0) if f1 > f0 else 0
            return round(x0 + (x1 - x0) * u), round(y0 + (y1 - y0) * u)
    return keys[-1][1], keys[-1][2]


def mini(d, x, y, sx=1, sy=3, color=OR, **sprite_args):
    """A smaller Clawd: the same sprite with sx x sy blocks instead of 2 x 5."""
    for r, line in enumerate(C.sprite(**sprite_args)):
        for c, ch in enumerate(line):
            if ch == "#":
                d.rectangle((x + c * sx, y + r * sy, x + c * sx + sx - 1, y + r * sy + sy - 1), fill=color)


def plus(d, x, y, color):
    d.line((x, y + 1, x + 2, y + 1), fill=color)
    d.line((x + 1, y, x + 1, y + 2), fill=color)


ARROW = ["#....", "##...", "###..", "####.", "#####", "##...", "#.#..", "..#.."]
BANG = ["#", "#", "#", ".", "#"]
QUESTION = ["###", "..#", ".##", "...", ".#."]
CHECK = ["......#", ".....#.", "#...#..", ".#.#...", "..#...."]


def cursor(size):
    """A mouse cursor teases him around the panel until he jumps and eats it."""
    keys = [(0, 64, 14), (8, 44, 12), (12, 47, 9), (16, 44, 12), (22, 20, -1), (26, 22, -1), (30, 42, 3),
            (32, 45, 8), (34, 41, 12), (36, 45, 15), (40, 42, 10)]
    frames = []
    for i in range(62):
        image, d = canvas(size)
        cx, cy = lerp(keys, min(i, 40))
        eaten = i >= 43
        look = 1 if cx > 30 else -1 if cx < 10 else 0
        pupils = (0, 3) if cy < 8 else (2, 5) if cy > 20 else (1, 4)
        if 26 <= i < 29:  # swats at it
            body(d, look=look, pupils=(0, 3), arms_up=("left", "right"))
        elif 38 <= i < 40:  # crouches
            body(d, dy=2, look=1, pupils=pupils)
        elif 40 <= i < 44:  # jumps at it
            body(d, x=X + 4, y=Y - 4, look=1, arms_up=("right",), pupils=(1, 4))
        elif 44 <= i < 52:  # chews
            body(d, dy=(i // 2) % 2, pupils=(3, 5))
        else:
            body(d, look=0 if eaten else look, pupils=(0, 5) if eaten else pupils)
        if not eaten:
            glyph(d, (cx, cy), ARROW, WHITE)
        frames.append((image, 0.08))
    return frames


def golf(size):
    """Drives the ball off the right edge; it comes back from the left and hits him on the head."""
    shaft, ball = (170, 170, 180), WHITE
    frames = []
    for i in range(50):
        image, d = canvas(size)
        if i < 6 or 9 <= i < 10:  # addresses the ball / hits it
            body(d, look=1, pupils=(2, 5))
            d.line((35, 18, 40, 29), fill=shaft)
            d.line((39, 30, 41, 30), fill=shaft)
        elif i < 9:  # backswing
            body(d, look=1, pupils=(2, 5), arms_up=("right",))
            d.line((35, 12, 39, 5), fill=shaft)
            d.line((38, 4, 40, 4), fill=shaft)
        elif i < 36:  # watches it fly away, then waits
            body(d, look=1, pupils=(0, 3) if i < 22 else (1, 5))
            d.line((35, 18, 40, 29), fill=shaft)
        else:  # dizzy, stars around the head
            body(d, x=X + (1 if i % 2 else -1) if i < 44 else X, eyes=False)
            for k, (ex, _) in enumerate(C.EYES):
                x0 = X + ex * SX - 1
                d.line((x0, Y + 6, x0 + 2, Y + 8), fill=BLACK)
                d.line((x0, Y + 8, x0 + 2, Y + 6), fill=BLACK)
            for k in range(3):
                a = (i - 36) * 0.8 + k * 2 * math.pi / 3
                d.point((round(19 + 10 * math.cos(a)), round(2 + 2 * math.sin(a))), fill=YELLOW)
        if i < 10:
            bx, by = 41, 29
        elif i < 20:  # flies off the right edge
            u = (i - 10) / 10
            bx, by = round(41 + 26 * u), round(29 - 30 * math.sin(math.pi * u * 0.8))
        elif i < 30:
            bx, by = None, None
        elif i < 36:  # comes back from the left, straight at his head
            bx, by = lerp([(30, -2, 10), (36, 14, 5)], i)
        else:  # bounces off and rolls back to the tee
            bx, by = lerp([(36, 14, 5), (40, 22, -1), (43, 30, 29), (49, 41, 29)], i)
        if bx is not None:
            d.rectangle((bx, by, bx + 1, by + 1), fill=ball)
        frames.append((image, 0.08))
    return frames


BUG = [".##.", "####", ".##."]


def bug(size):
    """A bug crawls in; he grabs it, eats it, and shows a green check: fixed."""
    green, legs = (70, 210, 90), (40, 120, 50)
    frames = []
    for i in range(37):
        image, d = canvas(size)
        if i < 10:
            body(d, look=1, pupils=(2, 5))
            bx, by = 47 - i, 28
        elif i < 12:  # crouches and stretches his arm to it
            body(d, dy=2, look=1, pupils=(2, 5))
            d.line((35, 19, 38, 26), fill=OR, width=2)
            bx, by = 38, 28
        elif i < 15:  # brings it to his mouth
            body(d, look=1, pupils=(1, 5))
            bx, by = [(34, 22), (29, 18), (None, None)][i - 12]
        elif i < 23:  # chews
            body(d, dy=(i // 2) % 2, pupils=(3, 5))
            if i < 17:
                d.point((24, Y + 12 + (i // 2) % 2), fill=legs)
            bx = by = None
        else:  # fixed
            body(d, arms_up=("left", "right") if i < 27 else ())
            if (i // 2) % 2 == 0:
                glyph(d, (16, 0), CHECK, green)
            bx = by = None
        if bx is not None:
            glyph(d, (bx, by), BUG, green)
            if i < 12:  # little legs
                for lx in (bx, bx + 3):
                    d.point((lx, by + 2 + i % 2 - 0), fill=legs)
        frames.append((image, 0.1))
    return frames


def clone(size):
    """Splits into two small Clawds that argue, then merge back."""
    frames = []
    for i in range(48):
        image, d = canvas(size)
        if i < 5:
            body(d)
        elif i < 11:  # buzzes
            body(d, x=X + (1 if i % 2 else -1), color=scale(OR, 1 + 0.06 * (i - 5)))
        elif i == 11 or i == 35:  # flash
            body(d, color=(255, 240, 225))
        elif i < 15:  # the halves slide apart
            u = (i - 11) / 3
            mini(d, round(11 - 7 * u), 16, look=1)
            mini(d, round(11 + 13 * u), 16, look=-1)
        elif i < 31:  # argue: take turns hopping and shouting
            left_turn = (i // 4) % 2 == 0
            mini(d, 4, 14 if left_turn and i % 4 < 2 else 16, look=1, arms_up=("right",) if left_turn else ())
            mini(d, 24, 14 if not left_turn and i % 4 < 2 else 16, look=-1, arms_up=("left",) if not left_turn else ())
            if left_turn:
                glyph(d, (12, 8), BANG, YELLOW)
            else:
                glyph(d, (32, 8), QUESTION, WHITE)
        elif i < 35:  # run into each other
            u = (i - 31) / 3
            mini(d, round(4 + 7 * u), 16, look=1, legs="step" if i % 2 else "stand")
            mini(d, round(24 - 13 * u), 16, look=-1, legs="stand" if i % 2 else "step")
        elif i < 41:  # shakes it off
            body(d, look=1 if i % 2 else -1)
        else:
            body(d, eyes=i != 44)
        frames.append((image, 0.1))
    return frames


def pixels(size):
    """Stretches his arm to the clock, steals its pixels one by one and stacks them on the left.
    The tower collapses and the pixels fly back home."""
    purple = (120, 100, 200)
    x0 = X + 6  # moved right, to leave room for the tower
    slots = [(0, 29), (3, 29), (6, 29), (1, 26), (4, 26), (2, 23)]
    frames = []

    def tower(d, n):
        for sx_, sy_ in slots[:n]:
            d.rectangle((sx_, sy_, sx_ + 1, sy_ + 1), fill=purple)

    for n in range(len(slots)):
        tx, ty = slots[n]
        for f in range(8):
            image, d = canvas(size)
            tower(d, n)
            reaching = f < 5
            body(d, x=x0, look=1 if reaching else -1, pupils=(0, 3) if reaching else (1, 5),
                 arms_up=("right",) if f >= 5 else ())
            if f < 5:  # the arm stretches to the clock and back
                reach = (0.5, 1, 1, 0.6, 0.2)[f]
                hx, hy = round(x0 + 34 + 6 * reach), round(Y + 11 - 9 * reach)
                d.line((x0 + 34, Y + 11, hx, hy), fill=OR, width=2)
                if f >= 2:
                    d.rectangle((hx, hy - 1, hx + 1, hy), fill=purple)
            else:  # tosses it over his head onto the tower
                u = (f - 4) / 4
                px = round(x0 + 34 + (tx - x0 - 34) * u)
                py = round(Y + 2 + (ty - Y - 2) * u - 14 * math.sin(math.pi * u))
                if f < 7:
                    d.rectangle((px, py, px + 1, py + 1), fill=purple)
                else:
                    d.rectangle((tx, ty, tx + 1, ty + 1), fill=purple)
            frames.append((image, 0.08))
    for f in range(10):  # the tower collapses, the pixels fly back to the clock
        image, d = canvas(size)
        body(d, x=x0, look=-1, pupils=(1, 5), arms_up=("left", "right") if f >= 6 else ())
        u = f / 9
        for k, (sx_, sy_) in enumerate(slots):
            px = round(sx_ + (50 - sx_) * u)
            py = round(sy_ + (2 - sy_) * u - 10 * math.sin(math.pi * u) + (k % 3))
            d.rectangle((px, py, px + 1, py + 1), fill=purple)
        frames.append((image, 0.08))
    return frames


FISH = ["..###.#", ".######", "..###.#"]
BOOT = ["##..", "##..", "####", "####"]
NULL = ["........#.#", "##..#.#.#.#", "#.#.#.#.#.#", "#.#.#.#.#.#", "#.#.###.#.#"]


def fishing(size):
    """Wades with a rod; catches a fish, then a boot, then null."""
    water, wave = (25, 60, 150), (90, 150, 240)
    rod, line = (150, 95, 50), (150, 150, 160)
    catches = [(FISH, (150, 200, 230), "happy"), (BOOT, (130, 80, 40), "meh"), (NULL, WHITE, "huh")]
    frames = []
    for catch, color, mood in catches:
        for i in range(30):
            image, d = canvas(size)
            yank = 13 <= i
            tip = (46, 5) if not yank else (42, 1)
            if i >= 20 and mood == "happy":
                body(d, arms_up=("left", "right"))
            elif i >= 20 and mood == "meh":
                body(d, look=-1, pupils=(2, 4))
            elif i >= 20:
                body(d, look=1, pupils=(0, 3))
                glyph(d, (19, 0), QUESTION, YELLOW)
            else:
                body(d, look=1, pupils=(2, 5) if i < 10 else (0, 5), eyes=i != 5,
                     arms_up=("right",) if yank else ())
            if 10 <= i < 13:
                glyph(d, (19, 0), BANG, YELLOW)
            d.line((35, 17 if not yank else 11, *tip), fill=rod)
            for x in range(0, 47):
                d.point((x, 29 + (1 if (x + i) % 8 < 4 else 0)), fill=water)
                d.rectangle((x, 30, x, 31), fill=water)
            for x in range(-(i % 8), 47, 8):
                d.point((x, 28 + (1 if (x // 8) % 2 else 0)), fill=wave)
            if i < 10:  # waiting: the bobber bobs
                by = 26 + (i // 3) % 2
                d.line((*tip, 45, by), fill=line)
                d.point((45, by), fill=(230, 50, 50))
                d.point((45, by + 1), fill=WHITE)
            elif i < 13:  # a bite: it goes under
                d.line((*tip, 45, 29), fill=line)
            else:  # the catch on the line
                u = min(1, (i - 13) / 6)
                cx = round(45 + (tip[0] - 4 - 45) * u)
                cy = round(28 + (tip[1] + 3 - 28) * u)
                d.line((*tip, cx + 2, cy), fill=line)
                glyph(d, (cx - (len(catch[0]) - 4 if catch is NULL else 0), cy), catch, color)
            frames.append((image, 0.1))
    return frames


def gym(size):
    """Presses a barbell; a counter goes up each rep, until he drops it and collapses."""
    bar, plate, sweat = (170, 170, 180), (80, 80, 95), (90, 170, 255)

    def barbell(d, y):
        d.line((0, y, 39, y), fill=bar)
        d.rectangle((1, y - 4, 3, y + 4), fill=plate)
        d.rectangle((36, y - 4, 38, y + 4), fill=plate)

    def counter(d, n, rise):
        plus(d, 40, 9 - rise, WHITE)
        P.text(d, (44, 8 - rise), str(n), WHITE)

    heights = [17, 17, 17, 17, 16, 10, 2, 2, 10, 17, 17, 17]
    frames = []
    for rep in range(1, 5):
        for f, y in enumerate(heights):
            image, d = canvas(size)
            if f in (3, 4):  # strains
                y += 1 if f == 3 else -1
                body(d, pupils=(2, 4), dy=1)
                d.point((7, Y + 2 + f), fill=sweat)
            else:
                body(d, arms_up=("left", "right") if y < 12 else ())
            barbell(d, y)
            if f >= 6:
                counter(d, rep, f - 6)
            frames.append((image, 0.08))
    for f in range(6):  # the fifth rep: shakes, can't get it up
        image, d = canvas(size)
        body(d, pupils=(3, 5), dy=1 + f % 2)
        barbell(d, 16 + f % 2)
        d.point((7, Y + 2 + f), fill=sweat)
        d.point((31, Y + 4 + f), fill=sweat)
        frames.append((image, 0.08))
    for f, y in enumerate((22, 29, 26, 29)):  # drops it
        image, d = canvas(size)
        body(d, dy=3, pupils=(3, 5))
        barbell(d, y)
        frames.append((image, 0.08))
    for f in range(8):  # lies there, exhausted
        image, d = canvas(size)
        body(d, dy=3, pupils=(4, 5) if f < 6 else (2, 5))
        barbell(d, 29)
        if f < 4:
            d.point((30 + f, Y + 3 + f), fill=sweat)
        frames.append((image, 0.12))
    return frames


# (id, button label, frames) — every one plays in the "working" rotation and can be picked in the work mode.
VARIANTS = (
    ("juggle", "Жонглирует", juggle),
    ("laptop", "Ноутбук", laptop),
    ("think", "Думает", think),
    ("sparkle", "Звёздочка", sparkle),
    ("orbit", "Спиннер", orbit),
    ("run", "Бег", run),
    ("hammer", "Молоток", hammer),
    ("dance", "Танец", dance),
    ("rain", "Код льётся", rain),
    ("jump_rope", "Скакалка", jump_rope),
    ("spin", "Прокрут", spin),
    ("paperwork", "Бумаги", paperwork),
    ("cursor", "Курсор", cursor),
    ("golf", "Гольф", golf),
    ("bug", "Ест жука", bug),
    ("clone", "Клон", clone),
    ("pixels", "Ворует пиксели", pixels),
    ("fishing", "Рыбалка", fishing),
    ("gym", "Качалка", gym),
)
LABELS = {name: label for name, label, _ in VARIANTS}


def animations(size):
    """id -> looping Animation, in VARIANTS order."""
    return {name: C.Animation([], frames(size)) for name, _, frames in VARIANTS}
