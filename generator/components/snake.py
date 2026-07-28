"""
generator/components/snake.py
--------------------------------
Generates a standalone animated SVG of a "snake" crawling across the
real contribution calendar, boustrophedon-style (left column down,
next column up, ...), eating each contribution square as it passes.
Inspired by the popular Platane/snk project, reimplemented in pure
Python/SMIL so it fits this repo's "no external binaries" philosophy.

Produces a full <svg> document — this is written directly to
output/snake.svg / output/snake-dark.svg, and is *not* one of the
panels embedded inside profile.svg.
"""

from __future__ import annotations
from .. import config


def _build_path(cols: int, rows: int) -> list[tuple[int, int]]:
    """Boustrophedon (snake-order) traversal of the grid."""
    path = []
    for c in range(cols):
        row_range = range(rows) if c % 2 == 0 else range(rows - 1, -1, -1)
        for r in row_range:
            path.append((c, r))
    return path


def _cell_color(count: int, theme: dict) -> str:
    if count == 0:
        return "#1a1c33"
    if count <= 2:
        return "#274a7a"
    if count <= 5:
        return theme["neon_blue"]
    if count <= 9:
        return theme["neon_purple"]
    return theme["neon_pink"]


def render(data: dict, theme: dict = config.THEME, light: bool = False) -> str:
    weeks = data["calendar"].get("weeks", [])
    cols = len(weeks) or config.SNAKE_COLS
    rows = config.SNAKE_ROWS
    cell = 12
    gap = 3
    pad = 20

    width = pad * 2 + cols * (cell + gap)
    height = pad * 2 + rows * (cell + gap)

    counts = [[0] * rows for _ in range(cols)]
    for ci, week in enumerate(weeks):
        for day in week.get("contributionDays", []):
            ri = day.get("weekday", 0)
            if ci < cols and ri < rows:
                counts[ci][ri] = day.get("contributionCount", 0)

    bg = "#f6f8ff" if light else theme["bg_top"]
    grid_empty = "#e4e8fb" if light else "#1a1c33"

    path = _build_path(cols, rows)
    total_steps = len(path)
    step_dur = 0.09  # seconds per grid cell
    total_dur = total_steps * step_dur
    snake_len = 5

    # cells: static squares that "reset" to empty color the instant the
    # snake's head passes over them, then relight on the next full loop.
    cell_nodes = []
    for c in range(cols):
        for r in range(rows):
            cx = pad + c * (cell + gap)
            cy = pad + r * (cell + gap)
            color = _cell_color(counts[c][r], theme)
            step_index = path.index((c, r))
            eat_time = step_index * step_dur
            cell_nodes.append(
                f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" rx="3" fill="{color}">'
                f'<animate attributeName="fill" '
                f'values="{color};{grid_empty};{grid_empty};{color}" '
                f'keyTimes="0;{eat_time/total_dur:.4f};{min(eat_time/total_dur+0.001,1):.4f};1" '
                f'dur="{total_dur:.2f}s" repeatCount="indefinite"/>'
                f'</rect>'
            )

    # snake body segments follow the same path with a small time offset
    segment_nodes = []
    accent_colors = theme["accent_gradient"]
    for s in range(snake_len):
        offset_steps = s
        values = []
        key_times = []
        for i in range(total_steps + 1):
            idx = (i - offset_steps) % total_steps
            c, r = path[idx]
            x = pad + c * (cell + gap) + cell / 2
            y = pad + r * (cell + gap) + cell / 2
            values.append(f"{x},{y}")
            key_times.append(f"{i/total_steps:.4f}")
        color = accent_colors[s % len(accent_colors)]
        radius = 7 - s * 0.7
        path_parts = [f"M {values[0]}"] + [f"L {v}" for v in values[1:]]
        path_d = " ".join(path_parts)
        key_points = ";".join(f"{i/total_steps:.4f}" for i in range(total_steps + 1))
        key_times_str = ";".join(key_times)
        segment_nodes.append(
            f'<circle r="{max(radius,2):.1f}" fill="{color}" opacity="{1 - s*0.13:.2f}" filter="url(#snakeGlow)">'
            f'<animateMotion dur="{total_dur:.2f}s" repeatCount="indefinite" '
            f'keyPoints="{key_points}" '
            f'keyTimes="{key_times_str}" calcMode="linear" '
            f'path="{path_d}"/>'
            f'</circle>'
        )

    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="snakeGlow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="{width}" height="{height}" rx="12" fill="{bg}"/>
  {''.join(cell_nodes)}
  {''.join(segment_nodes)}
</svg>"""
