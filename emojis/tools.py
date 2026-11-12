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
