"""Experiment cards and the stack matrix.

Each card pairs one generative illustration with verified facts taken from the
project's own README and manifests. Cards alternate sides for an editorial
rhythm; every illustration uses the same grid, hairlines and single accent.
"""
from __future__ import annotations

import math
import random

from ro import svg as V
from ro import tokens as K
from ro import typeset as T

W = K.W
H = 400
ART_W = 540


# ------------------------------------------------------------ illustrations --
# Each draws into a local box (0,0)-(ART_W, H-48) and returns SVG.

def art_frame(pid):
    w, h = ART_W, H - 48
    return (V.defs(V.grid_pattern(pid, 24, "#15171B", 0, 0), V.clip_rect(pid + "c", 0, 0, w, h, 14))
            + V.rect(0, 0, w, h, fill=K.VOID, r=14)
            + V.group(V.rect(0, 0, w, h, fill=f"url(#{pid})"), clip=pid + "c")
            + V.rect(0.5, 0.5, w - 1, h - 1, stroke=K.LINE, r=14))


def art_skillverse():
    w, h = ART_W, H - 48
    rnd = random.Random(11)
    out = [art_frame("sv")]
    out.append(V.defs(V.glow_filter("svg", 5)))
    for _ in range(140):
        x, y = rnd.uniform(12, w - 12), rnd.uniform(12, h - 12)
        out.append(V.circle(x, y, rnd.choice([0.6, 0.8, 1.0, 1.3]), fill=K.INK_3, opacity=round(rnd.uniform(0.25, 0.7), 2)))
    # a ringed planet, low in the frame
    px, py = 430, 262
    out.append(V.defs(V.clip_rect("svlow", px - 80, py, 160, 40)))
    out.append(V.ellipse(px, py, 58, 13, K.INK_3, 1, -16, 0.8))
    out.append(V.circle(px, py, 30, fill="#121418", stroke=K.INK_4))
    out.append(V.group(V.ellipse(px, py, 58, 13, K.INK_2, 1.2, -16, 0.9), clip="svlow"))
    nodes = {
        "HTML": (72, 250), "CSS": (128, 300), "JAVASCRIPT": (176, 214), "REACT": (262, 168),
        "TYPESCRIPT": (300, 252), "STATE": (364, 118), "TESTING": (196, 92), "APIS": (430, 72),
    }
    edges = [("HTML", "CSS"), ("HTML", "JAVASCRIPT"), ("CSS", "JAVASCRIPT"), ("JAVASCRIPT", "REACT"),
             ("JAVASCRIPT", "TESTING"), ("REACT", "TYPESCRIPT"), ("REACT", "STATE"), ("STATE", "APIS"),
             ("TESTING", "REACT")]
    path = ["HTML", "JAVASCRIPT", "REACT", "STATE", "APIS"]
    on = set(zip(path, path[1:])) | set(zip(path[1:], path))
    for a, b in edges:
        (x1, y1), (x2, y2) = nodes[a], nodes[b]
        lit = (a, b) in on
        out.append(V.line(x1, y1, x2, y2, K.ACID if lit else K.INK_4, 1.2 if lit else 1, 0.9 if lit else 0.9,
                          None if lit else "2 4"))
    done = {"HTML", "JAVASCRIPT", "REACT"}
    for name, (x, y) in nodes.items():
        lit = name in path
        if name in done:
            out.append(V.group(V.circle(x, y, 7, fill=K.ACID), opacity=0.55, filter_="svg"))
            out.append(V.circle(x, y, 4, fill=K.ACID))
        elif lit:
            out.append(V.circle(x, y, 4.5, stroke=K.ACID, sw_=1.4, fill=K.VOID))
        else:
            out.append(V.circle(x, y, 3.2, fill=K.INK_3))
        out.append(V.mono(name, x + 10, y - 9, K.INK_2 if lit else K.INK_3, 9, 500, 0.16))
    out.append(V.mono("LEARNING PATH · 3 OF 5 STARS LIT", 22, h - 22, K.INK_3, 9.5, 400, 0.16))
    return "".join(out)


def art_orion():
    w, h = ART_W, H - 48
    rnd = random.Random(3)
    out = [art_frame("or"), V.defs(V.glow_filter("org", 6))]
    for _ in range(90):
        out.append(V.circle(rnd.uniform(10, w - 10), rnd.uniform(10, h - 10), rnd.choice([0.6, 0.9]),
                            fill=K.INK_3, opacity=round(rnd.uniform(0.2, 0.5), 2)))
    # Orion, roughly as it sits in the sky; each star stands for a finding
    ox, oy, sx, sy = 70, 30, 300, 300
    stars = {
        "betelgeuse": (0.20, 0.16, "critical"), "bellatrix": (0.72, 0.22, "medium"),
        "meissa": (0.47, 0.04, "low"), "alnitak": (0.38, 0.55, "high"), "alnilam": (0.48, 0.515, "medium"),
        "mintaka": (0.58, 0.48, "low"), "saiph": (0.30, 0.93, "low"), "rigel": (0.80, 0.88, "high"),
    }
    P = {k: (ox + x * sx, oy + y * sy, s) for k, (x, y, s) in stars.items()}
    edges = [("betelgeuse", "meissa"), ("meissa", "bellatrix"), ("betelgeuse", "alnitak"), ("bellatrix", "mintaka"),
             ("alnitak", "alnilam"), ("alnilam", "mintaka"), ("alnitak", "saiph"), ("mintaka", "rigel"),
             ("betelgeuse", "bellatrix")]
    for a, b in edges:
        hot = "betelgeuse" in (a, b)
        out.append(V.line(P[a][0], P[a][1], P[b][0], P[b][1], K.AMBER if hot else K.INK_4, 1, 0.55 if hot else 0.9))
    size = {"critical": 6, "high": 4.6, "medium": 3.6, "low": 2.6}
    for k, (x, y, s) in P.items():
        if s == "critical":
            for r, op in ((26, 0.18), (17, 0.32)):
                out.append(V.circle(x, y, r, stroke=K.AMBER, sw_=1, stroke_opacity=op))
            out.append(V.group(V.circle(x, y, 10, fill=K.AMBER), opacity=0.6, filter_="org"))
            out.append(V.circle(x, y, size[s], fill=K.AMBER))
        else:
            col = K.INK if s == "high" else K.INK_2 if s == "medium" else K.INK_3
            out.append(V.circle(x, y, size[s], fill=col))
    # inspector card for the critical star
    bx, by, bw, bh = 300, 40, 216, 160
    out.append(V.rect(bx, by, bw, bh, fill="#0E1013", stroke=K.LINE, r=10))
    bxs, bys = P["betelgeuse"][0], P["betelgeuse"][1]
    out.append(V.line(bxs + 26, bys, bx, bys, K.AMBER, 1, 0.5, "2 3"))
    out.append(V.circle(bx + 18, by + 22, 3.5, fill=K.AMBER))
    out.append(V.mono("CRITICAL", bx + 30, by + 26, K.AMBER, 10, 500, 0.16))
    out.append(V.mono("SQL INJECTION", bx + 18, by + 50, K.INK, 11.5, 500, 0.08))
    trace = [("SOURCE", "req.query.id"), ("PASSES", "buildFilter()"), ("SINK", "db.query()")]
    ty = by + 80
    for i, (k, v) in enumerate(trace):
        out.append(V.circle(bx + 22, ty - 4, 2.6, fill=K.INK_3 if i < 2 else K.AMBER))
        if i < 2:
            out.append(V.line(bx + 22, ty, bx + 22, ty + 18, K.INK_4))
        out.append(V.mono(k, bx + 34, ty, K.INK_4, 9, 400, 0.16))
        out.append(V.mono(v, bx + 96, ty, K.INK_2, 10.5, 400, 0.02))
        ty += 22
    out.append(V.mono("FIX · PARAMETERISE THE QUERY", bx + 18, by + bh - 14, K.ACID, 9, 500, 0.12))
    out.append(V.mono("ILLUSTRATIVE FINDINGS", 22, h - 22, K.INK_3, 9.5, 400, 0.16))
    legend = [("CRITICAL", K.AMBER, 4), ("HIGH", K.INK, 3.4), ("MEDIUM", K.INK_2, 2.8), ("LOW", K.INK_3, 2.2)]
    lx = w - 22
    for name, col, r in reversed(legend):
        lw = V.mw(name, 9, 400, 0.16)
        out.append(V.mono(name, lx, h - 22, K.INK_3, 9, 400, 0.16, "end"))
        out.append(V.circle(lx - lw - 9, h - 25, r, fill=col))
        lx -= lw + 28
    return "".join(out)


def art_dilli():
    w, h = ART_W, H - 48
    out = [art_frame("dt")]
    # schematic, 45/90 degree lines. Grey for the network, acid for the route.
    yellow = [(150, 20), (150, 92), (178, 120), (178, 182), (178, 296)]
    blue = [(20, 200), (120, 200), (150, 182), (330, 182), (370, 222), (470, 222)]
    magenta = [(178, 296), (300, 296), (370, 226)]
    red = [(40, 100), (130, 100), (150, 92), (260, 92), (300, 52), (420, 52)]
    for ln, name, lab in ((red, "RED", (420, 44)), (magenta, "MAGENTA", (236, 286)), (blue, "BLUE", (28, 192)),
                          (yellow, "YELLOW", (108, 30))):
        out.append(V.poly(ln, K.INK_4, 6, 0.9))
        out.append(V.mono(name, lab[0], lab[1], K.INK_4, 8.5, 400, 0.18, "end" if name == "RED" else "start"))
    route = [(150, 92), (178, 120), (178, 182), (330, 182), (370, 222)]
    out.append(V.poly(route, K.ACID, 4))
    stations = [
        ("KASHMERE GATE", (150, 92), "interchange", (-12, -10), "end"),
        ("NEW DELHI", (178, 140), "stop", (14, 4), "start"),
        ("RAJIV CHOWK", (178, 182), "interchange", (14, 26), "start"),
        ("HAUZ KHAS", (178, 296), "interchange", (-12, 4), "end"),
        ("BOTANICAL GARDEN", (370, 222), "interchange", (16, 24), "start"),
    ]
    for name, (x, y), kind, (dx, dy), anc in stations:
        on_route = name in ("KASHMERE GATE", "NEW DELHI", "RAJIV CHOWK", "BOTANICAL GARDEN")
        if kind == "interchange":
            out.append(V.circle(x, y, 8, fill=K.VOID, stroke=K.ACID if on_route else K.INK_3, sw_=2))
        else:
            out.append(V.circle(x, y, 3.5, fill=K.VOID, stroke=K.ACID, sw_=1.6))
        out.append(V.mono(name, x + dx, y + dy, K.INK if on_route else K.INK_3, 9.5, 500, 0.12, anc))
    # live crowd report
    cx, cy = 300, 112
    out.append(V.rect(cx, cy, 214, 60, fill="#0E1013", stroke=K.LINE, r=10))
    out.append(V.circle(cx + 18, cy + 21, 3.5, fill=K.AMBER))
    out.append(V.mono("CROWD REPORT · LIVE", cx + 30, cy + 25, K.INK_2, 9.5, 500, 0.14))
    out.append(V.mono("RAJIV CHOWK  BUSY", cx + 18, cy + 46, K.INK_3, 9.5, 400, 0.14))
    out.append(V.poly([(cx, cy + 40), (196, 178)], K.INK_4, 1, dash="2 3"))
    # route toggle
    tx, ty = 22, h - 22
    out.append(V.mono("RANK BY", tx, ty, K.INK_4, 9.5, 400, 0.16))
    x = tx + V.mw("RANK BY", 9.5, 400, 0.16) + 14
    for i, opt in enumerate(("FASTEST", "FEWEST TRANSFERS")):
        ow = V.mw(opt, 9.5, 500, 0.14) + 20
        out.append(V.rect(x, ty - 14, ow, 20, r=10, fill=K.ACID if i == 0 else "none",
                          stroke=None if i == 0 else K.LINE, opacity=0.12 if i == 0 else None))
        out.append(V.mono(opt, x + ow / 2, ty, K.ACID if i == 0 else K.INK_3, 9.5, 500, 0.14, "middle"))
        x += ow + 8
    out.append(V.mono("SCHEMATIC", w - 22, ty, K.INK_4, 9.5, 400, 0.16, "end"))
    return "".join(out)


def art_simdu():
    w, h = ART_W, H - 48
    out = [art_frame("sd")]
    # a CDU, face-on: screen with line-select keys, then the key bed
    dx, dy, dw, dh = 130, 14, 280, 302
    out.append(V.rect(dx, dy, dw, dh, fill="#121418", stroke=K.INK_4, r=16))
    sx, sy, sw_, sh = dx + 40, dy + 20, dw - 80, 132
    out.append(V.rect(sx, sy, sw_, sh, fill="#050606", stroke=K.LINE, r=4))
    for i in range(6):
        ky = sy + 14 + i * 20
        out.append(V.rect(dx + 12, ky, 20, 10, fill="#1B1E22", stroke=K.LINE, r=2))
        out.append(V.rect(dx + dw - 32, ky, 20, 10, fill="#1B1E22", stroke=K.LINE, r=2))
    m = lambda s, x, y, c, sz=8.6, a="start": V.mono(s, x, y, c, sz, 500, 0.06, a)
    L, R_ = sx + 8, sx + sw_ - 8
    out.append(m("INIT", sx + sw_ / 2, sy + 16, K.INK, 9.4, "middle"))
    rows = [
        ("CO RTE", "FROM/TO", "", "EGCC/LFPG"),
        ("ALTN/CO RTE", "", "----/------", ""),
        ("FLT NBR", "", "RO2611", ""),
        ("COST INDEX", "TROPO", "35", "36090"),
        ("CRZ FL/TEMP", "", "FL350/-54°", ""),
    ]
    y = sy + 32
    for lab_l, lab_r, val_l, val_r in rows:
        out.append(m(lab_l, L, y, K.INK_3, 7.2))
        if lab_r:
            out.append(m(lab_r, R_, y, K.INK_3, 7.2, "end"))
        y += 10
        if val_l:
            out.append(m(val_l, L, y, K.ACID))
        if val_r:
            out.append(m(val_r, R_, y, K.ACID, 8.6, "end"))
        y += 10
    # function keys
    fk = ["DIR", "PROG", "PERF", "INIT", "DATA", "F-PLN", "RAD", "FUEL", "SEC", "MENU"]
    ky = sy + sh + 18
    for i, k in enumerate(fk):
        col, row = i % 5, i // 5
        kx = dx + 22 + col * 48
        yy = ky + row * 26
        lit = k == "INIT"
        out.append(V.rect(kx, yy, 42, 20, fill="#1B1E22", stroke=K.ACID if lit else K.LINE, r=3))
        out.append(V.mono(k, kx + 21, yy + 13.5, K.ACID if lit else K.INK_3, 7, 500, 0.06, "middle"))
    # letter grid
    gy = ky + 60
    for i, ch in enumerate("ABCDEFGHIJKLMNOPQR"):
        col, row = i % 6, i // 6
        kx = dx + 26 + col * 39
        yy = gy + row * 22
        out.append(V.rect(kx, yy, 32, 17, fill="#16191C", stroke=K.LINE, r=3))
        out.append(V.mono(ch, kx + 16, yy + 12, K.INK_3, 8, 500, 0, "middle"))
    out.append(V.mono("NO HARDWARE · PHONE OR TABLET", 22, h - 22, K.INK_3, 9.5, 400, 0.16))
    out.append(V.mono("MCDU SELF-TEST · PASS", w - 22, h - 22, K.ACID, 9.5, 500, 0.16, "end"))
    return "".join(out)


CAT = [
    "..x.......x..",
    "..xx.....xx..",
    "..xxxxxxxxx..",
    ".xxxxxxxxxxx.",
    ".xxoxxxxxoxx.",
    ".xxxxxxxxxxx.",
    ".xxxxx.xxxxx.",
    "..xxxxxxxxx..",
    "...xxxxxxx...",
    "..xxxxxxxxx..",
    ".xxxxxxxxxxxx",
    ".xxxxxxxxxxxx",
]


def art_mixtape():
    w, h = ART_W, H - 48
    out = [art_frame("mx")]
    cx, cy = 210, 206
    # wheel
    out.append(V.circle(cx, cy, 96, fill="#121418", stroke=K.INK_4))
    for deg in range(0, 360, 12):
        t = math.radians(deg)
        out.append(V.line(cx + 89 * math.cos(t), cy + 89 * math.sin(t), cx + 93 * math.cos(t),
                          cy + 93 * math.sin(t), K.INK_4, 1, 0.8))
    out.append(V.circle(cx, cy, 34, fill="#0D0F11", stroke=K.LINE))
    out.append(V.mono("MENU", cx, cy - 60, K.INK_2, 10, 500, 0.2, "middle"))
    # transport glyphs drawn as shapes
    def tri(x, y, s, d):
        return V.poly([(x, y - s), (x + d * s * 1.2, y), (x, y + s)], fill=K.INK_2, stroke=K.INK_2, w=0.5, close=True)
    out.append(tri(cx + 56, cy, 5, 1) + tri(cx + 63, cy, 5, 1))          # next
    out.append(tri(cx - 56, cy, 5, -1) + tri(cx - 63, cy, 5, -1))        # previous
    out.append(tri(cx - 7, cy + 64, 5, 1) + V.rect(cx + 3, cy + 59, 2.4, 10, fill=K.INK_2) + V.rect(cx + 7.5, cy + 59, 2.4, 10, fill=K.INK_2))
    # momentum arc
    arc = []
    for i in range(40):
        t = math.radians(-150 + i * 2.4)
        arc.append((cx + 75 * math.cos(t), cy + 75 * math.sin(t)))
    out.append(V.poly(arc, K.ACID, 2.2, 0.9))
    hx, hy = arc[-1]
    out.append(V.circle(hx, hy, 4, fill=K.ACID))
    # the cat, sitting on the wheel's rim
    px = 6
    ox, oy = cx - len(CAT[0]) * px / 2, cy - 96 - len(CAT) * px + 6
    for r, row in enumerate(CAT):
        for c, ch in enumerate(row):
            if ch == "x":
                out.append(V.rect(ox + c * px, oy + r * px, px, px, fill=K.INK))
            elif ch == "o":
                out.append(V.rect(ox + c * px, oy + r * px, px, px, fill=K.ACID))
    # tail
    for i, (tx, ty) in enumerate([(13, 10), (14, 9), (15, 8), (15, 7), (16, 6)]):
        out.append(V.rect(ox + tx * px, oy + ty * px, px, px, fill=K.INK))
    # now playing card
    nx, ny, nw, nh = 352, 52, 166, 120
    out.append(V.rect(nx, ny, nw, nh, fill="#0E1013", stroke=K.LINE, r=10))
    out.append(V.mono("NOW PLAYING", nx + 16, ny + 24, K.INK_3, 9, 500, 0.16))
    out.append(V.mono("SIDE A", nx + 16, ny + 48, K.INK, 12, 500, 0.1))
    out.append(V.mono("OFFLINE TAPE", nx + 16, ny + 66, K.INK_3, 9, 400, 0.14))
    out.append(V.rect(nx + 16, ny + 86, nw - 32, 3, fill=K.LINE))
    out.append(V.rect(nx + 16, ny + 86, (nw - 32) * 0.42, 3, fill=K.ACID))
    for i in range(10):
        hgt = [4, 9, 6, 12, 7, 10, 5, 8, 11, 6][i]
        out.append(V.rect(nx + 16 + i * 6, ny + 108 - hgt, 3, hgt, fill=K.INK_3))
    out.append(V.mono("WHEEL: MOMENTUM + DETENTS", 22, h - 22, K.INK_3, 9.5, 400, 0.16))
    out.append(V.mono("SHE NODS ON THE BEAT", w - 22, h - 22, K.INK_4, 9.5, 400, 0.16, "end"))
    return "".join(out)


# --------------------------------------------------------------------- cards --

CARDS = [
    dict(slug="skillverse", idx="E/01", meta="HACKATHON BUILD · NOV 2025", title="SkillVerse",
         desc="A learning tracker drawn as a galaxy. Every skill is a star, every path a constellation, "
              "and an AI guide sits inside it.",
         award="2ND PLACE · GREATUNIHACK 2025", state=("SOURCE PUBLIC", K.INK_2, "ring"),
         tags=["REACT", "TYPESCRIPT", "VITE", "THREE.JS", "SUPABASE"], art=art_skillverse, side="left"),
    dict(slug="orion", idx="E/02", meta="HACKATHON BUILD · I BUILT THE FRONTEND", title="Orion",
         desc="Application security as a constellation. Findings become stars, file dependencies become lines, "
              "and each star opens onto the vulnerable code and a concrete fix.",
         state=("REBUILDING", K.AMBER, "fill"),
         tags=["REACT", "TYPESCRIPT", "THREE.JS", "SUPABASE"], art=art_orion, side="right"),
    dict(slug="dilli-transit", idx="E/03", meta="DELHI METRO · INDEPENDENT", title="Dilli Transit",
         desc="A Delhi Metro trip planner with interchange-aware routing, fares, first and last trains, "
              "and a crowdsourced live layer for disruption and crowding.",
         state=("LIVE", K.INK_2, "fill"),
         tags=["NEXT.JS", "NESTJS", "POSTGRES", "REDIS", "MAPLIBRE"], art=art_dilli, side="left"),
    dict(slug="simdu", idx="E/04", meta="FLIGHT SIMULATION · PRE-LAUNCH", title="SIMDU",
         desc="Software that turns a phone or tablet into an aircraft’s flight-deck CDU. This is its "
              "cinematic pre-launch site: scroll-scrubbed sequences and real-time 3D.",
         state=("PRE-LAUNCH", K.INK_2, "ring"),
         tags=["NEXT.JS", "REACT THREE FIBER", "GSAP"], art=art_simdu, side="right"),
    dict(slug="mixtape", idx="E/05", meta="FOR FUN · PIXEL ART", title="Mixtape",
         desc="A pixel-art music player with a click wheel that has momentum, an offline chiptune tape, "
              "Spotify through PKCE, and a cat who nods along.",
         state=("LIVE", K.INK_2, "fill"),
         tags=["REACT", "TYPESCRIPT", "VITE", "FRAMER MOTION"], art=art_mixtape, side="left"),
]


def card(c):
    w, h = W, H
    out = [V.rect(0.5, 0.5, w - 1, h - 1, fill=K.BASE, stroke=K.LINE, r=20)]
    art_x = 24 if c["side"] == "left" else w - 24 - ART_W
    tx = (art_x + ART_W + 56) if c["side"] == "left" else 56
    tw = w - ART_W - 24 - 56 - 56
    out.append(V.group(c["art"](), transform=f"translate({art_x} 24)"))
    right = tx + tw
    out.append(V.mono(c["idx"], tx, 66, K.ACID, 12, 500, 0.14))
    out.append(V.mono(c["meta"], tx + V.mw(c["idx"], 12, 500, 0.14) + 14, 66, K.INK_3, 11, 400, 0.16))
    label, col, style = c["state"]
    out.append(V.mono(label, right, 66, col, 11, 500, 0.16, "end"))
    lx = right - V.mw(label, 11, 500, 0.16) - 13
    out.append(V.circle(lx, 61.5, 3.3, fill=col) if style == "fill" else V.circle(lx, 61.5, 3, stroke=col, sw_=1.2))
    out.append(V.line(tx, 84, right, 84, K.LINE))
    out.append(V.text(c["title"], tx - 3, 160, K.INK, 64, 600, "sans", -0.04))
    y = 204
    for ln in T.wrap(c["desc"], tw, "sans", 400, 19.5, 0):
        out.append(V.text(ln, tx, y, K.INK_2, 19.5, 400))
        y += 29
    if c.get("award"):
        y += 10
        aw = V.mw(c["award"], 11, 500, 0.16) + 44
        out.append(V.rect(tx, y - 4, aw, 30, r=15, fill=K.ACID, opacity=0.1, stroke=K.ACID, stroke_opacity=0.55))
        out.append(V.rect(tx + 14, y + 6, 8, 10, fill=K.ACID))
        out.append(V.mono(c["award"], tx + 30, y + 16, K.ACID, 11, 500, 0.16))
    out.append(V.line(tx, h - 70, right, h - 70, K.LINE))
    out.append(V.mono("   /   ".join(c["tags"]), tx, h - 42, K.INK_3, 11, 400, 0.14))
    title = f"{c['title']}: {c['desc']}"
    if c.get("award"):
        title += f" {c['award'].title()}."
    return V.doc(w, h, "".join(out), title, "Technologies: " + ", ".join(t.title() for t in c["tags"]))


# --------------------------------------------------------------------- stack --

PROJECTS = [("YK", "yukti"), ("SV", "skillverse"), ("OR", "orion"), ("DT", "dilli transit"),
            ("SD", "simdu"), ("MX", "mixtape"), ("JV", "jarvis")]

STACK_A = [
    ("LANGUAGES", [
        ("TypeScript", "1111110"), ("Python", "1000101"), ("SQL", "1011100"),
    ]),
    ("INTERFACE", [
        ("React", "1111110"), ("Next.js", "1001100"), ("Vite", "0110010"), ("Tailwind CSS", "0111100"),
        ("three.js · R3F", "1110100"), ("GSAP · Framer Motion", "0000110"), ("React Native · Expo", "0000100"),
        ("PySide6 · QML", "0000001"),
    ]),
]
STACK_B = [
    ("SERVER & DATA", [
        ("PostgreSQL · Supabase", "1111100"), ("NestJS", "0001000"), ("Drizzle · Prisma", "1001000"),
        ("Redis · SQLite", "0001001"), ("Better Auth", "1001000"),
    ]),
    ("AI & RUNTIME", [
        ("LLM features", "1100001"), ("Ollama · Whisper · Piper", "0000001"), ("Pyodide · WebAssembly", "1000000"),
    ]),
    ("SHIP & TEST", [
        ("Vitest · Jest · Playwright", "1011110"), ("Vercel · Fly.io · Docker", "1011110"),
        ("Turborepo · pnpm", "0001100"),
    ]),
]


def stack():
    w, h = W, 790
    out = [V.panel(w, h, "WHAT SHIPS WHERE", "READ FROM EACH PROJECT’S MANIFESTS · NOV 2026", "§04")]
    out.append(V.text("A dependency matrix, not a skills chart.", 54, 130, K.INK, 34, 500, "sans", -0.025))
    out.append(V.text("Each dot is a tool that a real project of mine depends on. No percentages, no self-ratings.",
                      56, 166, K.INK_3, 17, 400))
    # legend of project codes
    lx = 56
    for code, name in PROJECTS:
        out.append(V.mono(code, lx, 204, K.ACID if code == "YK" else K.INK_2, 11, 500, 0.12))
        lx += V.mw(code, 11, 500, 0.12) + 7
        out.append(V.mono(name.upper(), lx, 204, K.INK_4, 10, 400, 0.14))
        lx += V.mw(name.upper(), 10, 400, 0.14) + 22

    def block(groups, x0):
        o = []
        name_w = 236
        col_w = 41
        top = 252
        # column header
        for i, (code, _) in enumerate(PROJECTS):
            cx = x0 + name_w + col_w * i + col_w / 2
            o.append(V.mono(code, cx, top, K.ACID if code == "YK" else K.INK_3, 10.5, 500, 0.1, "middle"))
        o.append(V.rect(x0 + name_w, top + 10, col_w, 0, fill="none"))
        y = top + 16
        o.append(V.line(x0, y, x0 + name_w + col_w * 7, y, K.LINE))
        rows_y = []
        for gname, rows in groups:
            y += 30
            o.append(V.mono(gname, x0, y, K.INK_4, 10, 500, 0.2))
            y += 6
            for tech, mask in rows:
                y += 30
                rows_y.append(y)
                o.append(V.text(tech, x0, y, K.INK, 16.5, 400))
                cnt = mask.count("1")
                o.append(V.mono(f"×{cnt}", x0 + name_w - 14, y, K.INK_4, 10.5, 400, 0.04, "end"))
                for i, bit in enumerate(mask):
                    cx = x0 + name_w + col_w * i + col_w / 2
                    if bit == "1":
                        o.append(V.circle(cx, y - 5.5, 5, fill=K.ACID if i == 0 else K.INK))
                    else:
                        o.append(V.circle(cx, y - 5.5, 1.4, fill=K.INK_4))
                o.append(V.line(x0, y + 11, x0 + name_w + col_w * 7, y + 11, K.LINE_SOFT))
        # faint band down the current project's column
        bx = x0 + name_w
        o.insert(0, V.rect(bx + 4, top - 18, col_w - 8, y - top + 34, r=8, fill=K.ACID, opacity=0.05))
        return "".join(o)

    out.append(block(STACK_A, 56))
    out.append(block(STACK_B, 56 + 553))
    out.append(V.line(44, h - 58, w - 44, h - 58, K.LINE))
    out.append(V.circle(52, h - 34.5, 5, fill=K.INK))
    out.append(V.mono("USED IN THAT PROJECT", 66, h - 30, K.INK_3, 10.5, 400, 0.16))
    out.append(V.circle(260, h - 34.5, 5, fill=K.ACID))
    out.append(V.mono("YUKTI, THE CURRENT BUILD", 274, h - 30, K.INK_3, 10.5, 400, 0.16))
    out.append(V.mono("×N = NUMBER OF PROJECTS", w - 44, h - 30, K.INK_4, 10.5, 400, 0.16, "end"))
    desc = []
    for groups in (STACK_A, STACK_B):
        for g, rows in groups:
            desc.append(g.title() + ": " + ", ".join(f"{t} ({', '.join(PROJECTS[i][1] for i, b in enumerate(m) if b == '1')})" for t, m in rows))
    return V.doc(w, h, "".join(out), "Technical stack as a dependency matrix", ". ".join(desc))


def main(write):
    for c in CARDS:
        write(f"exp-{c['slug']}.svg", card(c))
    write("stack.svg", stack())
