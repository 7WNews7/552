"""Minimal Lottie builder tuned for Telegram TGS: 512x512, 60 fps, <= 180 frames.

Only features Telegram allows are produced: shape layers, groups, paths, ellipses,
rects, solid/gradient fills, solid strokes, trim paths. No masks, mattes, effects,
expressions, star shapes, repeaters, merge paths, gradient strokes or skew.
"""
import math

FPS = 60
SIZE = 512


# ---------------------------------------------------------------- colours
def hex2rgb(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    return [int(h[k:k + 2], 16) / 255.0 for k in (0, 2, 4)]


def rgb(c):
    return hex2rgb(c) if isinstance(c, str) else [float(x) for x in c[:3]]


def mix(c1, c2, t):
    a, b = rgb(c1), rgb(c2)
    return '#%02x%02x%02x' % tuple(int(round((x + (y - x) * t) * 255)) for x, y in zip(a, b))


# ---------------------------------------------------------------- properties
def val(v):
    return {'a': 0, 'k': v}


def is_anim(p):
    return isinstance(p, dict) and p.get('a') == 1


def prop(v):
    if isinstance(v, dict) and 'a' in v and 'k' in v:
        return v
    return val(v)


# cubic-bezier timing curves: (out handle of key A, in handle of key B)
EASE = {
    'linear': ((0.167, 0.167), (0.833, 0.833)),
    'io': ((0.42, 0.0), (0.58, 1.0)),
    'sine': ((0.37, 0.0), (0.63, 1.0)),
    'soft': ((0.33, 0.0), (0.67, 1.0)),
    'in': ((0.42, 0.0), (1.0, 1.0)),
    'in2': ((0.6, 0.0), (0.9, 0.6)),
    'out': ((0.0, 0.0), (0.58, 1.0)),
    'out2': ((0.16, 1.0), (0.3, 1.0)),
    'outback': ((0.34, 1.56), (0.64, 1.0)),
    'outback2': ((0.18, 1.9), (0.5, 1.0)),
    'inback': ((0.36, 0.0), (0.66, -0.56)),
}


def _wrapv(v):
    if isinstance(v, dict):
        return [v]
    if isinstance(v, (int, float)):
        return [v]
    return [float(x) for x in v]


def _set_ease(k, e):
    k.pop('h', None)
    if e == 'hold':
        k.pop('o', None)
        k.pop('i', None)
        k['h'] = 1
        return
    (ox, oy), (ix, iy) = EASE[e] if isinstance(e, str) else e
    k['o'] = {'x': [ox], 'y': [oy]}
    k['i'] = {'x': [ix], 'y': [iy]}


def anim(*keys, ease='io'):
    """anim((t, v), (t, v, 'outback'), ...) -> animated property.

    The optional third item is the easing of the segment that starts at that key
    (a name from EASE, a ((ox, oy), (ix, iy)) tuple, or 'hold').
    """
    if len(keys) == 1 and isinstance(keys[0], list):
        keys = keys[0]
    out = []
    for idx, key in enumerate(keys):
        t, v = key[0], key[1]
        k = {'t': t, 's': _wrapv(v)}
        if idx < len(keys) - 1:
            _set_ease(k, key[2] if len(key) > 2 else ease)
        out.append(k)
    return {'a': 1, 'k': out}


def sample(fn, T, step=3, ease='linear'):
    """Keyframes sampled from a periodic function fn(t) (fn(0) should equal fn(T))."""
    keys, t = [], 0
    while t < T - 1e-9:
        keys.append((t, fn(t), ease))
        t += step
    keys.append((T, fn(T)))
    return anim(keys)


# ---- evaluating / splitting / phase-shifting keyframes (for staggered loops)
def _bez1(u, a, b):
    return 3 * (1 - u) * (1 - u) * u * a + 3 * (1 - u) * u * u * b + u * u * u


def _handles(k):
    if k.get('h'):
        return None
    o, i = k['o'], k['i']
    f = lambda q: q[0] if isinstance(q, list) else q
    return (f(o['x']), f(o['y'])), (f(i['x']), f(i['y']))


def _solve_u(x, p1, p2):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if _bez1(mid, p1[0], p2[0]) < x:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _lerp_val(a, b, y):
    if a and isinstance(a[0], dict):
        sa, sb = a[0], b[0]
        sh = {'c': sa.get('c', True)}
        for key in ('i', 'o', 'v'):
            sh[key] = [[pa[0] + (pb[0] - pa[0]) * y, pa[1] + (pb[1] - pa[1]) * y]
                       for pa, pb in zip(sa[key], sb[key])]
        return [sh]
    return [x + (z - x) * y for x, z in zip(a, b)]


def _split(ka, kb, t):
    x = (t - ka['t']) / (kb['t'] - ka['t'])
    hd = _handles(ka)
    if hd is None:
        c_start = {'t': t, 's': ka['s'], 'h': 1}
        return dict(ka), {'t': t, 's': ka['s']}, c_start
    p1, p2 = hd
    u = _solve_u(x, p1, p2)
    L = lambda a, b: (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    P0, P3 = (0.0, 0.0), (1.0, 1.0)
    A, B, C = L(P0, p1), L(p1, p2), L(p2, P3)
    D, E = L(A, B), L(B, C)
    F = L(D, E)
    xc, yc = F

    def norm(pt, x0, y0, x1, y1):
        nx = (pt[0] - x0) / (x1 - x0) if abs(x1 - x0) > 1e-9 else 0.5
        ny = (pt[1] - y0) / (y1 - y0) if abs(y1 - y0) > 1e-9 else nx
        return (nx, ny)

    vc = _lerp_val(ka['s'], kb['s'], yc)
    left = dict(ka)
    _set_ease(left, (norm(A, 0, 0, xc, yc), norm(D, 0, 0, xc, yc)))
    c_start = {'t': t, 's': vc}
    _set_ease(c_start, (norm(E, xc, yc, 1, 1), norm(C, xc, yc, 1, 1)))
    return left, {'t': t, 's': vc}, c_start


def _same(a, b):
    if a and isinstance(a[0], dict):
        return a == b
    return all(abs(x - y) < 1e-6 for x, y in zip(a, b))


def phase(a, dt, T):
    """Time-shift a looping animation (keys spanning exactly 0..T) by dt frames, wrapping.

    If the values at 0 and T differ (saw-tooth motion such as falling snow or a
    0..360 spin) the wrap point becomes an instant jump."""
    if not is_anim(a):
        return a
    dt %= T
    if dt < 1e-6 or T - dt < 1e-6:
        return a
    ks = [dict(k) for k in a['k']]
    assert abs(ks[0]['t']) < 1e-6 and abs(ks[-1]['t'] - T) < 1e-6, 'phase() needs keys spanning 0..T'
    cut = T - dt
    idx = max(j for j in range(len(ks) - 1) if ks[j]['t'] <= cut + 1e-9)
    ka, kb = ks[idx], ks[idx + 1]
    if abs(ka['t'] - cut) < 1e-6:
        left = ks[:idx] + [{'t': cut, 's': ka['s']}]
        right = ks[idx:]
    else:
        l, ce, cs = _split(ka, kb, cut)
        left = ks[:idx] + [l, ce]
        right = [cs] + ks[idx + 1:]
    new = []
    for k in right:
        k2 = dict(k)
        k2['t'] = k['t'] - cut
        new.append(k2)
    if _same(new[-1]['s'], left[0]['s']):
        new.pop()
        jump = 0.0
    else:
        new[-1]['h'] = 1
        jump = 0.01
    for n, k in enumerate(left):
        k2 = dict(k)
        k2['t'] = k['t'] + dt + (jump if n == 0 else 0.0)
        new.append(k2)
    for key in ('o', 'i', 'h'):
        new[-1].pop(key, None)
    return {'a': 1, 'k': new}


def loop(keys, T, ease='io'):
    """Like anim(), but keys may span any window of length T (e.g. 90..270 for T=180);
    the result is wrapped into 0..T. First and last values must match."""
    t0 = keys[0][0]
    shifted = [(k[0] - t0,) + tuple(k[1:]) for k in keys]
    assert abs(shifted[-1][0] - T) < 1e-6, 'loop() keys must span exactly T frames'
    return phase(anim(shifted, ease=ease), t0, T)


def map_anim(a, fn):
    """Apply fn to every value (as list) of a static or animated property."""
    if is_anim(a):
        out = {'a': 1, 'k': []}
        for k in a['k']:
            k2 = dict(k)
            k2['s'] = _wrapv(fn(list(k['s'])))
            out['k'].append(k2)
        return out
    v = a['k'] if isinstance(a, dict) else a
    return val(fn(_wrapv(v)))


# ---------------------------------------------------------------- shapes & styles
def ellipse(cx, cy, w, h=None, name='ellipse'):
    """Ellipse centred at (cx, cy). Pass animated p / s via prop dicts if needed."""
    p = cx if isinstance(cx, dict) else val([cx, cy])
    if isinstance(w, dict):
        s = w
    else:
        s = val([w, w if h is None else h])
    return {'ty': 'el', 'd': 1, 'p': p, 's': s, 'nm': name}


def circle(cx, cy, r, name='circle'):
    return ellipse(cx, cy, 2 * r, 2 * r, name=name)


def rect(cx, cy, w, h, r=0, name='rect'):
    p = cx if isinstance(cx, dict) else val([cx, cy])
    s = w if isinstance(w, dict) else val([w, h])
    return {'ty': 'rc', 'd': 1, 'p': p, 's': s, 'r': prop(r), 'nm': name}


def fill(c, o=100, rule=1):
    col = c if isinstance(c, dict) else val(rgb(c) + [1])
    return {'ty': 'fl', 'c': col, 'o': prop(o), 'r': rule, 'bm': 0, 'nm': 'fill'}


def color_anim(*keys, ease='io'):
    """Animated colour: color_anim((t, '#hex'), ...)."""
    if len(keys) == 1 and isinstance(keys[0], list):
        keys = keys[0]
    return anim([(k[0], rgb(k[1]) + [1]) + tuple(k[2:]) for k in keys], ease=ease)


def stroke(c, w, o=100, cap='round', join='round', name='stroke'):
    col = c if isinstance(c, dict) else val(rgb(c) + [1])
    caps = {'butt': 1, 'round': 2, 'square': 3}
    joins = {'miter': 1, 'round': 2, 'bevel': 3}
    return {'ty': 'st', 'c': col, 'o': prop(o), 'w': prop(w), 'lc': caps[cap],
            'lj': joins[join], 'ml': 4, 'bm': 0, 'nm': name}


def gstops(stops, opacity=None):
    """stops: [(offset, colour)], opacity: optional [(offset, alpha 0..1)]."""
    flat = []
    for off, c in stops:
        flat += [off] + rgb(c)
    if opacity:
        for off, a in opacity:
            flat += [off, a]
    return flat


def gfill(stops, s, e, kind='linear', opacity=None, o=100, h=0, a=0, rule=1):
    """Gradient fill. s / e are start / end points (static [x, y] or animated)."""
    g = stops if isinstance(stops, dict) else val(gstops(stops, opacity))
    out = {'ty': 'gf', 'o': prop(o), 'r': rule, 'bm': 0, 'nm': 'gradient',
           'g': {'p': len(stops) if not isinstance(stops, dict) else stops['_p'], 'k': g},
           's': prop(s), 'e': prop(e), 't': 1 if kind == 'linear' else 2}
    if kind != 'linear':
        out['h'] = prop(h)
        out['a'] = prop(a)
    return out


def trim(s=0, e=100, o=0, mode=1):
    return {'ty': 'tm', 's': prop(s), 'e': prop(e), 'o': prop(o), 'm': mode, 'nm': 'trim'}


def tr(p=(0, 0), a=(0, 0), s=(100, 100), r=0, o=100):
    return {'ty': 'tr', 'p': prop(list(p) if not isinstance(p, dict) else p),
            'a': prop(list(a) if not isinstance(a, dict) else a),
            's': prop(list(s) if not isinstance(s, dict) else s),
            'r': prop(r), 'o': prop(o), 'sk': val(0), 'sa': val(0), 'nm': 'Transform'}


def _scale(s):
    if s is None:
        return [100, 100]
    if isinstance(s, (int, float)):
        return [s, s]
    if is_anim(s):
        return map_anim(s, lambda v: v * 2 if len(v) == 1 else v)
    return list(s)


def _shape_item(s):
    if hasattr(s, 'sh'):
        return s.sh()
    return s


def _flatten(xs):
    out = []
    for x in xs:
        if x is None:
            continue
        if isinstance(x, (list, tuple)):
            out += _flatten(x)
        else:
            out.append(x)
    return out


def _transform(pivot, pos, move, s, r, o):
    pivot = list(pivot)
    if pos is None:
        pos = pivot
    if move is not None:
        base = pos if not isinstance(pos, dict) else None
        if base is None:
            raise ValueError('use either pos (animated) or move, not both')
        pos = map_anim(prop(move), lambda d: [base[0] + d[0], base[1] + d[1]])
    return tr(p=pos, a=pivot, s=_scale(s), r=0 if r is None else r, o=100 if o is None else o)


def part(*shapes, fill=None, stroke=None, outline=None, extra=None, name='part',
         pivot=(0, 0), pos=None, move=None, s=None, r=None, o=None, trim=None):
    """One drawable: shapes + styles.

    fill    -- colour '#hex' or a gfill()/fill() dict
    stroke  -- stroke dict drawn ON TOP of the fill (centred)
    outline -- (colour, visible_width) or a number: stroke drawn BEHIND the fill, so
               only the outer half shows (sticker-like contour)
    extra   -- additional style items (list), drawn above everything else
    """
    from . import style as _st  # late import (palette)
    it = [_shape_item(x) for x in _flatten(shapes)]
    if trim is not None:
        it.append(trim)
    styles = []
    if extra:
        styles += list(extra)
    if stroke is not None:
        styles.append(stroke)
    if fill is not None:
        styles.append(globals()['fill'](fill) if isinstance(fill, str) else fill)
    if outline:
        if isinstance(outline, (int, float)):
            outline = (_st.OUTLINE, outline)
        col, w = outline
        styles.append(globals()['stroke'](col, w * 2 if not isinstance(w, dict) else w, name='outline'))
    it += styles
    it.append(_transform(pivot, pos, move, s, r, o))
    return {'ty': 'gr', 'nm': name, 'np': len(it) - 1, 'cix': 2, 'bm': 0, 'it': it}


def group(*children, name='group', pivot=(0, 0), pos=None, move=None, s=None, r=None, o=None):
    """Children in painter order (first = furthest back). Transform pivots around `pivot`;
    `move` is an (animated) [dx, dy] offset added to the pivot."""
    kids = _flatten(children)
    kids.reverse()  # Lottie draws the first item on top
    it = kids + [_transform(pivot, pos, move, s, r, o)]
    return {'ty': 'gr', 'nm': name, 'np': len(it) - 1, 'cix': 2, 'bm': 0, 'it': it}


# ---------------------------------------------------------------- document
def shape_layer(items, name='emoji', op=120, ind=1, pos=(256, 256), anchor=(256, 256)):
    kids = _flatten(items)
    kids.reverse()
    return {
        'ddd': 0, 'ind': ind, 'ty': 4, 'nm': name, 'sr': 1,
        'ks': {'o': val(100), 'r': val(0), 'p': val([pos[0], pos[1], 0]),
               'a': val([anchor[0], anchor[1], 0]), 's': val([100, 100, 100])},
        'ao': 0, 'shapes': kids, 'ip': 0, 'op': op, 'st': 0, 'bm': 0,
    }


def _round(o, nd=3):
    if isinstance(o, float):
        r = round(o, nd)
        return int(r) if r == int(r) else r
    if isinstance(o, list):
        return [_round(x, nd) for x in o]
    if isinstance(o, dict):
        return {k: _round(v, nd) for k, v in o.items()}
    return o


def animation(items, name='emoji', op=120, offset=0, extra_frames=0):
    """Full document. `offset` grows the canvas on every side (validation of bounds),
    `extra_frames` extends op (loop-seam validation)."""
    size = SIZE + 2 * offset
    layer = shape_layer(items, name=name, op=op + extra_frames,
                        pos=(256 + offset, 256 + offset))
    doc = {'tgs': 1, 'v': '5.7.4', 'fr': FPS, 'ip': 0, 'op': op + extra_frames,
           'w': size, 'h': size, 'nm': name, 'ddd': 0, 'assets': [], 'layers': [layer]}
    return _round(doc)
