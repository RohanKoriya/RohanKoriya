"""
generator/components/visitor_counter.py
------------------------------------------
Small footer bar showing the live visitor count (fetched during
generation via CountAPI) plus a last-updated timestamp, styled as a
thin neon status strip along the bottom of the dashboard.
"""

import datetime as dt
from .. import config
from ..utils import esc, number_format


def build(x: int, y: int, w: int, data: dict, theme: dict = config.THEME) -> str:
    visitors = data.get("visitors", 0)
    updated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""
  <g id="footer">
    <line x1="{x}" y1="{y}" x2="{x+w}" y2="{y}" stroke="{theme['glass_stroke']}"/>
    <circle cx="{x+14}" cy="{y+22}" r="4" fill="{theme['success']}">
      <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="{x+26}" y="{y+26}" font-size="11" class="mono" fill="{theme['text_secondary']}">
      {esc(number_format(visitors))} profile visits
    </text>
    <text x="{x+w-14}" y="{y+26}" text-anchor="end" font-size="10.5" class="mono"
          fill="{theme['text_muted']}">Last generated: {esc(updated)}</text>
  </g>
"""
