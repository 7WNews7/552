"""033-042: text badges (letters are glyph outlines, Telegram forbids text layers)."""
import math
import random

from kit.registry import emoji
from kit.lottie import part, group, anim, loop, stroke
from kit.geometry import P, Bez, bbox_of, rounded, circle_path, morph, star
from kit.motifs import crown, snowcap
from kit.text import glyphs, fit_cap
from kit import fx, style as S


@emoji(33, 'gg', '🎮', 'GG — хорошая игра', frames=120, still=0)
def e_gg(T):
    cap = fit_cap('GG', 440, 236, weight=900, tracking=0.02)
    cy = 318
    letters = []
    for k, (paths, (gx, gy)) in enumerate(glyphs('GG', 256, cy, cap, weight=900, tracking=0.02)):
        t0 = 6 + k * 14
        hop = anim((0, [0, 0], 'hold'), (t0, [0, 0], 'out'), (t0 + 14, [0, -30], 'in'), (t0 + 28, [0, 0], 'hold'), (T, [0, 0]))
        squash = anim((0, [100, 100], 'hold'), (t0 + 26, [100, 100], 'out'), (t0 + 31, [108, 92], 'io'),
                      (t0 + 42, [100, 100], 'hold'), (T, [100, 100]))
        letters.append(group(
            part(*paths, fill=S.vgrad(S.G_ICE, cy - cap / 2, cy + cap / 2), outline=10, name='glyph'),
            fx.shine(paths, T, t0=58 + k * 10, dur=40, alpha=0.8, width=0.3),
            pivot=(gx, cy + cap / 2), move=hop, s=squash, name='letter'))
    c = crown(256, 112, 176, ow=6)
    crown_g = group(c['parts'], fx.sparkles([(x, y, 18) for x, y in c['tips']], T, start=48, gap=14, dur=34),
                    pivot=(256, 150), r=fx.swing(T, 7, cycles=2), move=fx.bob(T, 10, cycles=2), name='crown')
    return [fx.glow(256, 300, 220, alpha=0.3), letters, crown_g]


# ------------------------------------------------------------------ helpers (034-042)
G_LETTER = [(0.0, '#ffffff'), (0.6, '#eef7ff'), (1.0, '#b7dcff')]    # white letters on blue
G_FLAME = [(0.0, '#e6f6ff'), (0.32, '#86c6ff'), (1.0, '#2a66d8')]
CONFETTI = [S.ICE_L, S.SKY, S.LILAC, S.TEAL, S.WHITE, S.BLUE_L, S.MINT]


def _box(cx, cy, w, h, r):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    return rounded([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], r)


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


def _icy_letters(gl, T, cy, cap, ow=10, stops=None, shadow=False, shine_t0=None, shine_gap=9, bbox=None, anims=None):
    """One group per glyph: optional navy drop shadow, gradient fill + navy contour, shine.
    anims(k, gx) -> dict(move=, s=, r=) for that letter."""
    out = []
    for k, (paths, (gx, gy)) in enumerate(gl):
        kids = []
        if shadow:
            kids.append(part(*_shift(paths, 0, 7), fill=S.OUTLINE, o=50, name='shadow'))
        kids.append(part(*paths, fill=S.vgrad(stops or S.G_ICE, cy - cap / 2, cy + cap / 2),
                         outline=(S.OUTLINE, ow), name='glyph'))
        if shine_t0 is not None:
            kids.append(fx.shine(paths, T, t0=shine_t0 + k * shine_gap, dur=38, alpha=0.85, width=0.3, bbox=bbox))
        tf = anims(k, gx) if anims else {}
        out.append(group(kids, pivot=(gx, cy + cap / 2), name='letter', **tf))
    return out


def _teardrop(cx, cy, w, h):
    """Drop with the point up; (cx, cy) = centre of the round bottom."""
    r = w / 2
    return P(f'M {cx} {cy - h + r} C {cx + w * 0.14} {cy - h * 0.62 + r} {cx + r} {cy - r * 0.55} {cx + r} {cy} '
             f'A {r} {r} 0 0 1 {cx - r} {cy} '
             f'C {cx - r} {cy - r * 0.55} {cx - w * 0.14} {cy - h * 0.62 + r} {cx} {cy - h + r} Z')


def _flame(cx, by, w, h, lean=0.0, lick=1.0):
    """Flame tongue with a smaller side lick on the left. Every variant has the same 6 vertices
    (morphable): tip, right bulge, bottom, left bulge, lick tip, notch."""
    b = Bez()
    b.add((cx + lean, by - h), (-w * 0.03 - lean * 0.25, h * 0.2), (w * 0.06 - lean * 0.2, h * 0.24))
    b.add((cx + w / 2, by - h * 0.3), (0, -h * 0.28), (0, h * 0.18))
    b.add((cx, by), (w * 0.3, 0), (-w * 0.3, 0))
    b.add((cx - w / 2, by - h * 0.3), (0, h * 0.18), (0, -h * 0.16))
    b.add((cx - w * 0.34 + lean * 0.35, by - h * 0.66 * lick), (-w * 0.02, h * 0.16), (w * 0.05, h * 0.1))
    b.add((cx - w * 0.1 + lean * 0.5, by - h * 0.5), (-w * 0.06, h * 0.02), (w * 0.02, -h * 0.12))
    return b


def _laugh_face(cx, cy, r, ow=10):
    """Round laughing face (stands in for the O of LOL): ^ ^ eyes, open mouth."""
    face = circle_path(cx, cy, r)
    eyes = [P(f'M {cx + s * r * 0.56} {cy - r * 0.1} Q {cx + s * r * 0.33} {cy - r * 0.62} {cx + s * r * 0.1} {cy - r * 0.1}')
            for s in (-1, 1)]
    mouth = P(f'M {cx - r * 0.6} {cy + r * 0.08} L {cx + r * 0.6} {cy + r * 0.08} '
              f'C {cx + r * 0.6} {cy + r * 0.52} {cx + r * 0.33} {cy + r * 0.78} {cx} {cy + r * 0.78} '
              f'C {cx - r * 0.33} {cy + r * 0.78} {cx - r * 0.6} {cy + r * 0.52} {cx - r * 0.6} {cy + r * 0.08} Z')
    return [
        part(face, fill=S.vgrad(S.G_ICE, cy - r, cy + r), outline=(S.OUTLINE, ow), name='face'),
        part(circle_path(cx - r * 0.5, cy - r * 0.55, r * 0.16, r * 0.09).rotate(-35, cx - r * 0.5, cy - r * 0.55),
             fill=S.WHITE, o=80, name='face_gloss'),
        part(*eyes, stroke=stroke(S.OUTLINE, r * 0.15), name='eyes'),
        part(mouth, fill=S.NAVY_D, outline=(S.OUTLINE, 3), name='mouth'),
        part(_box(cx, cy + r * 0.16, r * 0.92, r * 0.15, r * 0.07), fill=S.WHITE, name='teeth'),
        part(circle_path(cx, cy + r * 0.62, r * 0.26, r * 0.13), fill=S.PINK, name='tongue'),
    ]


# ------------------------------------------------------------------ 034 NEW
@emoji(34, 'new', '🆕', 'NEW', frames=120, still=0)
def e_new(T):
    cx, cy, n = 256, 256, 16
    burst = star(cx, cy, n, 230, 194, round_out=12, round_in=10)
    # fills inside the rotating group are rotation-invariant (radial around the centre)
    rays = group(part(burst, fill=S.rgrad([(0, '#7cc2ff'), (0.62, '#2f72e4'), (1, '#1a47b0')], cx, cy, 230),
                      outline=S.OW, name='burst'),
                 pivot=(cx, cy), r=fx.spin(T, 1 / n), name='rays')
    disc_r = 172
    deco = [
        part(circle_path(cx, cy, disc_r), stroke=stroke(S.ICE_L, 5, o=50), name='inner_rim'),
        part(_arc_band(cx, cy, disc_r - 14, disc_r - 34, 200, 252), fill=S.WHITE, o=45, name='gloss'),
    ]
    wt, tr, sq = 900, 0.03, 0.92
    cap = _fit('NEW', 2 * disc_r - 30, 116, wt, tr, sq)
    gl = _word('NEW', cx, cy, cap, wt, tr, sq)
    letters = _icy_letters(gl, T, cy, cap, ow=6, stops=G_LETTER, shadow=True,
                           anims=lambda k, gx: {'s': _pop(T, 10 + 7 * k, peak=124, dur=28)})
    body = group(rays, deco, fx.shine([circle_path(cx, cy, disc_r)], T, t0=58, dur=44, angle=22, width=0.3, alpha=0.45),
                 letters, pivot=(cx, cy), s=_pop(T, 4, peak=104, dur=26, under=99), name='badge')
    sparks = fx.sparkles([(430, 92, 26), (84, 424, 20), (444, 404, 16)], T, start=34, gap=14, dur=34)
    return [body, sparks]


# ------------------------------------------------------------------ 035 TOP
def _arrow_up(cx, top, w, h, shaft_w, head_h, r=16):
    pts = [(cx, top), (cx + w / 2, top + head_h), (cx + shaft_w / 2, top + head_h), (cx + shaft_w / 2, top + h),
           (cx - shaft_w / 2, top + h), (cx - shaft_w / 2, top + head_h), (cx - w / 2, top + head_h)]
    return rounded(pts, [r * 1.3, r, r * 0.6, r, r, r * 0.6, r])


@emoji(35, 'top', '🔝', 'TOP', frames=120, still=0)
def e_top(T):
    wt, tr = 900, 0.03
    cap = _fit('TOP', 444, 150, wt, tr)
    ty = 370
    gl = _word('TOP', 256, ty, cap, wt, tr)
    bb = bbox_of([p for ps, _ in gl for p in ps])
    t_land = 50
    letters = _icy_letters(gl, T, ty, cap, ow=10, shine_t0=72, bbox=bb,
                           anims=lambda k, gx: {'s': _squash(T, t_land + k * 2, k=5, dur=16)})
    aw, ah, top = 236, 236, 76
    arrow = _arrow_up(256, top, aw, ah, 104, 120)
    bot = top + ah
    a_parts = [
        part(arrow, fill=S.vgrad(S.G_ICE, top, bot), outline=S.OW, name='arrow'),
        part(P(f'M {256 - 18} {top + 30} L {256 - aw / 2 + 36} {top + 108} L {256 - aw / 2 + 58} {top + 108} '
               f'L {256 - 6} {top + 50} Z'), fill=S.WHITE, o=70, name='arrow_gloss'),
        part(_box(256 - 30, top + 190, 16, 70, 8), fill=S.WHITE, o=45, name='shaft_gloss'),
        fx.shine([arrow], T, t0=22, dur=26, angle=70, width=0.3, alpha=0.7),
    ]
    move = anim((0, [0, 0], 'io'), (12, [0, 0], 'out'), (30, [0, -34], 'in'), (t_land, [0, 0], 'out'),
                (58, [0, -9], 'in'), (66, [0, 0], 'io'), (T, [0, 0]))
    sc = anim((0, [100, 100], 'io'), (5, [100, 100], 'io'), (12, [106, 94], 'out'), (20, [96, 105], 'io'),
              (32, [100, 100], 'io'), (t_land, [100, 100], 'out'), (54, [108, 92], 'io'), (62, [99, 101], 'io'),
              (68, [102, 98], 'io'), (76, [100, 100], 'io'), (T, [100, 100]))
    streak_o = anim((0, 0, 'hold'), (14, 0, 'out'), (20, 80, 'in'), (32, 0, 'hold'), (T, 0))
    streaks = part(_box(256 - 84, bot - 60, 10, 64, 5), _box(256 + 84, bot - 60, 10, 64, 5), _box(256, bot + 26, 10, 44, 5),
                   fill=S.ICE_L, o=streak_o, name='streaks')
    arrow_g = group(streaks, group(a_parts, pivot=(256, bot), s=sc, name='stretch'), move=move, name='arrow_jump')
    sparks = fx.sparkles([(256 - 150, top + 20, 24), (256 + 152, top + 50, 20)], T, start=28, gap=8, dur=30)
    return [fx.glow(256, 280, 228, alpha=0.26), arrow_g, letters, sparks]


# ------------------------------------------------------------------ 036 HOT
@emoji(36, 'hot', '🔥', 'HOT', frames=120, still=0)
def e_hot(T):
    wt, tr = 900, 0.03
    cap = _fit('HOT', 444, 150, wt, tr)
    ty = 374
    gl = _word('HOT', 256, ty, cap, wt, tr)
    bb = bbox_of([p for ps, _ in gl for p in ps])
    var = [(1.0, 1.0, 0, 1.0), (0.93, 1.07, 16, 0.88), (1.05, 0.94, -12, 1.1), (0.96, 1.05, 9, 0.94),
           (1.04, 0.95, -16, 1.08), (0.95, 1.04, 6, 0.96)]
    step = T / len(var)
    flames = []
    for i, (fxc, fby, fw, fh, sh, mir) in enumerate([(148, 370, 156, 218, 2, False), (364, 370, 156, 218, 4, True),
                                                     (256, 356, 204, 296, 0, False)]):
        seq = var[sh:] + var[:sh]
        fl = (lambda b, x=fxc: b.mirror_x(x)) if mir else (lambda b: b)   # right flame licks outwards
        outer = [(round(step * j), fl(_flame(fxc, fby, fw * a, fh * b, c, d)), 'sine') for j, (a, b, c, d) in enumerate(seq)]
        inner = [(round(step * j), fl(_flame(fxc, fby - 10, fw * a * 0.52, fh * b * 0.6, c * 0.6, d)), 'sine')
                 for j, (a, b, c, d) in enumerate(seq)]
        outer.append((T, outer[0][1]))
        inner.append((T, inner[0][1]))
        flames.append(group(
            part(morph(outer), fill=S.vgrad(G_FLAME, fby - fh, fby), outline=(S.OUTLINE, 6), name='flame'),
            part(morph(inner), fill=S.vgrad([(0, S.WHITE), (1, S.ICE)], fby - fh * 0.6, fby), name='flame_core'),
            name='flame_%d' % i))
    embers = []
    rnd = random.Random(5)
    for k in range(6):
        x = 120 + k * 54 + rnd.uniform(-10, 10)
        y = 236 + rnd.uniform(-20, 20)
        embers.append(group(part(circle_path(x, y, rnd.uniform(6, 9)), fill=S.ICE_L, name='ember'), pivot=(x, y),
                            **fx.rise(T, k * T / 6, 52, dy=-120, dx=rnd.uniform(-16, 16), s0=100, s1=70, alpha=95)))
    letters = _icy_letters(gl, T, ty, cap, ow=10, shine_t0=58, bbox=bb,
                           anims=lambda k, gx: {'s': fx.wave(T, [100, 100], [103, 97], cycles=2, shift=k * 10)})
    return [fx.glow(256, 250, 230, alpha=0.32, s=fx.breathe(T, 94, 104, cycles=3)), flames, embers, letters]


# ------------------------------------------------------------------ 037 WIN
def _confetti(cx, cy, T, t0, n, rx, ry, seed=3, dur=60):
    """Small spinning ribbons bursting up/out, then drifting down and fading (once per loop)."""
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        a = math.radians(-174 + 168 * (k + 0.5) / n + rnd.uniform(-6, 6))
        d = rnd.uniform(0.6, 1.0)
        p1 = [math.cos(a) * rx * d, math.sin(a) * ry * d]
        p2 = [p1[0] * 1.15, p1[1] + rnd.uniform(70, 100)]
        mv = anim((0, [0, 0], 'hold'), (t0, [0, 0], 'out2'), (t0 + dur * 0.35, p1, 'in'), (t0 + dur, p2, 'hold'), (T, p2))
        op = anim((0, 0, 'hold'), (t0, 100, 'hold'), (t0 + dur * 0.7, 100, 'in'), (t0 + dur, 0, 'hold'), (T, 0))
        turn = rnd.choice((-1, 1)) * rnd.uniform(280, 520)
        spin = anim((0, 0, 'hold'), (t0, 0, 'linear'), (t0 + dur, turn, 'hold'), (T, turn))
        piece = part(_box(cx, cy, 18, 10, 3), fill=CONFETTI[k % len(CONFETTI)], name='ribbon')
        out.append(group(group(piece, pivot=(cx, cy), r=spin, name='spin'), pivot=(cx, cy), move=mv, o=op, name='confetti'))
    return out


def _trophy(cx, top):
    bowl = P(f'M {cx - 88} {top} L {cx + 88} {top} C {cx + 88} {top + 88} {cx + 58} {top + 126} {cx} {top + 132} '
             f'C {cx - 58} {top + 126} {cx - 88} {top + 88} {cx - 88} {top} Z')
    handles = [P(f'M {cx - 80} {top + 22} C {cx - 146} {top + 10} {cx - 150} {top + 98} {cx - 60} {top + 106}'),
               P(f'M {cx + 80} {top + 22} C {cx + 146} {top + 10} {cx + 150} {top + 98} {cx + 60} {top + 106}')]
    lip = _box(cx, top, 196, 26, 13)
    stem = _box(cx, top + 150, 38, 46, 10)
    base = _box(cx, top + 186, 128, 32, 12)
    plinth = _box(cx, top + 214, 172, 30, 12)
    st = star(cx, top + 62, 5, 32, 14, round_out=4, round_in=3)
    parts = [
        part(*handles, stroke=stroke(S.OUTLINE, 18 + 2 * S.OW_THIN), name='handle_outline'),
        part(*handles, stroke=stroke('#bcd6f2', 18), name='handles'),
        part(stem, plinth, fill=S.vgrad(S.G_DEEP, top + 128, top + 230), outline=S.OW, name='stem'),
        part(base, fill=S.vgrad(S.G_SILVER, top + 170, top + 202), outline=S.OW, name='base'),
        part(bowl, fill=S.vgrad(S.G_SILVER, top, top + 132), outline=S.OW, name='bowl'),
        part(lip, fill=S.vgrad(S.G_ICE, top - 13, top + 13), outline=S.OW, name='lip'),
        part(P(f'M {cx - 66} {top + 24} C {cx - 64} {top + 66} {cx - 52} {top + 94} {cx - 30} {top + 112} '
               f'L {cx - 42} {top + 112} C {cx - 66} {top + 94} {cx - 78} {top + 66} {cx - 78} {top + 24} Z'),
             fill=S.WHITE, o=80, name='bowl_gloss'),
        part(st, fill=S.vgrad(S.G_DEEP, top + 30, top + 94), outline=(S.OUTLINE, 4), name='star'),
    ]
    return parts, [bowl, lip, base]


@emoji(37, 'win', '🏆', 'WIN', frames=120, still=0)
def e_win(T):
    wt, tr = 900, 0.03
    cap = _fit('WIN', 444, 140, wt, tr)
    ty = 382
    gl = _word('WIN', 256, ty, cap, wt, tr)
    bb = bbox_of([p for ps, _ in gl for p in ps])
    letters = _icy_letters(gl, T, ty, cap, ow=10, shine_t0=64, bbox=bb,
                           anims=lambda k, gx: {'move': _hop(T, 18 + 6 * k, dy=-20, up=10, down=11),
                                                's': _squash(T, 39 + 6 * k, k=6, dur=16)})
    top = 70
    tparts, tshine = _trophy(256, top)
    trophy = group(tparts, fx.shine(tshine, T, t0=40, dur=34, angle=24, width=0.3, alpha=0.85),
                   pivot=(256, top + 228), s=_pop(T, 8, peak=110, dur=30), r=fx.swing(T, 2, cycles=2), name='trophy')
    conf = _confetti(256, top + 80, T, 12, 18, 196, 108, seed=4)
    sparks = fx.sparkles([(256 - 112, top - 14, 22), (256 + 116, top + 6, 26), (256 + 4, top - 30, 16)], T,
                         start=30, gap=10, dur=32)
    return [fx.glow(256, 260, 228, alpha=0.28), conf, trophy, letters, sparks]


# ------------------------------------------------------------------ 038 OK
@emoji(38, 'ok', '🆗', 'OK', frames=120, still=0)
def e_ok(T):
    cx, cy, sz = 256, 268, 376
    box = _box(cx, cy, sz, sz, 88)
    bot = cy + sz / 2
    badge = [
        part(box, fill=S.vgrad(S.G_DEEP, cy - sz / 2, bot), outline=S.OW, name='badge'),
        part(_box(cx, cy, sz - 26, sz - 26, 76), stroke=stroke(S.ICE_L, 5, o=55), name='inner_rim'),
        part(P(f'M {cx - sz / 2 + 30} {cy - 40} C {cx - sz / 2 + 30} {cy - sz / 2 + 60} {cx - sz / 2 + 60} '
               f'{cy - sz / 2 + 30} {cx - 40} {cy - sz / 2 + 30} L {cx - 40} {cy - sz / 2 + 48} '
               f'C {cx - sz / 2 + 74} {cy - sz / 2 + 48} {cx - sz / 2 + 48} {cy - sz / 2 + 74} {cx - sz / 2 + 48} {cy - 40} Z'),
             fill=S.WHITE, o=45, name='gloss'),
    ]
    wt, tr = 900, 0.04
    cap = _fit('OK', sz - 66, 170, wt, tr)
    ty = cy + 2
    gl = _word('OK', cx, ty, cap, wt, tr)
    letters = _icy_letters(gl, T, ty, cap, ow=7, stops=G_LETTER, shadow=True,
                           anims=lambda k, gx: {'s': _pop(T, 50 + 7 * k, peak=116, dur=24)})
    move = anim((0, [0, 0], 'io'), (12, [0, 0], 'out'), (30, [0, -30], 'in'), (46, [0, 0], 'out'), (55, [0, -8], 'in'),
                (63, [0, 0], 'io'), (T, [0, 0]))
    sc = anim((0, [100, 100], 'io'), (5, [100, 100], 'io'), (12, [107, 93], 'out'), (20, [97, 103], 'io'),
              (32, [100, 100], 'io'), (46, [100, 100], 'out'), (50, [108, 92], 'io'), (57, [99, 101], 'io'),
              (63, [102, 98], 'io'), (70, [100, 100], 'io'), (T, [100, 100]))
    body = group(group(badge, fx.shine([box], T, t0=72, dur=40, angle=22, width=0.26, alpha=0.45), letters,
                       pivot=(cx, bot), s=sc, name='squash'), move=move, name='bounce')
    sparks = fx.sparkles([(cx + sz / 2 - 18, cy - sz / 2 + 10, 26), (cx - sz / 2 + 4, cy + 60, 18)], T, start=28, gap=50, dur=34)
    return [fx.glow(cx, cy, 230, alpha=0.26), body, sparks]


# ------------------------------------------------------------------ 039 AFK
def _crescent(cx, cy, r, k=0.56):
    """Moon crescent opening to the right."""
    return P(f'M {cx} {cy - r} A {r} {r} 0 0 0 {cx} {cy + r} A {r * k} {r} 0 0 1 {cx} {cy - r} Z')


@emoji(39, 'afk', '💤', 'AFK', frames=180, still=0)
def e_afk(T):
    wt, tr = 900, 0.03
    cap = _fit('AFK', 410, 140, wt, tr)
    ty, wx = 378, 232
    gl = _word('AFK', wx, ty, cap, wt, tr)
    bb = bbox_of([p for ps, _ in gl for p in ps])
    letters = _icy_letters(gl, T, ty, cap, ow=10, shine_t0=96, shine_gap=10, bbox=bb,
                           anims=lambda k, gx: {'s': fx.wave(T, [100, 100], [101.5, 96], cycles=2, shift=k * 6)})
    word = group(letters, pivot=(wx, ty + cap / 2), r=fx.swing(T, 2), name='word')
    mx, my, mr = 126, 136, 78
    moon = group(
        part(_crescent(mx, my, mr), fill=S.vgrad(S.G_SILVER, my - mr, my + mr), outline=S.OW, name='moon'),
        part(circle_path(mx - mr * 0.62, my - mr * 0.25, 8), circle_path(mx - mr * 0.5, my + mr * 0.42, 6),
             fill=S.STEEL, o=55, name='craters'),
        pivot=(mx, my), r=fx.swing(T, 6), move=fx.bob(T, 8), name='moon_g')
    zs = []
    zx, zy = bb[2] - 66, ty - cap / 2 - 38
    for k in range(3):
        zc = 84
        zp = [p for ps, _ in _word('Z', zx, zy, zc, 900, 0) for p in ps]
        rise = fx.rise(T, 20 + k * T / 3, 120, dy=-184, dx=44, s0=40, s1=116, alpha=100)
        zs.append(group(part(*zp, fill=S.vgrad(S.G_ICE_SOFT, zy - zc / 2, zy + zc / 2), outline=(S.OUTLINE, 6), name='z'),
                        pivot=(zx, zy), r=fx.swing(T, 8, shift=k * 20), name='z_rot'))
        zs[-1] = group(zs[-1], pivot=(zx, zy), name='z_rise', **rise)
    sparks = fx.sparkles([(mx + 92, my - 40, 18), (mx + 30, my + 104, 14)], T, start=40, gap=70, dur=40)
    return [fx.glow(256, 290, 226, alpha=0.24), moon, sparks, word, zs]


# ------------------------------------------------------------------ 040 LOL
def _laugh(T, starts, delay, hops=3, period=12, amp=-16, rot=6):
    mv, rr = [(0, [0, 0], 'io')], [(0, 0, 'io')]
    for s0 in starts:
        for h in range(hops):
            t = s0 + delay + h * period
            if t > mv[-1][0]:
                mv.append((t, [0, 0], 'out'))
                rr.append((t, 0, 'out'))
            sgn = 1 if h % 2 == 0 else -1
            mv += [(t + period * 0.45, [0, amp * (1 - 0.18 * h)], 'in'), (t + period, [0, 0], 'out')]
            rr += [(t + period * 0.45, rot * sgn, 'in'), (t + period, 0, 'out')]
    mv.append((T, [0, 0]))
    rr.append((T, 0))
    return anim(mv), anim(rr)


def _tear(cx, cy, T, t0, dx, up=70, down=60, dur=34, size=1.0):
    """Tear drop flying sideways on a parabola (x eased out, y up then down), fading at the end."""
    w, h = 30 * size, 44 * size
    drop = _teardrop(cx, cy, w, h).rotate(-28 if dx < 0 else 28, cx, cy - h * 0.3)
    body = [part(drop, fill=S.vgrad([(0, '#eaf7ff'), (1, '#4f97f5')], cy - h, cy + w / 2), outline=(S.OUTLINE, 4.5),
                 name='tear'),
            part(circle_path(cx - w * 0.14, cy - w * 0.05, w * 0.13), fill=S.WHITE, o=90, name='tear_glint')]
    yk = anim((0, [0, 0], 'hold'), (t0, [0, 0], 'out'), (t0 + dur * 0.4, [0, -up], 'in'), (t0 + dur, [0, down], 'hold'),
              (T, [0, down]))
    xk = anim((0, [0, 0], 'hold'), (t0, [0, 0], 'out'), (t0 + dur, [dx, 0], 'hold'), (T, [dx, 0]))
    op = anim((0, 0, 'hold'), (t0, 0, 'out'), (t0 + 4, 100, 'hold'), (t0 + dur * 0.7, 100, 'in'), (t0 + dur, 0, 'hold'), (T, 0))
    sc = anim((0, 50, 'hold'), (t0, 50, 'outback'), (t0 + 10, 100, 'hold'), (T, 100))
    return group(group(body, pivot=(cx, cy), move=yk, s=sc, name='tear_y'), pivot=(cx, cy), move=xk, o=op, name='tear_x')


@emoji(40, 'lol', '😂', 'LOL', frames=120, still=0)
def e_lol(T):
    wt, tr = 900, 0.04
    cap = _fit('LOL', 436, 160, wt, tr)
    ty = 352
    gl = _word('LOL', 256, ty, cap, wt, tr)
    bb = bbox_of([p for ps, _ in gl for p in ps])
    starts = (6, 62)

    ox = gl[1][1][0]
    fr = cap * 0.54
    letters = []
    for k, (paths, (gx, gy)) in enumerate(gl):
        mv, rr = _laugh(T, starts, delay=k * 4, rot=6 if k != 1 else -5)
        if k == 1:   # the O is a laughing face
            kids = _laugh_face(ox, ty, fr) + [fx.shine([circle_path(ox, ty, fr)], T, t0=52, dur=38, alpha=0.6,
                                                       width=0.3, bbox=bb)]
        else:
            kids = [part(*paths, fill=S.vgrad(S.G_ICE, ty - cap / 2, ty + cap / 2), outline=10, name='glyph'),
                    fx.shine(paths, T, t0=44 + 8 * k, dur=38, alpha=0.85, width=0.3, bbox=bb)]
        letters.append(group(kids, pivot=(gx, ty + cap / 2), move=mv, r=rr, name='letter'))
    tears = []
    for s0 in starts:
        for j, dt in enumerate((4, 15)):
            sz = 1.25 - 0.2 * j
            tears.append(_tear(ox - fr * 0.62, ty - fr * 0.12, T, s0 + dt, dx=-140 + 30 * j, up=96 - 16 * j, down=24, size=sz))
            tears.append(_tear(ox + fr * 0.62, ty - fr * 0.12, T, s0 + dt + 3, dx=140 - 30 * j, up=96 - 16 * j, down=24,
                               size=sz))
    word = group(letters, pivot=(256, ty + cap / 2), s=fx.wave(T, [100, 100], [103, 97], cycles=2), name='word')
    return [fx.glow(256, 300, 226, alpha=0.26), word, tears]


# ------------------------------------------------------------------ 041 +1
@emoji(41, 'plus_one', '👍', '+1', frames=120, still=0)
def e_plus_one(T):
    cy, one_cap = 262, 318
    one = _word('1', 0, cy, one_cap, 900, 0)[0][0]
    ob = bbox_of(one)
    ow_ = ob[2] - ob[0]
    pl, th, gap = 214, 74, 24
    x0 = 256 - (pl + gap + ow_) / 2
    pcx = x0 + pl / 2
    one = _shift(one, x0 + pl + gap - ob[0], 0)
    ocx = x0 + pl + gap + ow_ / 2
    a, b = pl / 2, th / 2
    plus = rounded([(pcx - b, cy - a), (pcx + b, cy - a), (pcx + b, cy - b), (pcx + a, cy - b), (pcx + a, cy + b),
                    (pcx + b, cy + b), (pcx + b, cy + a), (pcx - b, cy + a), (pcx - b, cy + b), (pcx - a, cy + b),
                    (pcx - a, cy - b), (pcx - b, cy - b)], [16, 16, 8, 16, 16, 8, 16, 16, 8, 16, 16, 8])
    plus_g = group(part(plus, fill=S.vgrad(S.G_ICE, cy - a, cy + a), outline=S.OW, name='plus'),
                   part(_box(pcx - 8, cy - a + 34, 16, 48, 8), _box(pcx - a + 40, cy - 8, 48, 14, 7), fill=S.WHITE, o=70,
                        name='plus_gloss'),
                   fx.shine([plus], T, t0=50, dur=36, alpha=0.85, width=0.3),
                   pivot=(pcx, cy), s=_pop(T, 6, peak=120, dur=30, under=95), r=fx.wobble(T, 10, 30, 8, n=2), name='plus_g')
    one_g = group(part(*one, fill=S.vgrad(S.G_ICE, cy - one_cap / 2, cy + one_cap / 2), outline=S.OW, name='one'),
                  fx.shine(one, T, t0=58, dur=36, alpha=0.85, width=0.3),
                  pivot=(ocx, cy + one_cap / 2), s=_pop(T, 12, peak=114, dur=30, under=96), name='one_g')
    ring = fx.ring_pulse(256, cy, 120, 226, T, t0=10, dur=40, w0=14)
    burst = fx.burst(256, cy, T, 10, 10, 150, 228, size=16, color=S.WHITE, dur=32, rot=18, shape='spark', seed=7)
    body = group(plus_g, one_g, pivot=(256, cy), move=fx.bob(T, 10), name='body')
    sparks = fx.sparkles([(424, 98, 24), (94, 116, 18), (430, 420, 16)], T, start=44, gap=22, dur=34)
    return [fx.glow(256, cy, 230, alpha=0.3, s=_pop(T, 8, peak=108, dur=40)), ring, burst, body, sparks]


# ------------------------------------------------------------------ 042 2027
def _firework(cx, cy, T, t0, color, r=84, seed=1, rise=110, spark=S.ICE):
    trail_mv = loop([(t0 - 18, [0, rise], 'out'), (t0, [0, 0], 'hold'), (t0 - 18 + T, [0, rise])], T)
    trail_o = loop([(t0 - 18, 0, 'out'), (t0 - 14, 90, 'linear'), (t0 - 1, 90, 'hold'), (t0, 0, 'hold'), (t0 - 18 + T, 0)], T)
    return [
        group(part(circle_path(cx, cy, 7), fill=S.WHITE, name='trail'), pivot=(cx, cy), move=trail_mv, o=trail_o,
              name='rocket'),
        fx.ring_pulse(cx, cy, 8, r * 0.85, T, t0=t0, dur=30, color=color, w0=10, w1=1, alpha=75),
        fx.burst(cx, cy, T, t0, 14, 8, r, size=15, color=color, dur=40, rot=seed * 11, shape='dot', seed=seed),
        fx.burst(cx, cy, T, t0 + 3, 8, 4, r * 0.66, size=17, color=spark, dur=34, rot=seed * 11 + 22, shape='spark',
                 seed=seed + 9),
        fx.sparkle(cx, cy, 32, T, t0=t0 - 2, dur=16, turn=0, halo=True),
    ]


@emoji(42, 'year_2027', '🎆', '2027 — Новый год', frames=180, still=32)
def e_year_2027(T):
    wt, tr, sq = 900, 0.02, 0.9
    cap = _fit('2027', 458, 150, wt, tr, sq)
    ty = 356
    gl = _word('2027', 256, ty, cap, wt, tr, sq)
    bb = bbox_of([p for ps, _ in gl for p in ps])
    caps = []
    for ch, (paths, (gx, gy)) in zip('2027', gl):
        b = bbox_of(paths)
        w = b[2] - b[0]
        if ch == '7':
            caps.append(snowcap(b[0] + 10, b[2] - 12, b[1] + 6, h=26, drips=((0.3, 14), (0.7, 20))))
        else:
            caps.append(snowcap(b[0] + w * 0.2, b[2] - w * 0.2, b[1] + 12, h=24, drips=((0.42, 14),)))
    letters = _icy_letters(gl, T, ty, cap, ow=10, shine_t0=40, shine_gap=8, bbox=bb)
    for k, cp in enumerate(caps):
        letters[k] = group(letters[k], part(cp, fill=S.vgrad(S.G_SNOW, ty - cap / 2 - 20, ty - cap / 2 + 30),
                                            outline=(S.OUTLINE, 5), name='snowcap'),
                           move=fx.bob(T, 8, shift=k * 12), name='digit')
    # saturated cold colours: pale ones vanish on light chat backgrounds
    fw = [_firework(128, 140, T, 22, S.BLUE_L, seed=1, spark=S.SKY),
          _firework(386, 120, T, 78, S.VIOLET, seed=2, r=90, spark=S.LILAC),
          _firework(258, 152, T, 136, S.TEAL, seed=3, r=78, spark=S.MINT)]
    sparks = fx.sparkles([(60, 250, 16), (452, 236, 18)], T, start=60, gap=80, dur=36)
    return [fx.glow(256, 300, 228, alpha=0.26), fw, sparks, letters]
