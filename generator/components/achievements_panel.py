"""
generator/components/achievements_panel.py
----------------------------------------------
Standalone "Achievements" panel — a small grid of badge circles driven
by config.ACHIEVEMENTS. (The sidebar has its own compact achievements
row for when SHOW_SIDEBAR is on; this is the larger, labeled version
used in the main dashboard flow, matching a "featured projects +
achievements" row layout.)
"""

from .. import config
from ..utils import esc, glass_panel, section_title


def build(x: int, y: int, w: int, h: int, theme: dict = config.THEME) -> str:
    items = config.ACHIEVEMENTS
    cols = 2
    gap = 14
    cell_w = (w - 40 - (cols - 1) * gap) / cols
    cell_h = 50

    badges = []
    accents = [theme["warning"], theme["neon_blue"], theme["neon_purple"], theme["success"]]
    for i, item in enumerate(items[:6]):
        col = i % cols
        row = i // cols
        bx = x + 20 + col * (cell_w + gap)
        by = y + 42 + row * (cell_h + 10)
        accent = accents[i % len(accents)]
        badges.append(f"""
      <g transform="translate({bx},{by})">
        <rect width="{cell_w}" height="{cell_h}" rx="10" fill="url(#glassFill)"
              stroke="{theme['glass_stroke']}" stroke-width="1"/>
        <circle cx="25" cy="{cell_h/2}" r="15" fill="none" stroke="{accent}" stroke-width="1.5"/>
        <text x="25" y="{cell_h/2+5}" text-anchor="middle" font-size="14">{item['emoji']}</text>
        <foreignObject x="46" y="8" width="{cell_w-58}" height="{cell_h-16}">
          <div xmlns="http://www.w3.org/1999/xhtml" style="font-family:{theme['font_display']};
               font-size:10.5px;color:{theme['text_secondary']};line-height:1.3;
               display:flex;align-items:center;height:100%;">
            {esc(item['label'])}
          </div>
        </foreignObject>
      </g>""")

    return f"""
  <g id="achievements">
    {glass_panel(x, y, w, h)}
    {section_title(x+20, y+26, "Currently Learning", theme)}
    {''.join(badges)}
  </g>
"""
