"""001-010: KRONOS brand and staff roles."""
import math
import random

from kit.registry import emoji
from kit.lottie import part, group, anim, loop, stroke, trim, ellipse
from kit.geometry import P, Bez, bbox_of, rounded, circle_path, polyline, sparkle_path, star
from kit.motifs import crown
from kit.text import glyphs, fit_cap
from kit import fx, style as S


@emoji(1, 'crown', '👑', 'Ледяная корона KRONOS', frames=180, still=62)
def e_crown(T):
    c = crown(256, 272, 424)
    pivot = (256, 300)
    sparks = fx.sparkles([(x, y - 4, 32) for x, y in c['tips']], T, dur=46, start=44, gap=22)
    sparks.append(fx.sparkle(c['gem'][0] + 30, c['gem'][1] - 14, 20, T, t0=112, dur=36))
    body = group(c['parts'], fx.shine(c['shine'], T, t0=24, dur=62, angle=24, width=0.28, alpha=0.9), sparks,
                 pivot=pivot, r=fx.swing(T, 3), move=fx.bob(T, 14), name='crown')
    return [fx.glow(256, 286, 226, alpha=0.32, s=fx.breathe(T, 90, 104)), body]


# ------------------------------------------------------------------ helpers (002-010)
G_ROYAL = [(0.0, '#8aa6ff'), (0.55, '#4a63e0'), (1.0, '#25319a')]   # ADMIN pill
G_CYAN = [(0.0, '#6fd2ff'), (0.55, '#2490dc'), (1.0, '#15529a')]    # MOD badge
G_LETTER = [(0.0, '#ffffff'), (0.6, '#eef7ff'), (1.0, '#b7dcff')]    # white letters on blue


def _box(cx, cy, w, h, r):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    return rounded([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], r)


def _pill(cx, cy, w, h):
    return _box(cx, cy, w, h, h / 2)


def _ring(cx, cy, r_out, r_in):
    """Annulus: the reversed inner circle is a hole under the nonzero fill rule."""
    return [circle_path(cx, cy, r_out), circle_path(cx, cy, r_in).reversed()]


def _arc_band(cx, cy, r_out, r_in, a0, a1):
    """Ring sector between angles a0..a1 (degrees, clockwise from +x)."""
    def pt(r, a):
        return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = pt(r_out, a0), pt(r_out, a1), pt(r_in, a1), pt(r_in, a0)
    lg = 1 if (a1 - a0) % 360 > 180 else 0
    return P(f'M {x0} {y0} A {r_out} {r_out} 0 {lg} 1 {x1} {y1} L {x2} {y2} '
             f'A {r_in} {r_in} 0 {lg} 0 {x3} {y3} Z')


def _fit(word, max_w, cap, weight=900, tracking=0.03, width=1.0):
    """fit_cap() that also honours a horizontal squeeze."""
    return min(cap, fit_cap(word, max_w / width, 1e6, weight=weight, tracking=tracking))


def _word(word, cx, cy, cap, weight=900, tracking=0.03, width=1.0):
    """glyphs() re-centred on the visible bounding box (side bearings are uneven)."""
    gl = glyphs(word, cx, cy, cap, weight=weight, tracking=tracking, width=width)
    b = bbox_of([p for ps, _ in gl for p in ps])
    dx = cx - (b[0] + b[2]) / 2
    return [([p.translate(dx, 0) for p in ps], (c[0] + dx, c[1])) for ps, c in gl]


def _shift(paths, dx, dy):
    return [p.translate(dx, dy) for p in paths]


def _pop(T, t0, peak=112, dur=30, under=97):
    """Scalar scale: quick grow, soft overshooting settle, 100 elsewhere."""
    return loop([(t0, 100, 'out'), (t0 + dur * 0.3, peak, 'io'), (t0 + dur * 0.62, under, 'io'),
                 (t0 + dur, 100, 'linear'), (t0 + T, 100)], T)


def _hop(T, t0, dy=-22, up=11, down=12):
    """[dx, dy] offset: one hop (rise eased out, fall eased in)."""
    return loop([(t0, [0, 0], 'out'), (t0 + up, [0, dy], 'in'), (t0 + up + down, [0, 0], 'linear'),
                 (t0 + T, [0, 0])], T)


def _squash(T, t0, k=8, dur=18):
    """[sx, sy] landing squash starting at t0."""
    return loop([(t0, [100, 100], 'out'), (t0 + dur * 0.3, [100 + k, 100 - k], 'io'),
                 (t0 + dur, [100, 100], 'linear'), (t0 + T, [100, 100])], T)


def _fan(cx, cy, T, t0, n, r0, r1, a0, a1, size=14, color=S.WHITE, dur=30, seed=5, shape='spark'):
    """Particles flying out once per loop inside the angle range a0..a1 (fx.burst is 360)."""
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        a = math.radians(a0 + (a1 - a0) * (k + 0.5) / n + rnd.uniform(-6, 6))
        rr = r1 * rnd.uniform(0.75, 1.0)
        p0 = [math.cos(a) * r0, math.sin(a) * r0]
        p1 = [math.cos(a) * rr, math.sin(a) * rr]
        mv = loop([(t0, p0, 'out2'), (t0 + dur, p1, 'hold'), (t0 + T, p0)], T)
        sc = loop([(t0, 0, 'out'), (t0 + dur * 0.25, 100, 'in'), (t0 + dur, 0, 'hold'), (t0 + T, 0)], T)
        sz = size * rnd.uniform(0.7, 1.1)
        shp = sparkle_path(cx, cy, sz) if shape == 'spark' else circle_path(cx, cy, sz / 2)
        out.append(group(part(shp, fill=color, name='p'), pivot=(cx, cy), move=mv, s=sc, name='particle'))
    return out


def _flat_ring(cx, cy, w0, w1, ratio, T, t0, dur=30, color=S.ICE_L, sw0=12, sw1=2, alpha=90):
    """Flattened expanding ring (shock wave on the ground)."""
    size = loop([(t0, [w0, w0 * ratio], 'out'), (t0 + dur, [w1, w1 * ratio], 'hold'),
                 (t0 + T, [w0, w0 * ratio])], T)
    width = loop([(t0, sw0, 'out'), (t0 + dur, sw1, 'hold'), (t0 + T, sw0)], T)
    op = loop([(t0, 0, 'out'), (t0 + dur * 0.15, alpha, 'in'), (t0 + dur, 0, 'hold'), (t0 + T, 0)], T)
    return part(ellipse(cx, cy, size), stroke=stroke(color, width, o=op), name='shock')


def _shield(cx, top, w, h, half=False):
    """Heater shield (top edge arches up a little). half=True -> left half only (shading)."""
    x0, x1, by = cx - w / 2, cx + w / 2, top + h
    c = w * 0.09
    arch = top - h * 0.045
    left = (f'C {cx - w * 0.1} {top - h * 0.032} {cx - w * 0.22} {top} {x0 + c} {top} '
            f'C {x0 + c * 0.45} {top} {x0} {top + c * 0.45} {x0} {top + c} '
            f'L {x0} {top + h * 0.40} '
            f'C {x0} {top + h * 0.70} {cx - w * 0.26} {top + h * 0.88} {cx} {by} ')
    if half:
        return P(f'M {cx} {arch} ' + left + 'Z')
    right = (f'C {cx + w * 0.26} {top + h * 0.88} {x1} {top + h * 0.70} {x1} {top + h * 0.40} '
             f'L {x1} {top + c} '
             f'C {x1} {top + c * 0.45} {x1 - c * 0.45} {top} {x1 - c} {top} '
             f'C {cx + w * 0.22} {top} {cx + w * 0.1} {top - h * 0.032} {cx} {arch} ')
    return P(f'M {cx} {arch} ' + left + right + 'Z')


def _shield_parts(cx, top, w, h, ow=S.OW, rim=None, field=None):
    """Icy rim + deep-blue field + bevel light on the left half. Returns (parts, outer path)."""
    rim = w * 0.065 if rim is None else rim
    outer = _shield(cx, top, w, h)
    inner_args = (cx, top + rim, w - 2 * rim, h - rim * 2.6)
    inner = _shield(*inner_args)
    parts = [
        part(outer, fill=S.vgrad(S.G_SILVER, top - h * 0.05, top + h), outline=ow, name='shield_rim'),
        part(inner, fill=S.vgrad(field or S.G_DEEP, top, top + h), outline=(S.OUTLINE, max(2.5, ow * 0.35)),
             name='shield_field'),
        part(_shield(*inner_args, half=True), fill=S.WHITE, o=16, name='shield_bevel'),
    ]
    return parts, outer


def _rosette(cx, cy, R, A, n, peak_k=1.2, valley_k=0.6):
    """Scalloped badge outline: n round bumps (radius R +- A)."""
    b = Bez()
    step = math.pi / n
    base = 4.0 / 3.0 * math.tan(step / 4)
    for k in range(2 * n):
        a = -math.pi / 2 + k * step
        r = R + A if k % 2 == 0 else R - A
        hk = base * r * (peak_k if k % 2 == 0 else valley_k)
        tx, ty = -math.sin(a), math.cos(a)
        b.add((cx + r * math.cos(a), cy + r * math.sin(a)), (-tx * hk, -ty * hk), (tx * hk, ty * hk))
    return b


def _crown_group(cx, cy, w, T, ow=6, spark_t0=None, spark_gap=10, spark_r=None, **tf):
    c = crown(cx, cy, w, ow=ow)
    kids = list(c['parts'])
    if spark_t0 is not None:
        r = spark_r or max(12, w * 0.1)
        kids.append(fx.sparkles([(x, y, r) for x, y in c['tips']], T, start=spark_t0, gap=spark_gap, dur=32))
    return group(kids, name='crown', **tf), c


def _hammer(L, head_len, head_thk, handle_w, ow=S.OW, word=None, cap_w=None):
    """Hammer in LOCAL coordinates: grip at (0, 0), handle pointing up, head centred at (0, -L)
    with its long axis horizontal. Returns (handle parts, head parts, head path)."""
    cap_w = head_thk * 0.26 if cap_w is None else cap_w
    hy = -L
    handle = _box(0, (hy + head_thk * 0.2 + handle_w * 0.9) / 2, handle_w, -hy + handle_w * 0.9 - head_thk * 0.2,
                  handle_w / 2)
    hb = handle.bbox()
    handle_parts = [
        part(handle, fill=S.dgrad([(0, '#4a86ec'), (0.38, '#8cc4ff'), (1, '#173e9e')],
                                  (-handle_w / 2, 0), (handle_w / 2, 0)), outline=ow, name='handle'),
        part(_box(0, hb[3] - handle_w * 0.75, handle_w + 4, handle_w * 0.34, handle_w * 0.17),
             _box(0, hb[3] - handle_w * 1.45, handle_w + 4, handle_w * 0.34, handle_w * 0.17),
             fill=S.NAVY, name='grip_bands'),
    ]
    body = _box(0, hy, head_len - cap_w * 0.6, head_thk, head_thk * 0.16)
    caps = [_box(sx * (head_len / 2 - cap_w / 2), hy, cap_w, head_thk + head_thk * 0.16, cap_w * 0.42)
            for sx in (-1, 1)]
    head_parts = [
        part(body, fill=S.vgrad(S.G_ICE, hy - head_thk / 2, hy + head_thk / 2), outline=ow, name='head'),
        part(_box(0, hy - head_thk * 0.27, head_len - cap_w * 2.6, head_thk * 0.13, head_thk * 0.065),
             fill=S.WHITE, o=70, name='head_gloss'),
        part(*caps, fill=S.vgrad(S.G_DEEP, hy - head_thk * 0.58, hy + head_thk * 0.58), outline=ow, name='head_caps'),
        part(*[_box(sx * (head_len / 2 - cap_w / 2) - cap_w * 0.12, hy - head_thk * 0.1, cap_w * 0.26,
                    head_thk * 0.62, cap_w * 0.13) for sx in (-1, 1)], fill=S.WHITE, o=45, name='cap_gloss'),
    ]
    if word:
        room = head_len - cap_w * 2 - 18
        cap = _fit(word, room, head_thk * 0.42, 900, 0.04)
        paths = [p for ps, _ in _word(word, 0, hy + head_thk * 0.04, cap, 900, 0.04) for p in ps]
        head_parts.append(part(*paths, fill=S.vgrad([(0, '#1f4fb2'), (1, '#0d1d45')], hy - cap / 2, hy + cap / 2),
                               name='head_word'))
    return handle_parts, head_parts, body


# ------------------------------------------------------------------ 002 emblem
@emoji(2, 'kronos_logo', '👑', 'Эмблема KRONOS', frames=180, still=0)
def e_kronos_logo(T):
    cx, cy, R, rim = 256, 258, 206, 24
    fr = R - rim
    disc = circle_path(cx, cy, R)
    medal = [
        part(disc, fill=S.vgrad(S.G_ICE, cy - R, cy + R), outline=S.OW, name='rim'),
        part(circle_path(cx, cy, fr), fill=S.rgrad([(0, '#3f7ee0'), (0.55, '#1d4aa6'), (1, '#0f2763')],
                                                   cx - 50, cy - 80, fr + 80), outline=(S.OUTLINE, 4), name='field'),
        part(circle_path(cx, cy, fr - 16), stroke=stroke(S.ICE_L, 4, o=55), name='frame'),
        part(_arc_band(cx, cy, R - 5, R - rim + 6, 196, 256), fill=S.WHITE, o=75, name='rim_gloss'),
        part(_arc_band(cx, cy, fr - 26, fr - 44, 200, 238), fill=S.WHITE, o=14, name='field_gloss'),
    ]
    # light running around the ring (trim offset 0..360 per loop is seamless)
    run = anim((0, 0, 'linear'), (T, 360))
    path = circle_path(cx, cy, R - rim / 2)
    shimmer = [part(path, stroke=stroke(S.WHITE, 18, o=28), trim=trim(0, 18, run), name='shimmer_wide'),
               part(path, stroke=stroke(S.WHITE, 8, o=95), trim=trim(5, 13, run), name='shimmer')]

    cap, ky = 172, 310
    kp = [p for ps, _ in _word('K', cx, ky, cap, 900, 0) for p in ps]
    k_land = 137
    letter = group(
        part(*_shift(kp, 0, 8), fill=S.OUTLINE, o=45, name='k_shadow'),
        part(*kp, fill=S.vgrad(S.G_ICE_SOFT, ky - cap / 2, ky + cap / 2), outline=8, name='k'),
        fx.shine(kp, T, t0=52, dur=44, angle=22, width=0.3, alpha=0.85),
        pivot=(cx, ky + cap / 2), s=_squash(T, k_land, k=4, dur=20), name='K')

    cw = 136
    ccy = ky - cap / 2 - 12 - 0.338 * cw
    crown_in, c = _crown_group(cx, ccy, cw, T, ow=5, pivot=(cx, ccy + 0.3 * cw), s=_squash(T, k_land, k=10, dur=18))
    crown_g = group(crown_in, fx.sparkles([(x, y - 2, 15) for x, y in c['tips']], T, start=k_land + 2, gap=6, dur=30),
                    pivot=(cx, ccy), move=_hop(T, k_land - 25, dy=-22, up=12, down=13), name='crown_hop')

    body = group(medal, shimmer, letter, crown_g, fx.shine([disc], T, t0=26, dur=60, angle=24, width=0.34, alpha=0.32),
                 pivot=(cx, cy), s=fx.breathe(T, 99, 101.5), name='medal')
    sparks = [fx.sparkle(398, 116, 30, T, t0=18, dur=44), fx.sparkle(112, 398, 22, T, t0=72, dur=40),
              fx.sparkle(430, 330, 16, T, t0=156, dur=30)]
    return [fx.glow(cx, cy, 236, alpha=0.32, s=fx.breathe(T, 92, 105)), body, sparks]


# ------------------------------------------------------------------ 003 wordmark
@emoji(3, 'kronos_text', '✨', 'Надпись KRONOS', frames=180, still=0)
def e_kronos_text(T):
    word, wt, tr = 'KRONOS', 800, 0.13
    cap = fit_cap(word, 450, 110, weight=wt, tracking=tr)
    ty = 364
    gl = _word(word, 256, ty, cap, wt, tr)
    allp = [p for ps, _ in gl for p in ps]
    bb = bbox_of(allp)
    letters = []
    for k, (paths, (gx, gy)) in enumerate(gl):
        t0 = 24 + k * 9
        wave = loop([(t0, [0, 0], 'out'), (t0 + 14, [0, -20], 'in'), (t0 + 30, [0, 0], 'linear'), (t0 + T, [0, 0])], T)
        s = loop([(t0, [100, 100], 'out'), (t0 + 14, [96, 106], 'in'), (t0 + 30, [104, 95], 'out'),
                  (t0 + 40, [100, 100], 'linear'), (t0 + T, [100, 100])], T)
        letters.append(group(
            part(*paths, fill=S.vgrad(S.G_ICE, ty - cap / 2, ty + cap / 2), outline=S.OW_THIN, name='glyph'),
            fx.shine(paths, T, t0=104, dur=46, angle=20, width=0.2, alpha=0.9, bbox=bb),
            pivot=(gx, ty + cap / 2), move=wave, s=s, name='letter'))

    cw = 220
    band_bottom = ty - cap / 2 - 26
    ccy = band_bottom - 0.338 * cw
    crown_g, c = _crown_group(256, ccy, cw, T, ow=7, spark_t0=118, spark_gap=12, spark_r=22,
                              pivot=(256, ccy + 0.3 * cw), r=fx.swing(T, 3), move=fx.bob(T, 10, cycles=2))
    k = cw / 420
    ly = ccy + (374 - 266) * k
    half = (442 - 256) * k + 27 * k + 16
    x_l, x_r = bb[0] + 12, bb[2] - 12
    lines = [polyline([(x_l, ly), (256 - half, ly)]), polyline([(256 + half, ly), (x_r, ly)])]
    gems = [rounded([(x - 13, ly), (x, ly - 13), (x + 13, ly), (x, ly + 13)], 3) for x in (x_l, x_r)]
    deco = [
        part(*lines, stroke=stroke(S.OUTLINE, 15), name='line_outline'),
        part(*lines, stroke=stroke(S.ICE, 6), name='lines'),
        part(*gems, fill=S.vgrad(S.G_ICE_SOFT, ly - 13, ly + 13), outline=(S.OUTLINE, 4), name='line_gems'),
    ]
    sparks = [fx.sparkle(x_l, ly, 22, T, t0=70, dur=36, halo=False), fx.sparkle(x_r, ly, 22, T, t0=150, dur=36, halo=False)]
    return [fx.glow(256, 300, 230, alpha=0.26, s=fx.breathe(T, 94, 104)), deco, letters, crown_g, sparks]


# ------------------------------------------------------------------ 004 STAFF
@emoji(4, 'staff_text', '💼', 'Надпись STAFF', frames=120, still=0)
def e_staff_text(T):
    cx, cy, w, h = 256, 334, 440, 166
    pill = _pill(cx, cy, w, h)
    wt, tr, sq = 900, 0.05, 0.92
    cap = _fit('STAFF', w - 66, 86, wt, tr, sq)
    ty = cy + 2
    badge = [
        part(pill, fill=S.vgrad(S.G_DEEP, cy - h / 2, cy + h / 2), outline=S.OW, name='pill'),
        part(_pill(cx, cy, w - 24, h - 24), stroke=stroke(S.ICE_L, 5, o=55), name='inner_rim'),
        part(_pill(cx, cy - h * 0.27, w - 130, h * 0.17), fill=S.WHITE, o=22, name='gloss'),
    ]
    letters = []
    for k, (paths, (gx, gy)) in enumerate(_word('STAFF', cx, ty, cap, wt, tr, sq)):
        letters.append(group(
            part(*_shift(paths, 0, 7), fill=S.OUTLINE, o=50, name='shadow'),
            part(*paths, fill=S.vgrad(G_LETTER, ty - cap / 2, ty + cap / 2), outline=(S.OUTLINE, 5), name='glyph'),
            pivot=(gx, ty + cap / 2), s=_pop(T, 14 + k * 5, peak=118, dur=26), name='letter'))
    cw = 196
    ccy = cy - h / 2 + 12 - 0.338 * cw
    land = 8 + 24
    crown_in, c = _crown_group(256, ccy, cw, T, ow=7, pivot=(256, ccy + 0.338 * cw), s=_squash(T, land, k=9, dur=18))
    crown_g = group(crown_in, fx.sparkles([(x, y, 20) for x, y in c['tips']], T, start=land + 6, gap=8, dur=32),
                    pivot=(256, ccy + 0.3 * cw), move=_hop(T, 8, dy=-24, up=12, down=12),
                    r=fx.swing(T, 3, cycles=2), name='crown_hop')
    body = group(badge, letters, fx.shine([pill], T, t0=54, dur=44, angle=22, width=0.26, alpha=0.5), crown_g,
                 fx.sparkle(cx + w / 2 - 30, cy - h / 2 + 22, 22, T, t0=88, dur=32),
                 pivot=(cx, cy), s=_pop(T, 4, peak=104, dur=28, under=99), move=fx.bob(T, 8), name='badge')
    return [fx.glow(256, 300, 228, alpha=0.26), body]


# ------------------------------------------------------------------ 005 ADMIN
@emoji(5, 'admin_text', '🛡', 'ADMIN', frames=120, still=0)
def e_admin_text(T):
    cx, cy, w, h = 256, 344, 440, 160
    pill = _pill(cx, cy, w, h)
    wt, tr, sq = 900, 0.04, 0.92
    cap = _fit('ADMIN', w - 64, 84, wt, tr, sq)
    ty = cy + 1
    badge = [
        part(pill, fill=S.vgrad(G_ROYAL, cy - h / 2, cy + h / 2), outline=S.OW, name='pill'),
        part(_pill(cx, cy, w - 24, h - 24), stroke=stroke(S.ICE_L, 5, o=55), name='inner_rim'),
        part(_pill(cx, cy - h * 0.27, w - 130, h * 0.16), fill=S.WHITE, o=22, name='gloss'),
    ]
    letters = []
    for k, (paths, (gx, gy)) in enumerate(_word('ADMIN', cx, ty, cap, wt, tr, sq)):
        letters.append(group(
            part(*_shift(paths, 0, 7), fill=S.OUTLINE, o=50, name='shadow'),
            part(*paths, fill=S.vgrad(G_LETTER, ty - cap / 2, ty + cap / 2), outline=(S.OUTLINE, 5), name='glyph'),
            pivot=(gx, ty + cap / 2), s=_pop(T, 30 + k * 5, peak=116, dur=26), name='letter'))
    # shield emblem with a star, overlapping the top of the pill
    sw, sh = 160, 186
    stop = cy - h / 2 + 18 - sh
    sparts, souter = _shield_parts(cx, stop, sw, sh, ow=8)
    scy = stop + sh * 0.43
    st = star(cx, scy, 5, 46, 20, round_out=5, round_in=3)
    twist = anim((0, 0, 'hold'), (10, 0, 'io'), (40, 72, 'hold'), (T, 72))   # 72 deg = one star period
    emblem = group(
        sparts,
        group(part(st, fill=S.rgrad([(0, S.WHITE), (0.7, S.ICE_L), (1, S.ICE)], cx, scy, 46), outline=(S.OUTLINE, 5),
                   name='star'), pivot=(cx, scy), r=twist, name='star_spin'),
        part(P(f'M {cx - sw * 0.36} {stop + sh * 0.12} C {cx - sw * 0.36} {stop + sh * 0.3} '
               f'{cx - sw * 0.32} {stop + sh * 0.45} {cx - sw * 0.2} {stop + sh * 0.62} '
               f'L {cx - sw * 0.28} {stop + sh * 0.6} C {cx - sw * 0.39} {stop + sh * 0.44} '
               f'{cx - sw * 0.42} {stop + sh * 0.3} {cx - sw * 0.42} {stop + sh * 0.12} Z'),
             fill=S.WHITE, o=60, name='shield_gloss'),
        fx.shine([souter], T, t0=12, dur=30, angle=24, width=0.34, alpha=0.7),
        pivot=(cx, stop + sh * 0.5), s=_pop(T, 8, peak=114, dur=30), name='emblem')
    ring = fx.ring_pulse(cx, scy, 60, 168, T, t0=14, dur=40, w0=12, alpha=70)
    sparks = fx.sparkles([(cx - sw / 2 - 26, stop + 30, 22), (cx + sw / 2 + 30, stop + 70, 18)], T, start=26, gap=12, dur=34)
    body = group(badge, letters, fx.shine([pill], T, t0=62, dur=44, angle=22, width=0.26, alpha=0.5), emblem,
                 fx.sparkle(cx + w / 2 - 30, cy - h / 2 + 22, 22, T, t0=96, dur=30),
                 pivot=(cx, cy), move=fx.bob(T, 8), name='badge')
    return [fx.glow(256, 300, 228, alpha=0.26), ring, body, sparks]


# ------------------------------------------------------------------ 006 MOD
@emoji(6, 'mod_text', '🔨', 'MOD', frames=120, still=0)
def e_mod_text(T):
    bx, by, bw, bh = 226, 346, 388, 180
    box = _box(bx, by, bw, bh, 58)
    wt, tr = 900, 0.04
    cap = _fit('MOD', bw - 64, 104, wt, tr)
    ty = by + 2
    t_hits = (20, 36)
    badge = [
        part(box, fill=S.vgrad(G_CYAN, by - bh / 2, by + bh / 2), outline=S.OW, name='badge'),
        part(_box(bx, by, bw - 24, bh - 24, 46), stroke=stroke(S.ICE_L, 5, o=55), name='inner_rim'),
        part(_box(bx, by - bh * 0.3, bw - 120, bh * 0.13, bh * 0.065), fill=S.WHITE, o=24, name='gloss'),
    ]
    letters = []
    for k, (paths, (gx, gy)) in enumerate(_word('MOD', bx, ty, cap, wt, tr)):
        jig = loop([(t_hits[0], [0, 0], 'out'), (t_hits[0] + 5, [0, -6 - 3 * k], 'in'), (t_hits[0] + 12, [0, 0], 'out'),
                    (t_hits[1] + 5, [0, -8 - 3 * k], 'in'), (t_hits[1] + 13, [0, 0], 'linear'), (t_hits[0] + T, [0, 0])], T)
        letters.append(group(
            part(*_shift(paths, 0, 7), fill=S.OUTLINE, o=50, name='shadow'),
            part(*paths, fill=S.vgrad(G_LETTER, ty - cap / 2, ty + cap / 2), outline=(S.OUTLINE, 6), name='glyph'),
            pivot=(gx, ty + cap / 2), move=jig, name='letter'))
    squash = loop([(t_hits[0], [100, 100], 'out'), (t_hits[0] + 4, [103, 95], 'io'), (t_hits[0] + 12, [100, 100], 'out'),
                   (t_hits[1], [100, 100], 'out'), (t_hits[1] + 4, [104, 94], 'io'), (t_hits[1] + 16, [100, 100], 'linear'),
                   (t_hits[0] + T, [100, 100])], T)
    badge_g = group(badge, letters, fx.shine([box], T, t0=64, dur=40, angle=22, width=0.26, alpha=0.5),
                    pivot=(bx, by + bh / 2), s=squash, name='badge')

    # hammer: grip G, handle horizontal at impact (rot -90), head's lower face hits the badge top
    L, hl, ht = 112, 134, 78
    G = (444, by - bh / 2 - hl / 2 + 2)
    contact = (G[0] - L, by - bh / 2)
    handle, head, _ = _hammer(L, hl, ht, 28, ow=7)
    rot = anim((0, -52, 'io'), (12, -42, 'in'), (t_hits[0], -90, 'out'), (t_hits[0] + 7, -70, 'in'),
               (t_hits[1], -90, 'out'), (t_hits[1] + 12, -62, 'io'), (72, -52, 'io'), (T, -52))
    hammer = group(handle, head, pivot=(0, 0), pos=G, r=rot, name='hammer')
    fx_hits = []
    for n, th in enumerate(t_hits):
        fx_hits += _fan(contact[0], contact[1] - 6, T, th, 6, 14, 92 + 14 * n, -165, -15, size=15, dur=24, seed=11 + n)
        fx_hits.append(fx.sparkle(contact[0], contact[1] - 4, 30 + 8 * n, T, t0=th - 2, dur=16, turn=0, halo=False))
    return [fx.glow(240, 300, 226, alpha=0.24), badge_g, fx_hits, hammer]


# ------------------------------------------------------------------ 007 VIP
def _diamond(cx, top, w, h):
    """Brilliant-cut gem, front view. Returns (outline path, [(facet, colour)], points)."""
    gy, bot = top + h * 0.3, top + h
    tw = w * 0.56
    A, B = (cx - tw / 2, top), (cx + tw / 2, top)
    Ca, Cb = (cx - tw / 6, top), (cx + tw / 6, top)
    L, R = (cx - w / 2, gy), (cx + w / 2, gy)
    G1, G2, G3 = (cx - w / 4, gy), (cx, gy), (cx + w / 4, gy)
    D = (cx, bot)
    sil = rounded([A, B, R, D, L], [10, 10, 8, 10, 8])
    tri = lambda *p: Bez(list(p))
    facets = [
        (tri(A, L, G1), '#cfeaff'), (tri(A, G1, Ca), '#ffffff'), (tri(Ca, G1, G2), '#a9d6ff'),
        (tri(Ca, G2, Cb), '#e6f5ff'), (tri(Cb, G2, G3), '#8cc6ff'), (tri(Cb, G3, B), '#cdeaff'),
        (tri(B, G3, R), '#6fb2ff'),
        (tri(L, G1, D), '#86c4ff'), (tri(G1, G2, D), '#4a8ff0'), (tri(G2, G3, D), '#2a66d8'),
        (tri(G3, R, D), '#1b44a6'),
    ]
    return sil, facets, {'A': A, 'B': B, 'L': L, 'R': R, 'D': D, 'gy': gy}


@emoji(7, 'vip_text', '💎', 'VIP', frames=120, still=0)
def e_vip_text(T):
    wt, tr = 900, 0.05
    cap = _fit('VIP', 432, 156, wt, tr)
    ty = 364
    gl = _word('VIP', 256, ty, cap, wt, tr)
    bb = bbox_of([p for ps, _ in gl for p in ps])
    letters = []
    for k, (paths, (gx, gy)) in enumerate(gl):
        t0 = 40 + k * 6
        letters.append(group(
            part(*paths, fill=S.vgrad(S.G_ICE, ty - cap / 2, ty + cap / 2), outline=10, name='glyph'),
            fx.shine(paths, T, t0=58 + k * 9, dur=36, alpha=0.85, width=0.3, bbox=bb),
            pivot=(gx, ty + cap / 2), move=_hop(T, t0, dy=-18, up=10, down=11),
            s=_squash(T, t0 + 21, k=6, dur=16), name='letter'))
    dw, dh = 236, 168
    dtop = ty - cap / 2 - 30 - dh
    sil, facets, pts = _diamond(256, dtop, dw, dh)
    dcy = dtop + dh * 0.45
    gem = [part(sil, fill=S.SKY, outline=S.OW, name='gem_base')]
    gem += [part(f, fill=c, name='facet') for f, c in facets]
    gem += [
        part(*[Bez([a, b], closed=False) for a, b in ((pts['L'], pts['R']),)], stroke=stroke(S.WHITE, 3, o=55), name='girdle'),
        part(P(f'M {pts["A"][0] + 14} {dtop + 10} L {pts["A"][0] + 44} {dtop + 10} L {pts["A"][0] + 20} {pts["gy"] - 8} Z'),
             fill=S.WHITE, o=80, name='glint'),
        fx.shine([sil], T, t0=26, dur=34, angle=28, width=0.34, alpha=0.9),
    ]
    sparks = fx.sparkles([(pts['A'][0] - 6, dtop + 4, 24), (pts['R'][0] + 4, pts['gy'] + 2, 20),
                          (pts['B'][0] + 10, dtop - 6, 16)], T, start=24, gap=14, dur=34)
    burst = fx.burst(256, dcy, T, 20, 8, 40, 128, size=13, color=S.ICE_L, dur=30, rot=22, shape='spark', seed=4)
    diamond = group(gem, pivot=(256, dcy), s=_pop(T, 16, peak=112, dur=30), name='diamond')
    diamond_g = group(burst, diamond, sparks, pivot=(256, dcy), move=fx.bob(T, 12), r=fx.swing(T, 4), name='diamond_float')
    return [fx.glow(256, 250, 232, alpha=0.3, s=fx.breathe(T, 94, 104)), letters, diamond_g]


# ------------------------------------------------------------------ 008 verified rosette
@emoji(8, 'verified', '✔️', 'Подтверждено', frames=180, still=0)
def e_verified(T):
    cx, cy, R, A, n = 256, 256, 194, 17, 12
    ros = _rosette(cx, cy, R, A, n)
    inner_r = R - A - 22
    # everything in the rotating group is rotation-invariant except the scallop outline itself
    spinning = group(
        part(ros, fill=S.rgrad([(0, '#79bdff'), (0.55, '#3b82ee'), (1, '#1d4cb8')], cx, cy, R + A), outline=S.OW,
             name='rosette'),
        part(circle_path(cx, cy, inner_r), stroke=stroke(S.ICE_L, 5, o=45), name='inner_rim'),
        pivot=(cx, cy), r=fx.spin(T, 1 / n), name='spin')
    disc = circle_path(cx, cy, R - A)
    deco = [
        part(_arc_band(cx, cy, inner_r - 14, inner_r - 36, 198, 252), fill=S.WHITE, o=55, name='gloss'),
        part(_arc_band(cx, cy, inner_r - 12, inner_r - 30, 20, 80), fill=S.OUTLINE, o=16, name='shade'),
    ]
    mark = polyline([(166, 262), (230, 324), (350, 200)])
    pop = loop([(16, [100, 100], 'out'), (24, [118, 118], 'io'), (34, [95, 95], 'io'), (44, [100, 100], 'linear'),
                (16 + T, [100, 100])], T)
    tick = group(part(mark.translate(0, 12), stroke=stroke(S.NAVY_D, 54, o=40), name='tick_shadow'),
                 part(mark, stroke=stroke(S.WHITE, 54), name='tick'),
                 pivot=(cx, cy + 10), s=pop, name='check')
    body = group(spinning, deco, fx.shine([disc], T, t0=60, dur=50, angle=22, width=0.3, alpha=0.4), tick,
                 pivot=(cx, cy), s=fx.breathe(T, 98.5, 101.5), name='badge')
    ring = fx.ring_pulse(cx, cy, R - 10, R + 42, T, t0=22, dur=40, w0=14)
    sparks = fx.sparkles([(404, 112, 28), (112, 396, 22), (424, 360, 16)], T, start=30, gap=11, dur=36)
    return [fx.glow(cx, cy, 234, alpha=0.32, s=fx.breathe(T, 92, 104)), ring, body, sparks]


# ------------------------------------------------------------------ 009 staff shield
@emoji(9, 'shield', '🛡', 'Щит стаффа', frames=180, still=0)
def e_shield(T):
    cx, top, w, h = 256, 62, 352, 404
    sparts, outer = _shield_parts(cx, top, w, h, ow=S.OW, rim=24)
    c = crown(cx, 258, 232, ow=7)
    gloss = part(P(f'M {cx - w / 2 + 12} {top + 44} C {cx - w / 2 + 12} {top + 120} {cx - w / 2 + 18} {top + 180} '
                   f'{cx - w / 2 + 40} {top + 250} L {cx - w / 2 + 28} {top + 250} C {cx - w / 2 + 8} {top + 180} '
                   f'{cx - w / 2 + 4} {top + 120} {cx - w / 2 + 4} {top + 44} Z'), fill=S.WHITE, o=70, name='rim_gloss')
    crown_g = group(c['parts'], fx.shine(c['shine'], T, t0=58, dur=40, angle=24, width=0.3, alpha=0.8),
                    pivot=(cx, 300), s=_pop(T, 96, peak=108, dur=30, under=98), name='crown')
    sparks = [fx.sparkle(c['gem'][0] + 26, c['gem'][1] - 12, 20, T, t0=112, dur=32),
              fx.sparkle(c['tips'][1][0], c['tips'][1][1] - 4, 22, T, t0=104, dur=34)]
    body = group(sparts, gloss, crown_g, sparks,
                 fx.shine([outer], T, t0=40, dur=56, angle=24, width=0.3, alpha=0.55),
                 pivot=(cx, 150), r=fx.swing(T, 3), move=fx.bob(T, 10), name='shield')
    corner = [fx.sparkle(cx - w / 2 + 6, top + 6, 26, T, t0=20, dur=40),
              fx.sparkle(cx + w / 2 - 4, top + 150, 18, T, t0=64, dur=34),
              fx.sparkle(cx + 30, top + h - 4, 18, T, t0=146, dur=32)]
    return [fx.glow(cx, 262, 236, alpha=0.3, s=fx.breathe(T, 92, 104)), body, corner]


# ------------------------------------------------------------------ 010 ban hammer
@emoji(10, 'ban_hammer', '🔨', 'Бан-молот', frames=120, still=0)
def e_ban_hammer(T):
    L, hl, ht, hw = 200, 214, 116, 40
    G = (382, 318)
    t_imp = 40
    contact = (G[0] - L, G[1] + hl / 2)                  # left face of the head at rot = -90
    handle, head, _ = _hammer(L, hl, ht, hw, ow=S.OW, word='BAN')
    head_sq = loop([(t_imp, [100, 100], 'out'), (t_imp + 4, [90, 108], 'io'), (t_imp + 16, [100, 100], 'linear'),
                    (t_imp + T, [100, 100])], T)
    rot = anim((0, -35, 'io'), (28, -23, 'in'), (t_imp, -90, 'out'), (t_imp + 7, -81, 'in'), (t_imp + 13, -90, 'io'),
               (66, -90, 'io'), (100, -35, 'io'), (T, -35))
    hammer = group(handle, group(head, pivot=(-hl / 2, -L), s=head_sq, name='head_sq'),
                   pivot=(0, 0), pos=G, r=rot, name='hammer')
    # sound block the gavel strikes
    bx, bw, bh = contact[0], 176, 46
    bcy = contact[1] + bh / 2 + 2
    block = _box(bx, bcy, bw, bh, 18)
    block_sq = loop([(t_imp, [100, 100], 'out'), (t_imp + 4, [108, 86], 'io'), (t_imp + 18, [100, 100], 'linear'),
                     (t_imp + T, [100, 100])], T)
    block_g = group(part(block, fill=S.vgrad(S.G_DEEP, bcy - bh / 2, bcy + bh / 2), outline=S.OW, name='block'),
                    part(_box(bx, bcy - bh * 0.22, bw - 40, bh * 0.18, bh * 0.09), fill=S.WHITE, o=50, name='block_gloss'),
                    pivot=(bx, bcy + bh / 2), s=block_sq, name='block')
    hit = [
        _flat_ring(bx, contact[1] + 4, 60, 330, 0.3, T, t_imp, dur=30, sw0=14),
        fx.sparkle(contact[0], contact[1] - 8, 52, T, t0=t_imp - 1, dur=16, turn=0, halo=True),
        _fan(contact[0], contact[1] - 10, T, t_imp, 9, 20, 150, -172, -8, size=20, dur=30, seed=21),
        _fan(contact[0], contact[1] - 10, T, t_imp + 2, 7, 16, 110, -160, -20, size=12, color=S.ICE, dur=26,
             seed=8, shape='dot'),
    ]
    shake = fx.wobble(T, t_imp, 16, 5, n=2, vector=(0, 1))
    return [fx.glow(256, 280, 232, alpha=0.26), group(block_g, hit, hammer, move=shake, name='scene')]
