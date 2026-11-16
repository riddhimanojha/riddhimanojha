"""Typography engine.

Text is shaped with HarfBuzz (kerning included) and then either
  * emitted as SVG outlines, so SVGs render identically everywhere with no
    font loading (GitHub serves README images without web fonts), or
  * drawn glyph by glyph with Pillow/FreeType for raster frames.

Fonts: Geist and Geist Mono (SIL OFL 1.1), static weights instanced from the
variable fonts in scripts/fonts on first use.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import ImageFont

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
CACHE = FONT_DIR / ".cache"
VARIABLE = {"sans": "geist-latin-var.ttf", "mono": "geist-mono-latin-var.ttf"}
FEATURES = {"kern": True, "liga": False, "calt": False}


@dataclass
class Face:
    path: Path
    tt: TTFont
    hb_font: hb.Font
    upem: int
    glyphs: object


@lru_cache(maxsize=None)
def face(family: str, weight: int) -> Face:
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"{family}-{weight}.ttf"
    if not path.exists():
        var = TTFont(FONT_DIR / VARIABLE[family])
        static = instancer.instantiateVariableFont(var, {"wght": weight})
        static.save(path)
    tt = TTFont(path)
    hb_face = hb.Face(hb.Blob.from_file_path(str(path)))
    return Face(path, tt, hb.Font(hb_face), tt["head"].unitsPerEm, tt.getGlyphSet())


@dataclass
class Run:
    glyphs: list  # (glyph_name, x_px, char)
    width: float


def shape(text: str, family="sans", weight=400, size=16.0, tracking=0.0) -> Run:
    """tracking is in em (0.1 = +10% of the font size per glyph)."""
    if not text:
        return Run([], 0.0)
    f = face(family, weight)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(f.hb_font, buf, FEATURES)
    scale = size / f.upem
    order = f.tt.getGlyphOrder()
    x = 0.0
    out = []
    infos, positions = buf.glyph_infos, buf.glyph_positions
    for i, (info, pos) in enumerate(zip(infos, positions)):
        out.append((order[info.codepoint], x + pos.x_offset * scale, text[info.cluster]))
        x += pos.x_advance * scale
        if i < len(infos) - 1:
            x += tracking * size
    return Run(out, x)


def width(text, family="sans", weight=400, size=16.0, tracking=0.0) -> float:
    return shape(text, family, weight, size, tracking).width


def _num(v: float) -> str:
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def svg_path_d(text, x, y, family="sans", weight=400, size=16.0, tracking=0.0, anchor="start") -> tuple[str, float]:
    run = shape(text, family, weight, size, tracking)
    if anchor == "middle":
        x -= run.width / 2
    elif anchor == "end":
        x -= run.width
    f = face(family, weight)
    s = size / f.upem
    pen = SVGPathPen(f.glyphs, ntos=_num)
    for name, gx, _ in run.glyphs:
        f.glyphs[name].draw(TransformPen(pen, (s, 0, 0, -s, x + gx, y)))
    return pen.getCommands(), run.width


# Glyphs used by the document being built. Small text is drawn as <use>
# references to one outline per glyph, which keeps text-heavy panels small.
GLYPHS: dict[str, str] = {}
REUSE_BELOW = 40  # px; larger display type is emitted as direct outlines


def _glyph_id(family, weight, name):
    gid = f"{family[0]}{weight}-{name}"
    if gid not in GLYPHS:
        f = face(family, weight)
        pen = SVGPathPen(f.glyphs, ntos=lambda v: str(round(v)))
        f.glyphs[name].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))
        GLYPHS[gid] = pen.getCommands()
    return gid


def take_glyph_defs() -> str:
    out = "".join(f'<path id="{gid}" d="{d}"/>' for gid, d in GLYPHS.items() if d)
    GLYPHS.clear()
    return f"<defs>{out}</defs>" if out else ""


def svg_text(text, x, y, fill, family="sans", weight=400, size=16.0, tracking=0.0,
             anchor="start", opacity=None, extra="") -> str:
    """SVG that draws `text` with its baseline at y, as outlines."""
    if not text.strip():
        return ""
    op = f' fill-opacity="{opacity}"' if opacity is not None else ""
    if size >= REUSE_BELOW:
        d, _ = svg_path_d(text, x, y, family, weight, size, tracking, anchor)
        return f'<path d="{d}" fill="{fill}"{op}{extra}/>'
    run = shape(text, family, weight, size, tracking)
    if anchor == "middle":
        x -= run.width / 2
    elif anchor == "end":
        x -= run.width
    s = size / face(family, weight).upem
    uses = []
    for name, gx, ch in run.glyphs:
        if ch == " ":
            continue
        gid = _glyph_id(family, weight, name)
        uses.append(f'<use href="#{gid}" x="{_num((x + gx) / s)}" y="{_num(y / s)}"/>')
    return f'<g fill="{fill}"{op}{extra} transform="scale({s:.6g})">{"".join(uses)}</g>'


def wrap(text, max_width, family="sans", weight=400, size=16.0, tracking=0.0) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if cur and width(trial, family, weight, size, tracking) > max_width:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- raster ----

@lru_cache(maxsize=None)
def pil_font(family: str, weight: int, size: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(face(family, weight).path), size=round(size))


def draw_text(draw, xy, text, fill, family="sans", weight=400, size=16.0, tracking=0.0, anchor="start"):
    """Draw kerned text with Pillow. xy is (x, baseline_y). Returns width."""
    x, y = xy
    run = shape(text, family, weight, round(size), tracking)
    if anchor == "middle":
        x -= run.width / 2
    elif anchor == "end":
        x -= run.width
    font = pil_font(family, weight, size)
    for _, gx, ch in run.glyphs:
        if ch != " ":
            draw.text((x + gx, y), ch, font=font, fill=fill, anchor="ls")
    return run.width
