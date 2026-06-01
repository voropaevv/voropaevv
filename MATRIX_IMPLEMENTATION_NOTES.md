# Matrix implementation notes

## What was ported

The interactive GitHub Pages layer keeps the uploaded Matrix code's core behavior:

- mixed ASCII + Japanese glyph alphabet;
- background random glyph cells;
- falling column streams;
- stream trails with fading alpha;
- highlighted words injected into streams;
- cursor-reactive glyph spawning;
- source priority between background, cursor, and falling streams;
- resize-aware canvas rendering;
- `requestAnimationFrame` render loop.

## What changed

The highlighted words are tuned for Vlad Voropaev / vladthecyborg and shared
between the canvas and generated README assets:

`VLAD`, `VOROPAEV`, `VOROPAEVV`, `QUESTIONS`, `STRANGE`, `WHY`, `HOW`,
`WHAT IF`, `BUILDING`, `RESEARCH`, `SYSTEMS`, `AI AGENTS`, `LOCAL AI`,
`LOCAL FIRST`, `CHAT EXPORTER`, `SOURCE MAP`, `CLAIM MATRIX`, `MECHANISMS`,
`EVIDENCE`, `UNCERTAINTY`, `VISUAL STORIES`, `DEEP EXPLANATIONS`,
`EXPLAINERS`, `PYTHON`, `TYPESCRIPT`, `COMPUTER VISION`, `AUTOMATION`,
`NOTEBOOKS`, `DATA`, `DIAGRAMS`, `SCRIPTS`, `PROTOTYPES`, `AUDITABLE`,
`READABLE`, `STRUCTURE`, `TOOLS`, `CODE`, `GITHUB`, `README`, `FINDINGS`,
`BUILD AND SHARE`.

Colors:

- falling symbols: green;
- highlighted words: red;
- cursor reaction: white-green;
- background: black.

## GitHub limitation

GitHub profile README cannot run the canvas JavaScript directly. The README uses an animated GIF/SVG visual header. The cursor-reactive version lives in `docs/` and is published through GitHub Pages.

The page respects `prefers-reduced-motion` by rendering a static frame and
stops the animation frame loop while the tab is hidden.

The generated GIF/PNG must be rendered with a Japanese-capable font. The
generator prefers Hiragino/Noto CJK fonts and the GitHub Actions workflow
installs `fonts-noto-cjk` before regenerating assets.

## Update workflow

Edit words in two places:

- `docs/js/matrix.js` for the live interactive page;
- `scripts/generate_matrix_assets.py` for the README GIF/SVG.

Then run:

```bash
python scripts/generate_matrix_assets.py
```
