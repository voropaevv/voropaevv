# Matrix implementation notes

## Final structure

The profile uses two layers:

1. `README.md` — GitHub-safe visual profile using `assets/matrix-profile.svg`.
2. `docs/` — real cursor-reactive Matrix page published with GitHub Pages.

The README does not attempt to run JavaScript. The interactive canvas lives only in GitHub Pages.

## Shared configuration

The source of truth is:

```text
matrix.config.json
```

It controls:

- identity text;
- tags;
- links;
- terminal prompts;
- highlighted red Matrix words;
- main colors;
- animation parameters.

The generator copies this config to:

```text
docs/matrix.config.json
```

The Pages JavaScript loads that copy at runtime.

## User-facing positioning

Final identity:

```text
Vlad Voropaev · Vlad the Cyborg
```

Profile sentence:

```text
I like understanding complicated things, building useful tools, and turning what I find into something other people can use.
```

Top tags:

```text
AI systems · local-first tools · research workflows · automation
```

## Matrix terms

The highlighted red terms are tuned around Vlad's current public GitHub direction:

- `VLAD THE CYBORG`
- `QUESTIONS`
- `SYSTEMS`
- `AI AGENTS`
- `LOCAL FIRST`
- `AUTOMATION`
- `CODEX`
- `DATA`
- `DIAGRAMS`
- `SCRIPTS`
- `PROTOTYPES`
- `TOOLS`
- `CODE`
- `GITHUB`
- plus related terms for local AI, browser extension work, chat export, archives, visual explanations, and open-source utilities.

## Terminal prompt behavior

The rectangle inside the SVG and Pages panel is now terminal-like.

It rotates through prompts about the first public project:

```text
design a local-first browser extension for exporting AI chats
turn local AI conversations into readable archives
structure exported chats for search, backup, and reuse
prototype the small tool before the system gets complicated
publish the useful version when it can stand alone
```

In README, this is SVG animation. In Pages, it is JavaScript typing/erasing text.

## Removed from README

The final README intentionally removes:

- `Current build` block;
- `What I usually build` block;
- `Working interests` table;
- UAE footer;
- prompt list lines like `take a strange question apart`.

## Regeneration

Run:

```bash
python scripts/generate_matrix_assets.py
python -m unittest tests/test_matrix_assets.py
node --check docs/js/matrix.js
```

Generated/updated files:

```text
assets/matrix-profile.svg
assets/matrix-preview.png
docs/matrix.config.json
```

The GitHub Actions workflow regenerates assets when `matrix.config.json` or the generator changes.
