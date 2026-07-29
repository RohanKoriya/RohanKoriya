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
    return "#161b22"

   if count <= 2:
       return "#0e4429"
   
   if count <= 5:
       return "#006d32"
   
   if count <= 9:
       return "#26a641"
   
   return "#39d353"


def build(x: int, y: int, w: int, h: int, data: dict, theme: dict = config.THEME) -> str:
    weeks = data["calendar"].get("weeks", [])
    n_weeks = len(weeks) or 1
    gap = 3

    # Size cells to fill the panel nicely instead of a fixed small size
    # that leaves the heatmap looking sparse/floating in empty space.
    avail_w = w - 40
    avail_h = h - 78  # leave room for the title/legend row and bottom padding
    cell_from_w = (avail_w - (n_weeks - 1) * gap) / n_weeks
    cell_from_h = (avail_h - 6 * gap) / 7
    cell = max(6, min(cell_from_w, cell_from_h, 16))

    grid_w = n_weeks * (cell + gap) - gap
    offset_x = x + 20 + max(0, (avail_w - grid_w) / 2)
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
                f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="{cell*0.25:.1f}" '
                f'fill="{color}"{glow} opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
                f'dur="0.4s" fill="freeze"/></rect>'
            )

    total = data["calendar"].get("totalContributions", 0)

    # use the same intensity colors as the heatmap so legend matches the grid
    legend_colors = [
        _intensity_color(0, theme),
        _intensity_color(1, theme),
        _intensity_color(3, theme),
        _intensity_color(7, theme),
        _intensity_color(10, theme),
    ]

    legend = f"""
    <g transform="translate({x+w-150},{y+18})">
      <text font-size="9" class="mono" fill="{theme['text_muted']}">LESS</text>
      <rect x="34" y="-9" width="9" height="9" rx="2" fill="{legend_colors[0]}"/>
      <rect x="46" y="-9" width="9" height="9" rx="2" fill="{legend_colors[1]}"/>
      <rect x="58" y="-9" width="9" height="9" rx="2" fill="{legend_colors[2]}"/>
      <rect x="70" y="-9" width="9" height="9" rx="2" fill="{legend_colors[3]}"/>
      <rect x="82" y="-9" width="9" height="9" rx="2" fill="{legend_colors[4]}"/>
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
