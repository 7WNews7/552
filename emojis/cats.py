"""Cat faces: 083-085, 087-095."""
import math

from kit.registry import emoji
from kit.lottie import part, group, anim, loop, stroke
from kit.geometry import P, Bez, rounded, circle_path, morph
from kit import fx, style as S

# ============================================================ cat palette
PUPIL = '#10173a'
G_EAR = [(0.0, '#ffd9e5'), (1.0, '#ef8aab')]
G_NOSE = [(0.0, '#ffc9d8'), (1.0, '#ec6f96')]
G_MUZZLE = [(0.0, '#ffffff'), (1.0, '#dbe3ef')]
G_IRIS_YG = [(0.0, '#7b9828'), (0.42, '#c6dd5a'), (1.0, '#f3f9b4')]     # lid shadow on top, lit below
G_IRIS_GOLD = [(0.0, '#a9780e'), (0.42, '#f4c63a'), (1.0, '#fff3ab')]

FURS = {
    'gray': dict(fur=S.G_FUR_GRAY, stripe='#68738e', muzzle=G_MUZZLE, ear=G_EAR,
                 iris=G_IRIS_YG, ring='#52701a', blaze=False),
    'tuxedo': dict(fur=S.G_FUR_DARK, stripe=None, muzzle=G_MUZZLE, ear=G_EAR,
                   iris=G_IRIS_GOLD, ring='#7a5206', blaze=True),
}

# canonical head (design box): head 52..460 x 124..466, ear tips at y ~ 60
HEAD = P('M 256 124 C 352 124 430 160 448 252 C 462 322 452 396 404 430 '
         'C 364 458 312 466 256 466 C 200 466 148 458 108 430 C 60 396 50 322 64 252 '
         'C 82 160 160 124 256 124 Z')
HEAD_Y = (124, 466)
EYE_L, EYE_R = (170, 300), (342, 300)
EYE_RX, EYE_RY = 46, 52
NOSE_Y = 340


# ============================================================ small helpers
def _capsule(c1, r1, c2, r2):
    """Tapered capsule: circle (c1, r1) joined to circle (c2, r2) by their outer tangents."""
    (x1, y1), (x2, y2) = c1, c2
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    px, py = -uy, ux
    s = (r1 - r2) / L
    c = math.sqrt(1 - s * s)
    na, nb = (s * ux + c * px, s * uy + c * py), (s * ux - c * px, s * uy - c * py)
    a1, b1 = (x1 + r1 * na[0], y1 + r1 * na[1]), (x1 + r1 * nb[0], y1 + r1 * nb[1])
    a2, b2 = (x2 + r2 * na[0], y2 + r2 * na[1]), (x2 + r2 * nb[0], y2 + r2 * nb[1])
    big = 1 if r1 > r2 else 0
    return P(f'M {b1[0]} {b1[1]} A {r1} {r1} 0 {big} 0 {a1[0]} {a1[1]} L {a2[0]} {a2[1]} '
             f'A {r2} {r2} 0 {1 - big} 0 {b2[0]} {b2[1]} Z')


def _inked(paths, w, color, ow=4, o=None, name='ink'):
    """Solid stroke with a navy contour (gradient strokes are forbidden)."""
    return group(part(paths, stroke=stroke(S.OUTLINE, w + 2 * ow), name=name + '_contour'),
                 part(paths, stroke=stroke(color, w), name=name), o=o, name=name)


def _blinks(T, starts, dur=12, closed=8):
    """Several blinks per loop as one [sx, sy] scale property."""
    keys = [(0, [100, 100], 'linear')]
    for t0 in sorted(starts):
        keys += [(t0, [100, 100], 'in'), (t0 + dur * 0.45, [104, closed], 'hold'),
                 (t0 + dur * 0.55, [104, closed], 'out'), (t0 + dur, [100, 100], 'linear')]
    keys.append((T, [100, 100]))
    return anim(keys)


def _twitch(T, t0, deg=-14, n=2):
    """Quick ear flick(s) as a rotation, rest elsewhere."""
    keys = [(0, 0, 'linear'), (t0, 0, 'out')]
    t = t0
    for k in range(n):
        keys += [(t + 4, deg * (1 - 0.3 * k), 'io'), (t + 10, 0, 'io')]
        t += 10
    keys[-1] = (keys[-1][0], 0, 'linear')
    keys.append((T, 0))
    return anim(keys)


def _mirror(b):
    return b.mirror_x(256)


# ============================================================ the cat head
def _ear(side, pal, r=None):
    outer = rounded([(70, 284), (94, 40), (242, 132)], [0, 38, 0])
    inner = rounded([(100, 214), (110, 84), (204, 136)], [6, 24, 6])
    piv = (150, 196)
    if side > 0:
        outer, inner, piv = _mirror(outer), _mirror(inner), (362, 196)
    return group(part(outer, fill=S.vgrad(pal['fur'], 52, 300), outline=S.OW, name='ear'),
                 part(inner, fill=S.vgrad(pal['ear'], 96, 230), name='ear_in'),
                 pivot=piv, r=r, name='ear_l' if side < 0 else 'ear_r')


def _marks(pal):
    out = []
    if pal['stripe']:
        st = [_capsule((256, 142), 14, (256, 202), 3),
              _capsule((210, 146), 11, (222, 192), 3),
              _capsule((302, 146), 11, (290, 192), 3)]
        ch = [_capsule((66, 276), 12, (108, 284), 4), _capsule((66, 312), 12, (104, 314), 4)]
        ch += [_mirror(c) for c in ch]
        out.append(part(*st, *ch, fill=pal['stripe'], name='stripes'))
    if pal['blaze']:
        blaze = P('M 256 196 C 270 196 280 250 290 300 C 300 330 330 340 342 368 C 356 410 318 452 256 452 '
                  'C 194 452 156 410 170 368 C 182 340 212 330 222 300 C 232 250 242 196 256 196 Z')
        out.append(part(blaze, fill=S.vgrad(G_MUZZLE, 196, 452), name='blaze'))
    return out


def _eye_open(ex, ey, pal, look=None, rx=EYE_RX, ry=EYE_RY, pr=(24, 32)):
    eye = circle_path(ex, ey, rx, ry)
    pupil = group(part(circle_path(ex, ey + 4, pr[0], pr[1]), fill=PUPIL, name='pupil'),
                  part(circle_path(ex - rx * 0.3, ey - ry * 0.34, rx * 0.27), fill=S.WHITE, name='glint'),
                  part(circle_path(ex + rx * 0.3, ey + ry * 0.36, rx * 0.12), fill=S.WHITE, o=90, name='glint2'),
                  move=look, name='pupil')
    return [part(eye, fill=S.vgrad(pal['iris'], ey - ry, ey + ry), outline=(S.OUTLINE, 6), name='iris'),
            part(circle_path(ex, ey, rx - 6, ry - 6), stroke=stroke(pal['ring'], 4, o=55), name='ring'),
            pupil]


def _eyes(T, style, pal, s=None, look=None):
    out = []
    for (ex, ey) in (EYE_L, EYE_R):
        if style == 'open':
            body = _eye_open(ex, ey, pal, look=look)
        else:
            raise ValueError(style)
        out.append(group(body, pivot=(ex, ey), s=s, name='eye'))
    return out


def _mouth(style, y=NOSE_Y + 22):
    if style == 'w':
        w = [P(f'M 256 {y - 6} L 256 {y + 6}'),
             P(f'M 224 {y + 2} C 228 {y + 20} 252 {y + 22} 256 {y + 6} C 260 {y + 22} 284 {y + 20} 288 {y + 2}')]
        return [part(*w, stroke=stroke(S.OUTLINE, 7), name='mouth')]
    raise ValueError(style)


def cat_head(T, fur='gray', eyes='open', mouth='w', blush=40, blink=(), look=None,
             ear_l=None, ear_r=None, whisk=None):
    """The KRONOS cat head in canonical coordinates (head ~52..460 x 60..466).

    Returns an ordered dict of layers (painter order) so emoji can swap or add pieces:
    ears, head, marks, muzzle, blush, whiskers, eyes, nose, mouth."""
    pal = FURS[fur]
    L = {}
    L['ears'] = [_ear(-1, pal, ear_l), _ear(1, pal, ear_r)]
    L['head'] = [part(HEAD, fill=S.vgrad(pal['fur'], *HEAD_Y), outline=S.OW, name='head'),
                 part(P('M 96 248 C 100 210 124 180 160 160 C 136 188 122 216 116 252 Z'),
                      fill=S.WHITE, o=50, name='gloss'),
                 part(circle_path(128, 264, 8), fill=S.WHITE, o=45, name='gloss_dot')]
    L['marks'] = _marks(pal)
    L['muzzle'] = [part(circle_path(224, 380, 44, 34), circle_path(288, 380, 44, 34),
                        fill=S.vgrad(pal['muzzle'], 346, 414), name='muzzle')]
    L['blush'] = [part(circle_path(118, 366, 30, 17), circle_path(394, 366, 30, 17),
                       fill=S.PINK, o=blush, name='blush')] if blush else []
    wl = [P('M 176 372 C 140 364 96 360 40 366'), P('M 178 390 C 140 390 96 398 46 414')]
    wr = [_mirror(w) for w in wl]
    L['whiskers'] = [group(_inked(wl, 5, S.WHITE, ow=3, name='whisk'), pivot=(178, 380), r=whisk, name='whisk_l'),
                     group(_inked(wr, 5, S.WHITE, ow=3, name='whisk'), pivot=(334, 380),
                           r=None if whisk is None else _neg(whisk), name='whisk_r')]
    L['eyes'] = _eyes(T, eyes, pal, s=_blinks(T, blink) if blink else None, look=look)
    L['nose'] = [part(rounded([(230, NOSE_Y - 2), (282, NOSE_Y - 2), (256, NOSE_Y + 24)], [13, 13, 9]),
                      fill=S.vgrad(G_NOSE, NOSE_Y - 2, NOSE_Y + 24), outline=(S.OUTLINE, 4), name='nose'),
                 part(circle_path(246, NOSE_Y + 5, 7, 4), fill=S.WHITE, o=80, name='nose_glint')]
    L['mouth'] = _mouth(mouth)
    return L


def _neg(a):
    from kit.lottie import map_anim
    return map_anim(a, lambda v: [-x for x in v])


def flat(L):
    return [L[k] for k in L]


# ============================================================ 083-085
@emoji(83, 'cat', '🐱', 'Котик', frames=180, still=0)
def e_cat(T):
    tilt = anim((0, 0, 'io'), (34, 7, 'io'), (96, 7, 'io'), (128, 0, 'io'), (T, 0))
    L = cat_head(T, blink=(62, 150), ear_l=_twitch(T, 104), ear_r=_twitch(T, 136, deg=14))
    head = group(flat(L), pivot=(256, 466), r=tilt, s=fx.breathe(T, 100, 102, cycles=2), name='cat')
    return [fx.glow(256, 300, 230, alpha=0.3), head]


@emoji(84, 'cat_scarf', '😺', 'Котик в шарфе', frames=180, still=0)
def e_cat_scarf(T):
    L = cat_head(T, blink=(90,))
    return [group(flat(L), pivot=(256, 300), s=88)]


@emoji(85, 'cat_tuxedo', '🐈\u200d⬛', 'Кот-смокинг', frames=120, still=0)
def e_cat_tuxedo(T):
    L = cat_head(T, fur='tuxedo', blink=(40,), whisk=fx.wobble(T, 80, 24, 6, n=2))
    return [group(flat(L))]
