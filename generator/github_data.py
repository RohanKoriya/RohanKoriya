"""
All network access lives here. Every other module consumes plain dicts.

Failure policy (so fake or half-empty data never reaches the live profile):
  1. Try the live GitHub API (REST + GraphQL).
  2. If that fails, fall back to the last good snapshot (generated/data.json),
     and the footer will show when that data was actually fetched.
  3. If there is no snapshot either, abort without touching any output file.
Demo data is only used when explicitly requested with --demo.
"""
from __future__ import annotations
import datetime as dt
import json
import random
import time
import urllib.error
import urllib.request

from . import config

API = "https://api.github.com"
CACHE_PATH = config.GENERATED_DIR / "data.json"


class FetchError(RuntimeError):
    pass


def _request(url: str, token: str | None, body: dict | None = None, retries: int = 3):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-readme-generator"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    if data:
        headers["Content-Type"] = "application/json"
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=25) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in (401, 404, 422):  # not retryable
                break
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = exc
        time.sleep(1.5 * (attempt + 1))
    raise FetchError(f"{url}: {last}")


CAL_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date weekday } }
      }
    }
  }
}
"""


def compute_streaks(calendar: dict) -> dict:
    """Current / longest streak in days. Today having no contributions *yet*
    does not break a streak that was alive yesterday (same rule GitHub uses)."""
    days = sorted((d for w in calendar["weeks"] for d in w["contributionDays"]),
                  key=lambda d: d["date"])
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            current += 1
        elif i == 0:
            continue  # today, still in progress
        else:
            break
    active = sum(1 for d in days if d["contributionCount"] > 0)
    return {"current": current, "longest": longest, "active_days": active}


def fetch_live(username: str, token: str | None) -> dict:
    if not token:
        raise FetchError("No GITHUB_TOKEN/GH_TOKEN set: the contribution calendar needs the GraphQL API")
    profile = _request(f"{API}/users/{username}", token)

    repos: list[dict] = []
    for page in (1, 2, 3):
        chunk = _request(f"{API}/users/{username}/repos?per_page=100&type=owner&sort=pushed&page={page}", token)
        repos += chunk
        if len(chunk) < 100:
            break
    repos = [{
        "name": r["name"], "description": r.get("description") or "", "language": r.get("language") or "",
        "stars": r["stargazers_count"], "forks": r["forks_count"], "pushed_at": r["pushed_at"] or r["updated_at"],
        "url": r["html_url"], "fork": r["fork"], "archived": r["archived"], "homepage": r.get("homepage") or "",
    } for r in repos]

    # language share by bytes of code (not by repo count), original repos only
    langs: dict[str, int] = {}
    for r in [r for r in repos if not r["fork"]][:40]:
        try:
            for lang, n in _request(f"{API}/repos/{username}/{r['name']}/languages", token).items():
                langs[lang] = langs.get(lang, 0) + n
        except FetchError:
            continue  # one repo failing must not sink the whole run

    gql = _request(f"{API}/graphql", token, {"query": CAL_QUERY, "variables": {"login": username}})
    user = (gql.get("data") or {}).get("user")
    if not user:
        raise FetchError(f"GraphQL returned no user: {gql.get('errors')}")
    cc = user["contributionsCollection"]
    calendar = cc["contributionCalendar"]

    return {
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "demo": False,
        "username": username,
        "profile": {k: profile.get(k) for k in ("name", "followers", "following", "public_repos", "avatar_url")},
        "repos": repos,
        "languages": sorted(langs.items(), key=lambda kv: kv[1], reverse=True),
        "calendar": calendar,
        "totals": {
            "commits": cc["totalCommitContributions"],
            "pull_requests": cc["totalPullRequestContributions"],
            "issues": cc["totalIssueContributions"],
            "reviews": cc["totalPullRequestReviewContributions"],
        },
        "streaks": compute_streaks(calendar),
    }


def demo_data(username: str) -> dict:
    """Deterministic SAMPLE data for layout previews. Flagged demo=True."""
    rng = random.Random(7)
    today = dt.date.today()
    start = today - dt.timedelta(days=today.weekday() + 1 + 52 * 7)  # a Sunday
    weeks, total, d = [], 0, start
    for _ in range(53):
        days = []
        for wd in range(7):
            n = 0 if d > today else max(0, int(rng.gauss(2.2, 3)))
            total += n
            days.append({"contributionCount": n, "date": d.isoformat(), "weekday": wd})
            d += dt.timedelta(days=1)
        weeks.append({"contributionDays": days})
    cal = {"totalContributions": total, "weeks": weeks}
    repos = [
        {"name": "sample-project-one", "description": "A short sample description for layout preview.",
         "language": "TypeScript", "stars": 12, "forks": 3, "pushed_at": "2026-06-14T10:00:00Z",
         "url": f"https://github.com/{username}/sample-project-one", "fork": False, "archived": False, "homepage": ""},
        {"name": "sample-project-two", "description": "", "language": "Python", "stars": 4, "forks": 0,
         "pushed_at": "2026-05-02T10:00:00Z", "url": f"https://github.com/{username}/sample-project-two",
         "fork": False, "archived": False, "homepage": ""},
        {"name": "sample-project-three", "description": "Another sample used only for previews.",
         "language": "JavaScript", "stars": 1, "forks": 0, "pushed_at": "2026-03-21T10:00:00Z",
         "url": f"https://github.com/{username}/sample-project-three", "fork": False, "archived": False, "homepage": ""},
    ]
    return {
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "demo": True,
        "username": username, "profile": {"name": "Sample", "followers": 12, "following": 8, "public_repos": 11,
                                          "avatar_url": ""},
        "repos": repos,
        "languages": [("JavaScript", 520000), ("TypeScript", 280000), ("Python", 120000), ("CSS", 80000)],
        "calendar": cal,
        "totals": {"commits": 736, "pull_requests": 105, "issues": 52, "reviews": 31},
        "streaks": compute_streaks(cal),
    }


def save_cache(data: dict) -> None:
    config.GENERATED_DIR.mkdir(exist_ok=True)
    CACHE_PATH.write_text(json.dumps(data, indent=1), encoding="utf-8")


def load_cache() -> dict | None:
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def select_projects(data: dict, cfg: dict) -> list[dict]:
    pj = cfg["projects"]
    pool = [r for r in data["repos"]
            if not r["fork"] and not r["archived"]
            and r["name"].lower() != cfg["username"].lower()
            and r["name"] not in pj["exclude"]]
    pinned = [next((r for r in pool if r["name"] == n), None) for n in pj["pin"]]
    chosen = [r for r in pinned if r]
    if pj["mode"] == "auto" or len(chosen) < pj["count"]:
        rest = sorted((r for r in pool if r not in chosen),
                      key=lambda r: (r["stars"], r["pushed_at"]), reverse=True)
        chosen += rest
    out = []
    for r in chosen[: pj["count"]]:
        r = dict(r)
        r["description"] = pj["descriptions"].get(r["name"], r["description"])
        out.append(r)
    return out


def language_shares(data: dict, top: int = 6) -> list[tuple[str, float]]:
    total = sum(n for _, n in data["languages"]) or 1
    shares = [(l, n / total * 100) for l, n in data["languages"][:top]]
    other = 100 - sum(p for _, p in shares)
    if other >= 1.0:
        shares.append(("Other", other))
    return shares
