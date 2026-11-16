"""Static SVG panels for the profile README.

    python scripts/panels.py   -> assets/*.svg

Dark 'screen' panels look the same in GitHub's light and dark themes. The
typographic strips are transparent and ship in two versions, chosen with
<picture> and prefers-color-scheme.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from ro import svg as V
from ro import tokens as K
from ro import typeset as T

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
W = K.W

DARK = dict(ink=K.INK, ink2=K.INK_2, ink3=K.INK_3, line=K.LINE, acid=K.ACID)
LIGHT = dict(ink=K.L_INK, ink2=K.L_INK_2, ink3=K.L_INK_3, line=K.L_LINE, acid=K.L_ACID)


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    return name


# ---------------------------------------------------------------- strips ---

SECTIONS = [
    ("init", "00", "INIT", "~/README.md"),
    ("status", "01", "SYSTEM STATUS", "/proc/self/status"),
    ("building", "02", "NOW BUILDING", "~/yukti"),
    ("experiments", "03", "SELECTED EXPERIMENTS", "~/lab"),
    ("stack", "04", "TECHNICAL STACK", "package manifests"),
    ("log", "05", "OPERATOR NOTES", "~/.principles"),
]


def strip(idx, label, meta, th):
    h = 56
    y = 34
    out = [V.mono("§" + idx, 2, y, th["acid"], 14, 500, 0.12)]
    x = 2 + V.mw("§" + idx, 14, 500, 0.12) + 18
    out.append(V.mono(label, x, y, th["ink"], 14, 500, 0.2))
    x += V.mw(label, 14, 500, 0.2) + 22
    mx = W - 2 - V.mw(meta, 13, 400, 0.08)
    out.append(V.line(x, y - 5, mx - 22, y - 5, th["ink3"], opacity=0.45))
    out.append(V.line(mx - 22, y - 9, mx - 22, y - 1, th["ink3"], opacity=0.45))
    out.append(V.mono(meta, W - 2, y, th["ink3"], 13, 400, 0.08, "end"))
    return V.doc(W, h, "".join(out), f"Section {idx}: {label.title()}")


# ----------------------------------------------------------------- intro ---

INTRO_LINES = ["Most ideas sound great", "until they have to run.", "That’s the part I like."]


def intro(th):
    size, lh = 64, 70
    out = []
    y = 74
    for i, ln in enumerate(INTRO_LINES):
        col = th["ink"] if i < 2 else th["ink3"]
        out.append(V.text(ln, -3, y, col, size, 500, "sans", -0.032))
        y += lh
    # margin note, editorial style
    nx = 900
    out.append(V.line(nx, 26, nx, 196, th["line"]))
    notes = [("WHO", "Riddhiman Ojha"), ("WHAT", "Computer Science"), ("WHERE", "University of Manchester")]
    ny = 42
    for k, v in notes:
        out.append(V.mono(k, nx + 22, ny, th["ink3"], 11, 400, 0.18))
        out.append(V.text(v, nx + 22, ny + 24, th["ink"], 17, 500, "sans", -0.01))
        ny += 58
    return V.doc(W, 230, "".join(out), "Most ideas sound great until they have to run. That's the part I like.",
                 "Riddhiman Ojha, Computer Science, University of Manchester")


# ---------------------------------------------------------------- status ---

STATUS_ROWS = [
    ("USER", "RIDDHIMAN OJHA", K.INK),
    ("LOCATION", "MANCHESTER, UK", K.INK),
    ("ROLE", "COMPUTER SCIENCE STUDENT", K.INK),
    ("INSTITUTION", "UNIVERSITY OF MANCHESTER", K.INK),
    ("STATUS", "BUILDING", K.ACID),
    ("CURRENT PROJECT", "YUKTI", K.ACID),
]

PROCESSES = [
    ("01", "yukti", "RUNNING", K.ACID, "fill"),
    ("02", "dilli-transit", "LIVE", K.INK_2, "fill"),
    ("03", "orion", "REBUILDING", K.AMBER, "fill"),
    ("04", "simdu", "PRE-LAUNCH", K.INK_2, "ring"),
    ("05", "mixtape", "LIVE", K.INK_2, "fill"),
    ("06", "skillverse", "SHIPPED", K.INK_3, "ring"),
]


def status():
    w, h = W, 440
    out = [V.panel(w, h, "riddhiman@r/o:~$ cat /proc/self/status", "STATIC SNAPSHOT · NOT A LIVE FEED", "§01.1")]
    y = 124
    for k, v, col in STATUS_ROWS:
        out.append(V.mono(k, 56, y, K.INK_3, 13, 400, 0.16))
        kx = 56 + V.mw(k, 13, 400, 0.16) + 10
        out.append(V.dots_leader(kx, 300, y, K.INK_4))
        if col == K.ACID and k == "STATUS":
            out.append(V.rect(314, y - 15, 9, 17, fill=K.ACID))
            out.append(V.mono(v, 334, y, col, 21, 500, 0.06))
        else:
            out.append(V.mono(v, 314, y, col, 21, 500, 0.06))
        y += 46
    # process table
    px = 742
    out.append(V.line(700, 92, 700, 384, K.LINE))
    out.append(V.mono("PID", px, 104, K.INK_4, 11, 400, 0.18))
    out.append(V.mono("PROCESS", px + 56, 104, K.INK_4, 11, 400, 0.18))
    out.append(V.mono("STATE", 1144, 104, K.INK_4, 11, 400, 0.18, "end"))
    out.append(V.line(px, 118, 1144, 118, K.LINE))
    y = 154
    for pid, name, state, col, style in PROCESSES:
        out.append(V.mono(pid, px, y, K.INK_4, 15, 400, 0.04))
        out.append(V.mono(name, px + 56, y, K.INK if pid == "01" else K.INK_2, 17, 500 if pid == "01" else 400, 0.02))
        sx = 1144 - V.mw(state, 12, 500, 0.16)
        out.append(V.mono(state, 1144, y, col, 12, 500, 0.16, "end"))
        if style == "fill":
            out.append(V.circle(sx - 14, y - 4.5, 3.5, fill=col))
        else:
            out.append(V.circle(sx - 14, y - 4.5, 3.2, stroke=col, sw_=1.2))
        y += 40
    out.append(V.line(44, 392, w - 44, 392, K.LINE))
    out.append(V.mono("WRITTEN BY HAND · LAST EDITED 2026-11-16", 44, 418, K.INK_4, 11, 400, 0.16))
    out.append(V.mono("LIVE = DEPLOYED AND REACHABLE WHEN WRITTEN", w - 44, 418, K.INK_4, 11, 400, 0.16, "end"))
    desc = "; ".join(f"{k}: {v}" for k, v, _ in STATUS_ROWS) + ". Processes: " + "; ".join(
        f"{n} {s.lower()}" for _, n, s, _, _ in PROCESSES) + "."
    return V.doc(w, h, "".join(out), "System status (static snapshot)", desc)


# ----------------------------------------------------------------- yukti ---

PY = [
    [("def ", "k"), ("apply_discount", "f"), ("(total, pct):", "p")],
    [("    ", "p"), ('"""pct may be 0-1 or 0-100."""', "c")],
    [("    ", "p"), ("if ", "k"), ("pct > ", "p"), ("1", "n"), (":", "p")],
    [("        pct = pct / ", "p"), ("100", "n")],
    [("    ", "p"), ("return ", "k"), ("round(total * pct, ", "p"), ("2", "n"), (")", "p")],
    [],
    [("def ", "k"), ("basket_total", "f"), ("(items, pct=", "p"), ("0", "n"), ("):", "p")],
    [("    subtotal = sum(i.price ", "p"), ("for ", "k"), ("i ", "p"), ("in ", "k"), ("items)", "p")],
    [("    ", "p"), ("return ", "k"), ("apply_discount(subtotal, pct)", "p")],
]
PY_COL = dict(k=K.INK_3, f=K.INK, p=K.INK_2, c=K.INK_4, n=K.ACID_DIM)


def check(x, y, col, s=1.0):
    return V.poly([(x, y), (x + 3.5 * s, y + 3.5 * s), (x + 10 * s, y - 4 * s)], col, 1.8)


def cross(x, y, col, s=1.0):
    return V.line(x, y - 4 * s, x + 8 * s, y + 4 * s, col, 1.8, cap="round") + V.line(x + 8 * s, y - 4 * s, x, y + 4 * s, col, 1.8, cap="round")


def yukti():
    w, h = W, 720
    out = [V.panel(w, h, "FEATURED BUILD", "LIVE · YUKTI-GREEN.VERCEL.APP", "§02.1")]
    out.append(V.defs(V.glow_filter("yg", 10)))
    # left: the pitch
    out.append(V.rect(56, 108, 9, 16, fill=K.ACID))
    out.append(V.mono("NOW BUILDING", 76, 122, K.ACID, 12, 500, 0.2))
    out.append(V.text("Yukti", 50, 250, K.INK, 150, 600, "sans", -0.045))
    y = 306
    for ln in T.wrap("Practise the assessment the employer actually runs.", 470, "sans", 500, 30, -0.02):
        out.append(V.text(ln, 56, y, K.INK, 30, 500, "sans", -0.02))
        y += 38
    y += 12
    body = ("A candidate-side platform for technical recruitment assessments. Pick a company and a role; "
            "get realistic practice, timed simulations and a diagnosis after every attempt.")
    for ln in T.wrap(body, 456, "sans", 400, 18.5, 0):
        out.append(V.text(ln, 56, y, K.INK_2, 18.5, 400))
        y += 28
    y += 22
    feats = ["PYTHON RUNS IN THE BROWSER, VIA PYODIDE", "HIDDEN TESTS ON EVERY PROBLEM",
             "DEBUGGING INSIDE AN EXISTING CODEBASE", "REVIEWING AN AI ASSISTANT’S CODE",
             "TIMED, MULTI-SECTION SIMULATIONS"]
    for f in feats:
        out.append(V.rect(56, y - 8, 5, 5, fill=K.ACID))
        out.append(V.mono(f, 74, y, K.INK_2, 12.5, 400, 0.1))
        y += 25
    out.append(V.line(56, 648, 520, 648, K.LINE))
    out.append(V.mono("NEXT.JS · TYPESCRIPT · POSTGRES · DRIZZLE · PYODIDE · CODEMIRROR", 56, 676, K.INK_3, 10.5, 400, 0.1))

    # right: an illustrated assessment window
    x0, y0, x1, y1 = 572, 96, 1148, 652
    out.append(V.rect(x0, y0, x1 - x0, y1 - y0, fill="#0D0F12", stroke=K.LINE, r=14))
    out.append(V.mono("SECTION 2 / 4 · DEBUGGING", x0 + 22, y0 + 28, K.INK_3, 11, 400, 0.16))
    out.append(V.mono("REMAINING", x1 - 92, y0 + 28, K.INK_4, 10, 400, 0.16, "end"))
    out.append(V.mono("38:12", x1 - 22, y0 + 29, K.INK, 15, 500, 0.04, "end"))
    out.append(V.line(x0, y0 + 44, x1, y0 + 44, K.LINE))
    # section tabs
    tabs = [("CODING", "done"), ("DEBUGGING", "now"), ("AI REVIEW", ""), ("SQL", ""), ("JUDGEMENT", "")]
    tx = x0 + 22
    ty = y0 + 72
    for name, state in tabs:
        col = K.INK if state == "now" else (K.INK_3 if state == "done" else K.INK_4)
        if state == "done":
            out.append(check(tx, ty - 4, K.ACID, 0.8))
            out.append(V.mono(name, tx + 14, ty, col, 11, 500, 0.14))
            tw = V.mw(name, 11, 500, 0.14) + 14
        else:
            out.append(V.mono(name, tx, ty, col, 11, 500, 0.14))
            tw = V.mw(name, 11, 500, 0.14)
        if state == "now":
            out.append(V.line(tx, ty + 12, tx + tw, ty + 12, K.ACID, 2))
        tx += tw + 26
    out.append(V.line(x0, y0 + 86, x1, y0 + 86, K.LINE))
    # file tree
    fy = y0 + 118
    out.append(V.mono("SHOP/", x0 + 22, fy, K.INK_4, 10.5, 400, 0.16))
    files = [("pricing.py", True), ("basket.py", False), ("test_pricing.py", False)]
    fy += 26
    for fn, active in files:
        if active:
            out.append(V.rect(x0 + 12, fy - 15, 128, 22, fill=K.RAISE, r=5))
        out.append(V.mono(fn, x0 + 24, fy, K.INK if active else K.INK_3, 12, 400, 0.0))
        fy += 26
    out.append(V.line(x0 + 152, y0 + 86, x0 + 152, y0 + 370, K.LINE))
    # editor
    ex = x0 + 172
    ey = y0 + 120
    for i, toks in enumerate(PY):
        ln = i + 1
        if ln == 5:
            out.append(V.rect(x0 + 153, ey - 15, x1 - x0 - 153, 22, fill=K.AMBER, opacity=0.08))
            out.append(V.rect(x0 + 153, ey - 15, 2, 22, fill=K.AMBER))
        out.append(V.mono(f"{ln:>2}", ex - 4, ey, K.INK_4, 12, 400, 0.0))
        cx = ex + 26
        for s, kind in toks:
            out.append(V.mono(s, cx, ey, PY_COL[kind], 12.5, 400, 0.0))
            cx += V.mw(s, 12.5, 400, 0.0)
        ey += 27
    out.append(V.line(x0, y0 + 370, x1, y0 + 370, K.LINE))
    # assistant suggestion
    ax, ay = x0 + 22, y0 + 398
    out.append(V.mono("ASSISTANT SUGGESTION", ax, ay, K.INK_3, 10.5, 500, 0.18))
    out.append(V.mono("REVIEW BEFORE YOU ACCEPT", x1 - 22, ay, K.INK_4, 10.5, 400, 0.18, "end"))
    out.append(V.rect(ax, ay + 14, x1 - x0 - 44, 30, fill=K.AMBER, opacity=0.07))
    out.append(V.mono("−", ax + 12, ay + 34, K.AMBER, 13, 500, 0))
    out.append(V.mono("return round(total * pct, 2)", ax + 34, ay + 34, K.AMBER, 12.5, 400, 0, opacity=0.9))
    out.append(V.rect(ax, ay + 46, x1 - x0 - 44, 30, fill=K.ACID, opacity=0.07))
    out.append(V.mono("+", ax + 12, ay + 66, K.ACID, 13, 500, 0))
    out.append(V.mono("return round(total * (1 - pct), 2)", ax + 34, ay + 66, K.ACID, 12.5, 400, 0))
    # tests
    ty = y1 - 34
    out.append(V.line(x0, ty - 26, x1, ty - 26, K.LINE))
    out.append(V.mono("TESTS", ax, ty, K.INK_4, 10.5, 400, 0.18))
    out.append(check(ax + 70, ty - 4, K.ACID))
    out.append(V.mono("VISIBLE 3/3", ax + 88, ty, K.INK_2, 11, 500, 0.14))
    out.append(cross(ax + 204, ty - 4, K.AMBER, 0.8))
    out.append(V.mono("HIDDEN 4/6", ax + 220, ty, K.INK_2, 11, 500, 0.14))
    bx = x1 - 22
    label = "RUN TESTS"
    bw = V.mw(label, 11, 500, 0.16) + 28
    out.append(V.rect(bx - bw, ty - 17, bw, 26, stroke=K.ACID, r=13, stroke_opacity=0.7))
    out.append(V.mono(label, bx - bw / 2, ty, K.ACID, 11, 500, 0.16, "middle"))
    out.append(V.mono("ILLUSTRATION OF THE DEBUGGING AND AI-REVIEW FORMATS, NOT A SCREENSHOT", x1, 680, K.INK_4, 9.5, 400, 0.14, "end"))
    return V.doc(w, h, "".join(out), "Yukti: practise the assessment the employer actually runs",
                 "Candidate-side platform for technical recruitment assessments. Python in the browser via Pyodide, "
                 "hidden tests, debugging inside an existing codebase, reviewing an AI assistant's code, timed "
                 "multi-section simulations. Built with Next.js, TypeScript, Postgres, Drizzle, Pyodide and CodeMirror.")


def main_part1():
    OUT.mkdir(exist_ok=True)
    for sid, idx, label, meta in SECTIONS:
        write(f"strip-{sid}-dark.svg", strip(idx, label, meta, DARK))
        write(f"strip-{sid}-light.svg", strip(idx, label, meta, LIGHT))
    write("intro-dark.svg", intro(DARK))
    write("intro-light.svg", intro(LIGHT))
    write("status.svg", status())
    write("yukti.svg", yukti())


if __name__ == "__main__":
    import cards
    main_part1()
    cards.main(write)
