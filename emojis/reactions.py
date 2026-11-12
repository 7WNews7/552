"""011-032: reactions and symbols."""
from kit.registry import emoji
from kit.lottie import part, group, anim, stroke, trim
from kit.geometry import P, circle_path, heart_path, polyline
from kit import fx, style as S


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
