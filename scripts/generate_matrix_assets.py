from __future__ import annotations

import json
import os
import random
import shutil
import textwrap
from html import escape
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DOCS = ROOT / "docs"
CONFIG_PATH = ROOT / "matrix.config.json"
DOCS_CONFIG_PATH = DOCS / "matrix.config.json"
ASSETS.mkdir(exist_ok=True)
DOCS.mkdir(exist_ok=True)

W, H = 1200, 360
CELL_W = 16
CELL_H = 20
COLS = W // CELL_W
ROWS = H // CELL_H
SEED = 20260601
COMMAND_FONT_SIZE = 26
COMMAND_GLYPH_ADVANCE = 16.0
COMMAND_MAX_WIDTH = 820.0

GREEN = (0, 255, 65)
GREEN_DIM = (0, 96, 36)
GREEN_HEAD = (197, 255, 214)
RED = (255, 48, 48)
BLACK = (0, 0, 0)
WHITE_GREEN = (228, 255, 235)
MUTED_GREEN = (168, 255, 190)
PANEL_FILL = (0, 12, 3, 206)
PANEL_OUTLINE = (0, 255, 65, 92)
JAPANESE_GLYPH_SAMPLE = "アあヴ"

GLYPHS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~\\"
    "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンヴガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポァィゥェォャュョッー・"
    "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
)

FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/NotoSansCJK-Regular.ttc",
    "/Library/Fonts/NotoSansJP-Regular.otf",
    "/Library/Fonts/NotoSerifJP-Bold.otf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "/System/Library/Fonts/Monaco.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
]


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def sync_docs_config() -> None:
    if CONFIG_PATH.exists():
        shutil.copyfile(CONFIG_PATH, DOCS_CONFIG_PATH)


def write_public_profile_json(config: dict[str, Any]) -> None:
    profile = config.get("publicProfile", {})
    (DOCS / "public-profile.json").write_text(
        json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def font_renders_distinct_glyphs(font: ImageFont.ImageFont, text: str) -> bool:
    masks = {bytes(font.getmask(glyph)) for glyph in text}
    return len(masks) == len(text)


def get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    fallback_font: ImageFont.FreeTypeFont | ImageFont.ImageFont | None = None
    for path in FONT_CANDIDATES:
        try:
            font = ImageFont.truetype(path, size=size)
        except OSError:
            continue

        if fallback_font is None:
            fallback_font = font
        if font_renders_distinct_glyphs(font, JAPANESE_GLYPH_SAMPLE):
            return font

    if fallback_font is not None:
        return fallback_font
    return ImageFont.load_default()


def mix(color: tuple[int, int, int], alpha: float) -> tuple[int, int, int]:
    alpha = max(0.0, min(1.0, alpha))
    return tuple(max(0, min(255, int(value * alpha))) for value in color)


def rgb(color: tuple[int, int, int]) -> str:
    return f"rgb({color[0]},{color[1]},{color[2]})"


def draw_text_with_glow(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
) -> None:
    x, y = xy
    for radius, intensity in [(6, 0.08), (3, 0.16), (1, 0.28)]:
        glow = mix(fill, intensity)
        for dx in range(-radius, radius + 1, radius):
            for dy in range(-radius, radius + 1, radius):
                if dx == 0 and dy == 0:
                    continue
                draw.text((x + dx, y + dy), text, font=font, fill=glow)
    draw.text((x, y), text, font=font, fill=fill)


def create_streams(rng: random.Random, words: list[str]) -> list[dict[str, object]]:
    streams: list[dict[str, object]] = []
    for col in rng.sample(range(COLS), min(COLS, 42)):
        word = rng.choice(words).replace(" ", "·") if rng.random() < 0.7 else ""
        streams.append(
            {
                "col": col,
                "speed": rng.uniform(0.42, 0.92),
                "offset": rng.randint(-ROWS, ROWS),
                "trail": rng.randint(10, 25),
                "word": word,
                "word_offset": rng.randint(1, 14),
            }
        )
    return streams


def draw_background(draw: ImageDraw.ImageDraw, rng: random.Random, words: list[str], frame_idx: int = 0) -> None:
    mono = get_font(16)
    streams = create_streams(random.Random(SEED), words)

    for _ in range(230):
        x = rng.randrange(0, W // CELL_W) * CELL_W
        y = rng.randrange(0, H // CELL_H) * CELL_H
        ch = rng.choice(GLYPHS)
        alpha = rng.uniform(0.08, 0.24)
        draw.text((x, y), ch, font=mono, fill=mix(GREEN_DIM, alpha))

    for stream in streams:
        head = int((frame_idx * float(stream["speed"]) + int(stream["offset"])) % (ROWS + int(stream["trail"]) + 18)) - int(stream["trail"])
        col = int(stream["col"])
        word = str(stream["word"])
        word_start = int(stream["word_offset"])
        for t in range(int(stream["trail"])):
            row = head - t
            if row < 0 or row >= ROWS:
                continue
            x = col * CELL_W
            y = row * CELL_H
            alpha = 1.0 - (t / max(1, int(stream["trail"])))
            color = mix(GREEN, 0.22 + 0.78 * alpha)
            ch = rng.choice(GLYPHS)

            word_pos = t - word_start
            if word and 0 <= word_pos < len(word):
                ch = word[word_pos]
                color = RED
            elif t == 0:
                color = GREEN_HEAD

            draw.text((x, y), ch, font=mono, fill=color)


def draw_panel(draw: ImageDraw.ImageDraw, image: Image.Image) -> Image.Image:
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel)
    panel_draw.rounded_rectangle(
        (92, 74, W - 92, H - 46),
        radius=18,
        fill=(0, 12, 3, 224),
        outline=PANEL_OUTLINE,
        width=1,
    )
    return Image.alpha_composite(image.convert("RGBA"), panel).convert("RGB")


def terminal_prompt_width(prompt: str) -> float:
    """Return the deterministic width shared by SVG text, reveal mask, and cursor."""
    return min(COMMAND_MAX_WIDTH, max(8.0, len(prompt) * COMMAND_GLYPH_ADVANCE))


def draw_identity(draw: ImageDraw.ImageDraw, config: dict[str, Any]) -> None:
    title_font = get_font(52)
    subtitle_font = get_font(36)
    small_font = get_font(15)
    command_font = get_font(COMMAND_FONT_SIZE)
    title = config["identity"]["title"]
    subtitle = config["identity"]["subtitle"]
    readme_config = config.get("readme", {})
    prompt_max = int(readme_config.get("promptMaxLength", 62))
    prompt = config["terminalPrompts"][0][:prompt_max]

    draw.text((132, 106), config["identity"].get("eyebrow", "terminal://public-profile"), font=small_font, fill=RED)
    draw_text_with_glow(draw, (132, 132), title, title_font, WHITE_GREEN)
    draw_text_with_glow(draw, (132, 202), subtitle, subtitle_font, GREEN)

    draw.rounded_rectangle((132, 250, W - 132, 306), radius=6, fill=(0, 18, 4), outline=(0, 255, 65, 64), width=1)
    draw.text((156, 262), "$", font=command_font, fill=GREEN)
    draw.text((184, 262), prompt, font=command_font, fill=WHITE_GREEN)
    draw.text((184 + terminal_prompt_width(prompt), 262), "▌", font=command_font, fill=GREEN)


def write_preview_png(config: dict[str, Any]) -> None:
    rng = random.Random(SEED)
    image = Image.new("RGB", (W, H), BLACK)
    draw = ImageDraw.Draw(image)
    draw_background(draw, rng, config["highlightWords"], frame_idx=18)
    image = draw_panel(draw, image)
    draw = ImageDraw.Draw(image)
    draw_identity(draw, config)
    image.save(ASSETS / "matrix-preview.png")


def terminal_svg(config: dict[str, Any]) -> str:
    prompt_max = int(config.get("readme", {}).get("promptMaxLength", 62))
    raw_prompts = [prompt[:prompt_max] for prompt in config["terminalPrompts"]]
    total = 5.2 * len(raw_prompts)
    lines: list[str] = []
    cursor_key_times: list[float] = []
    cursor_x_values: list[float] = []
    prompt_x = 184
    prompt_y = 286

    for idx, raw_prompt in enumerate(raw_prompts):
        prompt = escape(raw_prompt)
        prompt_width = terminal_prompt_width(raw_prompt)
        start = idx * 5.2 / total
        type_end = (idx * 5.2 + 1.55) / total
        hold_end = (idx * 5.2 + 3.78) / total
        erase_end = (idx * 5.2 + 4.95) / total
        end = min(1.0, (idx * 5.2 + 5.2) / total)
        key_times = f"0;{start:.5f};{type_end:.5f};{hold_end:.5f};{erase_end:.5f};{end:.5f};1"
        opacity_values = "0;0;1;1;1;0;0"
        # The text reveal and cursor must travel over the same distance.
        # Using the full terminal width here lets glyphs appear ahead of the
        # cursor whenever the command is shorter than the terminal.
        width_values = f"0;0;{prompt_width:.1f};{prompt_width:.1f};0;0;0"
        clip_id = f"terminal-clip-{idx}"
        lines.append(
            f'''<clipPath id="{clip_id}"><rect x="{prompt_x}" y="{prompt_y - 26}" width="0" height="38"><animate attributeName="width" dur="{total:.1f}s" repeatCount="indefinite" values="{width_values}" keyTimes="{key_times}" /></rect></clipPath>'''
        )
        lines.append(
            f'''<text x="{prompt_x}" y="{prompt_y}" class="command" textLength="{prompt_width:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#{clip_id})" opacity="0">{prompt}<animate attributeName="opacity" dur="{total:.1f}s" repeatCount="indefinite" values="{opacity_values}" keyTimes="{key_times}" /></text>'''
        )

        for key_time, cursor_x in [
            (start, float(prompt_x)),
            (type_end, prompt_x + prompt_width),
            (hold_end, prompt_x + prompt_width),
            (erase_end, float(prompt_x)),
            (end, float(prompt_x)),
        ]:
            if cursor_key_times and abs(cursor_key_times[-1] - key_time) < 0.00001:
                cursor_x_values[-1] = cursor_x
                continue
            cursor_key_times.append(key_time)
            cursor_x_values.append(cursor_x)

    cursor_key_times_str = ";".join(f"{key_time:.5f}" for key_time in cursor_key_times)
    cursor_x_values_str = ";".join(f"{cursor_x:.1f}" for cursor_x in cursor_x_values)
    lines.append(
        f'''<text x="{prompt_x}" y="{prompt_y}" class="cursor">▌<animate attributeName="x" dur="{total:.1f}s" repeatCount="indefinite" values="{cursor_x_values_str}" keyTimes="{cursor_key_times_str}" /><animate attributeName="opacity" dur="1.05s" repeatCount="indefinite" values="1;1;0;0;1" keyTimes="0;0.48;0.49;0.98;1" /></text>'''
    )
    return "\n".join(lines)


def write_svg(config: dict[str, Any]) -> None:
    rng = random.Random(SEED)
    words = config["highlightWords"]
    chunks: list[str] = []

    for _ in range(430):
        x = rng.randrange(0, W)
        y = rng.randrange(0, H)
        ch = rng.choice(GLYPHS)
        opacity = rng.uniform(0.08, 0.38)
        color = "#00ff41" if rng.random() > 0.16 else "#00451f"
        chunks.append(f'<text x="{x}" y="{y}" fill="{color}" opacity="{opacity:.2f}">{escape(ch)}</text>')

    for i in range(32):
        x = rng.randrange(0, W)
        start_y = rng.randrange(-H, H)
        speed = rng.uniform(7.0, 14.5)
        stream_words = rng.choice(words).replace(" ", "·") if rng.random() < 0.75 else ""
        glyphs = [rng.choice(GLYPHS) for _ in range(18)]
        if stream_words:
            insert_at = rng.randrange(3, 12)
            for pos, ch in enumerate(stream_words[:10]):
                if insert_at + pos < len(glyphs):
                    glyphs[insert_at + pos] = ch
        glyph_lines = []
        for j, ch in enumerate(glyphs):
            color = "#ff3030" if ch in stream_words else ("#c5ffd6" if j == 0 else "#00ff41")
            opacity = max(0.12, 1.0 - j * 0.052)
            glyph_lines.append(f'<text x="0" y="{j * 20}" fill="{color}" opacity="{opacity:.2f}">{escape(ch)}</text>')
        chunks.append(
            f'''<g transform="translate({x},{start_y})">{''.join(glyph_lines)}<animateTransform attributeName="transform" type="translate" from="{x} {start_y}" to="{x} {H + 120}" dur="{speed:.2f}s" begin="-{rng.uniform(0, speed):.2f}s" repeatCount="indefinite" /></g>'''
        )

    title = escape(config["identity"]["title"])
    subtitle = escape(config["identity"]["subtitle"])
    eyebrow = escape(config["identity"].get("eyebrow", "terminal://public-profile"))
    terminal = terminal_svg(config)

    style = textwrap.dedent(
        f"""
        .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Noto Sans CJK JP', 'Noto Sans Mono CJK JP', monospace; }}
        .title {{ font-size: 52px; font-weight: 800; fill: #eafff0; filter: url(#glow); }}
        .subtitle {{ font-size: 36px; font-weight: 700; fill: #00ff41; }}
        .eyebrow {{ font-size: 14px; fill: #ff3030; font-weight: 700; }}
        .command {{ font-size: {COMMAND_FONT_SIZE}px; fill: #eafff0; }}
        .prompt {{ font-size: {COMMAND_FONT_SIZE}px; fill: #00ff41; font-weight: 700; }}
        .cursor {{ font-size: {COMMAND_FONT_SIZE}px; fill: #00ff41; }}
        """
    ).strip()

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Matrix-style terminal profile for Vlad Voropaev">
  <defs>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="2.5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <radialGradient id="centerGlow" cx="50%" cy="48%" r="55%">
      <stop offset="0%" stop-color="#00ff41" stop-opacity="0.13" />
      <stop offset="55%" stop-color="#00ff41" stop-opacity="0.035" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0" />
    </radialGradient>
    <style>{style}</style>
  </defs>
  <rect width="100%" height="100%" fill="#000000" />
  <rect width="100%" height="100%" fill="url(#centerGlow)" />
  <g class="mono" font-size="16">{''.join(chunks)}</g>
  <rect x="92" y="74" width="1016" height="240" rx="18" fill="#000c03" fill-opacity="0.88" stroke="#00ff41" stroke-opacity="0.36" stroke-width="1" />
  <g class="mono">
    <text x="132" y="106" class="eyebrow">{eyebrow}</text>
    <text x="132" y="160" class="title">{title}</text>
    <text x="132" y="220" class="subtitle">{subtitle}</text>
    <rect x="132" y="248" width="936" height="56" rx="6" fill="#00ff41" fill-opacity="0.045" stroke="#00ff41" stroke-opacity="0.22" />
    <text x="156" y="286" class="prompt">$</text>
    {terminal}
  </g>
</svg>
'''
    (ASSETS / "matrix-profile.svg").write_text(svg, encoding="utf-8")


def write_open_live_svg(config: dict[str, Any]) -> None:
    label = "open developer matrix"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="286" height="40" viewBox="0 0 286 40" role="img" aria-label="Open interactive Matrix developer profile">
  <rect width="286" height="40" rx="6" fill="#000c03" stroke="#00ff41" stroke-opacity="0.48" />
  <text x="22" y="26" fill="#00ff41" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="15">$</text>
  <text x="44" y="26" fill="#eafff0" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="15">{escape(label)}</text>
</svg>
'''
    (ASSETS / "open-live-version.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    config = load_config()
    sync_docs_config()
    write_public_profile_json(config)
    write_svg(config)
    if os.environ.get("MATRIX_SKIP_RASTER_PREVIEW") != "1":
        write_preview_png(config)
    write_open_live_svg(config)


if __name__ == "__main__":
    main()
