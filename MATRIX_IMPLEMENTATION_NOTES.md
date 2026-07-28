# Matrix developer profile implementation

## Purpose

This repository has two public surfaces:

1. `README.md` — the GitHub profile README
2. `docs/` — the interactive developer portfolio published with GitHub Pages

Both surfaces represent Vlad Voropaev as a Computer Vision Engineer, with industrial video analytics and measurable systems work first. The GitHub Pages site is intentionally developer-focused; a future broader personal website is a separate project and hosting decision.

## Visual direction

The existing Matrix language remains the design system:

- black background
- green digital rain
- sparse red signal words
- monospace typography
- terminal controls
- thin green borders and restrained glow

The live page extends the original single-card composition into a responsive portfolio without changing that visual identity.

## Public content hierarchy

1. Vlad Voropaev
2. Computer Vision Engineer
3. Industrial video analytics, multi-camera systems, detection, tracking, pose, PPE, zones, and OCR
4. Real operating work and measured outcomes
5. NeuroQuest as first-author IEEE research
6. Jelluvi as secondary open-source product engineering
7. Word Solver CV and older repositories as educational or historical archive material

Current product status is stated precisely. Jelluvi is open source and in active development.

## Shared configuration

The source of truth for generated Matrix assets and machine-readable public profile data is:

```text
matrix.config.json
```

The generator copies it to:

```text
docs/matrix.config.json
```

It also derives:

```text
assets/matrix-profile.svg
assets/matrix-preview.png
assets/open-live-version.svg
docs/public-profile.json
```

## Interactive terminal

The GitHub Pages terminal supports:

```text
help
about
projects
research
stack
contact
matrix
clear
```

The command form is keyboard-accessible and reports results through an `aria-live` region. Section commands scroll to the corresponding portfolio content. The Matrix command temporarily increases the rain density.

## Performance and accessibility

- Matrix rendering pauses while the page is hidden
- mobile density is lower than desktop density
- `prefers-reduced-motion` switches to a static Matrix frame
- semantic landmarks, heading order, skip navigation, visible focus states, and form labels are present
- all primary navigation items remain visible on mobile
- supporting text stays readable without competing with headings
- the background canvas is decorative and hidden from accessibility APIs

## Regeneration and verification

Run:

```bash
python3 scripts/generate_matrix_assets.py
python3 -m unittest tests/test_matrix_assets.py
node --check docs/js/matrix.js
```

Then verify the live page in a browser at desktop and mobile widths, test the terminal commands, inspect browser console errors, and confirm that `docs/matrix.config.json` exactly matches `matrix.config.json`.
