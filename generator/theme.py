"""
generator/theme.py
-------------------
Builds the shared <defs> block: background gradients, glassmorphism
fill, neon glow filters and reusable stroke gradients. Every component
references these ids instead of hard-coding colors, so retheming the
whole dashboard is a one-file change (see config.py -> THEME).
"""

from . import config


def build_defs(theme: dict = config.THEME) -> str:
    blue, purple, pink = theme["accent_gradient"]
    return f"""
  <defs>
    <linearGradient id="bgGradient" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{theme['bg_top']}"/>
      <stop offset="100%" stop-color="{theme['bg_bottom']}"/>
    </linearGradient>

    <linearGradient id="accentGradient" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{blue}"/>
      <stop offset="50%" stop-color="{purple}"/>
      <stop offset="100%" stop-color="{pink}"/>
    </linearGradient>

    <linearGradient id="accentGradientV" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{blue}"/>
      <stop offset="100%" stop-color="{pink}"/>
    </linearGradient>

    <radialGradient id="avatarGlow" cx="50%" cy="50%" r="60%">
      <stop offset="60%" stop-color="{purple}" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="{purple}" stop-opacity="0"/>
    </radialGradient>

    <linearGradient id="glassFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.06"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.015"/>
    </linearGradient>

    <linearGradient id="sidebarFill" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#12142a" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#0c0e1c" stop-opacity="0.98"/>
    </linearGradient>

    <filter id="softGlow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="strongGlow" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="10" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="cardShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#000000" flood-opacity="0.35"/>
    </filter>

    <clipPath id="avatarClip">
      <circle cx="150" cy="118" r="70"/>
    </clipPath>

    <style>
      text {{ font-family: {theme['font_display']}; }}
      .mono {{ font-family: {theme['font_mono']}; }}
    </style>
  </defs>
"""
