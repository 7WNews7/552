"""061-080: winter."""
import math

from kit.registry import emoji
from kit.lottie import part, group, anim, stroke
from kit.geometry import line, circle_path, rounded
from kit import fx, style as S


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
