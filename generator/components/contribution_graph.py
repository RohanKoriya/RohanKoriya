"""
generator/components/contribution_graph.py
--------------------------------------------
Renders the classic GitHub-style contribution heatmap (weeks x days)
inside a glass panel, using the real calendar data pulled from the
GraphQL API, recolored to fit the neon theme with a glow on the
highest-intensity cells.
"""

from .. import config
from ..utils import glass_panel, section_title


def _intensity_color(count: int, theme: dict) -> str:
    if count == 0:
        return "#1a1c33"
    if count <= 2:
        return "#274a7a"
    if count <= 5:
        return theme["neon_blue"]
    if count <= 9:
        return theme["neon_purple"]
    return theme["neon_pink"]


def build(x: int, y: int, w: int, h: int, data: dict, theme: dict = config.THEME) -> str:
    weeks = data["calendar"].get("weeks", [])
    cell = 10
    gap = 3
    grid_w = len(weeks) * (cell + gap)
    offset_x = x + 20 + max(0, (w - 40 - grid_w) // 2)
    offset_y = y + 46

    cells = []
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week.get("contributionDays", [])):
            count = day.get("contributionCount", 0)
            cx = offset_x + wi * (cell + gap)
            cy = offset_y + di * (cell + gap)
            color = _intensity_color(count, theme)
            glow = ' filter="url(#softGlow)"' if count > 9 else ""
            delay = (wi * 7 + di) * 0.003
            cells.append(
                f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" rx="2.5" '
                f'fill="{color}"{glow} opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
                f'dur="0.4s" fill="freeze"/></rect>'
            )

    total = data["calendar"].get("totalContributions", 0)

    legend = f"""
    <g transform="translate({x+w-150},{y+18})">
      <text font-size="9" class="mono" fill="{theme['text_muted']}">LESS</text>
      <rect x="34" y="-9" width="9" height="9" rx="2" fill="#1a1c33"/>
      <rect x="46" y="-9" width="9" height="9" rx="2" fill="#274a7a"/>
      <rect x="58" y="-9" width="9" height="9" rx="2" fill="{theme['neon_blue']}"/>
      <rect x="70" y="-9" width="9" height="9" rx="2" fill="{theme['neon_purple']}"/>
      <rect x="82" y="-9" width="9" height="9" rx="2" fill="{theme['neon_pink']}"/>
      <text x="96" y="0" font-size="9" class="mono" fill="{theme['text_muted']}">MORE</text>
    </g>"""

    return f"""
  <g id="contribution-graph">
    {glass_panel(x, y, w, h, glow_id="cardShadow")}
    {section_title(x+20, y+28, f"Contribution Activity · {total} total", theme)}
    {legend}
    {''.join(cells)}
  </g>
"""
