#!/usr/bin/env python3
"""Check every emoji against Telegram's TGS rules and render-based sanity checks.

    python validate.py [--only 1-10]

Checks: 512x512, 60 fps, <= 180 frames, <= 64 KB gzipped, no forbidden Lottie
features (python-lottie TgsValidator + own scan), nothing drawn outside the canvas
in any frame, and a seamless loop (last frame flows into the first).
"""
import argparse
import os
import sys
import tempfile

import numpy as np
from lottie.exporters.tgs_validator import TgsValidator, Severity

from build import parse_only
from kit.registry import load_all, build_json, tgs_bytes
from kit.render import Renderer

FORBIDDEN_SHAPES = {'sr': 'star shape', 'gs': 'gradient stroke', 'rp': 'repeater', 'mm': 'merge paths'}


def scan(doc):
    errs = []

    def walk(o, path):
        if isinstance(o, dict):
            ty = o.get('ty')
            if isinstance(ty, str) and ty in FORBIDDEN_SHAPES:
                errs.append('%s at %s' % (FORBIDDEN_SHAPES[ty], path))
            if 'x' in o and isinstance(o['x'], str):
                errs.append('expression at %s' % path)
            if o.get('ty') == 'tr' or 'sk' in o:
                sk = o.get('sk')
                if sk and (sk.get('a') == 1 or sk.get('k', 0) != 0):
                    errs.append('skew at %s' % path)
            for k, v in o.items():
                walk(v, path + '.' + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, path + '[%d]' % i)

    for L in doc['layers']:
        if L.get('ty') != 4:
            errs.append('layer type %s' % L.get('ty'))
        for key in ('ef', 'masksProperties', 'tt', 'tm'):
            if key in L:
                errs.append('layer has %s' % key)
        if L.get('ddd') or L.get('ao') or L.get('sr', 1) != 1:
            errs.append('3D / auto-orient / time-stretch layer')
    walk(doc['layers'], 'layers')
    return errs


def check(e, step=2):
    problems = []
    doc = build_json(e)
    data = tgs_bytes(doc)
    if len(data) > 64 * 1024:
        problems.append('size %.1f KB > 64 KB' % (len(data) / 1024))
    if doc['w'] != 512 or doc['h'] != 512 or doc['fr'] != 60 or doc['op'] - doc['ip'] > 180:
        problems.append('bad canvas/fps/duration')
    problems += scan(doc)

    with tempfile.NamedTemporaryFile(suffix='.tgs', delete=False) as f:
        f.write(data)
        tmp = f.name
    try:
        v = TgsValidator(Severity.Note)
        v.check_file(tmp)
        problems += ['lottie-validator: %s' % err for err in v.errors]
    finally:
        os.unlink(tmp)

    # out-of-canvas check: render on a 768 canvas (content shifted by 128) at half scale
    big = build_json(e, offset=128)
    alpha_out = 0
    union = None
    with Renderer(big) as r:
        for fr in range(0, e.frames, step):
            a = np.asarray(r.frame(fr, 384))[:, :, 3]
            inner = a[64:320, 64:320]
            outside = a.copy()
            outside[64:320, 64:320] = 0
            alpha_out = max(alpha_out, int(outside.max()))
            ys, xs = np.nonzero(inner > 24)
            if len(xs):
                b = (xs.min(), ys.min(), xs.max(), ys.max())
                union = b if union is None else (min(union[0], b[0]), min(union[1], b[1]),
                                                 max(union[2], b[2]), max(union[3], b[3]))
    if alpha_out > 12:
        problems.append('drawn outside the canvas (alpha %d)' % alpha_out)
    if union is None:
        problems.append('empty render')
        cover = 0
    else:
        cover = max(union[2] - union[0], union[3] - union[1]) / 256 * 100
        if cover < 70:
            problems.append('artwork small: %.0f%% of canvas' % cover)

    # loop seam: frame T (one past the end) must match frame 0
    seam_doc = build_json(e, extra_frames=1)
    with Renderer(seam_doc) as r:
        f0 = np.asarray(r.frame(0, 256)).astype(np.int16)
        fT = np.asarray(r.frame(e.frames, 256)).astype(np.int16)
    seam = float(np.abs(f0 - fT).mean())
    if seam > 0.6:
        problems.append('loop seam jump (mean diff %.2f)' % seam)
    return len(data), cover, seam, problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--only', default='')
    ap.add_argument('--step', type=int, default=2, help='frame step for the bounds check')
    args = ap.parse_args()
    reg = load_all()
    nums = parse_only(args.only, reg)
    bad = 0
    for n in nums:
        e = reg[n]
        try:
            size, cover, seam, problems = check(e, args.step)
        except Exception as ex:  # surface builder errors per emoji
            size, cover, seam, problems = 0, 0, 0, ['ERROR %s: %s' % (type(ex).__name__, ex)]
        status = 'OK ' if not problems else 'BAD'
        bad += bool(problems)
        print('%s %-30s %5.1f KB  cover %3.0f%%  seam %.2f  %s' % (status, e.slug, size / 1024, cover, seam,
                                                                  '; '.join(problems)))
    print('%d checked, %d with problems' % (len(nums), bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
