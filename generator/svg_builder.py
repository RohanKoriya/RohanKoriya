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
    visitor_counter, tech_stack, github_stats_panel, achievements_panel,
)


def build_profile_svg(data: dict, theme: dict = config.THEME) -> str:
    W = config.CANVAS_WIDTH
    PAD_TOP = 24

    defs = build_defs(theme)

    if config.SHOW_SIDEBAR:
        MAIN_X = config.SIDEBAR_WIDTH + 24
        sidebar_svg = sidebar.build(data, theme)
    else:
        MAIN_X = 24
        sidebar_svg = ""

    MAIN_W = W - MAIN_X - 24

    # ── terminal ──
    terminal_h = 170
    terminal_svg = terminal.build(MAIN_X, PAD_TOP, MAIN_W, terminal_h, theme)

    # ── stat tiles + score ring (now taller, with sparklines) ──
    stats_y = PAD_TOP + terminal_h + 24
    stats_h = 110
    stats_svg = stats.build(MAIN_X, stats_y, MAIN_W, stats_h, data, theme)

    # ── contribution heatmap ──
    graph_y = stats_y + stats_h + 24
    graph_h = 200
    graph_svg = contribution_graph.build(MAIN_X, graph_y, MAIN_W, graph_h, data, theme)

    # ── row 3: languages donut / tech stack / github stats — three even columns ──
    row3_y = graph_y + graph_h + 20
    row3_h = 190
    col_gap = 20
    col_w = (MAIN_W - 2 * col_gap) / 3
    lang_svg = languages.build(MAIN_X, row3_y, col_w, row3_h, data, theme)
    tech_svg = tech_stack.build(MAIN_X + col_w + col_gap, row3_y, col_w, row3_h, theme)
    ghstats_svg = github_stats_panel.build(MAIN_X + 2 * (col_w + col_gap), row3_y, col_w, row3_h, data, theme)

    # ── row 4: featured projects (wide) + achievements (narrow) ──
    row4_y = row3_y + row3_h + 20
    row4_h = 190
    projects_w = MAIN_W * 0.62
    achievements_x = MAIN_X + projects_w + col_gap
    achievements_w = MAIN_W - projects_w - col_gap
    projects_svg = project_cards.build(MAIN_X, row4_y, projects_w, row4_h, data, theme)
    achievements_svg = achievements_panel.build(achievements_x, row4_y, achievements_w, row4_h, theme)

    # ── footer ──
    footer_y = row4_y + row4_h + 24
    footer_svg = visitor_counter.build(MAIN_X, footer_y, MAIN_W, data, theme)

    H = footer_y + 56 + 24  # footer height + bottom padding

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
    {tech_svg}
    {ghstats_svg}
    {projects_svg}
    {achievements_svg}
    {footer_svg}
  </g>
</svg>"""
