"""
generator/components/sidebar.py
--------------------------------
Left-hand identity panel: avatar with neon glow ring, name, title,
location, quick links and an "achievements" strip of badges.
"""

from .. import config
from ..utils import esc, small_label


def build(data: dict, theme: dict = config.THEME) -> str:
    profile = data["profile"]
    followers = profile.get("followers", 0)
    following = profile.get("following", 0)
    public_repos = profile.get("public_repos", 0)
    avatar_url = profile.get("avatar_url", "")

    w = config.SIDEBAR_WIDTH
    h = config.CANVAS_HEIGHT

    avatar = (
        f'<circle cx="150" cy="118" r="82" fill="url(#avatarGlow)"/>'
        f'<circle cx="150" cy="118" r="72" fill="none" stroke="url(#accentGradient)" stroke-width="2.5"/>'
    )
    if avatar_url:
        avatar += (
            f'<image href="{esc(avatar_url)}" x="80" y="48" width="140" height="140" '
            f'clip-path="url(#avatarClip)" preserveAspectRatio="xMidYMid slice"/>'
        )
    else:
        avatar += (
            f'<circle cx="150" cy="118" r="70" fill="#1c1f38"/>'
            f'<text x="150" y="130" text-anchor="middle" font-size="42" '
            f'fill="{theme["text_primary"]}">👤</text>'
        )

    stats_row = f"""
    <g transform="translate(0,300)">
      <text x="30" y="0" font-size="18" font-weight="700" fill="{theme['text_primary']}">{public_repos}</text>
      <text x="30" y="17" font-size="9" fill="{theme['text_muted']}" class="mono">REPOS</text>
      <text x="115" y="0" font-size="18" font-weight="700" fill="{theme['text_primary']}">{followers}</text>
      <text x="115" y="17" font-size="9" fill="{theme['text_muted']}" class="mono">FOLLOWERS</text>
      <text x="215" y="0" font-size="18" font-weight="700" fill="{theme['text_primary']}">{following}</text>
      <text x="215" y="17" font-size="9" fill="{theme['text_muted']}" class="mono">FOLLOWING</text>
    </g>
    """

    links = []
    y = 360
    def link_row(icon: str, label: str, y: int) -> str:
        return (
            f'<g transform="translate(30,{y})">'
            f'<text font-size="13" fill="{theme["text_secondary"]}">{icon}  '
            f'<tspan fill="{theme["text_primary"]}">{esc(label)}</tspan></text></g>'
        )

    if config.LOCATION:
        links.append(link_row("📍", config.LOCATION, y)); y += 26
    if config.EMAIL:
        links.append(link_row("✉", config.EMAIL, y)); y += 26
    if config.WEBSITE:
        links.append(link_row("🔗", config.WEBSITE.replace("https://", ""), y)); y += 26
    if config.LINKEDIN:
        links.append(link_row("in", config.LINKEDIN.replace("https://", ""), y)); y += 26

    achievements = f"""
    <g transform="translate(30,{y+30})">
      <text font-size="11" fill="{theme['text_muted']}" class="mono" letter-spacing="1">ACHIEVEMENTS</text>
      <g transform="translate(0,16)">
        <circle cx="16" cy="16" r="16" fill="#2a2245" stroke="{theme['warning']}" stroke-width="1.5"/>
        <text x="16" y="21" text-anchor="middle" font-size="15">🏆</text>
        <circle cx="56" cy="16" r="16" fill="#1c2b45" stroke="{theme['neon_blue']}" stroke-width="1.5"/>
        <text x="56" y="21" text-anchor="middle" font-size="15">⚡</text>
        <circle cx="96" cy="16" r="16" fill="#2a1c45" stroke="{theme['neon_purple']}" stroke-width="1.5"/>
        <text x="96" y="21" text-anchor="middle" font-size="15">🔥</text>
      </g>
    </g>
    """

    return f"""
  <g id="sidebar">
    <rect x="0" y="0" width="{w}" height="{h}" fill="url(#sidebarFill)"/>
    <rect x="{w-1}" y="0" width="2" height="{h}" fill="url(#accentGradientV)" opacity="0.5"/>
    {avatar}
    <text x="30" y="230" font-size="22" font-weight="800" fill="{theme['text_primary']}">{esc(config.DISPLAY_NAME)}</text>
    <text x="30" y="252" font-size="12" fill="{theme['neon_blue']}" class="mono">@{esc(config.USERNAME)} · {esc(config.PRONOUNS)}</text>
    <foreignObject x="28" y="266" width="{w-56}" height="40">
      <div xmlns="http://www.w3.org/1999/xhtml" style="font-family:{theme['font_display']};font-size:12px;color:{theme['text_secondary']};line-height:1.4;">
        {esc(config.TITLE)}
      </div>
    </foreignObject>
    <line x1="30" y1="335" x2="{w-30}" y2="335" stroke="{theme['glass_stroke']}"/>
    {stats_row}
    <line x1="30" y1="345" x2="{w-30}" y2="345" stroke="{theme['glass_stroke']}"/>
    {''.join(links)}
    {achievements}
  </g>
"""
