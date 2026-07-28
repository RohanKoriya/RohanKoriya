"""
generator/utils.py
-------------------
Small, dependency-free helpers shared across every component builder.
Keeping these in one place means every card/panel produces visually
consistent rounded-corners, glow filters and typography.
"""

from __future__ import annotations
from xml.sax.saxutils import escape as _xml_escape


def esc(text: str) -> str:
    """Escape text for safe embedding inside SVG <text> nodes."""
    return _xml_escape(str(text))


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def truncate(text: str, max_len: int) -> str:
    text = str(text)
    return text if len(text) <= max_len else text[: max_len - 1].rstrip() + "…"


def glass_panel(x: int, y: int, w: int, h: int, rx: int = 18,
                 stroke: str = "#2c2f55", glow_id: str | None = None,
                 fill: str = "url(#glassFill)") -> str:
    """A rounded glassmorphism panel with an optional neon glow filter."""
    filter_attr = f' filter="url(#{glow_id})"' if glow_id else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.2"{filter_attr}/>'
    )

def section_title(x: int, y: int, text: str, theme: dict, size: int = 15) -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="{theme["font_display"]}" '
        f'font-size="{size}" font-weight="700" letter-spacing="0.4" '
        f'fill="{theme["text_primary"]}">{esc(text)}</text>'
    )


def small_label(x: int, y: int, text: str, theme: dict, size: int = 11,
                 color: str | None = None) -> str:
    color = color or theme["text_secondary"]
    return (
        f'<text x="{x}" y="{y}" font-family="{theme["font_mono"]}" '
        f'font-size="{size}" fill="{color}">{esc(text)}</text>'
    )


def progress_bar(x: int, y: int, w: int, h: int, pct: float,
                  gradient_id: str, track_color: str = "#1c1f38") -> str:
    pct = clamp(pct, 0, 100)
    filled_w = round(w * pct / 100)
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{track_color}"/>'
        f'<rect x="{x}" y="{y}" width="{filled_w}" height="{h}" rx="{h/2}" '
        f'fill="url(#{gradient_id})"/>'
    )


def number_format(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)
