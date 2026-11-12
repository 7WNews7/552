"""Text as vector paths (Telegram forbids text layers): glyph outlines from Montserrat (OFL)."""
import os
from functools import lru_cache

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

from .geometry import Bez, bbox_of

FONT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         'fonts', 'Montserrat[wght].ttf')


class _Pen(BasePen):
    def __init__(self, glyphset):
        super().__init__(glyphset)
        self.paths = []
        self.cur = None
        self.last = None

    def _moveTo(self, p):
        self.cur = Bez(closed=True).add(p)
        self.last = p

    def _lineTo(self, p):
        self.cur.add(p)
        self.last = p

    def _curveToOne(self, p1, p2, p3):
        lx, ly = self.last
        self.cur.o[-1] = [p1[0] - lx, p1[1] - ly]
        self.cur.add(p3, (p2[0] - p3[0], p2[1] - p3[1]))
        self.last = p3

    def _closePath(self):
        c = self.cur
        if len(c.v) > 1 and abs(c.v[-1][0] - c.v[0][0]) < 1e-6 and abs(c.v[-1][1] - c.v[0][1]) < 1e-6:
            c.i[0] = c.i[-1]
            c.v.pop()
            c.i.pop()
            c.o.pop()
        self.paths.append(c)
        self.cur = None

    def _endPath(self):
        self._closePath()


class Font:
    def __init__(self, weight=800, path=FONT_PATH):
        f = TTFont(path)
        if 'fvar' in f:
            f = instancer.instantiateVariableFont(f, {'wght': weight})
        self.font = f
        self.glyphs = f.getGlyphSet()
        self.cmap = f.getBestCmap()
        self.upm = f['head'].unitsPerEm
        self.cap = f['OS/2'].sCapHeight
        self.hmtx = f['hmtx']

    @lru_cache(maxsize=None)
    def glyph(self, ch):
        name = self.cmap[ord(ch)]
        pen = _Pen(self.glyphs)
        self.glyphs[name].draw(pen)
        return pen.paths, self.hmtx[name][0]


@lru_cache(maxsize=None)
def font(weight=800):
    return Font(weight)


def glyphs(text, cx, cy, cap, weight=800, tracking=0.0, width=1.0):
    """Lay out `text` centred at (cx, cy); `cap` = capital-letter height in px.

    Returns a list of (paths, (gcx, gcy)) per visible character so letters can be
    animated individually. `tracking` is extra spacing in em, `width` squeezes /
    stretches horizontally."""
    f = font(weight)
    sc = cap / f.cap
    x = 0.0
    laid = []
    for ch in text:
        paths, adv = f.glyph(ch)
        if paths:
            laid.append((x, paths, adv))
        x += adv + tracking * f.upm
    total = (x - tracking * f.upm) * sc * width
    ox = cx - total / 2
    base = cy + cap / 2
    out = []
    for gx, paths, adv in laid:
        moved = [p.map(lambda X, Y, gx=gx: (ox + (gx + X) * sc * width, base - Y * sc)) for p in paths]
        b = bbox_of(moved)
        out.append((moved, ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)))
    return out


def text(text, cx, cy, cap, weight=800, tracking=0.0, width=1.0):
    """All glyph paths of `text` as one flat list (fill them with one style)."""
    out = []
    for paths, _ in glyphs(text, cx, cy, cap, weight, tracking, width):
        out += paths
    return out


def fit_cap(text, max_width, cap, weight=800, tracking=0.0):
    """Largest cap height <= cap so that the text is no wider than max_width."""
    ps = globals()['text'](text, 256, 256, 100, weight, tracking)
    b = bbox_of(ps)
    w100 = b[2] - b[0]
    return min(cap, 100 * max_width / w100)
