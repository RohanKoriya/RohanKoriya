"""
Section renderers. Each function takes a palette and returns a standalone SVG
string (960 units wide). No scripts, no external resources, no foreignObject:
only features that GitHub's image proxy renders reliably.

Animations use SMIL only, and every animation has a sensible static state:
if a viewer ignores SMIL, nothing is missing or hidden.
"""
from __future__ import annotations
import datetime as dt
import math

from . import github_data as gd
from .kit import (MONO, SANS, SERIF, W, doc, esc, header, month_year, rule, short,
                  text, truncate, wrap)

NBSP = "\u00a0"


# ── 00 · Hero (portrait + introduction as ONE image, so GitHub cannot reflow it) ──
TEXT_X = 400                                   # left edge of the text column (also used for the link indent)
TEXT_COL_PCT = round(TEXT_X / W * 100, 2)      # same position as a percentage, for the README link row


def hero(pal, rows: list[str], cfg: dict) -> str:
    cols = max(cfg["portrait_columns"], max((len(r) for r in rows), default=1))
    pw = 340                                   # portrait drawing width
    cw = pw / cols                             # character advance
    fs = cw / 0.6                              # font size for a 0.6em monospace advance
    lh = fs
    ph = lh * len(rows)
    body = ""
    for i, row in enumerate(rows):
        glyphs = [(j, c) for j, c in enumerate(row) if c != " "]
        if not glyphs:
            continue
        # every glyph gets an explicit x, so columns stay aligned even if a viewer
        # substitutes a proportional font for the monospace stack
        xs = " ".join(f"{j * cw:.2f}" for j, _ in glyphs)
        body += (f'<text x="{xs}" y="{(i + 1) * lh - lh * 0.2:.2f}" font-family="{MONO}" '
                 f'font-size="{fs:.2f}" fill="{pal["text2"]}">{esc("".join(c for _, c in glyphs))}</text>')
    # one thin scan line + soft band sweep the portrait; hidden unless SMIL runs
    body += (f'<clipPath id="clip"><rect width="{pw}" height="{ph:.1f}"/></clipPath>'
             f'<g clip-path="url(#clip)" opacity="0">'
             f'<rect x="0" y="-26" width="{pw}" height="26" fill="{pal["accent"]}" opacity="0.10">'
             f'<animate attributeName="y" values="-26;{ph:.1f};{ph:.1f}" keyTimes="0;0.6;1" dur="8s" repeatCount="indefinite"/></rect>'
             f'<rect x="0" y="0" width="{pw}" height="1.2" fill="{pal["accent"]}" opacity="0.8">'
             f'<animate attributeName="y" values="0;{ph:.1f};{ph:.1f}" keyTimes="0;0.6;1" dur="8s" repeatCount="indefinite"/></rect>'
             f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.04;0.56;0.62;1" dur="8s" repeatCount="indefinite"/>'
             f'</g>')
    cap_y = ph + 24
    body += text(0, cap_y, f"@{cfg['username']}", 11, pal["muted"], MONO, spacing=0.6)
    body += text(pw, cap_y, "ASCII PORTRAIT", 10, pal["muted"], MONO, anchor="end", spacing=1.4)

    # text column: last intro line shares a baseline with the portrait caption
    lines = wrap(cfg["intro"], W - TEXT_X - 10, 16)
    y_end = cap_y
    y_intro = y_end - 27 * (len(lines) - 1)
    y_name = y_intro - 64
    body += text(TEXT_X, y_name - 58, cfg["role"].upper(), 12, pal["accent"], MONO, weight=500, spacing=2.4)
    body += text(TEXT_X, y_name, cfg["name"], 54, pal["text"], SERIF, weight=500, spacing=-0.8)
    body += f'<rect x="{TEXT_X}" y="{y_name + 24}" width="28" height="2" fill="{pal["accent"]}"/>'
    for i, line in enumerate(lines):
        body += text(TEXT_X, y_intro + 27 * i, line, 16, pal["text2"], SANS)
    return doc(W, cap_y + 10, body, f"{cfg['name']}, {cfg['role']}",
               f"ASCII portrait of {cfg['name']}. {cfg['name']}, {cfg['role']}. {cfg['intro']}")


# ── 01 · Activity ───────────────────────────────────────────────────
def _level(count: int, mx: int) -> int:
    return 0 if count <= 0 else min(4, max(1, math.ceil(count * 4 / mx)))


def activity(pal, data: dict) -> str:
    cal, st = data["calendar"], data["streaks"]
    weeks = cal["weeks"]
    out = header(pal, "01", "Activity", "Last 12 months")
    out += text(0, 100, f"{cal['totalContributions']:,}", 54, pal["text"], SERIF, weight=500, spacing=-1)
    out += text(0, 124, "contributions in the last year", 13, pal["text2"], SANS)
    for i, (label, value) in enumerate([("Current streak", f"{st['current']} days"),
                                        ("Longest streak", f"{st['longest']} days"),
                                        ("Active days", f"{st['active_days']}")]):
        x = 567 + i * 134
        out += text(x, 92, value, 28, pal["text"], SERIF, weight=500)
        out += text(x, 114, label.upper(), 10, pal["muted"], MONO, spacing=1.2)

    n = len(weeks)
    left = 36
    step = (W - left) / n
    gap = 3.2
    cell = step - gap
    gy = 180
    mx = max((d["contributionCount"] for w in weeks for d in w["contributionDays"]), default=1) or 1

    last_label = -9
    prev_month = None
    for wi, w in enumerate(weeks):
        first = w["contributionDays"][0]["date"]
        m = int(first[5:7])
        if m != prev_month:
            if wi - last_label >= 3:
                out += text(left + wi * step, gy - 12, dt.date(2000, m, 1).strftime("%b"), 10, pal["muted"], MONO)
                last_label = wi
            prev_month = m
    for r, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out += text(0, gy + r * step + cell * 0.8, label, 10, pal["muted"], MONO)

    last_day = None
    for wi, w in enumerate(weeks):
        for di, d in enumerate(w["contributionDays"]):
            x, y = left + wi * step, gy + di * step
            out += (f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2.5" '
                    f'fill="{pal["cells"][_level(d["contributionCount"], mx)]}"/>')
            last_day = (x, y)
    if last_day:  # today: a quiet ring that breathes (static ring if SMIL is ignored)
        x, y = last_day
        out += (f'<rect x="{x - 2:.1f}" y="{y - 2:.1f}" width="{cell + 4:.1f}" height="{cell + 4:.1f}" rx="4" '
                f'fill="none" stroke="{pal["accent"]}" stroke-width="1.4">'
                f'<animate attributeName="opacity" values="1;0.35;1" dur="2.8s" repeatCount="indefinite"/></rect>')

    ly = gy + 7 * step + 22
    out += text(W, ly + 9, "More", 10, pal["muted"], MONO, anchor="end")
    for i in range(5):
        out += f'<rect x="{W - 44 - (5 - i) * 15:.0f}" y="{ly}" width="11" height="11" rx="2.5" fill="{pal["cells"][i]}"/>'
    out += text(W - 44 - 5 * 15 - 6, ly + 9, "Less", 10, pal["muted"], MONO, anchor="end")
    out += text(0, ly + 9, f"Today is outlined. Data: GitHub contribution calendar.", 10, pal["muted"], MONO)
    return doc(W, ly + 24, out, "Contribution activity",
               f"{cal['totalContributions']:,} contributions in the last year; current streak {st['current']} days, "
               f"longest streak {st['longest']} days.")


# ── 02 · Overview (numbers + languages) ─────────────────────────────
def overview(pal, data: dict) -> str:
    t, p = data["totals"], data["profile"]
    stars = sum(r["stars"] for r in data["repos"] if not r["fork"])
    langs = gd.language_shares(data)
    out = header(pal, "02", "Overview", "Statistics & languages")

    def block(y_caption, caption, items):
        o = text(0, y_caption, caption, 10, pal["muted"], MONO, spacing=1.4)
        for i, (label, val) in enumerate(items):
            x = i * 118
            o += text(x, y_caption + 44, short(val), 38, pal["text"], SERIF, weight=500, spacing=-0.5)
            o += text(x, y_caption + 66, label, 12.5, pal["text2"], SANS)
        return o

    out += block(72, "LAST 12 MONTHS", [("Commits", t["commits"]), ("Pull requests", t["pull_requests"]),
                                        ("Reviews", t["reviews"]), ("Issues", t["issues"])])
    out += block(184, "ALL TIME", [("Repositories", p["public_repos"]), ("Stars earned", stars),
                                   ("Followers", p["followers"]), ("Following", p["following"])])

    x0, bw = 520, W - 520
    out += text(x0, 72, "LANGUAGES · BY CODE SIZE", 10, pal["muted"], MONO, spacing=1.4)
    for i, (name, pct) in enumerate(langs):
        y = 112 + i * 36
        out += text(x0, y, name, 14, pal["text"], SANS)
        out += text(W, y, f"{pct:.1f}%", 12, pal["text2"], MONO, anchor="end")
        fw = max(2.0, bw * pct / 100)
        out += f'<rect x="{x0}" y="{y + 10}" width="{bw}" height="3" rx="1.5" fill="{pal["rule"]}"/>'
        out += (f'<rect x="{x0}" y="{y + 10}" width="{fw:.1f}" height="3" rx="1.5" fill="{pal["accent"]}" '
                f'opacity="{1 if name != "Other" else 0.45}">'
                f'<animate attributeName="width" from="0" to="{fw:.1f}" dur="1.1s" begin="0s" fill="freeze" '
                f'calcMode="spline" keyTimes="0;1" keySplines="0.2 0.7 0.2 1"/></rect>')
    h = max(290, 112 + len(langs) * 36 + 16)
    summary = ", ".join(f"{n} {p:.0f}%" for n, p in langs[:4])
    return doc(W, h, out, "Statistics and languages",
               f"{t['commits']} commits, {t['pull_requests']} pull requests in the last year; "
               f"{p['public_repos']} repositories, {stars} stars, {p['followers']} followers. Languages: {summary}.")


# ── 03 · Stack & learning ───────────────────────────────────────────
def stack(pal, cfg: dict) -> str:
    out = header(pal, "03", "Stack & learning")
    for i, g in enumerate(cfg["stack"]):
        y = 82 + i * 40
        out += text(0, y, g["label"].upper(), 10.5, pal["muted"], MONO, spacing=1.4)
        spans = ""
        for j, item in enumerate(g["items"]):
            spans += (f'<tspan fill="{pal["muted"]}"> / </tspan>' if j else "") + f'<tspan>{esc(item)}</tspan>'
        out += (f'<text x="128" y="{y}" font-family="{SANS}" font-size="16" fill="{pal["text"]}">{spans}</text>')
    x0 = 640
    out += text(x0, 58, cfg["learning"]["title"].upper(), 10.5, pal["muted"], MONO, spacing=1.4)
    for i, item in enumerate(cfg["learning"]["items"]):
        y = 82 + i * 40
        out += text(x0, y, f"{i + 1:02d}", 11, pal["accent"], MONO)
        out += text(x0 + 34, y, item, 16, pal["text"], SANS)
    n = max(len(cfg["stack"]), len(cfg["learning"]["items"]))
    stack_desc = "; ".join(f"{g['label']}: {', '.join(g['items'])}" for g in cfg["stack"])
    return doc(W, 82 + n * 40 + 8, out, "Tech stack and currently learning",
               f"{stack_desc}. {cfg['learning']['title']}: {', '.join(cfg['learning']['items'])}.")


# ── 04 · Projects ───────────────────────────────────────────────────
def projects_head(pal) -> str:
    return doc(W, 44, header(pal, "04", "Projects", "Selected repositories"), "Projects")


def project_row(pal, i: int, repo: dict) -> str:
    desc = (repo["description"] or "").strip()
    out = text(0, 40, f"{i:02d}", 12, pal["muted"], MONO)
    out += text(44, 40 if desc else 46, truncate(repo["name"], 430, 19), 19, pal["text"], SANS, weight=600)
    if desc:
        out += text(44, 64, truncate(desc, 600, 14), 14, pal["text2"], SANS)
    bits = [b for b in (repo["language"], f"★ {repo['stars']}",
                        f"{repo['forks']} forks" if repo["forks"] else "", month_year(repo["pushed_at"])) if b]
    out += text(W - 34, 40, "  ·  ".join(bits), 12, pal["text2"], MONO, anchor="end")
    out += text(W, 42, "↗", 20, pal["accent"], SANS, anchor="end")
    out += rule(0, 83, W, pal)
    return doc(W, 84, out, repo["name"],
               f"{repo['name']}: {desc or 'no description'}. {', '.join(bits)}.")


# ── 05 · Snake ──────────────────────────────────────────────────────
def snake(pal, data: dict) -> str:
    weeks = data["calendar"]["weeks"]
    n = len(weeks)
    step = (W - 4) / n
    cell = step - 3.2
    top = 60
    mx = max((d["contributionCount"] for w in weeks for d in w["contributionDays"]), default=1) or 1
    path = [(c, r) for c in range(n) for r in (range(7) if c % 2 == 0 else range(6, -1, -1))]
    index = {p: i for i, p in enumerate(path)}
    dur_step = 0.07
    total = len(path) * dur_step
    empty = pal["cells"][0]

    out = header(pal, "05", "Snake", "Eats the contribution graph")
    for c, w in enumerate(weeks):
        for r, d in enumerate(w["contributionDays"]):
            lvl = _level(d["contributionCount"], mx)
            color = pal["cells"][lvl]
            x, y = c * step, top + r * step
            node = f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2.5" fill="{color}"'
            if lvl:
                t = index[(c, r)] / len(path)
                node += (f'><animate attributeName="fill" calcMode="discrete" values="{color};{empty}" '
                         f'keyTimes="0;{t:.4f}" dur="{total:.1f}s" repeatCount="indefinite"/></rect>')
            else:
                node += "/>"
            out += node

    body_len = 6
    for s in range(body_len - 1, -1, -1):          # tail first so the head draws on top
        xs, ys = [], []
        for i in range(len(path)):
            c, r = path[max(0, i - s)]
            xs.append(f"{c * step:.1f}")
            ys.append(f"{top + r * step:.1f}")
        op = 1 if s == 0 else max(0.25, 0.85 - s * 0.13)
        out += (f'<rect x="{xs[0]}" y="{ys[0]}" width="{cell:.1f}" height="{cell:.1f}" rx="4" fill="{pal["accent"]}" opacity="{op:.2f}">'
                f'<animate attributeName="x" values="{";".join(xs)}" dur="{total:.1f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="y" values="{";".join(ys)}" dur="{total:.1f}s" repeatCount="indefinite"/></rect>')
    return doc(W, top + 7 * step + 8, out, "Contribution snake",
               "A snake animation that eats the contribution graph.")


# ── Footer ──────────────────────────────────────────────────────────
def footer(pal, cfg: dict, data: dict) -> str:
    stamp = data["fetched_at"][:16].replace("T", " ") + " UTC"
    out = rule(0, 8, W, pal)
    y = 46
    if cfg["quote"]:
        out += text(W / 2, y, cfg["quote"], 16, pal["text2"], SERIF, anchor="middle", style="italic")
        y += 26
    note = "Sample data (preview)" if data.get("demo") else f"Statistics refreshed {stamp}"
    out += text(W / 2, y, note, 10.5, pal["muted"], MONO, anchor="middle", spacing=0.6)
    return doc(W, y + 14, out, "Footer", cfg["quote"] or "Footer")
