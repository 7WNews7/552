"""043-060: tools, moderation and community actions."""
import math
import random

from kit.registry import emoji
from kit.lottie import EASE, part, group, anim, loop, stroke, trim, ellipse
from kit.geometry import P, Bez, rounded, star, circle_path, heart_path, sparkle_path, line, polyline, morph
from kit.text import glyphs, fit_cap
from kit.motifs import crown, paw
from kit import fx, style as S

G_VIVID = [(0, '#bfe4ff'), (0.45, '#4d9cf5'), (1, '#1a40a0')]


# ------------------------------------------------------------- helpers
def _arc(cx, cy, r, a0, a1):
    """Open circular arc from a0 to a1 degrees (0 = right, 90 = down)."""
    n = max(1, int(math.ceil(abs(a1 - a0) / 90.0)))
    d = (a1 - a0) / n
    k = 4.0 / 3.0 * math.tan(math.radians(d) / 4) * r
    b = Bez(closed=False)
    for j in range(n + 1):
        a = math.radians(a0 + d * j)
        tx, ty = -math.sin(a), math.cos(a)
        b.add((cx + r * math.cos(a), cy + r * math.sin(a)), (-tx * k, -ty * k), (tx * k, ty * k))
    return b


def _lines(paths, w, color=S.ICE_L, ow=S.OW_THIN, o=None, tr=None, name='lines'):
    """Solid strokes with a navy contour behind them (gradient strokes are forbidden)."""
    return part(paths, stroke=stroke(color, w), outline=(S.OUTLINE, w / 2.0 + ow), o=o, trim=tr, name=name)


def _seq(T, starts, shape, rest):
    """Value resting at `rest` that plays `shape` = [(dt, value, ease)] at every start.
    shape must begin with (0, rest, ease) and end with (d, rest, 'hold')."""
    starts = sorted(starts)
    keys = []
    for t0 in starts:
        keys += [(t0 + dt, v, e) for dt, v, e in shape]
    keys.append((starts[0] + T, rest))
    return loop(keys, T)


def _blink_o(T, starts, dur, peak=100, rise=0.3):
    """Opacity flash 0 -> peak -> 0 at every start."""
    return _seq(T, starts, [(0, 0, 'out'), (dur * rise, peak, 'in'), (dur, 0, 'hold')], 0)


def _shadow(cx, cy, w, h, o=26, s=None, name='shadow'):
    return part(ellipse(cx, cy, w, h), fill=S.NAVY_D, o=o, pivot=(cx, cy), s=s, name=name)


def _xf(deg, ox, oy, k=1.0):
    """Local design (origin at 0, 0) -> canvas: scale k, rotate deg (clockwise), move to (ox, oy)."""
    return lambda b: b.scale(k).rotate(deg).translate(ox, oy)


# ------------------------------------------------------------- 043 bell
@emoji(43, 'bell', '🔔', 'Колокольчик', frames=120, still=30)
def e_bell(T):
    pv = (256, 64)
    body = P('M 256 84 C 318 84 352 128 354 188 C 356 250 362 306 410 340 '
             'C 428 352 432 372 420 380 L 92 380 C 80 372 84 352 102 340 '
             'C 150 306 156 250 158 188 C 160 128 194 84 256 84 Z')
    lip = rounded([(84, 352), (428, 352), (428, 402), (84, 402)], 25)
    cap = P('M 150 158 C 144 110 194 72 256 72 C 318 72 368 110 362 158 '
            'C 360 172 344 176 334 166 C 326 174 318 178 310 172 '
            'C 308 190 300 206 291 206 C 281 206 277 192 278 177 '
            'C 262 183 244 183 230 177 C 228 187 222 196 214 196 '
            'C 204 196 199 186 200 175 C 186 179 170 177 162 169 '
            'C 157 166 151 164 150 158 Z')
    ring = [circle_path(256, 58, 25), circle_path(256, 58, 12).reversed()]
    clapper = group(
        part(circle_path(256, 412, 36), fill=S.vgrad(S.G_DEEP, 376, 448), outline=S.OW, name='ball'),
        part(circle_path(243, 399, 10), fill=S.WHITE, o=80, name='ball_glint'),
        pivot=pv, r=fx.swing(T, 13, cycles=2, shift=7), name='clapper')
    bell = group(
        part(*ring, fill=S.vgrad(S.G_SILVER, 33, 83), outline=S.OW_THIN, name='hanger'),
        part(body, fill=S.vgrad(S.G_ICE, 96, 384), outline=S.OW, name='body'),
        fx.shine([body], T, t0=34, dur=40, angle=24, alpha=0.55, width=0.26),
        part(P('M 186 208 C 184 258 176 300 136 338 L 160 338 C 198 302 206 258 205 208 Z'),
             fill=S.WHITE, o=62, name='gloss'),
        part(P('M 330 214 C 332 262 342 304 388 340 L 404 340 C 362 304 350 262 348 214 Z'),
             fill=S.NAVY, o=22, name='shade'),
        part(lip, fill=S.vgrad(S.G_DEEP, 352, 402), outline=S.OW, name='lip'),
        part(rounded([(112, 361), (400, 361), (400, 368), (112, 368)], 3.5), fill=S.WHITE, o=45, name='lip_gloss'),
        part(cap, fill=S.vgrad(S.G_SNOW, 72, 206), outline=S.OW, name='cap'),
        part(P('M 176 136 C 184 108 210 90 240 86 C 216 98 198 116 192 140 Z'), fill=S.WHITE, o=90, name='cap_gloss'),
        fx.sparkle(326, 98, 17, T, t0=70, dur=34),
        pivot=pv, r=fx.swing(T, 9, cycles=2), name='bell')
    # clapper hits the wall a few frames after each extreme: left at 20/80, right at 50/110
    arcs = []
    for side, starts in ((-1, (19, 79)), (1, (49, 109))):
        a0, a1 = (200, 238) if side < 0 else (302, 340)
        for k, r in enumerate((168, 208)):
            st = [t + 5 * k for t in starts]
            arcs.append(group(_lines([_arc(256, 210, r, a0, a1)], 18, S.ICE_L), pivot=(256, 210),
                              s=_seq(T, st, [(0, 78, 'out'), (24, 100, 'hold'), (25, 78, 'hold')], 78),
                              o=_seq(T, st, [(0, 0, 'out'), (6, 100, 'linear'), (13, 100, 'in'), (24, 0, 'hold')], 0),
                              name='sound_arc'))
    sparks = fx.sparkles([(446, 436, 22), (66, 438, 18)], T, start=40, gap=50, dur=36)
    return [fx.glow(256, 250, 228, alpha=0.3), arcs, clapper, bell, sparks]


# ------------------------------------------------------------- 044 megaphone
@emoji(44, 'megaphone', '📢', 'Объявление', frames=120, still=16)
def e_megaphone(T):
    tilt = -14
    mouth = (304, 256)
    cap = rounded([(40, 208), (102, 208), (102, 304), (40, 304)], 20)
    horn = rounded([(92, 222), (302, 110), (302, 402), (92, 290)], [12, 4, 4, 12])
    band = rounded([(128, 203), (152, 190), (152, 322), (128, 309)], 3)
    handle = rounded([(150, 296), (196, 296), (208, 404), (162, 404)], 20)
    rim = circle_path(302, 256, 44, 148)
    hole = circle_path(310, 256, 29, 124)
    c = crown(208, 262, 94, ow=4, gems=False)
    shouts = (4, 64)
    body = group(
        part(handle, fill=S.vgrad(S.G_DEEP, 296, 404), outline=S.OW, name='handle'),
        part(rounded([(166, 330), (176, 330), (184, 392), (174, 392)], 5), fill=S.WHITE, o=40, name='handle_gloss'),
        part(cap, fill=S.vgrad(S.G_DEEP, 208, 304), outline=S.OW, name='cap'),
        part(horn, fill=S.vgrad(S.G_ICE, 110, 402), outline=S.OW, name='horn'),
        fx.shine([horn], T, t0=78, dur=36, angle=-60, alpha=0.5),
        part(P('M 112 222 L 290 128 L 292 146 L 116 236 Z'), fill=S.WHITE, o=60, name='horn_gloss'),
        part(band, fill=S.vgrad(S.G_DEEP, 190, 322), outline=S.OW_THIN, name='band'),
        c['parts'],
        part(rim, fill=S.vgrad(S.G_ICE_SOFT, 108, 404), outline=S.OW, name='rim'),
        part(hole, fill=S.vgrad([(0, S.NAVY_D), (1, S.BLUE_D)], 132, 380), name='hole'),
        part(P('M 296 150 C 300 132 306 122 312 120 C 306 140 304 160 304 180 Z'), fill=S.WHITE, o=70, name='rim_gloss'),
        pivot=(180, 280),
        move=_seq(T, shouts, [(0, [0, 0], 'out'), (4, [-16, 0], 'io'), (18, [0, 0], 'hold')], [0, 0]),
        s=_seq(T, shouts, [(0, 100, 'out'), (4, 108, 'outback'), (20, 100, 'hold')], 100),
        r=_seq(T, shouts, [(0, 0, 'out'), (4, -5, 'sine'), (11, 4, 'sine'), (18, -2, 'sine'), (26, 0, 'hold')], 0),
        name='megaphone')
    waves = []
    for k, r in enumerate((92, 132, 172)):
        st = [t + 3 + 7 * k for t in shouts]
        span = 26 + 3 * k
        waves.append(group(_lines([_arc(mouth[0], mouth[1], r, -span, span)], 18, S.ICE_L), pivot=mouth,
                           s=_seq(T, st, [(0, 72, 'out'), (30, 100, 'hold'), (31, 72, 'hold')], 72),
                           o=_seq(T, st, [(0, 0, 'out'), (6, 100, 'linear'), (16, 100, 'in'), (30, 0, 'hold')], 0),
                           name='wave'))
    tilted = group(waves, body, pivot=(256, 256), r=tilt, move=fx.bob(T, 8, cycles=2, shift=20))
    sparks = fx.sparkles([(124, 120, 24), (420, 404, 20)], T, start=30, gap=56, dur=36)
    return [fx.glow(250, 262, 222, alpha=0.28), tilted, sparks]


# ------------------------------------------------------------- 045 pin
@emoji(45, 'pin', '📌', 'Закреп', frames=120, still=0)
def e_pin(T):
    tip = (120, 466)
    M = _xf(40, tip[0], tip[1], 1.06)
    needle = M(P('M 0 8 L 11 -172 L -11 -172 Z'))
    flange = M(rounded([(-104, -214), (104, -214), (104, -166), (-104, -166)], 24))
    neck = M(P('M -50 -206 C -38 -236 -38 -268 -46 -300 L 46 -300 C 38 -268 38 -236 50 -206 Z'))
    head = M(rounded([(-100, -392), (100, -392), (100, -296), (-100, -296)], 44))
    hb = head.bbox()
    pin = [
        part(needle, fill=S.vgrad(S.G_SILVER, 280, 470), outline=S.OW_THIN, name='needle'),
        part(M(P('M -3 -10 L 4 -150 L -1 -150 Z')), fill=S.WHITE, o=70, name='needle_gloss'),
        part(flange, fill=S.vgrad(S.G_DEEP, 230, 410), outline=S.OW, name='flange'),
        part(neck, fill=S.vgrad(S.G_ICE_SOFT, 170, 330), outline=S.OW, name='neck'),
        part(M(P('M -30 -212 C -22 -238 -22 -264 -28 -292 L -16 -292 C -10 -264 -10 -238 -18 -212 Z')),
             fill=S.WHITE, o=70, name='neck_gloss'),
        part(head, fill=S.vgrad(G_VIVID, hb[1], hb[3]), outline=S.OW, name='head'),
        fx.shine([head], T, t0=90, dur=30, angle=30, alpha=0.6, width=0.3),
        part(M(circle_path(-46, -364, 34, 13)), fill=S.WHITE, o=85, name='head_gloss'),
        part(M(circle_path(30, -370, 9, 6)), fill=S.WHITE, o=70, name='head_gloss_dot'),
        part(M(rounded([(-84, -306), (84, -306), (84, -300), (-84, -300)], 3)), fill=S.NAVY, o=30, name='head_shade'),
    ]
    t_up, t_top, t_land = 42, 60, 72
    lift = anim((0, [0, 0], 'hold'), (t_up, [0, 0], 'io'), (t_top, [0, -46], 'in'), (t_land, [0, 0], 'out'),
                (t_land + 8, [0, -12], 'in'), (t_land + 15, [0, 0], 'hold'), (T, [0, 0]))
    tilt = anim((0, 0, 'hold'), (t_up, 0, 'io'), (t_top, -7, 'in'), (t_land, 0, 'hold'), (T, 0))
    inner = group(pin, fx.sparkle(*M.__call__(Bez([(62, -388)])).v[0], 20, T, t0=10, dur=36),
                  pivot=tip, r=fx.wobble(T, t_land + 15, 30, 4, n=3), name='pin_wobble')
    pin_g = group(inner, pivot=tip, move=lift, r=tilt, name='pin')
    sh_s = anim((0, 100, 'hold'), (t_up, 100, 'io'), (t_top, 64, 'in'), (t_land, 100, 'out'),
                (t_land + 8, 86, 'in'), (t_land + 15, 100, 'hold'), (T, 100))
    shadow = _shadow(tip[0] + 8, tip[1] + 2, 104, 22, o=30, s=sh_s)
    ring = group(fx.ring_pulse(tip[0], tip[1], 16, 76, T, t0=t_land, dur=30, w0=10, w1=2),
                 pivot=tip, s=[100, 34], name='impact')
    sparks = fx.sparkles([(84, 120, 26), (440, 404, 22)], T, start=t_land + 2, gap=12, dur=36)
    return [fx.glow(290, 270, 214, alpha=0.28), shadow, ring, pin_g, sparks]


# ------------------------------------------------------------- 046 chat
@emoji(46, 'chat', '💬', 'Чат', frames=120, still=12)
def e_chat(T):
    bub = P('M 256 64 C 384 64 474 138 474 228 C 474 318 384 390 256 390 '
            'C 230 390 206 388 184 382 C 158 408 116 434 70 440 '
            'C 96 416 110 388 112 362 C 68 330 38 282 38 228 '
            'C 38 138 128 64 256 64 Z')
    dots = []
    for k, x in enumerate((166, 256, 346)):
        st = [6 + 9 * k, 66 + 9 * k]
        hop = _seq(T, st, [(0, [0, 0], 'sine'), (12, [0, -28], 'sine'), (26, [0, 0], 'hold')], [0, 0])
        sc = _seq(T, st, [(0, 100, 'sine'), (12, 114, 'sine'), (26, 100, 'hold')], 100)
        dots.append(group(
            part(circle_path(x, 230, 32), fill=S.vgrad(S.G_DEEP, 198, 262), outline=S.OW_THIN, name='dot'),
            part(circle_path(x, 230, 32), fill=S.WHITE, o=_seq(T, st, [(0, 0, 'sine'), (12, 38, 'sine'), (26, 0, 'hold')], 0),
                 name='dot_flash'),
            part(circle_path(x - 10, 219, 9), fill=S.WHITE, o=80, name='dot_glint'),
            pivot=(x, 230), move=hop, s=sc, name='typing_dot'))
    bubble = group(
        part(bub, fill=S.vgrad(S.G_ICE, 64, 440), outline=S.OW, name='bubble'),
        fx.shine([bub], T, t0=88, dur=32, angle=24, alpha=0.5, width=0.24),
        part(P('M 90 178 C 108 124 166 90 234 86 C 182 104 136 136 114 190 Z'), fill=S.WHITE, o=78, name='gloss'),
        part(circle_path(80, 214, 11), fill=S.WHITE, o=70, name='gloss_dot'),
        dots,
        pivot=(256, 400), move=fx.bob(T, 10, cycles=2), s=fx.breathe(T, 99, 102, cycles=2), name='chat')
    sparks = fx.sparkles([(436, 86, 26), (470, 388, 18)], T, start=20, gap=50, dur=38)
    return [fx.glow(256, 240, 226, alpha=0.3), bubble, sparks]


# ------------------------------------------------------------- 047 lock
@emoji(47, 'lock', '🔒', 'Замок', frames=120, still=0)
def e_lock(T):
    body = rounded([(100, 236), (412, 236), (412, 464), (100, 464)], 48)
    shackle = P('M 148 340 L 148 190 A 108 108 0 0 1 364 190 L 364 238 A 23 23 0 0 1 318 238 '
                'L 318 190 A 62 62 0 0 0 194 190 L 194 340 Z')
    keyhole = [circle_path(256, 322, 17), P('M 248 328 L 264 328 L 272 372 L 240 372 Z')]
    t_open, t_shut = 18, 66
    lift = anim((0, [0, 0], 'hold'), (t_open, [0, 0], 'outback'), (t_open + 14, [0, -52], 'io'),
                (t_shut - 14, [0, -46], 'io'), (t_shut - 7, [0, -54], 'in'), (t_shut, [0, 0], 'hold'), (T, [0, 0]))
    sh = group(
        part(shackle, fill=S.vgrad(S.G_SILVER, 82, 300), outline=S.OW, name='shackle'),
        part(P('M 160 300 L 160 192 C 160 150 184 112 222 98 C 196 122 176 156 176 194 L 176 300 Z'),
             fill=S.WHITE, o=75, name='shackle_gloss'),
        pivot=(256, 236), move=lift, name='shackle_g')
    squash = _seq(T, [t_shut], [(0, [100, 100], 'out'), (4, [105, 94], 'outback'), (16, [100, 100], 'hold')], [100, 100])
    jolt = fx.wobble(T, t_open, 22, 3, n=2)
    lock_body = group(
        part(body, fill=S.vgrad([(0, '#86caff'), (0.5, '#2f74e6'), (1, '#173e9e')], 236, 464), outline=S.OW, name='body'),
        fx.shine([body], T, t0=76, dur=34, angle=24, alpha=0.5, width=0.26),
        part(P('M 124 380 L 124 290 C 124 266 138 254 164 254 L 280 254 L 280 268 L 168 268 '
               'C 150 268 140 278 140 296 L 140 380 Z'), fill=S.WHITE, o=55, name='gloss'),
        part(circle_path(256, 334, 48), fill=S.vgrad(S.G_ICE_SOFT, 286, 382), outline=S.OW_THIN, name='plate'),
        part(*keyhole, fill=S.vgrad([(0, S.NAVY), (1, S.OUTLINE)], 305, 372), name='keyhole'),
        part(circle_path(240, 304, 8), fill=S.WHITE, o=80, name='plate_glint'),
        pivot=(256, 464), s=squash, r=jolt, name='lock_body')
    clicks = []
    for x in (171, 341):
        clicks += fx.burst(x, 232, T, t_shut, 4, 8, 44, size=16, shape='spark', dur=24, rot=-135 if x < 256 else -45,
                           seed=x)
    glint = fx.sparkle(280, 314, 30, T, t0=t_shut + 6, dur=34)
    lock = group(sh, lock_body, clicks, glint, pivot=(256, 464), move=fx.bob(T, 8, shift=30), name='lock')
    sparks = fx.sparkles([(438, 120, 24), (74, 196, 18)], T, start=t_open + 16, gap=14, dur=34)
    return [fx.glow(256, 300, 214, alpha=0.3), lock, sparks]


# ------------------------------------------------------------- 048 hourglass
def _cubic_pts(p0, c1, c2, p3, n=24):
    out = []
    for j in range(n + 1):
        u = j / n
        a, b, c, d = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u * u, u ** 3
        out.append((a * p0[0] + b * c1[0] + c * c2[0] + d * p3[0], a * p0[1] + b * c1[1] + c * c2[1] + d * p3[1]))
    return out


def _area(b):
    v = b.v
    return abs(sum(v[k][0] * v[k - 1][1] - v[k - 1][0] * v[k][1] for k in range(len(v)))) / 2


def _bisect(fn, target, lo, hi, it=40):
    """x in [lo, hi] with fn(x) == target for monotonic fn."""
    inc = fn(hi) > fn(lo)
    for _ in range(it):
        mid = (lo + hi) / 2
        if (fn(mid) < target) == inc:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


@emoji(48, 'hourglass', '⏳', 'Ожидание', frames=180, still=60)
def e_hourglass(T):
    glass = P('M 164 96 L 348 96 C 362 120 364 168 346 200 C 328 230 282 244 270 256 '
              'C 282 268 328 282 346 312 C 364 344 362 392 348 416 L 164 416 '
              'C 150 392 148 344 166 312 C 184 282 230 268 242 256 '
              'C 230 244 184 230 166 200 C 148 168 150 120 164 96 Z')
    wall = _cubic_pts((348, 96), (362, 120), (364, 168), (346, 200)) + \
        _cubic_pts((346, 200), (328, 230), (282, 244), (270, 256))[1:]

    def xr(y):  # right wall of the top bulb (y in 96..256)
        for (xa, ya), (xb, yb) in zip(wall, wall[1:]):
            if ya <= y <= yb:
                return xa + (xb - xa) * (y - ya) / (yb - ya) if yb > ya else xb
        return wall[-1][0] if y > 200 else wall[0][0]

    n, ins = 9, 2

    # every sand shape: [left wall going down], bottom-mid, [right wall going up], top-mid
    def top_sand(L, dip=9):
        ys = [L + (256 - L) * j / n for j in range(n + 1)]
        return Bez([(512 - xr(y) + ins, y) for y in ys] + [(256, 258)] +
                   [(xr(y) - ins, y) for y in reversed(ys)] + [(256, min(L + dip, 256))])

    def bottom_sand(s):
        h = min(24.0, 0.45 * (416 - s))
        ys = [s + (416 - s) * j / n for j in range(n + 1)]
        return Bez([(512 - xr(512 - y) + ins, y) for y in ys] + [(256, 416)] +
                   [(xr(512 - y) - ins, y) for y in reversed(ys)] + [(256, s - h)])

    L0, t_flow, t_flip, steps = 138, 132, 166, 12
    A0 = _area(top_sand(L0))
    top_keys, bot_keys, stream_keys = [], [], []
    for k in range(steps + 1):
        t = t_flow * k / steps
        left = A0 * (1 - k / steps)
        L = 256.0 if k == steps else _bisect(lambda y: _area(top_sand(y)), left, L0, 256)
        s = 416.0 if k == 0 else _bisect(lambda y: _area(bottom_sand(y)), A0 - left, 262, 416)
        tb, bb = top_sand(L), bottom_sand(s)
        top_keys.append((t, tb, 'linear'))
        bot_keys.append((t, bb, 'linear'))
        stream_keys.append((t, Bez([(256, 250), (256, bb.v[-1][1] + 4)], closed=False), 'linear'))
    full_rot = top_sand(L0).rotate(180, 256, 256)
    full_rot = Bez(full_rot.v[n + 2:] + full_rot.v[:n + 2])
    top_keys[-1] = (t_flow, top_keys[-1][1], 'hold')
    top_keys.append((T, top_sand(L0)))
    bot_keys[-1] = (t_flow, bot_keys[-1][1], 'io')
    bot_keys += [(t_flip, full_rot, 'hold'), (T, bottom_sand(416))]
    stream_keys[-1] = (t_flow, stream_keys[-1][1], 'hold')
    stream_keys.append((T, stream_keys[0][1]))
    stream_o = anim((0, 0, 'linear'), (5, 100, 'hold'), (t_flow - 8, 100, 'linear'), (t_flow, 0, 'hold'), (T, 0))

    plate = rounded([(128, 56), (384, 56), (384, 98), (128, 98)], 18)
    plates = [plate, plate.rotate(180, 256, 256)]
    plate_gloss = rounded([(150, 72), (362, 72), (362, 79), (150, 79)], 3.5)
    posts = [rounded([(140, 92), (156, 92), (156, 420), (140, 420)], 8)]
    posts.append(posts[0].rotate(180, 256, 256))
    hl = P('M 186 118 C 176 146 178 176 194 200 L 204 194 C 190 172 188 148 196 122 Z')
    # every element is point-symmetric (or comes in rotated pairs) so the 180-degree flip
    # ends on a frame identical to frame 0
    hg = group(
        part(*posts, fill=S.SILVER, outline=S.OW_THIN, name='posts'),
        part(glass, fill=S.rgrad([(0, S.BLUE_D), (1, S.NAVY_D)], 256, 256, 190, opacity=[(0, 0.5), (1, 0.8)]),
             outline=S.OW, name='glass'),
        part(morph(top_keys), fill=S.SNOW, name='sand_top'),
        part(morph(stream_keys), stroke=stroke(S.SNOW, 7), o=stream_o, name='stream'),
        part(morph(bot_keys), fill=S.SNOW, name='sand_bottom'),
        part(glass, stroke=stroke(S.OUTLINE, 8), name='glass_edge'),
        part(hl, hl.rotate(180, 256, 256), fill=S.WHITE, o=60, name='glass_hl'),
        part(plates[0], fill=S.vgrad([(0, '#8eaedb'), (0.5, '#ffffff'), (1, '#8eaedb')], 56, 98), outline=S.OW,
             name='plate_top'),
        part(plates[1], fill=S.vgrad([(0, '#8eaedb'), (0.5, '#ffffff'), (1, '#8eaedb')], 414, 456), outline=S.OW,
             name='plate_bottom'),
        part(plate_gloss, plate_gloss.rotate(180, 256, 256), fill=S.WHITE, o=80, name='plate_gloss'),
        pivot=(256, 256),
        r=anim((0, 0, 'hold'), (t_flow, 0, 'io'), (t_flip, 180, 'hold'), (T, 0)),
        s=anim((0, 100, 'hold'), (t_flow, 100, 'io'), ((t_flow + t_flip) / 2, 90, 'outback'), (t_flip, 100, 'hold'), (T, 100)),
        name='hourglass')
    sparks = fx.sparkles([(436, 150, 24), (78, 366, 20), (430, 400, 16)], T, start=20, gap=46, dur=40)
    return [fx.glow(256, 256, 226, alpha=0.3), hg, sparks]


# ------------------------------------------------------------- 049 calendar
def _flake(cx, cy, r, w, color):
    arms, branches = [], []
    for k in range(6):
        a = math.radians(k * 60 - 90)
        u = (math.cos(a), math.sin(a))
        arms.append(line(cx, cy, cx + u[0] * r, cy + u[1] * r))
        bx, by = cx + u[0] * r * 0.58, cy + u[1] * r * 0.58
        for sg in (-1, 1):
            b = a + math.radians(48 * sg)
            branches.append(line(bx, by, bx + math.cos(b) * r * 0.36, by + math.sin(b) * r * 0.36))
    return [part(arms, branches, stroke=stroke(color, w), name='flake'),
            part(circle_path(cx, cy, w * 0.9), fill=color, name='flake_hub')]


def _holds(*keys):
    """Value switched instantly at every key: _holds((t, v), ..., (T, v))."""
    return anim([(t, v, 'hold') for t, v in keys[:-1]] + [keys[-1]])


@emoji(49, 'calendar', '📅', 'Событие', frames=120, still=0)
def e_calendar(T):
    x0, x1, y0, yh, y1, R = 62, 450, 104, 204, 458, 42
    body = rounded([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], R)
    header = rounded([(x0, y0), (x1, y0), (x1, yh), (x0, yh)], [R, R, 0, 0])
    page = rounded([(x0, yh), (x1, yh), (x1, y1), (x0, y1)], [0, 0, R, R])
    cx, cy = 256, 334

    def flake_page():
        return _flake(cx, cy, 86, 17, S.BLUE)

    def star_page():
        st = star(cx, cy + 6, 5, 96, 44, round_out=12, round_in=8)
        return [part(st, fill=S.vgrad(G_VIVID, cy - 90, cy + 80), outline=S.OW_THIN, name='star'),
                part(circle_path(cx - 26, cy - 22, 12, 8).rotate(-30, cx - 26, cy - 22), fill=S.WHITE, o=80)]

    under = [group(star_page(), o=_holds((0, 100), (66, 0), (116, 100), (T, 100)), name='under_star'),
             group(flake_page(), o=_holds((0, 0), (66, 100), (116, 0), (T, 0)), name='under_flake')]
    flip_s = anim((0, [100, 100], 'hold'), (22, [100, 100], 'in'), (36, [100, 0], 'out'), (44, [100, -38], 'hold'),
                  (56, [100, 100], 'hold'), (82, [100, 100], 'in'), (96, [100, 0], 'out'), (104, [100, -38], 'hold'),
                  (112, [100, 100], 'hold'), (T, [100, 100]))
    front = group(
        part(page, fill=S.vgrad(S.G_SNOW, yh, y1), outline=S.OW_THIN, name='page_front'),
        group(flake_page(), o=_holds((0, 100), (36, 0), (112, 100), (T, 100)), name='front_flake'),
        group(star_page(), o=_holds((0, 0), (56, 100), (96, 0), (T, 0)), name='front_star'),
        part(page, fill=S.NAVY, o=anim((0, 0, 'hold'), (22, 0, 'in'), (36, 40, 'hold'), (37, 6, 'hold'), (56, 0, 'hold'),
                                       (82, 0, 'in'), (96, 40, 'hold'), (97, 6, 'hold'), (112, 0, 'hold'), (T, 0)),
             name='flip_shade'),
        pivot=(256, yh), s=flip_s,
        o=_holds((0, 100), (46, 0), (56, 100), (106, 0), (112, 100), (T, 100)), name='front_page')
    rings = []
    for x in (168, 344):
        rings += [part(ellipse(x, 132, 38, 24), fill=S.OUTLINE, name='ring_hole'),
                  part(rounded([(x - 15, 62), (x + 15, 62), (x + 15, 138), (x - 15, 138)], 15),
                       fill=S.vgrad(S.G_SILVER, 62, 138), outline=S.OW_THIN, name='ring'),
                  part(rounded([(x - 8, 72), (x - 2, 72), (x - 2, 118), (x - 8, 118)], 3), fill=S.WHITE, o=80)]
    cal = group(
        part(body, fill=S.vgrad(S.G_SNOW, yh, y1), outline=S.OW, name='body'),
        under,
        front,
        part(header, fill=S.vgrad(S.G_DEEP, y0, yh), outline=S.OW, name='header'),
        fx.shine([header], T, t0=60, dur=30, angle=20, alpha=0.5, width=0.3),
        part(rounded([(x0 + 30, y0 + 16), (x1 - 30, y0 + 16), (x1 - 30, y0 + 24), (x0 + 30, y0 + 24)], 4),
             fill=S.WHITE, o=45, name='header_gloss'),
        rings,
        fx.sparkle(380, 270, 22, T, t0=40, dur=34), fx.sparkle(380, 270, 22, T, t0=100, dur=34),
        pivot=(256, 458), r=fx.swing(T, 2, cycles=2), move=fx.bob(T, 8, cycles=2, shift=15), name='calendar')
    sparks = fx.sparkles([(460, 70, 20), (50, 470, 16)], T, start=8, gap=60, dur=36)
    return [fx.glow(256, 280, 220, alpha=0.28), cal, sparks]


# ------------------------------------------------------------- 050 gear
def _gear(cx, cy, n, r_root, r_tip, hw_root, hw_tip, phase=0.0):
    pts, rad = [], []
    ar, at = math.degrees(hw_root / r_root), math.degrees(hw_tip / r_tip)
    for i in range(n):
        a = phase + 360.0 * i / n
        for ang, r, rr in ((a - ar, r_root, 6), (a - at, r_tip, 5), (a + at, r_tip, 5), (a + ar, r_root, 6)):
            t = math.radians(ang)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
            rad.append(rr)
    return rounded(pts, rad)


@emoji(50, 'gear', '⚙️', 'Настройки', frames=120, still=0)
def e_gear(T):
    c1, c2 = (194, 200), (194 + 224 * math.cos(math.pi / 4), 200 + 224 * math.sin(math.pi / 4))
    # 12 : 8 teeth, same pitch; each loop gear 1 turns 2 tooth periods (60 deg), gear 2 -90 deg;
    # holes repeat every 60 / 90 deg so the loop is seamless; fills are radial around the centres
    g1 = _gear(c1[0], c1[1], 12, 110, 152, 19, 11, phase=15)
    g2 = _gear(c2[0], c2[1], 8, 66, 108, 19, 11, phase=22.5)
    holes1 = [circle_path(c1[0] + 72 * math.cos(math.radians(a)), c1[1] + 72 * math.sin(math.radians(a)), 17).reversed()
              for a in range(0, 360, 60)]
    holes2 = [circle_path(c2[0] + 42 * math.cos(math.radians(a)), c2[1] + 42 * math.sin(math.radians(a)), 10).reversed()
              for a in range(45, 405, 90)]
    gear1 = group(
        part(g1, *holes1, fill=S.rgrad([(0, '#ffffff'), (0.55, '#cfe7ff'), (0.8, '#93c6f8'), (1, '#4a8ae4')], c1[0], c1[1], 152),
             outline=S.OW, name='gear1'),
        part(circle_path(c1[0], c1[1], 36), fill=S.rgrad([(0, '#6fb4ff'), (1, '#1f4fb2')], c1[0], c1[1], 36),
             outline=S.OW_THIN, name='hub1'),
        part(circle_path(c1[0], c1[1], 13), fill=S.OUTLINE, name='axle1'),
        pivot=c1, r=anim((0, 0, 'linear'), (T, 60)), name='gear1_rot')
    gear2 = group(
        part(g2, *holes2, fill=S.rgrad([(0, '#a9d6ff'), (0.6, '#3f86ee'), (1, '#1d4bb0')], c2[0], c2[1], 108),
             outline=S.OW, name='gear2'),
        part(circle_path(c2[0], c2[1], 24), fill=S.rgrad([(0, '#ffffff'), (1, '#9fbfe6')], c2[0], c2[1], 24),
             outline=S.OW_THIN, name='hub2'),
        part(circle_path(c2[0], c2[1], 9), fill=S.OUTLINE, name='axle2'),
        pivot=c2, r=anim((0, 0, 'linear'), (T, -90)), name='gear2_rot')
    gloss = [
        part(_arc(c1[0], c1[1], 96, 196, 252), stroke=stroke(S.WHITE, 9), o=70, name='gloss1'),
        part(circle_path(c1[0] - 12, c1[1] - 13, 7), fill=S.WHITE, o=85, name='hub1_glint'),
        part(_arc(c2[0], c2[1], 58, 196, 252), stroke=stroke(S.WHITE, 6), o=55, name='gloss2'),
        part(circle_path(c2[0] - 8, c2[1] - 9, 5), fill=S.WHITE, o=85, name='hub2_glint'),
    ]
    sparks = fx.sparkles([(432, 104, 26), (92, 426, 22), (470, 230, 14)], T, start=12, gap=40, dur=38)
    return [fx.glow(256, 262, 230, alpha=0.28), gear1, gear2, gloss, sparks]


# ------------------------------------------------------------- 051 search
@emoji(51, 'search', '🔍', 'Поиск', frames=120, still=0)
def e_search(T):
    c, Ro, Ri = (204, 204), 150, 110
    H = _xf(45, 304, 304)
    handle = H(rounded([(0, -31), (196, -31), (196, 31), (0, 31)], [4, 31, 31, 4]))
    collar = H(rounded([(4, -38), (52, -38), (52, 38), (4, 38)], 10))
    ring = [circle_path(c[0], c[1], Ro), circle_path(c[0], c[1], Ri).reversed()]
    lens = circle_path(c[0], c[1], Ri)
    paw_ = paw(c[0] + 6, c[1] + 14, 0.42, rot=-12)
    glass = group(
        part(handle, fill=S.dgrad(S.G_DEEP, (300, 300), (450, 450)), outline=S.OW, name='handle'),
        part(H(rounded([(70, -18), (184, -18), (184, -8), (70, -8)], 5)), fill=S.WHITE, o=45, name='handle_gloss'),
        part(collar, fill=S.dgrad(S.G_SILVER, (290, 290), (340, 340)), outline=S.OW, name='collar'),
        part(lens, fill=S.vgrad([(0, '#f2faff'), (0.55, '#b9defd'), (1, '#6aa9ef')], c[1] - Ri, c[1] + Ri,
                                 opacity=[(0, 0.7), (1, 0.85)]), name='lens'),
        part(paw_, fill=S.BLUE, o=38, name='paw'),
        fx.shine([lens], T, t0=46, dur=34, angle=30, alpha=0.75, width=0.3),
        part(P('M 122 196 C 124 150 156 118 200 112 C 166 128 144 156 140 198 Z'), fill=S.WHITE, o=85, name='lens_gloss'),
        part(circle_path(150, 228, 10), fill=S.WHITE, o=75, name='lens_gloss_dot'),
        part(*ring, fill=S.vgrad(S.G_SILVER, c[1] - Ro, c[1] + Ro), outline=S.OW, name='ring'),
        part(_arc(c[0], c[1], 130, 200, 250), stroke=stroke(S.WHITE, 9), o=80, name='ring_gloss'),
        fx.sparkle(c[0] + 76, c[1] - 76, 30, T, t0=60, dur=36),
        pivot=(300, 300), r=fx.swing(T, 4), name='magnifier')
    mx = group(glass, pivot=(256, 256), move=fx.wave(T, [-16, 0], [16, 0]))
    loop_ = group(mx, pivot=(256, 256), move=fx.wave(T, [0, -14], [0, 14], shift=T / 4))
    sparks = fx.sparkles([(440, 96, 26), (86, 430, 20)], T, start=16, gap=56, dur=38)
    return [fx.glow(232, 232, 220, alpha=0.3), loop_, sparks]


# ------------------------------------------------------------- 052 rocket
def _split_cubic(p0, c1, c2, p3, u):
    L = lambda a, b: (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    a, b, cc = L(p0, c1), L(c1, c2), L(c2, p3)
    d, e = L(a, b), L(b, cc)
    f = L(d, e)
    return (p0, a, d, f), (f, e, cc, p3)


def _jitter(T, amp, step, seed):
    """Small looping vibration offset (eased hops between random points)."""
    rnd = random.Random(seed)
    keys = [(0, [0, 0], 'sine')]
    t = step
    while t < T - step / 2:
        keys.append((t, [rnd.uniform(-amp, amp), rnd.uniform(-amp, amp)], 'sine'))
        t += step
    keys.append((T, [0, 0]))
    return anim(keys)


@emoji(52, 'rocket', '🚀', 'Ракета', frames=120, still=20)
def e_rocket(T):
    k, ctr = 1.0, (262, 250)
    M = _xf(45, ctr[0], ctr[1], k)
    tip, c1, c2, mid = (0, -222), (46, -192), (82, -122), (82, -30)
    body_l = 'M 0 -222 C 46 -192 82 -122 82 -30 C 82 40 74 90 60 126 L -60 126 C -74 90 -82 40 -82 -30 C -82 -122 -46 -192 0 -222 Z'
    body = M(P(body_l))
    # nose band = top of the body above y = -116 (split the side curve exactly)
    u = _bisect(lambda q: _split_cubic(tip, c1, c2, mid, q)[0][3][1], -116, 0, 1)
    seg = _split_cubic(tip, c1, c2, mid, u)[0]
    xe = seg[3][0]
    nose = M(P('M 0 -222 C %.2f %.2f %.2f %.2f %.2f %.2f C %.2f -100 %.2f -100 %.2f -116 C %.2f %.2f %.2f %.2f 0 -222 Z' % (
        seg[1][0], seg[1][1], seg[2][0], seg[2][1], xe, seg[3][1], xe * 0.55, -xe * 0.55, -xe,
        -seg[2][0], seg[2][1], -seg[1][0], seg[1][1])))
    fins = [M(P('M -64 26 C -104 52 -128 98 -124 156 C -112 150 -88 140 -62 128 Z')),
            M(P('M 64 26 C 104 52 128 98 124 156 C 112 150 88 140 62 128 Z'))]
    nozzle = M(rounded([(-42, 120), (42, 120), (54, 156), (-54, 156)], 7))
    window = M(circle_path(0, -36, 52))
    win_glass = M(circle_path(0, -36, 36))
    flame_o = M(P('M -46 150 C -48 196 -24 248 0 290 C 24 248 48 196 46 150 Z'))
    flame_m = M(P('M -32 150 C -32 186 -16 226 0 258 C 16 226 32 186 32 150 Z'))
    flame_i = M(P('M -18 150 C -18 176 -8 202 0 224 C 8 202 18 176 18 150 Z'))
    fa, fb = M(Bez([(0, 150)])).v[0], M(Bez([(0, 290)])).v[0]
    rnd = random.Random(5)
    fk, t = [], 0
    while t < T:
        fk.append((t, [100 + rnd.uniform(-5, 5), 100 if t == 0 else 100 + rnd.uniform(-14, 16)], 'sine'))
        t += 5
    fk.append((T, [100, 100]))
    flame = group(
        part(flame_o, fill=S.dgrad([(0, '#e6f8ff'), (0.5, '#7cd0ff'), (1, '#3b7ce8')], fa, fb), outline=S.OW_THIN, name='flame_out'),
        part(flame_m, fill=S.dgrad([(0, '#ffffff'), (1, '#8fe3ff')], fa, fb), name='flame_mid'),
        part(flame_i, fill=S.WHITE, name='flame_core'),
        pivot=fa, s=anim(fk), name='flame')
    rocket = group(
        flame,
        part(*fins, fill=S.vgrad(S.G_DEEP, 230, 420), outline=S.OW, name='fins'),
        part(nozzle, fill=S.vgrad([(0, '#c9d9ec'), (1, '#5f7fae')], 330, 400), outline=S.OW, name='nozzle'),
        part(body, fill=S.vgrad(S.G_SNOW, 80, 400), outline=S.OW, name='body'),
        part(nose, fill=S.vgrad(S.G_DEEP, 70, 220), name='nose'),
        part(M(P('M -60 -96 C -70 -60 -72 -10 -66 40 L -52 40 C -58 -10 -56 -60 -46 -96 Z')), fill=S.WHITE, o=80, name='body_gloss'),
        part(M(rounded([(-56, 92), (56, 92), (52, 106), (-52, 106)], 5)), fill=S.BLUE_D, o=55, name='body_band'),
        part(window, fill=S.vgrad(S.G_SILVER, 170, 290), outline=S.OW_THIN, name='window_rim'),
        part(win_glass, fill=S.vgrad([(0, '#7cc4ff'), (1, '#173e9e')], 190, 270), name='window_glass'),
        part(M(circle_path(-12, -50, 11, 8)), fill=S.WHITE, o=90, name='window_glint'),
        pivot=ctr, move=_jitter(T, 2.2, 4, 11), name='rocket')
    # streaks / stars fly tail-wards beside the rocket (rocket frame: x across, y along the
    # axis); every point stays within ~200 px of the centre so nothing leaves the canvas
    R = lambda x, y: Bez([(x, y)]).rotate(45).translate(*ctr).v[0]
    streaks, stars = [], []
    for x, y0, ln, travel, t0 in ((-150, -112, 70, 150, 0), (150, -120, 70, 150, 30), (-118, -150, 60, 160, 60),
                                  (124, -160, 60, 170, 90)):
        a, b, e = R(x, y0), R(x, y0 + ln), R(x, y0 + travel)
        st = loop([(t0, [0, 0], 'linear'), (t0 + 36, [e[0] - a[0], e[1] - a[1]], 'hold'), (t0 + T, [0, 0])], T)
        op = loop([(t0, 0, 'linear'), (t0 + 8, 85, 'linear'), (t0 + 26, 85, 'linear'), (t0 + 36, 0, 'hold'), (t0 + T, 0)], T)
        streaks.append(group(part(line(a[0], a[1], b[0], b[1]), stroke=stroke(S.ICE_L, 10)), move=st, o=op, name='streak'))
    for x, y0, r, travel, t0 in ((-170, -80, 15, 140, 14), (170, -60, 12, 140, 50), (-130, -150, 13, 140, 84),
                                 (110, -170, 11, 140, 104)):
        a, e = R(x, y0), R(x, y0 + travel)
        st = loop([(t0, [0, 0], 'linear'), (t0 + 50, [e[0] - a[0], e[1] - a[1]], 'hold'), (t0 + T, [0, 0])], T)
        op = loop([(t0, 0, 'linear'), (t0 + 10, 100, 'linear'), (t0 + 38, 100, 'linear'), (t0 + 50, 0, 'hold'), (t0 + T, 0)], T)
        stars.append(group(part(sparkle_path(a[0], a[1], r), fill=S.WHITE), move=st, o=op, name='star'))
    return [fx.glow(256, 256, 226, alpha=0.3), stars, streaks, rocket]


# ------------------------------------------------------------- 053 gamepad
@emoji(53, 'gamepad', '🎮', 'Игры', frames=120, still=0)
def e_gamepad(T):
    body = P('M 256 158 L 352 158 C 422 158 454 196 464 250 C 476 318 484 382 448 406 '
             'C 414 428 380 406 360 378 C 344 354 330 338 300 338 L 212 338 C 182 338 168 354 152 378 '
             'C 132 406 98 428 64 406 C 28 382 36 318 48 250 C 58 196 90 158 160 158 Z')
    dc = (148, 250)
    arm_w, arm_l = 36, 112
    dpad = [rounded([(dc[0] - arm_w / 2, dc[1] - arm_l / 2), (dc[0] + arm_w / 2, dc[1] - arm_l / 2),
                     (dc[0] + arm_w / 2, dc[1] + arm_l / 2), (dc[0] - arm_w / 2, dc[1] + arm_l / 2)], 9),
            rounded([(dc[0] - arm_l / 2, dc[1] - arm_w / 2), (dc[0] + arm_l / 2, dc[1] - arm_w / 2),
                     (dc[0] + arm_l / 2, dc[1] + arm_w / 2), (dc[0] - arm_l / 2, dc[1] + arm_w / 2)], 9)]
    bc = (366, 250)
    btns = [((bc[0], bc[1] - 44), S.G_TEAL), ((bc[0] + 44, bc[1]), S.G_VIOLET),
            ((bc[0], bc[1] + 44), G_VIVID), ((bc[0] - 44, bc[1]), S.G_ICE_SOFT)]
    buttons = []
    for j, ((x, y), g) in enumerate(btns):
        st = [8 + 12 * j, 70 + 12 * j]
        buttons.append(group(
            part(circle_path(x, y, 22), fill=S.vgrad(g, y - 22, y + 22), outline=S.OW_THIN, name='button'),
            part(circle_path(x, y, 22), fill=S.WHITE, o=_blink_o(T, st, 14, 75), name='button_flash'),
            part(circle_path(x - 7, y - 8, 6), fill=S.WHITE, o=85, name='button_glint'),
            pivot=(x, y), s=_seq(T, st, [(0, 100, 'out'), (4, 82, 'outback'), (14, 100, 'hold')], 100), name='btn'))
        buttons.append(group(fx.ring_pulse(x, y, 22, 40, T, t0=st[0], dur=18, w0=6, w1=1, alpha=80),
                             fx.ring_pulse(x, y, 22, 40, T, t0=st[1], dur=18, w0=6, w1=1, alpha=80)))
    # d-pad presses: up, right, down, left while the buttons rest
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    d_move = _seq(T, [56], sum([[(14 * j, [0, 0], 'out'), (14 * j + 4, [4 * dx, 4 * dy], 'in')]
                                for j, (dx, dy) in enumerate(dirs)], []) + [(56, [0, 0], 'hold')], [0, 0])
    hl = []
    for j, (dx, dy) in enumerate(dirs):
        ax, ay = dc[0] + dx * arm_l * 0.32, dc[1] + dy * arm_l * 0.32
        hl.append(part(circle_path(ax, ay, 12), fill=S.WHITE, o=_blink_o(T, [56 + 14 * j], 12, 80), name='dpad_hl'))
    pad = group(
        part(*dpad, fill=S.vgrad([(0, '#2b4f9e'), (1, S.OUTLINE)], dc[1] - 56, dc[1] + 56), outline=S.OW_THIN, name='dpad'),
        part(rounded([(dc[0] - 12, dc[1] - 48), (dc[0] - 4, dc[1] - 48), (dc[0] - 4, dc[1] - 24), (dc[0] - 12, dc[1] - 24)], 4),
             fill=S.WHITE, o=40, name='dpad_gloss'),
        hl, pivot=dc, move=d_move, name='dpad_g')
    pad_ = group(
        part(body, fill=S.vgrad(S.G_ICE, 158, 420), outline=S.OW, name='body'),
        fx.shine([body], T, t0=96, dur=24, angle=24, alpha=0.5, width=0.24),
        part(P('M 80 214 C 96 186 124 172 168 170 L 216 170 L 216 182 L 170 182 C 132 184 108 196 94 222 Z'),
             fill=S.WHITE, o=70, name='gloss'),
        part(rounded([(208, 214), (240, 214), (240, 228), (208, 228)], 7), rounded([(272, 214), (304, 214), (304, 228), (272, 228)], 7),
             fill=S.NAVY, outline=S.OW_THIN, name='menu_btns'),
        part(circle_path(256, 290, 22), fill=S.vgrad(S.G_SILVER, 268, 312), outline=S.OW_THIN, name='home'),
        part(circle_path(250, 284, 6), fill=S.WHITE, o=90, name='home_glint'),
        pad, buttons,
        pivot=(256, 300), r=fx.swing(T, 4, shift=0), move=fx.bob(T, 10, cycles=2), name='gamepad')
    sparks = fx.sparkles([(446, 116, 24), (70, 116, 18)], T, start=30, gap=60, dur=36)
    return [fx.glow(256, 286, 226, alpha=0.3), pad_, sparks]


# ------------------------------------------------------------- 054 trophy
@emoji(54, 'trophy', '🏆', 'Кубок', frames=180, still=0)
def e_trophy(T):
    bowl = P('M 118 84 C 118 204 166 276 230 296 L 282 296 C 346 276 394 204 394 84 Z')
    stem = P('M 234 290 L 278 290 C 276 312 272 324 290 346 L 222 346 C 240 324 236 312 234 290 Z')
    knot = rounded([(214, 338), (298, 338), (298, 360), (214, 360)], 10)
    tier1 = rounded([(180, 354), (332, 354), (332, 390), (180, 390)], 12)
    tier2 = rounded([(146, 384), (366, 384), (366, 446), (146, 446)], 18)
    rim = circle_path(256, 84, 138, 24)
    inside = circle_path(256, 86, 118, 15)
    handles = [P('M 128 112 C 66 102 40 156 66 202 C 82 232 116 244 152 238'),
               P('M 384 112 C 446 102 472 156 446 202 C 430 232 396 244 360 238')]
    st = star(256, 172, 5, 58, 27, round_out=8, round_in=5)
    cup = group(
        part(handles, stroke=stroke(S.SILVER, 26), outline=(S.OUTLINE, 13 + S.OW_THIN), name='handles'),
        part(handles, stroke=stroke(S.WHITE, 7), o=70, name='handle_gloss'),
        part(tier2, fill=S.vgrad(S.G_DEEP, 384, 446), outline=S.OW, name='base'),
        part(rounded([(196, 400), (316, 400), (316, 428), (196, 428)], 8), fill=S.vgrad(S.G_SILVER, 400, 428),
             outline=S.OW_THIN, name='plaque'),
        part(rounded([(168, 393), (344, 393), (344, 399), (168, 399)], 3), fill=S.WHITE, o=40, name='base_gloss'),
        part(tier1, fill=S.vgrad(S.G_SILVER, 354, 390), outline=S.OW, name='tier'),
        part(stem, fill=S.vgrad(S.G_SILVER, 290, 346), outline=S.OW, name='stem'),
        part(knot, fill=S.vgrad(S.G_DEEP, 338, 360), outline=S.OW_THIN, name='knot'),
        part(bowl, fill=S.vgrad(S.G_SILVER, 84, 296), outline=S.OW, name='bowl'),
        fx.shine([bowl], T, t0=40, dur=44, angle=28, alpha=0.75, width=0.28),
        part(P('M 146 112 C 148 176 170 230 206 262 C 178 224 164 174 164 112 Z'), fill=S.WHITE, o=80, name='bowl_gloss'),
        part(rim, fill=S.vgrad(S.G_ICE_SOFT, 60, 108), outline=S.OW, name='rim'),
        part(inside, fill=S.vgrad([(0, S.NAVY), (1, S.BLUE_D)], 72, 100), name='inside'),
        part(st, fill=S.vgrad(G_VIVID, 116, 226), outline=S.OW_THIN, name='star'),
        part(circle_path(240, 156, 9, 6).rotate(-30, 240, 156), fill=S.WHITE, o=85, name='star_glint'),
        pivot=(256, 446), move=fx.bob(T, 12), name='trophy')
    sparks = fx.sparkles([(118, 76, 28), (402, 70, 22), (310, 150, 18), (432, 300, 20), (84, 300, 16)],
                         T, start=10, gap=34, dur=40)
    return [fx.glow(256, 240, 226, alpha=0.32, s=fx.breathe(T, 92, 104)), cup, sparks]


# ------------------------------------------------------------- 055 coin
@emoji(55, 'coin', '🪙', 'Монета', frames=120, still=0)
def e_coin(T):
    cx, cy, R, th = 256, 244, 172, 34
    t0, t1 = 14, 62

    def theta(t):  # eased 0 -> 2 pi turn around the vertical axis
        if t <= t0 or t >= t1:
            return 0.0
        return math.pi * (1 - math.cos(math.pi * (t - t0) / (t1 - t0)))

    # fake 3D: visible face, hidden face and the edge band between them; x-scales are
    # |cos| / |sin| of the turn angle, the faces sit +-th/2 * sin apart
    fmv, fs, bmv, bs = [], [], [], []
    for t in [0] + list(range(t0, t1 + 1, 2)) + [T]:
        a = theta(t)
        c, s = math.cos(a), math.sin(a)
        xf = th / 2 * s * (1 if c >= 0 else -1)
        e = 'hold' if t in (0, t1) else 'linear'
        fmv.append((t, [xf, 0], e))
        bmv.append((t, [-xf, 0], e))
        fs.append((t, [max(abs(c), 0.004) * 100, 100], e))
        bs.append((t, [abs(s) * 100, 100], e))
    t_a, t_b = t0 + (t1 - t0) / 3, t0 + 2 * (t1 - t0) / 3   # edge-on moments: swap K <-> crown
    disc = circle_path(cx, cy, R)
    edge = S.vgrad([(0, '#b8d0ee'), (1, '#4c6c9e')], cy - R, cy + R)
    hidden = group(part(disc, fill=edge, outline=S.OW, name='back_disc'), pivot=(cx, cy), move=anim(bmv), s=anim(fs),
                   name='coin_back')
    band = group(part(Bez([(cx - th / 2, cy - R), (cx + th / 2, cy - R), (cx + th / 2, cy + R), (cx - th / 2, cy + R)]),
                      fill=edge, outline=S.OW, name='band'),
                 part([line(x, cy - R + 18, x, cy + R - 18) for x in (cx - 9, cx, cx + 9)], stroke=stroke(S.NAVY, 4), o=45,
                      name='reeds'),
                 pivot=(cx, cy), s=anim(bs), name='coin_edge')
    kp, _ = glyphs('K', cx + 4, cy, 148, weight=900)[0]
    cr = crown(cx, cy + 12, 204, ow=5)
    face = group(
        part(disc, fill=S.vgrad([(0, '#ffffff'), (0.5, '#d3e5f8'), (1, '#86a9d8')], cy - R, cy + R), outline=S.OW, name='rim'),
        part(circle_path(cx, cy, R - 28), fill=S.vgrad([(0, '#eef7ff'), (1, '#a9c8ec')], cy - R, cy + R), name='face'),
        part(circle_path(cx, cy, R - 28), stroke=stroke(S.STEEL, 5), o=75, name='groove'),
        group(part([p.translate(5, 7) for p in kp], fill=S.NAVY, o=30, name='k_shadow'),
              part(kp, fill=S.vgrad(G_VIVID, cy - 74, cy + 74), outline=S.OW_THIN, name='k'),
              o=_holds((0, 100), (t_a, 0), (t_b, 100), (T, 100)), name='front'),
        group(cr['parts'], o=_holds((0, 0), (t_a, 100), (t_b, 0), (T, 0)), name='back'),
        fx.shine([disc], T, t0=80, dur=32, angle=28, alpha=0.7, width=0.28),
        part(_arc(cx, cy, R - 14, 198, 250), stroke=stroke(S.WHITE, 9), o=85, name='rim_gloss'),
        pivot=(cx, cy), move=anim(fmv), s=anim(fs), name='coin_face')
    hop = anim((0, [0, 0], 'hold'), (t0, [0, 0], 'out'), ((t0 + t1) / 2, [0, -46], 'in'), (t1, [0, 0], 'out'),
               (t1 + 7, [0, -10], 'in'), (t1 + 14, [0, 0], 'hold'), (T, [0, 0]))
    squash = _seq(T, [t1], [(0, [100, 100], 'out'), (3, [106, 94], 'io'), (10, [100, 100], 'hold')], [100, 100])
    coin = group(hidden, band, face, pivot=(cx, cy + R), move=hop, s=squash, name='coin')
    sh = anim((0, 100, 'hold'), (t0, 100, 'out'), ((t0 + t1) / 2, 74, 'in'), (t1, 100, 'out'), (t1 + 7, 92, 'in'),
              (t1 + 14, 100, 'hold'), (T, 100))
    sparks = fx.sparkles([(424, 92, 28), (92, 126, 20), (446, 338, 18)], T, start=t1 + 2, gap=10, dur=36)
    return [fx.glow(cx, cy, 226, alpha=0.3), _shadow(cx, 452, 220, 26, o=28, s=sh), coin, sparks]


# ------------------------------------------------------------- 056 ban
def _damped(t0, dur, amp, n=3):
    """Keys of a damped oscillation in [t0, t0 + dur] ending with a hold at 0."""
    keys = [(t0, 0, 'sine')]
    for k in range(1, 2 * n + 1):
        keys.append((t0 + dur * k / (2 * n + 1), amp * (1 - (k - 1) / (2 * n)) * (1 if k % 2 else -1), 'sine'))
    return keys + [(t0 + dur, 0, 'hold')]


@emoji(56, 'ban', '🚫', 'Запрет', frames=120, still=0)
def e_ban(T):
    c, Ro, Ri, w = (256, 256), 190, 142, 52
    slash = rounded([(-150, -w / 2), (150, -w / 2), (150, w / 2), (-150, w / 2)], 6).rotate(45).translate(*c)
    ring = [circle_path(c[0], c[1], Ro), circle_path(c[0], c[1], Ri).reversed()]
    pulse = anim((0, 100, 'hold'), (6, 100, 'out'), (11, 113, 'io'), (18, 95, 'io'), (26, 101, 'io'), (32, 100, 'hold'),
                 (66, 100, 'out'), (71, 105, 'io'), (80, 100, 'hold'), (T, 100))
    shake = anim([(0, 0, 'hold')] + _damped(8, 42, 10) + _damped(68, 24, 4, 2) + [(T, 0)])
    sign = group(
        part(circle_path(c[0], c[1], Ri), fill=S.vgrad([(0, '#ffffff'), (1, '#d6e7f8')], c[1] - Ri, c[1] + Ri),
             name='face'),
        part(*ring, slash, fill=S.vgrad(S.G_RED, c[1] - Ro, c[1] + Ro), outline=S.OW, name='sign'),
        fx.shine(ring + [slash], T, t0=74, dur=32, alpha=0.55, width=0.26),
        part(_arc(c[0], c[1], Ro - 24, 198, 252), stroke=stroke(S.WHITE, 12), o=75, name='ring_gloss'),
        part(line(-96, -13, 96, -13).rotate(45).translate(*c), stroke=stroke(S.WHITE, 8), o=55, name='slash_gloss'),
        pivot=c, s=pulse, r=shake, name='ban')
    ring_fx = fx.ring_pulse(c[0], c[1], 192, 228, T, t0=8, dur=30, color='#ffc2c9', w0=14, w1=2, alpha=80)
    sparks = fx.sparkles([(440, 84, 22), (78, 436, 18)], T, start=36, gap=40, dur=34)
    return [fx.glow(256, 256, 226, color='#ff9fb0', alpha=0.22, s=pulse), ring_fx, sign, sparks]


# ------------------------------------------------------------- 057 mute
@emoji(57, 'mute', '🔇', 'Мут', frames=120, still=0)
def e_mute(T):
    spk = P('M 62 216 C 62 204 70 196 82 196 L 148 196 L 254 104 C 266 94 286 100 286 116 L 286 396 '
            'C 286 412 266 418 254 408 L 148 316 L 82 316 C 70 316 62 308 62 296 Z')
    xc = (396, 256)
    bar = rounded([(-62, -21), (62, -21), (62, 21), (-62, 21)], 21)
    cross = [bar.rotate(45).translate(*xc), bar.rotate(-45).translate(*xc)]
    throb = _seq(T, [28, 36, 44, 52], [(0, 100, 'out'), (3, 104, 'in'), (8, 100, 'hold')], 100)
    speaker = group(
        part(spk, fill=S.vgrad(S.G_ICE, 98, 414), outline=S.OW, name='speaker'),
        part(P('M 162 214 L 262 128 L 262 384 L 162 298 Z'), fill=S.NAVY, o=14, name='cone_shade'),
        part(line(148, 206, 148, 306), stroke=stroke(S.OUTLINE, 6), o=45, name='divider'),
        fx.shine([spk], T, t0=96, dur=24, angle=24, alpha=0.5),
        part(rounded([(78, 210), (134, 210), (134, 218), (78, 218)], 4), fill=S.WHITE, o=70, name='box_gloss'),
        part(P('M 164 200 L 252 122 C 258 118 264 120 266 126 L 176 206 Z'), fill=S.WHITE, o=60, name='cone_gloss'),
        pivot=(176, 256), s=throb, r=anim([(0, 0, 'hold')] + _damped(76, 22, 4, 2) + [(T, 0)]), name='speaker_g')
    waves = []
    for j, (r, span) in enumerate(((74, 38), (120, 40))):
        ta, tf = 28 + 8 * j, 62 + 6 * j
        waves.append(group(
            _lines([_arc(300, 256, r, -span, span)], 18, S.ICE_L),
            pivot=(300, 256),
            s=anim((0, 70, 'hold'), (ta, 70, 'outback'), (ta + 12, 100, 'hold'), (tf, 100, 'out'), (tf + 14, 114, 'hold'), (T, 70)),
            o=anim((0, 0, 'hold'), (ta, 0, 'out'), (ta + 6, 100, 'hold'), (tf, 100, 'in'), (tf + 14, 0, 'hold'), (T, 0)),
            name='wave'))
    xg = group(
        part(*cross, fill=S.vgrad(S.G_RED, xc[1] - 70, xc[1] + 70), outline=S.OW, name='cross'),
        part(rounded([(-44, -9), (-6, -9), (-6, -3), (-44, -3)], 3).rotate(45).translate(*xc), fill=S.WHITE, o=70,
             name='cross_gloss'),
        pivot=xc,
        s=anim((0, 100, 'hold'), (16, 100, 'inback'), (26, 0, 'hold'), (72, 0, 'outback'), (84, 100, 'hold'), (T, 100)),
        r=anim((0, 0, 'hold'), (60, -90, 'hold'), (72, -90, 'out'), (84, 0, 'hold'), (T, 0)), name='cross_g')
    sparks = [fx.sparkle(456, 176, 22, T, t0=84, dur=34), fx.sparkle(94, 128, 18, T, t0=40, dur=34)]
    return [fx.glow(250, 256, 224, alpha=0.28), waves, speaker, xg, sparks]


# ------------------------------------------------------------- 058 flag
def _subdiv(b, step=18.0):
    """Insert vertices along the straight edges of a path (curved edges are kept)."""
    out = Bez(closed=b.c)
    n = len(b.v)
    for k in range(n):
        out.add(b.v[k], b.i[k], b.o[k])
        if not b.c and k == n - 1:
            break
        j = (k + 1) % n
        v, w = b.v[k], b.v[j]
        if b.o[k] == [0.0, 0.0] and b.i[j] == [0.0, 0.0]:
            m = int(math.hypot(w[0] - v[0], w[1] - v[1]) // step)
            for q in range(1, m + 1):
                u = q / (m + 1)
                out.add((v[0] + (w[0] - v[0]) * u, v[1] + (w[1] - v[1]) * u))
    return out


def _smooth(b, sharp=(), k=1 / 6.0):
    """Catmull-Rom tangents through the vertices of a polygon (vertices in `sharp` stay corners)."""
    n = len(b.v)
    out = Bez(closed=b.c)
    for j in range(n):
        p = b.v[j]
        if j in sharp or (not b.c and j in (0, n - 1)):
            out.add(p)
            continue
        a, c = b.v[j - 1], b.v[(j + 1) % n]
        t = ((c[0] - a[0]) * k, (c[1] - a[1]) * k)
        out.add(p, (-t[0], -t[1]), t)
    return out


@emoji(58, 'flag', '🚩', 'Жалоба / флаг', frames=120, still=0)
def e_flag(T):
    x0, x1, yt, yb = 116, 452, 92, 300
    W, H, lam, N = x1 - x0, yb - yt, 236.0, 8
    pts = ([(x0 + W * j / N, yt) for j in range(N + 1)] + [(x1, yt + H * j / 4) for j in range(1, 4)] +
           [(x1 - W * j / N, yb) for j in range(N + 1)] + [(x0, yb - H * j / 4) for j in range(1, 4)])
    corners = {0, N, N + 4, 2 * N + 4}
    cloth = Bez(pts)
    kp = [_subdiv(p, 22) for p in glyphs('K', 296, 194, 118, weight=900)[0][0]]
    gl = _subdiv(Bez([(x0 + 34, yt + 16), (x1 - 40, yt + 16)], closed=False), 36)

    def wave(ph):
        def f(x, y):
            u = max(0.0, (x - x0) / W)
            a = 2 * math.pi * (x - x0) / lam - ph
            return (x - 7 * u * (1 - math.cos(a)) / 2, y + 23 * u ** 0.9 * math.sin(a) + 5 * u)
        return f

    steps = 16   # 2 wave cycles per loop
    keys_c, keys_k, keys_g = [], [[] for _ in kp], []
    for j in range(steps + 1):
        f = wave(4 * math.pi * j / steps)
        t = T * j / steps
        keys_c.append((t, _smooth(cloth.map(f), corners), 'linear'))
        for q, p in enumerate(kp):
            keys_k[q].append((t, p.map(f), 'linear'))
        keys_g.append((t, _smooth(gl.map(f)), 'linear'))
    # moving shade bands that follow the travelling wave (gradient period = wavelength)
    span = 4 * lam
    s0 = x0 - 2 * lam + lam / 4
    shade = S.dgrad([(j / 16.0, S.NAVY) for j in range(17)], (0, 0), (1, 0),
                    opacity=[(j / 16.0, 0.24 * (0.5 + 0.5 * math.cos(2 * math.pi * 4 * j / 16.0))) for j in range(17)])
    shade['s'] = anim((0, [s0, 200], 'linear'), (T, [s0 + 2 * lam, 200]))
    shade['e'] = anim((0, [s0 + span, 200], 'linear'), (T, [s0 + span + 2 * lam, 200]))
    flag = [
        part(morph(keys_c), fill=S.vgrad(G_VIVID, yt - 20, yb + 30), outline=S.OW, name='cloth'),
        part(morph(keys_c), fill=shade, name='cloth_shade'),
        part(morph(keys_g), stroke=stroke(S.WHITE, 7), o=45, name='cloth_gloss'),
        part([morph(kk) for kk in keys_k], fill=S.vgrad(S.G_SNOW, 130, 260), outline=S.OW_THIN, name='k'),
    ]
    pole = [
        part(rounded([(98, 80), (126, 80), (126, 470), (98, 470)], 14), fill=S.dgrad(S.G_SILVER, (98, 0), (126, 0)),
             outline=S.OW, name='pole'),
        part(rounded([(104, 96), (110, 96), (110, 440), (104, 440)], 3), fill=S.WHITE, o=70, name='pole_gloss'),
        part(circle_path(112, 66, 24), fill=S.vgrad(S.G_ICE_SOFT, 42, 90), outline=S.OW, name='finial'),
        part(circle_path(104, 58, 7), fill=S.WHITE, o=90, name='finial_glint'),
        part(P('M 38 488 C 48 452 82 438 112 438 C 144 438 178 452 188 488 Z'), fill=S.vgrad(S.G_SNOW, 438, 488),
             outline=S.OW, name='snow'),
        part(P('M 66 470 C 76 456 92 450 110 450 C 92 456 82 464 78 476 Z'), fill=S.WHITE, o=90, name='snow_gloss'),
    ]
    sparks = fx.sparkles([(160, 40, 20), (462, 380, 22), (300, 400, 16)], T, start=14, gap=36, dur=38)
    return [fx.glow(280, 220, 220, alpha=0.28), flag, pole, sparks]


# ------------------------------------------------------------- 059 scroll
def _ease(name, u):
    """Progress (0..1, may overshoot) of a kit EASE curve at time fraction u."""
    (x1, y1), (x2, y2) = EASE[name]
    bz = lambda s, a, b: 3 * (1 - s) ** 2 * s * a + 3 * (1 - s) * s * s * b + s ** 3
    s = _bisect(lambda q: bz(q, x1, x2), u, 0.0, 1.0)
    return bz(s, y1, y2)


@emoji(59, 'scroll', '📜', 'Правила', frames=180, still=100)
def e_scroll(T):
    y_top, y_closed, y_open = 96, 142, 418
    t_un, d_un, t_up, d_up = 0, 32, 136, 26
    ex, ew = 96, 416

    def roller(y):
        return [part(circle_path(62, y, 21), circle_path(450, y, 21), fill=S.vgrad(S.G_SILVER, y - 21, y + 21),
                     outline=S.OW, name='knobs'),
                part(rounded([(74, y - 22), (438, y - 22), (438, y + 22), (74, y + 22)], 22),
                     fill=S.vgrad(S.G_DEEP, y - 22, y + 22), outline=S.OW, name='roller'),
                part(rounded([(92, y - 13), (420, y - 13), (420, y - 7), (92, y - 7)], 3), fill=S.WHITE, o=55, name='roller_gloss'),
                part(circle_path(56, y - 7, 6), circle_path(444, y - 7, 6), fill=S.WHITE, o=85, name='knob_glint')]

    def yb_at(t):
        if t <= t_un:
            return y_closed
        if t < t_un + d_un:
            return y_closed + (y_open - y_closed) * _ease('outback', (t - t_un) / d_un)
        if t < t_up:
            return y_open
        if t < t_up + d_up:
            return y_open - (y_open - y_closed) * _ease('io', (t - t_up) / d_up)
        return y_closed

    def reveal(y_bottom):
        """(time the roller uncovers y_bottom while unrolling, time it reaches it rolling up)."""
        a = _bisect(lambda t: yb_at(t) - 22, y_bottom, t_un, t_un + d_un * 0.7)
        b = _bisect(lambda t: yb_at(t) - 22, y_bottom, t_up, t_up + d_up)
        return a, b

    paper = lambda y: Bez([(ex, y_top), (ew, y_top), (ew, y), (ex, y)])
    paper_shape = morph((0, paper(y_closed), 'outback'), (d_un, paper(y_open), 'hold'), (t_up, paper(y_open), 'io'),
                        (t_up + d_up, paper(y_closed), 'hold'), (T, paper(y_closed)))
    bottom_move = anim((0, [0, 0], 'outback'), (d_un, [0, y_open - y_closed], 'hold'), (t_up, [0, y_open - y_closed], 'io'),
                       (t_up + d_up, [0, 0], 'hold'), (T, [0, 0]))
    items = []
    # crown
    a, b = reveal(206)
    cr = crown(256, 166, 112, ow=4, gems=False)
    items.append(group(cr['parts'], pivot=(256, 166),
                       s=anim((0, 0, 'hold'), (a, 0, 'outback'), (a + 14, 100, 'hold'), (b - 3, 100, 'in'), (b + 1, 0, 'hold'), (T, 0)),
                       name='rules_crown'))
    for j, (y, xe) in enumerate(((234, 380), (268, 352), (302, 380), (336, 326), (370, 298))):
        a, b = reveal(y + 7)
        a += 2 * j
        items.append(part(line(132, y, xe, y), stroke=stroke(S.BLUE_D, 12), o=_holds((0, 0), (a, 70), (b, 0), (T, 0)),
                          trim=trim(0, anim((0, 0, 'hold'), (a, 0, 'out'), (a + 16, 100, 'hold'), (T, 0))), name='text_line'))
    a, b = reveal(394)
    items.append(group(
        part(circle_path(366, 362, 30), fill=S.vgrad(G_VIVID, 332, 392), outline=S.OW_THIN, name='seal'),
        part(star(366, 364, 5, 15, 7, round_out=2, round_in=1), fill=S.WHITE, name='seal_star'),
        pivot=(366, 362),
        s=anim((0, 0, 'hold'), (a + 8, 0, 'outback'), (a + 22, 100, 'hold'), (b - 3, 100, 'in'), (b + 1, 0, 'hold'), (T, 0)),
        name='seal_g'))
    scroll = group(
        part(paper_shape, fill=S.vgrad(S.G_SNOW, y_top, y_open), outline=S.OW, name='paper'),
        part(rounded([(ex + 10, y_top + 22), (ew - 10, y_top + 22), (ew - 10, y_top + 30), (ex + 10, y_top + 30)], 4),
             fill=S.NAVY, o=12, name='paper_shade'),
        items,
        group(roller(y_closed), move=bottom_move, name='bottom_roller'),
        roller(y_top),
        fx.sparkle(392, 336, 22, T, t0=74, dur=34),
        pivot=(256, 256), move=fx.bob(T, 8, cycles=2), name='scroll')
    sparks = fx.sparkles([(470, 196, 18), (44, 300, 16), (462, 470, 14)], T, start=40, gap=30, dur=36)
    return [fx.glow(256, 260, 224, alpha=0.28), scroll, sparks]


# ------------------------------------------------------------- 060 mail
@emoji(60, 'mail', '✉️', 'Письмо', frames=120, still=0)
def e_mail(T):
    hinge = (256, 204)
    env = rounded([(58, 198), (454, 198), (454, 440), (58, 440)], 26)
    flap = rounded([(58, 204), (454, 204), (256, 344)], [18, 18, 34])
    pocket = rounded([(58, 204), (256, 330), (454, 204), (454, 440), (58, 440)], [14, 30, 14, 26, 26])
    t_open, t_close = 14, 92
    front_s = anim((0, [100, 100], 'hold'), (t_open, [100, 100], 'in'), (t_open + 8, [100, 0], 'hold'),
                   (t_close + 8, [100, 0], 'out'), (t_close + 16, [100, 100], 'hold'), (T, [100, 100]))
    back_s = anim((0, [100, 0], 'hold'), (t_open + 8, [100, 0], 'out'), (t_open + 16, [100, -100], 'hold'),
                  (t_close, [100, -100], 'in'), (t_close + 8, [100, 0], 'hold'), (T, [100, 0]))
    letter_mv = anim((0, [0, 0], 'hold'), (t_open + 10, [0, 0], 'outback'), (t_open + 32, [0, -150], 'hold'),
                     (t_close - 16, [0, -150], 'in'), (t_close, [0, 0], 'hold'), (T, [0, 0]))
    beat = _seq(T, [52, 64], [(0, 100, 'out'), (5, 118, 'in'), (11, 98, 'out'), (16, 100, 'hold')], 100)
    hp = heart_path(256, 272, 118, 104)
    letter = group(
        part(rounded([(104, 214), (408, 214), (408, 420), (104, 420)], 14), fill=S.vgrad(S.G_SNOW, 214, 420),
             outline=S.OW_THIN, name='letter'),
        group(part(hp, fill=S.vgrad(G_VIVID, 220, 324), outline=S.OW_THIN, name='heart'),
              part(circle_path(228, 250, 15, 9).rotate(-38, 228, 250), fill=S.WHITE, o=85, name='heart_gloss'),
              pivot=(256, 280), s=beat, name='heart_g'),
        part(line(160, 352, 352, 352), line(160, 382, 300, 382), stroke=stroke(S.BLUE_D, 10), o=45, name='letter_lines'),
        move=letter_mv, name='letter_g')
    seal = [part(circle_path(256, 318, 32), fill=S.vgrad(S.G_DEEP, 286, 350), outline=S.OW_THIN, name='seal'),
            part(heart_path(256, 320, 34, 30), fill=S.WHITE, name='seal_heart')]
    squash = _seq(T, [t_close + 16], [(0, [100, 100], 'out'), (3, [104, 96], 'outback'), (12, [100, 100], 'hold')], [100, 100])
    mail = group(
        part(env, fill=S.vgrad([(0, '#3c78dc'), (1, '#173e9e')], 198, 440), outline=S.OW, name='inside'),
        group(part(flap, fill=S.vgrad([(0, '#cfe8ff'), (1, '#7fb6f2')], 204, 344), outline=S.OW, name='flap_in'),
              pivot=hinge, s=back_s, name='flap_open'),
        letter,
        part(pocket, fill=S.vgrad(S.G_ICE, 204, 440), outline=S.OW, name='pocket'),
        part(line(76, 428, 222, 324), line(436, 428, 290, 324), stroke=stroke(S.NAVY, 6), o=22, name='folds'),
        part(rounded([(78, 420), (200, 420), (200, 427), (78, 427)], 3), fill=S.WHITE, o=40, name='pocket_gloss'),
        fx.shine([pocket], T, t0=100, dur=20, angle=24, alpha=0.45),
        group(part(flap, fill=S.vgrad(S.G_ICE_SOFT, 204, 344), outline=S.OW, name='flap'),
              part(P('M 92 214 L 250 316 L 240 318 L 84 220 Z'), fill=S.WHITE, o=65, name='flap_gloss'),
              seal, pivot=hinge, s=front_s, name='flap_closed'),
        fx.sparkle(392, 98, 24, T, t0=50, dur=34), fx.sparkle(122, 140, 18, T, t0=62, dur=32),
        pivot=(256, 440), s=squash, move=fx.bob(T, 8, cycles=2), name='mail')
    sparks = fx.sparkles([(462, 160, 18), (46, 470, 16)], T, start=8, gap=60, dur=36)
    return [fx.glow(256, 300, 220, alpha=0.28), mail, sparks]
