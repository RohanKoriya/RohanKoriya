"""
generator/components/languages.py
------------------------------------
Horizontal "most used languages" bar chart (a single stacked bar plus
a ranked list with animated fill), similar to the GitHub-stats-style
widgets popular on developer READMEs.
"""

from .. import config
from ..utils import esc, glass_panel, section_title, progress_bar

LANG_COLORS = {
    "Python": "#4fd1ff", "TypeScript": "#8a6bff", "JavaScript": "#ffcf6b",
    "Dart": "#43e6a0", "Go": "#4fd1ff", "Rust": "#ff6bd6", "Java": "#ff9d6b",
    "C++": "#8a6bff", "Shell": "#43e6a0", "HTML": "#ff6bd6", "CSS": "#4fd1ff",
    "C": "#9aa0c3", "Kotlin": "#b46bff", "Swift": "#ffcf6b",
}


def _color_for(lang: str, i: int, theme: dict) -> str:
    palette = [theme["neon_blue"], theme["neon_purple"], theme["neon_pink"],
               theme["success"], theme["warning"]]
    return LANG_COLORS.get(lang, palette[i % len(palette)])


def build(x: int, y: int, w: int, h: int, data: dict, theme: dict = config.THEME) -> str:
    languages = data["languages"]

    # stacked bar
    bar_x, bar_y, bar_w, bar_h = x + 20, y + 42, w - 40, 14
    segments = []
    cursor = bar_x
    for i, (lang, pct) in enumerate(languages):
        seg_w = bar_w * pct / 100
        color = _color_for(lang, i, theme)
        segments.append(
            f'<rect x="{cursor:.1f}" y="{bar_y}" width="0" height="{bar_h}" fill="{color}">'
            f'<animate attributeName="width" to="{seg_w:.1f}" dur="1s" begin="{i*0.1:.1f}s" fill="freeze"/>'
            f'</rect>'
        )
        cursor += seg_w
    bar_group = (
        f'<clipPath id="langBarClip"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" '
        f'height="{bar_h}" rx="7"/></clipPath>'
        f'<g clip-path="url(#langBarClip)">'
        f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" fill="#1a1c33"/>'
        f'{"".join(segments)}</g>'
    )

    # legend rows, two columns
    rows = []
    col_w = (w - 40) / 2
    for i, (lang, pct) in enumerate(languages):
        col = i % 2
        row = i // 2
        lx = x + 20 + col * col_w
        ly = bar_y + bar_h + 26 + row * 24
        color = _color_for(lang, i, theme)
        rows.append(
            f'<circle cx="{lx+5}" cy="{ly-4}" r="5" fill="{color}"/>'
            f'<text x="{lx+18}" y="{ly}" font-size="12" fill="{theme["text_primary"]}">{esc(lang)}</text>'
            f'<text x="{lx+col_w-15}" y="{ly}" text-anchor="end" font-size="11" class="mono" '
            f'fill="{theme["text_muted"]}">{pct:.1f}%</text>'
        )

    return f"""
  <g id="languages">
    {glass_panel(x, y, w, h)}
    {section_title(x+20, y+26, "Most Used Languages", theme)}
    {bar_group}
    {''.join(rows)}
  </g>
"""
