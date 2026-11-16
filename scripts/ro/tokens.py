"""R/O design tokens.

One accent, used on purpose. Everything else is a step on a warm grey ramp.
"""

# Surfaces: almost-black to graphite
VOID = "#070809"      # deepest background (header, screens)
BASE = "#0B0C0E"      # panel background
PANEL = "#101215"     # raised surface
RAISE = "#16181C"     # windows, chips
LINE = "#25282E"      # hairlines
LINE_SOFT = "#17191D" # grid

# Ink: warm white and its quieter steps
INK = "#EDE9E1"
INK_2 = "#A9A49B"
INK_3 = "#6E6B64"
INK_4 = "#46443F"

# Accent: acid. Means "active", "passing", "now".
ACID = "#C6FF3D"
ACID_DIM = "#6F8F22"

# Secondary: amber. Means "warning", "failing", "rebuilding". Used rarely.
AMBER = "#FFB23E"

# Light-theme ink for transparent typographic strips
L_INK = "#111214"
L_INK_2 = "#55524C"
L_INK_3 = "#8A867E"
L_LINE = "#D9D6CF"
L_ACID = "#4E7A00"  # acid darkened enough to read on white

W = 1200  # canonical canvas width for every panel


def rgb(hex_):
    h = hex_.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
