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
    updated = dt.datetime.now(dt.timezone.utc).strftime("%d %B %Y")

    quote = ""
    if config.FOOTER_QUOTE:
        quote = (
            f'<text x="{x+w/2}" y="{y+22}" text-anchor="middle" font-size="11" '
            f'font-style="italic" fill="{theme["text_secondary"]}">'
            f'"{esc(config.FOOTER_QUOTE)}" — {esc(config.DISPLAY_NAME)}</text>'
        )

    row_y = y + (44 if config.FOOTER_QUOTE else 22)

    return f"""
  <g id="footer">
    <line x1="{x}" y1="{y}" x2="{x+w}" y2="{y}" stroke="{theme['glass_stroke']}"/>
    {quote}
    <circle cx="{x+14}" cy="{row_y}" r="4" fill="{theme['success']}">
      <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="{x+26}" y="{row_y+4}" font-size="11" class="mono" fill="{theme['text_secondary']}">
      {esc(number_format(visitors))} profile visits
    </text>
    <text x="{x+w-14}" y="{row_y+4}" text-anchor="end" font-size="10.5" class="mono"
          fill="{theme['text_muted']}">Last updated: {esc(updated)}</text>
  </g>
"""
