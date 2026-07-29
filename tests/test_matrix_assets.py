from __future__ import annotations

import json
import os
import unittest
from pathlib import Path
from xml.etree import ElementTree

from scripts.generate_matrix_assets import get_font

ROOT = Path(__file__).resolve().parents[1]


class MatrixAssetFontTests(unittest.TestCase):
    def test_matrix_font_renders_japanese_glyphs_as_distinct_shapes(self) -> None:
        if os.environ.get("MATRIX_SKIP_RASTER_FONT_TEST") == "1":
            self.skipTest("CI validates vector assets without installing a platform CJK raster font")

        font = get_font(16)
        sample_glyphs = "アあヴ"
        masks = {bytes(font.getmask(glyph)) for glyph in sample_glyphs}

        self.assertEqual(
            len(masks),
            len(sample_glyphs),
            f"{getattr(font, 'path', 'default font')} renders Japanese glyphs as fallback boxes",
        )


class MatrixProfileContractTests(unittest.TestCase):
    def test_readme_leads_with_industrial_computer_vision(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        required = {
            "assets/matrix-profile.svg",
            "assets/open-live-version.svg",
            "https://voropaevv.github.io/voropaevv/",
            "Computer Vision Engineer",
            "Industrial Computer Vision",
            "Crane operator safety vision system",
            "17,696 CCTV frames",
            "Jelluvi",
            "Word Solver CV",
            "10.1109/ACDSA59508.2024.10467698",
            "https://www.linkedin.com/in/thevladvoropaev/",
            "mailto:thevladvoropaev@gmail.com",
            "Vlad_Voropaev_Computer_Vision_Engineer_Resume.pdf",
        }
        for item in required:
            self.assertIn(item, readme)

        unsupported_claims = {
            "thousands of users",
            "released on the Chrome Web Store",
            "production customers",
            "44 comics",
            "22+22",
        }
        for claim in unsupported_claims:
            self.assertNotIn(claim, readme.lower())

    def test_docs_config_matches_root_config(self) -> None:
        root_config = json.loads((ROOT / "matrix.config.json").read_text(encoding="utf-8"))
        docs_config = json.loads((ROOT / "docs" / "matrix.config.json").read_text(encoding="utf-8"))
        self.assertEqual(root_config, docs_config)

    def test_svg_is_well_formed_and_has_terminal_animation(self) -> None:
        svg_path = ROOT / "assets" / "matrix-profile.svg"
        svg_tree = ElementTree.parse(svg_path)
        svg = svg_path.read_text(encoding="utf-8")
        config = json.loads((ROOT / "matrix.config.json").read_text(encoding="utf-8"))
        self.assertIn("terminal://developer-profile", svg)
        self.assertIn("Computer Vision Engineer", svg)
        self.assertIn("animate", svg)
        self.assertIn('height="360"', svg)
        self.assertNotIn(config["identity"]["lead"], svg)
        self.assertNotIn("matrix-profile.gif", svg)

        namespace = {"svg": "http://www.w3.org/2000/svg"}
        clip_widths = []
        for clip in svg_tree.findall(".//svg:clipPath", namespace):
            width_animation = clip.find(
                'svg:rect/svg:animate[@attributeName="width"]',
                namespace,
            )
            self.assertIsNotNone(width_animation)
            width_values = [
                float(value)
                for value in width_animation.attrib["values"].split(";")
            ]
            clip_widths.append(width_values[2])

        cursor = svg_tree.find('.//svg:text[@class="cursor"]', namespace)
        self.assertIsNotNone(cursor)
        cursor_animation = cursor.find(
            'svg:animate[@attributeName="x"]',
            namespace,
        )
        self.assertIsNotNone(cursor_animation)
        cursor_x_values = [
            float(value)
            for value in cursor_animation.attrib["values"].split(";")
        ]

        prompts = [
            prompt[: config["readme"]["promptMaxLength"]]
            for prompt in config["terminalPrompts"]
        ]
        commands = svg_tree.findall('.//svg:text[@class="command"]', namespace)
        self.assertEqual(len(commands), len(prompts))
        self.assertEqual(len(clip_widths), len(prompts))

        for index, (command, prompt, clip_width) in enumerate(
            zip(commands, prompts, clip_widths, strict=True)
        ):
            self.assertEqual(command.text, prompt)
            self.assertEqual(command.attrib["lengthAdjust"], "spacingAndGlyphs")
            self.assertAlmostEqual(float(command.attrib["textLength"]), clip_width)
            cursor_at_type_end = cursor_x_values[1 + index * 4]
            cursor_during_hold = cursor_x_values[2 + index * 4]
            self.assertAlmostEqual(cursor_at_type_end - 184.0, clip_width)
            self.assertAlmostEqual(cursor_during_hold - 184.0, clip_width)

    def test_config_contains_current_positioning_and_public_evidence(self) -> None:
        config = json.loads((ROOT / "matrix.config.json").read_text(encoding="utf-8"))
        terms = set(config["highlightWords"])
        required_terms = {
            "VLAD VOROPAEV",
            "COMPUTER VISION",
            "VIDEO ANALYTICS",
            "MULTI CAMERA",
            "OBJECT DETECTION",
            "OBJECT TRACKING",
            "POSE ESTIMATION",
            "PPE",
            "RTSP",
            "NEUROQUEST",
            "EVIDENCE",
        }
        self.assertTrue(required_terms.issubset(terms))
        self.assertEqual(config["identity"]["role"], "Computer Vision Engineer")
        self.assertEqual(config["identity"]["email"], "thevladvoropaev@gmail.com")
        self.assertEqual(config["identity"]["location"], "UAE")
        self.assertEqual(config["readme"]["mode"], "compact")
        self.assertFalse(config["readme"]["showLeadInsideHero"])
        self.assertEqual(config["readme"]["height"], 360)
        self.assertEqual(config["pages"]["mode"], "interactive")
        self.assertIn("analyze rtsp --detect --track --reason", config["terminalPrompts"])
        self.assertNotIn("cursorDecodeTerms", config)

    def test_public_profile_is_public_safe_and_evidence_backed(self) -> None:
        profile = json.loads((ROOT / "docs" / "public-profile.json").read_text(encoding="utf-8"))
        self.assertEqual(profile["name"], "Vlad Voropaev")
        self.assertEqual(profile["role"], "Computer Vision Engineer")
        self.assertEqual(profile["location"], "UAE")
        self.assertEqual(profile["email"], "thevladvoropaev@gmail.com")
        self.assertEqual(
            [project["name"] for project in profile["industrial_experience"]],
            ["Crane operator safety vision system", "Industrial safety video analytics"],
        )
        self.assertEqual([project["name"] for project in profile["open_source"]], ["Jelluvi"])
        self.assertEqual([project["name"] for project in profile["educational_archive"]], ["Word Solver CV"])
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
            "Computer Vision Engineer",
            "Industrial Video",
            "thevladvoropaev@gmail.com",
            "Vlad_Voropaev_Computer_Vision_Engineer_Resume.pdf",
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

    def test_mobile_navigation_keeps_every_primary_destination_visible(self) -> None:
        css = (ROOT / "docs" / "css" / "style.css").read_text(encoding="utf-8")
        self.assertNotIn(".site-nav a:nth-child", css)

    def test_public_copy_keeps_professional_and_educational_work_separate(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        industrial_index = readme.index("## Industrial Computer Vision")
        research_index = readme.index("## Research to System")
        open_source_index = readme.index("## Open-Source Engineering")
        educational_index = readme.index("<summary>Educational and historical public archive</summary>")
        self.assertLess(industrial_index, research_index)
        self.assertLess(research_index, open_source_index)
        self.assertLess(open_source_index, educational_index)

        public_text = "\n".join(
            [
                readme,
                (ROOT / "docs" / "index.html").read_text(encoding="utf-8"),
                (ROOT / "matrix.config.json").read_text(encoding="utf-8"),
            ]
        ).lower()
        for forbidden in (
            "44 comics",
            "22+22",
            "verified personal contribution",
            "evidence boundary",
            "raw_private",
            "/users/msm4m-vv",
            "/volumes/vlados",
        ):
            self.assertNotIn(forbidden, public_text)


if __name__ == "__main__":
    unittest.main()
