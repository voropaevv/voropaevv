# Matrix README port notes

## Source logic used

The uploaded site used `public/js/matrix.js` with:

- ASCII + Japanese glyph pools;
- configurable background glyphs;
- falling columns;
- occasional highlighted words;
- fading cells;
- cursor-spawned glyphs around the pointer.

## README constraint

GitHub profile README is Markdown. It can display images/GIFs/SVGs, but it cannot run arbitrary `canvas` + `requestAnimationFrame` JavaScript inside the README itself.

So the port is split into two layers:

1. `assets/matrix.svg` — GitHub-safe animated SVG for the actual README.
2. `docs/` — real cursor-reactive canvas version for GitHub Pages.

## Highlight words

The old YouTube-course words were replaced with profile-appropriate terms:

`VLAD`, `VOROPAEV`, `QUESTIONS`, `RESEARCH`, `AI_AGENTS`, `LOCAL_AI`, `CHAT_EXPORTER`, `SOURCE_MAPS`, `CLAIM_MATRIX`, `COMPUTER_VISION`, `VISUAL_STORIES`, `BUILD_AND_SHARE`, and related terms.

## Edit points

- Update red/green colors in `MatrixConfig` inside `scripts/generate_matrix_svg.py`.
- Update falling words in the `WORDS` list in both:
  - `scripts/generate_matrix_svg.py`
  - `docs/js/matrix.js`
- Regenerate SVG:

```bash
python scripts/generate_matrix_svg.py --output assets/matrix.svg
```

## GitHub Pages

To use the cursor-reactive version:

1. Push this repo.
2. Go to Settings → Pages.
3. Set source to `/docs` on the default branch.
4. Open the generated Pages URL.
