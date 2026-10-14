"""
Turns a photo/avatar into an ASCII portrait.

Source priority:  assets/portrait.(png|jpg|jpeg|webp)  ->  GitHub avatar
                  ->  cached generated/portrait.txt (last good result)
"""
from __future__ import annotations
import io
import urllib.request

from . import config

CACHE = config.GENERATED_DIR / "portrait.txt"
RAMP = " .,:;-=+*#%@"          # light -> dense ink
CELL_ASPECT = 0.6               # monospace cell width / height


def from_image(img_bytes: bytes, cols: int) -> list[str]:
    from PIL import Image, ImageFilter, ImageOps  # imported lazily: optional at runtime

    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    w, h = img.size
    side = min(w, h)                                  # centre-crop to a square
    img = img.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))
    rows = max(8, round(cols * CELL_ASPECT))

    # Work at 4x the character grid and smooth first: real avatars are crisp and textured,
    # and un-smoothed detail turns into speckle noise instead of a face.
    big = ImageOps.autocontrast(img.convert("L"), cutoff=2).resize((cols * 4, rows * 4), Image.LANCZOS)
    big = big.filter(ImageFilter.GaussianBlur(1.6)).filter(ImageFilter.MedianFilter(5))
    bw, bh = big.size
    bp = big.load()
    border = [bp[i, 0] for i in range(bw)] + [bp[i, bh - 1] for i in range(bw)] + \
             [bp[0, i] for i in range(bh)] + [bp[bw - 1, i] for i in range(bh)]
    paper = sorted(border)[len(border) // 2]          # background = median of the border
    ink_is_dark = paper >= 128

    hist = big.histogram()
    total = sum(hist)
    lo = next(i for i in range(256) if sum(hist[: i + 1]) > total * 0.01)
    hi = next(i for i in range(255, -1, -1) if sum(hist[i:]) > total * 0.01)
    span = max(40, (paper - lo) if ink_is_dark else (hi - paper))

    tone = big.resize((cols, rows), Image.BOX).load()
    edges = big.filter(ImageFilter.FIND_EDGES).resize((cols, rows), Image.BOX).load()

    out = []
    for y in range(rows):
        line = []
        for x in range(cols):
            v = tone[x, y]
            ink = (paper - v) / span if ink_is_dark else (v - paper) / span
            ink = max(0.0, min(1.0, ink)) ** 1.5       # light tones stay airy, darks carry the weight
            near_border = min(x, y, cols - 1 - x, rows - 1 - y) < 2
            edge = 0.0 if near_border else min(1.0, edges[x, y] / 30) ** 1.2
            ink = max(ink, edge * 0.7)
            line.append(RAMP[0] if ink < 0.13 else RAMP[1 + min(len(RAMP) - 2, int(ink * (len(RAMP) - 1)))])
        out.append("".join(line).rstrip())
    return out


def _fetch_avatar(url: str) -> bytes | None:
    try:
        sep = "&" if "?" in url else "?"
        with urllib.request.urlopen(urllib.request.Request(f"{url}{sep}s=400",
                                    headers={"User-Agent": "profile-readme-generator"}), timeout=20) as r:
            return r.read()
    except Exception:
        return None


def get_portrait(cfg: dict, data: dict) -> list[str]:
    cols = cfg["portrait_columns"]
    for ext in ("png", "jpg", "jpeg", "webp"):
        p = config.safe_path(f"assets/portrait.{ext}")
        if p.exists():
            rows = from_image(p.read_bytes(), cols)
            _save(rows)
            return rows
    url = (data.get("profile") or {}).get("avatar_url")
    if url and not data.get("demo"):
        raw = _fetch_avatar(url)
        if raw:
            try:
                rows = from_image(raw, cols)
                _save(rows)
                return rows
            except Exception:
                pass
    if CACHE.exists():
        return CACHE.read_text(encoding="utf-8").split("\n")
    return [f"{cfg['name']}"]


def _save(rows: list[str]) -> None:
    config.GENERATED_DIR.mkdir(exist_ok=True)
    CACHE.write_text("\n".join(rows), encoding="utf-8")
