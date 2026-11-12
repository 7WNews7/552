# KRONOS STAFF emoji — style guide for authors

Every emoji is a Python function that returns Lottie groups; `build.py` turns it into a
Telegram TGS (animated custom emoji) and a 100x100 PNG (static custom emoji).

## Telegram rules (enforced by `validate.py`)

* 512x512 canvas, 60 fps, loop length `frames` <= 180 (use 120 = 2 s or 180 = 3 s).
* Everything stays inside the canvas in every frame, incl. particles, glows and overshoot.
  Keep ~16 px margin; `validate.py` renders every 2nd frame on a larger canvas to check.
* Seamless loop: frame T must look like frame 0 (`validate.py` compares them).
  Use the helpers in `kit/fx.py`, `anim()` keys that start and end on the same value,
  `loop()` / `phase()` for staggered timing.
* Forbidden: masks, mattes, effects, expressions, text layers, images, star shapes
  (use `geometry.star()` which builds a path), repeaters, merge paths, gradient STROKES,
  skew. Gradient FILLS, trim paths and path morphing are fine.
* <= 64 KB gzipped (our files are 2-10 KB; avoid sampling hundreds of keyframes).

## Look

* Theme: night winter forest of the KRONOS STAFF avatar — deep navy, royal blue, icy
  light blue, snow white, white twinkles. Brand crown = icy silver with blue gems.
* Main silhouettes: icy gradient fill (light at the top, deep blue at the bottom) and a dark
  navy contour drawn BEHIND the fill: `part(shape, fill=S.vgrad(...), outline=S.OW)`.
  The contour keeps emoji readable on white chat backgrounds; never skip it on the main
  shape. Small inner details may use `outline=S.OW_THIN` or no contour.
* Light from the top-left: white gloss highlight (opacity 50-90) on the upper-left of round
  bodies, darker blue at the bottom right.
* Accents: `fx.sparkle(s)` twinkles, snow caps (`motifs.snowcap` or your own white blob
  with a light-blue underside), subtle `fx.glow` (alpha <= 0.45 — it shows as haze on
  light themes).
* Palette lives in `kit/style.py` (`S.BLUE`, `S.ICE`, `S.G_ICE`, ...). Stay cold. Warm colours
  only as tiny natural accents (cat eyes `#d8e86a`-ish, pink nose, rottweiler tan) or where
  meaning needs them (a red cross may be ice-pink `S.G_RED`, used sparingly).
* Big and bold: artwork should fill ~80-90 % of the canvas (validate warns below 70 %).
  Check the 48 px and 24 px renders in the preview sheet: the silhouette must still read.
  Prefer few large shapes over many tiny details. Text: max ~5 letters, Montserrat Black.

## Motion

* Smooth: always ease (`'io'`, `'sine'`, `'out'`, `'outback'` for pops with overshoot).
  Linear only for constant spins / falling particles.
* One clear main action + gentle idle (bob / breathe / swing) + secondary details
  (sparkles, shine sweep, particles). Avoid frantic full-body jitter.
* Typical recipes: `fx.bob`, `fx.breathe`, `fx.swing`, `fx.wobble` (damped shake),
  `fx.pulse` (one-off pop), `fx.blink` (eyes), `fx.rise` (floating hearts / Zz / steam),
  `fx.draw_on` + `trim()` (stroke drawing), `fx.shine` (light band sweeping over shapes),
  `fx.ring_pulse`, `fx.burst`, `fx.snowfall`, `geometry.morph` (shape morphing).
* The static PNG uses frame `still=`: pick a frame where the emoji looks complete.

## API cheat sheet

```python
from kit.registry import emoji
from kit.lottie import part, group, anim, loop, phase, stroke, fill, trim, color_anim, ellipse, rect
from kit.geometry import P, svg, Bez, rounded, star, circle_path, heart_path, sparkle_path, line, polyline, morph
from kit.text import glyphs, text, fit_cap
from kit.motifs import crown, paw, snowcap
from kit import fx, style as S

@emoji(43, 'bell', '🔔', 'Колокольчик', frames=120, still=0)
def e_bell(T):                 # T = frames
    body = P('M ... Z')         # SVG path syntax (M L H V C S Q T A Z), absolute or relative
    return [                    # painter order: first = back
        fx.glow(256, 260, 220),
        group(part(body, fill=S.vgrad(S.G_ICE, 80, 430), outline=S.OW),
              pivot=(256, 90), r=fx.swing(T, 12)),
    ]
```

* `part(*shapes, fill=, stroke=, outline=, trim=, pivot=, move=, s=, r=, o=)` — one style
  applied to several shapes (compound paths with holes work: nonzero fill).
  `stroke=` is drawn on top of the fill, `outline=` behind it.
* `group(*children, pivot=, move=, s=, r=, o=)` — children in painter order. `pivot` is the
  rotation/scale centre; `move` is an [dx, dy] offset (static or animated); `s` scalar or
  [sx, sy] (animated scalars are expanded automatically); `r` degrees; `o` 0..100.
* `anim((t, v), (t, v, 'ease'), ...)` — ease applies to the segment starting at that key;
  `'hold'` jumps. Keys must start at 0 and end at T for looping helpers like `phase()`.
* `loop(keys, T)` — keys may span any window of length T (e.g. 100..220 for T=120).
* Shapes in canvas coordinates (0..512, y down). `Bez.translate/scale/rotate/mirror_x`.
* Text: `glyphs('NEW', cx, cy, cap, weight=900)` -> [(paths, centre)] per letter;
  `fit_cap('ADMIN', max_width, cap)` picks a cap height that fits.

## Workflow

```
/tmp/venv/bin/python build.py    --only 43-48
/tmp/venv/bin/python validate.py --only 43-48
/tmp/venv/bin/python preview.py  --only 43-48 --out /tmp/prev_43.png   # then look at the PNG
```
The preview row shows 6 frames across the loop, plus 100/48/24 px renders on a white and
a Telegram-dark background.
