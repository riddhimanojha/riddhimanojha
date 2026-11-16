"""Raster helpers shared by the animated assets: palette, layers, GIF writer."""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import tokens as K


def lerp(a, b, u):
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))


def ramp(anchors, n):
    """n colours spread along a polyline of hex anchors (by RGB distance)."""
    pts = [K.rgb(a) for a in anchors]
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(segs)
    out = []
    for j in range(n):
        d = total * j / (n - 1)
        for i, s in enumerate(segs):
            if d <= s or i == len(segs) - 1:
                out.append(lerp(pts[i], pts[i + 1], min(d / s, 1) if s else 0))
                break
            d -= s
    return [tuple(int(round(c)) for c in col) for col in out]


def design_palette():
    """255 colours built from the design tokens (index 255 is left free for
    GIF transparency). Every frame maps onto the same palette, so colours never
    shimmer between frames and the glow ramps stay smooth."""
    cols = []
    # near-blacks get their own dense ramp: large dark gradients band otherwise
    cols += ramp(["#040505", K.VOID, "#0D0F11", "#15171A", "#1B1D21"], 30)
    cols += ramp([K.VOID, "#0C0D0F", K.LINE_SOFT, K.LINE, K.INK_4, K.INK_3, K.INK_2, K.INK, "#FFFFFF"], 100)
    cols += ramp([K.VOID, "#1A2208", K.ACID_DIM, K.ACID, "#F2FFD0"], 62)
    cols += ramp([K.VOID, "#2A1D08", K.AMBER], 18)
    cols += ramp([K.LINE, K.ACID], 14)
    cols += ramp([K.INK_3, K.ACID], 10)
    cols += ramp([K.INK, K.ACID], 8)
    cols += [K.rgb(c) for c in (K.BASE, K.PANEL, K.RAISE, "#111316", "#0E1012", "#13161A", "#1D2025", "#2C3036")]
    seen, uniq = set(), []
    for c in cols:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    uniq = uniq[:255]
    while len(uniq) < 255:
        uniq.append(uniq[-1])
    pal = Image.new("P", (1, 1))
    flat = [v for c in uniq for v in c] + [0, 0, 0]
    pal.putpalette(flat)
    return pal


def to_p(img_rgb: Image.Image, pal: Image.Image) -> Image.Image:
    return img_rgb.quantize(palette=pal, dither=Image.Dither.NONE)


def corner_mask(size, r):
    """'1' image: set outside a rounded rectangle of radius r."""
    w, h = size
    m = Image.new("1", size, 1)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=0)
    return m


def save_gif(path, frames_rgb, fps, pal=None, radius=0):
    """Frames share one palette. With radius, corners are transparent (index
    255) so the GIF sits on the page with the same rounded corners as the
    SVG panels, in light and dark themes alike."""
    pal = pal or design_palette()
    frames = [to_p(f, pal) for f in frames_rgb]
    if radius:
        m = corner_mask(frames[0].size, radius)
        for f in frames:
            f.paste(255, mask=m)
            f.info["transparency"] = 255
    extra = {"transparency": 255} if radius else {}
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=round(1000 / fps),
                   loop=0, optimize=True, disposal=1, **extra)


def save_png_rounded(img: Image.Image, path, radius):
    out = img.convert("RGBA")
    out.paste((0, 0, 0, 0), mask=corner_mask(out.size, radius))
    out.save(path, optimize=True)


def add_glow(base: np.ndarray, emissive: Image.Image, radius: float, strength: float) -> np.ndarray:
    """Additive bloom: blur an RGB emissive layer and add it to base (float32)."""
    blurred = np.asarray(emissive.filter(ImageFilter.GaussianBlur(radius)), dtype=np.float32)
    return base + blurred * strength


def ease_in_out(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 3


def rgba(hex_, a=1.0):
    r, g, b = K.rgb(hex_)
    return (r, g, b, int(round(255 * max(0.0, min(1.0, a)))))


def layer(size):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)
