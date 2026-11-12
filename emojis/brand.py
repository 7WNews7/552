"""001-010: KRONOS brand and staff roles."""
from kit.registry import emoji
from kit.lottie import group
from kit.motifs import crown
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
