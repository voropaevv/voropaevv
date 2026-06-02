from __future__ import annotations

import json
import unittest
from pathlib import Path
from xml.etree import ElementTree

from scripts.generate_matrix_assets import get_font

ROOT = Path(__file__).resolve().parents[1]


class MatrixAssetFontTests(unittest.TestCase):
    def test_matrix_font_renders_japanese_glyphs_as_distinct_shapes(self) -> None:
        font = get_font(16)
        sample_glyphs = "アあヴ"
        masks = {bytes(font.getmask(glyph)) for glyph in sample_glyphs}

        self.assertEqual(
            len(masks),
            len(sample_glyphs),
            f"{getattr(font, 'path', 'default font')} renders Japanese glyphs as fallback boxes",
        )


class MatrixProfileContractTests(unittest.TestCase):
    def test_readme_uses_svg_profile_asset_and_pages_link(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("assets/matrix-profile.svg", readme)
        self.assertIn("assets/open-live-version.svg", readme)
        self.assertIn("https://voropaevv.github.io/voropaevv/", readme)
        self.assertIn("<details>", readme)
        self.assertIn("Public index", readme)
        self.assertNotIn("Current build", readme)
        self.assertNotIn("Working interests", readme)

    def test_docs_config_matches_root_config(self) -> None:
        root_config = json.loads((ROOT / "matrix.config.json").read_text(encoding="utf-8"))
        docs_config = json.loads((ROOT / "docs" / "matrix.config.json").read_text(encoding="utf-8"))
        self.assertEqual(root_config, docs_config)

    def test_svg_is_well_formed_and_has_terminal_animation(self) -> None:
        svg_path = ROOT / "assets" / "matrix-profile.svg"
        ElementTree.parse(svg_path)
        svg = svg_path.read_text(encoding="utf-8")
        config = json.loads((ROOT / "matrix.config.json").read_text(encoding="utf-8"))
        self.assertIn("terminal://public-profile", svg)
        self.assertIn("animate", svg)
        self.assertIn('height="360"', svg)
        self.assertNotIn(config["identity"]["lead"], svg)
        self.assertNotIn("matrix-profile.gif", svg)

    def test_config_contains_requested_terms(self) -> None:
        config = json.loads((ROOT / "matrix.config.json").read_text(encoding="utf-8"))
        terms = set(config["highlightWords"])
        required = {
            "VLAD THE CYBORG",
            "AI AGENTS",
            "LOCAL FIRST",
            "CHAT EXPORTER",
            "LOCAL CHAT",
            "ARCHIVE",
            "SEARCH",
            "STRUCTURE",
            "AUTOMATION",
            "CODEX",
            "PROTOTYPE",
            "PUBLIC TOOL",
            "TOOLS",
            "GITHUB",
        }
        self.assertTrue(required.issubset(terms))
        self.assertEqual(config["readme"]["mode"], "compact")
        self.assertFalse(config["readme"]["showLeadInsideHero"])
        self.assertEqual(config["readme"]["height"], 360)
        self.assertEqual(config["pages"]["mode"], "interactive")
        self.assertIn("mobile", config)
        self.assertIn("build local-ai-chat-exporter --target browser", config["terminalPrompts"])
        self.assertNotIn("cursorDecodeTerms", config)

    def test_cursor_reaction_stays_random_gaussian_cloud(self) -> None:
        matrix_js = (ROOT / "docs" / "js" / "matrix.js").read_text(encoding="utf-8")
        self.assertIn("Math.exp(-distSq / (2 * sigma * sigma))", matrix_js)
        self.assertIn("randChoice(GLYPHS)", matrix_js)
        self.assertNotIn("spawnDecodeWord", matrix_js)
        self.assertNotIn("cursorDecodeTerms", matrix_js)

    def test_terminal_cursor_tracks_typed_text(self) -> None:
        index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "docs" / "css" / "style.css").read_text(encoding="utf-8")
        svg = (ROOT / "assets" / "matrix-profile.svg").read_text(encoding="utf-8")

        self.assertIn('class="terminal-command-line"', index)
        self.assertIn('grid-template-columns: auto minmax(0, 1fr);', css)
        self.assertNotIn("grid-template-columns: auto minmax(0, 1fr) auto", css)
        self.assertIn('attributeName="x"', svg)
        self.assertNotIn('x="1020"', svg)

    def test_pages_has_machine_readable_profile_metadata(self) -> None:
        index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn('type="application/ld+json"', index)
        self.assertIn("Vlad the Cyborg", index)
        public_profile = json.loads((ROOT / "docs" / "public-profile.json").read_text(encoding="utf-8"))
        self.assertEqual(public_profile["name"], "Vlad Voropaev")
        self.assertEqual(public_profile["public_identity"], "Vlad the Cyborg")
        self.assertIn("local-ai-chat-exporter", public_profile["current_projects"][0]["name"])


if __name__ == "__main__":
    unittest.main()
