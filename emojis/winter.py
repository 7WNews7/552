"""061-080: winter."""
import math
import random

from kit.registry import emoji
from kit.lottie import part, group, anim, stroke
from kit.geometry import line, circle_path, rounded
from kit import fx, style as S
from kit.lottie import loop, phase, fill, trim, ellipse
from kit.geometry import P, Bez, polyline, star, sparkle_path, morph
from kit.motifs import crown, snowcap


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
    chunks = [(36, 30, 13), (-44, -6, 10), (60, -34, 9), (-6, 70, 9), (-14, -62, 8), (-62, 52, 7)]
    ball = group(
        group(
            part(_blob(cx, cy, R, 13, 0.05, 4), fill=_snow_fill(cx, cy, R), outline=S.OW, name='ball'),
            # packed-snow chunks: raised lumps (shadow below), not craters
            part(*[circle_path(cx + x + 2, cy + y + 4, r) for x, y, r in chunks], fill='#a9cdf2', name='chunk_shadow'),
            part(*[circle_path(cx + x, cy + y, r) for x, y, r in chunks], fill=S.WHITE, name='chunks'),
            part(P('M %f %f C %f %f %f %f %f %f' % (cx + 18, cy + 58, cx + 34, cy + 68, cx + 56, cy + 62, cx + 70, cy + 46)),
                 P('M %f %f C %f %f %f %f %f %f' % (cx - 74, cy + 8, cx - 66, cy + 26, cx - 52, cy + 36, cx - 36, cy + 40)),
                 stroke=stroke('#a9cdf2', 6), name='packing'),
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
        side = -1 if k < 4 else 1                      # bits spray out from both sides of the contact
        elev = math.radians(18 + 16 * (k % 4) + rnd.uniform(-5, 5))
        dist = rnd.uniform(90, 130)
        dx, up = side * math.cos(elev) * dist, -math.sin(elev) * dist - 30
        x0, y0 = gx + side * (R * 0.8 + 6 * (k % 4)), gy - 14
        r = rnd.uniform(10, 15)
        t0, dur = 1, rnd.uniform(30, 38)
        mx = anim((0, [0, 0], 'hold'), (t0, [0, 0], 'linear'), (t0 + dur, [dx, 0], 'hold'), (T, [0, 0]))
        my = anim((0, [0, 0], 'hold'), (t0, [0, 0], 'out'), (t0 + dur * 0.45, [0, up], 'in'),
                  (t0 + dur, [0, up + 44], 'hold'), (T, [0, 0]))
        sc = anim((0, 0, 'hold'), (t0, 40, 'out'), (t0 + 8, 100, 'linear'), (t0 + dur * 0.7, 100, 'in'),
                  (t0 + dur, 0, 'hold'), (T, 0))
        bits.append(group(group(part(_blob(x0, y0, r, 6, 0.15, k), fill=S.SNOW, outline=(S.OUTLINE, 3.5), name='bit'),
                                pivot=(x0, y0), move=my, s=sc), pivot=(x0, y0), move=mx, name='bit'))
    sparks = fx.sparkles([(404, 112, 24), (112, 150, 20)], T, start=34, gap=24, dur=40)
    return [fx.glow(256, 300, 230, alpha=0.28), drift, shadow, ball, bits, sparks]


# ============================================================= 067 snow cloud
@emoji(67, 'snow_cloud', '🌨', 'Снегопад', frames=120, still=0)
def e_snow_cloud(T):
    lobes = [circle_path(166, 206, 70), circle_path(258, 158, 94), circle_path(352, 198, 76),
             rounded([(100, 196), (414, 196), (414, 282), (100, 282)], 42)]
    cloud = group(
        part(*lobes, fill=S.vgrad([(0, '#ffffff'), (0.55, '#e3f2ff'), (1, '#a9d1f7')], 64, 284), outline=S.OW,
             name='cloud'),
        # inner lobe contours (side puffs sit in front of the big one)
        part(P('M %.1f %.1f A 70 70 0 0 1 %.1f %.1f' % (*_pol(166, 206, 70, -78), *_pol(166, 206, 70, -22))),
             P('M %.1f %.1f A 76 76 0 0 1 %.1f %.1f' % (*_pol(352, 198, 76, -158), *_pol(352, 198, 76, -104))),
             stroke=stroke('#b3d7f6', 7), name='lobe_lines'),
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


def _smooth(pts, sharp=()):
    """Closed Catmull-Rom spline through pts; indices in `sharp` become corners."""
    n = len(pts)
    b = Bez()
    for k, p in enumerate(pts):
        if k in sharp:
            b.add(p)
            continue
        a, c = pts[k - 1], pts[(k + 1) % n]
        t = ((c[0] - a[0]) / 6, (c[1] - a[1]) / 6)
        b.add(p, (-t[0], -t[1]), t)
    return b


def _inset(pts, d):
    """Convex polygon (clockwise on screen) moved inwards by d px."""
    n = len(pts)
    lines = []
    for k in range(n):
        a, b = pts[k], pts[(k + 1) % n]
        ex, ey = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(ex, ey)
        lines.append(((a[0] - ey / ln * d, a[1] + ex / ln * d), (ex, ey)))
    out = []
    for k in range(n):
        (p1, d1), (p2, d2) = lines[k - 1], lines[k]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        s = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
        out.append((p1[0] + s * d1[0], p1[1] + s * d1[1]))
    return out


def _disc_hill(cx, cy, R, yl, yr, mid):
    """Hill inside a disc: wavy top from the left rim (y=yl) to the right rim (y=yr), closed along the
    disc's lower arc (stays inside the badge without masks). mid = [c1, c2, (p, c1, c2)...]."""
    assert len(mid) % 3 == 2, 'mid: control pairs with an end point between them'
    xl = cx - math.sqrt(R * R - (yl - cy) ** 2)
    xr = cx + math.sqrt(R * R - (yr - cy) ** 2)
    d = 'M %.2f %.2f ' % (xl, yl)
    pts = [(xl, yl)] + mid + [(xr, yr)]
    for k in range(0, len(mid), 3):
        d += 'C %.2f %.2f %.2f %.2f %.2f %.2f ' % (*pts[k + 1], *pts[k + 2], *pts[k + 3])
    d += 'A %.2f %.2f 0 0 1 %.2f %.2f Z' % (R, R, xl, yl)
    return P(d)


def _mini_fir(x, yb, h, stops=G_FIR_NIGHT, ow=S.OW_THIN):
    tiers = [(yb - h * 0.62, yb, h * 0.42, 3, [h * 0.03, h * 0.06, h * 0.03]),
             (yb - h * 0.86, yb - h * 0.3, h * 0.32, 3, [h * 0.03, h * 0.05, h * 0.03]),
             (yb - h, yb - h * 0.58, h * 0.22, 2, [h * 0.03, h * 0.045])]
    return _fir(x, tiers, stops, snow_t=0.42, ow=ow, droop=h * 0.07, notch=h * 0.05)


def _ribbon(x0, x1, y0, amp, height, ph, n=8, wl=1.0):
    """Aurora curtain: wavy bright lower edge around y0, tapered ends, `ph` shifts the wave."""
    bottom, top = [], []
    for k in range(n + 1):
        u = k / n
        x = x0 + (x1 - x0) * u
        y = y0 + amp * math.sin(2 * math.pi * wl * u + ph)
        h = height * math.sin(math.pi * u) ** 0.8 * (0.82 + 0.18 * math.sin(3 * math.pi * u + ph))
        bottom.append((x, y))
        top.append((x, y - h))
    return _smooth(bottom + top[-2:0:-1], sharp=(0, n))


def _steam(x, y0, y1, T, t0, w=18):
    """Steam curl drawn on and off with trim paths (fading would show the stroke layers)."""
    h = y0 - y1
    path = P('M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f' % (
        x, y0, x - 26, y0 - h * 0.17, x + 26, y0 - h * 0.33, x, y0 - h * 0.5,
        x - 26, y0 - h * 0.67, x + 20, y0 - h * 0.83, x, y1))
    e = phase(anim((0, 0, 'out'), (T * 0.45, 100, 'hold'), (T, 100)), t0, T)
    s = phase(anim((0, 0, 'hold'), (T * 0.25, 0, 'in'), (T * 0.85, 100, 'hold'), (T, 100)), t0, T)
    mv = phase(anim((0, [0, 12], 'linear'), (T, [0, -18])), t0, T)
    return group(part(path, stroke=stroke(S.SKY, w), trim=trim(s, e), name='steam'),
                 part(path, stroke=stroke(S.WHITE, w * 0.4, o=90), trim=trim(s, e), name='steam_core'),
                 pivot=(x, y0), move=mv, name='steam')


# ============================================================= 070 aurora badge
@emoji(70, 'aurora', '🌌', 'Северное сияние', frames=180, still=0)
def e_aurora(T):
    cx, cy, R = 256, 256, 224
    disc = circle_path(cx, cy, R)
    aur = [(0, S.VIOLET), (0.5, '#56c8ff'), (0.85, S.MINT), (1, '#d8fff4')]
    ribbons = []
    for x0, x1, y0, amp, hgt, wl, ph0, op in ((96, 416, 184, 22, 116, 1.2, 0.0, 90), (74, 438, 256, 16, 96, 0.9, 1.9, 100)):
        keys = [(T * k / 6, _ribbon(x0, x1, y0, amp, hgt, ph0 + 2 * math.pi * k / 6, wl=wl), 'linear') for k in range(7)]
        ribbons.append(part(morph(keys), fill=S.vgrad(aur, y0 - hgt - amp, y0 + amp, opacity=[(0, 0), (0.4, 0.5), (0.85, 1), (1, 1)]),
                            o=fx.wave(T, op * 0.8, op, cycles=3), name='aurora'))
    back = _disc_hill(cx, cy, R, 318, 300, [(150, 296), (220, 300), (270, 316), (318, 330), (400, 298)])
    front = _disc_hill(cx, cy, R, 378, 360, [(150, 350), (240, 356), (300, 378), (350, 396), (420, 358)])
    shoot = line(316, 84, 404, 128)
    st_e = anim((0, 0, 'hold'), (118, 0, 'out'), (138, 100, 'hold'), (T, 100))
    st_s = anim((0, 0, 'hold'), (126, 0, 'in'), (150, 100, 'hold'), (T, 100))
    scene = [
        part(disc, fill=S.vgrad([(0, '#0b1a40'), (0.55, '#173a85'), (1, '#2a5cc0')], cy - R, cy + R), outline=S.OW,
             name='sky'),
        part(*[circle_path(x, y, r) for x, y, r in ((150, 110, 3), (210, 70, 2.5), (360, 168, 3), (120, 230, 2.5),
                                                    (300, 132, 2.5), (402, 222, 3))], fill=S.WHITE, o=80, name='stars'),
        fx.glow(cx, 196, 150, color=S.MINT, alpha=0.22, s=fx.breathe(T, 92, 104, cycles=3)),
        ribbons,
        part(shoot, stroke=stroke(S.WHITE, 6), trim=trim(st_s, st_e), name='shooting_star'),
        part(back, fill=S.vgrad([(0, '#d7ecff'), (1, '#8fbdf0')], 296, 480), name='hill_back'),
        _mini_fir(142, 318, 96), _mini_fir(184, 326, 128), _mini_fir(380, 310, 108),
        part(front, fill=S.vgrad(S.G_SNOW, 350, 480), name='hill_front'),
        part(P('M 132 372 C 170 356 220 356 262 366'), stroke=stroke(S.WHITE, 8, o=80), name='hill_gloss'),
        part(circle_path(cx, cy, R - 18), stroke=stroke(S.WHITE, 5, o=65), name='ring'),
    ]
    sparks = fx.sparkles([(240, 96, 18), (420, 260, 14), (92, 300, 14), (330, 230, 12)], T, start=10, gap=45, dur=40,
                         halo=False)
    return [fx.glow(cx, cy, 240, alpha=0.3), scene, sparks]


# ============================================================= 071 ice cube
@emoji(71, 'ice_cube', '🧊', 'Лёд', frames=120, still=0)
def e_ice_cube(T):
    cx, cy, a = 256, 272, 198
    k3 = a * math.sqrt(3) / 2
    top, ur, lr = (cx, cy - a), (cx + k3, cy - a / 2), (cx + k3, cy + a / 2)
    bot, ll, ul, c = (cx, cy + a), (cx - k3, cy + a / 2), (cx - k3, cy - a / 2), (cx, cy)
    sil = rounded([top, ur, lr, bot, ll, ul], 34)
    face = lambda pts: rounded(_inset(pts, 13), 20)
    f_top, f_left, f_right = face([top, ur, c, ul]), face([ul, c, bot, ll]), face([c, ur, lr, bot])
    cube = [
        part(sil, fill=S.vgrad([(0, '#ffffff'), (1, '#b9defc')], cy - a, cy + a), outline=S.OW, name='cube'),
        part(f_top, fill=S.vgrad([(0, '#ffffff'), (1, '#cbe8ff')], cy - a, cy), name='face_top'),
        part(f_left, fill=S.vgrad([(0, '#b4e0ff'), (1, '#5d9ff0')], cy - a / 2, cy + a), name='face_left'),
        part(f_right, fill=S.vgrad([(0, '#78b8ff'), (1, '#2a5fcf')], cy - a / 2, cy + a), name='face_right'),
        # reflections, bubbles and a crack inside the ice
        part(line(ul[0] + 44, ul[1] + 66, ul[0] + 44, ul[1] + 170), line(ul[0] + 76, ul[1] + 104, ul[0] + 76, ul[1] + 148),
             stroke=stroke(S.WHITE, 13, o=70), name='refl_left'),
        part(P('M %f %f L %f %f L %f %f L %f %f' % (cx + 70, cy + 40, cx + 92, cy + 78, cx + 80, cy + 100, cx + 104, cy + 146)),
             stroke=stroke('#cfe9ff', 5, o=80), name='crack'),
        part(circle_path(cx + 128, cy + 24, 10), circle_path(cx + 110, cy + 62, 6), circle_path(cx + 40, cy + 150, 7),
             fill=S.WHITE, o=75, name='bubbles'),
        part(circle_path(cx - 62, cy - 120, 34, 15).rotate(-28, cx - 62, cy - 120), fill=S.WHITE, o=95, name='gloss'),
        part(circle_path(cx + 8, cy - 154, 10, 6).rotate(-28, cx + 8, cy - 154), fill=S.WHITE, o=90, name='gloss_dot'),
    ]
    t_hop = 22
    hop = anim((0, [0, 0], 'hold'), (t_hop, [0, 0], 'out'), (t_hop + 16, [0, -34], 'in'), (t_hop + 30, [0, 0], 'hold'),
               (T, [0, 0]))
    sq = anim((0, [100, 100], 'hold'), (t_hop - 10, [100, 100], 'io'), (t_hop, [104, 95], 'out'),
              (t_hop + 8, [97, 104], 'io'), (t_hop + 30, [100, 100], 'out'), (t_hop + 36, [105, 94], 'io'),
              (t_hop + 50, [100, 100], 'hold'), (T, [100, 100]))
    body = group(
        group(cube, fx.shine([sil], T, t0=64, dur=44, angle=24, width=0.26, alpha=0.85), pivot=(cx, cy + a), s=sq,
              r=fx.wobble(T, t_hop + 30, 44, 4, n=3), name='cube_wobble'),
        pivot=(cx, cy + a), move=hop, name='cube')
    sparks = fx.sparkles([(ur[0] + 6, ur[1] - 10, 30), (ll[0] + 6, ll[1] + 4, 24), (top[0] + 70, top[1] + 10, 22)], T,
                         start=56, gap=18, dur=40)
    return [fx.glow(cx, cy, 236, alpha=0.32), body, sparks]


# ============================================================= 072 snow globe
@emoji(72, 'snow_globe', '🔮', 'Снежный шар', frames=180, still=40)
def e_snow_globe(T):
    gx, gy, gr = 256, 208, 168
    rnd = random.Random(12)
    swirl = []
    for ring, (n, r0, r1, turns) in enumerate(((6, 52, 74, 1), (7, 92, 116, -1), (6, 126, 142, 1))):
        flakes = []
        for k in range(n):
            ang = 360 * k / n + rnd.uniform(-14, 14)
            x, y = _pol(gx, gy, rnd.uniform(r0, r1), ang)
            r = rnd.uniform(5, 9)
            flakes.append(group(part(circle_path(x, y, r), fill=S.WHITE, o=95, name='snow'),
                                pivot=(x, y), move=fx.wave(T, [0, -12], [0, 12], cycles=2, shift=rnd.uniform(0, T))))
        swirl.append(group(flakes, pivot=(gx, gy), r=anim((0, 0, 'out'), (T, 360 * turns)), name='swirl'))
    gloss = P('M %.1f %.1f A %d %d 0 0 1 %.1f %.1f' % (*_pol(gx, gy, gr - 24, 196), gr - 24, gr - 24,
                                                      *_pol(gx, gy, gr - 24, 250)))
    glass = [
        part(circle_path(gx, gy, gr), fill=S.vgrad([(0, '#3f7ad8'), (0.6, '#1f4caa'), (1, '#142f74')], gy - gr, gy + gr),
             outline=S.OW, name='globe'),
        fx.glow(gx, gy + 30, 130, color=S.SKY, alpha=0.4),
        part(_disc_hill(gx, gy, gr, 302, 312, [(180, 286), (232, 292), (262, 300), (296, 308), (350, 292)]),
             fill=S.vgrad(S.G_SNOW, 286, 380), name='snow_ground'),
        _mini_fir(gx, 300, 168, stops=G_FIR),
        swirl,
        part(circle_path(gx, gy, gr - 7), stroke=stroke(S.ICE_L, 6, o=50), name='rim_light'),
    ]
    c = crown(256, 424, 108, ow=5)
    base = [
        part(rounded([(138, 350), (374, 350), (410, 470), (102, 470)], [14, 14, 22, 22]),
             fill=S.vgrad(S.G_DEEP, 350, 470), outline=S.OW, name='base'),
        part(rounded([(122, 336), (390, 336), (390, 366), (122, 366)], 14), fill=S.vgrad(S.G_SILVER, 336, 366),
             outline=S.OW_THIN, name='base_rim'),
        part(P('M 132 384 C 128 412 122 440 116 458'), stroke=stroke(S.WHITE, 8, o=40), name='base_gloss'),
        c['parts'],
    ]
    top_gloss = [part(gloss, stroke=stroke(S.WHITE, 15, o=85), name='glass_gloss'),
                 part(circle_path(gx - 30, gy - 132, 9), fill=S.WHITE, o=85, name='glass_dot'),
                 part(P('M %.1f %.1f A %d %d 0 0 1 %.1f %.1f' % (*_pol(gx, gy, gr - 20, -24), gr - 20, gr - 20,
                                                               *_pol(gx, gy, gr - 20, 16))),
                      stroke=stroke(S.WHITE, 8, o=35), name='glass_side')]
    body = group(glass, base, top_gloss, fx.sparkle(c['tips'][1][0] + 26, c['tips'][1][1] - 6, 18, T, t0=100, dur=36),
                 pivot=(256, 470), r=fx.wobble(T, 0, 50, 6, n=3), name='globe')
    sparks = fx.sparkles([(430, 70, 22), (70, 120, 18)], T, start=60, gap=50, dur=40)
    return [fx.glow(256, 250, 236, alpha=0.3), body, sparks]


# ============================================================= 073 cocoa
@emoji(73, 'cocoa', '☕', 'Какао', frames=120, still=0)
def e_cocoa(T):
    mx, rim_y = 236, 228
    body = P('M 108 228 L 364 228 C 362 330 358 400 344 438 C 338 456 322 468 300 468 L 172 468 '
             'C 150 468 134 456 128 438 C 114 400 110 330 108 228 Z')
    handle = P('M 352 262 C 422 254 458 288 458 334 C 458 386 420 416 350 410 L 350 376 '
               'C 398 380 424 362 424 334 C 424 306 400 290 352 296 Z')
    lip = P('M 108 228 A 128 28 0 0 0 364 228 L 348 232 A 112 20 0 0 1 124 232 Z')
    main, side = _flake_arms(mx, 352, 14, 58, [(30, 22, 52)])
    mallows = []
    for k, (x, y, rot) in enumerate(((190, 222, -14), (244, 212, 8), (290, 224, -4))):
        sq = rounded([(x - 24, y - 21), (x + 24, y - 21), (x + 24, y + 21), (x - 24, y + 21)], 12).rotate(rot, x, y)
        mallows.append(group(part(sq, fill=S.vgrad([(0, '#ffffff'), (1, '#ddd6ff')], y - 22, y + 22),
                                  outline=(S.OUTLINE, 4.5), name='marshmallow'),
                             pivot=(x, y + 18), move=fx.bob(T, 5, shift=k * 26), r=fx.swing(T, 4, shift=k * 34)))
    mug = [
        part(handle, fill=S.vgrad(S.G_DEEP, 254, 416), outline=S.OW, name='handle'),
        part(body, fill=S.vgrad(S.G_DEEP, 228, 468), outline=S.OW, name='mug'),
        part(ellipse(mx, rim_y, 256, 56), fill=S.vgrad(S.G_SILVER, 200, 256), outline=S.OW, name='rim'),
        part(ellipse(mx, rim_y + 4, 224, 40), fill=S.vgrad([(0, '#a8745a'), (1, '#6e4636')], 212, 252),
             outline=(S.OUTLINE, 3), name='cocoa'),
        mallows,
        part(lip, fill=S.vgrad([(0, '#ffffff'), (1, '#9fbfe6')], 230, 256), name='lip'),
        part(*main, stroke=stroke(S.WHITE, 11), name='print'),
        part(*side, stroke=stroke(S.WHITE, 8), name='print_branches'),
        part(circle_path(mx, 352, 13), fill=S.WHITE, name='print_hub'),
        part(P('M 132 266 C 134 330 140 392 154 432'), stroke=stroke(S.WHITE, 12, o=55), name='gloss'),
    ]
    steam = [_steam(196, 194, 60, T, 0), _steam(246, 184, 44, T, T / 3), _steam(292, 196, 72, T, 2 * T / 3)]
    sparks = fx.sparkles([(402, 210, 22), (90, 300, 18)], T, start=20, gap=60, dur=38)
    return [fx.glow(256, 300, 228, alpha=0.28), steam, mug, sparks]


def _flame(cx, by, w, h, lean=0.0):
    """Candle flame: round bottom at y=by, sharp tip leaning sideways by `lean` (4 vertices, morphable)."""
    r = w / 2
    yc = by - r
    b = Bez()
    b.add((cx + lean, by - h), (-r * 0.2, h * 0.28), (r * 0.2, h * 0.28))
    b.add((cx + r, yc), (0, -h * 0.4), (0, r * 0.56))
    b.add((cx, by), (r * 0.56, 0), (-r * 0.56, 0))
    b.add((cx - r, yc), (0, r * 0.56), (0, -h * 0.4))
    return b


# ============================================================= 074 candle
@emoji(74, 'candle', '🕯', 'Свеча', frames=120, still=0)
def e_candle(T):
    cx, fb = 256, 200                       # flame bottom
    keys = [(0, 0, 132, 64), (20, 9, 142, 60), (40, -7, 126, 66), (60, 6, 138, 62), (80, -9, 130, 64), (100, 4, 140, 60)]
    keys.append((T,) + keys[0][1:])
    outer = morph([(t, _flame(cx, fb, w, h, lean), 'sine') for t, lean, h, w in keys])
    inner = morph([(t, _flame(cx, fb - 8, w * 0.44, h * 0.52, lean * 0.6), 'sine') for t, lean, h, w in keys])
    flicker = fx.wave(T, 100, 104, cycles=3)
    flame = group(
        part(outer, fill=S.vgrad([(0, '#fffbe8'), (0.42, '#ffd66b'), (0.78, '#ffb347'), (1, '#6fb6ff')], fb - 142, fb),
             outline=(S.OUTLINE, 5), name='flame'),
        part(inner, fill=S.vgrad([(0, '#ffffff'), (1, '#fff1c4')], fb - 80, fb - 8), name='flame_core'),
        pivot=(cx, fb), s=flicker, name='flame')
    body = rounded([(188, 222), (324, 222), (324, 446), (188, 446)], 10)
    cap = snowcap(188, 324, 228, h=34, drips=((0.2, 30), (0.66, 50)))
    drip_mv = anim((0, [0, 0], 'hold'), (26, [0, 0], 'in'), (96, [0, 150], 'hold'), (T, [0, 0]))
    drip_s = anim((0, [0, 0], 'hold'), (12, [0, 0], 'outback'), (26, [100, 120], 'linear'), (86, [100, 125], 'in'),
                  (100, [0, 0], 'hold'), (T, [0, 0]))
    drip = group(part(P('M 302 248 C 312 262 314 270 314 276 C 314 284 308 290 302 290 C 296 290 290 284 290 276 '
                        'C 290 270 292 262 302 248 Z'), fill=S.vgrad([(0, '#ffffff'), (1, '#d4eaff')], 248, 290),
                      outline=(S.OUTLINE, 3.5), name='wax_drop'),
                 pivot=(302, 270), move=drip_mv, s=drip_s, name='drip')
    candle = [
        part(P('M 108 440 C 112 466 180 482 256 482 C 332 482 400 466 404 440 Z'), fill=S.vgrad(S.G_DEEP, 430, 482),
             outline=S.OW, name='dish'),
        part(ellipse(256, 440, 296, 52), fill=S.vgrad(S.G_SILVER, 414, 466), outline=S.OW, name='dish_top'),
        part(ellipse(256, 438, 236, 30), fill=S.vgrad([(0, '#b6cde8'), (1, '#e8f2ff')], 424, 452), name='dish_well'),
        part(body, fill=S.dgrad([(0, '#f4fbff'), (0.55, '#d3e9fd'), (1, '#8fbcef')], (188, 300), (324, 300)),
             outline=S.OW, name='candle'),
        part(line(208, 284, 208, 424), stroke=stroke(S.WHITE, 12, o=75), name='candle_gloss'),
        drip,
        part(cap, fill=S.vgrad([(0, '#ffffff'), (1, '#e1f0ff')], 206, 280), outline=(S.OUTLINE, 4.5), name='wax_cap'),
        part(ellipse(256, 214, 64, 12), fill='#cfe4fb', name='wax_pool'),
        part(line(cx, 216, cx + 2, 192), stroke=stroke(COAL, 7), name='wick'),
    ]
    glow_warm = fx.glow(cx, 138, 116, color='#ffe7a3', alpha=0.42, s=fx.wave(T, 90, 106, cycles=3, shift=6))
    sparks = fx.sparkles([(338, 92, 20), (170, 146, 16), (390, 300, 18)], T, start=14, gap=40, dur=36)
    return [fx.glow(256, 300, 226, alpha=0.24), glow_warm, candle, flame, sparks]


def _mitten(cx, cy, s=1.0, mirror=False):
    """Knitted mitten (thumb on the left, or on the right when mirrored). Returns parts."""
    m = (lambda b: b.map(lambda x, y: (cx - x * s, cy + y * s))) if mirror else \
        (lambda b: b.map(lambda x, y: (cx + x * s, cy + y * s)))
    hand = m(P('M -56 64 L -58 26 C -82 30 -104 8 -104 -20 C -104 -46 -86 -60 -70 -54 C -60 -50 -56 -36 -56 -20 '
               'L -58 -98 C -58 -138 -28 -160 8 -160 C 46 -160 72 -136 72 -98 L 70 64 Z'))
    cuff = m(rounded([(-70, 46), (82, 46), (82, 146), (-70, 146)], 18))
    zig = m(polyline([(-48, 14), (-34, 2), (-20, 22), (-6, 2), (8, 22), (22, 2), (36, 22), (50, 2), (62, 14)]))
    flake = [m(line(*_pol(8, -84, 26, a), *_pol(8, -84, 26, a + 180))) for a in (90, 30, -30)]
    ribs = [m(line(x, 58, x, 134)) for x in range(-52, 72, 16)]
    gloss = m(P('M -40 -98 C -40 -124 -24 -140 -2 -146'))
    y0, y1 = cy - 160 * s, cy + 146 * s
    return [
        part(hand, fill=S.vgrad(S.G_DEEP, y0, cy + 64 * s), outline=S.OW, name='mitten'),
        part(zig, stroke=stroke(S.WHITE, 7), name='zigzag'),
        part(*flake, stroke=stroke(S.WHITE, 8), name='flake'),
        part(gloss, stroke=stroke(S.WHITE, 10, o=60), name='gloss'),
        part(cuff, fill=S.vgrad(S.G_SNOW, cy + 46 * s, y1), outline=S.OW, name='cuff'),
        part(*ribs, stroke=stroke('#a9cdf2', 6), name='ribs'),
    ]


# ============================================================= 075 mittens
@emoji(75, 'mittens', '🧤', 'Варежки', frames=120, still=0)
def e_mittens(T):
    string = P('M 36 96 C 150 136 362 136 476 96')
    pins = [(150, 122), (362, 122)]
    hang = []
    for k, (px, py) in enumerate(pins):
        pin = rounded([(px - 12, py - 26), (px + 12, py - 26), (px + 12, py + 26), (px - 12, py + 26)], 7)
        mit = _mitten(px, py + 148, 0.92, mirror=(k == 0))
        hang.append(group(mit, part(pin, fill=S.vgrad(S.G_ICE_SOFT, py - 26, py + 26), outline=S.OW_THIN, name='pin'),
                          part(line(px - 6, py - 4, px + 6, py - 4), stroke=stroke(S.STEEL, 4), name='pin_spring'),
                          pivot=(px, py), r=fx.swing(T, 7, shift=-12 * k), name='mitten'))
    line_parts = [part(string, stroke=stroke(S.OUTLINE, 14), name='string_ow'),
                  part(string, stroke=stroke(S.ICE_L, 6), name='string'),
                  part(circle_path(36, 96, 9), circle_path(476, 96, 9), fill=S.vgrad(S.G_DEEP, 86, 106),
                       outline=S.OW_THIN, name='pegs')]
    flakes = _flakes(T, [(256, 170, 330, 13, 0.0, 10), (256, 300, 470, 11, 0.5, 9), (60, 220, 420, 10, 0.3, 8),
                         (454, 230, 420, 10, 0.8, 8)])
    sparks = fx.sparkles([(256, 214, 20), (96, 448, 18), (420, 448, 18)], T, start=30, gap=40, dur=36)
    return [fx.glow(256, 280, 228, alpha=0.26), flakes, line_parts, hang, sparks]


# ============================================================= 076 scarf
@emoji(76, 'scarf', '🧣', 'Шарф', frames=120, still=0)
def e_scarf(T):
    cx, cy = 256, 150
    RX, RY, rx, ry = 176, 90, 100, 40
    back = P('M %f %f A %f %f 0 0 1 %f %f L %f %f A %f %f 0 0 0 %f %f Z' % (
        cx - RX, cy, RX, RY, cx + RX, cy, cx + rx, cy - 6, rx, ry, cx - rx, cy - 6))
    front = P('M %f %f A %f %f 0 0 0 %f %f L %f %f A %f %f 0 0 1 %f %f Z' % (
        cx - RX, cy, RX, RY, cx + RX, cy, cx + rx, cy - 6, rx, ry, cx - rx, cy - 6))
    knit_dark = [(0.0, '#3159bd'), (1.0, '#142a66')]
    band_ribs = []
    for a in (24, 46, 68, 90, 112, 134, 156):
        p0 = (cx + rx * math.cos(math.radians(a)) * 1.06, cy - 6 + ry * math.sin(math.radians(a)) * 1.1)
        p1 = (cx + RX * math.cos(math.radians(a)) * 0.95, cy + RY * math.sin(math.radians(a)) * 0.93)
        band_ribs.append(line(*p0, *p1))

    def tail(x0, x1, xb0, xb1, yt, yb, bend):
        """Tail from top edge (x0..x1 at yt) to bottom edge (xb0..xb1 at yb); returns body, ribs, stripes, fringe."""
        body = P('M %f %f L %f %f C %f %f %f %f %f %f L %f %f C %f %f %f %f %f %f Z' % (
            x0, yt, x1, yt + 4, x1 + bend, yt + (yb - yt) * 0.4, xb1 - bend * 0.3, yb - (yb - yt) * 0.3, xb1, yb,
            xb0, yb + 6, xb0 - bend * 0.3, yb - (yb - yt) * 0.3, x0 + bend, yt + (yb - yt) * 0.4, x0, yt))
        def across(u):
            pa = _cubic((x0, yt), (x0 + bend, yt + (yb - yt) * 0.4), (xb0 - bend * 0.3, yb - (yb - yt) * 0.3),
                        (xb0, yb + 6), u)
            pb = _cubic((x1, yt + 4), (x1 + bend, yt + (yb - yt) * 0.4), (xb1 - bend * 0.3, yb - (yb - yt) * 0.3),
                        (xb1, yb), u)
            k = 0.06   # stop short of the edges so stroke ends stay inside the tail
            return line(pa[0] + (pb[0] - pa[0]) * k, pa[1] + (pb[1] - pa[1]) * k,
                        pb[0] - (pb[0] - pa[0]) * k, pb[1] - (pb[1] - pa[1]) * k)
        ribs = [across(u) for u in (0.3, 0.45, 0.6)]
        stripes = [across(0.76), across(0.88)]
        fringe = [line(xb0 + (xb1 - xb0) * f, yb + 6 - 6 * f, xb0 + (xb1 - xb0) * f + bend * 0.15,
                       yb + 34 - 6 * f) for f in (0.1, 0.3, 0.5, 0.7, 0.9)]
        return body, ribs, stripes, fringe

    def tail_parts(body, ribs, stripes, fringe, stops):
        return [part(*fringe, stroke=stroke(S.OUTLINE, 22), name='fringe_ow'),
                part(*fringe, stroke=stroke('#2c4fa8', 9), name='fringe'),
                part(body, fill=S.vgrad(stops, 200, 460), outline=S.OW, name='tail'),
                part(*ribs, stroke=stroke('#6d93ea', 5, o=60), name='tail_ribs'),
                part(*stripes, stroke=stroke(S.ICE_L, 13), name='tail_stripes')]

    # back tail flutters (morph between bends); every path keeps its vertex count
    flutter = [(0, 0), (30, 16), (60, 4), (90, -12), (120, 0)]
    shapes = [tail(250, 330, 290 + b, 370 + b, 214, 408 - abs(b) * 0.3, 10 + b) for _, b in flutter]
    mk = lambda sel: [morph([(t, sh[sel] if sel == 0 else sh[sel][j], 'sine') for (t, _), sh in zip(flutter, shapes)])
                      for j in range(1 if sel == 0 else len(shapes[0][sel]))]
    back_tail = tail_parts(mk(0)[0], mk(1), mk(2), mk(3), knit_dark)
    f_body, f_ribs, f_stripes, f_fringe = tail(166, 252, 142, 228, 210, 444, -6)
    front_tail = group(tail_parts(f_body, f_ribs, f_stripes, f_fringe, G_KNIT), pivot=(212, 212),
                       r=fx.swing(T, 2.5, shift=20), name='front_tail')
    scarf = group(
        part(back, fill=S.vgrad(knit_dark, cy - RY, cy), outline=S.OW, name='loop_back'),
        back_tail,
        part(front, fill=S.vgrad(G_KNIT, cy - 10, cy + RY), outline=S.OW, name='loop_front'),
        part(*band_ribs, stroke=stroke('#6d93ea', 5, o=60), name='loop_ribs'),
        part(P('M %f %f A %f %f 0 0 0 %f %f' % (cx + (RX - 18) * math.cos(math.radians(160)), cy + (RY - 18) * math.sin(math.radians(160)),
                                                RX - 18, RY - 18, cx + (RX - 18) * math.cos(math.radians(122)),
                                                cy + (RY - 18) * math.sin(math.radians(122)))),
             stroke=stroke(S.WHITE, 8, o=45), name='loop_gloss'),
        front_tail,
        pivot=(256, 260), move=fx.bob(T, 8), name='scarf')
    flakes = _flakes(T, [(420, 250, 470, 12, 0.0, 12), (80, 260, 470, 11, 0.5, 12), (460, 120, 300, 9, 0.3, 10)])
    sparks = fx.sparkles([(434, 70, 22), (84, 76, 18)], T, start=40, gap=40, dur=36)
    return [fx.glow(256, 270, 230, alpha=0.26), flakes, scarf, sparks]


# ============================================================= 077 ornament ball
@emoji(77, 'xmas_ball', '🎄', 'Ёлочный шар', frames=180, still=0)
def e_xmas_ball(T):
    bx, by, br = 256, 324, 146
    pv = (256, 62)
    ball = circle_path(bx, by, br)
    lat = lambda y, inset=10: (bx - math.sqrt(br * br - (y - by) ** 2) + inset, bx + math.sqrt(br * br - (y - by) ** 2) - inset)
    bands = []
    for y, sag in ((262, 22), (390, 24)):
        xa, xb = lat(y)
        bands.append(P('M %f %f C %f %f %f %f %f %f' % (xa, y, xa + (xb - xa) * 0.3, y + sag, xa + (xb - xa) * 0.7, y + sag, xb, y)))
    dots = []
    for y, sag in ((262, 22), (390, 24)):
        xa, xb = lat(y)
        for u in (0.12, 0.3, 0.7, 0.88):
            px, py = _cubic((xa, y), (xa + (xb - xa) * 0.3, y + sag), (xa + (xb - xa) * 0.7, y + sag), (xb, y), u)
            dots.append(circle_path(px, py + (16 if y < by else -16), 6))
    main, side = _flake_arms(bx, by + 2, 12, 50, [(26, 18, 50)])
    hanging = group(
        part(rounded([(249, 58), (263, 58), (263, 150), (249, 150)], 4), fill=S.vgrad(S.G_VIOLET, 58, 150),
             outline=S.OW_THIN, name='ribbon'),
        part(circle_path(256, 146, 11), stroke=stroke(S.OUTLINE, 11), name='ring_ow'),
        part(circle_path(256, 146, 11), stroke=stroke(S.SILVER, 5), name='ring'),
        part(ball, fill=S.rgrad([(0, '#eaf6ff'), (0.35, '#9fd0ff'), (0.75, '#3f7fe8'), (1, '#1f4fb2')], bx - 52, by - 62,
                                br * 1.55), outline=S.OW, name='ball'),
        part(*bands, stroke=stroke(S.WHITE, 8, o=85), name='bands'),
        part(*dots, fill=S.WHITE, o=85, name='dots'),
        part(*main, stroke=stroke(S.WHITE, 9), name='flake'),
        part(*side, stroke=stroke(S.WHITE, 6), name='flake_branches'),
        part(circle_path(bx, by + 2, 11), fill=S.WHITE, name='flake_hub'),
        part(circle_path(bx - 62, by - 78, 40, 19).rotate(-40, bx - 62, by - 78), fill=S.WHITE, o=90, name='gloss'),
        part(circle_path(bx - 104, by - 26, 9), fill=S.WHITE, o=85, name='gloss_dot'),
        fx.shine([ball], T, t0=88, dur=60, angle=28, width=0.24, alpha=0.6),
        part(rounded([(224, 160), (288, 160), (288, 194), (224, 194)], 7), fill=S.vgrad(S.G_SILVER, 160, 194),
             outline=S.OW_THIN, name='cap'),
        part(*[line(x, 166, x, 188) for x in (238, 250, 262, 274)], stroke=stroke(S.STEEL, 4, o=70), name='cap_ridges'),
        pivot=pv, r=fx.swing(T, 9), name='ornament')
    bow = [part(circle_path(226, 52, 30, 17).rotate(-18, 226, 52), circle_path(286, 52, 30, 17).rotate(18, 286, 52),
                fill=S.vgrad(S.G_VIOLET, 34, 70), outline=S.OW_THIN, name='bow_loops'),
           part(circle_path(256, 60, 15), fill=S.vgrad(S.G_VIOLET, 46, 74), outline=S.OW_THIN, name='bow_knot'),
           part(circle_path(220, 46, 8, 4).rotate(-18, 220, 46), circle_path(280, 46, 8, 4).rotate(18, 280, 46),
                fill=S.WHITE, o=70, name='bow_gloss')]
    sparks = fx.sparkles([(430, 196, 24), (84, 252, 20), (404, 452, 18)], T, start=20, gap=55, dur=40)
    return [fx.glow(256, 320, 226, alpha=0.3), hanging, bow, sparks]
