# Codex implementation prompt

You are working in the GitHub profile repository `voropaevv`.

The attached ZIP contains the desired final implementation. Apply it to the repository, preserving the existing Git history and avoiding destructive changes outside the files listed below.

## Goal

Create the final Matrix-style GitHub profile based on these decisions:

- Identity: `Vlad Voropaev · Vlad the Cyborg`.
- The GitHub profile should feel memorable, visually unusual, coherent, and indexable for search/LLM systems.
- Do not make the profile sound like cyberpunk roleplay.
- Keep the public connection to Vlad the Cyborg light but visible.
- README must be short and visual.
- Remove the old content blocks: `Current build`, `What I usually build`, `Working interests`, UAE footer, and the multi-line prompt list.
- Use a terminal-like panel inside the Matrix rectangle.
- The terminal panel should type/erase prompts related to the first public project: `local-ai-chat-exporter`.
- Use a shared `matrix.config.json` as the source of truth for words, colors, texts, prompts, links, and animation settings.
- Use SVG as the README hero asset.

## Files to apply from the ZIP

Copy/replace these files from the ZIP into the repository:

```text
README.md
matrix.config.json
MATRIX_IMPLEMENTATION_NOTES.md
CODEX_IMPLEMENTATION_PROMPT.md
assets/matrix-profile.svg
assets/matrix-preview.png
docs/.nojekyll
docs/404.html
docs/index.html
docs/matrix.config.json
docs/css/style.css
docs/js/matrix.js
scripts/generate_matrix_assets.py
tests/test_matrix_assets.py
.github/workflows/update-matrix.yml
```

Do not copy `.git` or `__MACOSX` files if they exist.

## README requirements

`README.md` must contain only:

1. clickable SVG hero:
   `assets/matrix-profile.svg` linking to `https://voropaevv.github.io/voropaevv/`;
2. centered heading:
   `Vlad Voropaev · Vlad the Cyborg`;
3. centered sentence:
   `I like understanding complicated things, building useful tools, and turning what I find into something other people can use.`;
4. centered tags:
   `AI systems`, `local-first tools`, `research workflows`, `automation`;
5. centered link:
   `Open interactive Matrix version`.

README must not contain:

```text
Current build
What I usually build
Working interests
UAE · building public artifacts
computer vision as a top tag
take a strange question apart
map sources, claims, and mechanisms
build a small tool when the process repeats
share the useful version when it is ready
```

## Matrix asset requirements

- README hero asset must be `assets/matrix-profile.svg`.
- SVG must include a green Matrix rain background.
- Red highlighted words should come from `matrix.config.json`.
- The panel must not have a red top border.
- The central panel must show a terminal-style command line.
- The terminal line should animate by typing and erasing prompt commands.
- The README asset must not rely on JavaScript.

## GitHub Pages requirements

`docs/` is the live interactive layer.

The Pages page must:

- run the real cursor-reactive canvas Matrix logic;
- load `docs/matrix.config.json` at runtime;
- show the same identity, lead sentence, tags, and links as the config;
- type and erase terminal prompts with JavaScript;
- react to mouse and touch movement;
- pause efficiently when the tab is hidden;
- respect `prefers-reduced-motion`;
- remain responsive on mobile.

## Matrix words

Use this exact core word direction, stored in `matrix.config.json`:

```text
VLAD THE CYBORG
VOROPAEV
QUESTIONS
SYSTEMS
AI AGENTS
LOCAL FIRST
LOCAL AI
RESEARCH WORKFLOWS
AUTOMATION
CODEX
DATA
DIAGRAMS
SCRIPTS
PROTOTYPES
TOOLS
CODE
GITHUB
BROWSER EXTENSION
CHAT EXPORTER
LOCAL AI CHAT EXPORTER
CHAT ARCHIVE
VISUAL EXPLANATIONS
OPEN SOURCE
```

## Validation

After applying files, run:

```bash
python scripts/generate_matrix_assets.py
python -m unittest tests/test_matrix_assets.py
node --check docs/js/matrix.js
```

Then verify:

```bash
python - <<'PY'
from pathlib import Path
readme = Path('README.md').read_text()
required = [
    'assets/matrix-profile.svg',
    'https://voropaevv.github.io/voropaevv/',
    'Vlad Voropaev · Vlad the Cyborg',
    'AI systems',
    'local-first tools',
    'research workflows',
    'automation',
]
for item in required:
    assert item in readme, item
for banned in ['Current build', 'What I usually build', 'Working interests', 'UAE · building public artifacts']:
    assert banned not in readme, banned
print('README contract OK')
PY
```

Also verify that:

- `docs/matrix.config.json` exactly matches root `matrix.config.json` after generation;
- `assets/matrix-profile.svg` is valid XML;
- GitHub Pages source remains `main` + `/docs`.

## Commit

Commit with:

```text
Finalize Matrix profile README
```
