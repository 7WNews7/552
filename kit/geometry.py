"""Bezier paths: SVG path parsing, transforms and common shape builders."""
import math
import re

from .lottie import val


class Bez:
    """Lottie bezier path. v = vertices, i / o = in / out tangents RELATIVE to vertices."""

    def __init__(self, v=None, i=None, o=None, closed=True):
        self.v = [list(map(float, p)) for p in (v or [])]
        n = len(self.v)
        self.i = [list(map(float, p)) for p in i] if i else [[0.0, 0.0] for _ in range(n)]
        self.o = [list(map(float, p)) for p in o] if o else [[0.0, 0.0] for _ in range(n)]
        self.c = closed

    def add(self, p, i=(0, 0), o=(0, 0)):
        self.v.append([float(p[0]), float(p[1])])
        self.i.append([float(i[0]), float(i[1])])
        self.o.append([float(o[0]), float(o[1])])
        return self

    def copy(self):
        return Bez([p[:] for p in self.v], [p[:] for p in self.i], [p[:] for p in self.o], self.c)

    # -- transforms (operate on absolute control points so any affine map is exact)
    def map(self, fn):
        out = Bez(closed=self.c)
        for v, i, o in zip(self.v, self.i, self.o):
            nv = fn(v[0], v[1])
            ni = fn(v[0] + i[0], v[1] + i[1])
            no = fn(v[0] + o[0], v[1] + o[1])
            out.add(nv, (ni[0] - nv[0], ni[1] - nv[1]), (no[0] - nv[0], no[1] - nv[1]))
        return out

    def translate(self, dx, dy):
        return self.map(lambda x, y: (x + dx, y + dy))

    def scale(self, sx, sy=None, cx=0.0, cy=0.0):
        sy = sx if sy is None else sy
        return self.map(lambda x, y: (cx + (x - cx) * sx, cy + (y - cy) * sy))

    def rotate(self, deg, cx=0.0, cy=0.0):
        a = math.radians(deg)
        ca, sa = math.cos(a), math.sin(a)
        return self.map(lambda x, y: (cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca))

    def mirror_x(self, cx=256.0):
        return self.map(lambda x, y: (2 * cx - x, y)).reversed()

    def mirror_y(self, cy=256.0):
        return self.map(lambda x, y: (x, 2 * cy - y)).reversed()

    def reversed(self):
        n = len(self.v)
        out = Bez(closed=self.c)
        for k in range(n - 1, -1, -1):
            out.add(self.v[k], self.o[k], self.i[k])
        return out

    def bbox(self):
        xs, ys = [], []
        for v, i, o in zip(self.v, self.i, self.o):
            for p in (v, (v[0] + i[0], v[1] + i[1]), (v[0] + o[0], v[1] + o[1])):
                xs.append(p[0])
                ys.append(p[1])
        return min(xs), min(ys), max(xs), max(ys)

    def data(self):
        return {'i': [p[:] for p in self.i], 'o': [p[:] for p in self.o],
                'v': [p[:] for p in self.v], 'c': self.c}

    def sh(self, name='path'):
        return {'ty': 'sh', 'd': 1, 'ks': val(self.data()), 'nm': name}


def bbox_of(paths):
    bs = [p.bbox() for p in paths]
    return min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)


def morph(*keys, ease='io'):
    """Animated path: morph((t, Bez), (t, Bez, 'ease'), ...). All Bez need equal vertex counts."""
    from .lottie import anim
    if len(keys) == 1 and isinstance(keys[0], list):
        keys = keys[0]
    n = len(keys[0][1].v)
    for k in keys:
        assert len(k[1].v) == n, 'morph(): vertex counts differ'
    data = anim([(k[0], k[1].data()) + tuple(k[2:]) for k in keys], ease=ease)
    return {'ty': 'sh', 'd': 1, 'ks': data, 'nm': 'morph'}


# ---------------------------------------------------------------- SVG path parser
_TOK = re.compile(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?')


def _arc(x1, y1, rx, ry, phi, fa, fs, x2, y2):
    if rx == 0 or ry == 0:
        return [((x1, y1), (x2, y2), (x2, y2))]
    phi = math.radians(phi)
    cp, sp = math.cos(phi), math.sin(phi)
    dx2, dy2 = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = cp * dx2 + sp * dy2, -sp * dx2 + cp * dy2
    rx, ry = abs(rx), abs(ry)
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        rx *= math.sqrt(lam)
        ry *= math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    coef = math.sqrt(max(0.0, num / den)) if den else 0.0
    if fa == fs:
        coef = -coef
    cxp, cyp = coef * rx * y1p / ry, -coef * ry * x1p / rx
    cx = cp * cxp - sp * cyp + (x1 + x2) / 2
    cy = sp * cxp + cp * cyp + (y1 + y2) / 2

    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a

    th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dth > 0:
        dth -= 2 * math.pi
    elif fs and dth < 0:
        dth += 2 * math.pi
    nseg = max(1, int(math.ceil(abs(dth) / (math.pi / 2) - 1e-9)))
    delta = dth / nseg
    t = 4.0 / 3.0 * math.tan(delta / 4)

    def pt(ux, uy):
        return (cx + rx * cp * ux - ry * sp * uy, cy + rx * sp * ux + ry * cp * uy)

    segs = []
    for k in range(nseg):
        a0 = th1 + k * delta
        a1 = a0 + delta
        c1 = pt(math.cos(a0) - t * math.sin(a0), math.sin(a0) + t * math.cos(a0))
        c2 = pt(math.cos(a1) + t * math.sin(a1), math.sin(a1) - t * math.cos(a1))
        p = pt(math.cos(a1), math.sin(a1))
        segs.append((c1, c2, p))
    return segs


def svg(d):
    """Parse an SVG path 'd' string into a list of Bez (one per subpath)."""
    toks = _TOK.findall(d)
    paths = []
    cur = None
    x = y = 0.0
    sx = sy = 0.0
    prev_c2 = None
    prev_q = None
    k = 0
    cmd = None

    def num():
        nonlocal k
        v = float(toks[k])
        k += 1
        return v

    def has_num():
        return k < len(toks) and not toks[k].isalpha()

    def finish(closed):
        nonlocal cur
        if cur is None or not cur.v:
            cur = None
            return
        if closed:
            if len(cur.v) > 1 and abs(cur.v[-1][0] - cur.v[0][0]) < 1e-6 and abs(cur.v[-1][1] - cur.v[0][1]) < 1e-6:
                cur.i[0] = cur.i[-1]
                cur.v.pop()
                cur.i.pop()
                cur.o.pop()
            cur.c = True
        else:
            cur.c = False
        paths.append(cur)
        cur = None

    def cubic(c1, c2, p):
        nonlocal x, y
        cur.o[-1] = [c1[0] - x, c1[1] - y]
        cur.add(p, (c2[0] - p[0], c2[1] - p[1]))
        x, y = p

    while k < len(toks):
        if toks[k].isalpha():
            cmd = toks[k]
            k += 1
        C = cmd.upper()
        rel = cmd.islower()
        if C == 'Z':
            finish(True)
            x, y = sx, sy
            prev_c2 = prev_q = None
            continue
        if C == 'M':
            if cur is not None:
                finish(False)
            nx, ny = num(), num()
            if rel:
                nx, ny = nx + x, ny + y
            x, y = sx, sy = nx, ny
            cur = Bez(closed=False).add((x, y))
            cmd = 'l' if rel else 'L'
            prev_c2 = prev_q = None
            continue
        if cur is None:
            cur = Bez(closed=False).add((x, y))
        if C == 'L':
            nx, ny = num(), num()
            if rel:
                nx, ny = nx + x, ny + y
            cur.add((nx, ny))
            x, y = nx, ny
            prev_c2 = prev_q = None
        elif C == 'H':
            nx = num() + (x if rel else 0)
            cur.add((nx, y))
            x = nx
            prev_c2 = prev_q = None
        elif C == 'V':
            ny = num() + (y if rel else 0)
            cur.add((x, ny))
            y = ny
            prev_c2 = prev_q = None
        elif C == 'C':
            a = [num() for _ in range(6)]
            if rel:
                a = [a[0] + x, a[1] + y, a[2] + x, a[3] + y, a[4] + x, a[5] + y]
            cubic((a[0], a[1]), (a[2], a[3]), (a[4], a[5]))
            prev_c2 = (a[2], a[3])
            prev_q = None
        elif C == 'S':
            a = [num() for _ in range(4)]
            if rel:
                a = [a[0] + x, a[1] + y, a[2] + x, a[3] + y]
            c1 = (2 * x - prev_c2[0], 2 * y - prev_c2[1]) if prev_c2 else (x, y)
            cubic(c1, (a[0], a[1]), (a[2], a[3]))
            prev_c2 = (a[0], a[1])
            prev_q = None
        elif C in 'QT':
            if C == 'Q':
                a = [num() for _ in range(4)]
                if rel:
                    a = [a[0] + x, a[1] + y, a[2] + x, a[3] + y]
                q = (a[0], a[1])
                p = (a[2], a[3])
            else:
                a = [num(), num()]
                if rel:
                    a = [a[0] + x, a[1] + y]
                q = (2 * x - prev_q[0], 2 * y - prev_q[1]) if prev_q else (x, y)
                p = (a[0], a[1])
            c1 = (x + 2 / 3 * (q[0] - x), y + 2 / 3 * (q[1] - y))
            c2 = (p[0] + 2 / 3 * (q[0] - p[0]), p[1] + 2 / 3 * (q[1] - p[1]))
            cubic(c1, c2, p)
            prev_q = q
            prev_c2 = None
        elif C == 'A':
            rx, ry, phi, fa, fs, nx, ny = [num() for _ in range(7)]
            if rel:
                nx, ny = nx + x, ny + y
            for c1, c2, p in _arc(x, y, rx, ry, phi, int(fa), int(fs), nx, ny):
                cubic(c1, c2, p)
            prev_c2 = prev_q = None
        else:
            raise ValueError('unsupported SVG command ' + cmd)
    if cur is not None:
        finish(False)
    return paths


def P(d):
    """Single-subpath convenience: P('M ... Z') -> Bez."""
    ps = svg(d)
    assert len(ps) == 1, 'P() expects exactly one subpath, use svg() for several'
    return ps[0]


# ---------------------------------------------------------------- builders
def poly(points, closed=True):
    return Bez(points, closed=closed)


def rounded(points, radius, closed=True):
    """Polygon with rounded corners (radius in px, clamped per corner)."""
    n = len(points)
    out = Bez(closed=closed)
    rad = radius if isinstance(radius, (list, tuple)) else [radius] * n
    for k in range(n):
        p = points[k]
        if not closed and (k == 0 or k == n - 1):
            out.add(p)
            continue
        a = points[k - 1]
        b = points[(k + 1) % n]
        da = math.hypot(a[0] - p[0], a[1] - p[1])
        db = math.hypot(b[0] - p[0], b[1] - p[1])
        r = min(rad[k], da * 0.5, db * 0.5)
        if r <= 0:
            out.add(p)
            continue
        ua = ((a[0] - p[0]) / da, (a[1] - p[1]) / da)
        ub = ((b[0] - p[0]) / db, (b[1] - p[1]) / db)
        p1 = (p[0] + ua[0] * r, p[1] + ua[1] * r)
        p2 = (p[0] + ub[0] * r, p[1] + ub[1] * r)
        kk = 0.55
        out.add(p1, (0, 0), (-ua[0] * r * kk, -ua[1] * r * kk))
        out.add(p2, (-ub[0] * r * kk, -ub[1] * r * kk), (0, 0))
    return out


def star(cx, cy, n, ro, ri, rot=-90.0, round_out=0.0, round_in=0.0):
    """n-pointed star as a path (Telegram forbids the native star shape)."""
    pts = []
    for k in range(2 * n):
        r = ro if k % 2 == 0 else ri
        a = math.radians(rot + 180.0 * k / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    if round_out or round_in:
        return rounded(pts, [round_out if k % 2 == 0 else round_in for k in range(2 * n)])
    return Bez(pts)


def sparkle_path(cx, cy, R, k=0.16, ry=None):
    """Four-point twinkle star with concave sides."""
    ry = R if ry is None else ry
    kx, ky = R * k, ry * k
    b = Bez()
    b.add((cx, cy - ry), (0, 0), (0, ry - ky))
    b.add((cx + R, cy), (-(R - kx), 0), (-(R - kx), 0))
    b.add((cx, cy + ry), (0, -(ry - ky)), (0, -(ry - ky)))
    b.add((cx - R, cy), (R - kx, 0), (R - kx, 0))
    b.i[0] = [0, ry - ky]
    return b


def heart_path(cx, cy, w, h=None):
    """Classic heart, bounding box ~ w x h, centred at (cx, cy)."""
    h = w * 0.9 if h is None else h
    x0, y0 = cx - w / 2, cy - h / 2
    X = lambda u: x0 + u * w
    Y = lambda v: y0 + v * h
    return P(
        f'M {X(0.5)} {Y(0.22)} '
        f'C {X(0.5)} {Y(0.08)} {X(0.38)} {Y(0.0)} {X(0.26)} {Y(0.0)} '
        f'C {X(0.1)} {Y(0.0)} {X(0.0)} {Y(0.13)} {X(0.0)} {Y(0.3)} '
        f'C {X(0.0)} {Y(0.56)} {X(0.26)} {Y(0.74)} {X(0.5)} {Y(1.0)} '
        f'C {X(0.74)} {Y(0.74)} {X(1.0)} {Y(0.56)} {X(1.0)} {Y(0.3)} '
        f'C {X(1.0)} {Y(0.13)} {X(0.9)} {Y(0.0)} {X(0.74)} {Y(0.0)} '
        f'C {X(0.62)} {Y(0.0)} {X(0.5)} {Y(0.08)} {X(0.5)} {Y(0.22)} Z')


def circle_path(cx, cy, r, ry=None, start=-90.0):
    """Circle / ellipse as a 4-vertex path (useful for morphing)."""
    ry = r if ry is None else ry
    kx, ky = r * 0.5523, ry * 0.5523
    b = Bez()
    b.add((cx, cy - ry), (-kx, 0), (kx, 0))
    b.add((cx + r, cy), (0, -ky), (0, ky))
    b.add((cx, cy + ry), (kx, 0), (-kx, 0))
    b.add((cx - r, cy), (0, ky), (0, -ky))
    if start != -90.0:
        b = b.rotate(start + 90.0, cx, cy)
    return b


def line(x1, y1, x2, y2):
    return Bez([(x1, y1), (x2, y2)], closed=False)


def polyline(points):
    return Bez(points, closed=False)
