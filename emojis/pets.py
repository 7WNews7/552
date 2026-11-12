"""Paws, dogs and pet items: 081, 082, 086, 096-100."""
import math
import random

from kit.registry import emoji
from kit.lottie import part, group, anim, loop, stroke, trim, ellipse
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
        part(rim, stroke=stroke(S.SKY, 5, o=30), trim=trim(52, 78), name='head_rim'),
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
                part(heart_path(ex, ey + 4, 82, 74), fill=S.vgrad(HEART_EYE, ey - 33, ey + 41), outline=(S.OUTLINE, 5),
                     name='heart_eye'),
                part(_ell(ex - 18, ey - 12, 11, 6.5, -38), fill=S.WHITE, o=92, name='glint'),
                part(_ell(ex + 16, ey + 8, 4.5), fill=S.WHITE, o=70, name='glint2'),
                pivot=(ex, ey + 8), s=eye_s, name='eye'))
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
@emoji(81, 'paw', '🐾', 'Лапка', frames=120, still=90)
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
    paw_g = group(paw_g, pivot=(cx, base_y), s=fx.breathe(T, 99, 101.5, shift=T / 2), name='idle')
    puff = (_fan(cx - 130, base_y - 14, T, 40, 5, 6, 90, 185, 250, size=(16, 28), dur=32, lift=30, seed=3) +
            _fan(cx + 130, base_y - 14, T, 40, 5, 6, 90, 290, 355, size=(16, 28), dur=32, lift=30, seed=8))
    ring = _flat_ring(cx, base_y - 24, 320, 470, 0.16, T, 40, dur=24, sw0=9, sw1=2, alpha=40)
    sparks = [fx.sparkle(424, 116, 28, T, t0=50, dur=40), fx.sparkle(92, 150, 20, T, t0=78, dur=36)]
    return [fx.glow(256, 276, 236, alpha=0.32), ring, shadow, paw_g, puff, sparks]


# ------------------------------------------------------------------ 082 paw trail
@emoji(82, 'paw_trail', '🐾', 'Следы лапок', frames=120, still=116)
def e_paw_trail(T):
    n, gap = 5, T / 5
    a, b = (104, 396), (388, 80)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
    nrm = (-u[1], u[0])
    rot = math.degrees(math.atan2(u[0], -u[1]))
    prints = []
    for k in range(n):
        side = 1 if k % 2 == 0 else -1
        f = k / (n - 1)
        px = a[0] + (b[0] - a[0]) * f + nrm[0] * 26 * side
        py = a[1] + (b[1] - a[1]) * f + nrm[1] * 26 * side
        sz = 0.44
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


# ------------------------------------------------------------------ 096 happy dog
@emoji(96, 'dog_happy', '😄', 'Довольный пёс', frames=120, still=15)
def e_dog_happy(T):
    # panting: mouth + tongue morph 4x per loop, head bobs on every breath, ears bounce behind
    pant = []
    for c in range(4):
        t0 = c * T / 4
        pant += [(t0, 0.15, 'sine'), (t0 + T / 8, 1.0, 'sine')]
    pant.append((T, 0.15))
    ear_l = fx.wave(T, -3, 7, cycles=4, shift=-4)
    ear_r = fx.wave(T, 3, -7, cycles=4, shift=-4)
    d = dog_head(T, eyes='happy', mouth='open', pant=pant, ear_l=ear_l, ear_r=ear_r, cy=246,
                 brows=fx.wave(T, [0, 0], [0, -5], cycles=4))
    sway = fx.swing(T, 4)
    head = group(d['head'], pivot=(256, 430), r=sway, move=fx.bob(T, 7, cycles=4, shift=T / 16), name='dog')
    sparks = [fx.sparkle(436, 118, 28, T, t0=10, dur=40), fx.sparkle(74, 132, 22, T, t0=40, dur=36),
              fx.sparkle(440, 420, 18, T, t0=70, dur=34)]
    return [fx.glow(256, 270, 236, alpha=0.3), head, sparks]


# ------------------------------------------------------------------ 097 dog in love
def _heart(x, y, w, stops):
    h = heart_path(x, y, w)
    return [part(h, fill=S.vgrad(stops, y - w * 0.45, y + w * 0.45), outline=S.OW_THIN, name='heart'),
            part(_ell(x - w * 0.2, y - w * 0.17, w * 0.13, w * 0.07, -38), fill=S.WHITE, o=85, name='heart_gloss')]


@emoji(97, 'dog_love', '🥰', 'Влюблённый пёс', frames=120, still=12)
def e_dog_love(T):
    beat = anim((0, 100, 'out'), (8, 118, 'in'), (16, 97, 'out'), (25, 112, 'in'), (40, 100, 'hold'),
                (60, 100, 'out'), (68, 118, 'in'), (76, 97, 'out'), (85, 112, 'in'), (100, 100, 'hold'), (T, 100))
    d = dog_head(T, eyes='heart', eye_s=beat, blush=70, cy=276, k=0.9,
                 ear_l=fx.swing(T, 4, shift=-8), ear_r=fx.swing(T, 4, shift=-8))
    head = group(d['head'], pivot=(256, 440), r=fx.swing(T, 5), move=fx.bob(T, 6, cycles=2), name='dog')
    # side hearts float up in front; the top one rises out from behind the head
    front = [group(_heart(x, y, w, stops), pivot=(x, y), **fx.rise(T, t0, 72, dy=-118, dx=dx, s0=30, s1=100))
             for x, y, w, t0, dx, stops in ((70, 318, 74, 0, -10, S.G_PINK), (444, 306, 66, 40, 10, S.G_ICE_SOFT))]
    back = [group(_heart(256, 150, 70, S.G_PINK), pivot=(256, 150), **fx.rise(T, 80, 64, dy=-84, s0=50, s1=100))]
    sparks = [fx.sparkle(110, 96, 24, T, t0=26, dur=36), fx.sparkle(412, 92, 22, T, t0=68, dur=36)]
    return [fx.glow(256, 286, 230, alpha=0.3, s=fx.breathe(T, 94, 104, cycles=2)), back, head, front, sparks]


# ------------------------------------------------------------------ 098 fish
FISH_BODY = [(68, 262), (100, 204), (168, 164), (254, 154), (332, 178), (380, 222), (394, 262), (378, 302),
             (330, 344), (254, 368), (168, 360), (100, 322)]
G_FISH = [(0.0, '#d4eeff'), (0.4, '#7cbcff'), (1.0, '#2f6fe0')]
G_FIN = [(0.0, '#8cc8ff'), (0.55, '#3f86ec'), (1.0, '#1f4fb2')]


@emoji(98, 'fish', '🐟', 'Рыбка', frames=120, still=0)
def e_fish(T):
    body = _spline(FISH_BODY)
    tail = P('M 366 244 C 398 214 432 178 474 160 C 460 204 452 236 448 262 C 452 288 460 320 474 364 '
             'C 432 346 398 310 366 280 Z')
    dorsal = P('M 176 176 C 190 128 232 102 290 104 C 280 126 292 152 318 182 Z')
    belly_fin = P('M 222 358 C 236 392 258 408 292 410 C 282 390 290 370 304 350 Z')
    pect = P('M 194 280 C 222 274 256 284 280 300 C 268 308 266 320 272 334 C 246 338 216 326 198 306 '
             'C 190 298 188 288 194 280 Z')
    pect_rays = [P('M 204 290 L 268 304'), P('M 204 298 L 258 326')]
    rays = [P('M 400 236 L 446 198'), P('M 404 262 L 440 262'), P('M 400 288 L 446 326'),
            P('M 214 160 L 236 120'), P('M 250 160 L 266 116')]
    scales = [P(f'M {x - 18} {y} C {x - 12} {y + 16} {x + 12} {y + 16} {x + 18} {y}')
              for x, y in ((262, 214), (306, 232), (262, 258), (306, 276), (342, 254), (218, 238))]
    swim = fx.swing(T, 14, cycles=2)
    tail_g = group(part(tail, fill=S.dgrad(G_FIN, (400, 180), (440, 360)), outline=S.OW, name='tail'),
                   part(rays[:3], stroke=stroke(S.ICE_L, 5, o=55), name='tail_rays'),
                   pivot=(372, 262), r=swim, name='tail')
    fins_back = [
        group(part(dorsal, fill=S.vgrad(G_FIN, 104, 182), outline=S.OW, name='dorsal'),
              part(rays[3:], stroke=stroke(S.ICE_L, 5, o=55), name='dorsal_rays'),
              pivot=(240, 176), r=fx.swing(T, 4, cycles=2, shift=6), name='dorsal'),
        group(part(belly_fin, fill=S.vgrad(G_FIN, 350, 410), outline=S.OW, name='belly_fin'),
              pivot=(262, 356), r=fx.swing(T, 6, cycles=2, shift=10), name='belly_fin'),
    ]
    body_parts = [
        part(body, fill=S.vgrad(G_FISH, 154, 368), outline=S.OW, name='body'),
        part(P('M 110 318 C 160 352 250 366 330 340 C 290 360 230 372 176 362 C 140 354 118 338 110 318 Z'),
             fill=S.WHITE, o=55, name='belly'),
        part(scales, stroke=stroke(S.WHITE, 5, o=45), name='scales'),
        part(P('M 172 196 C 192 226 194 296 172 330'), stroke=stroke(S.BLUE_D, 7, o=70), name='gill'),
        part(_ell(150, 200, 44, 16, -24), fill=S.WHITE, o=70, name='gloss'),
        part(_ell(214, 176, 10, 6, -12), fill=S.WHITE, o=60, name='gloss_dot'),
        group(part(pect, fill=S.dgrad(G_FIN, (214, 276), (270, 330)), outline=S.OW_THIN, name='pect'),
              part(pect_rays, stroke=stroke(S.ICE_L, 4, o=60), name='pect_rays'),
              pivot=(198, 290), r=fx.swing(T, 14, cycles=4), name='pect'),
        group(part(_ell(128, 236, 27, 29), fill=S.vgrad(S.G_SNOW, 208, 264), outline=(S.OUTLINE, 5), name='eye_white'),
              part(_ell(122, 240, 16, 18), fill=S.OUTLINE, name='pupil'),
              part(_ell(116, 232, 6.5), fill=S.WHITE, o=95, name='eye_glint'),
              pivot=(128, 236), s=fx.blink(T, 86, dur=12, closed=10), name='eye'),
        part(P('M 80 280 C 90 290 104 290 112 280'), stroke=stroke(S.OUTLINE, 7), name='mouth'),
    ]
    fish = group(tail_g, fins_back, body_parts, pivot=(256, 262),
                 r=fx.swing(T, 3, cycles=2, shift=T / 4), move=fx.bob(T, 14, cycles=1), name='fish')
    bubbles = []
    for k, (t0, r, dx) in enumerate(((6, 27, -18), (46, 19, 4), (84, 23, -24))):
        x, y = 70, 228
        bubbles.append(group(
            part(circle_path(x, y, r), fill=S.vgrad([(0, S.ICE_L), (1, S.SKY)], y - r, y + r, opacity=[(0, 0.15), (1, 0.45)]),
                 stroke=stroke(S.WHITE, 5, o=90), outline=(S.OUTLINE, 3.5), name='bubble'),
            part(_ell(x - r * 0.38, y - r * 0.38, r * 0.26), fill=S.WHITE, o=95, name='bubble_glint'),
            pivot=(x, y), **fx.rise(T, t0, 64, dy=-140, dx=dx, s0=30, s1=100)))
    sparks = [fx.sparkle(440, 120, 24, T, t0=24, dur=38), fx.sparkle(408, 444, 18, T, t0=78, dur=34)]
    return [fx.glow(256, 262, 232, alpha=0.3), group(fish, pivot=(256, 262), r=8), bubbles, sparks]


# ------------------------------------------------------------------ 099 bone
G_BONE = [(0.0, '#ffffff'), (0.45, '#eef7ff'), (1.0, '#a3cdf4')]


@emoji(99, 'bone', '🦴', 'Косточка', frames=120, still=0)
def e_bone(T):
    # crouch -> toss with a full twirl -> squash landing with a little rock, sparks fly off the ends
    cx, cy = 256, 254
    hx, ky, kr, hw = 134, 36, 46, 30          # knob centre x / y offset, knob radius, shaft half-width
    knobs = [circle_path(cx + sx * hx, cy + sy * ky, kr) for sx in (-1, 1) for sy in (-1, 1)]
    shaft = P(f'M {cx - hx} {cy - hw} L {cx + hx} {cy - hw} L {cx + hx} {cy + hw} L {cx - hx} {cy + hw} Z')
    bone = [shaft] + knobs
    top, bot = cy - ky - kr, cy + ky + kr
    under = P(f'M {cx - 96} {cy + 2} L {cx + 96} {cy + 2} L {cx + 96} {cy + hw} L {cx - 96} {cy + hw} Z')
    body = [
        part(bone, fill=S.vgrad(G_BONE, top, bot), outline=S.OW, name='bone'),
        part(under, fill=S.vgrad([(0, S.ICE), (1, '#7fb4ea')], cy, cy + hw, opacity=[(0, 0), (1, 0.75)]),
             name='shaft_shade'),
        part([_ell(cx + sx * hx + 6, cy + ky + 18, 22, 9, -10 * sx) for sx in (-1, 1)], fill='#86b9ec', o=45,
             name='knob_shade'),
        part(_ell(cx - 40, cy - 14, 44, 5), fill=S.ICE, o=55, name='shaft_line'),
        fx.shine(bone, T, t0=86, dur=30, angle=30, width=0.3, alpha=0.75),
    ]
    rest = -28
    spin = anim((0, rest, 'hold'), (24, rest, 'io'), (64, rest + 360, 'hold'), (T, rest + 360))
    toss = anim((0, [0, 0], 'hold'), (14, [0, 0], 'io'), (24, [0, 8], 'out'), (44, [0, -42], 'in'),
                (64, [0, 0], 'hold'), (T, [0, 0]))
    squash = anim((0, [100, 100], 'hold'), (14, [100, 100], 'io'), (24, [107, 93], 'out'), (32, [96, 104], 'io'),
                  (44, [100, 100], 'hold'), (64, [100, 100], 'out'), (68, [112, 88], 'io'), (78, [96, 104], 'io'),
                  (88, [100, 100], 'hold'), (T, [100, 100]))
    rock = fx.wobble(T, 66, 40, 5, n=2)
    piv = (cx, cy + 140)
    b = group(group(body, pivot=(cx, cy), r=spin, name='spin'), pivot=piv, s=squash, move=toss, r=rock, name='bone')
    sh_s = anim((0, [100, 100], 'hold'), (24, [100, 100], 'out'), (44, [62, 62], 'in'), (64, [100, 100], 'hold'), (T, [100, 100]))
    sh_o = anim((0, 22, 'hold'), (24, 22, 'out'), (44, 8, 'in'), (64, 22, 'hold'), (T, 22))
    shadow = part(ellipse(cx, 446, 300, 34), fill=S.NAVY_D, pivot=(cx, 446), s=sh_s, o=sh_o, name='shadow')
    a = math.radians(rest)
    ends = [(cx + 150 * math.cos(a), cy + 150 * math.sin(a) - 30), (cx - 150 * math.cos(a), cy - 150 * math.sin(a) - 30)]
    sparks = (_fan(ends[0][0], ends[0][1], T, 64, 4, 30, 74, 220, 330, size=(20, 30), dur=30, seed=4, shape='spark') +
              _fan(ends[1][0], ends[1][1], T, 66, 4, 30, 70, 200, 300, size=(18, 26), dur=30, seed=9, shape='spark') +
              [fx.sparkle(424, 334, 22, T, t0=96, dur=34), fx.sparkle(122, 150, 20, T, t0=8, dur=32)])
    return [fx.glow(cx, cy, 230, alpha=0.32), shadow, b, sparks]


# ------------------------------------------------------------------ 100 yarn
def _arc(px, py, rho, a0, a1):
    """Circular arc as an open Bez (angles in radians, y down)."""
    n = max(1, int(math.ceil(abs(a1 - a0) / (math.pi / 4))))
    da = (a1 - a0) / n
    kk = 4 / 3 * math.tan(da / 4) * rho
    b = Bez(closed=False)
    for j in range(n + 1):
        a = a0 + da * j
        tx, ty = -math.sin(a), math.cos(a)
        b.add((px + rho * math.cos(a), py + rho * math.sin(a)), (-tx * kk, -ty * kk), (tx * kk, ty * kk))
    b.i[0], b.o[-1] = [0.0, 0.0], [0.0, 0.0]
    return b


def _arc_inside(px, py, rho, cx, cy, R):
    """The part of circle (px, py, rho) that lies inside circle (cx, cy, R), or None."""
    d = math.hypot(cx - px, cy - py)
    if d >= rho + R or d <= abs(rho - R):
        return None
    a = (rho * rho - R * R + d * d) / (2 * d)
    h = math.sqrt(max(rho * rho - a * a, 0.0))
    ux, uy = (cx - px) / d, (cy - py) / d
    mx, my = px + a * ux, py + a * uy
    a1 = math.atan2(my - h * ux - py, mx + h * uy - px)
    a2 = math.atan2(my + h * ux - py, mx - h * uy - px)
    wrap = lambda x: (x + math.pi) % (2 * math.pi) - math.pi
    sweep = wrap(a2 - a1)
    t = wrap(math.atan2(uy, ux) - a1)
    if not (min(0, sweep) <= t <= max(0, sweep)):
        sweep -= math.copysign(2 * math.pi, sweep)
    return _arc(px, py, rho, a1, a1 + sweep)


@emoji(100, 'yarn', '🧶', 'Клубок', frames=120, still=30)
def e_yarn(T):
    cx, cy, R = 290, 238, 158
    base = S.BLUE
    # fills inside the rolling group are solid (rotation-invariant): the shading lives in static overlays
    set_b, set_a, erase = [], [], []
    pb = (cx + 1.6 * R, cy - 0.9 * R)
    for j in range(14):
        a = _arc_inside(pb[0], pb[1], R * (0.95 + 0.14 * j), cx, cy, R - 7)
        if a:
            set_b.append(a)
    pa = (cx - 1.15 * R, cy + 1.0 * R)
    for j in range(7):
        rho = R * (0.98 + 0.13 * j)
        a = _arc_inside(pa[0], pa[1], rho, cx, cy, R - 16)
        if a:
            set_a.append(a)
            erase.append(a)
    ball = circle_path(cx, cy, R)
    rolling = group(
        part(set_b, stroke=stroke('#62a0f2', 9), name='strands_back'),
        part(erase, stroke=stroke(base, R * 0.13 + 4, cap='butt'), name='band'),
        part(set_a, stroke=stroke(S.ICE, 10), name='strands_front'),
        pivot=(cx, cy), r=fx.spin(T, 1), name='rolling')
    shade = S.rgrad([(0, S.NAVY_D), (1, S.NAVY_D)], cx - 0.32 * R, cy - 0.36 * R, 1.5 * R,
                    opacity=[(0, 0), (0.5, 0.04), (1, 0.6)])
    ball_g = [
        part(ball, fill=base, outline=S.OW, name='ball'),
        rolling,
        part(ball, fill=shade, name='shade'),
        part(_ell(cx - 0.46 * R, cy - 0.5 * R, 0.3 * R, 0.13 * R, -42), fill=S.WHITE, o=70, name='gloss'),
        part(_ell(cx - 0.72 * R, cy - 0.12 * R, 0.06 * R), fill=S.WHITE, o=60, name='gloss_dot'),
    ]
    bounce = fx.wave(T, [0, 0], [0, -12], cycles=2)
    squash = anim((0, [106, 94], 'out'), (12, [100, 100], 'io'), (30, [100, 100], 'in'), (60, [106, 94], 'out'),
                  (72, [100, 100], 'io'), (90, [100, 100], 'in'), (T, [106, 94]))
    ball_grp = group(ball_g, pivot=(cx, cy + R), s=squash, move=bounce, name='yarn_ball')

    # loose thread: travelling wave running away from the rolling ball
    def thread(ph):
        pts = []
        n = 10
        for j in range(n):
            f = j / (n - 1)
            x = 222 - 178 * f
            y = 336 + 86 * math.sin(min(f * 2.0, 1) * math.pi / 2)
            y += (2 + 15 * f) * math.sin(2 * math.pi * (f * 1.5 + ph))
            pts.append((x, y))
        return _spline(pts, closed=False)
    keys = [(T * j / 8, thread(j / 8), 'linear') for j in range(8)] + [(T, thread(1.0))]
    th = morph(keys)
    thread_g = [part(th, stroke=stroke(S.OUTLINE, 16 + 10), name='thread_contour'),
                part(th, stroke=stroke(S.ICE, 16), name='thread')]
    sparks = [fx.sparkle(452, 96, 26, T, t0=20, dur=40), fx.sparkle(120, 120, 20, T, t0=74, dur=36)]
    return [fx.glow(cx, cy + 10, 226, alpha=0.3), thread_g, ball_grp, sparks]
