"""Shared KRONOS motifs: crown, paw print, snow cap. Coordinates are in the 512 canvas."""
from .lottie import part, group
from .geometry import P, rounded, circle_path, Bez
from . import style as S


def _mapper(cx, cy, k, ox=256, oy=266):
    return lambda b: b.map(lambda x, y: (cx + (x - ox) * k, cy + (y - oy) * k))


def crown(cx=256, cy=266, w=420, ow=S.OW, gems=True, body_stops=None, band_stops=None):
    """KRONOS crown (three peaks with orbs, gem band). Returns dict:
        parts   -- painter-ordered parts
        shine   -- Bez list covering body + band (feed to fx.shine)
        tips    -- orb centres [(x, y)] (good sparkle spots)
        gem     -- centre gem position
    Design box at w=420: x 43..469, y 80..408 around centre (256, 266)."""
    k = w / 420.0
    M = _mapper(cx, cy, k)
    Y = lambda y: cy + (y - 266) * k
    X = lambda x: cx + (x - 256) * k
    body = M(rounded([(112, 352), (70, 166), (178, 256), (256, 124), (334, 256), (442, 166), (400, 352)],
                     [8, 12, 18, 12, 18, 12, 8]))
    band = M(rounded([(98, 340), (414, 340), (414, 408), (98, 408)], 26))
    orbs = [M(circle_path(70, 150, 27)), M(circle_path(256, 106, 31)), M(circle_path(442, 150, 27))]
    parts = [
        part(body, fill=S.vgrad(body_stops or S.G_SILVER, Y(124), Y(352)), outline=ow, name='crown_body'),
        # soft inner shade along the bottom of the body
        part(M(rounded([(118, 352), (110, 300), (402, 300), (394, 352)], 6)),
             fill=S.vgrad([(0, '#89aedb'), (1, '#5e86c4')], Y(300), Y(352), opacity=[(0, 0), (1, 0.55)]),
             name='crown_shade'),
        # gloss stripe on the left flank
        part(M(P('M 92 186 C 104 236 116 290 124 334 L 140 334 C 132 290 118 236 104 200 Z')),
             fill=S.WHITE, o=70, name='crown_gloss'),
        part(*orbs, fill=S.vgrad(S.G_ICE_SOFT, Y(76), Y(180)), outline=ow, name='crown_orbs'),
        part(*[M(circle_path(x - 9, y - 10, 8)) for x, y in ((70, 150), (256, 106), (442, 150))],
             fill=S.WHITE, o=90, name='orb_gloss'),
        part(band, fill=S.vgrad(band_stops or S.G_DEEP, Y(340), Y(408)), outline=ow, name='crown_band'),
        part(M(rounded([(118, 350), (394, 350), (394, 358), (118, 358)], 4)), fill=S.WHITE, o=35, name='band_gloss'),
    ]
    if gems:
        parts += [
            part(M(rounded([(256, 350), (290, 374), (256, 398), (222, 374)], 6)),
                 fill=S.vgrad(S.G_ICE_SOFT, Y(350), Y(398)), outline=(S.OUTLINE, ow * 0.6), name='gem_c'),
            part(M(circle_path(166, 374, 14)), M(circle_path(346, 374, 14)),
                 fill=S.vgrad(S.G_TEAL, Y(360), Y(388)), outline=(S.OUTLINE, ow * 0.55), name='gems_side'),
            part(M(rounded([(256, 196), (284, 236), (256, 276), (228, 236)], 7)),
                 fill=S.vgrad(S.G_DEEP, Y(196), Y(276)), outline=(S.OUTLINE, ow * 0.6), name='gem_body'),
            part(M(P('M 256 210 L 268 230 L 256 230 Z')), fill=S.WHITE, o=85, name='gem_glint'),
        ]
    return {'parts': parts, 'shine': [body, band], 'tips': [(X(70), Y(150)), (X(256), Y(106)), (X(442), Y(150))],
            'gem': (X(256), Y(374)), 'k': k}


def paw(cx, cy, size=1.0, rot=0.0):
    """Paw print as a list of Bez (pad + 4 toes). size=1 -> about 200 x 190 px."""
    pad = P('M 0 -10 C 54 -10 100 34 100 70 C 100 104 72 114 46 106 C 30 101 16 98 0 98 '
            'C -16 98 -30 101 -46 106 C -72 114 -100 104 -100 70 C -100 34 -54 -10 0 -10 Z')
    toes = [circle_path(-92, -38, 27, 36).rotate(-24, -92, -38),
            circle_path(-34, -86, 28, 38).rotate(-8, -34, -86),
            circle_path(34, -86, 28, 38).rotate(8, 34, -86),
            circle_path(92, -38, 27, 36).rotate(24, 92, -38)]
    out = []
    for b in [pad] + toes:
        out.append(b.rotate(rot).scale(size).translate(cx, cy))
    return out


def snowcap(x0, x1, y, h=34, drips=((0.28, 20), (0.62, 30)), seed_bumps=(0.18, 0.5, 0.8)):
    """Snow cap lying on a (roughly flat) top edge at height y, from x0 to x1.
    Returns a Bez: rounded hump on top, wavy edge with drips below."""
    w = x1 - x0
    b = Bez()
    top = y - h * 0.55
    b.add((x0 - 6, y + 6), (0, 0), (-4, -h * 0.6))
    # top hump
    b.add((x0 + w * 0.25, top), (-w * 0.14, 0), (w * 0.12, 0))
    b.add((x0 + w * 0.7, top - h * 0.12), (-w * 0.14, 0), (w * 0.12, 0))
    b.add((x1 + 6, y + 6), (4, -h * 0.6), (0, 0))
    # wavy bottom with drips, from right to left
    pts = sorted(drips, key=lambda d: -d[0])
    for fx, depth in pts:
        xd = x0 + w * fx
        b.add((xd + 18, y + 10), (10, 0), (-6, 0))
        b.add((xd, y + 10 + depth), (10, 0), (-10, 0))
        b.add((xd - 18, y + 10), (6, 0), (-10, 0))
    return b
