# R/O asset pipeline

Everything in `assets/` is generated here. Nothing is hand-drawn or downloaded.

```bash
pip install pillow numpy fonttools brotli uharfbuzz
python scripts/build.py
```

| File | Makes |
| :-- | :-- |
| `header.py` | `header.gif` (1200×460, 8 s loop at 25 fps) and `header-static.png` |
| `eof.py` | `eof.gif` (6 s loop) and `eof-static.png` |
| `panels.py` | section strips (light and dark), intro, status, Yukti feature |
| `cards.py` | experiment cards and the stack matrix |
| `preview.py` | renders SVGs to PNG with headless Chrome for review |

## How it stays consistent

- **One token file.** `ro/tokens.py` holds every colour. Acid (`#C6FF3D`) means active or passing; amber means failing or rebuilding. Nothing else is coloured.
- **Real typography in SVG.** GitHub serves README images without web fonts, so `ro/typeset.py` shapes text with HarfBuzz (kerning included) and writes the glyph outlines into each SVG. Small text reuses one outline per glyph through `<use>`.
- **No CSS or scripts in SVG.** Every SVG is static. Motion lives only in the GIFs, which GitHub always renders.
- **Seamless loops.** Everything that moves is periodic in the loop length: orbits complete whole revolutions, the boot log scrolls through exactly one cycle, the prompt retypes its first command, the cursor blinks a whole number of times.
- **A designed palette.** Both GIFs map every frame onto one 255-colour palette built from the tokens, with a dense near-black ramp, so gradients don't band and colours never shimmer between frames. Unchanged pixels are written as transparent, which keeps the header under 2 MB.
- **Reduced motion.** The README serves the static PNGs through `<picture>` when the viewer prefers reduced motion.

Fonts: [Geist and Geist Mono](https://github.com/vercel/geist-font), SIL Open Font License 1.1 (`fonts/OFL.txt`).
