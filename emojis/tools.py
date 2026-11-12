"""043-060: tools, moderation and community actions."""
import math

from kit.registry import emoji
from kit.lottie import part, group, anim, loop, stroke, fill, trim, ellipse
from kit.geometry import P, Bez, rounded, star, circle_path, heart_path, line, polyline, morph
from kit.text import glyphs, fit_cap
from kit.motifs import crown
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
        part(page, fill=S.vgrad([(0, '#dcebfb'), (1, '#b4d2f2')], yh, y1), name='under_page'),
        under,
        part(rounded([(x0 + 26, yh + 16), (x1 - 26, yh + 16), (x1 - 26, yh + 22), (x0 + 26, yh + 22)], 3), fill=S.NAVY, o=12),
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
