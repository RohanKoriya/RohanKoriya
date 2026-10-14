"""Loads and validates profile.toml. All user content passes through here."""
from __future__ import annotations
import os
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = ROOT / "generated"
USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
REPO_RE = re.compile(r"^[A-Za-z0-9._-]{1,100}$")
SAFE_URL_RE = re.compile(r"^(https://[^\s\"'<>]+|mailto:[^\s\"'<>]+@[^\s\"'<>]+)$")


class ConfigError(ValueError):
    pass


def safe_path(rel, base: Path = ROOT) -> Path:
    """Resolve a path and refuse anything that escapes the repository."""
    base = base.resolve()
    p = (base / rel).resolve()
    if p != base and base not in p.parents:
        raise ConfigError(f"Path escapes the repository: {rel}")
    return p


def check_url(label: str, url: str) -> str:
    if not SAFE_URL_RE.match(url):
        raise ConfigError(f"Link '{label}' must start with https:// or mailto: (got {url!r})")
    return url


def load(path: Path | None = None) -> dict:
    path = path or ROOT / "profile.toml"
    with open(path, "rb") as fh:
        raw = tomllib.load(fh)

    ident = raw.get("identity", {})
    username = os.environ.get("GH_USERNAME") or ident.get("username", "")
    if not USERNAME_RE.match(username):
        raise ConfigError(f"Invalid GitHub username: {username!r}")
    for key in ("name", "role", "intro"):
        if not str(ident.get(key, "")).strip():
            raise ConfigError(f"[identity] {key} is required")

    links = {k: check_url(k, v) for k, v in raw.get("links", {}).items() if v}

    stack = raw.get("stack", [])[:6]
    projects = raw.get("projects", {})
    for name in list(projects.get("pin", [])) + list(projects.get("exclude", [])):
        if not REPO_RE.match(name):
            raise ConfigError(f"Invalid repository name in [projects]: {name!r}")
    cols = int(raw.get("portrait", {}).get("columns", 76))
    if not 40 <= cols <= 120:
        raise ConfigError("[portrait] columns must be between 40 and 120")

    learning = raw.get("learning", {})
    return {
        "username": username,
        "name": ident["name"].strip(),
        "role": ident["role"].strip(),
        "intro": ident["intro"].strip(),
        "links": links,
        "stack": [{"label": s["label"], "items": list(s["items"])} for s in stack],
        "learning": {
            "title": learning.get("title", "Currently learning"),
            "items": list(learning.get("items", []))[:5],
        },
        "projects": {
            "mode": projects.get("mode", "auto"),
            "count": max(1, min(int(projects.get("count", 3)), 6)),
            "pin": list(projects.get("pin", [])),
            "exclude": list(projects.get("exclude", [])),
            "descriptions": dict(projects.get("descriptions", {})),
        },
        "quote": raw.get("footer", {}).get("quote", ""),
        "portrait_columns": cols,
    }
