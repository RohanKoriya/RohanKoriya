"""Design kit: palettes, typography and tiny SVG helpers shared by all sections."""
from __future__ import annotations
import datetime as dt
from xml.sax.saxutils import escape

W = 960  # every section is 960 units wide; README scales it to 100%

SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Times New Roman',serif"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

# Restrained charcoal / white / gray with ONE subtle blue accent.
PALETTES = {
    "dark": {
        "text": "#E6EDF3", "text2": "#9DA7B3", "muted": "#6E7781", "rule": "#30363D",
        "accent": "#58A6FF", "cells": ["#161B22", "#1B3550", "#25507A", "#3573B0", "#58A6FF"],
    },
    "light": {
        "text": "#24292F", "text2": "#57606A", "muted": "#8C959F", "rule": "#D0D7DE",
        "accent": "#0969DA", "cells": ["#EBEDF0", "#C4D7EE", "#8DB6E3", "#4E8FD6", "#0969DA"],
    },
}


def esc(s) -> str:
    return escape(str(s), {'"': "&quot;"})


def doc(width: float, height: float, body: str, title: str, desc: str = "") -> str:
    height = round(height)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">'
            f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc or title)}</desc>{body}</svg>\n')


def text(x, y, s, size=14, fill="#000", family=SANS, weight=400, anchor="start",
         spacing=0, style="", extra="") -> str:
    attrs = f'x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{fill}"'
    if weight != 400:
        attrs += f' font-weight="{weight}"'
    if anchor != "start":
        attrs += f' text-anchor="{anchor}"'
    if spacing:
        attrs += f' letter-spacing="{spacing}"'
    if style:
        attrs += f' font-style="{style}"'
    return f"<text {attrs} {extra}>{esc(s)}</text>"


def rule(x1, y, x2, pal, opacity=1) -> str:
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{pal["rule"]}" stroke-width="1" opacity="{opacity}"/>'


def header(pal, number: str, title: str, meta: str = "") -> str:
    """Small-caps mono section label + hairline: the consistent editorial device."""
    out = text(0, 20, f"{number} / {title.upper()}", 11, pal["muted"], MONO, spacing=1.6)
    if meta:
        out += text(W, 20, meta, 11, pal["muted"], MONO, anchor="end", spacing=0.4)
    return out + rule(0, 32, W, pal)


def est_width(s: str, size: float, mono: bool = False) -> float:
    return len(s) * size * (0.6 if mono else 0.52)


def truncate(s: str, max_px: float, size: float, mono: bool = False) -> str:
    if est_width(s, size, mono) <= max_px:
        return s
    keep = max(1, int(max_px / (size * (0.6 if mono else 0.52))) - 1)
    return s[:keep].rstrip() + "…"


def wrap(s: str, max_px: float, size: float) -> list[str]:
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if est_width(trial, size) > max_px and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    return lines + ([cur] if cur else [])


def short(n: float) -> str:
    n = int(n)
    if n >= 10_000:
        return f"{n / 1000:.0f}k"
    if n >= 1_000:
        return f"{n:,}"
    return str(n)


def month_year(iso: str) -> str:
    try:
        return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%b %Y")
    except ValueError:
        return ""
