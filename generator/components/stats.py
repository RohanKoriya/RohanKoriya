"""
generator/components/stats.py
-------------------------------
Grid of KPI tiles: total contributions, stars earned, repos, followers,
and a computed "developer score" ring — similar to a real analytics
dashboard widget.
"""

from .. import config
from ..utils import esc, number_format


def _tile(x: int, y: int, w: int, h: int, label: str, value: str,
           accent: str, theme: dict) -> str:
    return f"""
    <g transform="translate({x},{y})">
      <rect width="{w}" height="{h}" rx="14" fill="url(#glassFill)"
            stroke="{theme['glass_stroke']}" stroke-width="1"/>
      <rect x="0" y="0" width="4" height="{h}" rx="2" fill="{accent}"/>
      <text x="18" y="26" font-size="20" font-weight="800" fill="{theme['text_primary']}">{esc(value)}</text>
      <text x="18" y="44" font-size="10" letter-spacing="0.6" class="mono"
            fill="{theme['text_muted']}">{esc(label.upper())}</text>
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


def build(x: int, y: int, w: int, data: dict, theme: dict = config.THEME) -> str:
    profile = data["profile"]
    total_contrib = data["calendar"].get("totalContributions", 0)
    stars = data["total_stars"]
    repos = profile.get("public_repos", len(data["repos"]))
    followers = profile.get("followers", 0)

    # simple composite "developer score" out of 100
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
        _tile(x, y, tile_w, 60, "Contributions", number_format(total_contrib), theme["neon_blue"], theme),
        _tile(x + (tile_w + gap), y, tile_w, 60, "Stars Earned", number_format(stars), theme["warning"], theme),
        _tile(x + 2 * (tile_w + gap), y, tile_w, 60, "Repositories", number_format(repos), theme["neon_purple"], theme),
        _tile(x + 3 * (tile_w + gap), y, tile_w, 60, "Followers", number_format(followers), theme["neon_pink"], theme),
    ])

    ring_box_x = x + tiles_area_w + gap
    ring_box_h = 60
    # radius + half the stroke width must stay comfortably inside the
    # card, otherwise the glow filter's blur (which isn't limited to the
    # circle's own bounding box) bleeds past the card's rounded border.
    ring = _score_ring(ring_box_x + ring_box_w / 2, y + ring_box_h / 2, 20, score, theme)

    return f"""
  <g id="stats">
    <clipPath id="scoreCardClip">
      <rect x="{ring_box_x}" y="{y}" width="{ring_box_w}" height="{ring_box_h}" rx="14"/>
    </clipPath>
    <rect x="{ring_box_x}" y="{y}" width="{ring_box_w}" height="{ring_box_h}" rx="14"
          fill="url(#glassFill)" stroke="{theme['glass_stroke']}" stroke-width="1"/>
    {tiles}
    <g clip-path="url(#scoreCardClip)">{ring}</g>
  </g>
"""
