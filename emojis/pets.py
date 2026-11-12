"""Paws, dogs and pet items: 081, 082, 086, 096-100."""
import math
import random

from kit.registry import emoji
from kit.lottie import part, group, anim, loop, stroke, trim
from kit.geometry import P, Bez, bbox_of, circle_path, heart_path, morph, sparkle_path
from kit.motifs import paw
from kit import fx, style as S


# ------------------------------------------------------------------ helpers (this file only)
def _spline(pts, sharp=(), k=1.0, tip=0.2, closed=True):
    """Catmull-Rom curve through pts; indices in `sharp` become pointed corners."""
    n = len(pts)
    b = Bez(closed=closed)
    for j in range(n):
        p1 = pts[j]
        p0 = pts[j - 1] if (closed or j > 0) else p1
        p2 = pts[(j + 1) % n] if (closed or j < n - 1) else p1
        if j in sharp:
            i = ((p0[0] - p1[0]) * tip, (p0[1] - p1[1]) * tip)
            o = ((p2[0] - p1[0]) * tip, (p2[1] - p1[1]) * tip)
        else:
            tx, ty = (p2[0] - p0[0]) / 6 * k, (p2[1] - p0[1]) / 6 * k
            i, o = (-tx, -ty), (tx, ty)
        b.add(p1, i, o)
    return b


def _ell(cx, cy, rx, ry=None, rot=0.0):
    return circle_path(cx, cy, rx, ry).rotate(rot, cx, cy) if rot else circle_path(cx, cy, rx, ry)


def _mx(b):
    return b.mirror_x(256)


def _fan(cx, cy, T, t0, n, r0, r1, a0, a1, size=(10, 16), color=S.WHITE, dur=30, lift=0, seed=5, shape='dot'):
    """Particles flying out once per loop inside the angle range a0..a1 (degrees, y down)."""
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        a = math.radians(a0 + (a1 - a0) * (k + rnd.uniform(0.2, 0.8)) / n)
        rr = r1 * rnd.uniform(0.75, 1.0)
        sz = rnd.uniform(*size)
        p0 = [math.cos(a) * r0, math.sin(a) * r0]
        p1 = [math.cos(a) * rr, math.sin(a) * rr - lift * rnd.uniform(0.6, 1.0)]
        st = t0 + rnd.uniform(0, 3)
        mv = loop([(st, p0, 'out2'), (st + dur, p1, 'hold'), (st + T, p0)], T)
        sc = loop([(st, 0, 'out'), (st + dur * 0.25, 100, 'in'), (st + dur, 0, 'hold'), (st + T, 0)], T)
        body = sparkle_path(cx, cy, sz) if shape == 'spark' else circle_path(cx, cy, sz / 2)
        out.append(group(part(body, fill=color, name='p'), pivot=(cx, cy), move=mv, s=sc, name='particle'))
    return out


def _flat_ring(cx, cy, w0, w1, ratio, T, t0, dur=30, color=S.ICE_L, sw0=12, sw1=2, alpha=90):
    """Ground ripple: a flattened ring that widens and fades once per loop."""
    from kit.lottie import ellipse
    size = loop([(t0, [w0, w0 * ratio], 'out'), (t0 + dur, [w1, w1 * ratio], 'hold'), (t0 + T, [w0, w0 * ratio])], T)
    width = loop([(t0, sw0, 'out'), (t0 + dur, sw1, 'hold'), (t0 + T, sw0)], T)
    op = loop([(t0, 0, 'out'), (t0 + dur * 0.15, alpha, 'in'), (t0 + dur, 0, 'hold'), (t0 + T, 0)], T)
    return part(ellipse(cx, cy, size), stroke=stroke(color, width, o=op), name='ripple')


# ------------------------------------------------------------------ the rottweiler (086, 096, 097)
FUR = [(0.0, '#505b7c'), (0.5, '#2a3150'), (1.0, '#1b2136')]        # blue-black coat, moonlit on top
FUR_EAR = [(0.0, '#434c6c'), (1.0, '#141a2c')]
TAN = [(0.0, '#f2c58e'), (0.5, '#c98a4b'), (1.0, '#a3622e')]         # rottweiler markings
IRIS = [(0.0, '#2d180c'), (0.55, '#6b3b1c'), (1.0, '#b97a3a')]
PUPIL = '#170c07'
NOSE = [(0.0, '#5d6787'), (0.45, '#262d46'), (1.0, '#0b0f22')]
MOUTH_IN = [(0.0, '#1d2a58'), (1.0, '#0a1230')]
TONGUE = [(0.0, '#ffc6d8'), (0.55, '#ff8fb2'), (1.0, '#e26489')]
HEART_EYE = [(0.0, '#ffd9e6'), (0.5, '#ff7da6'), (1.0, '#d9466f')]
HAPPY_EYE = '#c3cfea'

HEAD = [(256, 100), (332, 104), (392, 132), (424, 190), (434, 262), (428, 334), (394, 392), (330, 430),
        (256, 442), (182, 430), (118, 392), (84, 334), (78, 262), (88, 190), (120, 132), (180, 104)]
MUZZLE = [(256, 318), (230, 306), (198, 310), (164, 332), (150, 368), (166, 402), (204, 424), (256, 432),
          (308, 424), (346, 402), (362, 368), (348, 332), (314, 310), (282, 306)]
EAR_L = P('M 212 116 C 178 96 126 98 96 122 C 70 142 64 196 78 238 C 86 264 106 274 120 256 '
          'C 146 218 172 170 212 116 Z')
EAR_PIVOT = (158, 114)
EYES = ((196, 268), (316, 268))
NOSE_C = (256, 322)


def _mouth_open(o):
    d = 50 + 24 * o
    return P(f'M 208 366 C 232 382 280 382 304 366 C 302 {366 + d * 0.78} 282 {366 + d} 256 {366 + d} '
             f'C 230 {366 + d} 210 {366 + d * 0.78} 208 366 Z')


def _tongue(o):
    b = 448 + 26 * o
    return P(f'M 224 398 C 236 388 276 388 288 398 C 292 {b - 26} 282 {b} 256 {b} C 230 {b} 220 {b - 26} 224 398 Z')


def _tongue_line(o):
    b = 448 + 26 * o
    return P(f'M 256 404 L 256 {b - 24}')


def dog_head(T, eyes='open', mouth='smile', ear_l=0, ear_r=0, blink=None, eye_s=None, nose=None,
             brows=None, pant=None, blush=0, cx=256, cy=256, k=1.0):
    """Chibi rottweiler head: the one character shared by 086 / 096 / 097.

    Design box at k=1 around (256, 256): head 76..436 x 98..442, ears out to x 60 / 452.
      eyes   'open' glossy brown | 'happy' ^ ^ squint | 'heart' pink hearts
      mouth  'smile' closed w-mouth | 'open' panting with the tongue out (animate with pant)
      ear_l, ear_r  ear rotation in degrees around the ear root, clockwise positive
                    (+ flops the left ear outwards, - the right one); static or animated
      blink  [sx, sy] eye scale (fx.blink); eye_s scalar eye scale (heart beat)
      nose   [sx, sy] nose scale (sniff twitch); brows [dx, dy] eyebrow offset (animated ok)
      pant   [(t, openness 0..1[, ease]), ...] keys spanning 0..T for the open mouth + tongue
      blush  cheek blush opacity 0..100 (static or animated)
    Returns dict(head=group, eyes=[(x, y)], nose=(x, y), top=(x, y), cheeks=[(x, y)]) in canvas
    coordinates; the group is placed with its design centre at (cx, cy), scaled by k."""
    head = _spline(HEAD)
    ear_r_path = _mx(EAR_L)
    piv_r = (512 - EAR_PIVOT[0], EAR_PIVOT[1])

    def ear(path, pivot, r, side):
        gx = 128 if side < 0 else 384
        return group(
            part(path, fill=S.vgrad(FUR_EAR, 104, 300), outline=S.OW, name='ear'),
            part(P('M 200 120 C 172 104 130 104 106 126').map(lambda x, y: (x if side < 0 else 512 - x, y)),
                 stroke=stroke('#8a96b8', 7, o=55), name='ear_fold'),
            part(_ell(gx, 160, 9, 22, 18 * -side), fill=S.WHITE, o=22, name='ear_gloss'),
            pivot=pivot, r=r, name='ear_' + ('l' if side < 0 else 'r'))

    # moonlit rim inside the lower-left contour keeps the dark coat readable on dark chat themes
    rim = head.scale(0.962, 0.962, 256, 272)
    base = [
        part(head, fill=S.vgrad(FUR, 98, 442), outline=S.OW, name='head'),
        part(rim, stroke=stroke(S.SKY, 6, o=45), trim=trim(50, 80), name='head_rim'),
        part(_ell(250, 132, 46, 15, -6), fill=S.WHITE, o=26, name='head_gloss'),
        part(_ell(300, 126, 9, 6), fill=S.WHITE, o=30, name='head_gloss_dot'),
    ]
    brow_paths = [_ell(202, 204, 27, 20, -12), _mx(_ell(202, 204, 27, 20, -12))]
    marks = [
        part(*brow_paths, fill=S.vgrad(TAN, 184, 224), outline=(S.OUTLINE, 3), move=brows, name='brows'),
        part(_spline(MUZZLE), fill=S.vgrad(TAN, 300, 434), outline=(S.OUTLINE, 4), name='muzzle'),
        part(_ell(214, 344, 20, 10, -20), fill=S.WHITE, o=35, name='muzzle_gloss'),
    ]
    if blush:
        marks.append(part(_ell(178, 360, 27, 14), _ell(334, 360, 27, 14), fill=S.PINK, o=blush, name='blush'))

    eye_items = []
    for ex, ey in EYES:
        if eyes == 'happy':
            arc = P(f'M {ex - 30} {ey + 12} C {ex - 20} {ey - 22} {ex + 20} {ey - 22} {ex + 30} {ey + 12}')
            eye_items.append(group(part(arc, stroke=stroke(S.OUTLINE, 28), name='lid_contour'),
                                   part(arc, stroke=stroke(HAPPY_EYE, 14), name='lid'),
                                   pivot=(ex, ey), s=eye_s, name='eye'))
        elif eyes == 'heart':
            eye_items.append(group(
                part(heart_path(ex, ey + 2, 92, 84), fill=S.vgrad(HEART_EYE, ey - 40, ey + 44), outline=(S.OUTLINE, 5),
                     name='heart_eye'),
                part(_ell(ex - 20, ey - 16, 12, 7, -38), fill=S.WHITE, o=92, name='glint'),
                part(_ell(ex + 18, ey + 8, 5), fill=S.WHITE, o=70, name='glint2'),
                pivot=(ex, ey + 6), s=eye_s, name='eye'))
        else:
            eye_items.append(group(
                part(_ell(ex, ey, 36, 40), fill=S.vgrad(IRIS, ey - 40, ey + 40), outline=(S.OUTLINE, 5), name='iris'),
                part(_ell(ex + 1, ey - 4, 23, 26), fill=PUPIL, name='pupil'),
                part(_ell(ex - 13, ey - 16, 13, 14), fill=S.WHITE, o=96, name='glint'),
                part(_ell(ex + 14, ey + 17, 6.5), fill=S.WHITE, o=85, name='glint2'),
                pivot=(ex, ey), s=blink if blink is not None else eye_s, name='eye'))

    nose_path = P('M 256 290 C 292 290 310 300 310 316 C 310 336 282 354 256 356 '
                  'C 230 354 202 336 202 316 C 202 300 220 290 256 290 Z')
    nose_g = group(
        part(nose_path, fill=S.vgrad(NOSE, 290, 356), outline=(S.OUTLINE, 5), name='nose'),
        part(_ell(236, 304, 17, 8, -12), fill=S.WHITE, o=88, name='nose_gloss'),
        part(_ell(272, 302, 5, 3), fill=S.WHITE, o=60, name='nose_gloss2'),
        pivot=(256, 330), s=nose, name='nose')

    lip = [P('M 256 352 L 256 370'), P('M 256 368 C 250 386 226 392 210 376'),
           P('M 256 368 C 262 386 286 392 302 376')]
    mouth_items = []
    if mouth == 'open':
        keys = pant or [(0, 1.0), (T, 1.0)]
        mk = lambda fn: morph([(kk[0], fn(kk[1])) + tuple(kk[2:]) for kk in keys]) if len(keys) > 1 else fn(keys[0][1])
        mouth_items += [
            part(mk(_mouth_open), fill=S.vgrad(MOUTH_IN, 366, 440), outline=(S.OUTLINE, 5), name='mouth'),
            part(mk(_tongue), fill=S.vgrad(TONGUE, 392, 476), outline=(S.OUTLINE, 5), name='tongue'),
            part(mk(_tongue_line), stroke=stroke('#d0507a', 6), name='tongue_line'),
            part(_ell(238, 412, 9, 5, -20), fill=S.WHITE, o=60, name='tongue_gloss'),
        ]
    mouth_items.append(part(*lip, stroke=stroke(S.OUTLINE, 9), name='lip'))

    parts = [base, ear(EAR_L, EAR_PIVOT, ear_l, -1), ear(ear_r_path, piv_r, ear_r, 1),
             marks, eye_items, mouth_items, nose_g]
    g = group(parts, pivot=(256, 256), pos=(cx, cy), s=None if k == 1 else k * 100, name='dog_head')
    to = lambda x, y: (cx + (x - 256) * k, cy + (y - 256) * k)
    return {'head': g, 'eyes': [to(*e) for e in EYES], 'nose': to(*NOSE_C), 'top': to(256, 98),
            'cheeks': [to(178, 360), to(334, 360)], 'k': k}


# ------------------------------------------------------------------ 081 paw
@emoji(81, 'paw', '🐾', 'Лапка', frames=120, still=70)
def e_paw(T):
    cx, cy, sz = 256, 270, 1.6
    pw = paw(cx, cy, size=sz)
    x0, y0, x1, y1 = bbox_of(pw)
    base_y = y1                       # squash pivot: bottom of the pad
    glints = [_ell(cx - 44 * sz, cy + 22 * sz, 24 * sz, 11 * sz, -32)]
    for tx, ty, rot in ((-92, -38, -24), (-34, -86, -8), (34, -86, 8), (92, -38, 24)):
        gx, gy = cx + (tx - 9) * sz, cy + (ty - 14) * sz
        glints.append(_ell(gx, gy, 7 * sz, 12 * sz, rot - 20))
    body = [
        part(pw, fill=S.vgrad(S.G_ICE, y0, y1), outline=S.OW, name='paw'),
        part(glints, fill=S.WHITE, o=80, name='paw_gloss'),
        fx.shine(pw, T, t0=64, dur=44, angle=24, width=0.26, alpha=0.75),
    ]
    # lift (anticipation) -> slam -> squash -> settle
    lift = anim((0, [0, 0], 'hold'), (8, [0, 0], 'io'), (30, [0, -30], 'in2'), (40, [0, 0], 'hold'), (T, [0, 0]))
    tilt = anim((0, 0, 'hold'), (8, 0, 'io'), (30, -6, 'in2'), (40, 0, 'hold'), (T, 0))
    scl = anim((0, [100, 100], 'hold'), (8, [100, 100], 'io'), (30, [105, 105], 'in2'), (40, [100, 100], 'out'),
               (44, [113, 87], 'io'), (54, [95, 105], 'io'), (64, [102, 98], 'io'), (74, [100, 100], 'hold'), (T, [100, 100]))
    shadow_o = anim((0, 40, 'hold'), (8, 40, 'io'), (30, 18, 'in2'), (40, 40, 'hold'), (T, 40))
    shadow_s = anim((0, [100, 100], 'hold'), (8, [100, 100], 'io'), (30, [92, 92], 'in2'), (40, [100, 100], 'hold'), (T, [100, 100]))
    shadow = part([b.translate(0, 12) for b in pw], fill=S.NAVY_D, pivot=(cx, base_y), s=shadow_s, o=shadow_o,
                  name='paw_shadow')
    paw_g = group(group(body, pivot=(cx, base_y), s=scl, name='squash'), pivot=(cx, base_y), move=lift, r=tilt, name='paw')
    puff = (_fan(cx - 130, base_y - 14, T, 40, 5, 6, 90, 185, 250, size=(16, 28), dur=32, lift=30, seed=3) +
            _fan(cx + 130, base_y - 14, T, 40, 5, 6, 90, 290, 355, size=(16, 28), dur=32, lift=30, seed=8))
    ring = _flat_ring(cx, base_y - 24, 320, 470, 0.16, T, 40, dur=26, sw0=10, sw1=2, alpha=55)
    sparks = [fx.sparkle(424, 116, 28, T, t0=50, dur=40), fx.sparkle(92, 150, 20, T, t0=78, dur=36)]
    return [fx.glow(256, 276, 236, alpha=0.32), ring, shadow, paw_g, puff, sparks]


# ------------------------------------------------------------------ 082 paw trail
@emoji(82, 'paw_trail', '🐾', 'Следы лапок', frames=120, still=100)
def e_paw_trail(T):
    n, gap = 5, T / 5
    a, b = (112, 424), (400, 100)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
    nrm = (-u[1], u[0])
    rot = math.degrees(math.atan2(u[0], -u[1]))
    prints = []
    for k in range(n):
        side = 1 if k % 2 == 0 else -1
        f = k / (n - 1)
        px = a[0] + (b[0] - a[0]) * f + nrm[0] * 30 * side
        py = a[1] + (b[1] - a[1]) * f + nrm[1] * 30 * side
        sz = 0.46
        pw = paw(px, py, size=sz, rot=rot)
        bx0, by0, bx1, by1 = bbox_of(pw)
        t0 = 4 + k * gap
        sc = loop([(t0, 40, 'outback2'), (t0 + 14, 100, 'hold'), (t0 + 74, 100, 'in'), (t0 + 94, 84, 'hold'), (t0 + T, 40)], T)
        op = loop([(t0, 0, 'out'), (t0 + 5, 100, 'hold'), (t0 + 74, 100, 'in'), (t0 + 94, 0, 'hold'), (t0 + T, 0)], T)
        prints.append(group(
            part(pw, fill=S.vgrad(S.G_ICE_SOFT, by0, by1), outline=(S.OUTLINE, 6), name='print'),
            part(_ell(px - 34 * sz, py + 22 * sz, 24 * sz, 11 * sz, -32).rotate(rot, px, py), fill=S.WHITE, o=85,
                 name='print_gloss'),
            pivot=(px, py), s=sc, o=op, name='step'))
    sparks = [fx.sparkle(420, 300, 22, T, t0=30, dur=34), fx.sparkle(110, 150, 18, T, t0=80, dur=34)]
    return [fx.glow(256, 262, 230, alpha=0.26), prints, sparks]


# ------------------------------------------------------------------ 086 dog
@emoji(86, 'dog', '🐶', 'Ротвейлер', frames=180, still=0)
def e_dog(T):
    # curious head tilt (ears lag behind), sniff-sniff, ears perk and flop back, blinks
    tilt = anim((0, 0, 'hold'), (36, 0, 'outback'), (58, 9, 'io'), (104, 9, 'io'), (130, 0, 'hold'), (T, 0))
    lag = [(0, 0), (36, 0), (44, -7), (54, 5), (63, -2.5), (72, 0), (104, 0), (112, 7), (122, -4.5), (131, 2), (138, 0)]
    perk = [(140, 0, 'outback'), (149, 11), (156, 11, 'in'), (163, -4), (169, 2), (175, 0)]
    ear_l = anim([(t, v, 'sine') for t, v in lag] + [(t, v) + tuple(e) for t, v, *e in perk] + [(T, 0)])
    ear_r = anim([(t, v, 'sine') for t, v in lag] + [(t, -v) + tuple(e) for t, v, *e in perk] + [(T, 0)])
    sniff = anim((0, [100, 100], 'hold'), (64, [100, 100], 'out'), (68, [108, 92], 'in'), (72, [100, 100], 'out'),
                 (76, [108, 92], 'in'), (81, [100, 100], 'hold'), (T, [100, 100]))
    brows = anim((0, [0, 0], 'hold'), (38, [0, 0], 'outback'), (54, [0, -8], 'hold'), (104, [0, -8], 'io'),
                 (124, [0, 0], 'hold'), (T, [0, 0]))
    blink = anim((0, [100, 100], 'hold'), (14, [100, 100], 'in'), (19, [104, 8], 'hold'), (21, [104, 8], 'out'),
                 (27, [100, 100], 'hold'), (146, [100, 100], 'in'), (151, [104, 8], 'hold'), (153, [104, 8], 'out'),
                 (159, [100, 100], 'hold'), (T, [100, 100]))
    d = dog_head(T, ear_l=ear_l, ear_r=ear_r, blink=blink, nose=sniff, brows=brows, cy=262)
    head = group(d['head'], pivot=(256, 430), r=tilt, move=fx.bob(T, 6, cycles=2), name='dog')
    sparks = [fx.sparkle(430, 108, 26, T, t0=56, dur=40), fx.sparkle(84, 424, 18, T, t0=132, dur=36)]
    return [fx.glow(256, 276, 236, alpha=0.3), head, sparks]
