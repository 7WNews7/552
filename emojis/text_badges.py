"""033-042: text badges (letters are glyph outlines, Telegram forbids text layers)."""
from kit.registry import emoji
from kit.lottie import part, group, anim
from kit.motifs import crown
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
