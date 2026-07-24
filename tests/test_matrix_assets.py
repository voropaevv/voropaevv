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
    def test_readme_leads_with_verified_developer_work(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        required = {
            "assets/matrix-profile.svg",
            "assets/open-live-version.svg",
            "https://voropaevv.github.io/voropaevv/",
            "Applied AI Engineer &amp; Product Builder",
            "Jelluvi",
            "Word Solver CV",
            "123,509",
            "10.1109/ACDSA59508.2024.10467698",
            "https://www.linkedin.com/in/thevladvoropaev/",
        }
        for item in required:
            self.assertIn(item, readme)

        unsupported_claims = {
            "thousands of users",
            "released on the Chrome Web Store",
            "production customers",
        }
        for claim in unsupported_claims:
            self.assertNotIn(claim, readme.lower())

    def test_docs_config_matches_root_config(self) -> None:
        root_config = json.loads((ROOT / "matrix.config.json").read_text(encoding="utf-8"))
        docs_config = json.loads((ROOT / "docs" / "matrix.config.json").read_text(encoding="utf-8"))
        self.assertEqual(root_config, docs_config)

    def test_svg_is_well_formed_and_has_terminal_animation(self) -> None:
        svg_path = ROOT / "assets" / "matrix-profile.svg"
        ElementTree.parse(svg_path)
        svg = svg_path.read_text(encoding="utf-8")
        config = json.loads((ROOT / "matrix.config.json").read_text(encoding="utf-8"))
        self.assertIn("terminal://developer-profile", svg)
        self.assertIn("Applied AI Engineer &amp; Product Builder", svg)
        self.assertIn("animate", svg)
        self.assertIn('height="360"', svg)
        self.assertNotIn(config["identity"]["lead"], svg)
        self.assertNotIn("matrix-profile.gif", svg)

    def test_config_contains_current_positioning_and_public_evidence(self) -> None:
        config = json.loads((ROOT / "matrix.config.json").read_text(encoding="utf-8"))
        terms = set(config["highlightWords"])
        required_terms = {
            "VLAD VOROPAEV",
            "APPLIED AI",
            "PRODUCT BUILDER",
            "COMPUTER VISION",
            "MULTIMODAL AI",
            "AI AGENTS",
            "LOCAL FIRST",
            "JELLUVI",
            "WORD SOLVER",
            "NEUROCOMICS",
            "EVIDENCE",
        }
        self.assertTrue(required_terms.issubset(terms))
        self.assertEqual(config["identity"]["role"], "Applied AI Engineer & Product Builder")
        self.assertEqual(config["identity"]["location"], "UAE")
        self.assertEqual(config["readme"]["mode"], "compact")
        self.assertFalse(config["readme"]["showLeadInsideHero"])
        self.assertEqual(config["readme"]["height"], 360)
        self.assertEqual(config["pages"]["mode"], "interactive")
        self.assertIn("build useful-ai --from research --to product", config["terminalPrompts"])
        self.assertNotIn("cursorDecodeTerms", config)

    def test_public_profile_is_public_safe_and_evidence_backed(self) -> None:
        profile = json.loads((ROOT / "docs" / "public-profile.json").read_text(encoding="utf-8"))
        self.assertEqual(profile["name"], "Vlad Voropaev")
        self.assertEqual(profile["role"], "Applied AI Engineer & Product Builder")
        self.assertEqual(profile["location"], "UAE")
        self.assertEqual(
            [project["name"] for project in profile["current_projects"]],
            ["Jelluvi", "Word Solver CV"],
        )
        self.assertEqual(
            profile["research"][0]["doi"],
            "10.1109/ACDSA59508.2024.10467698",
        )
        serialized = json.dumps(profile).lower()
        for private_term in ("raw_private", "golden visa", "home address"):
            self.assertNotIn(private_term, serialized)

    def test_cursor_reaction_stays_random_gaussian_cloud(self) -> None:
        matrix_js = (ROOT / "docs" / "js" / "matrix.js").read_text(encoding="utf-8")
        self.assertIn("Math.exp(-distSq / (2 * sigma * sigma))", matrix_js)
        self.assertIn("randChoice(GLYPHS)", matrix_js)
        self.assertNotIn("spawnDecodeWord", matrix_js)
        self.assertNotIn("cursorDecodeTerms", matrix_js)

    def test_terminal_is_interactive_and_accessible(self) -> None:
        index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "docs" / "css" / "style.css").read_text(encoding="utf-8")
        js = (ROOT / "docs" / "js" / "matrix.js").read_text(encoding="utf-8")
        svg = (ROOT / "assets" / "matrix-profile.svg").read_text(encoding="utf-8")

        self.assertIn('class="terminal-command-line"', index)
        self.assertIn('id="terminal-form"', index)
        self.assertIn('id="terminal-input"', index)
        self.assertIn('aria-live="polite"', index)
        self.assertIn("executeCommand", js)
        self.assertIn("grid-template-columns: auto minmax(0, 1fr) auto;", css)
        self.assertIn('attributeName="x"', svg)
        self.assertNotIn('x="1020"', svg)

    def test_pages_has_search_and_machine_readable_metadata(self) -> None:
        index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        required = {
            'type="application/ld+json"',
            'rel="canonical"',
            'property="og:title"',
            'name="twitter:card"',
            "Applied AI Engineer &amp; Product Builder",
            "https://www.linkedin.com/in/thevladvoropaev/",
            "https://doi.org/10.1109/ACDSA59508.2024.10467698",
            'id="work"',
            'id="research"',
            'id="stack"',
            'id="contact"',
        }
        for item in required:
            self.assertIn(item, index)

        self.assertNotIn('"alternateName"', index)
        self.assertNotIn('data-config="alias"', index)


if __name__ == "__main__":
    unittest.main()
