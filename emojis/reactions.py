"""011-032: reactions and symbols."""
import math

from kit.registry import emoji
from kit.lottie import part, group, anim, loop, phase, stroke, trim, ellipse
from kit.geometry import P, Bez, bbox_of, circle_path, heart_path, polyline, line, rounded, star, sparkle_path, morph
from kit.text import glyphs, fit_cap
from kit.motifs import paw
from kit import fx, style as S


# ------------------------------------------------------------- helpers (this file only)
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


def _spline(pts, sharp=(), k=1.0, tip=0.2):
    """Closed Catmull-Rom curve through pts; indices in `sharp` become pointed tips."""
    n = len(pts)
    b = Bez()
    for j in range(n):
        p0, p1, p2 = pts[j - 1], pts[j], pts[(j + 1) % n]
        if j in sharp:
            i = ((p0[0] - p1[0]) * tip, (p0[1] - p1[1]) * tip)
            o = ((p2[0] - p1[0]) * tip, (p2[1] - p1[1]) * tip)
        else:
            tx, ty = (p2[0] - p0[0]) / 6 * k, (p2[1] - p0[1]) / 6 * k
            i, o = (-tx, -ty), (tx, ty)
        b.add(p1, i, o)
    return b


def _inked(paths, w, color, ow=S.OW_THIN, tr=None, o=None, name='ink'):
    """Solid stroke with a navy contour (gradient strokes are forbidden)."""
    return group(part(paths, stroke=stroke(S.OUTLINE, w + 2 * ow), trim=tr, name=name + '_contour'),
                 part(paths, stroke=stroke(color, w), trim=tr, name=name), o=o, name=name)


def _sq(T, keys):
    """[sx, sy] scale keys -> looping property (keys: (t, sx, sy[, ease]))."""
    return anim([(k[0], [k[1], k[2]]) + tuple(k[3:]) for k in keys] + [(T, [100, 100])])


ICE_GRAD = [(0, '#f2faff'), (0.45, '#a3d4ff'), (1, '#3b7ce8')]


@emoji(11, 'check', '✅', 'Галочка — принято', frames=120, still=64)
def e_check(T):
    cx, cy, R = 256, 256, 192
    pop = anim((0, 100, 'in'), (8, 93, 'outback'), (30, 100, 'io'), (T, 100))
    disc = circle_path(cx, cy, R)
    badge = [
        part(disc, fill=S.vgrad([(0, '#7cc4ff'), (0.5, '#2f74e6'), (1, '#173e9e')], cy - R, cy + R), outline=S.OW),
        part(circle_path(cx, cy, R - 24), stroke=stroke(S.ICE_L, 7, o=30), name='inner_ring'),
        part(P('M 118 196 C 140 132 196 92 262 88 C 210 104 160 140 136 206 Z'), fill=S.WHITE, o=55, name='gloss'),
    ]
    mark = polyline([(158, 262), (224, 328), (356, 194)])
    s_tr = anim((0, 0, 'in'), (8, 100, 'hold'), (9, 0, 'hold'), (T, 0))
    e_tr = anim((0, 100, 'hold'), (9, 0, 'hold'), (12, 0, 'out2'), (34, 100, 'hold'), (T, 100))
    shadow = part(mark.translate(0, 12), stroke=stroke(S.NAVY_D, 60, o=40), trim=trim(s_tr, e_tr), name='shadow')
    tick = part(mark, stroke=stroke(S.WHITE, 60), trim=trim(s_tr, e_tr), name='tick')
    body = group(badge, fx.shine([disc], T, t0=56, dur=50, alpha=0.45), shadow, tick, pivot=(cx, cy), s=pop)
    ring = fx.ring_pulse(cx, cy, R - 6, R + 46, T, t0=30, dur=42, w0=16)
    sparks = fx.sparkles([(394, 128, 30), (116, 392, 22), (420, 352, 18)], T, start=32, gap=9, dur=38)
    return [ring, body, sparks]


@emoji(12, 'cross', '❌', 'Крестик — отклонено', frames=120, still=64)
def e_cross(T):
    cx, cy, R = 256, 256, 192
    pop = anim((0, 100, 'in'), (8, 93, 'outback'), (30, 100, 'io'), (T, 100))
    disc = circle_path(cx, cy, R)
    badge = [
        part(disc, fill=S.vgrad(S.G_RED, cy - R, cy + R), outline=S.OW),
        part(circle_path(cx, cy, R - 24), stroke=stroke('#ffe1e7', 7, o=35), name='inner_ring'),
        part(P('M 118 196 C 140 132 196 92 262 88 C 210 104 160 140 136 206 Z'), fill=S.WHITE, o=55, name='gloss'),
    ]
    d = 80
    bars = [line(cx - d, cy - d, cx + d, cy + d), line(cx + d, cy - d, cx - d, cy + d)]
    # both strokes are wiped at the loop start, then redrawn one after the other
    s_tr = anim((0, 0, 'in'), (8, 100, 'hold'), (9, 0, 'hold'), (T, 0))
    trims = [trim(s_tr, anim((0, 100, 'hold'), (9, 0, 'hold'), (t0, 0, 'out2'), (t0 + 16, 100, 'hold'), (T, 100)))
             for t0 in (11, 23)]
    shadows = [part(b.translate(0, 12), stroke=stroke('#7a1430', 58, o=40), trim=tr, name='shadow')
               for b, tr in zip(bars, trims)]
    marks = [part(b, stroke=stroke(S.WHITE, 58), trim=tr, name='bar') for b, tr in zip(bars, trims)]
    shake = fx.wobble(T, 40, 36, 14, n=3, vector=(1, 0))
    body = group(badge, fx.shine([disc], T, t0=78, dur=40, alpha=0.4), shadows, marks,
                 pivot=(cx, cy), s=pop, move=shake, r=fx.wobble(T, 40, 36, 5, n=3))
    ring = fx.ring_pulse(cx, cy, R - 6, R + 46, T, t0=36, dur=42, w0=16, color='#ffd3da')
    sparks = fx.sparkles([(398, 124, 26), (112, 396, 20)], T, start=80, gap=12, dur=36)
    return [ring, body, sparks]


@emoji(13, 'exclamation', '❗', 'Восклицательный знак', frames=120, still=62)
def e_exclamation(T):
    cx, top, y1 = 256, 66, 450
    bar = _capsule((cx, top + 62), 62, (cx, 300), 38)
    dot = circle_path(cx, 402, 48)
    grad = S.vgrad(ICE_GRAD, top, y1)
    sign = [
        part(bar, dot, fill=grad, outline=S.OW, name='sign'),
        part(_capsule((cx - 30, top + 44), 13, (cx - 22, top + 168), 8), fill=S.WHITE, o=75, name='gloss'),
        part(circle_path(cx - 18, 384, 13, 9).rotate(-35, cx - 18, 384), fill=S.WHITE, o=80, name='dot_gloss'),
    ]
    # anticipation squash -> jump -> landing squash, around the bottom of the dot
    sq = _sq(T, [(0, 100, 100, 'hold'), (10, 100, 100, 'io'), (20, 112, 89, 'out'), (28, 95, 104, 'io'),
                 (40, 100, 100, 'in'), (52, 97, 103, 'out'), (56, 115, 87, 'outback'), (74, 100, 100, 'hold')])
    jump = anim((0, [0, 0], 'hold'), (20, [0, 0], 'out'), (40, [0, -34], 'in'), (54, [0, 0], 'hold'), (T, [0, 0]))
    body = group(sign, fx.shine([bar, dot], T, t0=74, dur=40, alpha=0.7, width=0.3),
                 pivot=(cx, y1), s=sq, move=jump, name='bang')
    # alert strokes shoot out at the landing and retract outwards
    rays = []
    for a in (165, 195, 225):
        for sgn in (1, -1):
            ang = math.radians(a if sgn > 0 else 180 - a)
            r0, r1 = 150, 196
            c0 = (cx + r0 * math.cos(ang), 196 + r0 * math.sin(ang))
            c1 = (cx + r1 * math.cos(ang), 196 + r1 * math.sin(ang))
            rays.append(line(c0[0], c0[1], c1[0], c1[1]))
    ray_tr = trim(anim((0, 0, 'hold'), (64, 0, 'in'), (80, 100, 'hold'), (T, 100)),
                  anim((0, 0, 'hold'), (54, 0, 'out'), (62, 100, 'hold'), (T, 100)))
    glow = fx.glow(cx, 250, 232, alpha=0.4, s=fx.pulse(T, 50, 56, 86, 106), o=fx.pulse(T, 50, 56, 55, 100))
    sparks = [fx.sparkle(346, 86, 24, T, t0=66, dur=36), fx.sparkle(168, 392, 18, T, t0=80, dur=32)]
    return [glow, _inked(rays, 18, S.WHITE, tr=ray_tr, name='rays'), body, sparks]


@emoji(14, 'question', '❓', 'Вопрос', frames=120, still=0)
def e_question(T):
    cap = 372
    (paths, _), = glyphs('?', 256, 256, cap, weight=900)
    hook, dot = sorted(paths, key=lambda p: p.bbox()[1])
    x0, y0, x1, y1 = hook.bbox()[0], hook.bbox()[1], hook.bbox()[2], dot.bbox()[3]
    dx, dy = 256 - (x0 + x1) / 2, 254 - (y0 + y1) / 2
    hook, dot = hook.translate(dx, dy), dot.translate(dx, dy)
    x0, y0, x1, y1 = x0 + dx, y0 + dy, x1 + dx, y1 + dy
    grad = S.vgrad(ICE_GRAD, y0, y1)
    dx0, dy0, dx1, dy1 = dot.bbox()
    dcx, dcy = (dx0 + dx1) / 2, (dy0 + dy1) / 2
    hb = hook.bbox()
    stem = ((hb[0] + hb[2]) / 2 - 4, hb[3])           # bottom of the stem: tilt pivot
    hook_g = group(
        part(hook, fill=grad, outline=S.OW, name='hook'),
        part(circle_path(x0 + 74, y0 + 92, 34, 20).rotate(-48, x0 + 74, y0 + 92), fill=S.WHITE, o=80, name='gloss'),
        fx.shine([hook], T, t0=58, dur=40, alpha=0.7, width=0.3),
        pivot=stem, r=anim((0, 0, 'hold'), (14, 0, 'outback'), (30, -13, 'sine'), (52, -10, 'outback'),
                           (68, 12, 'sine'), (90, 9, 'outback'), (108, 0, 'hold'), (T, 0)),
        name='hook')
    hop = anim((0, [0, 0], 'hold'), (12, [0, 0], 'out'), (20, [0, -22], 'in'), (28, [0, 0], 'hold'),
               (50, [0, 0], 'out'), (58, [0, -22], 'in'), (66, [0, 0], 'hold'),
               (88, [0, 0], 'out'), (96, [0, -16], 'in'), (104, [0, 0], 'hold'), (T, [0, 0]))
    dot_sq = _sq(T, [(0, 100, 100, 'hold'), (27, 100, 100, 'out'), (30, 118, 84, 'outback'), (40, 100, 100, 'hold'),
                     (65, 100, 100, 'out'), (68, 118, 84, 'outback'), (78, 100, 100, 'hold'),
                     (103, 100, 100, 'out'), (106, 112, 90, 'outback'), (116, 100, 100, 'hold')])
    dot_g = group(group(part(dot, fill=grad, outline=S.OW, name='dot'),
                        part(circle_path(dcx - 12, dcy - 12, 10, 7).rotate(-35, dcx - 12, dcy - 12), fill=S.WHITE, o=80),
                        pivot=(dcx, dy1), s=dot_sq), move=hop, name='dot')
    body = group(hook_g, dot_g, pivot=(256, y1), move=fx.bob(T, 8, cycles=2))
    sparks = [fx.sparkle(410, 96, 28, T, t0=30, dur=38), fx.sparkle(96, 120, 22, T, t0=70, dur=36),
              fx.sparkle(404, 330, 16, T, t0=96, dur=30)]
    return [fx.glow(256, 250, 226, alpha=0.32), body, sparks]


@emoji(15, 'warning', '⚠️', 'Внимание', frames=120, still=20)
def e_warning(T):
    tri = rounded([(256, 30), (488, 448), (24, 448)], 54)
    pivot = (256, 312)
    beat = anim((0, 100, 'out'), (8, 106, 'io'), (26, 100, 'hold'), (60, 100, 'out'), (68, 106, 'io'), (86, 100, 'hold'), (T, 100))
    # gloss strip parallel to the upper-left edge
    ex, ey = (24 - 256) / 448.0, 418 / 448.0
    el = math.hypot(ex, ey)
    ex, ey = ex / el, ey / el
    nx, ny = -ey, ex
    nx, ny = -nx, -ny
    def at(t, off):
        return (256 + (24 - 256) * t + nx * off, 30 + 418 * t + ny * off)
    gloss = rounded([at(0.2, 30), at(0.2, 46), at(0.56, 46), at(0.56, 30)], 7)
    plate = [
        part(tri, fill=S.vgrad(S.G_GOLD, 40, 448), outline=S.OW, name='plate'),
        part(rounded([(256, 100), (432, 418), (80, 418)], 30), stroke=stroke(S.WHITE, 8, o=40), name='inner'),
        part(gloss, fill=S.WHITE, o=70, name='gloss'),
    ]
    mark_sq = _sq(T, [(0, 100, 100, 'hold'), (20, 100, 100, 'out'), (24, 112, 88, 'outback'), (38, 100, 100, 'hold'),
                      (80, 100, 100, 'out'), (84, 112, 88, 'outback'), (98, 100, 100, 'hold')])
    hop = anim((0, [0, 0], 'out'), (10, [0, -24], 'in'), (20, [0, 0], 'hold'),
               (60, [0, 0], 'out'), (70, [0, -24], 'in'), (80, [0, 0], 'hold'), (T, [0, 0]))
    mark = group(part(_capsule((256, 214), 30, (256, 318), 19), circle_path(256, 378, 25),
                      fill=S.vgrad([(0, '#1f3f86'), (1, S.OUTLINE)], 184, 403), name='mark'),
                 part(circle_path(246, 214, 9, 14), fill=S.WHITE, o=35, name='mark_gloss'),
                 pivot=(256, 403), s=mark_sq, move=hop, name='bang')
    def ping(t0):
        sc = loop([(t0, 100, 'out'), (t0 + 40, 112, 'hold'), (t0 + T, 100)], T)
        op = loop([(t0, 0, 'out'), (t0 + 6, 80, 'in'), (t0 + 40, 0, 'hold'), (t0 + T, 0)], T)
        return part(tri, stroke=stroke('#ffe7a0', 12), pivot=pivot, s=sc, o=op, name='ping')
    body = group(plate, fx.shine([tri], T, t0=30, dur=44, alpha=0.5), mark, pivot=pivot, s=beat)
    glow = fx.glow(256, 300, 236, color='#ffd66b', alpha=0.3,
                   o=anim((0, 60, 'out'), (10, 100, 'io'), (40, 60, 'hold'), (60, 60, 'out'), (70, 100, 'io'), (100, 60, 'hold'), (T, 60)))
    sparks = [fx.sparkle(330, 64, 24, T, t0=26, dur=34), fx.sparkle(444, 380, 18, T, t0=86, dur=30)]
    return [glow, ping(2), ping(62), body, sparks]


@emoji(16, 'heart', '💙', 'Ледяное сердце', frames=120, still=0)
def e_heart(T):
    beat = anim((0, 100, 'out'), (9, 113, 'in'), (18, 98, 'out'), (28, 109, 'in'), (44, 100, 'io'), (T, 100))
    h = heart_path(256, 270, 404, 366)
    body = [
        part(h, fill=S.vgrad([(0, '#b2e0ff'), (0.45, '#4f97f5'), (1, '#1a40a0')], 88, 452), outline=S.OW),
        part(circle_path(168, 172, 50, 26).rotate(-38, 168, 172), fill=S.WHITE, o=85, name='gloss'),
        part(circle_path(118, 236, 13), fill=S.WHITE, o=75, name='gloss_dot'),
    ]
    heart = group(body, fx.shine([h], T, t0=52, dur=48, alpha=0.55), pivot=(256, 300), s=beat)
    minis = []
    for k, (x, y, sz, t0) in enumerate(((96, 330, 64, 18), (420, 300, 54, 30))):
        mh = heart_path(x, y, sz)
        rise = anim((0, [0, 0], 'hold'), (t0, [0, 0], 'out'), (t0 + 56, [0, -150], 'hold'), (T, [0, -150]))
        op = anim((0, 0, 'hold'), (t0, 0, 'out'), (t0 + 10, 100, 'linear'), (t0 + 36, 100, 'in'), (t0 + 56, 0, 'hold'), (T, 0))
        sc = anim((0, 40, 'hold'), (t0, 40, 'outback'), (t0 + 20, 100, 'io'), (T, 100))
        minis.append(group(part(mh, fill=S.vgrad(S.G_ICE, y - sz / 2, y + sz / 2), outline=S.OW_THIN),
                           pivot=(x, y), move=rise, o=op, s=sc, name='mini_heart'))
    return [fx.glow(256, 270, 236, alpha=0.38, s=beat), minis, heart,
            fx.sparkles([(404, 128, 26), (120, 112, 20)], T, start=14, gap=40, dur=40)]


HEART_GRAD = [(0, '#b2e0ff'), (0.45, '#4f97f5'), (1, '#1a40a0')]


@emoji(17, 'heart_break', '💔', 'Разбитое сердце', frames=120, still=50)
def e_heart_break(T):
    h = heart_path(256, 272, 380, 344)
    tip = (256, 444)
    crack = [(279, 220), (237, 272), (281, 326), (241, 384)]       # dip -> tip
    hv, hi, ho = h.v, h.i, h.o
    left = Bez().add(hv[0], (0, 0), ho[0]).add(hv[1], hi[1], ho[1]).add(hv[2], hi[2], ho[2]).add(hv[3], hi[3], (0, 0))
    for p in reversed(crack):
        left.add(p)
    right = Bez().add(hv[3], (0, 0), ho[3]).add(hv[4], hi[4], ho[4]).add(hv[5], hi[5], ho[5]).add(hv[0], hi[0], (0, 0))
    for p in crack:
        right.add(p)
    seam = polyline([tuple(hv[0])] + crack + [tuple(hv[3])])
    grad = S.vgrad(HEART_GRAD, 98, 444)
    # halves hinge on the bottom tip: crack -> split -> hold apart -> snap back together
    def half(sgn):
        r = anim((0, 0, 'hold'), (4, 0, 'sine'), (8, -1.5 * sgn, 'sine'), (12, 0, 'out'), (26, 9 * sgn, 'io'),
                 (48, 7.5 * sgn, 'io'), (68, 9 * sgn, 'in'), (80, 0, 'outback'), (96, 0, 'hold'), (T, 0))
        mv = anim((0, [0, 0], 'hold'), (12, [0, 0], 'out'), (26, [6 * sgn, 0], 'io'), (68, [6 * sgn, 0], 'in'),
                  (80, [0, 0], 'hold'), (T, [0, 0]))
        return {'pivot': tip, 'r': r, 'move': mv}
    L, R = half(-1), half(1)
    hb = h.bbox()
    outlines = [group(part(left, stroke=stroke(S.OUTLINE, 2 * S.OW)), **L, name='l_contour'),
                group(part(right, stroke=stroke(S.OUTLINE, 2 * S.OW)), **R, name='r_contour')]
    fills = [
        group(part(left, fill=grad, name='left'),
              part(circle_path(172, 182, 46, 24).rotate(-38, 172, 182), fill=S.WHITE, o=85, name='gloss'),
              part(circle_path(124, 242, 12), fill=S.WHITE, o=75, name='gloss_dot'),
              fx.shine([left], T, t0=92, dur=26, alpha=0.5, bbox=hb),
              part(seam, stroke=stroke(S.OUTLINE, 9), name='crack'), **L, name='left_half'),
        group(part(right, fill=grad, name='right'),
              part(circle_path(348, 164, 18, 10).rotate(-30, 348, 164), fill=S.WHITE, o=45, name='gloss'),
              fx.shine([right], T, t0=92, dur=26, alpha=0.5, bbox=hb),
              part(seam, stroke=stroke(S.OUTLINE, 9), name='crack'), **R, name='right_half'),
    ]
    thump = anim((0, 100, 'hold'), (80, 100, 'out'), (86, 106, 'io'), (100, 100, 'hold'), (T, 100))
    heart = group(outlines, fills, pivot=(256, 300), s=thump, name='heart')
    shards = []
    specs = [((262, 200), (-70, -60), -160), ((250, 250), (84, -48), 200), ((262, 300), (-96, -10), -220),
             ((252, 350), (98, 6), 180), ((258, 396), (-74, -30), -140), ((244, 172), (40, -84), 120)]
    for k, ((x, y), (ddx, ddy), rot) in enumerate(specs):
        t0 = 14 + k * 2
        sz = 15 - (k % 3) * 2
        sh = rounded([(x, y - sz), (x + sz * 0.8, y + sz * 0.6), (x - sz * 0.7, y + sz * 0.7)], 3)
        mv = anim((0, [0, 0], 'hold'), (t0, [0, 0], 'out'), (t0 + 20, [ddx, ddy], 'in'),
                  (t0 + 46, [ddx * 1.25, ddy + 60], 'hold'), (T, [0, 0]))
        op = anim((0, 0, 'hold'), (t0, 0, 'out'), (t0 + 4, 100, 'hold'), (t0 + 30, 100, 'in'), (t0 + 46, 0, 'hold'), (T, 0))
        rr = anim((0, 0, 'hold'), (t0, 0, 'out'), (t0 + 46, rot, 'hold'), (T, 0))
        shards.append(group(part(sh, fill=S.vgrad(S.G_ICE_SOFT, y - sz, y + sz), outline=(S.OUTLINE, 4)),
                            pivot=(x, y), move=mv, o=op, r=rr, name='shard'))
    glow = fx.glow(256, 280, 232, alpha=0.36, s=fx.breathe(T, 94, 102))
    sparks = [fx.sparkle(426, 118, 24, T, t0=86, dur=34), fx.sparkle(94, 392, 18, T, t0=98, dur=30)]
    return [glow, heart, shards, sparks]


@emoji(18, 'heart_paw', '💕', 'Сердце с лапкой', frames=120, still=0)
def e_heart_paw(T):
    beat = anim((0, 100, 'out'), (9, 112, 'in'), (18, 98, 'out'), (28, 108, 'in'), (44, 100, 'io'), (T, 100))
    h = heart_path(256, 262, 408, 368)
    pw = paw(256, 300, size=0.8)
    body = [
        part(h, fill=S.vgrad([(0, '#a6dbff'), (0.45, '#3f8af0'), (1, '#173c9a')], 78, 446), outline=S.OW),
        part(circle_path(162, 166, 46, 24).rotate(-38, 162, 166), fill=S.WHITE, o=80, name='gloss'),
        part(circle_path(114, 228, 12), fill=S.WHITE, o=70, name='gloss_dot'),
        part([b.translate(0, 9) for b in pw], fill=S.NAVY_D, o=35, name='paw_shadow'),
        part(pw, fill=S.vgrad(S.G_SNOW, 200, 392), name='paw'),
    ]
    heart = group(body, fx.shine([h], T, t0=52, dur=48, alpha=0.5), pivot=(256, 300), s=beat, name='heart')

    def mini_heart(x, y, sz):
        return part(heart_path(x, y, sz), fill=S.vgrad(S.G_ICE_SOFT, y - sz / 2, y + sz / 2), outline=S.OW_THIN, name='mini_heart')

    def mini_paw(x, y, k):
        return part(paw(x, y, size=k), fill=S.vgrad(S.G_SNOW, y - 124 * k, y + 114 * k), outline=(S.OUTLINE, 4), name='mini_paw')
    # one heart floats out of the top dip (starts hidden behind the big heart), two minis rise at the sides
    back = [group(mini_heart(256, 196, 72), pivot=(256, 196), **fx.rise(T, 6, 64, dy=-128, s0=50, s1=100))]
    front = [group(mini_paw(96, 432, 0.3), pivot=(96, 432), **fx.rise(T, 40, 60, dy=-130, dx=-24, s0=40, s1=100)),
             group(mini_heart(420, 436, 58), pivot=(420, 436), **fx.rise(T, 74, 60, dy=-130, dx=22, s0=40, s1=100))]
    glow = fx.glow(256, 270, 236, alpha=0.38, s=beat)
    sparks = fx.sparkles([(420, 104, 24), (92, 104, 20)], T, start=24, gap=44, dur=38)
    return [glow, back, heart, front, sparks]


FIRE_OUT = [(256, 478), (148, 460), (88, 378), (94, 268), (124, 170), (170, 234), (202, 160), (250, 46),
            (318, 132), (344, 210), (396, 124), (426, 256), (422, 378), (364, 460)]
FIRE_MID = [(256, 470), (184, 458), (140, 398), (148, 316), (182, 250), (206, 290), (226, 212), (262, 118),
            (302, 210), (316, 268), (346, 228), (370, 316), (372, 400), (330, 458)]
FIRE_CORE = [(256, 464), (204, 452), (182, 402), (194, 344), (228, 292), (256, 220), (286, 294), (320, 346),
             (330, 404), (308, 452)]


def _flicker(pts, sharp, T, seed, ax=22, ay=16, step=6):
    """Morphing flame: every vertex wanders on a looping mix of sines, more at the top."""
    phs = [(seed * 1.7 + j * 2.3, seed * 0.9 + j * 1.3, seed * 2.1 + j * 0.7) for j in range(len(pts))]

    def shape(t):
        u = 2 * math.pi * t / T
        out = []
        for (x, y), (p1, p2, p3) in zip(pts, phs):
            w = max(0.0, (480 - y) / 450.0) ** 1.3
            out.append((x + w * ax * (0.65 * math.sin(2 * u + p1) + 0.35 * math.sin(3 * u + p2)),
                        y + w * ay * math.sin(3 * u + p3)))
        b = _spline(out, sharp)
        # 1-decimal precision keeps the morph keyframes small
        return Bez([[round(c, 1) for c in q] for q in b.v], [[round(c, 1) for c in q] for q in b.i],
                   [[round(c, 1) for c in q] for q in b.o])
    keys = [(t, shape(t), 'linear') for t in range(0, T, step)] + [(T, shape(T))]
    return morph(keys)


@emoji(19, 'fire', '🔥', 'Ледяной огонь', frames=120, still=0)
def e_fire(T):
    base = (256, 478)
    outer = _flicker(FIRE_OUT, (4, 7, 10), T, 1)
    mid = _flicker(FIRE_MID, (4, 7, 10), T, 2, ax=18, ay=14)
    core = _flicker(FIRE_CORE, (5,), T, 3, ax=12, ay=12)
    flame = group(
        part(outer, fill=S.vgrad([(0, '#86ccff'), (0.5, '#3a80ec'), (1, '#1c44a6')], 30, 478), outline=S.OW, name='outer'),
        part(mid, fill=S.vgrad([(0, '#d2f8ff'), (0.5, '#74d8ff'), (1, '#33a2ee')], 118, 470), name='middle'),
        part(core, fill=S.vgrad([(0, '#ffffff'), (1, '#dcf7ff')], 220, 464), name='core'),
        pivot=base, s=_sq(T, [(0, 100, 100, 'sine'), (30, 101, 97, 'sine'), (60, 99, 102, 'sine'), (90, 101, 98, 'sine')]),
        r=fx.swing(T, 1.5, cycles=2), name='flame')
    embers = []
    for k, (x, y, dx, sz, col) in enumerate([(144, 250, -18, 14, S.WHITE), (372, 214, 16, 12, '#9ff0ff'),
                                             (196, 170, -10, 10, S.ICE_L), (330, 160, 14, 12, S.WHITE),
                                             (118, 330, -14, 10, '#9ff0ff'), (398, 300, 12, 10, S.ICE_L)]):
        kw = fx.rise(T, k * T / 6, 58, dy=-110, dx=dx, s0=100, s1=80)
        embers.append(group(part(circle_path(x, y, sz / 2), fill=col, name='ember'), pivot=(x, y), **kw, name='ember'))
    glow = fx.glow(256, 300, 232, color='#56c8ff', alpha=0.42, s=fx.breathe(T, 92, 104, cycles=2))
    return [glow, flame, embers]


@emoji(20, 'star', '⭐', 'Звезда', frames=120, still=0)
def e_star(T):
    cx, cy, ro, ri = 256, 272, 226, 110
    t_a, t_b = 34, 76
    light = math.radians(-125)

    def face(mirror):
        st = star(cx, cy, 5, ro, ri, round_out=30, round_in=14)
        facets = []
        for k in range(10):
            a0, a1 = math.radians(-90 + 36 * k), math.radians(-90 + 36 * (k + 1))
            r0, r1 = (ro - 34, ri) if k % 2 == 0 else (ri, ro - 34)
            tri = Bez([(cx, cy), (cx + r0 * math.cos(a0), cy + r0 * math.sin(a0)),
                       (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1))])
            b = math.cos((a0 + a1) / 2 - light)
            facets.append((tri, b))
        gloss = circle_path(cx - 62, cy - 58, 30, 16).rotate(-40, cx - 62, cy - 58)
        if mirror:
            st, gloss = st.mirror_x(cx), gloss.mirror_x(cx)
            facets = [(f.mirror_x(cx), b) for f, b in facets]
        items = [part(st, fill=S.vgrad(S.G_SILVER, cy - ro, cy + ro * 0.81), outline=S.OW, name='star')]
        items += [part(f, fill=S.WHITE, o=12 + 34 * b, name='lit') for f, b in facets if b > 0.05]
        items += [part(f, fill=S.NAVY, o=-20 * b, name='shade') for f, b in facets if b < -0.05]
        items.append(part(gloss, fill=S.WHITE, o=85, name='gloss'))
        return items, st
    front, st = face(False)
    back, _ = face(True)

    # Y-flip: x-scale follows cos of an eased turn; faces swap while edge-on
    def ease(u):
        return 0.5 - 0.5 * math.cos(math.pi * u)
    sx = [(0, 100, 'hold'), (t_a, 100, 'linear')]
    for t in range(t_a + 2, t_b, 2):
        sx.append((t, 100 * math.cos(2 * math.pi * ease((t - t_a) / (t_b - t_a))), 'linear'))
    sx += [(t_b, 100, 'hold'), (T, 100)]
    sxa = anim([(k[0], [k[1], 100]) + tuple(k[2:]) for k in sx])
    t_c1, t_c2 = t_a + (t_b - t_a) / 3, t_a + 2 * (t_b - t_a) / 3
    o_front = anim((0, 100, 'hold'), (t_c1, 0, 'hold'), (t_c2, 100, 'hold'), (T, 100))
    o_back = anim((0, 0, 'hold'), (t_c1, 100, 'hold'), (t_c2, 0, 'hold'), (T, 0))
    spin = group(group(front, fx.shine([st], T, t0=84, dur=36, alpha=0.6), o=o_front, name='front'),
                 group(back, o=o_back, name='back'), pivot=(cx, cy), s=sxa, name='spin')
    hop = anim((0, [0, 0], 'hold'), (t_a - 6, [0, 0], 'out'), (55, [0, -24], 'in'), (t_b, [0, 0], 'hold'), (T, [0, 0]))
    land = _sq(T, [(0, 100, 100, 'hold'), (t_a - 10, 100, 100, 'out'), (t_a - 4, 106, 94, 'io'), (t_a + 4, 100, 100, 'hold'),
                   (t_b - 2, 100, 100, 'out'), (t_b + 3, 107, 93, 'outback'), (t_b + 18, 100, 100, 'hold')])
    body = group(spin, pivot=(cx, cy + ro * 0.81), s=land, move=hop, name='star')
    glow = fx.glow(cx, cy, 236, alpha=0.36, s=fx.breathe(T, 92, 104))
    sparks = fx.sparkles([(438, 88, 30), (76, 412, 22), (448, 404, 18), (70, 96, 16)], T, start=78, gap=10, dur=36)
    return [glow, body, sparks]


@emoji(21, 'sparkles', '✨', 'Блёстки', frames=120, still=0)
def e_sparkles(T):
    items = []
    # radial fills keep the stars rotation-invariant, so the 90-degree twinkle turn loops cleanly
    for (x, y), R, k, t0, ow in (((210, 296), 160, 0.2, 8, S.OW), ((384, 132), 86, 0.22, 34, S.OW),
                                 ((404, 398), 56, 0.24, 56, S.OW_THIN)):
        sp = sparkle_path(x, y, R, k)
        sc = loop([(t0, 100, 'in'), (t0 + 8, 72, 'out'), (t0 + 18, 110, 'io'), (t0 + 34, 100, 'hold'), (t0 + T, 100)], T)
        rot = anim((0, 0, 'hold'), (t0, 0, 'io'), (t0 + 30, 90, 'hold'), (T, 90))
        halo = fx.glow(x, y, R * 1.15, color=S.ICE_L, alpha=0.4,
                       o=loop([(t0, 30, 'out'), (t0 + 16, 100, 'in'), (t0 + 50, 30, 'hold'), (t0 + T, 30)], T))
        star_g = group(
            part(sp, fill=S.rgrad([(0, S.WHITE), (0.3, '#e2f4ff'), (0.72, '#7cbcff'), (1, '#3a78e6')], x, y, R),
                 outline=ow, name='sparkle'),
            part(circle_path(x, y, R * 0.13), fill=S.WHITE, name='core'),
            pivot=(x, y), s=sc, r=rot, name='star')
        items += [halo, star_g]
    dots = fx.sparkles([(92, 96, 18), (300, 470, 14), (478, 262, 14)], T, start=20, gap=34, dur=34)
    return [group(items, pivot=(256, 256), move=fx.bob(T, 10)), dots]


@emoji(22, 'lightning', '⚡', 'Молния', frames=120, still=16)
def e_lightning(T):
    pts = [(292, 44), (404, 44), (330, 200), (420, 200), (182, 470), (240, 288), (124, 288)]
    bolt = rounded(pts, [12, 12, 8, 12, 6, 8, 12])
    pivot = (272, 257)
    # gloss strip just inside the upper-left edge
    (ax, ay), (bx, by) = (292, 44), (124, 288)
    L = math.hypot(bx - ax, by - ay)
    nx, ny = (by - ay) / L, -(bx - ax) / L
    def at(t, off):
        return (ax + (bx - ax) * t + nx * off, ay + (by - ay) * t + ny * off)
    gloss = rounded([at(0.12, 18), at(0.12, 32), at(0.6, 32), at(0.6, 18)], 6)
    flash = anim((0, 0, 'hold'), (12, 0, 'out'), (14, 85, 'out'), (24, 0, 'hold'), (27, 0, 'out'), (29, 55, 'out'),
                 (38, 0, 'hold'), (64, 0, 'out'), (66, 60, 'out'), (76, 0, 'hold'), (T, 0))
    pop = anim((0, 100, 'hold'), (6, 100, 'in'), (12, 95, 'out'), (16, 107, 'outback'), (34, 100, 'hold'),
               (62, 100, 'out'), (66, 104, 'io'), (80, 100, 'hold'), (T, 100))
    body = group(
        part(bolt, fill=S.vgrad([(0, S.WHITE), (0.35, '#c6ecff'), (1, '#4a98f2')], 44, 470), outline=S.OW, name='bolt'),
        part(gloss, fill=S.WHITE, o=80, name='gloss'),
        fx.shine([bolt], T, t0=86, dur=30, alpha=0.6),
        part(bolt, fill=S.WHITE, o=flash, name='flash'),
        pivot=pivot, s=pop, r=fx.swing(T, 2), name='bolt')
    sparks = []
    for k, ((x, y), ang, t0) in enumerate((((96, 150), 200, 14), ((446, 118), -20, 16), ((92, 396), 160, 18),
                                           ((440, 330), 20, 15), ((326, 468), 70, 19), ((174, 74), 240, 64),
                                           ((452, 236), 0, 66), ((118, 470), 130, 68))):
        a = math.radians(ang)
        ux, uy, px, py = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
        zz = polyline([(x - ux * 26 + px * 4, y - uy * 26 + py * 4), (x - ux * 8 - px * 10, y - uy * 8 - py * 10),
                       (x + ux * 8 + px * 10, y + uy * 8 + py * 10), (x + ux * 26 - px * 4, y + uy * 26 - py * 4)])
        tr = trim(0, anim((0, 0, 'hold'), (t0, 0, 'out'), (t0 + 4, 100, 'hold'), (T, 0)))
        op = anim((0, 0, 'hold'), (t0, 100, 'hold'), (t0 + 6, 100, 'in'), (t0 + 14, 0, 'hold'), (T, 0))
        sparks.append(_inked([zz], 8, '#e9fbff', ow=4, tr=tr, o=op, name='zap'))
    glow = fx.glow(272, 258, 236, color='#9fe0ff', alpha=0.42,
                   o=anim((0, 45, 'hold'), (12, 45, 'out'), (15, 100, 'in'), (50, 45, 'hold'), (64, 45, 'out'),
                          (67, 85, 'in'), (96, 45, 'hold'), (T, 45)))
    return [glow, body, sparks]


@emoji(23, 'hundred', '💯', 'Сотка', frames=120, still=0)
def e_hundred(T):
    cap = fit_cap('100', 400, 230, weight=900, tracking=-0.01)
    cy = 214
    gl = glyphs('100', 256, cy, cap, weight=900, tracking=-0.01)
    y0, y1 = cy - cap / 2, cy + cap / 2
    grad = S.vgrad(ICE_GRAD, y0, y1)
    digits = []
    for k, (paths, (gx, gy)) in enumerate(gl):
        t0 = 4 + k * 5
        sq = _sq(T, [(0, 100, 100, 'hold'), (t0, 100, 100, 'out'), (t0 + 6, 92, 110, 'io'), (t0 + 14, 106, 95, 'io'),
                     (t0 + 24, 100, 100, 'hold')])
        digits.append(group(part(*paths, fill=grad, outline=10, name='digit'),
                            fx.shine(paths, T, t0=50 + k * 8, dur=36, alpha=0.8, width=0.3),
                            pivot=(gx, y1), s=sq, name='digit'))
    lines = [line(78, y1 + 58, 434, y1 + 50), line(108, y1 + 112, 404, y1 + 104)]
    s_tr = anim((0, 0, 'in'), (8, 100, 'hold'), (9, 0, 'hold'), (T, 0))
    under = [_inked([ln], 30, S.ICE_L, ow=S.OW_THIN,
                    tr=trim(s_tr, anim((0, 100, 'hold'), (9, 0, 'hold'), (t0, 0, 'out2'), (t0 + 16, 100, 'hold'), (T, 100))),
                    name='underline')
             for ln, t0 in zip(lines, (10, 16))]
    pulse = anim((0, 100, 'hold'), (24, 100, 'out'), (30, 108, 'io'), (46, 100, 'hold'), (T, 100))
    body = group(under, digits, pivot=(256, 270), s=pulse, r=anim((0, -8, 'sine'), (60, -5, 'sine'), (T, -8)), name='hundred')
    sparks = fx.sparkles([(452, 106, 28), (66, 382, 20), (440, 446, 16)], T, start=56, gap=12, dur=36)
    return [fx.glow(256, 270, 236, alpha=0.32), body, sparks]


@emoji(24, 'eyes', '👀', 'Глаза', frames=180, still=0)
def e_eyes(T):
    rx, ry, ir = 98, 140, 56
    look = [(0, (0, 0)), (12, (0, 0)), (24, (-36, 6)), (52, (-36, 6)), (66, (36, 6)), (94, (36, 6)),
            (110, (0, -70)), (138, (0, -70)), (154, (0, 0))]
    gaze = anim([(t, list(v), 'io') for t, v in look] + [(T, [0, 0])])
    squash = anim([(t, [100 - abs(v[0]) / 36 * 12, 100], 'io') for t, v in look] + [(T, [100, 100])])
    follow = anim([(t, [v[0] * 0.25, v[1] * 0.12], 'io') for t, v in look] + [(T, [0, 0])])
    eyes = []
    for cx in (150, 362):
        cy = 262
        iris = group(
            part(circle_path(cx, cy, ir), fill=S.rgrad([(0, '#a8e0ff'), (0.55, '#3d86ee'), (1, '#173e9e')], cx - 12, cy - 16, ir + 14),
                 outline=S.OW_THIN, name='iris'),
            part(circle_path(cx, cy, 27), fill=S.OUTLINE, name='pupil'),
            part(circle_path(cx - 18, cy - 20, 15), fill=S.WHITE, name='glint'),
            part(circle_path(cx + 17, cy + 16, 7), fill=S.WHITE, o=90, name='glint2'),
            pivot=(cx, cy), move=gaze, s=squash, name='iris')
        eye = group(part(circle_path(cx, cy, rx, ry), fill=S.vgrad(S.G_SNOW, cy - ry, cy + ry), outline=S.OW, name='white'),
                    part(circle_path(cx - 40, cy - 74, 22, 12).rotate(-40, cx - 40, cy - 74), fill=S.WHITE, o=90, name='gloss'),
                    iris, pivot=(cx, cy), s=fx.blink(T, 98, dur=14, closed=8), name='eye')
        eyes.append(group(eye, pivot=(cx, cy), s=fx.blink(T, 160, dur=12, closed=8)))
    return [fx.glow(256, 262, 236, alpha=0.3), group(eyes, pivot=(256, 262), move=follow, name='eyes')]


@emoji(25, 'zzz', '💤', 'Сон', frames=180, still=0)
def e_zzz(T):
    (zp, _), = glyphs('Z', 0, 0, 150, weight=900)
    S0, E0 = (134, 414), (378, 112)
    dx, dy = E0[0] - S0[0], E0[1] - S0[1]
    ln = math.hypot(dx, dy)
    px, py = -dy / ln, dx / ln
    n = 18
    # one Z travels the whole path per loop (small -> big, fading at both ends); three of them are staggered
    mv, sc, rot, op = [], [], [], []
    for j in range(n + 1):
        u = j / n
        t = T * u
        sw = 24 * math.sin(2 * math.pi * u)
        mv.append((t, [S0[0] + dx * u + px * sw, S0[1] + dy * u + py * sw], 'linear'))
        sc.append((t, 36 + 66 * u, 'linear'))
        rot.append((t, -12 + 9 * math.sin(2 * math.pi * u + 1.2), 'linear'))
    op = [(0, 0, 'out'), (0.1 * T, 100, 'hold'), (0.84 * T, 100, 'in'), (T, 0)]
    zs = []
    for k in range(3):
        dt = (-(0.12 + k / 3.0) * T) % T
        zs.append(group(group(part(*zp, fill=S.vgrad(ICE_GRAD, -75, 75), outline=8, name='z'), r=phase(anim(rot), dt, T)),
                        pos=phase(anim(mv), dt, T), s=phase(anim(sc), dt, T), o=phase(anim(op), dt, T), name='Z'))
    sparks = fx.sparkles([(96, 150, 20), (430, 330, 16), (250, 470, 14)], T, start=30, gap=56, dur=40)
    return [fx.glow(256, 270, 230, alpha=0.3, s=fx.breathe(T, 92, 104)), sparks, zs]


@emoji(26, 'online', '🔵', 'В сети', frames=120, still=20)
def e_online(T):
    cx, cy, r = 256, 256, 142
    beat = anim((0, 100, 'out'), (8, 106, 'io'), (26, 100, 'io'), (60, 100, 'out'), (68, 106, 'io'), (86, 100, 'io'), (T, 100))
    dot = circle_path(cx, cy, r)
    body = group(
        part(dot, fill=S.rgrad([(0, '#effdff'), (0.28, '#86e4ff'), (0.68, '#2f7fea'), (1, '#183c98')], cx - 46, cy - 54, r * 1.5),
             outline=S.OW, name='dot'),
        part(circle_path(cx, cy, r - 22), stroke=stroke(S.WHITE, 6, o=22), name='inner_ring'),
        part(circle_path(cx - 54, cy - 62, 42, 22).rotate(-40, cx - 54, cy - 62), fill=S.WHITE, o=85, name='gloss'),
        part(circle_path(cx - 98, cy - 6, 10), fill=S.WHITE, o=70, name='gloss_dot'),
        fx.shine([dot], T, t0=30, dur=40, alpha=0.5),
        pivot=(cx, cy), s=beat, name='status')
    rings = [fx.ring_pulse(cx, cy, r + 2, 234, T, t0=t0, dur=58, color='#8fe8ff', w0=18, w1=3, alpha=95) for t0 in (2, 62)]
    glow = fx.glow(cx, cy, 228, color='#56c8ff', alpha=0.45, s=beat)
    sparks = [fx.sparkle(388, 118, 22, T, t0=34, dur=34), fx.sparkle(126, 398, 16, T, t0=94, dur=30)]
    return [glow, rings, body, sparks]


@emoji(27, 'loading', '🔄', 'Загрузка', frames=120, still=0)
def e_loading(T):
    cx, cy, R, r = 256, 256, 170, 40
    per = T / 2                       # one lap per second
    keys = []
    for c in range(2):
        b = c * per
        keys += [(b, 100, 'out'), (b + per * 0.45, 0, 'hold'), (b + per * 0.88, 0, 'in')]
    keys.append((T, 100))
    dots = []
    for k in range(8):
        a = math.radians(-90 + 45 * k)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        dt = k * per / 8
        lit = phase(anim([(t, v) + tuple(e) for t, v, *e in keys]), dt, T)
        sc = phase(anim([(t, 78 + 0.4 * v) + tuple(e) for t, v, *e in keys]), dt, T)
        dots.append(group(
            part(circle_path(x, y, r), fill=S.vgrad([(0, '#4f8ce6'), (1, '#1c47a6')], y - r, y + r), outline=S.OW_THIN, name='dot'),
            part(circle_path(x, y, r), fill=S.vgrad([(0, S.WHITE), (0.6, '#cdeeff'), (1, '#86c8ff')], y - r, y + r), o=lit, name='lit'),
            part(circle_path(x - 12, y - 13, 10, 7).rotate(-35, x - 12, y - 13), fill=S.WHITE, o=80, name='glint'),
            pivot=(x, y), s=sc, name='dot'))
    track = part(circle_path(cx, cy, R), stroke=stroke(S.BLUE_D, 22, o=35), name='track')
    return [fx.glow(cx, cy, 236, alpha=0.3), track, dots]


MITTEN_GRAD = [(0, '#7fc2ff'), (0.5, '#2f72e4'), (1, '#1a3f9c')]


def _mitten(rot, thumb, center=(256, 260), size=410, curl=1.0):
    """The KRONOS knitted mitten shared by 028-030. Canonical pose: fingers up, cuff down,
    thumb on the right, wrist at the origin. `rot` turns the whole mitten, `thumb` is the
    thumb direction in the canonical frame (degrees), `curl` < 1 shortens the finger part
    (a fist inside the mitten). The result is scaled so its larger side equals `size` and
    centred on `center`. Gradients and the gloss are computed in canvas space, so the
    light always comes from the top-left."""
    body0 = P('M -86 46 L -86 0 C -94 -40 -100 -84 -100 -132 C -100 -212 -54 -252 0 -252 '
              'C 56 -252 100 -208 100 -134 C 100 -84 94 -40 86 0 L 86 46 Z').scale(1, curl)
    tb = (70, -100 * curl)
    ta = math.radians(thumb)
    tt = (tb[0] + 96 * math.cos(ta), tb[1] + 96 * math.sin(ta))
    thumb0 = _capsule(tb, 48, tt, 42)
    cuff0 = rounded([(-108, -10), (108, -10), (108, 88), (-108, 88)], 30)
    x0, y0, x1, y1 = bbox_of([b.rotate(rot) for b in (body0, thumb0, cuff0)])
    k = size / max(x1 - x0, y1 - y0)
    ox, oy = center[0] - (x0 + x1) / 2 * k, center[1] - (y0 + y1) / 2 * k

    def M(b):
        return b.rotate(rot).scale(k).translate(ox, oy)

    def pt(x, y):
        return tuple(M(Bez([(x, y)])).v[0])
    body, th, cuff = M(body0), M(thumb0), M(cuff0)
    hy0, hy1 = bbox_of([body, th])[1::2]
    grad = S.vgrad(MITTEN_GRAD, hy0, hy1)
    fc, fr = (-2, -126 * curl), 40
    flake = []
    for j in range(6):
        a = math.radians(j * 60 - 90)
        ux, uy = math.cos(a), math.sin(a)
        flake.append(M(line(fc[0], fc[1], fc[0] + ux * fr, fc[1] + uy * fr)))
        bx, by = fc[0] + ux * fr * 0.6, fc[1] + uy * fr * 0.6
        for sg in (-1, 1):
            b2 = a + math.radians(45 * sg)
            flake.append(M(line(bx, by, bx + math.cos(b2) * fr * 0.36, by + math.sin(b2) * fr * 0.36)))
    zig = M(polyline([(-76 + 19 * j, -44 * curl + (8 if j % 2 else -8)) for j in range(9)]))
    ribs = [M(line(x, 12, x, 68)) for x in (-72, -48, -24, 0, 24, 48, 72)]
    d = Bez([(-0.6, -0.8)]).rotate(-rot).v[0]           # canvas up-left, in the canonical frame
    gc = pt(-4 + 64 * d[0], (-128 + 90 * d[1]) * curl)
    gloss = circle_path(gc[0], gc[1], 30 * k, 14 * k).rotate(-37, gc[0], gc[1])
    tm = pt((tb[0] + tt[0]) / 2 + 16 * d[0], (tb[1] + tt[1]) / 2 + 16 * d[1])
    cy0, cy1 = cuff.bbox()[1::2]
    return {
        'thumb': [part(th, fill=grad, outline=S.OW, name='thumb'),
                  part(circle_path(tm[0], tm[1], 14 * k, 8 * k).rotate(-37, tm[0], tm[1]), fill=S.WHITE, o=60, name='thumb_gloss')],
        'hand': [part(body, fill=grad, outline=S.OW, name='hand'),
                 part(zig, stroke=stroke(S.ICE_L, 8 * k, o=90), name='knit'),
                 part(flake, stroke=stroke(S.WHITE, 9 * k), name='flake'),
                 part(gloss, fill=S.WHITE, o=70, name='gloss')],
        'cuff': [part(cuff, fill=S.vgrad(S.G_SNOW, cy0, cy1), outline=S.OW, name='cuff'),
                 part(ribs, stroke=stroke('#a9cdf2', 9 * k), name='ribs')],
        'wrist': pt(0, 0), 'arm': pt(0, 88), 'thumb_base': pt(*tb), 'thumb_tip': pt(*tt),
        'top': pt(0, -252 * curl), 'k': k, 'shine': [body, th],
    }


@emoji(28, 'thumbs_up', '👍', 'Класс', frames=120, still=40)
def e_thumbs_up(T):
    m = _mitten(-66, -24, center=(250, 270), size=420)
    thumb = group(m['thumb'], pivot=m['thumb_base'],
                  r=anim((0, 0, 'hold'), (24, 0, 'out'), (31, -10, 'io'), (39, 6, 'io'), (50, 0, 'hold'), (T, 0)))
    pump_mv = anim((0, [0, 0], 'hold'), (8, [0, 0], 'io'), (18, [8, 14], 'out'), (28, [-6, -26], 'io'),
                   (52, [0, 0], 'hold'), (T, [0, 0]))
    pump_r = anim((0, 0, 'hold'), (8, 0, 'io'), (18, 5, 'out'), (28, -7, 'io'), (52, 0, 'hold'), (T, 0))
    mitt = group(thumb, m['hand'], fx.shine(m['shine'], T, t0=54, dur=40, alpha=0.5), m['cuff'],
                 pivot=m['arm'], move=pump_mv, r=pump_r, name='mitten')
    tx, ty = m['thumb_tip']
    sparks = [fx.sparkle(tx + 92, ty + 14, 30, T, t0=28, dur=36), fx.sparkle(tx - 96, ty + 30, 22, T, t0=33, dur=34),
              fx.sparkle(tx + 30, ty - 30, 16, T, t0=38, dur=30), fx.sparkle(430, 400, 20, T, t0=80, dur=34)]
    return [fx.glow(256, 266, 232, alpha=0.32), group(mitt, move=fx.bob(T, 8, shift=60)), sparks]


@emoji(29, 'thumbs_down', '👎', 'Не класс', frames=120, still=0)
def e_thumbs_down(T):
    m = _mitten(114, -24, center=(262, 244), size=420)
    droop = anim((0, [0, 0], 'hold'), (10, [0, 0], 'io'), (30, [0, 12], 'hold'), (80, [0, 12], 'io'), (104, [0, 0], 'hold'),
                 (T, [0, 0]))
    tilt = anim((0, 0, 'hold'), (10, 0, 'io'), (30, 6, 'hold'), (80, 6, 'io'), (104, 0, 'hold'), (T, 0))
    shake = fx.wobble(T, 34, 40, 12, n=3, vector=(1, 0))
    mitt = group(group(m['thumb'], m['hand'], m['cuff'], pivot=m['arm'], r=tilt, move=droop, name='mitten'),
                 move=shake, name='shake')
    tx, ty = m['thumb_tip']
    dy0 = ty + 30 * m['k']
    drop = P(f'M {tx} {dy0 - 26} C {tx + 4} {dy0 - 14} {tx + 14} {dy0 - 4} {tx + 14} {dy0 + 6} '
             f'C {tx + 14} {dy0 + 16} {tx + 7} {dy0 + 22} {tx} {dy0 + 22} '
             f'C {tx - 7} {dy0 + 22} {tx - 14} {dy0 + 16} {tx - 14} {dy0 + 6} '
             f'C {tx - 14} {dy0 - 4} {tx - 4} {dy0 - 14} {tx} {dy0 - 26} Z')
    dmv = anim((0, [0, 0], 'hold'), (40, [0, 0], 'in'), (76, [0, 70], 'hold'), (T, [0, 0]))
    dop = anim((0, 0, 'hold'), (40, 0, 'out'), (46, 100, 'hold'), (62, 100, 'in'), (76, 0, 'hold'), (T, 0))
    dsc = anim((0, 30, 'hold'), (36, 30, 'outback'), (46, 100, 'hold'), (T, 30))
    drop_g = group(group(part(drop, fill=S.vgrad(S.G_ICE_SOFT, dy0 - 26, dy0 + 22), outline=(S.OUTLINE, 4), name='drop'),
                         pivot=(tx, dy0), s=dsc), move=dmv, o=dop, name='drop')
    return [fx.glow(256, 250, 228, alpha=0.26), mitt, drop_g]


@emoji(30, 'wave', '👋', 'Привет', frames=120, still=15)
def e_wave(T):
    m = _mitten(6, -48, center=(246, 266), size=404)
    wx, wy = m['wrist']
    hand = group(m['thumb'], m['hand'], pivot=m['wrist'], r=fx.swing(T, 14, cycles=2), name='hand')
    mitt = group(hand, m['cuff'], pivot=m['arm'], r=fx.swing(T, 3, cycles=2, shift=-4), name='mitten')
    tx, ty = m['top']
    R0 = math.hypot(tx - wx, ty - wy) + 30
    arcs = []
    for side, t0s in ((1, (6, 66)), (-1, (36, 96))):
        paths = []
        for dr, a0, a1 in ((0, 14, 40), (34, 18, 36)):
            r_ = R0 + dr
            b0, b1 = math.radians(-90 + side * a0), math.radians(-90 + side * a1)
            p0 = (wx + r_ * math.cos(b0), wy + r_ * math.sin(b0))
            p1 = (wx + r_ * math.cos(b1), wy + r_ * math.sin(b1))
            paths.append(P(f'M {p0[0]} {p0[1]} A {r_} {r_} 0 0 {1 if side > 0 else 0} {p1[0]} {p1[1]}'))
        for t0 in t0s:
            tr = trim(anim((0, 0, 'hold'), (t0 + 10, 0, 'in'), (t0 + 22, 100, 'hold'), (T, 0)),
                      anim((0, 0, 'hold'), (t0, 0, 'out'), (t0 + 10, 100, 'hold'), (T, 0)))
            arcs.append(_inked(paths, 12, S.WHITE, ow=5, tr=tr, name='motion'))
    sparks = [fx.sparkle(84, 330, 20, T, t0=50, dur=32), fx.sparkle(440, 380, 16, T, t0=100, dur=30)]
    return [fx.glow(250, 262, 232, alpha=0.3), arcs, mitt, sparks]


@emoji(31, 'party', '🎉', 'Праздник', frames=120, still=34)
def e_party(T):
    A, Mo, hw = (86, 446), (224, 302), 92
    ax, ay = Mo[0] - A[0], Mo[1] - A[1]
    L = math.hypot(ax, ay)
    ux, uy = ax / L, ay / L
    nx, ny = -uy, ux
    Lp, Rp = (Mo[0] - nx * hw, Mo[1] - ny * hw), (Mo[0] + nx * hw, Mo[1] + ny * hw)

    def edge(p, t):
        return (A[0] + (p[0] - A[0]) * t, A[1] + (p[1] - A[1]) * t)
    cone = rounded([A, Lp, Rp], [16, 4, 4])
    stripes = [Bez([edge(Lp, ta), edge(Lp, tb), edge(Rp, min(1, tb + 0.1)), edge(Rp, min(1, ta + 0.1))])
               for ta, tb in ((0.22, 0.34), (0.5, 0.62), (0.78, 0.9))]
    ang = math.degrees(math.atan2(ny, nx))
    rim = circle_path(Mo[0], Mo[1], hw, hw * 0.3).rotate(ang, Mo[0], Mo[1])
    inner = circle_path(Mo[0], Mo[1], hw - 14, hw * 0.3 - 8).rotate(ang, Mo[0], Mo[1])
    gl0, gl1 = edge(Lp, 0.2), edge(Lp, 0.72)
    cone_g = group(
        part(cone, fill=S.vgrad(S.G_DEEP, Lp[1], A[1]), outline=S.OW, name='cone'),
        part(stripes, fill=S.vgrad(S.G_SNOW, Lp[1], A[1]), name='stripes'),
        part(line(gl0[0] + nx * 16, gl0[1] + ny * 16, gl1[0] + nx * 18, gl1[1] + ny * 18), stroke=stroke(S.WHITE, 9, o=60), name='gloss'),
        part(rim, fill=S.vgrad(S.G_ICE_SOFT, Mo[1] - hw, Mo[1] + hw), outline=S.OW_THIN, name='rim'),
        part(inner, fill=S.vgrad([(0, S.NAVY_D), (1, S.NAVY)], Mo[1] - hw, Mo[1] + hw), name='mouth'),
        pivot=A, s=anim((0, 100, 'hold'), (4, 100, 'io'), (11, 94, 'out'), (16, 107, 'io'), (36, 100, 'hold'), (T, 100)),
        r=anim((0, 0, 'sine'), (11, 4, 'out'), (18, -5, 'io'), (40, 1, 'sine'), (80, -1, 'sine'), (T, 0)), name='popper')
    cols = [S.ICE, S.TEAL, S.VIOLET, S.WHITE, S.LILAC, S.MINT, S.SKY]
    bits = []
    for i in range(14):
        a = math.radians(-112 + 124 * i / 13 + (7 if i % 2 else -5))
        rr = 160 + 90 * ((i * 37) % 10) / 10
        tx, ty = Mo[0] + rr * math.cos(a), Mo[1] + rr * math.sin(a)
        t0 = 13 + (i % 4)
        drift = 16 if i % 3 else -16
        col = cols[i % len(cols)]
        kind = i % 3
        if kind == 0:
            shp = rounded([(Mo[0] - 14, Mo[1] - 7), (Mo[0] + 14, Mo[1] - 7), (Mo[0] + 14, Mo[1] + 7), (Mo[0] - 14, Mo[1] + 7)], 3)
        elif kind == 1:
            shp = circle_path(Mo[0], Mo[1], 9)
        else:
            shp = sparkle_path(Mo[0], Mo[1], 15, 0.3)
        mv = anim((0, [0, 0], 'hold'), (t0, [0, 0], 'out2'), (t0 + 24, [tx - Mo[0], ty - Mo[1]], 'sine'),
                  (t0 + 70, [tx - Mo[0] + drift, ty - Mo[1] + 56], 'hold'), (T, [0, 0]))
        op = anim((0, 0, 'hold'), (t0, 100, 'hold'), (t0 + 50, 100, 'in'), (t0 + 70, 0, 'hold'), (T, 0))
        sc = anim((0, 0, 'hold'), (t0, 0, 'outback'), (t0 + 8, 100, 'hold'), (T, 0))
        spin = anim((0, 0, 'hold'), (t0, 0, 'linear'), (t0 + 70, 300 if i % 2 else -300, 'hold'), (T, 0))
        bits.append(group(part(shp, fill=col, outline=(S.OUTLINE, 3.5), name='confetti'), pivot=Mo, move=mv, o=op,
                          s=sc, r=spin, name='bit'))
    mx, my = Mo
    ribbons = [P(f'M {mx} {my} C {mx + 6} {my - 50} {mx - 44} {my - 80} {mx - 16} {my - 128} S {mx + 30} {my - 176} {mx + 2} {my - 222}'),
               P(f'M {mx} {my} C {mx + 40} {my - 40} {mx + 40} {my - 100} {mx + 96} {my - 104} S {mx + 150} {my - 150} {mx + 196} {my - 168}'),
               P(f'M {mx} {my} C {mx + 50} {my - 6} {mx + 70} {my + 40} {mx + 120} {my + 22} S {mx + 176} {my - 30} {mx + 226} {my - 12}')]
    rib = []
    for j, (path, col) in enumerate(zip(ribbons, (S.VIOLET, S.TEAL, S.SKY))):
        t0 = 13 + j * 2
        tr = trim(anim((0, 0, 'hold'), (t0 + 44, 0, 'in'), (t0 + 70, 100, 'hold'), (T, 0)),
                  anim((0, 0, 'hold'), (t0, 0, 'out'), (t0 + 22, 100, 'hold'), (T, 0)))
        rib.append(_inked([path], 11, col, ow=4, tr=tr, name='ribbon'))
    flash = fx.sparkle(mx + 10, my - 10, 64, T, t0=11, dur=22, turn=0)
    return [fx.glow(250, 260, 232, alpha=0.3), rib, bits, cone_g, flash]


@emoji(32, 'diamond', '💎', 'Бриллиант', frames=120, still=0)
def e_diamond(T):
    T0, T1, T2, T3 = (150, 116), (220, 116), (292, 116), (362, 116)
    G0, G1, G2, G3 = (50, 214), (186, 214), (326, 214), (462, 214)
    B = (256, 466)
    sil = Bez([T0, T3, G3, B, G0])
    facets = [([G0, T0, G1], '#d4efff'), ([T0, T1, G1], '#ffffff'), ([T1, T2, G2, G1], '#b4e0ff'),
              ([T2, T3, G2], '#e8f7ff'), ([T3, G3, G2], '#86c6ff'),
              ([G0, G1, B], '#78baff'), ([G1, G2, B], '#3f86ee'), ([G2, G3, B], '#2456c0')]
    items = [part(sil, fill='#5aa0f5', outline=S.OW, name='gem')]
    glints = []
    for pts, col in facets:
        f = Bez(pts)
        items.append(part(f, fill=col, name='facet'))
        xc = sum(p[0] for p in pts) / len(pts)
        t0 = 30 + (xc - 50) / 412 * 34
        glints.append(part(f, fill=S.WHITE, o=fx.pulse(T, t0, 18, 0, 60, up='out', down='in', peak=0.35), name='glint'))
    edges = [line(*G0, *G3), line(*T0, *G1), line(*T1, *G1), line(*T2, *G2), line(*T3, *G2), line(*G1, *B), line(*G2, *B)]
    items += glints
    items.append(part(edges, stroke=stroke(S.WHITE, 4, o=55), name='edges'))
    items.append(part(P('M 96 206 L 150 130 L 162 130 L 112 206 Z'), fill=S.WHITE, o=55, name='gloss'))
    gem = group(items, fx.shine([sil], T, t0=70, dur=36, alpha=0.6, width=0.26), pivot=(256, 290),
                r=fx.swing(T, 3), move=fx.bob(T, 10), s=fx.breathe(T, 98, 102, cycles=2), name='diamond')
    sparks = [fx.sparkle(372, 112, 46, T, t0=58, dur=46, turn=180), fx.sparkle(58, 204, 28, T, t0=96, dur=36),
              fx.sparkle(420, 420, 20, T, t0=18, dur=34), fx.sparkle(110, 64, 16, T, t0=36, dur=30)]
    return [fx.glow(256, 280, 232, alpha=0.4, s=fx.breathe(T, 92, 104)), gem, sparks]
