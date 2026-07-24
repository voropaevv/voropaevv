# Maintenance brief for the developer profile

Work in the GitHub profile repository `voropaevv/voropaevv`.

## Goal

Keep the GitHub profile and GitHub Pages site aligned around one public professional identity:

```text
Vlad Voropaev
Applied AI Engineer & Product Builder
```

The GitHub Pages surface is a developer portfolio in the existing Matrix style. A future general personal website is separate and must not be folded into this repository without a new explicit decision.

## Content rules

- Lead with working systems and inspectable evidence
- Treat Computer Vision as the deepest verified technical foundation
- Show multimodal AI, LLM agents, automation, and product engineering as connected expansion areas
- Keep Jelluvi status precise: open source and in active development
- Do not claim an extension-store release, customers, user counts, or adoption without current evidence
- Present Word Solver CV as a documented portfolio system and preserve its verified facts
- Link the IEEE paper through DOI `10.1109/ACDSA59508.2024.10467698`
- Label older repositories as historical public archive material
- Keep public location at UAE country level
- Do not add private projects, private repository names, personal identifiers, credentials, or raw personal context

## Visual rules

- Preserve the black, green, and sparse-red Matrix language
- Keep the developer content readable above the animation
- Use responsive layouts and visible focus states
- Respect reduced-motion preferences
- Keep the terminal interaction functional
- Do not replace the existing Matrix engine with a generic template

## Source of truth

Update `matrix.config.json`, then regenerate derived files:

```bash
python3 scripts/generate_matrix_assets.py
```

Generated files:

```text
assets/matrix-profile.svg
assets/matrix-preview.png
assets/open-live-version.svg
docs/matrix.config.json
docs/public-profile.json
```

## Required verification

```bash
python3 -m unittest tests/test_matrix_assets.py
node --check docs/js/matrix.js
python3 -m json.tool matrix.config.json
cmp matrix.config.json docs/matrix.config.json
```

Also verify the page visually in a real browser at desktop and mobile widths, test the terminal commands, and inspect the browser console before publishing.
