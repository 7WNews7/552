"""Reusable effects and motion presets. Every animation returned here loops seamlessly over T."""
import math
import random

from .lottie import anim, loop, phase, part, group, gfill, fill, stroke, trim, ellipse, circle, val
from .geometry import sparkle_path, bbox_of, Bez
from . import style as S


# ------------------------------------------------------------- motion curves
def wave(T, lo, hi, cycles=1, ease='sine', shift=0):
    """lo -> hi -> lo, `cycles` times per loop. shift = time offset in frames."""
    keys = []
    for k in range(cycles):
        t0 = T * k / cycles
        keys += [(t0, lo, ease), (t0 + T / (2 * cycles), hi, ease)]
    keys.append((T, lo))
    a = anim(keys)
    return phase(a, shift, T) if shift else a


def swing(T, deg, cycles=1, shift=0, base=0):
    """Pendulum rotation base-deg .. base+deg, passing base at t=0 (moving towards +deg)."""
    a = wave(T, base - deg, base + deg, cycles)
    return phase(a, -T / (4 * cycles) + shift, T)


def bob(T, amp=10, cycles=1, shift=0, axis='y'):
    """[dx, dy] offset floating +-amp/2 around rest (use as `move=`)."""
    lo, hi = ([0, amp / 2], [0, -amp / 2]) if axis == 'y' else ([amp / 2, 0], [-amp / 2, 0])
    a = wave(T, lo, hi, cycles)
    return phase(a, -T / (4 * cycles) + shift, T)


def breathe(T, lo=97, hi=103, cycles=1, shift=0):
    """Uniform scale breathing (use as `s=`)."""
    return wave(T, lo, hi, cycles, shift=shift)


def pulse(T, t0, dur, lo, hi, up='out', down='in', peak=0.45):
    """Value rests at lo, rises to hi and returns during [t0, t0 + dur] (wraps around T)."""
    t0 = t0 % T
    tp = t0 + dur * peak
    keys = [(t0, lo, up), (tp, hi, down), (t0 + dur, lo, 'linear'), (t0 + T, lo)]
    return loop(keys, T)


def spin(T, turns=1, start=0, cw=True):
    """Continuous rotation; seamless for any whole number of `turns` (or symmetric shapes)."""
    end = start + 360 * turns * (1 if cw else -1)
    return anim((0, start, 'linear'), (T, end))


def wobble(T, t0, dur, amp, n=4, vector=None):
    """Damped oscillation inside [t0, t0+dur], rest (0) elsewhere. Scalar (rotation) by
    default; pass vector=(dx, dy) to get an [x, y] offset shake along that direction."""
    keys = [(t0, 0)]
    for k in range(1, 2 * n + 1):
        a = amp * (1 - (k - 1) / (2 * n)) * (1 if k % 2 else -1)
        keys.append((t0 + dur * k / (2 * n + 1), a))
    keys.append((t0 + dur, 0))
    keys.append((t0 + T, 0))
    if vector is not None:
        keys = [(t, [v * vector[0], v * vector[1]]) for t, v in keys]
    return loop([(t, v, 'sine') for t, v in keys], T)


def blink(T, t0, dur=12, closed=8):
    """Eye blink as a [sx, sy] scale (apply around the eye centre)."""
    return loop([(t0, [100, 100], 'in'), (t0 + dur * 0.45, [104, closed], 'hold'),
                 (t0 + dur * 0.55, [104, closed], 'out'), (t0 + dur, [100, 100], 'linear'),
                 (t0 + T, [100, 100])], T)


def rise(T, t0, dur, dy=-140, dx=0, s0=40, s1=100, alpha=100):
    """Something floating up and fading (hearts, Zz, steam, bubbles).
    Returns kwargs for group(): move, s, o."""
    move = loop([(t0, [0, 0], 'out'), (t0 + dur, [dx, dy], 'hold'), (t0 + T, [0, 0])], T)
    sc = loop([(t0, s0, 'outback'), (t0 + dur * 0.35, s1, 'io'), (t0 + dur, s1 * 0.9, 'hold'), (t0 + T, s0)], T)
    op = loop([(t0, 0, 'out'), (t0 + dur * 0.2, alpha, 'linear'), (t0 + dur * 0.6, alpha, 'in'),
               (t0 + dur, 0, 'hold'), (t0 + T, 0)], T)
    return {'move': move, 's': sc, 'o': op}


def draw_on(T, t0, dur, ease='out2'):
    """Trim 'end' going 0 -> 100 during [t0, t0+dur] and staying drawn (resets at the loop seam
    only if t0 > 0: then the stroke is hidden before t0)."""
    if t0 <= 0:
        return anim((0, 0, ease), (dur, 100, 'hold'), (T, 100))
    return anim((0, 0, 'hold'), (t0, 0, ease), (t0 + dur, 100, 'hold'), (T, 100))


def keys_loop(T, keys, ease='io'):
    """Shorthand for loop() with explicit keys within one period."""
    return loop(keys, T, ease=ease)


# ------------------------------------------------------------- light & glow
def glow(cx, cy, r, color=S.SKY, alpha=0.45, o=None, s=None, name='glow'):
    """Soft radial halo (keep alpha low: emoji also sit on white chat backgrounds)."""
    g = gfill([(0, color), (1, color)], [cx, cy], [cx + r, cy], kind='radial',
              opacity=[(0, alpha), (0.4, alpha * 0.55), (1, 0)])
    return part(ellipse(cx, cy, 2 * r, 2 * r), fill=g, pivot=(cx, cy), o=o, s=s, name=name)


def sparkle(cx, cy, R, T, t0=0, dur=40, color=S.WHITE, turn=90, halo=True, k=0.16, lo=0, hi=100):
    """Twinkling 4-point star: grows from lo to hi and back during [t0, t0+dur]."""
    sc = pulse(T, t0, dur, lo, hi, up='out', down='in', peak=0.4)
    rot = anim((0, 0, 'linear'), (T, turn)) if turn else 0
    items = []
    if halo:
        items.append(glow(cx, cy, R * 1.1, color=S.ICE_L, alpha=0.55, name='spark_halo'))
    items.append(part(sparkle_path(cx, cy, R, k), fill=color, name='spark'))
    return group(items, pivot=(cx, cy), s=sc, r=rot, name='sparkle')


def sparkles(points, T, R=26, dur=40, color=S.WHITE, gap=None, start=0, **kw):
    """Several sparkles that twinkle one after another. points: [(x, y)] or [(x, y, R)]."""
    out = []
    n = len(points)
    gap = T / n if gap is None else gap
    for k, p in enumerate(points):
        r = p[2] if len(p) > 2 else R
        out.append(sparkle(p[0], p[1], r, T, t0=start + k * gap, dur=dur, color=color, **kw))
    return out


def ring_pulse(cx, cy, r0, r1, T, t0=0, dur=50, color=S.ICE_L, w0=14, w1=2, alpha=90):
    """Expanding ring that fades out (a 'ping')."""
    size = loop([(t0, [2 * r0, 2 * r0], 'out'), (t0 + dur, [2 * r1, 2 * r1], 'hold'),
                 (t0 + T, [2 * r0, 2 * r0])], T)
    width = loop([(t0, w0, 'out'), (t0 + dur, w1, 'hold'), (t0 + T, w0)], T)
    op = loop([(t0, 0, 'out'), (t0 + dur * 0.15, alpha, 'in'), (t0 + dur, 0, 'hold'), (t0 + T, 0)], T)
    return part(ellipse(cx, cy, size), stroke=stroke(color, width, o=op), name='ring')


def shine(shapes, T, t0=10, dur=46, angle=20, width=0.22, alpha=0.8, color=S.WHITE, bbox=None):
    """Glossy light band sweeping across `shapes` (no masks: an animated gradient fill
    whose transparent ends hide everything except the band)."""
    if bbox is None:
        bbox = bbox_of([p for p in shapes if isinstance(p, Bez)])
    x0, y0, x1, y1 = bbox
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    L = math.hypot(x1 - x0, y1 - y0)
    a = math.radians(angle)
    d = (math.cos(a), math.sin(a))

    def se(c):
        return [c[0] - d[0] * L / 2, c[1] - d[1] * L / 2], [c[0] + d[0] * L / 2, c[1] + d[1] * L / 2]

    s0, e0 = se((cx - d[0] * L, cy - d[1] * L))
    s1, e1 = se((cx + d[0] * L, cy + d[1] * L))
    t1 = min(t0 + dur, T)
    keys_s = [(0, s0, 'hold'), (t0, s0, 'sine'), (t1, s1, 'hold'), (T, s1)] if t0 > 0 else \
        [(0, s0, 'sine'), (t1, s1, 'hold'), (T, s1)]
    keys_e = [(0, e0, 'hold'), (t0, e0, 'sine'), (t1, e1, 'hold'), (T, e1)] if t0 > 0 else \
        [(0, e0, 'sine'), (t1, e1, 'hold'), (T, e1)]
    w = width / 2
    g = gfill([(0, color), (1, color)], anim(keys_s), anim(keys_e),
              opacity=[(0, 0), (0.5 - w, 0), (0.5 - w * 0.35, alpha * 0.6), (0.5, alpha),
                       (0.5 + w * 0.35, alpha * 0.6), (0.5 + w, 0), (1, 0)])
    return part(*shapes, fill=g, name='shine')


def snowfall(T, n, box, r=(5, 10), seed=7, color=S.WHITE, alpha=95, sway=14, glow_r=0):
    """Snow particles falling through box=(x0, y0, x1, y1) once per loop, staggered."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for k in range(n):
        x = x0 + (x1 - x0) * (k + rnd.uniform(0.15, 0.85)) / n
        rad = rnd.uniform(*r)
        ph = T * k / n + rnd.uniform(-0.2, 0.2) * T / n
        fall = phase(anim((0, [0, 0], 'linear'), (T, [0, y1 - y0])), ph, T)
        op = phase(anim((0, 0, 'out'), (T * 0.18, alpha, 'linear'), (T * 0.75, alpha, 'in'), (T, 0)), ph, T)
        flake = part(circle(x, y0, rad), fill=color, name='flake')
        inner = group(flake, pivot=(x, y0), move=wave(T, [-sway, 0], [sway, 0], 1, shift=rnd.uniform(0, T)),
                      name='sway')
        out.append(group(inner, pivot=(x, y0), move=fall, o=op, name='snow'))
    return out


def burst(cx, cy, T, t0, n, r0, r1, size=14, color=S.WHITE, dur=34, rot=0, shape='dot', seed=3):
    """Particles flying out radially once per loop (confetti / impact sparks)."""
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        a = math.radians(rot + 360 * k / n + rnd.uniform(-8, 8))
        rr1 = r1 * rnd.uniform(0.85, 1.0)
        mv = loop([(t0, [math.cos(a) * r0, math.sin(a) * r0], 'out2'),
                   (t0 + dur, [math.cos(a) * rr1, math.sin(a) * rr1], 'hold'),
                   (t0 + T, [math.cos(a) * r0, math.sin(a) * r0])], T)
        sc = loop([(t0, 0, 'out'), (t0 + dur * 0.25, 100, 'in'), (t0 + dur, 0, 'hold'), (t0 + T, 0)], T)
        if shape == 'spark':
            body = part(sparkle_path(cx, cy, size), fill=color, name='p')
        else:
            body = part(circle(cx, cy, size / 2), fill=color, name='p')
        out.append(group(body, pivot=(cx, cy), move=mv, s=sc, name='particle'))
    return out
