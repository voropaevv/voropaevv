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
- README compact mode and Pages interactive mode;
- terminal prompts;
- highlighted red Matrix words;
- cursor decode terms and command-mode messages;
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

The highlighted red terms are intentionally sparse and tuned around Vlad's current public GitHub direction:

- `VLAD THE CYBORG`
- `AI AGENTS`
- `LOCAL FIRST`
- `CHAT EXPORTER`
- `LOCAL CHAT`
- `ARCHIVE`
- `SEARCH`
- `STRUCTURE`
- `AUTOMATION`
- `CODEX`
- `PROTOTYPE`
- `PUBLIC TOOL`
- `TOOLS`
- `GITHUB`

## Terminal prompt behavior

The rectangle inside the SVG and Pages panel is now terminal-like.

It rotates through prompts about the first public project:

```text
build local-ai-chat-exporter --target browser
export ai-chats --format markdown,json
index chat-archive --searchable --local-first
package useful-parts --public
prototype small-tool --before system-bloat
publish when-useful --not-before
```

In README, this is SVG animation. In Pages, it is JavaScript typing/erasing text.

The README hero is compact and does not include the long lead sentence inside the SVG. The Pages panel keeps the lead and adds a status line plus command hint:

```text
try: help · project · tools · matrix · github
```

Keyboard command mode supports `h`, `p`, `t`, `m`, and `g`. The `m` command briefly boosts Matrix density; cursor movement also injects short white-green decode terms.

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
assets/open-live-version.svg
docs/matrix.config.json
docs/public-profile.json
```

The GitHub Actions workflow regenerates assets when `matrix.config.json` or the generator changes.
