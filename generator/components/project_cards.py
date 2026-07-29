"""
generator/components/project_cards.py
----------------------------------------
Row of glassmorphism "featured project" cards, either from
config.PROJECTS (manual curation) or auto-populated from the user's
top starred repositories.
"""

from .. import config
from ..utils import esc, glass_panel, section_title, truncate


def _card(x: int, y: int, w: int, h: int, name: str, desc: str,
           lang: str, stars: int, accent: str, theme: dict, index: int) -> str:
    available_title_w = w - 32
    max_chars = max(8, int(available_title_w / 7.6))
    title = truncate(name, max_chars)

    clip_id = f"cardClip{index}"
    return f"""
    <g transform="translate({x},{y})">
      <clipPath id="{clip_id}"><rect width="{w}" height="{h}" rx="14"/></clipPath>
      <g clip-path="url(#{clip_id})">
        <rect width="{w}" height="{h}" rx="14" fill="url(#glassFill)"
              stroke="{theme['glass_stroke']}" stroke-width="1"/>
        <rect width="{w}" height="3" rx="1.5" fill="{accent}"/>
        <text x="16" y="30" font-size="14" font-weight="700" fill="{theme['text_primary']}">{esc(title)}</text>
        <foreignObject x="14" y="40" width="{w-28}" height="46">
          <div xmlns="http://www.w3.org/1999/xhtml" style="font-family:{theme['font_display']};
               font-size:11px;color:{theme['text_secondary']};line-height:1.4;">
            {esc(truncate(desc, 70))}
          </div>
        </foreignObject>
        <circle cx="20" cy="{h-18}" r="4" fill="{accent}"/>
        <text x="30" y="{h-14}" font-size="10.5" class="mono" fill="{theme['text_muted']}">{esc(lang or 'Code')}</text>
        <text x="{w-16}" y="{h-14}" text-anchor="end" font-size="10.5" class="mono"
              fill="{theme['warning']}">★ {stars}</text>
      </g>
    </g>"""

def build(x: int, y: int, w: int, h: int, data: dict, theme: dict = config.THEME) -> str:
    projects = config.PROJECTS or [
        {
            "name": r.get("name", "repo"),
            "description": r.get("description") or "No description provided.",
            "language": r.get("language") or "—",
            "stars": r.get("stargazers_count", 0),
        }
        for r in data["top_repos"]
    ]

    gap = 16
    card_w = (w - 40 - gap * (len(projects) - 1)) / max(len(projects), 1)
    accents = [theme["neon_blue"], theme["neon_purple"], theme["neon_pink"]]

    cards = []
    for i, p in enumerate(projects[:3]):
        cx = x + 20 + i * (card_w + gap)
        cards.append(_card(cx, y + 40, card_w, h - 56, p["name"], p["description"],
                            p["language"], p.get("stars", 0), accents[i % len(accents)], theme, i))

    return f"""
  <g id="projects">
    {glass_panel(x, y, w, h)}
    {section_title(x+20, y+26, "Featured Projects", theme)}
    {''.join(cards)}
  </g>
"""
