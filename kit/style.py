"""KRONOS STAFF palette and style presets ("ice on a winter night").

Rules of the style (keep every emoji consistent):
  * main silhouettes: icy gradient fill + dark navy OUTLINE drawn behind (OW px visible)
  * light comes from the top-left: white gloss highlight, darker blue at the bottom
  * accents: white twinkle sparkles, snow caps, soft radial glow (subtle!)
  * colours stay in the cold range; warm colours only as tiny accents (cat eyes, nose)
"""
from .lottie import gfill, fill, stroke, mix

# ------------------------------------------------------------- palette
OUTLINE = '#0a1534'   # contour of every main shape
NAVY_D = '#0d1d45'
NAVY = '#16306b'
BLUE_D = '#1f4fb2'
BLUE = '#2f72e4'
BLUE_L = '#57a2ff'
SKY = '#7cc0ff'
ICE = '#a6d8ff'
ICE_L = '#d4eeff'
SNOW = '#f3faff'
WHITE = '#ffffff'
SILVER = '#c9d9ec'
STEEL = '#8aa3c4'
TEAL = '#56e0d6'
MINT = '#8ff5d9'
VIOLET = '#8b7bff'
LILAC = '#c3b8ff'
PINK = '#ff9fc0'
ROSE = '#f2789c'
GOLD = '#ffd66b'
AMBER = '#f5a83a'
RED = '#ff5a6e'
GREEN = '#46d6a0'

OW = 9          # visible outline width (stroke drawn behind with 2*OW)
OW_THIN = 6

# ------------------------------------------------------------- gradient stop sets (top -> bottom)
G_ICE = [(0.0, '#eef8ff'), (0.42, '#9fd2ff'), (1.0, '#3b7ce8')]
G_ICE_SOFT = [(0.0, '#ffffff'), (0.5, '#c9e8ff'), (1.0, '#7db8f5')]
G_DEEP = [(0.0, '#5aa8ff'), (0.55, '#2f6fe0'), (1.0, '#1a3f9c')]
G_NIGHT = [(0.0, '#2b5fc4'), (1.0, '#0f2763')]
G_SILVER = [(0.0, '#ffffff'), (0.45, '#d9e8f8'), (1.0, '#89aedb')]
G_SNOW = [(0.0, '#ffffff'), (0.65, '#eaf5ff'), (1.0, '#b9daf7')]
G_AURORA = [(0.0, '#8ff5d9'), (0.5, '#56c8ff'), (1.0, '#8b7bff')]
G_TEAL = [(0.0, '#c8fff6'), (0.5, '#56e0d6'), (1.0, '#1f8fb0')]
G_VIOLET = [(0.0, '#e2dcff'), (0.5, '#9d8cff'), (1.0, '#5640d6')]
G_GOLD = [(0.0, '#fff4c2'), (0.5, '#ffd66b'), (1.0, '#e09a2a')]
G_PINK = [(0.0, '#ffe3ee'), (0.5, '#ff9fc0'), (1.0, '#e0607f')]
G_RED = [(0.0, '#ffc2c9'), (0.5, '#ff6f82'), (1.0, '#c9304a')]
G_GREEN = [(0.0, '#d8fff0'), (0.5, '#5fe0b0'), (1.0, '#1f9e78')]
G_FUR_GRAY = [(0.0, '#d5dbe6'), (0.5, '#a7b0c0'), (1.0, '#6f7a8f')]
G_FUR_DARK = [(0.0, '#4a5470'), (1.0, '#1b2136')]


def vgrad(stops, y0, y1, x=256, opacity=None, o=100):
    """Vertical linear gradient from y0 (first stop) to y1 (last stop)."""
    return gfill(stops, [x, y0], [x, y1], opacity=opacity, o=o)


def dgrad(stops, p0, p1, opacity=None, o=100):
    """Linear gradient between two arbitrary points."""
    return gfill(stops, list(p0), list(p1), opacity=opacity, o=o)


def rgrad(stops, cx, cy, r, opacity=None, o=100):
    """Radial gradient centred at (cx, cy) with radius r."""
    return gfill(stops, [cx, cy], [cx + r, cy], kind='radial', opacity=opacity, o=o)


def ice(y0, y1, stops=None, x=256):
    return vgrad(stops or G_ICE, y0, y1, x=x)


def white(o=100):
    return fill(WHITE, o)


def navy_stroke(w):
    return stroke(OUTLINE, w)


def tint(c, t):
    """Lighten (t > 0, towards white) or darken (t < 0, towards outline navy)."""
    return mix(c, WHITE, t) if t >= 0 else mix(c, OUTLINE, -t)
