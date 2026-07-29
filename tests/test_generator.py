"""
tests/test_generator.py
--------------------------
Lightweight smoke tests (stdlib `unittest`, no extra dependencies) that
run entirely offline against the sample-data fallback in
`data_fetcher.py`. These aren't meant to assert pixel-perfect output —
just to catch broken f-strings, malformed XML, and layout regressions
before they get committed by the scheduled workflow.

Run with:  python -m unittest discover -s tests
"""

import unittest
import xml.etree.ElementTree as ET

from generator import config, data_fetcher
from generator.svg_builder import build_profile_svg
from generator.components import snake


class TestDataFetcher(unittest.TestCase):
    def test_collect_all_shape(self):
        data = data_fetcher.collect_all("octocat")
        for key in ("profile", "repos", "top_repos", "languages",
                    "calendar", "visitors", "total_stars"):
            self.assertIn(key, data)
        self.assertIsInstance(data["languages"], list)
        self.assertIsInstance(data["calendar"].get("weeks"), list)


class TestSvgBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = data_fetcher.collect_all("octocat")

    def test_profile_svg_is_valid_xml(self):
        svg = build_profile_svg(self.data)
        self.assertTrue(svg.strip().startswith("<svg"))
        ET.fromstring(svg)  # raises on malformed XML

    def test_profile_svg_contains_all_panels(self):
        svg = build_profile_svg(self.data)
        for panel_id in ("sidebar", "terminal", "stats", "contribution-graph",
                          "languages", "tech-stack", "github-stats-panel",
                          "projects", "achievements", "footer"):
            self.assertIn(f'id="{panel_id}"', svg)

    def test_snake_svg_is_valid_xml(self):
        svg = snake.render(self.data)
        ET.fromstring(svg)


if __name__ == "__main__":
    unittest.main()
