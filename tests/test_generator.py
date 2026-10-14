"""Offline tests (stdlib unittest). Run:  python -m unittest discover -s tests -v"""
import datetime as dt
import io
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

from generator import build, config, github_data as gd, portrait
from generator.kit import PALETTES


def load_cfg(**over):
    cfg = config.load()
    cfg.update(over)
    return cfg


class ConfigTests(unittest.TestCase):
    def test_rejects_unsafe_links(self):
        for bad in ("javascript:alert(1)", "http://example.com", "https://x.com/a b", "data:text/html,hi"):
            with self.assertRaises(config.ConfigError):
                config.check_url("x", bad)
        self.assertEqual(config.check_url("x", "mailto:a@b.co"), "mailto:a@b.co")

    def test_rejects_bad_username(self):
        with mock.patch.dict("os.environ", {"GH_USERNAME": "bad name!"}):
            with self.assertRaises(config.ConfigError):
                config.load()

    def test_path_cannot_escape_repo(self):
        with self.assertRaises(config.ConfigError):
            config.safe_path("../etc/passwd")
        self.assertTrue(str(config.safe_path("assets/portrait.png")).startswith(str(config.ROOT)))


class DataTests(unittest.TestCase):
    def cal(self, counts):
        start = dt.date(2026, 1, 1)
        days = [{"contributionCount": c, "date": (start + dt.timedelta(days=i)).isoformat(), "weekday": i % 7}
                for i, c in enumerate(counts)]
        return {"totalContributions": sum(counts), "weeks": [{"contributionDays": days}]}

    def test_streaks(self):
        s = gd.compute_streaks(self.cal([1, 1, 0, 2, 3, 4, 0]))   # today (last) empty: streak stays alive
        self.assertEqual((s["current"], s["longest"], s["active_days"]), (3, 3, 5))
        s = gd.compute_streaks(self.cal([1, 0, 0, 0]))
        self.assertEqual(s["current"], 0)

    def test_project_selection_skips_profile_repo_and_forks(self):
        data = gd.demo_data("RohanKoriya")
        data["repos"] += [{"name": "RohanKoriya", "description": "", "language": "", "stars": 99, "forks": 0,
                           "pushed_at": "2026-01-01T00:00:00Z", "url": "https://github.com/RohanKoriya/RohanKoriya",
                           "fork": False, "archived": False, "homepage": ""},
                          {"name": "forked", "description": "", "language": "", "stars": 500, "forks": 0,
                           "pushed_at": "2026-01-01T00:00:00Z", "url": "https://github.com/x/forked",
                           "fork": True, "archived": False, "homepage": ""}]
        names = [r["name"] for r in gd.select_projects(data, load_cfg())]
        self.assertNotIn("RohanKoriya", names)
        self.assertNotIn("forked", names)
        self.assertEqual(names[0], "sample-project-one")

    def test_failure_policy(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(gd, "CACHE_PATH", Path(d) / "data.json"):
            with self.assertRaises(SystemExit):           # no live data, no cache -> never overwrite outputs
                build.acquire_data(load_cfg(), demo=False, offline=True)
            gd.save_cache(gd.demo_data("x") | {"demo": False})
            self.assertEqual(build.acquire_data(load_cfg(), demo=False, offline=True)["username"], "x")


class PortraitTests(unittest.TestCase):
    def test_ascii_from_image(self):
        from PIL import Image, ImageDraw
        im = Image.new("RGB", (200, 200), "white")
        ImageDraw.Draw(im).ellipse((50, 50, 150, 150), fill="black")
        buf = io.BytesIO()
        im.save(buf, "PNG")
        rows = portrait.from_image(buf.getvalue(), 60)
        self.assertEqual(len(rows), 36)
        self.assertLessEqual(max(len(r) for r in rows), 60)
        self.assertTrue(any(ch not in " " for r in rows for ch in r))


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = load_cfg(intro="Hello <script>alert(1)</script> & \"friends\"")
        cls.data = gd.demo_data("RohanKoriya")
        with mock.patch.object(portrait, "get_portrait", return_value=["  .:-=+*#%@  ", " @@##**++== "]):
            cls.files = build.render_all(cls.cfg, cls.data)

    def test_all_variants_exist_and_are_valid_xml(self):
        self.assertEqual(len([f for f in self.files if f.startswith("activity-")]), len(PALETTES))
        for name, svg in self.files.items():
            ET.fromstring(svg)                       # raises on malformed XML
            self.assertLess(len(svg), 400_000, name)

    def test_svgs_are_safe_for_github(self):
        for name, svg in self.files.items():
            low = svg.lower()
            for banned in ("<script", "foreignobject", "onload=", "onclick=", "javascript:", "<image", "@import", "url(http"):
                self.assertNotIn(banned, low, f"{name} contains {banned}")
            self.assertEqual(re.findall(r'(?:href|src)="[^#"]', low), [], name)   # no external references
            self.assertEqual(low.count("http://"), 1, name)                          # only the xmlns

    def test_user_text_is_escaped(self):
        svg = self.files["hero-dark.svg"]
        self.assertNotIn("<script", svg)
        self.assertIn("&lt;script&gt;", svg)

    def test_snake_animation_is_consistent(self):
        svg = self.files["snake-dark.svg"]
        counts = {len(m.split(";")) for m in re.findall(r'attributeName="[xy]" values="([^"]+)"', svg)}
        self.assertEqual(counts, {53 * 7})

    def test_static_state_is_complete(self):
        """Scan line must be hidden by default; snake must start inside the grid."""
        svg = self.files["hero-dark.svg"]
        self.assertIn('opacity="0"', svg)
        self.assertNotIn('x="0" y="0" width="14.1"', self.files["snake-dark.svg"])


class ReadmeTests(unittest.TestCase):
    def test_region_replace_is_idempotent_and_preserves_outside(self):
        cfg, data = load_cfg(), gd.demo_data("RohanKoriya")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "README.md"
            path.write_text("before\n" + build.START + "\nold\n" + build.END + "\nafter\n")
            self.assertTrue(build.update_readme(cfg, data, 3, path))
            first = path.read_text()
            self.assertTrue(first.startswith("before\n") and first.endswith("\nafter\n"))
            self.assertNotIn("\nold\n", first)
            self.assertFalse(build.update_readme(cfg, data, 3, path))           # second run: no change
            self.assertEqual(first, path.read_text())

    def test_readme_links_are_escaped_and_clickable(self):
        block = build.readme_block(load_cfg(), gd.demo_data("RohanKoriya"), 3)
        self.assertIn('href="https://github.com/RohanKoriya"', block)
        self.assertIn("prefers-color-scheme: dark", block)
        self.assertEqual(block.count("<picture>"), block.count("</picture>"))


if __name__ == "__main__":
    unittest.main()
