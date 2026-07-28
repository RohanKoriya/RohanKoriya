"""
generator/components/terminal.py
----------------------------------
A macOS-style terminal window with a SMIL-animated typing effect that
cycles through config.TYPING_STRINGS. Pure SVG/SMIL — no JS required,
so it animates correctly when embedded as a static <img> in a README.
"""

from .. import config
from ..utils import esc

def _typing_animation(x: int, y: int, strings: list[str], theme: dict) -> str:
    """Builds one <text> per string, faded in/out sequentially via SMIL.

    All strings share a single looping timeline (`dur=total`) instead of
    each having its own independent repeatCount="indefinite" loop. If
    every string looped on its own, their cycles fall back into phase
    alignment after the first full rotation (since each begin offset is
    an exact multiple of the same per-string duration), and every string
    ends up rendering on top of the others — a garbled, overlapping mess.
    A shared timeline keeps them permanently offset instead.
    """
    if not strings:
        return ""
    n = len(strings)
    per_string = 3.2
    fade = 0.35  # seconds spent fading in/out at each edge
    total = per_string * n
    nodes = []
    for i, s in enumerate(strings):
        seg_start = i * per_string
        seg_end = seg_start + per_string
        fade_in_end = seg_start + fade
        fade_out_start = seg_end - fade

        points = [(0.0, 0.0)]
        if seg_start > 0:
            points.append((seg_start, 0.0))
        points.append((fade_in_end, 1.0))
        points.append((fade_out_start, 1.0))
        points.append((min(seg_end, total), 0.0))
        if seg_end < total:
            points.append((total, 0.0))

        cleaned = [points[0]]
        for t, v in points[1:]:
            if t > cleaned[-1][0]:
                cleaned.append((t, v))
        if cleaned[-1][0] < total:
            cleaned.append((total, cleaned[-1][1]))

        key_times = ";".join(f"{t/total:.5f}" for t, _ in cleaned)
        values = ";".join(f"{v:g}" for _, v in cleaned)

        nodes.append(f"""
      <text x="{x}" y="{y}" font-family="{theme['font_mono']}" font-size="14"
            fill="{theme['success']}" opacity="0">
        <tspan>{esc(s)}</tspan>
        <tspan fill="{theme['neon_purple']}">▍
          <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
        </tspan>
        <animate attributeName="opacity" values="{values}" keyTimes="{key_times}"
                 dur="{total:.2f}s" repeatCount="indefinite"/>
      </text>""")
    return "\n".join(nodes)


def build(x: int, y: int, w: int, h: int, theme: dict = config.THEME) -> str:
    header_h = 34
    body_y = y + header_h

    prompt = f"{config.USERNAME}@profile-os"

    lines = [
        (f"$ whoami", theme["text_secondary"]),
        (f"{config.USERNAME}", theme["neon_blue"]),
        (f"$ status --check", theme["text_secondary"]),
        ("● online · shipping code", theme["success"]),
    ]

    static_lines = []
    ly = body_y + 30
    for text, color in lines:
        static_lines.append(
            f'<text x="{x+24}" y="{ly}" font-family="{theme["font_mono"]}" '
            f'font-size="13" fill="{color}">{esc(text)}</text>'
        )
        ly += 22

    typing = _typing_animation(x + 24, ly + 6, config.TYPING_STRINGS, theme)

    return f"""
  <g id="terminal">
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="url(#glassFill)"
          stroke="{theme['glass_stroke']}" stroke-width="1.2" filter="url(#cardShadow)"/>
    <rect x="{x}" y="{y}" width="{w}" height="{header_h}" rx="16" fill="#161832"/>
    <rect x="{x}" y="{y+header_h-16}" width="{w}" height="16" fill="#161832"/>
    <circle cx="{x+20}" cy="{y+17}" r="6" fill="#ff5f57"/>
    <circle cx="{x+40}" cy="{y+17}" r="6" fill="#febc2e"/>
    <circle cx="{x+60}" cy="{y+17}" r="6" fill="#28c840"/>
    <text x="{x+w/2}" y="{y+21}" text-anchor="middle" font-family="{theme['font_mono']}"
          font-size="11" fill="{theme['text_muted']}">{esc(prompt)}</text>
    {''.join(static_lines)}
    {typing}
  </g>
"""
