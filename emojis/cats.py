"""Cat faces: 083-085, 087-095."""
import math

from kit.registry import emoji
from kit.lottie import part, group, anim, loop, stroke, map_anim
from kit.geometry import P, Bez, rounded, circle_path, heart_path, morph, star
from kit.motifs import crown, snowcap
from kit.text import glyphs
from kit import fx, style as S

# ============================================================ cat palette
PUPIL = '#10173a'
MOUTH_IN = '#2b2452'                                                   # open mouth (cool plum navy)
G_EAR = [(0.0, '#ffd9e5'), (1.0, '#ef8aab')]
G_NOSE = [(0.0, '#ffc9d8'), (1.0, '#ec6f96')]
G_TONGUE = [(0.0, '#ffb6cb'), (1.0, '#e8668e')]
G_MUZZLE = [(0.0, '#ffffff'), (1.0, '#dbe3ef')]
G_IRIS_YG = [(0.0, '#7b9828'), (0.42, '#c6dd5a'), (1.0, '#f3f9b4')]     # lid shadow on top, lit below
G_IRIS_GOLD = [(0.0, '#a9780e'), (0.42, '#f4c63a'), (1.0, '#fff3ab')]
G_SCLERA = [(0.0, '#ffffff'), (1.0, '#d3e4f6')]
G_HEART = [(0.0, '#ffd0e0'), (0.45, '#ff7fa6'), (1.0, '#d9406c')]
G_TEAR = [(0.0, '#eaf7ff'), (0.5, '#8fd0ff'), (1.0, '#3f8fe6')]
G_KNIT = [(0.0, '#4f7bdc'), (0.55, '#2c4fa6'), (1.0, '#1a3276')]       # navy knitted wool (avatar scarf)
G_LENS = [(0.0, '#3b4f8c'), (0.5, '#16224d'), (1.0, '#070d24')]
G_LEDGE = [(0.0, '#5a9cf0'), (0.6, '#2c62c8'), (1.0, '#183b8f')]
KNIT_LINE = '#7aa0f0'

FURS = {
    'gray': dict(fur=S.G_FUR_GRAY, stripe='#68738e', muzzle=G_MUZZLE, ear=G_EAR,
                 iris=G_IRIS_YG, ring='#52701a', blaze=False),
    'tuxedo': dict(fur=S.G_FUR_DARK, stripe=None, muzzle=G_MUZZLE, ear=G_EAR,
                   iris=G_IRIS_GOLD, ring='#7a5206', blaze=True),
}

# canonical head (design box): head 52..460 x 122..470, ear tips at y ~ 44
HEAD = P('M 256 122 C 356 122 432 160 450 250 C 462 312 458 380 420 422 '
         'C 380 460 320 470 256 470 C 192 470 132 460 92 422 C 54 380 50 312 62 250 '
         'C 80 160 156 122 256 122 Z')
HEAD_Y = (122, 470)
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


def _mirror(b):
    return b.mirror_x(256)


def _neg(a):
    return map_anim(a, lambda v: [-x for x in v])


def _keys(T, keys, rest):
    """anim() from keys inside 0..T, padded with the rest value at 0 and T."""
    ks = list(keys)
    if ks[0][0] > 0:
        ks.insert(0, (0, rest, 'linear'))
    if ks[-1][0] < T:
        last = ks[-1]
        ks[-1] = (last[0], last[1], 'linear') if len(last) < 3 else last
        ks.append((T, rest))
    return anim(ks)


def _blinks(T, starts, dur=12, closed=8):
    """Several blinks per loop as one [sx, sy] scale property."""
    keys = []
    for t0 in sorted(starts):
        keys += [(t0, [100, 100], 'in'), (t0 + dur * 0.45, [104, closed], 'hold'),
                 (t0 + dur * 0.55, [104, closed], 'out'), (t0 + dur, [100, 100], 'linear')]
    return _keys(T, keys, [100, 100])


def _twitch(T, t0, deg=-14, n=2, step=10):
    """Quick ear flick(s) as a rotation, rest elsewhere."""
    keys = [(t0, 0, 'out')]
    t = t0
    for k in range(n):
        keys += [(t + step * 0.4, deg * (1 - 0.3 * k), 'io'), (t + step, 0, 'io')]
        t += step
    return _keys(T, keys, 0)


def _hearts_beat(T, t0, hi=118, lo2=104, hi2=112):
    return loop([(t0, 100, 'out'), (t0 + 7, hi, 'in'), (t0 + 14, lo2, 'out'), (t0 + 20, hi2, 'in'),
                 (t0 + 32, 100, 'linear'), (t0 + T, 100)], T)


# ============================================================ eye / mouth builders
def _eye_open(ex, ey, pal, look=None, rx=EYE_RX, ry=EYE_RY, pr=(24, 32), wet=False):
    eye = circle_path(ex, ey, rx, ry)
    glints = [part(circle_path(ex - rx * 0.3, ey - ry * 0.34, rx * 0.27), fill=S.WHITE, name='glint'),
              part(circle_path(ex + rx * 0.3, ey + ry * 0.36, rx * 0.12), fill=S.WHITE, o=90, name='glint2')]
    if wet:
        glints.append(part(circle_path(ex + rx * 0.12, ey - ry * 0.5, rx * 0.12), fill=S.WHITE, o=95, name='glint3'))
    pupil = group(part(circle_path(ex, ey + 4, pr[0], pr[1]), fill=PUPIL, name='pupil'), glints,
                  move=look, name='pupil')
    out = [part(eye, fill=S.vgrad(pal['iris'], ey - ry, ey + ry), outline=(S.OUTLINE, 6), name='iris'),
           part(circle_path(ex, ey, rx - 6, ry - 6), stroke=stroke(pal['ring'], 4, o=55), name='ring'),
           pupil]
    if wet:   # tear film pooling along the lower lid
        out.append(part(P(f'M {ex - rx + 4} {ey + 14} C {ex - rx * 0.6} {ey + ry + 6} {ex + rx * 0.6} {ey + ry + 6} '
                          f'{ex + rx - 4} {ey + 14} C {ex + rx * 0.5} {ey + ry - 12} {ex - rx * 0.5} {ey + ry - 12} '
                          f'{ex - rx + 4} {ey + 14} Z'), fill=S.ICE_L, o=80, name='tear_film'))
    return out


def _lid(ex, ey, pal, y_mid, slope, rx=EYE_RX, ry=EYE_RY, pad=10, w=9):
    """Upper eyelid in fur colour covering the eye above the line y = y_mid + slope * (x - ex),
    plus a navy lid line. Draw it above the open eye."""
    def cut(a, b):
        d = y_mid - ey
        A = 1 / a ** 2 + slope ** 2 / b ** 2
        B = 2 * d * slope / b ** 2
        C = d ** 2 / b ** 2 - 1
        q = math.sqrt(B * B - 4 * A * C)
        u1, u2 = (-B - q) / (2 * A), (-B + q) / (2 * A)
        return (ex + u1, y_mid + slope * u1), (ex + u2, y_mid + slope * u2)
    a, b = rx + pad, ry + pad
    p1, p2 = cut(a, b)
    large = 1 if y_mid > ey else 0
    shape = P(f'M {p1[0]} {p1[1]} A {a} {b} 0 {large} 1 {p2[0]} {p2[1]} Z')
    q1, q2 = cut(rx + 4, ry + 4)
    return [part(shape, fill=S.vgrad(pal['fur'], *HEAD_Y), name='lid'),
            part(P(f'M {q1[0]} {q1[1]} L {q2[0]} {q2[1]}'), stroke=stroke(S.OUTLINE, w), name='lid_line')]


def _eye_arc(ex, ey, up=True, w=36, h=30, sw=12):
    if up:
        d = f'M {ex - w} {ey + h * 0.45} C {ex - w * 0.6} {ey - h} {ex + w * 0.6} {ey - h} {ex + w} {ey + h * 0.45}'
    else:
        d = f'M {ex - w} {ey - h * 0.2} C {ex - w * 0.6} {ey + h} {ex + w * 0.6} {ey + h} {ex + w} {ey - h * 0.2}'
    return [part(P(d), stroke=stroke(S.OUTLINE, sw), name='eye_arc')]


def _eye_shock(ex, ey, pal, look=None, pupil_s=None):
    return [part(circle_path(ex, ey, 50, 56), fill=S.vgrad(G_SCLERA, ey - 56, ey + 56), outline=(S.OUTLINE, 6),
                 name='sclera'),
            group(part(circle_path(ex, ey + 2, 19), fill=S.vgrad(pal['iris'], ey - 17, ey + 21), outline=(S.OUTLINE, 3),
                       name='iris'),
                  part(circle_path(ex, ey + 2, 10), fill=PUPIL, name='pupil'),
                  part(circle_path(ex - 6, ey - 5, 5), fill=S.WHITE, name='glint'),
                  pivot=(ex, ey + 2), s=pupil_s, move=look, name='pupil')]


def _eye_heart(ex, ey):
    h = heart_path(ex, ey + 2, 116, 104)
    return [part(h, fill=S.vgrad(G_HEART, ey - 50, ey + 54), outline=(S.OUTLINE, 6), name='heart_eye'),
            part(circle_path(ex - 26, ey - 22, 14, 9).rotate(-38, ex - 26, ey - 22), fill=S.WHITE, o=90, name='glint'),
            part(circle_path(ex - 40, ey - 2, 5), fill=S.WHITE, o=80, name='glint2')]


def _eyes(style, pal, s=None, look=None, pupil_s=None, side_s=None):
    """Both eyes as groups around their centres (s = blink / pulse scale)."""
    out = []
    for k, (ex, ey) in enumerate((EYE_L, EYE_R)):
        sg = -1 if k == 0 else 1          # +1 = right eye
        if style == 'open':
            body = _eye_open(ex, ey, pal, look=look)
        elif style == 'smug':            # heavy relaxed lids, side glance
            body = _eye_open(ex, ey, pal, look=look) + _lid(ex, ey, pal, ey - 4, 0.06 * -sg)
        elif style == 'angry':           # lids slope down towards the nose
            body = _eye_open(ex, ey, pal, look=look, pr=(22, 28)) + _lid(ex, ey, pal, ey - 10, 0.42 * -sg)
        elif style == 'sad':             # inner corners raised, watery
            body = _eye_open(ex, ey, pal, look=look, wet=True) + _lid(ex, ey, pal, ey - 30, 0.34 * sg, w=7)
        elif style == 'happy':
            body = _eye_arc(ex, ey + 6, up=True)
        elif style == 'closed':
            body = _eye_arc(ex, ey + 4, up=False)
        elif style == 'shock':
            body = _eye_shock(ex, ey, pal, look=look, pupil_s=pupil_s)
        elif style == 'heart':
            body = _eye_heart(ex, ey)
        else:
            raise ValueError(style)
        out.append(group(body, pivot=(ex, ey), s=s, name='eye'))
    return out


def _brows(style, color=S.OUTLINE):
    if style == 'angry':
        b = _capsule((122, 216), 9, (214, 250), 12)
    elif style == 'sad':
        b = _capsule((126, 238), 8, (206, 214), 10)
    else:
        return []
    return [part(b, _mirror(b), fill=color, name='brows')]


def _mouth(style, s=None, shape=None):
    y = NOSE_Y + 22
    nose_line = P(f'M 256 {y - 6} L 256 {y + 6}')
    if style == 'w':
        w = P(f'M 224 {y + 2} C 228 {y + 20} 252 {y + 22} 256 {y + 6} C 260 {y + 22} 284 {y + 20} 288 {y + 2}')
        return [part(nose_line, w, stroke=stroke(S.OUTLINE, 7), name='mouth')]
    if style == 'smirk':
        w = P(f'M 228 {y + 6} C 232 {y + 20} 252 {y + 22} 256 {y + 6} C 262 {y + 22} 288 {y + 16} 298 {y - 6}')
        return [part(nose_line, w, stroke=stroke(S.OUTLINE, 7), name='mouth')]
    if style == 'open':          # laughing D-mouth with tongue
        m = P(f'M 210 {y + 2} C 232 {y + 14} 248 {y + 12} 256 {y + 4} C 264 {y + 12} 280 {y + 14} 302 {y + 2} '
              f'C 304 {y + 58} 280 {y + 82} 256 {y + 82} C 232 {y + 82} 208 {y + 58} 210 {y + 2} Z')
        body = [part(m, fill=MOUTH_IN, outline=(S.OUTLINE, 5), name='mouth_in'),
                part(circle_path(256, y + 62, 28, 15), fill=S.vgrad(G_TONGUE, y + 48, y + 76), name='tongue'),
                part(nose_line, stroke=stroke(S.OUTLINE, 7), name='nose_line')]
        return [group(body, pivot=(256, y + 4), s=s, name='mouth')]
    if style == 'o':             # shocked
        body = [part(circle_path(256, y + 38, 26, 34), fill=MOUTH_IN, outline=(S.OUTLINE, 5), name='mouth_in'),
                part(circle_path(256, y + 60, 16, 9), fill=S.vgrad(G_TONGUE, y + 51, y + 69), name='tongue'),
                part(nose_line, stroke=stroke(S.OUTLINE, 7), name='nose_line')]
        return [group(body, pivot=(256, y + 6), s=s, name='mouth')]
    if style == 'sad':           # wobbly frown; `shape` may be an animated morph
        w = shape or P(f'M 222 {y + 26} C 228 {y + 8} 250 {y + 6} 256 {y + 18} C 262 {y + 6} 284 {y + 8} 290 {y + 26}')
        return [part(nose_line, stroke=stroke(S.OUTLINE, 7), name='nose_line'),
                part(w, stroke=stroke(S.OUTLINE, 7), name='mouth')]
    if style == 'frown':         # angry: frown with a little fang
        w = P(f'M 220 {y + 30} C 232 {y + 10} 280 {y + 10} 292 {y + 30}')
        fang = rounded([(262, y + 14), (282, y + 16), (276, y + 32)], [2, 2, 4])
        return [part(fang, fill=S.WHITE, outline=(S.OUTLINE, 3), name='fang'),
                part(nose_line, w, stroke=stroke(S.OUTLINE, 7), name='mouth')]
    if style == 'small':
        w = P(f'M 238 {y + 4} C 242 {y + 14} 252 {y + 15} 256 {y + 6} C 260 {y + 15} 270 {y + 14} 274 {y + 4}')
        return [part(nose_line, w, stroke=stroke(S.OUTLINE, 6), name='mouth')]
    raise ValueError(style)


# ============================================================ the cat head
def _ear(side, pal, r=None):
    outer = rounded([(70, 284), (94, 40), (242, 132)], [0, 38, 0])
    inner = rounded([(100, 214), (110, 84), (204, 136)], [6, 24, 6])
    piv = (150, 196)
    if side > 0:
        outer, inner, piv = _mirror(outer), _mirror(inner), (362, 196)
    return group(part(outer, fill=S.vgrad(pal['fur'], 44, 300), outline=S.OW, name='ear'),
                 part(inner, fill=S.vgrad(pal['ear'], 84, 230), name='ear_in'),
                 pivot=piv, r=r, name='ear_l' if side < 0 else 'ear_r')


def _marks(pal):
    out = []
    if pal['stripe']:
        st = [_capsule((256, 140), 14, (256, 200), 3),
              _capsule((210, 144), 11, (222, 190), 3),
              _capsule((302, 144), 11, (290, 190), 3)]
        ch = [_capsule((76, 276), 10, (112, 283), 4), _capsule((74, 310), 10, (106, 313), 4)]
        ch += [_mirror(c) for c in ch]
        out.append(part(*st, *ch, fill=pal['stripe'], name='stripes'))
    if pal['blaze']:
        blaze = P('M 256 196 C 270 196 280 250 290 300 C 300 330 330 340 342 368 C 356 410 318 452 256 452 '
                  'C 194 452 156 410 170 368 C 182 340 212 330 222 300 C 232 250 242 196 256 196 Z')
        out.append(part(blaze, fill=S.vgrad(G_MUZZLE, 196, 452), name='blaze'))
    return out


def cat_head(T, fur='gray', eyes='open', mouth='w', blush=40, brows=None, blink=(), look=None,
             ear_l=None, ear_r=None, whisk=None, eye_s=None, pupil_s=None, mouth_s=None, mouth_shape=None):
    """The KRONOS cat head in canonical coordinates (head ~52..460 x 44..470, centre x 256).

    fur    -- 'gray' tabby or 'tuxedo'
    eyes   -- open / smug / angry / sad / happy / closed / shock / heart
    mouth  -- w / smirk / open / o / sad / frown / small
    blink  -- frames where a blink starts (or pass eye_s, an [sx, sy] scale for both eyes)
    look   -- animated [dx, dy] pupil offset; ear_l / ear_r / whisk -- rotation properties

    Returns a dict of layers in painter order (ears, head, marks, muzzle, blush, whiskers,
    brows, eyes, nose, mouth) so emoji can drop, swap or add pieces; flat(L) lists them."""
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
    L['blush'] = [part(circle_path(116, 366, 30, 17), circle_path(396, 366, 30, 17),
                       fill=S.PINK, o=blush, name='blush')] if blush else []
    wl = [P('M 176 372 C 140 364 96 360 40 366'), P('M 178 390 C 140 390 96 398 46 414')]
    wr = [_mirror(w) for w in wl]
    L['whiskers'] = [group(_inked(wl, 5, S.WHITE, ow=3, name='whisk'), pivot=(178, 380), r=whisk, name='whisk_l'),
                     group(_inked(wr, 5, S.WHITE, ow=3, name='whisk'), pivot=(334, 380),
                           r=None if whisk is None else _neg(whisk), name='whisk_r')]
    L['brows'] = _brows(brows)
    if eye_s is None and blink:
        eye_s = _blinks(T, blink)
    L['eyes'] = _eyes(eyes, pal, s=eye_s, look=look, pupil_s=pupil_s)
    L['nose'] = [part(rounded([(230, NOSE_Y - 2), (282, NOSE_Y - 2), (256, NOSE_Y + 24)], [13, 13, 9]),
                      fill=S.vgrad(G_NOSE, NOSE_Y - 2, NOSE_Y + 24), outline=(S.OUTLINE, 4), name='nose'),
                 part(circle_path(246, NOSE_Y + 5, 7, 4), fill=S.WHITE, o=80, name='nose_glint')]
    L['mouth'] = _mouth(mouth, s=mouth_s, shape=mouth_shape)
    return L


def flat(L, skip=()):
    return [L[k] for k in L if k not in skip]


# ============================================================ props
def _flake(cx, cy, r):
    """Tiny six-point snowflake (path star) with a navy rim."""
    return part(star(cx, cy, 6, r, r * 0.5, round_out=r * 0.28, round_in=r * 0.12),
                fill=S.WHITE, outline=(S.OUTLINE, 3), name='flake')


def _drop(cx, cy, r, tilt=0):
    """Tear drop pointing up, round end centred at (cx, cy)."""
    d = P(f'M {cx} {cy - r * 2.1} C {cx + r * 0.4} {cy - r * 1.3} {cx + r} {cy - r * 0.7} {cx + r} {cy} '
          f'C {cx + r} {cy + r * 0.6} {cx + r * 0.55} {cy + r} {cx} {cy + r} '
          f'C {cx - r * 0.55} {cy + r} {cx - r} {cy + r * 0.6} {cx - r} {cy} '
          f'C {cx - r} {cy - r * 0.7} {cx - r * 0.4} {cy - r * 1.3} {cx} {cy - r * 2.1} Z')
    if tilt:
        d = d.rotate(tilt, cx, cy)
    return [part(d, fill=S.vgrad(G_TEAR, cy - r * 2.1, cy + r), outline=(S.OUTLINE, 4), name='drop'),
            part(circle_path(cx - r * 0.38, cy - r * 0.2, r * 0.26), fill=S.WHITE, o=90, name='drop_glint')]


def _paw(cx, cy, w=96, h=92, rot=0, fur=S.G_FUR_GRAY, toes=3):
    """Chibi front paw seen from the front: rounded mitten with toe creases."""
    x0, y0 = cx - w / 2, cy - h / 2
    body = P(f'M {cx} {y0} C {cx + w * 0.42} {y0} {x0 + w} {y0 + h * 0.22} {x0 + w} {cy + h * 0.06} '
             f'C {x0 + w} {y0 + h * 0.86} {cx + w * 0.3} {y0 + h} {cx} {y0 + h} '
             f'C {cx - w * 0.3} {y0 + h} {x0} {y0 + h * 0.86} {x0} {cy + h * 0.06} '
             f'C {x0} {y0 + h * 0.22} {cx - w * 0.42} {y0} {cx} {y0} Z')
    creases = [P(f'M {cx + w * f} {y0 + 4} C {cx + w * f * 1.05} {y0 + h * 0.18} {cx + w * f} {y0 + h * 0.3} '
                 f'{cx + w * f * 0.95} {y0 + h * 0.34}') for f in ((-0.17, 0.17) if toes == 3 else (-0.22, 0, 0.22))]
    items = [part(body, fill=S.vgrad(fur, y0, y0 + h), outline=S.OW, name='paw'),
             part(*creases, stroke=stroke(S.OUTLINE, 5), name='toes'),
             part(circle_path(cx - w * 0.24, y0 + h * 0.3, w * 0.1, h * 0.07), fill=S.WHITE, o=55, name='paw_gloss')]
    return group(items, pivot=(cx, cy), r=rot, name='paw')


def _puff(cx, cy, r):
    """Steam / dust puff: three merged circles with a navy rim."""
    cs = [circle_path(cx - r * 0.55, cy + r * 0.15, r * 0.62), circle_path(cx + r * 0.5, cy + r * 0.2, r * 0.58),
          circle_path(cx, cy - r * 0.25, r * 0.72)]
    return [part(*cs, fill=S.vgrad(S.G_SNOW, cy - r, cy + r * 0.8), outline=(S.OUTLINE, 4), name='puff')]


def _vein(cx, cy, r):
    """Anger mark: four bent corners around (cx, cy)."""
    arm = P(f'M {cx - r * 0.25} {cy - r} C {cx - r * 0.2} {cy - r * 0.45} {cx - r * 0.45} {cy - r * 0.2} '
            f'{cx - r} {cy - r * 0.25}')
    arms = [arm.rotate(a, cx, cy) for a in (0, 90, 180, 270)]
    return [part(*arms, stroke=stroke(S.OUTLINE, r * 0.34 + 8), name='vein_ow'),
            part(*arms, stroke=stroke('#ff6f8e', r * 0.34), name='vein')]


def _wrap(T, t0, dur, keys_fn):
    return keys_fn


# ============================================================ 083-085
@emoji(83, 'cat', '🐱', 'Котик', frames=180, still=0)
def e_cat(T):
    tilt = anim((0, 0, 'io'), (34, 7, 'io'), (96, 7, 'io'), (128, 0, 'io'), (T, 0))
    L = cat_head(T, blink=(62, 150), ear_l=_twitch(T, 104), ear_r=_twitch(T, 136, deg=14))
    head = group(flat(L), pivot=(256, 470), r=tilt, s=fx.breathe(T, 100, 102, cycles=2), name='cat')
    return [fx.glow(256, 300, 230, alpha=0.3), head]


def _scarf(T):
    """Navy knitted scarf (avatar) wrapped under the chin, tail fluttering to the right."""
    band = P('M 96 428 C 160 462 352 462 416 428 C 436 446 438 484 418 500 C 356 530 156 530 94 500 '
             'C 74 484 76 446 96 428 Z')
    knit = []
    for row, (yy, amp) in enumerate(((452, 16), (480, 18), (506, 12))):
        for k in range(9):
            x = 128 + k * 32 + (row % 2) * 16
            if x > 400:
                continue
            u = (x - 256) / 170
            y = yy - amp * (u * u) + 4
            knit.append(P(f'M {x - 9} {y - 7} L {x} {y + 3} L {x + 9} {y - 7}'))
    tail_a = P('M 352 474 C 380 466 404 470 426 478 C 444 484 458 482 470 474 L 482 512 '
               'C 466 524 446 522 424 514 C 402 506 380 506 360 514 Z')
    tail_b = P('M 352 474 C 380 476 404 462 426 458 C 444 456 458 462 472 470 L 480 510 '
               'C 464 500 448 496 426 500 C 404 504 382 518 360 514 Z')
    tail_c = P('M 352 474 C 378 470 400 482 424 486 C 446 490 460 480 474 470 L 482 508 '
               'C 468 520 448 528 426 524 C 402 520 380 508 360 514 Z')
    tail_shape = morph((0, tail_a, 'sine'), (T / 4, tail_b, 'sine'), (T / 2, tail_c, 'sine'), (3 * T / 4, tail_b, 'sine'),
                       (T, tail_a))
    knot = circle_path(352, 486, 34, 30)
    return [
        part(tail_shape, fill=S.vgrad(G_KNIT, 458, 524), outline=S.OW, name='tail'),
        part(band, fill=S.vgrad(G_KNIT, 428, 526), outline=S.OW, name='band'),
        part(*knit, stroke=stroke(KNIT_LINE, 4, o=70), name='knit'),
        part(P('M 112 440 C 170 466 300 470 380 452'), stroke=stroke(S.WHITE, 5, o=35), name='band_gloss'),
        part(knot, fill=S.vgrad(G_KNIT, 456, 516), outline=S.OW, name='knot'),
        part(P('M 334 476 L 344 488 L 354 476'), P('M 350 496 L 360 508 L 370 496'),
             stroke=stroke(KNIT_LINE, 4, o=70), name='knot_knit'),
    ]


@emoji(84, 'cat_scarf', '😺', 'Котик в шарфе', frames=180, still=0)
def e_cat_scarf(T):
    L = cat_head(T, blink=(96, 110))
    flakes = []
    for k, ((x, y), r) in enumerate((((194, 120), 13), ((104, 52), 11), ((318, 118), 12))):
        t0 = 8 + 52 * k
        fall = loop([(t0, [0, -150], 'linear'), (t0 + 34, [0, 0], 'hold'), (t0 + T, [0, -150])], T)
        sway = loop([(t0, [-10, 0], 'sine'), (t0 + 17, [10, 0], 'sine'), (t0 + 34, [0, 0], 'hold'), (t0 + T, [-10, 0])], T)
        sc = loop([(t0, 100, 'hold'), (t0 + 34, 100, 'out'), (t0 + 38, 120, 'io'), (t0 + 46, 100, 'hold'),
                   (t0 + 104, 100, 'in'), (t0 + 124, 0, 'hold'), (t0 + T, 100)], T)
        op = loop([(t0, 0, 'out'), (t0 + 10, 100, 'hold'), (t0 + 104, 100, 'in'), (t0 + 124, 0, 'hold'), (t0 + T, 0)], T)
        flakes.append(group(group(_flake(x, y, r), pivot=(x, y), move=sway, name='sway'),
                            pivot=(x, y), move=fall, s=sc, o=op, name='flake'))
    body = group(flat(L), _scarf(T), flakes, pivot=(256, 300), s=84, r=fx.swing(T, 2),
                 move=fx.bob(T, 8), name='cat')
    return [fx.glow(256, 290, 220, alpha=0.3), body]


@emoji(85, 'cat_tuxedo', '🐈\u200d⬛', 'Кот-смокинг', frames=120, still=0)
def e_cat_tuxedo(T):
    whisk = fx.wobble(T, 64, 30, 7, n=3)
    L = cat_head(T, fur='tuxedo', blink=(30, 96), whisk=whisk, ear_r=_twitch(T, 84, deg=14))
    head = group(flat(L), pivot=(256, 470), r=fx.swing(T, 2.5), s=fx.breathe(T, 100, 102), name='cat')
    return [fx.glow(256, 300, 230, alpha=0.3), head]
