"""
generator/components/tech_stack.py
--------------------------------------
A clean grid of icon-only "tech stack" badges, driven entirely by
config.TECH_STACK. Each badge is a solid-colored rounded square with
just the glyph centered inside — no inline label text, which is what
was causing the glyph/label collision in the earlier text+icon layout.
The tool name is still available on hover via a native SVG <title>
tooltip, so it's not lost, just not permanently on-screen.

Uses generic glyphs/emoji + a brand-ish accent color rather than
tracing actual logos, so there's no trademark/logo reproduction
concern.
"""

from .. import config
from ..utils import esc, glass_panel, section_title


def _text_color_for(hex_color: str) -> str:
    """Pick black or white glyph text based on background luminance,
    so the icon stays readable regardless of the badge's brand color."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return "#0b0e17"
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#0b0e17" if luminance > 0.55 else "#ffffff"


def build(x: int, y: int, w: int, h: int, theme: dict = config.THEME) -> str:
    items = config.TECH_STACK
    cols = 4
    gap = 14
    pad = 20
    cell = (w - 2 * pad - (cols - 1) * gap) / cols
    cell = min(cell, 60)  # keep icons from ballooning on very wide panels

    row_w = cols * cell + (cols - 1) * gap
    start_x = x + (w - row_w) / 2  # center the grid within the panel

    badges = []
    for i, item in enumerate(items[:8]):
        col = i % cols
        row = i // cols
        bx = start_x + col * (cell + gap)
        by = y + 46 + row * (cell + gap)
        color = item.get("color", theme["neon_blue"])
        text_color = _text_color_for(color)
        font_size = cell * 0.34
        badges.append(f"""
      <g transform="translate({bx},{by})">
        <title>{esc(item['label'])}</title>
        <rect width="{cell}" height="{cell}" rx="{cell*0.24:.1f}" fill="{color}"/>
        <rect width="{cell}" height="{cell}" rx="{cell*0.24:.1f}" fill="none"
              stroke="{color}" stroke-width="1" opacity="0.5" filter="url(#softGlow)"/>
        <text x="{cell/2}" y="{cell/2 + font_size*0.34}" text-anchor="middle"
              font-size="{font_size:.1f}" font-weight="800" fill="{text_color}">{esc(item['glyph'])}</text>
      </g>""")

    return f"""
  <g id="tech-stack">
    {glass_panel(x, y, w, h)}
    {section_title(x+20, y+26, "Tech Stack", theme)}
    {''.join(badges)}
  </g>
"""