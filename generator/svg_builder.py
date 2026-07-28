"""
generator/svg_builder.py
--------------------------
Lays out and composes every component into the final profile.svg
canvas. This is the only file that knows the absolute coordinates of
each panel — components themselves just render into the box they're
given, which keeps the layout easy to rearrange.
"""

from . import config
from .theme import build_defs
from .components import (
    sidebar, terminal, stats, contribution_graph, languages, project_cards,
    visitor_counter,
)


def build_profile_svg(data: dict, theme: dict = config.THEME) -> str:
    W, H = config.CANVAS_WIDTH, config.CANVAS_HEIGHT
    PAD_TOP = 24

    defs = build_defs(theme)

    if config.SHOW_SIDEBAR:
        MAIN_X = config.SIDEBAR_WIDTH + 24
        sidebar_svg = sidebar.build(data, theme)
    else:
        MAIN_X = 24
        sidebar_svg = ""

    MAIN_W = W - MAIN_X - 24

    terminal_h = 170
    terminal_svg = terminal.build(MAIN_X, PAD_TOP, MAIN_W, terminal_h, theme)

    stats_y = PAD_TOP + terminal_h + 24
    stats_svg = stats.build(MAIN_X, stats_y, MAIN_W, data, theme)

    graph_y = stats_y + 90
    graph_h = 190
    graph_svg = contribution_graph.build(MAIN_X, graph_y, MAIN_W, graph_h, data, theme)

    lang_y = graph_y + graph_h + 20
    lang_h = 190
    lang_w = (MAIN_W - 20) * 0.42
    lang_svg = languages.build(MAIN_X, lang_y, lang_w, lang_h, data, theme)

    projects_x = MAIN_X + lang_w + 20
    projects_w = MAIN_W - lang_w - 20
    projects_svg = project_cards.build(projects_x, lang_y, projects_w, lang_h, data, theme)

    footer_y = lang_y + lang_h + 24
    footer_svg = visitor_counter.build(MAIN_X, footer_y, MAIN_W, data, theme)

    return f"""<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"
     xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     font-family="{theme['font_display']}">
{defs}
  <rect width="{W}" height="{H}" rx="22" fill="url(#bgGradient)"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="21" fill="none"
        stroke="url(#accentGradient)" stroke-width="1.5" opacity="0.55"/>

  <clipPath id="canvasClip"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <g clip-path="url(#canvasClip)">
    {sidebar_svg}
    {terminal_svg}
    {stats_svg}
    {graph_svg}
    {lang_svg}
    {projects_svg}
    {footer_svg}
  </g>
</svg>"""
