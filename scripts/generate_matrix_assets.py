from __future__ import annotations

import random
from html import escape
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

WORDS = [
    "VLAD",
    "VOROPAEV",
    "VOROPAEVV",
    "QUESTIONS",
    "STRANGE",
    "WHY",
    "HOW",
    "WHAT IF",
    "BUILDING",
    "RESEARCH",
    "SYSTEMS",
    "AI AGENTS",
    "LOCAL AI",
    "LOCAL FIRST",
    "CHAT EXPORTER",
    "SOURCE MAP",
    "CLAIM MATRIX",
    "MECHANISMS",
    "EVIDENCE",
    "UNCERTAINTY",
    "VISUAL STORIES",
    "DEEP EXPLANATIONS",
    "EXPLAINERS",
    "PYTHON",
    "TYPESCRIPT",
    "COMPUTER VISION",
    "AUTOMATION",
    "NOTEBOOKS",
    "DATA",
    "DIAGRAMS",
    "SCRIPTS",
    "PROTOTYPES",
    "AUDITABLE",
    "READABLE",
    "STRUCTURE",
    "TOOLS",
    "CODE",
    "GITHUB",
    "README",
    "FINDINGS",
    "BUILD AND SHARE",
]

GLYPHS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~\\"
    "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンヴガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポァィゥェォャュョッー・"
    "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
)

W, H = 1200, 460
CELL_W = 16
CELL_H = 20
COLS = W // CELL_W
ROWS = H // CELL_H
FRAMES = 42
DURATION_MS = 72
SEED = 20260601

GREEN = (0, 255, 65)
GREEN_DIM = (0, 96, 36)
GREEN_HEAD = (197, 255, 214)
RED = (255, 48, 48)
BLACK = (0, 0, 0)
WHITE_GREEN = (228, 255, 235)
MUTED_GREEN = (168, 255, 190)


def get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/Monaco.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def mix(color: tuple[int, int, int], alpha: float) -> tuple[int, int, int]:
    alpha = max(0.0, min(1.0, alpha))
    return tuple(max(0, min(255, int(value * alpha))) for value in color)


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


def create_streams(rng: random.Random) -> list[dict[str, object]]:
    streams: list[dict[str, object]] = []
    for col in rng.sample(range(COLS), min(COLS, 56)):
        word = rng.choice(WORDS).replace(" ", "·") if rng.random() < 0.82 else ""
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


def draw_panel(draw: ImageDraw.ImageDraw, image: Image.Image) -> Image.Image:
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel)
    panel_draw.rounded_rectangle(
        (92, 112, W - 92, H - 92),
        radius=20,
        fill=(0, 12, 3, 192),
        outline=(0, 255, 65, 90),
        width=1,
    )
    panel_draw.rectangle((92, 112, W - 92, 114), fill=(255, 48, 48, 175))
    return Image.alpha_composite(image.convert("RGBA"), panel).convert("RGB")


def draw_identity(draw: ImageDraw.ImageDraw) -> None:
    title_font = get_font(42)
    subtitle_font = get_font(20)
    small_font = get_font(15)
    draw_text_with_glow(draw, (132, 150), "Vlad Voropaev · vladthecyborg", title_font, WHITE_GREEN)
    draw_text_with_glow(draw, (132, 213), "AI systems · research tools · visual explanations", subtitle_font, GREEN)
    draw.text(
        (132, 270),
        "strange questions  ->  mechanisms  ->  useful tools  ->  public artifacts",
        font=small_font,
        fill=MUTED_GREEN,
    )
    draw.text(
        (132, 316),
        "highlight terms: SOURCE MAP · CLAIM MATRIX · LOCAL AI · COMPUTER VISION",
        font=small_font,
        fill=RED,
    )


def generate_frames() -> list[Image.Image]:
    rng = random.Random(SEED)
    mono = get_font(16)
    streams = create_streams(rng)
    frames: list[Image.Image] = []

    for frame_idx in range(FRAMES):
        image = Image.new("RGB", (W, H), BLACK)
        draw = ImageDraw.Draw(image)

        for _ in range(360):
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

        image = draw_panel(draw, image)
        draw = ImageDraw.Draw(image)
        draw_identity(draw)
        frames.append(image)

    return frames


def write_svg() -> None:
    rng = random.Random(SEED)
    chunks: list[str] = []
    for _ in range(700):
        x = rng.randrange(0, W)
        y = rng.randrange(0, H)
        ch = rng.choice(GLYPHS)
        opacity = rng.uniform(0.08, 0.42)
        color = "#00ff41" if rng.random() > 0.16 else "#00451f"
        chunks.append(f'<text x="{x}" y="{y}" fill="{color}" opacity="{opacity:.2f}">{escape(ch)}</text>')

    red_words = ["AI AGENTS", "SOURCE MAP", "CLAIM MATRIX", "LOCAL FIRST", "UNCERTAINTY", "VISUAL STORIES"]
    for i, word in enumerate(red_words):
        chunks.append(f'<text x="{120 + (i % 2) * 480}" y="{70 + i * 54}" class="red">{word}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Matrix-style digital rain profile graphic">
  <rect width="100%" height="100%" fill="#000"/>
  <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, Liberation Mono, monospace" font-size="16">
    {''.join(chunks)}
  </g>
  <rect x="92" y="112" width="1016" height="256" rx="20" fill="#000c03" fill-opacity="0.78" stroke="#00ff41" stroke-opacity="0.45"/>
  <rect x="92" y="112" width="1016" height="2" fill="#ff3030" opacity="0.8"/>
  <text x="132" y="190" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, Liberation Mono, monospace" font-size="42" fill="#e4ffeb">Vlad Voropaev · vladthecyborg</text>
  <text x="132" y="242" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, Liberation Mono, monospace" font-size="22" fill="#00ff41">AI systems · research tools · visual explanations</text>
  <text x="132" y="294" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, Liberation Mono, monospace" font-size="16" fill="#a8ffbe">strange questions -> mechanisms -> useful tools -> public artifacts</text>
  <text x="132" y="334" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, Liberation Mono, monospace" font-size="16" fill="#ff3030">SOURCE MAP · CLAIM MATRIX · LOCAL AI · COMPUTER VISION</text>
  <style>.red{{fill:#ff3030;font-weight:700;letter-spacing:0}}</style>
</svg>'''
    (ASSETS / "matrix-profile.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    frames = generate_frames()
    frames[0].save(
        ASSETS / "matrix-profile.gif",
        save_all=True,
        append_images=frames[1:],
        duration=DURATION_MS,
        loop=0,
        optimize=True,
    )
    frames[0].save(ASSETS / "matrix-preview.png")
    write_svg()


if __name__ == "__main__":
    main()
