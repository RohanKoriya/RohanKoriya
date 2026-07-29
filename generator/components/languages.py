"""
generator/components/languages.py
------------------------------------
"Most used languages" donut chart plus a ranked legend list —
computed from the user's public, non-fork repositories.
"""

from .. import config
from ..utils import esc, glass_panel, section_title

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


def _donut(cx: float, cy: float, r: float, stroke_w: float,
            languages: list[tuple[str, float]], theme: dict) -> str:
    circumference = 2 * 3.14159265 * r
    cumulative = 0.0
    arcs = []
    for i, (lang, pct) in enumerate(languages):
        color = _color_for(lang, i, theme)
        dash_len = circumference * pct / 100
        gap_len = circumference - dash_len
        offset = -cumulative
        arcs.append(
            f'<circle r="{r}" fill="none" stroke="{color}" stroke-width="{stroke_w}" '
            f'stroke-dasharray="{dash_len:.2f} {gap_len:.2f}" stroke-dashoffset="{offset:.2f}" '
            f'transform="rotate(-90)" stroke-linecap="butt">'
            f'<animate attributeName="stroke-dasharray" '
            f'from="0 {circumference:.2f}" to="{dash_len:.2f} {gap_len:.2f}" '
            f'dur="1s" begin="{i*0.12:.2f}s" fill="freeze"/>'
            f'</circle>'
        )
        cumulative += dash_len

    return f"""
    <g transform="translate({cx},{cy})">
      <circle r="{r}" fill="none" stroke="#1a1c33" stroke-width="{stroke_w}"/>
      {''.join(arcs)}
    </g>"""


def build(x: int, y: int, w: int, h: int, data: dict, theme: dict = config.THEME) -> str:
        languages = data.get("languages", [])

        # graceful fallback
        if not languages:
                return f"""
    <g id="languages">
        {glass_panel(x, y, w, h)}
        {section_title(x+20, y+26, "Most Used Languages", theme)}
        <text x="{x + w/2}" y="{y + h/2}" text-anchor="middle" fill="{theme['text_muted']}" class="mono">No language data</text>
    </g>
"""

        # slightly smaller donut and nudged right/down to avoid overlapping the title
        donut_r = min(46, h / 2 - 20)
        donut_cx = x + 28 + donut_r
        donut_cy = y + h / 2 + 8
        # only show top 8 languages in legend/donut for clarity
        slice_langs = languages[:8]
        donut = _donut(donut_cx, donut_cy, donut_r, donut_r * 0.38, slice_langs, theme)

        # legend to the right, vertically centered relative to donut
        legend_x = donut_cx + donut_r + 18
        legend_w = x + w - 20 - legend_x
        rows = []
        row_h = 26
        total_rows = len(slice_langs)
        start_y = int(donut_cy - (total_rows - 1) * row_h / 2)
        sw = 10
        for i, (lang, pct) in enumerate(slice_langs):
                ly = start_y + i * row_h
                color = _color_for(lang, i, theme)
                rows.append(
                        f'<rect x="{legend_x}" y="{ly - sw/2}" width="{sw}" height="{sw}" rx="2" fill="{color}"/>'
                        f'<text x="{legend_x + sw + 12}" y="{ly + 4}" font-size="13" fill="{theme["text_primary"]}" font-weight="700">{esc(lang)}</text>'
                        f'<text x="{legend_x + legend_w}" y="{ly + 4}" text-anchor="end" font-size="12" class="mono" '
                        f'fill="{theme["text_muted"]}">{pct:.1f}%</text>'
                )

        return f"""
    <g id="languages">
        {glass_panel(x, y, w, h)}
        {section_title(x+20, y+26, "Most Used Languages", theme)}
        {donut}
        {''.join(rows)}
    </g>
"""
