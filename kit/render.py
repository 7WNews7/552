"""Rendering through rlottie (the engine Telegram clients use)."""
import json

from PIL import Image
from rlottie_python import LottieAnimation


class Renderer:
    def __init__(self, doc):
        self.anim = LottieAnimation.from_data(json.dumps(doc))
        self.frames = self.anim.lottie_animation_get_totalframe()

    def frame(self, n, size):
        buf = self.anim.lottie_animation_render(frame_num=n, width=size, height=size)
        # rlottie returns premultiplied BGRA
        return Image.frombuffer('RGBA', (size, size), buf, 'raw', 'BGRa', 0, 1).copy()

    def close(self):
        self.anim.lottie_animation_destroy()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def render(doc, n, size):
    with Renderer(doc) as r:
        return r.frame(n, size)


def on_bg(img, color):
    bg = Image.new('RGBA', img.size, color)
    bg.alpha_composite(img)
    return bg
