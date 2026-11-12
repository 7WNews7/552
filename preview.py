#!/usr/bin/env python3
"""Preview renders.

    python preview.py --only 1-5                 # check sheet: frames + small sizes on light/dark
    python preview.py --sheet                    # contact sheet of all emoji on the KRONOS background
    python preview.py --video                    # animated grid of all emoji (mp4)
"""
import argparse
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont, ImageEnhance

from build import parse_only
from kit.registry import load_all, build_json
from kit.render import Renderer
from kit.text import FONT_PATH

DARK = (14, 22, 48, 255)
TG_LIGHT = (255, 255, 255, 255)
TG_DARK = (24, 34, 45, 255)
BG_IMAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'background.jpg')


def label_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()


def check_sheet(reg, nums, cols, out):
    cell, small_w = 200, 230
    W = cols * cell + small_w
    H = len(nums) * cell
    sheet = Image.new('RGBA', (W, H), DARK)
    d = ImageDraw.Draw(sheet)
    f = label_font(16)
    for row, n in enumerate(nums):
        e = reg[n]
        y = row * cell
        with Renderer(build_json(e)) as r:
            for c in range(cols):
                fr = int(round(c * e.frames / cols))
                sheet.alpha_composite(r.frame(fr, cell), (c * cell, y))
            still = r.frame(e.still, 512)
        x0 = cols * cell
        d.rectangle([x0, y, W, y + 100], fill=TG_LIGHT)
        d.rectangle([x0, y + 100, W, y + cell], fill=TG_DARK)
        for yy in (y, y + 100):
            sheet.alpha_composite(still.resize((100, 100), Image.LANCZOS), (x0 + 6, yy))
            sheet.alpha_composite(still.resize((48, 48), Image.LANCZOS), (x0 + 116, yy + 26))
            sheet.alpha_composite(still.resize((24, 24), Image.LANCZOS), (x0 + 178, yy + 38))
        d.text((6, y + 4), '%s  %s' % (e.slug, e.title), font=f, fill=(255, 255, 255, 200))
    sheet.convert('RGB').save(out)
    print('saved', out)


def _background(W, H):
    if os.path.exists(BG_IMAGE):
        bg = Image.open(BG_IMAGE).convert('RGBA')
        scale = max(W / bg.width, H / bg.height)
        bg = bg.resize((int(bg.width * scale) + 1, int(bg.height * scale) + 1), Image.LANCZOS)
        left, top = (bg.width - W) // 2, (bg.height - H) // 2
        bg = bg.crop((left, top, left + W, top + H))
        bg = ImageEnhance.Brightness(bg).enhance(0.55)
        return bg
    return Image.new('RGBA', (W, H), DARK)


def contact_sheet(reg, nums, out, cols=10, cell=150):
    rows = (len(nums) + cols - 1) // cols
    pad = 70
    W, H = cols * cell + 40, rows * (cell + 26) + pad + 20
    sheet = _background(W, H)
    d = ImageDraw.Draw(sheet)
    d.text((W // 2, 38), 'KRONOS STAFF  ·  %d emoji' % len(nums), font=label_font(30), fill=(235, 245, 255, 255), anchor='mm')
    f = label_font(13)
    for k, n in enumerate(nums):
        e = reg[n]
        x = 20 + (k % cols) * cell
        y = pad + (k // cols) * (cell + 26)
        with Renderer(build_json(e)) as r:
            im = r.frame(e.still, 512).resize((cell - 16, cell - 16), Image.LANCZOS)
        sheet.alpha_composite(im, (x + 8, y + 8))
        d.text((x + cell // 2, y + cell + 8), '%03d %s' % (n, e.name), font=f, fill=(225, 238, 255, 255), anchor='mm')
    sheet.convert('RGB').save(out, quality=92)
    print('saved', out)


def video(reg, nums, out, cols=10, cell=108, fps=30):
    rows = (len(nums) + cols - 1) // cols
    W, H = cols * cell, rows * cell
    W += W % 2
    H += H % 2
    bg = _background(W, H)
    total = 360  # lcm of 120 and 180 frames -> every emoji loops cleanly
    rends = [(reg[n], Renderer(build_json(reg[n]))) for n in nums]
    tmpdir = os.path.join(os.path.dirname(out) or '.', '_frames')
    os.makedirs(tmpdir, exist_ok=True)
    step = 60 // fps
    for i, t in enumerate(range(0, total, step)):
        frame = bg.copy()
        for k, (e, r) in enumerate(rends):
            im = r.frame(t % e.frames, cell)
            frame.alpha_composite(im, ((k % cols) * cell, (k // cols) * cell))
        frame.convert('RGB').save(os.path.join(tmpdir, '%04d.png' % i))
    for _, r in rends:
        r.close()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i',
                    os.path.join(tmpdir, '%04d.png'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-crf', '20', '-movflags', '+faststart', out], check=True)
    for fn in os.listdir(tmpdir):
        os.unlink(os.path.join(tmpdir, fn))
    os.rmdir(tmpdir)
    print('saved', out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--only', default='')
    ap.add_argument('--cols', type=int, default=6, help='frames per row in the check sheet')
    ap.add_argument('--sheet', action='store_true')
    ap.add_argument('--video', action='store_true')
    ap.add_argument('--out', default='')
    args = ap.parse_args()
    reg = load_all()
    nums = parse_only(args.only, reg)
    os.makedirs('dist/preview', exist_ok=True)
    if args.sheet:
        contact_sheet(reg, nums, args.out or 'dist/preview/all_emoji.jpg')
    elif args.video:
        video(reg, nums, args.out or 'dist/preview/all_emoji.mp4')
    else:
        name = args.only.replace(',', '_') or 'all'
        check_sheet(reg, nums, args.cols, args.out or '/tmp/preview_%s.png' % name)
    return 0


if __name__ == '__main__':
    sys.exit(main())
