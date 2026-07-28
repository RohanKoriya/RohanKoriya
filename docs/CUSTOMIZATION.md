# Customization Guide

## 1. Basic identity

Everything personal lives in [`generator/config.py`](../generator/config.py).
Edit the constants at the top — `DISPLAY_NAME`, `TITLE`, `LOCATION`,
`EMAIL`, `WEBSITE`, `LINKEDIN` — or set the matching environment
variable (`GH_DISPLAY_NAME`, `GH_TITLE`, ...) so you never have to touch
code in CI. The workflow file already forwards GitHub Actions **repo
variables** (Settings → Secrets and variables → Actions → Variables) of
the same name.

## 2. Typing animation

`TYPING_STRINGS` is a plain Python list. Add, remove, or reorder lines
— the terminal component cycles through them automatically and adjusts
timing.

## 3. Featured projects

By default the dashboard auto-selects your top starred repositories.
To pin specific projects instead, fill in `PROJECTS`:

```python
PROJECTS = [
    {"name": "profile-os", "description": "This very repo.", "language": "Python", "stars": 240},
    {"name": "neon-ui-kit", "description": "A React component kit.", "language": "TypeScript", "stars": 180},
]
```

Leave it as `[]` to keep auto-selection (`MAX_AUTO_PROJECTS` controls how
many show up).

## 4. Theme / palette

`THEME` in `config.py` is a single dict consumed by every component via
`theme.py`'s `build_defs()`. To go, say, green/cyan instead of
blue/purple/pink:

```python
THEME["accent_gradient"] = ["#43e6a0", "#4fd1ff", "#43e6a0"]
THEME["neon_blue"] = "#4fd1ff"
THEME["neon_purple"] = "#43e6a0"
```

Every gradient, glow filter, and progress bar references these values
indirectly — no color is hard-coded inside a component file.

## 5. Layout

`generator/svg_builder.py` positions every panel using plain
`x, y, w, h` arithmetic — there's no CSS grid or flexbox to fight.
To, e.g., swap the order of the language and project panels, just swap
the two function calls and the `x` values they're given.

To add a brand-new panel:

```python
# generator/components/my_panel.py
def build(x, y, w, h, data, theme):
    return f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" .../></g>'
```

```python
# generator/svg_builder.py
from .components import my_panel
...
my_panel_svg = my_panel.build(MAIN_X, some_y, MAIN_W, 120, data, theme)
# then include `{my_panel_svg}` in the returned f-string
```

## 6. Canvas size

`CANVAS_WIDTH` / `CANVAS_HEIGHT` / `SIDEBAR_WIDTH` in `config.py` control
the overall dashboard dimensions. If you add or remove panels, adjust
`CANVAS_HEIGHT` so nothing gets clipped (there's no auto-fit — it's a
deliberate tradeoff to keep the generator simple and dependency-free).

## 7. Snake animation

`SNAKE_ENABLED`, `SNAKE_COLS`, `SNAKE_ROWS` in `config.py` control the
snake. The traversal pattern, speed and colors live in
`generator/components/snake.py` if you want a different eating order
(e.g. spiral instead of boustrophedon).

## 8. Visitor counter

Uses the free [CountAPI](https://countapi.xyz) service, namespaced by
`COUNTER_NAMESPACE` in `config.py`. Swap in any other counter API by
editing `data_fetcher.get_visitor_count()` — it just needs to return an
int.
