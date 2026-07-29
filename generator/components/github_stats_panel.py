"""
generator/components/github_stats_panel.py
----------------------------------------------
A compact list-style panel of GitHub activity totals: commits, pull
requests, issues, and PR reviews — pulled from the same GraphQL
contributionsCollection query used for the contribution calendar (see
data_fetcher.get_contribution_calendar).
"""

from .. import config
from ..utils import esc, glass_panel, section_title, number_format, icon


def build(x: int, y: int, w: int, h: int, data: dict, theme: dict = config.THEME) -> str:
    cal = data["calendar"]
    rows = [
        ("commit", "Total Commits", cal.get("totalCommitContributions", 0), theme["neon_blue"]),
        ("pull-request", "Pull Requests", cal.get("totalPullRequestContributions", 0), theme["neon_purple"]),
        ("issue", "Issues", cal.get("totalIssueContributions", 0), theme["neon_pink"]),
        ("check", "Reviews", cal.get("totalPullRequestReviewContributions", 0), theme["success"]),
    ]

    row_h = (h - 50) / len(rows)
    badge = 26
    icon_size = 14
    nodes = []
    for i, (icon_name, label, value, color) in enumerate(rows):
        row_top = y + 46 + i * row_h
        center_y = row_top + row_h / 2
        badge_y = center_y - badge / 2
        icon_x = x + 20 + (badge - icon_size) / 2
        icon_y = badge_y + (badge - icon_size) / 2
        label_y = center_y + 4
        value_y = center_y + 4
        nodes.append(f"""
      <rect x="{x+20}" y="{badge_y}" width="{badge}" height="{badge}" rx="8"
            fill="{color}" opacity="0.14" stroke="{color}" stroke-width="1" stroke-opacity="0.45"/>
      <g transform="translate({icon_x},{icon_y})">{icon(icon_name, icon_size, color, 1.9)}</g>
      <text x="{x+20+badge+14}" y="{label_y}" font-size="12" fill="{theme['text_secondary']}">{esc(label)}</text>
      <text x="{x+w-20}" y="{value_y}" text-anchor="end" font-size="13" font-weight="700"
            fill="{theme['text_primary']}">{number_format(value)}</text>""")

    return f"""
  <g id="github-stats-panel">
    {glass_panel(x, y, w, h)}
    {section_title(x+20, y+26, "GitHub Stats", theme)}
    {''.join(nodes)}
  </g>
"""