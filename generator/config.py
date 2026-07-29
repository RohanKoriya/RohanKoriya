"""
generator/config.py
--------------------
Single source of truth for everything a user needs to customize.
Edit the values below (or override with environment variables of the
same name) — nothing else in the codebase needs to change.

Environment variables (used by the GitHub Action):
    GITHUB_TOKEN   -> required, used to query the GitHub GraphQL/REST API
    GH_USERNAME    -> overrides USERNAME below
"""

import os


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


# ── Identity ──────────────────────────────────────────────────────────
USERNAME = _env("GH_USERNAME", "RohanKoriya")
DISPLAY_NAME = _env("GH_DISPLAY_NAME", "Rohan Koriya")
PRONOUNS = _env("GH_PRONOUNS", "He/Him")
TITLE = _env("GH_TITLE", "Software Engineer  ·  Open Source Builder")
LOCATION = _env("GH_LOCATION", "Earth")
EMAIL = _env("GH_EMAIL", "koriyarohan123@gmail.com")
WEBSITE = _env("GH_WEBSITE", "")
LINKEDIN = _env("GH_LINKEDIN", "https://www.linkedin.com/in/rohankoriya/")
TWITTER = _env("GH_TWITTER", "")

# ── Typing animation (rotating tagline under the name) ─────────────────
TYPING_STRINGS = [
    "Building things that matter.",
    "Learning, experimenting, and sharing what I create.",
    "I enjoy solving problems more than memorizing solutions.",
    "Every project teaches me something new.",
]

# ── Featured projects (shown as glass cards) ────────────────────────────
# Leave PROJECTS empty to auto-pick the user's top starred repos instead.
PROJECTS: list[dict] = []
MAX_AUTO_PROJECTS = 3

# ── Visitor counter ──────────────────────────────────────────────────
# Uses the free CountAPI service; namespace should be unique to your repo.
COUNTER_NAMESPACE = _env("GH_COUNTER_NAMESPACE", f"{USERNAME}-profile-os")
COUNTER_KEY = "visits"

# ── Snake contribution animation ────────────────────────────────────
SNAKE_ENABLED = True
SNAKE_COLS = 53          # GitHub contribution calendar is 53 weeks wide
SNAKE_ROWS = 7

# ── Theme ────────────────────────────────────────────────────────────
# Cyberpunk / glassmorphism, blue-purple neon palette.
THEME = {
    "bg_top": "#0b0e17",
    "bg_bottom": "#141225",
    "glass_fill": "rgba(255,255,255,0.04)",
    "glass_stroke": "#2c2f55",
    "neon_blue": "#4fd1ff",
    "neon_purple": "#b46bff",
    "neon_pink": "#ff6bd6",
    "accent_gradient": ["#4fd1ff", "#8a6bff", "#ff6bd6"],
    "text_primary": "#eef1ff",
    "text_secondary": "#9aa0c3",
    "text_muted": "#5f6690",
    "success": "#43e6a0",
    "warning": "#ffcf6b",
    "font_display": "'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif",
    "font_mono": "'JetBrains Mono', 'Fira Code', ui-monospace, monospace",
}

# ── Tech stack (shown as a small icon grid) ─────────────────────────
# Each entry: display glyph/emoji, label, and brand-ish accent color.
TECH_STACK = [
    {"glyph": "JS", "label": "JavaScript", "color": "#f0db4f"},
    {"glyph": "TS", "label": "TypeScript", "color": "#3178c6"},
    {"glyph": "⚛", "label": "React", "color": "#61dafb"},
    {"glyph": "N", "label": "Node.js", "color": "#3c873a"},
    {"glyph": "🐍", "label": "Python", "color": "#3776ab"},
    {"glyph": "🐳", "label": "Docker", "color": "#2496ed"},
]

# ── Footer quote (shown in the bottom strip) ────────────────────────
FOOTER_QUOTE = "Code. Learn. Build. Repeat."

# ── Achievements (shown as their own panel) ─────────────────────────
ACHIEVEMENTS = [
    {"emoji": "📘", "label": "Learning System Design"},
    {"emoji": "🧠", "label": "Exploring ML/AI"},
    {"emoji": "🌐", "label": "Building ai projects"},
]

# ── Canvas ───────────────────────────────────────────────────────────
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 820
SIDEBAR_WIDTH = 300
SHOW_SIDEBAR = False

# ── Output paths ─────────────────────────────────────────────────────
OUTPUT_DIR = "output"
PROFILE_SVG_PATH = f"{OUTPUT_DIR}/profile.svg"
SNAKE_SVG_PATH = f"{OUTPUT_DIR}/snake.svg"
SNAKE_DARK_SVG_PATH = f"{OUTPUT_DIR}/snake-dark.svg"
