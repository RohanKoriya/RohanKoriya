"""
generator/main.py
--------------------
Entry point. Run with:

    python -m generator.main

Fetches live GitHub data, renders profile.svg + snake.svg/snake-dark.svg,
and writes them into OUTPUT_DIR. This is exactly what the GitHub Action
runs on a 24h schedule.
"""

from __future__ import annotations
import os
import sys
import time

from . import config
from . import data_fetcher
from .svg_builder import build_profile_svg
from .components import snake


def log(msg: str) -> None:
    print(f"[profile-os] {msg}", flush=True)


def main() -> int:
    start = time.time()
    log(f"Generating dashboard for @{config.USERNAME} ...")

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    data = data_fetcher.collect_all(config.USERNAME)
    log(f"Fetched data: {len(data['repos'])} repos, "
        f"{data['calendar'].get('totalContributions', 0)} contributions, "
        f"{data['visitors']} visitors")

    profile_svg = build_profile_svg(data)
    with open(config.PROFILE_SVG_PATH, "w", encoding="utf-8") as f:
        f.write(profile_svg)
    log(f"Wrote {config.PROFILE_SVG_PATH}")

    if config.SNAKE_ENABLED:
        with open(config.SNAKE_SVG_PATH, "w", encoding="utf-8") as f:
            f.write(snake.render(data, light=False))
        with open(config.SNAKE_DARK_SVG_PATH, "w", encoding="utf-8") as f:
            f.write(snake.render(data, light=True))
        log(f"Wrote {config.SNAKE_SVG_PATH} and {config.SNAKE_DARK_SVG_PATH}")

    log(f"Done in {time.time() - start:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
