"""Small SVG vocabulary for the R/O panels. Static only: no scripts, no CSS
animation, no external references, text drawn as outlines."""
from __future__ import annotations

import math
from html import escape

from . import tokens as K
from . import typeset as T


def doc(w, h, body, title, desc=""):
    body = T.take_glyph_defs() + body
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-labelledby="t d" fill="none">'
        f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>{body}</svg>'
    )


def n(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def text(s, x, y, fill, size=16, weight=400, family="sans", tracking=0.0, anchor="start", opacity=None):
    return T.svg_text(s, x, y, fill, family, weight, size, tracking, anchor, opacity)


def mono(s, x, y, fill, size=12, weight=400, tracking=0.14, anchor="start", opacity=None):
    return text(s, x, y, fill, size, weight, "mono", tracking, anchor, opacity)


def mw(s, size=12, weight=400, tracking=0.14):
    return T.width(s, "mono", weight, size, tracking)


def sw(s, size=16, weight=400, tracking=0.0):
    return T.width(s, "sans", weight, size, tracking)


def line(x1, y1, x2, y2, stroke=K.LINE, w=1, opacity=None, dash=None, cap=None):
    o = f' stroke-opacity="{opacity}"' if opacity is not None else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    c = f' stroke-linecap="{cap}"' if cap else ""
    return f'<path d="M{n(x1)} {n(y1)}L{n(x2)} {n(y2)}" stroke="{stroke}" stroke-width="{w}"{o}{d}{c}/>'


def poly(pts, stroke=K.LINE, w=1, opacity=None, fill="none", close=False, join="round", dash=None):
    d = "M" + "L".join(f"{n(x)} {n(y)}" for x, y in pts) + ("Z" if close else "")
    o = f' stroke-opacity="{opacity}"' if opacity is not None else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{w}" fill="{fill}" stroke-linejoin="{join}" stroke-linecap="round"{o}{da}/>'


def rect(x, y, w, h, fill="none", stroke=None, sw_=1, r=0, opacity=None, stroke_opacity=None):
    s = f' stroke="{stroke}" stroke-width="{sw_}"' if stroke else ""
    o = f' fill-opacity="{opacity}"' if opacity is not None else ""
    so = f' stroke-opacity="{stroke_opacity}"' if stroke_opacity is not None else ""
    rr = f' rx="{n(r)}"' if r else ""
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"{rr} fill="{fill}"{o}{s}{so}/>'


def circle(cx, cy, r, fill="none", stroke=None, sw_=1, opacity=None, stroke_opacity=None, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw_}"' if stroke else ""
    o = f' fill-opacity="{opacity}"' if opacity is not None else ""
    so = f' stroke-opacity="{stroke_opacity}"' if stroke_opacity is not None else ""
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{fill}"{o}{s}{so}{extra}/>'


def ellipse(cx, cy, rx, ry, stroke=K.LINE, sw_=1, rot=0, opacity=None, fill="none", dash=None):
    o = f' stroke-opacity="{opacity}"' if opacity is not None else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    t = f' transform="rotate({n(rot)} {n(cx)} {n(cy)})"' if rot else ""
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" stroke="{stroke}" stroke-width="{sw_}" fill="{fill}"{o}{d}{t}/>'


def group(body, opacity=None, transform=None, filter_=None, clip=None):
    a = ""
    if opacity is not None:
        a += f' opacity="{opacity}"'
    if transform:
        a += f' transform="{transform}"'
    if filter_:
        a += f' filter="url(#{filter_})"'
    if clip:
        a += f' clip-path="url(#{clip})"'
    return f"<g{a}>{body}</g>"


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


def grid_pattern(pid, size=40, stroke="#15171A", ox=0, oy=0):
    return (f'<pattern id="{pid}" width="{size}" height="{size}" patternUnits="userSpaceOnUse" x="{ox}" y="{oy}">'
            f'<path d="M{size} 0H0V{size}" stroke="{stroke}" stroke-width="1"/></pattern>')


def glow_filter(fid, sd=6):
    return (f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%">'
            f'<feGaussianBlur stdDeviation="{sd}"/></filter>')


def clip_rect(cid, x, y, w, h, r=0):
    return f'<clipPath id="{cid}">{rect(x, y, w, h, fill="#000", r=r)}</clipPath>'


def crop_marks(x0, y0, x1, y1, size=10, col=K.INK_4):
    out = []
    for (x, y, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        out.append(poly([(x + size * sx, y), (x, y), (x, y + size * sy)], col, 1, join="miter"))
    return "".join(out)


def mark(cx, cy, r=7, ink=K.INK_3, acid=K.ACID):
    """The R/O signature: a ring with one satellite."""
    a = math.radians(-40)
    return (circle(cx, cy, r, stroke=ink, sw_=1.2)
            + circle(cx + r * math.cos(a), cy + r * math.sin(a), max(1.8, r * 0.3), fill=acid))


def panel(w, h, left_label, right_label, idx="", body_grid=True, pid="pg"):
    """Shared chrome for the dark 'screen' panels."""
    out = [defs(grid_pattern(pid, 40, "#14161A", 0, 4), clip_rect(pid + "c", 0.5, 0.5, w - 1, h - 1, 20))]
    out.append(rect(0.5, 0.5, w - 1, h - 1, fill=K.BASE, stroke=K.LINE, r=20))
    if body_grid:
        out.append(group(rect(0, 0, w, h, fill=f"url(#{pid})"), clip=pid + "c"))
    out.append(crop_marks(16, 16, w - 16, h - 16, 9))
    x = 44
    if idx:
        out.append(mono(idx, x, 45, K.ACID, 12, 500, 0.14))
        x += mw(idx, 12, 500) + 14
    out.append(mono(left_label, x, 45, K.INK_3, 12, 400, 0.16))
    out.append(mono(right_label, w - 44, 45, K.INK_3, 12, 400, 0.16, "end"))
    out.append(line(44, 64, w - 44, 64, K.LINE))
    return "".join(out)


def dots_leader(x0, x1, y, col=K.INK_4, step=6, opacity=0.9):
    out = []
    x = x0
    while x < x1:
        out.append(rect(x, y - 2, 1.4, 1.4, fill=col, opacity=opacity))
        x += step
    return "".join(out)
