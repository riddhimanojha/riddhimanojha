"""Animated profile header.

    python scripts/header.py            -> assets/header.gif, assets/header-static.png
    python scripts/header.py --preview  -> a few PNG frames in scripts/.preview/

Everything that moves is periodic in the loop length, so the last frame flows
into the first: orbits complete whole revolutions, the boot log scrolls through
exactly one cycle, the prompt retypes its first command, the cursor blinks a
whole number of times and the signal meter uses integer frequencies.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from ro import raster as R
from ro import tokens as K
from ro import typeset as T

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"

W, H = 1200, 460
S = 2                 # supersampling for every frame
FPS = 25
DUR = 8.0
N = int(FPS * DUR)

# ------------------------------------------------------------------ orrery --
CX, CY = 946, 236
INCL = math.radians(70)    # tilt of the orbital plane towards the viewer
OMEGA = math.radians(-8)     # roll of the plane on screen
ORBITS = [
    dict(R=72, k=3, ph=0.5, col=K.ACID, r=4.4, label="YUKTI", hot=True),
    dict(R=108, k=2, ph=2.3, col=K.INK, r=3.0, label="ORION"),
    dict(R=142, k=2, ph=4.9, col=K.INK, r=3.0, label="SKILLVERSE"),
    dict(R=174, k=1, ph=0.9, col=K.INK, r=3.0, label="DILLI TRANSIT"),
    dict(R=204, k=1, ph=3.7, col=K.INK, r=2.6, label="SIMDU"),
    dict(R=204, k=1, ph=3.7 + math.pi, col=K.INK, r=2.6, label="MIXTAPE"),
]

# --------------------------------------------------------------- boot log --
LOG = [
    ("0.0412", "r/o kernel 26.11 · manchester node", ""),
    ("0.1187", "mount /dev/ideas", "ok"),
    ("0.2290", "load yukti.ko · assessment engine", "ok"),
    ("0.3315", "link constellations: orion, skillverse", "ok"),
    ("0.4471", "route dilli-transit --fewest-transfers", "ok"),
    ("0.5530", "simdu: cdu self-test", "pass"),
    ("0.6623", "mixtape: cat detected, nodding", "ok"),
    ("0.7709", "all systems nominal · building", ""),
]
LOG_STEP = DUR / len(LOG)
LOG_X, LOG_TOP, LOG_LH = 46, 80, 18
LOG_STATUS_X = 404

# ----------------------------------------------------------------- prompt --
P1 = "ship --from concept --to working-system"
P2 = "cd ~/yukti   # currently building"
PROMPT_Y = 398

NAME_X, NAME_Y1, NAME_Y2, NAME_SIZE = 40, 238, 342, 120
GLITCH = [(5.20, 5.32), (5.44, 5.52)]


def proj(rad, th):
    x, y = rad * math.cos(th), rad * math.sin(th)
    yy, z = y * math.cos(INCL), y * math.sin(INCL)
    X = x * math.cos(OMEGA) - yy * math.sin(OMEGA)
    Y = x * math.sin(OMEGA) + yy * math.cos(OMEGA)
    return CX + X, CY + Y, z / rad


def mono(d, xy, text, fill, size=11, weight=400, tracking=0.0, anchor="start", sc=S):
    return T.draw_text(d, (xy[0] * sc, xy[1] * sc), text, fill, "mono", weight, size * sc, tracking, anchor) / sc


# ------------------------------------------------------------- static art --

def build_static():
    SS = 4  # static art is drawn at 4x and reduced, so hairlines are smooth
    w, h = W * SS, H * SS
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)

    # background: void with a faint pool of light under the orrery
    bg = np.empty((h, w, 3), np.float32)
    bg[:] = K.rgb(K.VOID)
    d = np.sqrt(((xx / SS - CX) / 1.25) ** 2 + (yy / SS - CY) ** 2)
    pool = np.clip(1 - d / 330, 0, 1) ** 2
    bg += pool[..., None] * (np.array(K.rgb("#121417"), np.float32) - K.rgb(K.VOID))
    # CRT scanlines: one darker row in three
    rows = ((np.arange(h) // SS) % 3 == 0)
    bg[rows] *= 0.86
    base = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
    dr = ImageDraw.Draw(base, "RGBA")

    def L(x0, y0, x1, y1, col, a=1.0, wd=1.0):
        dr.line([(x0 * SS, y0 * SS), (x1 * SS, y1 * SS)], fill=R.rgba(col, a), width=max(1, round(wd * SS)))

    # grid
    for gx in range(4, W, 40):
        L(gx, 0, gx, H, "#15171A", 0.9)
    for gy in range(16, H, 40):
        L(0, gy, W, gy, "#15171A", 0.9)
    for gx in range(164, W, 160):
        for gy in range(56, H - 40, 160):
            L(gx - 4, gy, gx + 4, gy, K.INK_4, 0.7)
            L(gx, gy - 4, gx, gy + 4, K.INK_4, 0.7)

    # frame furniture: rules, crop marks, ruler
    for y in (50, 414):
        L(44, y, 1156, y, K.LINE)
        L(44, y - 3, 44, y + 3, K.INK_4)
        L(1156, y - 3, 1156, y + 3, K.INK_4)
    for (x, y, sx, sy) in ((14, 14, 1, 1), (W - 14, 14, -1, 1), (14, H - 14, 1, -1), (W - 14, H - 14, -1, -1)):
        L(x, y, x + 12 * sx, y, K.INK_4)
        L(x, y, x, y + 12 * sy, K.INK_4)
    for y in range(70, 400, 10):
        long = (y - 70) % 50 == 0
        L(22, y, 22 + (7 if long else 3), y, K.INK_4, 0.8 if long else 0.5)

    # top bar
    dr.ellipse([(51 - 5.5) * SS, (31 - 5.5) * SS, (51 + 5.5) * SS, (31 + 5.5) * SS], outline=R.rgba(K.INK_3), width=SS)
    a = math.radians(-40)
    sx, sy = 51 + 5.5 * math.cos(a), 31 + 5.5 * math.sin(a)
    dr.ellipse([(sx - 2) * SS, (sy - 2) * SS, (sx + 2) * SS, (sy + 2) * SS], fill=R.rgba(K.ACID))
    x = 66 + mono(dr, (66, 35), "R/O", K.rgb(K.INK), 11, 500, 0.16, sc=SS)
    mono(dr, (x + 12, 35), "SYSTEM 26.11", K.rgb(K.INK_3), 11, 400, 0.16, sc=SS)
    mono(dr, (600, 35), "PERSONAL OPERATING SYSTEM", K.rgb(K.INK_3), 11, 400, 0.16, "middle", sc=SS)
    mono(dr, (1156, 35), "53.4808° N   2.2426° W", K.rgb(K.INK_3), 11, 400, 0.16, "end", sc=SS)
    # bottom bar
    mono(dr, (44, 440), "COMPUTER SCIENCE  /  UNIVERSITY OF MANCHESTER", K.rgb(K.INK_3), 11, 400, 0.16, sc=SS)
    mono(dr, (1092, 440), "SIGNAL", K.rgb(K.INK_4), 11, 400, 0.16, "end", sc=SS)

    # orrery: instrument dial
    for deg in range(0, 360, 6):
        t = math.radians(deg)
        major = deg % 30 == 0
        r0, r1 = 168, 168 + (8 if major else 3)
        L(CX + r0 * math.cos(t), CY + r0 * math.sin(t), CX + r1 * math.cos(t), CY + r1 * math.sin(t),
          K.INK_3 if major else K.INK_4, 0.55 if major else 0.45)
    for deg, lab in ((270, "000"), (0, "090"), (90, "180"), (180, "270")):
        t = math.radians(deg)
        r = 186
        mono(dr, (CX + r * math.cos(t), CY + r * math.sin(t) + 3), lab, R.rgba(K.INK_4), 8, 400, 0.1, "middle", sc=SS)
    # vertical axis through the core
    for y0 in range(CY - 150, CY + 150, 8):
        L(CX, y0, CX, y0 + 3, K.INK_4, 0.55)
    # the orbital plane as faint glass
    pts = [proj(ORBITS[-1]["R"] + 10, t * math.tau / 240)[:2] for t in range(240)]
    plane = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(plane).polygon([(x * SS, y * SS) for x, y in pts], fill=R.rgba("#16191D", 0.55))
    base.alpha_composite(plane)

    front = Image.new("RGBA", base.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(front, "RGBA")
    seen = set()
    for o in ORBITS:
        if o["R"] in seen:
            continue
        seen.add(o["R"])
        hot = o.get("hot")
        steps = 720
        for i in range(steps):
            t0, t1 = i * math.tau / steps, (i + 1) * math.tau / steps
            x0, y0, z0 = proj(o["R"], t0)
            x1, y1, _ = proj(o["R"], t1)
            if z0 >= 0:
                col, al, tgt = (K.ACID, 0.62, fd) if hot else (K.INK_3, 0.75, fd)
            else:
                col, al, tgt = (K.ACID, 0.26, dr) if hot else (K.INK_4, 0.7, dr)
            tgt.line([(x0 * SS, y0 * SS), (x1 * SS, y1 * SS)], fill=R.rgba(col, al), width=SS)

    # core (sits between the far and near halves of the rings)
    def circ(drw, r, **kw):
        drw.ellipse([(CX - r) * SS, (CY - r) * SS, (CX + r) * SS, (CY + r) * SS], **kw)
    circ(dr, 15, fill=R.rgba("#0D0F11"), outline=R.rgba(K.INK_4), width=SS)
    circ(dr, 8.5, outline=R.rgba(K.LINE), width=SS)
    circ(dr, 3.6, fill=R.rgba(K.ACID))
    mono(dr, (1156, 402), "FIG. 1  NOT TO SCALE", R.rgba(K.INK_4), 8.5, 400, 0.16, "end", sc=SS)

    base = base.reduce(SS // S)
    front = front.reduce(SS // S)
    return base, front


def build_name():
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    T.draw_text(d, (NAME_X * S, NAME_Y1 * S), "Riddhiman", K.rgb(K.INK), "sans", 600, NAME_SIZE * S, -0.035)
    w2 = T.draw_text(d, (NAME_X * S, NAME_Y2 * S), "Ojha", K.rgb(K.INK), "sans", 600, NAME_SIZE * S, -0.035) / S
    cap = NAME_SIZE * 0.70
    cursor = (NAME_X + w2 + 16, NAME_Y2 - cap, NAME_X + w2 + 16 + 46, NAME_Y2)
    return img, cursor


# ---------------------------------------------------------------- timing ---

def prompt_text(t):
    """(visible text, typing?) for the prompt at time t."""
    def typed(phrase, t0, t1, tt):
        n = len(phrase)
        u = (tt - t0) / (t1 - t0)
        # slight human unevenness, deterministic and still monotone
        u = u + 0.035 * math.sin(u * 23.0) * (1 - u) * u * 4
        return phrase[: max(0, min(n, int(round(u * n))))]
    if t < 2.4:
        return P1, False
    if t < 2.9:
        return P1[: int(len(P1) * (1 - (t - 2.4) / 0.5))], True
    if t < 4.1:
        return typed(P2, 2.9, 4.1, t), True
    if t < 6.4:
        return P2, False
    if t < 6.8:
        return P2[: int(len(P2) * (1 - (t - 6.4) / 0.4))], True
    return typed(P1, 6.8, 7.96, t), True


def in_glitch(t):
    return any(a <= t < b for a, b in GLITCH)


# ----------------------------------------------------------------- frames ---

def draw_prompt(d, t):
    x = 44
    x += mono(d, (x, PROMPT_Y), "~", K.rgb(K.INK_3), 15)
    x += mono(d, (x, PROMPT_Y), " $ ", K.rgb(K.INK_4), 15)
    text, typing = prompt_text(t)
    cx = x
    for tok in text.split(" "):
        col = K.INK_2
        if tok.startswith("--"):
            col = K.INK_3
        cx += mono(d, (cx, PROMPT_Y), tok, K.rgb(col), 15)
        cx += mono(d, (cx, PROMPT_Y), " ", K.rgb(col), 15)
    if "#" in text:  # repaint the comment quieter
        pre, post = text.split("#", 1)
        px = x + T.width(pre, "mono", 400, 15)
        d.rectangle([px * S, (PROMPT_Y - 14) * S, (px + T.width("#" + post, "mono", 400, 15) + 4) * S, (PROMPT_Y + 5) * S], fill=(0, 0, 0, 0))
        mono(d, (px, PROMPT_Y), "#" + post, K.rgb(K.INK_4), 15)
    end = x + T.width(text, "mono", 400, 15)
    if typing:
        d.rectangle([(end + 2) * S, (PROMPT_Y - 12) * S, (end + 10) * S, (PROMPT_Y + 2) * S], fill=R.rgba(K.INK_2))


def draw_log(d, t):
    c = int(t // LOG_STEP)
    u = (t - c * LOG_STEP) / LOG_STEP * LOG_STEP  # seconds into this step
    slide = 1 - R.ease_out(u / 0.22)
    for slot in range(-1, 4):
        idx = (c - 3 + slot) % len(LOG)
        y = LOG_TOP + slot * LOG_LH + slide * LOG_LH
        alpha = 1.0
        if slot == -1:
            alpha = slide  # the line leaving the top fades out as it goes
        elif slot == 0:
            alpha = 0.55 + 0.45 * (1 - slide)
        if slot == 3:
            y = LOG_TOP + 3 * LOG_LH  # the newest line types in place, below the slide
            if u < 0.2:
                continue
        if alpha <= 0.01:
            continue
        ts, msg, st = LOG[idx]
        shown, show_status = msg, True
        if slot == 3:
            k = max(0.0, min(1.0, (u - 0.22) / 0.36))
            shown = msg[: int(round(k * len(msg)))]
            show_status = u > 0.62
        dim = 0.75 if slot < 2 else 1.0
        x = LOG_X
        x += mono(d, (x, y), f"[{ts}]", R.rgba(K.INK_4, alpha), 11, 400, 0.04)
        x += 10
        x += mono(d, (x, y), shown, R.rgba(K.INK_3, alpha * dim), 11, 400, 0.04)
        if st and show_status:
            dots_from = x + 8
            for dx in np.arange(dots_from, LOG_STATUS_X - 8, 6):
                d.rectangle([dx * S, (y - 2) * S, (dx + 1) * S, (y - 1) * S], fill=R.rgba(K.INK_4, alpha * 0.9))
            mono(d, (LOG_STATUS_X, y), st.upper(), R.rgba(K.ACID, alpha * (0.85 if slot < 3 else 1)), 11, 500, 0.12)


def draw_orrery(back, front, emis, t):
    labels = []
    for o in ORBITS:
        th = o["ph"] + math.tau * o["k"] * t / DUR
        hot = o.get("hot")
        arc = 0.45 + 0.22 * o["k"]
        steps = 34
        for j in range(steps):
            a0 = th - arc * j / steps
            a1 = th - arc * (j + 1) / steps
            x0, y0, z0 = proj(o["R"], a0)
            x1, y1, _ = proj(o["R"], a1)
            fade = (1 - j / steps) ** 2
            al = fade * (0.85 if hot else 0.55) * (1 if z0 >= 0 else 0.45)
            tgt = front if z0 >= 0 else back
            tgt.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=R.rgba(o["col"], al), width=round(1.6 * S))
        x, y, z = proj(o["R"], th)
        near = z >= 0
        r = o["r"] * (1.0 if near else 0.8)
        tgt = front if near else back
        if not near:
            # a dark halo keeps far satellites legible against the ring
            tgt.ellipse([(x - r - 2) * S, (y - r - 2) * S, (x + r + 2) * S, (y + r + 2) * S], fill=R.rgba(K.VOID, 0.8))
        tgt.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S],
                    fill=R.rgba(o["col"], 1.0 if near else 0.55))
        if hot:
            emis.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=K.rgb(K.ACID))
        labels.append((x, y, near, o))
    for x, y, near, o in labels:
        col = K.ACID if o.get("hot") else (K.INK_2 if near else K.INK_3)
        al = 0.95 if near else 0.45
        tgt = front if near else back
        mono(tgt, (x + 9, y - 7), o["label"], R.rgba(col, al), 9, 500, 0.16)


def draw_meter(d, t):
    rnd = random.Random(7)
    for i in range(10):
        f, g = rnd.randint(3, 9), rnd.randint(1, 3)
        p1, p2 = rnd.random() * math.tau, rnd.random() * math.tau
        v = (0.5 + 0.5 * math.sin(math.tau * f * t / DUR + p1)) * (0.65 + 0.35 * math.sin(math.tau * g * t / DUR + p2))
        hgt = 2 + 9 * v
        x = 1103 + i * 5.4
        d.rectangle([x * S, (441 - hgt) * S, (x + 3) * S, 441 * S], fill=R.rgba(K.INK_3, 0.9))


def glitch_name(name, t):
    rnd = random.Random(int(t * 1000))
    out = Image.new("RGBA", name.size, (0, 0, 0, 0))
    ghost = Image.new("RGBA", name.size, (0, 0, 0, 0))
    acid = Image.new("RGBA", name.size, R.rgba(K.ACID))
    y = 140 * S
    out.alpha_composite(name.crop((0, 0, name.width, y)), (0, 0))
    while y < 380 * S:
        hgt = rnd.randint(4, 26) * S
        band = name.crop((0, y, name.width, y + hgt))
        dx = rnd.choice([0, 0, 0, rnd.randint(-26, 26) * S, rnd.randint(-10, 10) * S])
        out.alpha_composite(band, (dx, y))
        if dx:
            tint = Image.composite(acid.crop((0, 0, band.width, band.height)), band, band)
            tint.putalpha(band.getchannel("A").point(lambda v: v * 0.5))
            ghost.alpha_composite(tint, (dx + 7 * S, y))
        y += hgt
    out.alpha_composite(name.crop((0, 380 * S, name.width, name.height)), (0, 380 * S))
    ghost.alpha_composite(out)
    return ghost


def frame(t, static, name, cursor):
    base, front_rings = static
    img = base.copy()
    size = img.size
    back, bd = R.layer(size)
    front, fd = R.layer(size)
    emis = Image.new("RGB", size, (0, 0, 0))
    ed = ImageDraw.Draw(emis)
    draw_orrery(bd, fd, ed, t)
    img.alpha_composite(back)
    img.alpha_composite(front_rings)
    img.alpha_composite(front)

    ui, ud = R.layer(size)
    draw_log(ud, t)
    draw_prompt(ud, t)
    draw_meter(ud, t)
    img.alpha_composite(ui)

    glitching = in_glitch(t)
    img.alpha_composite(glitch_name(name, t) if glitching else name)

    blink_on = (t % 1.0) < 0.56
    if glitching:
        blink_on = int(t * 50) % 2 == 0
    if blink_on:
        x0, y0, x1, y1 = cursor
        cd = ImageDraw.Draw(img)
        cd.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=R.rgba(K.ACID))
        ed.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=tuple(int(c * 0.28) for c in K.rgb(K.ACID)))
    # core pulse
    pulse = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(math.tau * 2 * t / DUR))
    rr = 4.5
    ed.ellipse([(CX - rr) * S, (CY - rr) * S, (CX + rr) * S, (CY + rr) * S],
               fill=tuple(int(c * pulse) for c in K.rgb(K.ACID)))

    arr = np.asarray(img.convert("RGB"), dtype=np.float32)
    arr = R.add_glow(arr, emis, 11 * S, 0.55)

    # scan beam: one pass per loop, top to bottom
    if 0.6 <= t <= 2.7:
        u = R.ease_in_out((t - 0.6) / 2.1)
        by = (-40 + (H + 80) * u) * S
        ys = np.arange(size[1], dtype=np.float32)[:, None]
        above = by - ys
        trail = np.where(above >= 0, np.exp(-above / (26 * S)), 0) * 0.075
        line = np.exp(-((ys - by) / (0.9 * S)) ** 2) * 0.22
        arr += trail[..., None] * np.array(K.rgb(K.ACID), np.float32)
        arr += line[..., None] * np.array(K.rgb(K.INK), np.float32)

    if glitching:
        rnd = random.Random(int(t * 997))
        for _ in range(3):
            gy = rnd.randint(150, 370) * S
            arr[gy:gy + S, : 700 * S] = arr[gy:gy + S, : 700 * S] * 0.4 + np.array(K.rgb(K.INK_2)) * 0.6

    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def main():
    preview = "--preview" in sys.argv
    static = build_static()
    name, cursor = build_name()
    if preview:
        pdir = Path(__file__).parent / ".preview"
        pdir.mkdir(exist_ok=True)
        for t in (0.0, 1.5, 3.5, 5.24, 7.2):
            frame(t, static, name, cursor).save(pdir / f"header_{t:.2f}.png")
        print("preview written to", pdir)
        return
    OUT.mkdir(exist_ok=True)
    frames = []
    for i in range(N):
        f = frame(i / FPS, static, name, cursor)
        if i == 0:
            R.save_png_rounded(f, OUT / "header-static.png", 18 * S)
        frames.append(f.reduce(S))
        if i % 25 == 0:
            print(f"frame {i}/{N}", flush=True)
    R.save_gif(OUT / "header.gif", frames, FPS, radius=18)
    print("header.gif", (OUT / "header.gif").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
