#!/usr/bin/env python3
"""Build Telegram files for every registered emoji.

    python build.py                 # all emoji -> dist/
    python build.py --only 1-10,33  # a subset

Outputs per emoji:
    dist/tgs/NNN_name.tgs      animated custom emoji (Lottie, 512x512, 60 fps)
    dist/png/NNN_name.png      static custom emoji, 100x100 (Telegram requirement)
    dist/png512/NNN_name.png   same frame at 512x512 (for stickers / previews)
"""
import argparse
import csv
import os
import sys

from PIL import Image

from kit.registry import load_all, build_json, tgs_bytes
from kit.render import Renderer


def parse_only(spec, available):
    if not spec:
        return sorted(available)
    out = set()
    for chunk in spec.split(','):
        chunk = chunk.strip()
        if not chunk:
            continue
        if '-' in chunk:
            a, b = chunk.split('-')
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(chunk))
    return sorted(n for n in out if n in available)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--only', default='', help='numbers, e.g. 1-10,15')
    ap.add_argument('--out', default='dist')
    ap.add_argument('--no-png', action='store_true')
    args = ap.parse_args()

    reg = load_all()
    nums = parse_only(args.only, reg)
    for sub in ('tgs', 'png', 'png512'):
        os.makedirs(os.path.join(args.out, sub), exist_ok=True)

    worst = 0
    for n in nums:
        e = reg[n]
        doc = build_json(e)
        data = tgs_bytes(doc)
        worst = max(worst, len(data))
        with open(os.path.join(args.out, 'tgs', e.slug + '.tgs'), 'wb') as f:
            f.write(data)
        if not args.no_png:
            with Renderer(doc) as r:
                big = r.frame(e.still, 512)
            big.save(os.path.join(args.out, 'png512', e.slug + '.png'), optimize=True)
            big.resize((100, 100), Image.LANCZOS).save(os.path.join(args.out, 'png', e.slug + '.png'), optimize=True)
        print('%-30s %6.1f KB  %3d frames  %s' % (e.slug, len(data) / 1024, e.frames, e.uni))

    if not args.only:
        with open(os.path.join(args.out, 'emoji_list.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['num', 'file', 'emoji', 'title', 'seconds'])
            for n in nums:
                e = reg[n]
                w.writerow([n, e.slug, e.uni, e.title, round(e.frames / 60, 2)])
    print('built %d emoji, largest %.1f KB' % (len(nums), worst / 1024))
    return 0


if __name__ == '__main__':
    sys.exit(main())
