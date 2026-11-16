"""Closing sequence: assets/eof.gif (+ assets/eof-static.png).

The session 'logs out': the signature mark keeps orbiting, the cursor blinks,
then the screen collapses like a CRT switching off and powers back on, which is
also where the loop joins.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from ro import raster as R
from ro import tokens as K
from ro import typeset as T

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
W, H = 1200, 280
S = 2
FPS = 25
DUR = 6.0
N = int(FPS * DUR)
MX, MY, MR = 128, 140, 46


def mono(d, x, y, s, fill, size=11, weight=400, tracking=0.16, anchor="start"):
    return T.draw_text(d, (x * S, y * S), s, fill, "mono", weight, size * S, tracking, anchor) / S


def sans(d, x, y, s, fill, size, weight=500, tracking=-0.02):
    return T.draw_text(d, (x * S, y * S), s, fill, "sans", weight, size * S, tracking) / S


def build_static():
    w, h = W * S, H * S
    bg = np.empty((h, w, 3), np.float32)
    bg[:] = K.rgb(K.VOID)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx / S - MX) ** 2 + (yy / S - MY) ** 2)
    bg += (np.clip(1 - d / 260, 0, 1) ** 2)[..., None] * (np.array(K.rgb("#121417"), np.float32) - K.rgb(K.VOID))
    bg[(np.arange(h) // S) % 3 == 0] *= 0.86
    img = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")
    dr = ImageDraw.Draw(img, "RGBA")

    def L(x0, y0, x1, y1, col, a=1.0):
        dr.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=R.rgba(col, a), width=S)

    for gx in range(4, W, 40):
        L(gx, 0, gx, H, "#15171A", 0.9)
    for gy in range(20, H, 40):
        L(0, gy, W, gy, "#15171A", 0.9)
    for y in (36, 244):
        L(44, y, 1156, y, K.LINE)
    for (x, y, sx, sy) in ((14, 14, 1, 1), (W - 14, 14, -1, 1), (14, H - 14, 1, -1), (W - 14, H - 14, -1, -1)):
        L(x, y, x + 12 * sx, y, K.INK_4)
        L(x, y, x, y + 12 * sy, K.INK_4)
    mono(dr, 44, 25, "§06  END OF FILE", K.rgb(K.INK_3))
    mono(dr, 1156, 25, "~/README.md  ·  0 ERRORS  ·  0 WARNINGS", K.rgb(K.INK_3), anchor="end")
    # the mark: ring, with the satellite drawn per frame
    dr.ellipse([(MX - MR) * S, (MY - MR) * S, (MX + MR) * S, (MY + MR) * S], outline=R.rgba(K.INK_3), width=round(1.4 * S))
    dr.ellipse([(MX - MR - 14) * S, (MY - MR - 14) * S, (MX + MR + 14) * S, (MY + MR + 14) * S], outline=R.rgba(K.INK_4, 0.5), width=S)
    # words
    x = 236
    mono(dr, x, 100, "riddhiman@r/o:~$ logout", K.rgb(K.INK_3), 12, 400, 0.04)
    sans(dr, x - 2, 156, "Session closed.", K.rgb(K.INK), 50, 600, -0.035)
    sans(dr, x, 194, "Thanks for reading all the way down.", K.rgb(K.INK_3), 21, 400, -0.005)
    rx = 1156
    for i, (s, col) in enumerate((("RIDDHIMAN OJHA", K.INK_2), ("MANCHESTER · 53.48° N", K.INK_3),
                                  ("R/O SYSTEM 26.11", K.INK_3))):
        mono(dr, rx, 120 + i * 22, s, K.rgb(col), 11, 500 if i == 0 else 400, 0.16, "end")
    mono(dr, 44, 266, "CONNECTION TO RIDDHIMAN CLOSED.", K.rgb(K.INK_4), 11)
    mono(dr, 1156, 266, "EOF", K.rgb(K.ACID), 11, 500, 0.2, "end")
    return img


def content(t, static):
    img = static.copy()
    d = ImageDraw.Draw(img, "RGBA")
    emis = Image.new("RGB", img.size, (0, 0, 0))
    ed = ImageDraw.Draw(emis)
    th = -math.pi / 2 + math.tau * t / DUR
    for j in range(40):
        a0 = th - 0.03 * j
        a1 = th - 0.03 * (j + 1)
        al = (1 - j / 40) ** 2 * 0.8
        d.line([((MX + MR * math.cos(a0)) * S, (MY + MR * math.sin(a0)) * S),
                ((MX + MR * math.cos(a1)) * S, (MY + MR * math.sin(a1)) * S)], fill=R.rgba(K.ACID, al), width=round(2 * S))
    sx, sy = MX + MR * math.cos(th), MY + MR * math.sin(th)
    for drw, col in ((d, R.rgba(K.ACID)), (ed, K.rgb(K.ACID))):
        drw.ellipse([(sx - 5.5) * S, (sy - 5.5) * S, (sx + 5.5) * S, (sy + 5.5) * S], fill=col)
    if (t % 1.0) < 0.56:
        box = [(MX - 9) * S, (MY - 16) * S, (MX + 9) * S, (MY + 16) * S]
        d.rectangle(box, fill=R.rgba(K.ACID))
        ed.rectangle(box, fill=tuple(int(c * 0.3) for c in K.rgb(K.ACID)))
    arr = R.add_glow(np.asarray(img.convert("RGB"), np.float32), emis, 10 * S, 0.6)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def crt(img, t):
    """Power-off between 4.5s and 5.5s, power-on until 6.0s."""
    w, h = img.size
    black = Image.new("RGB", (w, h), K.rgb(K.VOID))
    def squash(sy, sx=1.0, boost=1.0):
        hh = max(2, int(h * sy))
        ww = max(2, int(w * sx))
        part = img.resize((ww, hh), Image.Resampling.BILINEAR)
        if boost != 1.0:
            part = Image.fromarray(np.clip(np.asarray(part, np.float32) * boost + 40 * (boost - 1), 0, 255).astype(np.uint8))
        black.paste(part, ((w - ww) // 2, (h - hh) // 2))
        return black
    if t < 4.5:
        return img
    if t < 4.85:  # collapse vertically, brightening
        u = R.ease_in_out((t - 4.5) / 0.35)
        return squash(1 - 0.994 * u, 1.0, 1 + 1.4 * u)
    if t < 5.15:  # line shrinks to a point
        u = R.ease_in_out((t - 4.85) / 0.3)
        return squash(0.006, 1 - 0.995 * u, 2.4)
    if t < 5.5:  # the point fades
        u = (t - 5.15) / 0.35
        dot = Image.new("RGB", (w, h), K.rgb(K.VOID))
        dd = ImageDraw.Draw(dot)
        r = 3 * S * (1 - u)
        v = 1 - u
        col = tuple(int(K.rgb(K.VOID)[i] + (K.rgb(K.INK)[i] - K.rgb(K.VOID)[i]) * v) for i in range(3))
        dd.ellipse([w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r], fill=col)
        return dot
    if t < 5.6:
        return black
    u = R.ease_out((t - 5.6) / 0.4)  # power back on
    return squash(0.006 + 0.994 * u, 1.0, 1 + 0.8 * (1 - u))


def main():
    static = build_static()
    frames = []
    for i in range(N):
        t = i / FPS
        f = crt(content(t, static), t)
        if i == 0:
            R.save_png_rounded(f, OUT / "eof-static.png", 18 * S)
        frames.append(f.reduce(S))
    R.save_gif(OUT / "eof.gif", frames, FPS, radius=18)
    print("eof.gif", (OUT / "eof.gif").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
