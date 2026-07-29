"""
generator/components/stats.py
-------------------------------
Grid of KPI tiles: total contributions, stars earned, repos, followers —
each with a glyph icon and a small decorative sparkline — plus a
computed "developer score" ring, similar to a real analytics dashboard
widget.
"""

import random

from .. import config
from ..utils import esc, number_format, icon


def _sparkline(w: int, h: int, seed: str, color: str) -> str:
    """A small deterministic wavy trend line, purely decorative — seeded
    off the tile's label so it's stable across regenerations rather than
    jittering every run."""
    rng = random.Random(seed)
    points = 8
    ys = [h * 0.5]
    for _ in range(points - 1):
        ys.append(min(h - 2, max(2, ys[-1] + rng.uniform(-h * 0.35, h * 0.35))))
    step = w / (points - 1)
    coords = [(round(i * step, 1), round(h - y, 1)) for i, y in enumerate(ys)]
    path_d = "M " + " L ".join(f"{px},{py}" for px, py in coords)
    area_d = path_d + f" L {w},{h} L 0,{h} Z"
    return f"""
      <path d="{area_d}" fill="{color}" opacity="0.12"/>
      <path d="{path_d}" fill="none" stroke="{color}" stroke-width="1.6"
            stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>"""


def _tile(x: int, y: int, w: int, h: int, label: str, value: str,
           icon_name: str, accent: str, theme: dict) -> str:
    spark_h = 22
    spark_y = h - spark_h - 10
    return f"""
    <g transform="translate({x},{y})">
      <rect width="{w}" height="{h}" rx="14" fill="url(#glassFill)"
            stroke="{theme['glass_stroke']}" stroke-width="1"/>
      <rect x="0" y="0" width="4" height="{h}" rx="2" fill="{accent}"/>
      <g transform="translate(16,10)">{icon(icon_name, 15, accent, 1.9)}</g>
      <text x="18" y="46" font-size="19" font-weight="800" fill="{theme['text_primary']}">{esc(value)}</text>
      <text x="18" y="62" font-size="9.5" letter-spacing="0.5" class="mono"
            fill="{theme['text_muted']}">{esc(label.upper())}</text>
      <g transform="translate(14,{spark_y})">
        {_sparkline(w - 28, spark_h, label, accent)}
      </g>
    </g>"""


def _score_ring(cx: int, cy: int, r: int, pct: float, theme: dict) -> str:
    stroke_w = 8
    circumference = 2 * 3.14159265 * r
    offset = circumference * (1 - pct / 100)
    return f"""
    <g transform="translate({cx},{cy})">
      <circle r="{r}" fill="none" stroke="#1c1f38" stroke-width="{stroke_w}"/>
      <circle r="{r}" fill="none" stroke="url(#accentGradient)" stroke-width="{stroke_w}"
              stroke-linecap="round" stroke-dasharray="{circumference:.1f}"
              stroke-dashoffset="{offset:.1f}" transform="rotate(-90)" filter="url(#softGlow)">
        <animate attributeName="stroke-dashoffset" from="{circumference:.1f}" to="{offset:.1f}"
                 dur="1.4s" fill="freeze"/>
      </circle>
      <text text-anchor="middle" y="5" font-size="17" font-weight="800" fill="{theme['text_primary']}">{pct:.0f}</text>
      <text text-anchor="middle" y="20" font-size="8" class="mono" fill="{theme['text_muted']}">SCORE</text>
    </g>"""


def build(x: int, y: int, w: int, h: int, data: dict, theme: dict = config.THEME) -> str:
    profile = data["profile"]
    total_contrib = data["calendar"].get("totalContributions", 0)
    stars = data["total_stars"]
    repos = profile.get("public_repos", len(data["repos"]))
    followers = profile.get("followers", 0)

    score = min(100, round(
        (min(total_contrib, 2000) / 2000) * 40
        + (min(stars, 500) / 500) * 30
        + (min(followers, 500) / 500) * 30
    ))

    ring_box_w = 140
    gap = 14
    tiles_area_w = w - ring_box_w - gap
    tile_w = (tiles_area_w - 3 * gap) / 4
    tiles = "".join([
        _tile(x, y, tile_w, h, "Contributions", number_format(total_contrib), "trend-up", theme["neon_blue"], theme),
        _tile(x + (tile_w + gap), y, tile_w, h, "Stars Earned", number_format(stars), "star", theme["warning"], theme),
        _tile(x + 2 * (tile_w + gap), y, tile_w, h, "Repositories", number_format(repos), "repo", theme["neon_purple"], theme),
        _tile(x + 3 * (tile_w + gap), y, tile_w, h, "Followers", number_format(followers), "users", theme["neon_pink"], theme),
    ])

    ring_box_x = x + tiles_area_w + gap
    ring_r = min(26, h / 2 - 10)
    ring = _score_ring(ring_box_x + ring_box_w / 2, y + h / 2, ring_r, score, theme)

    return f"""
  <g id="stats">
    <clipPath id="scoreCardClip">
      <rect x="{ring_box_x}" y="{y}" width="{ring_box_w}" height="{h}" rx="14"/>
    </clipPath>
    <rect x="{ring_box_x}" y="{y}" width="{ring_box_w}" height="{h}" rx="14"
          fill="url(#glassFill)" stroke="{theme['glass_stroke']}" stroke-width="1"/>
    {tiles}
    <g clip-path="url(#scoreCardClip)">{ring}</g>
  </g>
"""