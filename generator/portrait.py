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
RAMP = " .:-=+*#%@"              # Standard smooth character ramp
CELL_ASPECT = 0.6               # monospace cell width / height


def from_image(img_bytes: bytes, cols: int) -> list[str]:
    from PIL import Image, ImageFilter, ImageOps

    with Image.open(io.BytesIO(img_bytes)) as source:
        img = ImageOps.exif_transpose(source).convert("RGB")

    # 1. Center-crop to a square.
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))

    rows = max(8, round(cols * CELL_ASPECT))

    # 2. Preserve facial tones without excessive contrast.
    gray = ImageOps.autocontrast(img.convert("L"), cutoff=1)

    # Light smoothing reduces speckling while preserving features.
    gray = gray.filter(ImageFilter.GaussianBlur(0.35))

    # 3. Estimate the background from the image border.
    px = gray.load()
    iw, ih = gray.size

    border = (
        [px[x, 0] for x in range(iw)]
        + [px[x, ih - 1] for x in range(iw)]
        + [px[0, y] for y in range(ih)]
        + [px[iw - 1, y] for y in range(ih)]
    )

    border.sort()
    paper = border[len(border) // 2]
    ink_is_dark = paper >= 128

    # 4. Find useful tonal range.
    hist = gray.histogram()
    total = sum(hist)

    cumulative = 0
    lo = 0
    for i, count in enumerate(hist):
        cumulative += count
        if cumulative > total * 0.01:
            lo = i
            break

    cumulative = 0
    hi = 255
    for i in range(255, -1, -1):
        cumulative += hist[i]
        if cumulative > total * 0.01:
            hi = i
            break

    span = max(45, (paper - lo) if ink_is_dark else (hi - paper))

    # 5. Downsample the image to character resolution.
    tone_img = gray.resize((cols, rows), Image.Resampling.LANCZOS)
    tone = tone_img.load()

    # Subtle edge map to retain eyes, nose, hair and jawline.
    edge_img = (
        gray.resize((cols * 2, rows * 2), Image.Resampling.LANCZOS)
        .filter(ImageFilter.GaussianBlur(0.5))
        .filter(ImageFilter.FIND_EDGES)
        .resize((cols, rows), Image.Resampling.LANCZOS)
    )
    edges = edge_img.load()

    out = []

    for y in range(rows):
        line = []

        for x in range(cols):
            value = tone[x, y]

            # 6. Convert brightness relative to the background.
            if ink_is_dark:
                ink = (paper - value) / span
            else:
                ink = (value - paper) / span

            ink = max(0.0, min(1.0, ink))

            # Keep highlights airy and shadows recognizable.
            ink = ink ** 1.2

            # Suppress weak background noise; preserve stronger detail.
            edge = min(1.0, edges[x, y] / 90.0)
            if ink < 0.10:
                ink = max(0.0, ink - 0.04)

            ink = max(ink, edge * 0.30)

            # Use spaces for the background instead of visible dots.
            if ink < 0.09:
                line.append(" ")
            else:
                index = round(ink * (len(RAMP) - 1))
                line.append(RAMP[min(index, len(RAMP) - 1)])

        out.append("".join(line).rstrip())

    # Remove empty rows only from the top and bottom.
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()

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