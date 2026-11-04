"""Hand-drawn pixel art for the corner overlay: a 3x5 font and 8x7 weather icons."""

# '#' is lit, anything else is off. Glyphs are 5 rows tall, 1px apart.
GLYPHS = {
    "0": ["###", "#.#", "#.#", "#.#", "###"],
    "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["###", "..#", "###", "#..", "###"],
    "3": ["###", "..#", ".##", "..#", "###"],
    "4": ["#.#", "#.#", "###", "..#", "..#"],
    "5": ["###", "#..", "###", "..#", "###"],
    "6": ["###", "#..", "###", "#.#", "###"],
    "7": ["###", "..#", "..#", ".#.", ".#."],
    "8": ["###", "#.#", "###", "#.#", "###"],
    "9": ["###", "#.#", "###", "..#", "###"],
    ":": [".", "#", ".", "#", "."],
    "-": ["...", "...", "###", "...", "..."],
    "°": ["##", "##", "..", "..", ".."],
    " ": [".", ".", ".", ".", "."],
}


def text_width(text):
    glyphs = [GLYPHS[c] for c in text if c in GLYPHS]
    return sum(len(g[0]) for g in glyphs) + max(len(glyphs) - 1, 0)


def text(draw, xy, text, fill, right=False):
    """Draws text with its top-left (or top-right, if right=True) corner at xy."""
    x, y = xy
    if right:
        x -= text_width(text) - 1
    for c in text:
        glyph = GLYPHS.get(c)
        if glyph is None:
            continue
        for row, line in enumerate(glyph):
            for col, ch in enumerate(line):
                if ch == "#":
                    draw.point((x + col, y + row), fill=fill)
        x += len(glyph[0]) + 1


WHITE = (170, 175, 190)
SUN = (255, 196, 0)
RAIN = (60, 140, 255)
SNOW = (200, 230, 255)
COLORS = {"w": WHITE, "y": SUN, "b": RAIN, "c": SNOW}

WEATHER = {
    "clear": [
        "...y....",
        ".y...y..",
        "..yyy...",
        "y.yyy.y.",
        "..yyy...",
        ".y...y..",
        "...y....",
    ],
    "partly": [
        "....y.y.",
        ".....yyy",
        "..ww.yyy",
        ".wwww.y.",
        "wwwwww..",
        ".wwwww..",
        "........",
    ],
    "cloudy": [
        "........",
        "....ww..",
        "..wwwwww",
        ".wwwwwww",
        "wwwwwwww",
        ".wwwwww.",
        "........",
    ],
    "rain": [
        "...ww...",
        ".wwwww..",
        "wwwwwww.",
        ".wwwww..",
        "..b..b..",
        ".b..b...",
        "b..b....",
    ],
    "snow": [
        "...ww...",
        ".wwwww..",
        "wwwwwww.",
        ".wwwww..",
        "........",
        ".c..c..c",
        "c..c..c.",
    ],
    "storm": [
        "...ww...",
        ".wwwww..",
        "wwwwwww.",
        ".wwwww..",
        "...yy...",
        "..yy....",
        "...y....",
    ],
    "fog": [
        "........",
        "wwwwww..",
        "........",
        ".wwwwww.",
        "........",
        "wwwwww..",
        "........",
    ],
}
ICON_WIDTH = 8


def icon(draw, xy, rows):
    x, y = xy
    for row, line in enumerate(rows):
        for col, ch in enumerate(line):
            if ch in COLORS:
                draw.point((x + col, y + row), fill=COLORS[ch])
