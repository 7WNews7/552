"""Emoji registry: every emoji module registers its builders with @emoji(...)."""
import gzip
import io
import json
from dataclasses import dataclass
from typing import Callable

from .lottie import animation

REGISTRY = {}


@dataclass
class Emoji:
    num: int
    name: str
    uni: str          # Unicode emoji to attach in @Stickers
    title: str        # Russian description
    frames: int       # loop length at 60 fps (<= 180)
    still: int        # frame used for the static PNG
    fn: Callable

    @property
    def slug(self):
        return '%03d_%s' % (self.num, self.name)


def emoji(num, name, uni, title, frames=120, still=0):
    """Decorator. The function receives T (= frames) and returns a list of
    groups/parts in painter order (first = back)."""
    assert 1 <= num <= 999 and frames <= 180

    def deco(fn):
        if num in REGISTRY:
            raise ValueError('emoji number %d registered twice (%s, %s)' % (num, REGISTRY[num].name, name))
        REGISTRY[num] = Emoji(num, name, uni, title, frames, still, fn)
        return fn
    return deco


def build_json(e, offset=0, extra_frames=0):
    items = e.fn(e.frames)
    return animation(items, name='KRONOS STAFF %s' % e.slug, op=e.frames,
                     offset=offset, extra_frames=extra_frames)


def dumps(doc):
    return json.dumps(doc, separators=(',', ':'), ensure_ascii=False)


def tgs_bytes(doc):
    buf = io.BytesIO()
    with gzip.GzipFile(filename='', mode='wb', fileobj=buf, compresslevel=9, mtime=0) as g:
        g.write(dumps(doc).encode('utf-8'))
    return buf.getvalue()


def load_all():
    import emojis  # noqa: F401  (registers everything)
    return REGISTRY
