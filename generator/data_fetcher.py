"""
generator/data_fetcher.py
--------------------------
All network access lives here. Everything else in the project consumes
plain Python dicts/lists so it can be unit-tested without hitting the
network. If GITHUB_TOKEN is missing (e.g. a local dry run) we fall back
to realistic sample data so the SVG can still be previewed.
"""

from __future__ import annotations
import os
import json
import datetime as dt
import urllib.request
import urllib.error

from . import config

GITHUB_API = "https://api.github.com"
GITHUB_GRAPHQL = "https://api.github.com/graphql"


def _token() -> str | None:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def _rest(path: str) -> dict | list | None:
    token = _token()
    req = urllib.request.Request(f"{GITHUB_API}{path}")
    req.add_header("Accept", "application/vnd.github+json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError):
        return None


def _graphql(query: str, variables: dict) -> dict | None:
    token = _token()
    if not token:
        return None
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(GITHUB_GRAPHQL, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError):
        return None


# ── Public data-shaping functions ──────────────────────────────────────

def get_profile(username: str) -> dict:
    data = _rest(f"/users/{username}")
    if not data:
        return {
            "login": username,
            "public_repos": 42,
            "followers": 128,
            "following": 37,
            "created_at": "2019-01-01T00:00:00Z",
        }
    return data


def get_repos(username: str) -> list[dict]:
    data = _rest(f"/users/{username}/repos?per_page=100&sort=updated")
    if not data:
        return [
            {"name": "profile-os", "stargazers_count": 240, "language": "Python", "fork": False},
            {"name": "neon-ui-kit", "stargazers_count": 180, "language": "TypeScript", "fork": False},
            {"name": "snake-svg", "stargazers_count": 95, "language": "Python", "fork": False},
        ]
    return [r for r in data if isinstance(r, dict)]


def get_language_breakdown(repos: list[dict]) -> list[tuple[str, float]]:
    counts: dict[str, int] = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            counts[lang] = counts.get(lang, 0) + 1
    if not counts:
        counts = {"Python": 6, "TypeScript": 4, "Dart": 3, "Shell": 1}
    total = sum(counts.values())
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return [(lang, round(c / total * 100, 1)) for lang, c in ranked]


def get_contribution_calendar(username: str) -> dict:
    """Returns weeks of daily contribution counts, plus commit/PR/issue/
    review totals, via a single GraphQL query. Falls back to a
    deterministic pseudo-random calendar when no token is available, so
    the generator still produces a valid SVG locally.
    """
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays { contributionCount date weekday }
            }
          }
        }
      }
    }
    """
    result = _graphql(query, {"login": username})
    if result and "data" in result and result["data"].get("user"):
        cc = result["data"]["user"]["contributionsCollection"]
        cal = cc["contributionCalendar"]
        cal["totalCommitContributions"] = cc.get("totalCommitContributions", 0)
        cal["totalIssueContributions"] = cc.get("totalIssueContributions", 0)
        cal["totalPullRequestContributions"] = cc.get("totalPullRequestContributions", 0)
        cal["totalPullRequestReviewContributions"] = cc.get("totalPullRequestReviewContributions", 0)
        return cal

    # ── deterministic fallback (no API token) ──
    import random
    random.seed(username)
    weeks = []
    today = dt.date.today()
    start = today - dt.timedelta(weeks=config.SNAKE_COLS - 1)
    start -= dt.timedelta(days=start.weekday() + 1 if start.weekday() != 6 else 0)
    total = 0
    day = start
    for _w in range(config.SNAKE_COLS):
        days = []
        for wd in range(7):
            count = max(0, int(random.gauss(3, 3)))
            total += count
            days.append({"contributionCount": count, "date": day.isoformat(), "weekday": wd})
            day += dt.timedelta(days=1)
        weeks.append({"contributionDays": days})
    return {
        "totalContributions": total,
        "weeks": weeks,
        "totalCommitContributions": int(total * 0.7),
        "totalIssueContributions": int(total * 0.05),
        "totalPullRequestContributions": int(total * 0.1),
        "totalPullRequestReviewContributions": int(total * 0.03),
    }


def compute_streaks(calendar: dict) -> dict:
    """Derives longest-streak / current-streak (in days) from the
    contribution calendar. Pure function of already-fetched data, no
    extra network calls."""
    days = []
    for week in calendar.get("weeks", []):
        days.extend(week.get("contributionDays", []))
    days.sort(key=lambda d: d["date"])

    longest = current = 0
    running = 0
    for d in days:
        if d.get("contributionCount", 0) > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    # current streak: walk backwards from the most recent day
    for d in reversed(days):
        if d.get("contributionCount", 0) > 0:
            current += 1
        else:
            break

    return {"longest": longest, "current": current}


def get_visitor_count(namespace: str, key: str) -> int:
    """Uses the free CountAPI hit-counter service. Falls back to a
    time-based pseudo counter if the service is unreachable."""
    url = f"https://api.countapi.xyz/hit/{namespace}/{key}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return int(data.get("value", 0))
    except Exception:
        # Deterministic, monotonic-looking fallback based on the date.
        epoch = dt.date(2024, 1, 1)
        return (dt.date.today() - epoch).days + 1000


def collect_all(username: str) -> dict:
    """Single entry point the rest of the app calls."""
    profile = get_profile(username)
    repos = [r for r in get_repos(username) if not r.get("fork")]
    languages = get_language_breakdown(repos)
    calendar = get_contribution_calendar(username)
    streaks = compute_streaks(calendar)
    top_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)
    visitors = get_visitor_count(config.COUNTER_NAMESPACE, config.COUNTER_KEY)

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)

    return {
        "profile": profile,
        "repos": repos,
        "top_repos": top_repos[: config.MAX_AUTO_PROJECTS],
        "languages": languages,
        "calendar": calendar,
        "streaks": streaks,
        "visitors": visitors,
        "total_stars": total_stars,
    }
