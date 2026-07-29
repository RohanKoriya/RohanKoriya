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

# ── Icon library ─────────────────────────────────────────────────────
# Small, hand-built line icons (24x24 viewBox, stroke-based — same
# visual family as Octicons/Feather) instead of emoji. Emoji render
# inconsistently across OS/browsers and clash with the neon theme;
# these are self-authored so there's no external dependency or
# licensing concern, and they always render identically everywhere.
_ICON_PATHS = {
    "commit": '<circle cx="12" cy="12" r="3.2"/><line x1="2.5" y1="12" x2="8.8" y2="12"/><line x1="15.2" y1="12" x2="21.5" y2="12"/>',
    "pull-request": '<circle cx="6" cy="6" r="2.4"/><circle cx="6" cy="18" r="2.4"/><circle cx="18" cy="6" r="2.4"/><line x1="6" y1="8.4" x2="6" y2="15.6"/><path d="M6 8.4 C6 13.5, 12.5 15.6, 18 15.6 L18 8.4" fill="none"/>',
    "issue": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="2.6" fill="currentColor" stroke="none"/>',
    "check": '<path d="M4.5 12.5l5 5L19.5 7" fill="none"/>',
    "trend-up": '<polyline points="3,17 9,11 13,15 21,6" fill="none"/><polyline points="15,6 21,6 21,12" fill="none"/>',
    "star": '<path d="M12 3.5l2.6 5.6 6.1.6-4.6 4.1 1.3 6-5.4-3.1-5.4 3.1 1.3-6-4.6-4.1 6.1-.6z" fill="currentColor" stroke="none"/>',
    "repo": '<rect x="4" y="3.5" width="16" height="17" rx="2" fill="none"/><line x1="4" y1="7.5" x2="20" y2="7.5"/>',
    "users": '<circle cx="9" cy="8" r="3.2" fill="none"/><path d="M3.5 19c0-3.3 2.5-6 5.5-6s5.5 2.7 5.5 6" fill="none"/><circle cx="17" cy="9" r="2.4" fill="none"/><path d="M15.2 13.2c2.4.3 4.3 2.5 4.3 5.3" fill="none"/>',
    "trophy": '<path d="M7 4h10v4a5 5 0 0 1-10 0V4z" fill="none"/><path d="M7 5H4v1.5A3 3 0 0 0 7 9.5" fill="none"/><path d="M17 5h3v1.5a3 3 0 0 1-3 3" fill="none"/><line x1="12" y1="13" x2="12" y2="17"/><path d="M8.5 20.5h7" /><path d="M9.5 20.5V18h5v2.5"/>',
}


def icon(name: str, size: float = 16, color: str = "currentColor", stroke_w: float = 1.8) -> str:
    """Renders one of the built-in line icons at the given pixel size."""
    inner = _ICON_PATHS.get(name, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="{color}" stroke-width="{stroke_w}" '
        f'stroke-linecap="round" stroke-linejoin="round" style="color:{color}">{inner}</svg>'
    )
