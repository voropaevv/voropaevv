from __future__ import annotations

import unittest

from scripts.generate_matrix_assets import get_font


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


if __name__ == "__main__":
    unittest.main()
