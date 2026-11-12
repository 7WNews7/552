"""061-080: winter."""
import math
import random

from kit.registry import emoji
from kit.lottie import part, group, anim, stroke
from kit.geometry import line, circle_path, rounded
from kit import fx, style as S
from kit.lottie import loop, phase, fill, trim, ellipse
from kit.geometry import P, Bez, polyline, star, sparkle_path, morph


def _flake_arms(cx, cy, r_in, r_out, branches):
    """Six arms with V-branches. branches: [(radius, length, angle_deg)]."""
    main, side = [], []
    for k in range(6):
        a = math.radians(k * 60 - 90)
        u = (math.cos(a), math.sin(a))
        main.append(line(cx + u[0] * r_in, cy + u[1] * r_in, cx + u[0] * r_out, cy + u[1] * r_out))
        for rb, ln, ang in branches:
            bx, by = cx + u[0] * rb, cy + u[1] * rb
            for sgn in (-1, 1):
                b = a + math.radians(ang * sgn)
                side.append(line(bx, by, bx + math.cos(b) * ln, by + math.sin(b) * ln))
    return main, side


@emoji(61, 'snowflake', '❄️', 'Снежинка', frames=180, still=0)
def e_snowflake(T):
    cx, cy = 256, 256
    main, side = _flake_arms(cx, cy, 40, 190, [(92, 58, 52), (146, 40, 52)])
    tips = [(cx + 196 * math.cos(math.radians(k * 60 - 90)), cy + 196 * math.sin(math.radians(k * 60 - 90))) for k in range(6)]
    hexa = rounded([(cx + 50 * math.cos(math.radians(k * 60)), cy + 50 * math.sin(math.radians(k * 60))) for k in range(6)], 8)
    # fills inside the rotating group must be rotation-invariant (solid / radial around the
    # centre), otherwise the 60-degree turn per loop shows up as a jump at the seam
    flake = [
        part(*main, *side, stroke=stroke(S.OUTLINE, 30 + 2 * S.OW), name='outline'),
        part(*[circle_path(x, y, 15) for x, y in tips], fill=S.OUTLINE, outline=S.OW, name='tip_outline'),
        part(*main, stroke=stroke(S.ICE, 30), name='arms'),
        part(*side, stroke=stroke(S.ICE, 24), name='branches'),
        part(*[circle_path(x, y, 15) for x, y in tips], fill=S.ICE_L, name='tips'),
        part(*main, stroke=stroke(S.WHITE, 10), name='core'),
        part(hexa, fill=S.rgrad([(0, S.WHITE), (0.6, S.ICE_L), (1, S.SKY)], cx, cy, 52), outline=S.OW, name='hub'),
    ]
    gem = [
        part(circle_path(cx, cy, 18), fill=S.vgrad(S.G_DEEP, cy - 18, cy + 18), name='hub_gem'),
        part(circle_path(cx - 6, cy - 7, 6), fill=S.WHITE, o=90, name='hub_glint'),
    ]
    # sparkles live outside the rotating group (a 60-degree turn per loop would otherwise
    # move a visible sparkle to another tip at the seam); each one is placed where its tip
    # will be at the moment it twinkles
    sparks = []
    for k in range(6):
        t0 = 10 + k * T / 6
        a = math.radians(k * 60 - 90 + 60 * (t0 + 16) / T)
        sparks.append(fx.sparkle(cx + 196 * math.cos(a), cy + 196 * math.sin(a), 26, T, t0=t0, dur=40))
    body = group(group(flake, pivot=(cx, cy), r=fx.spin(T, 1 / 6)), gem, sparks,
                 pivot=(cx, cy), s=fx.breathe(T, 95, 104, cycles=2))
    return [fx.glow(cx, cy, 236, alpha=0.4, s=fx.breathe(T, 88, 102, cycles=2)), body]


# ============================================================= shared helpers (062-080)
COAL = '#1d2747'
G_KNIT = [(0.0, '#4a74d6'), (1.0, '#1b357f')]          # navy knitted wool (avatar scarf)
G_FIR = [(0.0, '#7fe3d4'), (0.5, '#249c9f'), (1.0, '#105a7a')]
G_FIR_NIGHT = [(0.0, '#4aa6bf'), (0.5, '#1f6b8f'), (1.0, '#123d6e')]
G_CARROT = [(0.0, '#ffb35a'), (1.0, '#e8742a')]


def _pol(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def _cubic(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u * u * u * a + 3 * u * u * t * b + 3 * u * t * t * c + t * t * t * d
                 for a, b, c, d in zip(p0, p1, p2, p3))


def _cubic_head(p0, p1, p2, p3, t):
    """Control points of the 0..t piece of a cubic (de Casteljau)."""
    L = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    a, b, c = L(p0, p1), L(p1, p2), L(p2, p3)
    d, e = L(a, b), L(b, c)
    return p0, a, d, L(d, e)


def _snow_fill(x, y, r):
    """Round snow body lit from the top-left (radial, no extra shading shapes needed)."""
    return S.rgrad([(0, '#ffffff'), (0.45, '#f1f8ff'), (0.75, '#d3e8fb'), (1, '#9fc8f0')],
                   x - r * 0.32, y - r * 0.38, r * 1.5)


def _mini_flake(x, y, r, w=7, color=S.ICE_L, ow=4):
    arms = [line(*_pol(x, y, r, a), *_pol(x, y, r, a + 180)) for a in (90, 30, -30)]
    return [part(*arms, stroke=stroke(S.OUTLINE, w + 2 * ow), name='flake_ow'),
            part(*arms, stroke=stroke(color, w), name='flake')]


def _flakes(T, specs, fade=0.2):
    """Falling outlined mini flakes. specs: [(x, y0, y1, r, phase 0..1, sway px)].
    They grow in / shrink out: group opacity would show the navy outline through the fill."""
    out = []
    for x, y0, y1, r, ph, sway in specs:
        dt = ph * T
        fall = phase(anim((0, [0, 0], 'linear'), (T, [0, y1 - y0])), dt, T)
        sc = phase(anim((0, 0, 'out'), (T * fade, 100, 'linear'), (T * (1 - fade), 100, 'in'), (T, 0)), dt, T)
        rot = phase(anim((0, 0, 'linear'), (T, 120)), dt, T)
        inner = group(_mini_flake(x, y0, r), pivot=(x, y0), r=rot, s=sc,
                      move=fx.wave(T, [-sway, 0], [sway, 0], 1, shift=dt * 0.7), name='flake_sway')
        out.append(group(inner, pivot=(x, y0), move=fall, name='flake_fall'))
    return out


def _blob(cx, cy, r, n=10, amp=0.04, seed=1):
    """Lumpy closed round shape (snowballs, clouds of snow)."""
    rnd = random.Random(seed)
    b = Bez()
    k = 4 / 3 * math.tan(math.pi / (2 * n))
    for j in range(n):
        a = 2 * math.pi * j / n
        rr = r * (1 + rnd.uniform(-amp, amp))
        p = (cx + rr * math.cos(a), cy + rr * math.sin(a))
        t = (-math.sin(a) * rr * k, math.cos(a) * rr * k)
        b.add(p, (-t[0], -t[1]), t)
    return b


def _arcs(segs):
    """Closed path from circle arcs [(cx, cy, r, deg0, deg1)], each starting where the last ended."""
    b = Bez()
    for s, (cx, cy, r, a0, a1) in enumerate(segs):
        n = max(1, int(math.ceil(abs(a1 - a0) / 90 - 1e-9)))
        da = (a1 - a0) / n
        k = 4 / 3 * math.tan(math.radians(da) / 4) * r
        for j in range(n + 1):
            a = math.radians(a0 + da * j)
            p = (cx + r * math.cos(a), cy + r * math.sin(a))
            t = (-math.sin(a) * k, math.cos(a) * k)
            if j == 0:
                if s == 0:
                    b.add(p, (0, 0), t)
                else:
                    b.o[-1] = list(t)
            else:
                b.add(p, (-t[0], -t[1]), t if j < n else (0, 0))
    if math.hypot(b.v[-1][0] - b.v[0][0], b.v[-1][1] - b.v[0][1]) < 1e-3:
        b.i[0] = b.i[-1]
        b.v.pop()
        b.i.pop()
        b.o.pop()
    return b


def _circle_cross(c1, r1, c2, r2):
    """Intersection points of two circles (angles are easier to take from these)."""
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dy)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, r1 * r1 - a * a))
    mx, my = c1[0] + a * dx / d, c1[1] + a * dy / d
    return (mx + h * dy / d, my - h * dx / d), (mx - h * dy / d, my + h * dx / d)


def _ang(c, p):
    return math.degrees(math.atan2(p[1] - c[1], p[0] - c[0]))


def _tier_edge(cx, ya, yb, hw, side=1):
    """Cubic (apex -> branch tip) of one side of a fir tier; side=1 right, -1 left."""
    h = yb - ya
    return ((cx, ya), (cx + side * hw * 0.2, ya + h * 0.42), (cx + side * hw * 0.62, yb - h * 0.1),
            (cx + side * hw, yb))


def _tier(cx, ya, yb, hw, n=3, droop=16, notch=10):
    """Fir tier: concave sides and a scalloped lower edge."""
    r = _tier_edge(cx, ya, yb, hw, 1)
    lft = _tier_edge(cx, ya, yb, hw, -1)
    d = 'M %.2f %.2f C %.2f %.2f %.2f %.2f %.2f %.2f ' % (*r[0], *r[1], *r[2], *r[3])
    xs = [cx + hw - 2 * hw * j / n for j in range(n + 1)]
    for j in range(n):
        x0, x1 = xs[j], xs[j + 1]
        y0 = yb if j == 0 else yb - notch
        y1 = yb if j == n - 1 else yb - notch
        w = x0 - x1
        d += 'C %.2f %.2f %.2f %.2f %.2f %.2f ' % (x0 - w * 0.08, y0 + droop * 1.3, x1 + w * 0.08, y1 + droop * 1.3, x1, y1)
    d += 'C %.2f %.2f %.2f %.2f %.2f %.2f Z' % (*lft[2], *lft[1], *lft[0])
    return P(d)


def _tier_snow(cx, ya, yb, hw, t, depths, dy=0.0):
    """Snow lying on the upper part of a tier (follows its sides down to edge parameter t)."""
    r = [(x, y + dy) for x, y in _cubic_head(*_tier_edge(cx, ya, yb, hw, 1), t)]
    lft = [(x, y + dy) for x, y in _cubic_head(*_tier_edge(cx, ya, yb, hw, -1), t)]
    d = 'M %.2f %.2f C %.2f %.2f %.2f %.2f %.2f %.2f ' % (*r[0], *r[1], *r[2], *r[3])
    x0, y = r[3]
    x1 = lft[3][0]
    n = len(depths)
    for j, dep in enumerate(depths):
        xa = x0 + (x1 - x0) * j / n
        xb = x0 + (x1 - x0) * (j + 1) / n
        d += 'Q %.2f %.2f %.2f %.2f ' % ((xa + xb) / 2, y + dep * 2, xb, y)
    d += 'C %.2f %.2f %.2f %.2f %.2f %.2f Z' % (*lft[2], *lft[1], *lft[0])
    return P(d)


def _fir(cx, tiers, fill_stops, snow_t=0.42, ow=S.OW, snow=True, droop=16, notch=10):
    """Tiered fir, tiers back -> front: [(ya, yb, hw, scallops, snow depths)]. Returns parts."""
    out = []
    for ya, yb, hw, n, depths in tiers:
        out.append(part(_tier(cx, ya, yb, hw, n, droop, notch), fill=S.vgrad(fill_stops, ya, yb + 16), outline=ow,
                        name='tier'))
        if snow:
            out.append(part(_tier_snow(cx, ya, yb, hw, snow_t, depths, dy=7), fill=S.ICE, name='snow_under'))
            out.append(part(_tier_snow(cx, ya, yb, hw, snow_t, depths),
                            fill=S.vgrad(S.G_SNOW, ya, ya + (yb - ya) * snow_t + 20), name='snow'))
    return out


# ============================================================= 062 ice crystal
@emoji(62, 'snowflake_crystal', '💠', 'Кристалл льда', frames=180, still=0)
def e_crystal(T):
    cx, cy = 256, 256
    RT, RI = 210, 100
    il = (-RI * 0.5, RI * math.sqrt(3) / 2)
    tip = (0.0, RT)
    dx, dy = tip[0] - il[0], tip[1] - il[1]
    ln = math.hypot(dx, dy)
    du = (dx / ln, dy / ln)
    nout = (-du[1], du[0])
    b1 = (il[0] + dx * 0.34, il[1] + dy * 0.34)
    b2 = (il[0] + dx * 0.53, il[1] + dy * 0.53)
    bt = (b1[0] + nout[0] * 42 + du[0] * 28, b1[1] + nout[1] * 42 + du[1] * 28)
    left = [(0.0, 0.0), il, b1, bt, b2, tip]
    right = [(-x, y) for x, y in reversed(left)]
    rim = [il, b1, bt, b2, tip] + [(-x, y) for x, y in (b2, bt, b1)]

    def arm(deg):
        a = math.radians(deg)
        u, p = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
        return lambda pts: [(cx + u[0] * y + p[0] * x, cy + u[1] * y + p[1] * x) for x, y in pts]

    angles = [-90 + 60 * k for k in range(6)]
    outline_pts = []
    for d in angles:
        outline_pts += arm(d)(rim)
    shape = Bez(outline_pts)
    lights = [Bez(arm(d)(left)) for d in angles]
    darks = [Bez(arm(d)(right)) for d in angles]
    # fills inside the rotating group are solid or radial around the centre (rotation-invariant)
    g_light = S.rgrad([(0, '#ffffff'), (0.42, '#e3f4ff'), (1, '#93cdff')], cx, cy, RT)
    g_dark = S.rgrad([(0, '#c9e8ff'), (0.45, '#77b7ff'), (1, '#2f6fe0')], cx, cy, RT)
    # the arm that passes the top-left light during the loop catches it (arm 5: -150 -> -90 deg)
    catch = fx.pulse(T, T / 2 - 40, 80, 0, 100, up='sine', down='sine', peak=0.5)
    hexa = Bez([_pol(cx, cy, 100, d) for d in angles])
    hub = rounded([_pol(cx, cy, 54, d) for d in angles], 6)
    ridges = [line(*_pol(cx, cy, 46, d), *_pol(cx, cy, RT - 18, d)) for d in angles]
    crystal = group(
        part(shape, fill=S.BLUE_L, outline=S.OW, name='silhouette'),
        part(*lights, fill=g_light, name='facets_light'),
        part(*darks, fill=g_dark, name='facets_dark'),
        part(lights[5], fill=S.WHITE, o=catch, name='catch_light'),
        part(darks[5], fill=S.ICE_L, o=catch, name='catch_dark'),
        part(hexa, stroke=stroke(S.WHITE, 5, o=55), name='etch'),
        part(*ridges, stroke=stroke(S.WHITE, 6, o=85), name='ridges'),
        fx.shine([shape], T, t0=96, dur=56, angle=30, width=0.26, alpha=0.75),
        part(hub, fill=S.rgrad([(0, S.WHITE), (0.6, S.ICE_L), (1, S.SKY)], cx, cy, 56), outline=S.OW_THIN, name='hub'),
        pivot=(cx, cy), r=fx.spin(T, 1 / 6), name='crystal')
    gem = [part(circle_path(cx, cy, 22), fill=S.vgrad(S.G_DEEP, cy - 22, cy + 22), outline=(S.OUTLINE, 4), name='gem'),
           part(circle_path(cx - 7, cy - 8, 6.5), fill=S.WHITE, o=90, name='gem_glint')]
    # glints sit where a tip will be when they peak (outside the rotating group)
    sparks = []
    for k, t0 in enumerate((20, 80, 140)):
        tp = t0 + 16
        sparks.append(fx.sparkle(*_pol(cx, cy, RT + 4, angles[(2 * k + 1) % 6] + 60 * tp / T), 26, T, t0=t0, dur=40))
    body = group(crystal, gem, sparks, pivot=(cx, cy), move=fx.bob(T, 12), s=fx.breathe(T, 98, 102, cycles=2))
    return [fx.glow(cx, cy, 236, alpha=0.36, s=fx.breathe(T, 90, 102, cycles=2)), body]


# ============================================================= 063 snowman
@emoji(63, 'snowman', '⛄', 'Снеговик', frames=180, still=0)
def e_snowman(T):
    hx, hy, hr = 256, 212, 88
    bx, by, br = 256, 372, 108
    stick = '#6f5446'

    def arm(pts, twigs):
        lines = [polyline(pts)] + [line(*a, *b) for a, b in twigs]
        return [part(*lines, stroke=stroke(S.OUTLINE, 26), name='arm_ow'),
                part(*lines, stroke=stroke(stick, 13), name='arm')]

    arm_l = arm([(170, 336), (118, 300), (66, 270)], [((112, 296), (102, 264)), ((66, 270), (40, 264)), ((66, 270), (58, 244))])
    wave = anim((0, 0, 'io'), (16, -22, 'sine'), (28, -6, 'sine'), (40, -24, 'sine'), (52, -6, 'sine'),
                (64, -24, 'sine'), (82, 0, 'io'), (T, 0))
    arm_r = group(arm([(342, 336), (394, 298), (444, 264)], [((400, 294), (410, 262)), ((444, 264), (470, 260)), ((444, 264), (452, 238))]),
                  pivot=(342, 336), r=wave, name='arm_wave')
    body = [part(circle_path(bx, by, br), fill=_snow_fill(bx, by, br), outline=S.OW, name='body'),
            part(*[circle_path(256, y, 9) for y in (368, 408, 446)], fill=COAL, name='buttons'),
            part(*[circle_path(253, y - 3, 3) for y in (368, 408, 446)], fill=S.WHITE, o=70, name='button_glint')]
    # scarf: band around the neck + a tail hanging over the body
    band = P('M 168 284 C 210 304 302 304 344 284 C 356 292 356 318 344 326 C 302 346 210 346 168 326 '
             'C 156 318 156 292 168 284 Z')
    ribs = [line(x, 284 + 15 * (1 - ((x - 256) / 88) ** 2) + 4, x, 326 + 15 * (1 - ((x - 256) / 88) ** 2) - 4)
            for x in range(182, 340, 16)]
    tail_shape = P('M 294 312 L 338 306 C 344 340 352 374 360 408 L 316 418 C 310 384 302 346 294 312 Z')
    fringe = [line(316 + 44 * f, 418 - 10 * f, 316 + 44 * f + 4, 438 - 10 * f) for f in (0.12, 0.38, 0.62, 0.88)]
    tail = group(
        part(*fringe, stroke=stroke(S.OUTLINE, 20), name='fringe_ow'),
        part(*fringe, stroke=stroke('#2c4fa8', 8), name='fringe'),
        part(tail_shape, fill=S.vgrad(G_KNIT, 306, 418), outline=S.OW_THIN + 1, name='tail'),
        part(line(300, 336, 342, 330), line(304, 356, 346, 350), stroke=stroke('#6d93ea', 4, o=70), name='tail_ribs'),
        part(line(308, 380, 352, 372), line(311, 398, 355, 390), stroke=stroke(S.ICE_L, 9), name='tail_stripes'),
        pivot=(316, 312), r=fx.swing(T, 3, cycles=2), name='scarf_tail')
    scarf = [part(band, fill=S.vgrad(G_KNIT, 284, 342), outline=S.OW, name='band'),
             part(*ribs, stroke=stroke('#6d93ea', 4, o=60), name='band_ribs'),
             part(P('M 182 292 C 214 306 250 308 286 306'), stroke=stroke(S.WHITE, 5, o=35), name='band_gloss')]
    # head: face + beanie
    eye = lambda x: group(part(circle_path(x, 214, 11, 14), fill=COAL, name='eye'),
                          part(circle_path(x - 4, 208, 4), fill=S.WHITE, o=95, name='eye_glint'),
                          pivot=(x, 214), s=fx.blink(T, 132), name='eye')
    mouth = [circle_path(x, 264 + 7 * (1 - ((x - 256) / 30) ** 2), 5) for x in (226, 241, 256, 271, 286)]
    nose = P('M 252 228 C 272 230 302 240 324 252 C 304 258 274 256 254 248 C 248 242 248 234 252 228 Z')
    dome = P('M 180 172 C 178 116 214 80 256 80 C 298 80 334 116 332 172 Z')
    pom = group(part(circle_path(256, 72, 27), fill=_snow_fill(256, 72, 27), outline=S.OW, name='pompom'),
                pivot=(256, 96), r=fx.wobble(T, 76, 44, 12, n=3), name='pompom')
    head = group(
        part(circle_path(hx, hy, hr), fill=_snow_fill(hx, hy, hr), outline=S.OW, name='head'),
        part(circle_path(204, 244, 14, 8), circle_path(308, 246, 14, 8), fill=S.PINK, o=45, name='cheeks'),
        eye(226), eye(288),
        part(*mouth, fill=COAL, name='mouth'),
        part(nose, fill=S.vgrad(G_CARROT, 228, 256), outline=(S.OUTLINE, 4), name='carrot'),
        part(line(272, 236, 270, 248), line(292, 242, 290, 252), stroke=stroke('#c45a1c', 3, o=70), name='carrot_lines'),
        pom,
        part(dome, fill=S.vgrad(G_KNIT, 80, 172), outline=S.OW, name='beanie'),
        part(*[P('M %d 166 C %d 140 %d 110 %d 92' % (x, x, 256 + (x - 256) * 0.55, 256 + (x - 256) * 0.3))
               for x in (206, 231, 256, 281, 306)], stroke=stroke('#6d93ea', 5, o=55), name='beanie_ribs'),
        part(P('M 200 140 C 202 116 220 98 240 92'), stroke=stroke(S.WHITE, 6, o=45), name='beanie_gloss'),
        part(rounded([(168, 148), (344, 148), (344, 190), (168, 190)], 18), fill=S.vgrad(S.G_SNOW, 148, 190),
             outline=S.OW, name='cuff'),
        part(*[line(x, 156, x, 182) for x in range(186, 334, 16)], stroke=stroke('#a9cdf2', 5), name='cuff_ribs'),
        pivot=(256, 300), r=anim((0, 0, 'io'), (20, 4, 'io'), (64, 4, 'io'), (86, 0, 'io'), (T, 0)), name='head')
    flakes = _flakes(T, [(74, 60, 200, 13, 0.0, 10), (132, 40, 160, 10, 0.45, 8), (414, 50, 170, 11, 0.25, 9),
                         (462, 110, 240, 13, 0.7, 10)])
    snowman = group(arm_l, arm_r, body, tail, head, scarf, pivot=(256, 482),
                    s=fx.wave(T, [100, 100], [101.5, 98.8], cycles=2), name='snowman')
    sparks = fx.sparkles([(312, 52, 22), (46, 226, 20), (420, 430, 22)], T, start=30, gap=50, dur=40)
    return [fx.glow(256, 286, 228, alpha=0.3), flakes, snowman, sparks]


# ============================================================= 064 christmas tree
@emoji(64, 'xmas_tree', '🎄', 'Ёлка', frames=120, still=10)
def e_xmas_tree(T):
    cx = 256
    tiers = [(228, 412, 188, 4, [10, 18, 9, 16, 10]), (152, 316, 142, 3, [9, 16, 8, 14]),
             (100, 214, 94, 3, [8, 14, 9])]
    edge = lambda k, side, t: _cubic(*_tier_edge(cx, tiers[k][0], tiers[k][1], tiers[k][2], side), t)
    # garland zig-zags down the tree: (tier, start side, t start, t end, bulbs)
    runs = [(2, -1, 0.62, 0.82, 3), (1, 1, 0.55, 0.86, 4), (0, -1, 0.5, 0.88, 5)]
    colors = [S.ICE_L, S.TEAL, S.VIOLET, S.PINK, S.SKY]
    garlands, bulbs = [], []
    for k, side, ta, tb, n in runs:
        p0 = edge(k, side, ta)
        p3 = edge(k, -side, tb)
        sag = 26
        p1 = (p0[0] + (p3[0] - p0[0]) / 3, p0[1] + (p3[1] - p0[1]) / 3 + sag)
        p2 = (p0[0] + 2 * (p3[0] - p0[0]) / 3, p0[1] + 2 * (p3[1] - p0[1]) / 3 + sag)
        garlands.append(Bez([p0, p3], i=[(0, 0), (p2[0] - p3[0], p2[1] - p3[1])],
                            o=[(p1[0] - p0[0], p1[1] - p0[1]), (0, 0)], closed=False))
        for j in range(n):
            bulbs.append(_cubic(p0, p1, p2, p3, (j + 0.5) / n))
    nb = len(bulbs)
    lights = []
    for j, (x, y) in enumerate(bulbs):
        c = colors[j % len(colors)]
        t0 = j * T / nb
        lit = fx.pulse(T, t0, 34, 0, 100, up='out', down='in', peak=0.3)
        lights.append(group(
            fx.glow(x, y, 30, color=c, alpha=0.75, o=lit),
            part(circle_path(x, y, 12), fill=c, outline=(S.OUTLINE, 3.5), name='bulb'),
            part(circle_path(x, y, 12), fill=S.WHITE, o=lit, name='bulb_lit'),
            part(circle_path(x - 4, y - 4, 4), fill=S.WHITE, o=85, name='bulb_glint'),
            name='light'))
    tree = [part(rounded([(228, 396), (284, 396), (284, 460), (228, 460)], 10),
                 fill=S.vgrad([(0, '#3a4f8a'), (1, '#1d2b55')], 396, 460), outline=S.OW, name='trunk'),
            part(P('M 146 474 C 156 446 206 436 256 436 C 306 436 356 446 366 474 C 330 488 182 488 146 474 Z'),
                 fill=S.vgrad(S.G_SNOW, 436, 486), outline=S.OW, name='mound'),
            _fir(cx, tiers, G_FIR, snow_t=0.36),
            part(*garlands, stroke=stroke(S.SNOW, 5, o=80), name='garland'),
            lights]
    st = star(256, 92, 5, 54, 25, round_out=7, round_in=5)
    star_g = group(
        fx.glow(256, 94, 88, color=S.ICE_L, alpha=0.5, s=fx.breathe(T, 85, 110, cycles=2)),
        part(st, fill=S.vgrad(S.G_SILVER, 40, 140), outline=S.OW, name='star'),
        part(circle_path(240, 84, 10, 6).rotate(-35, 240, 84), fill=S.WHITE, o=85, name='star_gloss'),
        fx.sparkle(290, 56, 22, T, t0=40, dur=40),
        pivot=(256, 96), r=fx.swing(T, 5), s=fx.breathe(T, 97, 105, cycles=2), name='star')
    sparks = fx.sparkles([(84, 300, 22), (436, 220, 20), (420, 404, 18)], T, start=10, gap=40, dur=38)
    return [fx.glow(256, 280, 236, alpha=0.3), group(tree, pivot=(256, 470), s=fx.breathe(T, 99, 101)),
            star_g, sparks]


# ============================================================= 065 snowy fir
@emoji(65, 'fir_tree', '🌲', 'Заснеженная ель', frames=180, still=0)
def e_fir_tree(T):
    cx = 256
    tiers = [(250, 404, 196, 5, [12, 22, 10, 20, 12]), (180, 318, 156, 4, [10, 20, 9, 18]),
             (118, 238, 114, 4, [10, 18, 9, 16]), (62, 168, 74, 3, [9, 16, 10])]
    tip = (390, 306)          # snow clump resting on the right branch tip of tier 2
    base = (tip[0], tip[1] + 12)
    t_drop, t_land = 90, 116  # the sway passes 0 deg at T/2, so the hand-over is invisible
    clump = lambda x, y: P('M %f %f C %f %f %f %f %f %f C %f %f %f %f %f %f C %f %f %f %f %f %f Z' % (
        x - 30, y + 8, x - 32, y - 10, x - 14, y - 22, x + 2, y - 18, x + 18, y - 24, x + 34, y - 10, x + 30, y + 8,
        x + 16, y + 14, x - 16, y + 14, x - 30, y + 8))
    snow_g = S.vgrad(S.G_SNOW, tip[1] - 24, tip[1] + 14)
    attached = part(clump(*tip), fill=snow_g, outline=S.OW_THIN, name='clump', pivot=base,
                    s=anim((0, 100, 'hold'), (t_drop, 0, 'hold'), (128, 0, 'outback'), (156, 100, 'hold'), (T, 100)))
    tree = group(
        part(rounded([(234, 390), (278, 390), (278, 452), (234, 452)], 8),
             fill=S.vgrad([(0, '#3a4f8a'), (1, '#1d2b55')], 390, 452), outline=S.OW, name='trunk'),
        _fir(cx, tiers, G_FIR_NIGHT, snow_t=0.5, droop=14, notch=14),
        attached,
        pivot=(256, 448), r=fx.wobble(T, t_drop, 50, 2.2, n=3), name='tree_spring')
    tree = group(tree, pivot=(256, 448), r=fx.swing(T, 2), name='tree_sway')
    land = (base[0] + 14, 446)
    fall_mv = anim((0, [0, 0], 'hold'), (t_drop, [0, 0], 'in'), (t_land, [land[0] - base[0], land[1] - base[1]], 'hold'),
                   (T, [0, 0]))
    spin = anim((0, 0, 'hold'), (t_drop, 0, 'in'), (t_land, 30, 'out'), (t_land + 6, 0, 'hold'), (T, 0))
    # squash on the outer (unrotated) group so the splat stays flat on the mound
    splat = anim((0, [100, 100], 'hold'), (t_land, [100, 100], 'out'), (t_land + 8, [165, 42], 'in'),
                 (t_land + 22, [0, 0], 'hold'), (T, [100, 100]))
    falling = group(
        group(part(clump(*tip), fill=snow_g, outline=S.OW_THIN, name='clump_fall'), pivot=base, r=spin),
        pivot=base, move=fall_mv, s=splat,
        o=anim((0, 0, 'hold'), (t_drop, 100, 'hold'), (t_land + 22, 0, 'hold'), (T, 0)), name='falling')
    bits = fx.burst(land[0], land[1] - 6, T, t_land, 6, 6, 46, size=12, color=S.SNOW, dur=26, rot=-90, seed=5)
    bits = [group(b, pivot=land, s=[100, 60]) for b in bits]
    mound = part(P('M 60 482 C 76 440 170 422 256 422 C 342 422 436 440 452 482 C 380 496 132 496 60 482 Z'),
                 fill=S.vgrad(S.G_SNOW, 422, 494), outline=S.OW, name='mound')
    flakes = _flakes(T, [(70, 70, 330, 11, 0.1, 10), (446, 60, 300, 12, 0.55, 10), (110, 40, 200, 9, 0.8, 8),
                         (412, 90, 220, 9, 0.3, 8)])
    sparks = fx.sparkles([(190, 252, 18), (330, 182, 16), (150, 448, 20)], T, start=20, gap=56, dur=40)
    return [fx.glow(256, 270, 232, alpha=0.28), flakes, tree, mound, falling, bits, sparks]


# ============================================================= 066 snowball
@emoji(66, 'snowball', '⚪', 'Снежок', frames=120, still=60)
def e_snowball(T):
    R = 110
    gx, gy = 256, 448                       # contact point on the drift
    cx, cy = gx, gy - R
    H = 172
    # impact at frame 0: up with 'out', down with 'in' (a parabola-like hop)
    hop = loop([(5, [0, 0], 'out'), (60, [0, -H], 'in'), (115, [0, 0], 'hold'), (125, [0, 0])], T)
    squash = loop([(115, [97, 104], 'out'), (120, [128, 74], 'io'), (127, [90, 112], 'io'), (136, [104, 97], 'io'),
                   (146, [100, 100], 'hold'), (200, [100, 100], 'in'), (230, [93, 108], 'linear'), (235, [97, 104])], T)
    tilt = loop([(5, 0, 'io'), (60, -9, 'io'), (115, 0, 'hold'), (125, 0)], T)
    ball = group(
        group(
            part(_blob(cx, cy, R, 11, 0.035, 4), fill=_snow_fill(cx, cy, R), outline=S.OW, name='ball'),
            part(circle_path(cx + 34, cy + 42, 10), circle_path(cx - 46, cy + 26, 7), circle_path(cx + 58, cy - 14, 8),
                 circle_path(cx - 8, cy + 72, 6), circle_path(cx + 4, cy - 30, 5), fill='#b4d6f5', name='clumps'),
            part(circle_path(cx - 46, cy - 50, 24, 13).rotate(-42, cx - 46, cy - 50), fill=S.WHITE, o=95, name='gloss'),
            pivot=(cx, cy), r=tilt),
        pivot=(gx, gy), move=hop, s=squash, name='snowball')
    sh_s = loop([(5, [100, 100], 'out'), (60, [56, 56], 'in'), (115, [100, 100], 'hold'), (125, [100, 100])], T)
    sh_o = loop([(5, 30, 'out'), (60, 12, 'in'), (115, 30, 'hold'), (125, 30)], T)
    shadow = part(ellipse(gx, gy - 6, 190, 26), fill=S.OUTLINE, o=sh_o, pivot=(gx, gy - 6), s=sh_s, name='shadow')
    drift = part(P('M 52 478 C 62 452 106 440 150 444 C 182 430 232 428 262 436 C 304 426 354 432 386 444 '
                   'C 426 440 456 456 460 478 C 386 494 126 494 52 478 Z'),
                 fill=S.vgrad(S.G_SNOW, 428, 492), outline=S.OW, name='drift')
    rnd = random.Random(9)
    bits = []
    for k in range(8):
        a = math.radians(-166 + 152 * k / 7 + rnd.uniform(-6, 6))
        dist = rnd.uniform(90, 140)
        dx, up = math.cos(a) * dist, -abs(math.sin(a)) * dist * 0.9 - 36
        x0, y0 = gx + math.cos(a) * 70, gy - 12
        r = rnd.uniform(8, 13)
        t0, dur = 1, rnd.uniform(30, 38)
        mx = anim((0, [0, 0], 'hold'), (t0, [0, 0], 'linear'), (t0 + dur, [dx, 0], 'hold'), (T, [0, 0]))
        my = anim((0, [0, 0], 'hold'), (t0, [0, 0], 'out'), (t0 + dur * 0.45, [0, up], 'in'),
                  (t0 + dur, [0, up + 44], 'hold'), (T, [0, 0]))
        sc = anim((0, 0, 'hold'), (t0, 40, 'out'), (t0 + 8, 100, 'linear'), (t0 + dur * 0.7, 100, 'in'),
                  (t0 + dur, 0, 'hold'), (T, 0))
        bits.append(group(group(part(_blob(x0, y0, r, 6, 0.15, k), fill=S.SNOW, outline=(S.OUTLINE, 3.5), name='bit'),
                                pivot=(x0, y0), move=my, s=sc), pivot=(x0, y0), move=mx, name='bit'))
    sparks = fx.sparkles([(404, 112, 24), (112, 150, 20)], T, start=34, gap=24, dur=40)
    return [fx.glow(256, 300, 230, alpha=0.28), drift, shadow, bits, ball, sparks]


# ============================================================= 067 snow cloud
@emoji(67, 'snow_cloud', '🌨', 'Снегопад', frames=120, still=0)
def e_snow_cloud(T):
    lobes = [circle_path(166, 206, 70), circle_path(258, 158, 94), circle_path(352, 198, 76),
             rounded([(100, 196), (414, 196), (414, 282), (100, 282)], 42)]
    cloud = group(
        part(*lobes, fill=S.vgrad([(0, '#ffffff'), (0.55, '#e3f2ff'), (1, '#a9d1f7')], 64, 284), outline=S.OW,
             name='cloud'),
        part(P('M 196 252 C 214 266 244 268 266 256'), P('M 300 246 C 320 258 348 258 366 246'),
             stroke=stroke('#9ccaf3', 7), name='puff_lines'),
        part(P('M 186 128 C 198 102 222 84 248 78'), stroke=stroke(S.WHITE, 10, o=90), name='gloss'),
        pivot=(258, 220), move=fx.bob(T, 14), s=fx.breathe(T, 98, 102, shift=10), name='cloud')
    specs = [(146, 250, 466, 16, 0.0, 10), (198, 240, 472, 13, 0.42, 9), (248, 250, 470, 17, 0.17, 10),
             (298, 244, 466, 13, 0.6, 9), (346, 250, 470, 16, 0.3, 10), (390, 240, 446, 12, 0.8, 8),
             (112, 240, 430, 12, 0.72, 8)]
    flakes = _flakes(T, specs, fade=0.14)
    sparks = fx.sparkles([(96, 104, 22), (430, 92, 20)], T, start=16, gap=60, dur=40)
    return [fx.glow(256, 240, 230, alpha=0.3), flakes, cloud, sparks]


# ============================================================= 068 moon
@emoji(68, 'moon', '🌙', 'Луна', frames=180, still=0)
def e_moon(T):
    c1, r1 = (232, 258), 186
    c2, r2 = (318, 206), 158
    top, bot = sorted(_circle_cross(c1, r1, c2, r2), key=lambda p: p[1])
    a1t, a1b = _ang(c1, top), _ang(c1, bot)
    if a1b > a1t:
        a1b -= 360
    a2t, a2b = _ang(c2, top), _ang(c2, bot)
    if a2t < a2b:
        a2t += 360
    moon = _arcs([(c1[0], c1[1], r1, a1t, a1b), (c2[0], c2[1], r2, a2b, a2t)])
    gx, gy = _pol(c1[0], c1[1], r1 - 26, 200), _pol(c1[0], c1[1], r1 - 26, 246)
    gloss = P('M %.1f %.1f A %d %d 0 0 1 %.1f %.1f' % (*gx, r1 - 26, r1 - 26, *gy))
    face = [
        part(P('M 104 234 C 114 248 136 250 148 238'), stroke=stroke(COAL, 8), name='eye_closed'),
        part(line(110, 244, 104, 254), line(124, 248, 122, 259), line(138, 246, 140, 257),
             stroke=stroke(COAL, 4.5), name='lashes'),
        part(P('M 134 296 C 142 306 156 306 164 296'), stroke=stroke(COAL, 7), name='smile'),
        part(circle_path(108, 280, 16, 10), fill=S.PINK, o=45, name='cheek'),
    ]
    body = group(
        part(moon, fill=S.vgrad([(0, '#ffffff'), (0.45, '#d9edff'), (1, '#86b4ee')], 72, 444), outline=S.OW,
             name='moon'),
        part(circle_path(94, 168, 12), circle_path(92, 340, 14), circle_path(188, 404, 12), circle_path(222, 116, 9),
             fill='#a9c8ef', name='craters'),
        part(gloss, stroke=stroke(S.WHITE, 12, o=75), name='gloss'),
        face,
        pivot=(170, 262), r=fx.swing(T, 7), move=fx.bob(T, 10, shift=20), name='moon')

    def twinkle(x, y, r, t0):
        st = star(x, y, 5, r, r * 0.46, round_out=r * 0.16, round_in=r * 0.08)
        sc = fx.pulse(T, t0, 70, 100, 125, up='sine', down='sine', peak=0.5)
        return group(part(st, fill=S.vgrad(S.G_SILVER, y - r, y + r), outline=S.OW_THIN, name='star'),
                     pivot=(x, y), s=sc, r=fx.swing(T, 8, shift=t0), name='twinkle_star')

    stars = [twinkle(352, 196, 40, 0), twinkle(436, 104, 24, 60), twinkle(424, 300, 26, 120)]
    sparks = fx.sparkles([(300, 66, 20), (468, 210, 16), (452, 420, 20), (330, 300, 16)], T, start=30, gap=45, dur=40)
    return [fx.glow(200, 258, 230, alpha=0.32, s=fx.breathe(T, 94, 102)), body, stars, sparks]


# ============================================================= 069 shooting star
@emoji(69, 'shooting_star', '🌠', 'Падающая звезда', frames=120, still=0)
def e_shooting_star(T):
    sx, sy = 330, 330

    def streak(off, x0, L, w0, re):
        return P('M %.1f %.1f L %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f L %.1f %.1f Z' % (
            x0, sy + off - w0 / 2, sx + L, sy + off - re, re, re, sx + L, sy + off + re, x0, sy + off + w0 / 2))

    # trail is built along +x from the star and turned to point up-left (225 deg)
    tails = []
    for off, x0, L, w0, re, ph, g in ((-62, sx + 10, 214, 48, 14, 0, [(0, S.WHITE), (0.5, S.MINT), (1, S.TEAL)]),
                                      (62, sx + 10, 190, 48, 14, 40, [(0, S.WHITE), (0.5, S.LILAC), (1, S.VIOLET)]),
                                      (0, sx, 318, 118, 22, 20, [(0, S.WHITE), (0.4, S.ICE), (1, S.BLUE_L)])):
        shp = streak(off, x0, L, w0, re)
        tails.append(group(
            part(shp, fill=S.dgrad(g, (sx, sy), (sx + L + re, sy)), outline=S.OW, name='tail'),
            part(line(sx + 70, sy + off, sx + L * 0.72, sy + off), stroke=stroke(S.WHITE, 10 if off else 16, o=80),
                 name='tail_core'),
            pivot=(sx, sy), s=fx.wave(T, [100, 100], [109, 100], cycles=2, shift=ph), name='tail'))
    trail = group(tails, pivot=(sx, sy), r=225, name='trail')
    d = (-math.sqrt(0.5), -math.sqrt(0.5))
    dust = []
    for k, (off, dist, R, ph) in enumerate(((-30, 250, 16, 0), (36, 220, 13, 0.25), (-4, 280, 18, 0.5), (60, 200, 12, 0.75))):
        x, y = sx + d[0] * 110 - d[1] * off, sy + d[1] * 110 + d[0] * off
        mv = phase(anim((0, [0, 0], 'linear'), (T, [d[0] * dist, d[1] * dist])), ph * T, T)
        sc = phase(anim((0, 0, 'out'), (T * 0.25, 100, 'linear'), (T * 0.6, 80, 'in'), (T, 0)), ph * T, T)
        dust.append(group(part(sparkle_path(x, y, R), fill=S.WHITE, name='dust'), pivot=(x, y), move=mv, s=sc,
                          name='dust'))
    st = star(sx, sy, 5, 124, 56, rot=-78, round_out=16, round_in=9)
    head = group(
        fx.glow(sx, sy, 150, color=S.ICE_L, alpha=0.4, s=fx.breathe(T, 90, 108, cycles=2)),
        part(st, fill=S.vgrad([(0, '#ffffff'), (0.45, '#bfe4ff'), (1, '#4f97f5')], sy - 124, sy + 104),
             outline=S.OW, name='star'),
        part(circle_path(sx - 36, sy - 40, 22, 12).rotate(-40, sx - 36, sy - 40), fill=S.WHITE, o=90, name='gloss'),
        part(circle_path(sx - 64, sy - 14, 7), fill=S.WHITE, o=80, name='gloss_dot'),
        pivot=(sx, sy), r=fx.swing(T, 6, cycles=2), name='head')
    surge = fx.wave(T, [-6, -6], [8, 8], cycles=2)
    body = group(trail, dust, head, pivot=(sx, sy), move=surge, name='shooting_star')
    sparks = fx.sparkles([(456, 210, 22), (214, 454, 20), (130, 300, 16)], T, start=8, gap=40, dur=36)
    return [body, sparks]
