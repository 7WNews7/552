"""011-032: reactions and symbols."""
import math

from kit.registry import emoji
from kit.lottie import part, group, anim, loop, phase, stroke, trim, ellipse
from kit.geometry import P, Bez, circle_path, heart_path, polyline, line, rounded, star, sparkle_path, morph
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
