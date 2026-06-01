#!/usr/bin/env python3
"""Generate a GitHub-safe Matrix-style SVG for a profile README.

This ports the core idea from the uploaded canvas implementation into a
static/animated SVG asset that can be embedded in GitHub Markdown.

Why SVG instead of canvas/JS?
GitHub profile READMEs are Markdown documents. They can display images/GIFs/SVGs,
but they do not execute arbitrary JavaScript/canvas logic inside the README.
"""

from __future__ import annotations

import argparse
import html
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

GLYPHS_ASCII = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~\\"
)
GLYPHS_JP_KATAKANA = (
    "アイウエオカキクケコサシスセソタチツテトナニヌネノ"
    "ハヒフヘホマミムメモヤユヨラリルレロワヲンヴ"
    "ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ"
    "ァィゥェォャュョッー・"
)
GLYPHS_JP_HIRAGANA = (
    "あいうえおかきくけこさしすせそたちつてとなにぬねの"
    "はひふへほまみむめもやゆよらりるれろわをん"
    "がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ"
    "ぁぃぅぇぉゃゅょっー・"
)
GLYPHS = GLYPHS_ASCII + GLYPHS_JP_KATAKANA + GLYPHS_JP_HIRAGANA

WORDS = [
    "VLAD",
    "VOROPAEV",
    "QUESTIONS",
    "STRANGE",
    "WHY",
    "HOW",
    "WHAT_IF",
    "BUILDING",
    "RESEARCH",
    "SYSTEMS",
    "AI_AGENTS",
    "LOCAL_AI",
    "CHAT_EXPORTER",
    "SOURCE_MAPS",
    "CLAIM_MATRIX",
    "MECHANISMS",
    "EVIDENCE",
    "VISUAL_STORIES",
    "EXPLAINERS",
    "PYTHON",
    "TYPESCRIPT",
    "COMPUTER_VISION",
    "AUTOMATION",
    "NOTEBOOKS",
    "DATA",
    "DIAGRAMS",
    "SCRIPTS",
    "PROTOTYPES",
    "LOCAL_FIRST",
    "AUDITABLE",
    "READABLE",
    "STRUCTURE",
    "TOOLS",
    "CODE",
    "GITHUB",
    "README",
    "FINDINGS",
    "BUILD_AND_SHARE",
]


@dataclass(frozen=True)
class MatrixConfig:
    width: int = 1200
    height: int = 500
    font_size: int = 15
    row_gap: int = 2
    stream_count: int = 64
    min_trail: int = 22
    max_trail: int = 44
    word_probability: float = 0.72
    seed: int = 20260601
    background_glyphs: int = 520
    bg_fill: str = "#020503"
    green_dim: str = "#005c2e"
    green: str = "#00ff66"
    green_head: str = "#d7ffe4"
    red: str = "#ff2d55"
    red_soft: str = "#ff5c74"
    text_primary: str = "#eafff1"
    text_secondary: str = "#9fffc3"

    @property
    def row_height(self) -> int:
        return self.font_size + self.row_gap

    @property
    def rows(self) -> int:
        return self.height // self.row_height

    @property
    def cols(self) -> int:
        return self.width // self.font_size


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def rand_choice(rng: random.Random, chars: str) -> str:
    return chars[rng.randrange(len(chars))]


def make_stream_chars(
    rng: random.Random,
    length: int,
    words: list[str],
    word_probability: float,
) -> list[tuple[str, str]]:
    """Return (glyph, role) pairs. role is head, tail, word, or dim."""
    chars = [(rand_choice(rng, GLYPHS), "tail") for _ in range(length)]
    if rng.random() < word_probability:
        word = rng.choice(words)
        start = rng.randrange(2, max(3, length - len(word) - 1))
        for offset, ch in enumerate(word):
            chars[start + offset] = (ch, "word")
    if chars:
        chars[0] = (chars[0][0], "head")
    return chars


def opacity_for(index: int, length: int, role: str, rng: random.Random) -> float:
    if role == "head":
        return 1.0
    if role == "word":
        return rng.uniform(0.82, 1.0)
    normalized = index / max(1, length - 1)
    base = max(0.10, 0.88 - normalized * 0.78)
    jitter = rng.uniform(-0.05, 0.07)
    return max(0.05, min(0.9, base + jitter))


def stream_color(role: str, cfg: MatrixConfig) -> str:
    if role == "head":
        return cfg.green_head
    if role == "word":
        return cfg.red
    return cfg.green


def build_background(rng: random.Random, cfg: MatrixConfig) -> list[str]:
    nodes: list[str] = []
    for _ in range(cfg.background_glyphs):
        x = rng.randrange(0, cfg.width)
        y = rng.randrange(0, cfg.height)
        ch = rand_choice(rng, GLYPHS)
        opacity = rng.uniform(0.05, 0.22)
        color = cfg.green_dim if rng.random() > 0.08 else cfg.red_soft
        nodes.append(
            f'<text x="{x}" y="{y}" fill="{color}" '
            f'opacity="{opacity:.3f}">{esc(ch)}</text>'
        )
    return nodes


def build_streams(rng: random.Random, cfg: MatrixConfig) -> list[str]:
    nodes: list[str] = []
    cols = list(range(cfg.cols))
    rng.shuffle(cols)
    selected_cols = cols[: min(cfg.stream_count, len(cols))]

    for stream_id, col in enumerate(selected_cols):
        trail = rng.randint(cfg.min_trail, cfg.max_trail)
        stream_len = cfg.rows + trail
        x = col * cfg.font_size
        start_y = -trail * cfg.row_height
        end_y = cfg.height + trail * cfg.row_height
        duration = rng.uniform(7.5, 16.0)
        begin = -rng.uniform(0.0, duration)
        chars = make_stream_chars(rng, stream_len, WORDS, cfg.word_probability)

        text_parts = [
            f'<g id="s{stream_id}" transform="translate({x} {start_y})">',
            (
                '<animateTransform attributeName="transform" type="translate" '
                f'from="{x} {start_y}" to="{x} {end_y}" '
                f'dur="{duration:.2f}s" begin="{begin:.2f}s" '
                'repeatCount="indefinite" />'
            ),
        ]
        for i, (ch, role) in enumerate(chars):
            y = i * cfg.row_height
            opacity = opacity_for(i, len(chars), role, rng)
            color = stream_color(role, cfg)
            text_parts.append(
                f'<text x="0" y="{y}" fill="{color}" '
                f'opacity="{opacity:.3f}">{esc(ch)}</text>'
            )
        text_parts.append("</g>")
        nodes.append("\n".join(text_parts))

    return nodes


def build_overlay(cfg: MatrixConfig) -> str:
    cx = cfg.width / 2
    panel_w = 850
    panel_h = 145
    panel_x = (cfg.width - panel_w) / 2
    panel_y = (cfg.height - panel_h) / 2
    return f"""
  <g id="identity-panel">
    <rect x="{panel_x:.1f}" y="{panel_y:.1f}" width="{panel_w}" height="{panel_h}" rx="18"
          fill="#020503" fill-opacity="0.72" stroke="{cfg.green}" stroke-opacity="0.45" />
    <text x="{cx:.1f}" y="{panel_y + 43:.1f}" text-anchor="middle"
          class="title" fill="{cfg.text_primary}">Vlad Voropaev · vladthecyborg</text>
    <text x="{cx:.1f}" y="{panel_y + 78:.1f}" text-anchor="middle"
          class="subtitle" fill="{cfg.text_secondary}">I like taking strange questions apart, building tools around them, and sharing what I find.</text>
    <text x="{cx:.1f}" y="{panel_y + 112:.1f}" text-anchor="middle"
          class="micro" fill="{cfg.red}">AI systems · research tooling · local-first experiments · computer vision · visual explanations</text>
  </g>
"""


def build_svg(cfg: MatrixConfig) -> str:
    rng = random.Random(cfg.seed)
    background = "\n  ".join(build_background(rng, cfg))
    streams = "\n  ".join(build_streams(rng, cfg))
    overlay = build_overlay(cfg)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{cfg.width}" height="{cfg.height}" viewBox="0 0 {cfg.width} {cfg.height}" role="img" aria-label="Animated Matrix-style digital rain profile header for Vlad Voropaev">
  <defs>
    <radialGradient id="red-glow" cx="50%" cy="42%" r="70%">
      <stop offset="0%" stop-color="{cfg.red}" stop-opacity="0.13" />
      <stop offset="42%" stop-color="{cfg.red}" stop-opacity="0.035" />
      <stop offset="100%" stop-color="{cfg.bg_fill}" stop-opacity="0" />
    </radialGradient>
    <radialGradient id="green-glow" cx="50%" cy="50%" r="76%">
      <stop offset="0%" stop-color="{cfg.green}" stop-opacity="0.08" />
      <stop offset="100%" stop-color="{cfg.bg_fill}" stop-opacity="0" />
    </radialGradient>
    <filter id="soft-glow" x="-35%" y="-35%" width="170%" height="170%">
      <feGaussianBlur stdDeviation="2.1" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <style>
      text {{
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace;
        font-size: {cfg.font_size}px;
        dominant-baseline: text-before-edge;
      }}
      .title {{ font-size: 32px; font-weight: 700; letter-spacing: 0.01em; }}
      .subtitle {{ font-size: 18px; font-weight: 450; }}
      .micro {{ font-size: 16px; font-weight: 650; letter-spacing: 0.025em; }}
      #streams {{ filter: url(#soft-glow); }}
      #identity-panel {{ filter: url(#soft-glow); }}
    </style>
  </defs>

  <rect width="100%" height="100%" fill="{cfg.bg_fill}" />
  <rect width="100%" height="100%" fill="url(#green-glow)" />
  <rect width="100%" height="100%" fill="url(#red-glow)" />

  <g id="background" opacity="0.9">
  {background}
  </g>

  <g id="streams">
  {streams}
  </g>

  <rect width="100%" height="100%" fill="#000" opacity="0.20" />
  {overlay}
</svg>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Matrix-style README SVG.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("assets/matrix.svg"),
        help="Output SVG path.",
    )
    parser.add_argument("--width", type=int, default=MatrixConfig.width)
    parser.add_argument("--height", type=int, default=MatrixConfig.height)
    parser.add_argument("--seed", type=int, default=MatrixConfig.seed)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = MatrixConfig(width=args.width, height=args.height, seed=args.seed)
    svg = build_svg(cfg)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8")
    print(f"Generated {args.output}")


if __name__ == "__main__":
    main()
