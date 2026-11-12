"""Cat faces: 083-085, 087-095."""
import math

from kit.registry import emoji
from kit.lottie import part, group, anim, loop, stroke, map_anim
from kit.geometry import P, rounded, circle_path, heart_path, morph, star
from kit.motifs import crown
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


def _marks(pal, forehead=True):
    out = []
    if pal['stripe']:
        st = [_capsule((256, 140), 14, (256, 200), 3),
              _capsule((210, 144), 11, (222, 190), 3),
              _capsule((302, 144), 11, (290, 190), 3)] if forehead else []
        ch = [_capsule((76, 276), 10, (112, 283), 4), _capsule((74, 310), 10, (106, 313), 4)]
        ch += [_mirror(c) for c in ch]
        out.append(part(*st, *ch, fill=pal['stripe'], name='stripes'))
    if pal['blaze']:
        blaze = P('M 256 196 C 270 196 280 250 290 300 C 300 330 330 340 342 368 C 356 410 318 452 256 452 '
                  'C 194 452 156 410 170 368 C 182 340 212 330 222 300 C 232 250 242 196 256 196 Z')
        out.append(part(blaze, fill=S.vgrad(G_MUZZLE, 196, 452), name='blaze'))
    return out


def cat_head(T, fur='gray', eyes='open', mouth='w', blush=40, brows=None, blink=(), look=None,
             ear_l=None, ear_r=None, whisk=None, eye_s=None, pupil_s=None, mouth_s=None, mouth_shape=None,
             forehead=True):
    """The KRONOS cat head in canonical coordinates (head ~52..460 x 44..470, centre x 256).

    fur      -- 'gray' tabby or 'tuxedo'
    eyes     -- open / smug / angry / sad / happy / closed / shock / heart
    mouth    -- w / smirk / open / o / sad / frown / small
    brows    -- None / 'angry' / 'sad'; forehead=False drops the tabby forehead stripes
    blink    -- frames where a blink starts (or pass eye_s, an [sx, sy] scale for both eyes)
    look     -- animated [dx, dy] pupil offset; pupil_s scales the pupils (shock eyes)
    ear_l / ear_r / whisk -- rotation properties; mouth_s scales the mouth, mouth_shape
               replaces the 'sad' mouth path (e.g. a trembling morph)

    Returns a dict of layers in painter order (ears, head, marks, muzzle, blush, whiskers,
    brows, eyes, nose, mouth) so emoji can drop, swap or add pieces; flat(L) lists them.
    Place / animate the whole head by wrapping flat(L) in a group()."""
    pal = FURS[fur]
    L = {}
    L['ears'] = [_ear(-1, pal, ear_l), _ear(1, pal, ear_r)]
    L['head'] = [part(HEAD, fill=S.vgrad(pal['fur'], *HEAD_Y), outline=S.OW, name='head'),
                 part(P('M 96 248 C 100 210 124 180 160 160 C 136 188 122 216 116 252 Z'),
                      fill=S.WHITE, o=50, name='gloss'),
                 part(circle_path(128, 264, 8), fill=S.WHITE, o=45, name='gloss_dot')]
    L['marks'] = _marks(pal, forehead)
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


def _shifted(a, dx, dy):
    """Add a constant offset to an (animated) [dx, dy] move property."""
    return map_anim(a, lambda v: [v[0] + dx, v[1] + dy])


def EASE_OUT(u):            # rising, decelerating
    return 1 - (1 - u) ** 2


def EASE_IN(u):             # sliding / dripping, accelerating
    return u ** 1.7


def _bez_at(pts, u):
    while len(pts) > 1:
        pts = [[a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u] for a, b in zip(pts, pts[1:])]
    return pts[0]


def _flight(T, t0, dur, pts, s0=30, s1=100, fade=0.75, ease=None, steps=8):
    """Group kwargs for a particle travelling along the Bezier curve with control points pts
    (relative offsets, first = [0, 0]), popping in at t0 and fading out at the end of dur.
    A quadratic curve with linear timing is a true throw parabola; `ease` reshapes timing."""
    keys = [(t0 + dur * k / steps, _bez_at(pts, (ease or (lambda u: u))(k / steps)),
             'linear' if k < steps else 'hold') for k in range(steps + 1)]
    move = loop(keys + [(t0 + T, list(pts[0]))], T)
    sc = loop([(t0, s0, 'outback'), (t0 + dur * 0.25, s1, 'io'), (t0 + dur, s1 * 0.8, 'hold'), (t0 + T, s0)], T)
    op = loop([(t0, 0, 'out'), (t0 + dur * 0.12, 100, 'linear'), (t0 + dur * fade, 100, 'in'), (t0 + dur, 0, 'hold'),
               (t0 + T, 0)], T)
    return {'move': move, 's': sc, 'o': op}


# ============================================================ 083-085
@emoji(83, 'cat', '🐱', 'Котик', frames=180, still=0)
def e_cat(T):
    tilt = anim((0, 0, 'io'), (34, 7, 'io'), (96, 7, 'io'), (128, 0, 'io'), (T, 0))
    L = cat_head(T, blink=(62, 150), ear_l=_twitch(T, 104), ear_r=_twitch(T, 136, deg=14))
    head = group(flat(L), pivot=(256, 470), r=tilt, s=fx.breathe(T, 100, 102, cycles=2), name='cat')
    return [fx.glow(256, 300, 230, alpha=0.3), head]


def _scarf(T):
    """Chunky navy knitted scarf (avatar) wrapped under the chin, tail fluttering to the right."""
    band = P('M 82 420 C 150 468 362 468 430 420 C 456 444 460 500 430 520 C 362 556 150 556 82 520 '
             'C 52 500 56 444 82 420 Z')
    knit = []
    for k in range(-5, 6):
        x = 256 + k * 31
        u = (x - 256) / 200
        top = 466 - 40 * u * u
        for j in range(3):
            y = top + 10 + j * 22 - 6 * u * u * j
            if y > 540 - 30 * u * u:
                continue
            knit.append(P(f'M {x - 11} {y - 8} L {x} {y + 4} L {x + 11} {y - 8}'))
    knot = circle_path(366, 488, 40, 36)
    tail_keys = [
        P('M 380 462 C 410 456 440 468 466 482 C 480 490 492 488 500 482 L 496 530 '
          'C 484 538 470 536 454 528 C 432 516 408 512 388 520 Z'),
        P('M 380 462 C 412 466 438 452 464 452 C 480 452 492 460 502 470 L 494 518 '
          'C 482 508 468 506 452 512 C 430 520 408 526 388 520 Z'),
        P('M 380 462 C 408 460 432 476 460 486 C 478 492 494 482 504 470 L 498 520 '
          'C 486 532 470 540 450 536 C 428 530 406 518 388 520 Z'),
    ]
    tail_shape = morph((0, tail_keys[0], 'sine'), (T / 4, tail_keys[1], 'sine'), (T / 2, tail_keys[2], 'sine'),
                       (3 * T / 4, tail_keys[1], 'sine'), (T, tail_keys[0]))
    fringe = [P(f'M {x} {y} L {x + 18} {y + 4}') for x, y in ((500, 488), (500, 502), (499, 516))]
    return [
        part(band, fill=S.vgrad(G_KNIT, 420, 548), outline=S.OW, name='band'),
        part(*knit, stroke=stroke(KNIT_LINE, 5, o=75), name='knit'),
        part(P('M 104 438 C 170 474 300 480 392 460'), stroke=stroke(S.WHITE, 6, o=35), name='band_gloss'),
        group(part(*fringe, stroke=stroke(S.OUTLINE, 14), name='fringe_ow'),
              part(*fringe, stroke=stroke('#2c4fa6', 6), name='fringe'),
              part(tail_shape, fill=S.vgrad(G_KNIT, 452, 540), outline=S.OW, name='tail'),
              pivot=(384, 490), r=fx.swing(T, 4, cycles=2), name='scarf_tail'),
        part(knot, fill=S.vgrad(G_KNIT, 452, 524), outline=S.OW, name='knot'),
        part(P('M 352 470 L 364 482 L 376 470'), P('M 352 494 L 364 506 L 376 494'),
             stroke=stroke(KNIT_LINE, 5, o=75), name='knot_knit'),
    ]


@emoji(84, 'cat_scarf', '😺', 'Котик в шарфе', frames=180, still=128)
def e_cat_scarf(T):
    L = cat_head(T, blink=(100, 114))
    flakes = []
    for k, ((x, y), r, t0) in enumerate((((194, 112), 21, 6), ((322, 110), 19, 40), ((140, 60), 17, 74))):
        dist = 90 if y > 100 else 40
        fall = anim((0, [0, -dist], 'hold'), (t0, [0, -dist], 'linear'), (t0 + 36, [0, 0], 'hold'), (T, [0, 0]))
        sway = anim((0, [-10, 0], 'hold'), (t0, [-10, 0], 'sine'), (t0 + 18, [10, 0], 'sine'), (t0 + 36, [0, 0], 'hold'),
                    (T, [0, 0]))
        sc = anim((0, 100, 'hold'), (t0 + 36, 100, 'out'), (t0 + 40, 125, 'io'), (t0 + 48, 100, 'hold'),
                  (150, 100, 'in'), (174, 0, 'hold'), (T, 0))
        op = anim((0, 0, 'hold'), (t0, 0, 'out'), (t0 + 10, 100, 'hold'), (150, 100, 'in'), (174, 0, 'hold'), (T, 0))
        flakes.append(group(group(_flake(x, y, r), pivot=(x, y), move=sway, name='sway'),
                            pivot=(x, y), move=fall, s=sc, o=op, name='flake'))
    body = group(flat(L), _scarf(T), flakes, pivot=(256, 300), s=84, r=fx.swing(T, 2),
                 move=_shifted(fx.bob(T, 8), 0, -26), name='cat')
    return [fx.glow(256, 290, 220, alpha=0.3), body]


@emoji(85, 'cat_tuxedo', '🐈\u200d⬛', 'Кот-смокинг', frames=120, still=0)
def e_cat_tuxedo(T):
    whisk = fx.wobble(T, 64, 30, 7, n=3)
    L = cat_head(T, fur='tuxedo', blink=(30, 96), whisk=whisk, ear_r=_twitch(T, 84, deg=14))
    head = group(flat(L), pivot=(256, 470), r=fx.swing(T, 2.5), s=fx.breathe(T, 100, 102), name='cat')
    return [fx.glow(256, 300, 230, alpha=0.3), head]


# ============================================================ 087-095
@emoji(87, 'cat_king', '👑', 'Кот-король', frames=180, still=70)
def e_cat_king(T):
    look = anim((0, [10, 4], 'io'), (70, [10, 4], 'io'), (86, [-8, 4], 'io'), (130, [-8, 4], 'io'), (146, [10, 4], 'io'),
                (T, [10, 4]))
    L = cat_head(T, eyes='smug', mouth='smirk', blink=(104,), look=look, blush=30)
    nod = anim((0, 0, 'io'), (24, -4, 'io'), (60, -4, 'io'), (90, 0, 'io'), (T, 0))
    c = crown(250, 124, 190)
    sparks = fx.sparkles([(x, y - 4, 22) for x, y in c['tips']], T, dur=40, start=60, gap=20)
    sparks.append(fx.sparkle(c['gem'][0] + 44, c['gem'][1] - 8, 16, T, t0=130, dur=34))
    crown_g = group(c['parts'], fx.shine(c['shine'], T, t0=36, dur=56, angle=24, width=0.3, alpha=0.9), sparks,
                    pivot=(250, 188), r=anim((0, -14, 'io'), (30, -10, 'io'), (90, -15, 'io'), (T, -14)), name='crown')
    head = group(flat(L), pivot=(256, 476), s=88, name='head')
    body = group(head, crown_g, pivot=(256, 476), r=nod, move=fx.bob(T, 6), name='king')
    return [fx.glow(256, 300, 230, alpha=0.3), body]


@emoji(88, 'cat_love', '😻', 'Влюблённый кот', frames=120, still=12)
def e_cat_love(T):
    beat = _hearts_beat(T, 4)
    L = cat_head(T, eyes='heart', mouth='w', blush=75, eye_s=beat)
    head = group(flat(L), pivot=(256, 476), s=92, r=fx.swing(T, 3), name='head')
    minis = []
    for k, (x, y, sz, t0, dx) in enumerate(((78, 250, 74, 0, -8), (436, 236, 66, 40, 8), (444, 400, 56, 80, 12))):
        h = heart_path(x, y, sz)
        minis.append(group(part(h, fill=S.vgrad(G_HEART, y - sz / 2, y + sz / 2), outline=S.OW_THIN),
                           part(circle_path(x - sz * 0.2, y - sz * 0.16, sz * 0.11), fill=S.WHITE, o=85),
                           pivot=(x, y), **_flight(T, t0, 70, [[0, 0], [dx * 2, -70], [dx, -120]], s0=20, fade=0.7,
                                                   ease=EASE_OUT),
                           name='mini_heart'))
    return [fx.glow(256, 300, 226, color=S.PINK, alpha=0.22, s=fx.breathe(T, 94, 104)), head, minis]


@emoji(89, 'cat_laugh', '😹', 'Ржущий кот', frames=120, still=26)
def e_cat_laugh(T):
    ha = anim((0, [100, 100], 'io'), (10, [104, 76], 'io'), (20, [100, 104], 'io'), (30, [104, 76], 'io'),
              (40, [100, 104], 'io'), (50, [104, 80], 'io'), (62, [100, 100], 'io'), (T, [100, 100]))
    L = cat_head(T, eyes='happy', mouth='open', blush=60, mouth_s=ha)
    tears = []
    for side in (-1, 1):
        ex = 256 + side * 134
        for j, t0 in enumerate((4, 34, 64) if side < 0 else (18, 48, 80)):
            pts = [[0, 0], [side * 36, -96], [side * 72, 36]]
            tears.append(group(_drop(ex, 296, 18, tilt=side * 50), pivot=(ex, 296),
                               **_flight(T, t0, 38, pts, s0=40, fade=0.7), name='tear'))
    shake = anim((0, 0, 'io'), (10, -4, 'io'), (20, 4, 'io'), (30, -4, 'io'), (40, 4, 'io'), (50, -3, 'io'),
                 (62, 0, 'io'), (T, 0))
    hop = anim((0, [0, 0], 'out'), (5, [0, -10], 'in'), (10, [0, 0], 'out'), (15, [0, -10], 'in'), (20, [0, 0], 'out'),
               (25, [0, -10], 'in'), (30, [0, 0], 'out'), (35, [0, -10], 'in'), (40, [0, 0], 'out'), (45, [0, -8], 'in'),
               (50, [0, 0], 'io'), (T, [0, 0]))
    head = group(flat(L), tears, pivot=(256, 470), s=96, r=shake, move=hop, name='head')
    return [fx.glow(256, 300, 226, alpha=0.3), head]


@emoji(90, 'cat_shock', '🙀', 'Шок', frames=120, still=40)
def e_cat_shock(T):
    tremble = fx.wave(T, 100, 78, cycles=10)
    gape = anim((0, [100, 100], 'outback'), (14, [100, 118], 'io'), (60, [96, 110], 'io'), (90, [100, 118], 'io'),
                (T, [100, 100]))
    pop = anim((0, [100, 100], 'outback'), (12, [112, 112], 'io'), (40, [104, 104], 'io'), (T, [100, 100]))
    L = cat_head(T, eyes='shock', mouth='o', blush=0, pupil_s=tremble, eye_s=pop, mouth_s=gape, forehead=False,
                 ear_l=anim((0, 0, 'out'), (10, 12, 'io'), (100, 12, 'io'), (T, 0)),
                 ear_r=anim((0, 0, 'out'), (10, -12, 'io'), (100, -12, 'io'), (T, 0)))
    pale = part(HEAD, fill=S.vgrad([(0, '#3d6fe0'), (1, '#3d6fe0')], 122, 330, opacity=[(0, 0.55), (1, 0)]),
                name='pale')
    gloom = part(*[P(f'M {x} {150 + abs(x - 256) * 0.1} L {x} {214 - abs(x - 256) * 0.15}') for x in (196, 226, 256, 286, 316)],
                 stroke=stroke('#2f5fcf', 7, o=75), name='gloom')
    L['marks'] = L['marks'] + [pale, gloom]
    paws = [group(_paw(108, 404, rot=24), pivot=(108, 404),
                  move=anim((0, [-14, 6], 'outback'), (12, [0, 0], 'io'), (100, [0, 0], 'io'), (T, [-14, 6])), name='paw_l'),
            group(_paw(404, 404, rot=-24), pivot=(404, 404),
                  move=anim((0, [14, 6], 'outback'), (12, [0, 0], 'io'), (100, [0, 0], 'io'), (T, [14, 6])), name='paw_r')]
    sweat = group(_drop(424, 196, 21, tilt=-14), pivot=(424, 196),
                  **_flight(T, 20, 70, [[0, 0], [10, 64]], s0=50, fade=0.8, ease=EASE_IN), name='sweat')
    shiver = []
    for b0, dur in ((0, 30), (60, 24)):     # two shudders per loop, calm in between
        n = dur // 3
        shiver += [(b0 + 3 * k, [0 if k in (0, n) else 4.5 * (1 - 0.5 * k / n) * (1 if k % 2 else -1), 0], 'sine')
                   for k in range(n + 1)]
    head = group(flat(L, skip=('whiskers',)), paws, sweat, pivot=(256, 256), s=100, move=_keys(T, shiver, [0, 0]),
                 name='head')
    return [fx.glow(256, 300, 226, alpha=0.3), head]


@emoji(91, 'cat_cry', '😿', 'Плачущий кот', frames=120, still=50)
def e_cat_cry(T):
    y = NOSE_Y + 22
    m1 = P(f'M 222 {y + 26} C 228 {y + 8} 250 {y + 6} 256 {y + 18} C 262 {y + 6} 284 {y + 8} 290 {y + 26}')
    m2 = P(f'M 222 {y + 24} C 228 {y + 12} 250 {y + 2} 256 {y + 16} C 262 {y + 10} 284 {y + 4} 290 {y + 28}')
    wob = morph((0, m1, 'sine'), (6, m2, 'sine'), (12, m1, 'sine'), (18, m2, 'sine'), (24, m1, 'sine'), (30, m2, 'sine'),
                (36, m1, 'sine'), (60, m1, 'sine'), (66, m2, 'sine'), (72, m1, 'sine'), (78, m2, 'sine'), (84, m1, 'sine'),
                (T, m1))
    L = cat_head(T, eyes='sad', brows='sad', mouth='sad', blush=45, mouth_shape=wob, blink=(100,))
    streams = []
    for side in (-1, 1):
        ex = 256 + side * 86
        s = P(f'M {ex + side * 18} 346 C {ex + side * 26} 380 {ex + side * 18} 410 {ex + side * 30} 452')
        streams.append(_inked([s], 16, S.ICE, ow=3, o=85, name='stream'))
    drops = []
    for side in (-1, 1):
        ex = 256 + side * 86
        for t0 in ((0, 60) if side < 0 else (30, 90)):
            drops.append(group(_drop(ex + side * 18, 352, 13), pivot=(ex + side * 18, 352),
                               **_flight(T, t0, 56, [[0, 0], [side * 2, 60], [side * 12, 110]], s0=40, fade=0.8,
                                         ease=EASE_IN),
                               name='tear'))
    sob = anim((0, [0, 0], 'io'), (8, [0, 8], 'io'), (16, [0, -2], 'io'), (24, [0, 8], 'io'), (34, [0, 0], 'io'),
               (60, [0, 0], 'io'), (68, [0, 8], 'io'), (76, [0, -2], 'io'), (84, [0, 8], 'io'), (94, [0, 0], 'io'), (T, [0, 0]))
    L['eyes'] = streams + L['eyes']
    head = group(flat(L), drops, pivot=(256, 256), s=100, move=sob, name='head')
    return [fx.glow(256, 300, 226, alpha=0.3), head]


@emoji(92, 'cat_angry', '😾', 'Злой кот', frames=120, still=30)
def e_cat_angry(T):
    L = cat_head(T, eyes='angry', brows='angry', mouth='frown', blush=0,
                 ear_l=anim((0, -18, 'io'), (T, -18)), ear_r=anim((0, 18, 'io'), (T, 18)))
    flush = part(HEAD, fill=S.vgrad([(0, '#ff5a7a'), (1, '#ff5a7a')], 122, 300, opacity=[(0, 0.3), (1, 0)]),
                 name='flush')
    L['marks'] = [flush] + L['marks']
    vein = group(_vein(392, 196, 30), pivot=(392, 196), s=anim((0, 100, 'out'), (8, 128, 'in'), (16, 96, 'out'),
                                                                (24, 120, 'in'), (36, 100, 'io'), (60, 100, 'out'),
                                                                (68, 128, 'in'), (76, 96, 'out'), (84, 120, 'in'),
                                                                (96, 100, 'io'), (T, 100)), name='vein')
    puffs = []
    for k, (x, y, t0, sd) in enumerate(((92, 196, 0, -1), (420, 196, 14, 1), (92, 196, 60, -1), (420, 196, 74, 1))):
        puffs.append(group(_puff(x, y, 34), pivot=(x, y),
                           **_flight(T, t0, 46, [[0, 0], [sd * 6, -64], [sd * 40, -104]], s0=30, fade=0.6,
                                     ease=EASE_OUT),
                           name='steam'))
    shake = fx.wobble(T, 2, 30, 8, n=4, vector=(1, 0))
    head = group(flat(L), vein, pivot=(256, 476), s=90, move=shake, name='head')
    return [fx.glow(256, 300, 226, color='#ff8aa6', alpha=0.18), puffs, head]


@emoji(93, 'cat_sleep', '😴', 'Сонный кот', frames=180, still=80)
def e_cat_sleep(T):
    L = cat_head(T, eyes='closed', mouth='small', blush=45)
    bubble = group(part(circle_path(292, 362, 30), fill=S.rgrad([(0, '#ffffff'), (1, '#9fd2ff')], 284, 352, 34,
                                                                  opacity=[(0, 0.35), (1, 0.75)]),
                        outline=(S.OUTLINE, 3), name='bubble'),
                   part(circle_path(279, 352, 6), fill=S.WHITE, o=90, name='bubble_glint'),
                   pivot=(268, 358), s=fx.wave(T, 30, 100), name='bubble')
    L['mouth'] = L['mouth'] + [bubble]
    head = group(flat(L), pivot=(256, 476), s=fx.wave(T, [89, 89], [91.5, 87.5]), name='head')
    zs = []
    for k, (t0, cap) in enumerate(((0, 62), (60, 52), (120, 44))):
        (paths, (gx, gy)), = glyphs('Z', 392, 186, cap, weight=900)
        zs.append(group(part(*paths, fill=S.vgrad(S.G_ICE_SOFT, 186 - cap / 2, 186 + cap / 2), outline=S.OW_THIN),
                        pivot=(gx, gy), r=-12, **fx.rise(T, t0, 120, dy=-112, dx=40, s0=40, s1=100)))
    return [fx.glow(256, 300, 226, alpha=0.3), head, zs]


def _shades():
    lens = P('M 98 236 L 242 236 C 244 286 238 330 212 352 C 188 372 140 372 116 352 C 96 334 94 286 98 236 Z')
    lenses = [lens, _mirror(lens)]
    bar = rounded([(84, 222), (428, 222), (428, 246), (84, 246)], 10)
    refl = [P('M 126 252 L 150 252 L 118 330 L 108 316 Z'), P('M 164 252 L 176 252 L 140 344 L 130 340 Z')]
    refl += [r.translate(172, 0) for r in refl]
    return lenses, [
        part(*lenses, bar, fill=S.vgrad(G_LENS, 222, 366), outline=S.OW, name='lenses'),
        part(rounded([(92, 226), (420, 226), (420, 234), (92, 234)], 4), fill=S.WHITE, o=30, name='bar_gloss'),
        part(*refl, fill=S.WHITE, o=28, name='reflections'),
    ]


@emoji(94, 'cat_cool', '😎', 'Крутой кот', frames=180, still=70)
def e_cat_cool(T):
    L = cat_head(T, mouth='smirk', blush=0, blink=(6,))
    lenses, shades = _shades()
    slide = anim((0, [0, -132], 'hold'), (16, [0, -132], 'in'), (34, [0, 6], 'out'), (40, [0, -4], 'io'), (46, [0, 0], 'hold'),
                 (150, [0, 0], 'io'), (172, [0, -132], 'hold'), (T, [0, -132]))
    glint = fx.shine(lenses, T, t0=64, dur=40, angle=-30, width=0.18, alpha=0.95)
    spark = fx.sparkle(392, 250, 26, T, t0=96, dur=34)
    glasses = group(shades, glint, spark, move=slide, name='glasses')
    eyes_o = anim((0, 100, 'hold'), (34, 0, 'hold'), (150, 100, 'hold'), (T, 100))
    L['eyes'] = [group(L['eyes'], o=eyes_o, name='eyes')]
    head = group(flat(L), glasses, pivot=(256, 256), s=100, r=anim((0, 0, 'io'), (40, -4, 'io'), (140, -4, 'io'),
                                                                   (170, 0, 'io'), (T, 0)), name='head')
    return [fx.glow(256, 300, 226, alpha=0.3), head]


@emoji(95, 'cat_peek', '👀', 'Подглядывает', frames=180, still=44)
def e_cat_peek(T):
    look = anim((0, [0, 0], 'io'), (46, [0, 0], 'io'), (56, [-15, 2], 'io'), (80, [-15, 2], 'io'), (92, [15, 2], 'io'),
                (116, [15, 2], 'io'), (126, [0, 0], 'io'), (T, [0, 0]))
    L = cat_head(T, look=look, blink=(134,), ear_l=_twitch(T, 30, n=1), ear_r=_twitch(T, 30, deg=14, n=1))
    # head without the lower face: its flat cut always stays hidden behind the snowdrift
    cut = P('M 58 378 C 50 334 52 290 62 250 C 80 160 156 122 256 122 C 356 122 432 160 450 250 '
            'C 460 290 462 334 454 378 Z')
    L['head'][0] = part(cut, fill=S.vgrad(FURS['gray']['fur'], *HEAD_Y), outline=S.OW, name='head')
    head = group(flat(L, skip=('muzzle', 'blush', 'whiskers', 'mouth')), pivot=(256, 300),
                 r=anim((0, 0, 'io'), (46, 0, 'io'), (56, -4, 'io'), (80, -4, 'io'), (92, 4, 'io'), (116, 4, 'io'),
                        (126, 0, 'io'), (T, 0)),
                 move=anim((0, [0, 104], 'hold'), (8, [0, 104], 'outback'), (30, [0, 30], 'io'), (148, [0, 30], 'in'),
                           (170, [0, 104], 'hold'), (T, [0, 104])), name='head')
    drift = P('M 28 422 C 66 390 122 386 170 398 C 214 408 244 402 286 392 C 340 378 420 382 484 418 '
              'L 484 462 C 484 476 476 484 462 484 L 50 484 C 36 484 28 476 28 462 Z')
    snow = [part(drift, fill=S.vgrad(S.G_SNOW, 384, 484), outline=S.OW, name='drift'),
            part(P('M 48 418 C 84 402 130 398 166 406'), P('M 302 398 C 350 386 410 390 456 410'),
                 stroke=stroke(S.WHITE, 8, o=90), name='drift_gloss'),
            fx.sparkles([(92, 452, 15), (256, 460, 12), (424, 448, 14)], T, start=20, gap=55, dur=36,
                        color=S.BLUE_L, halo=False)]
    grip = anim((0, [0, 22], 'hold'), (10, [0, 22], 'outback'), (28, [0, 0], 'io'), (150, [0, 0], 'in'),
                (166, [0, 22], 'hold'), (T, [0, 22]))
    paws = [group(_paw(150, 404, w=100, h=78), pivot=(150, 404), move=grip, name='paw_l'),
            group(_paw(362, 404, w=100, h=78), pivot=(362, 404), move=grip, name='paw_r')]
    return [head, snow, paws]
