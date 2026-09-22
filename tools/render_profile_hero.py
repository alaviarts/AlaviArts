#!/usr/bin/env python3
"""Render Ali Alavi's restrained, GitHub-compatible motion hero.

This is a pre-rendered GIF. GitHub README cannot execute React or Canvas.
Name stays readable in every frame, with a subtle character-glow sequence.
"""
from __future__ import annotations
import math
import os
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 350
FPS, DURATION = 4, 12
N = FPS * DURATION
OUT = Path(os.environ.get("HERO_OUT", "assets/ali-alavi-hero-motion-v2.gif"))
FONT_PATHS = [
    "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf",
    "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
REGULAR_PATHS = [
    "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    "/usr/share/fonts/opentype/inter/InterDisplay-Regular.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def font(paths: list[str], size: int) -> ImageFont.FreeTypeFont:
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)

NAME_FONT = font(FONT_PATHS, 80)
ROLE_FONT = font(REGULAR_PATHS, 26)
TAG_FONT = font(REGULAR_PATHS, 24)
NAME = "ALI ALAVI"
PHRASES = [
    "Connected organizations.",
    "Coherent projects.",
    "Deeper human understanding.",
]

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def clamp(x: float, lo: float = 0, hi: float = 1) -> float:
    return max(lo, min(hi, x))

def smooth(x: float) -> float:
    x = clamp(x)
    return x * x * (3 - 2 * x)

def phrase_opacity(index: int, t: float) -> float:
    slot = (t / 4) % 3
    distance = ((slot - index + 1.5) % 3) - 1.5
    return 1 - smooth((abs(distance) - .43) / .14)

def base_layer() -> Image.Image:
    image = Image.new("RGBA", (W, H))
    pixels = image.load()
    for y in range(H):
        for x in range(W):
            radial = math.exp(-(((x - 600) / 500) ** 2 + ((y - 162) / 238) ** 2))
            pixels[x, y] = (
                round(7 + radial * 5 + y / H),
                round(11 + radial * 8 + y / H * 3),
                round(20 + radial * 15 + y / H * 4), 255
            )
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(art, "RGBA")
    d.arc((-220, 35, 320, 585), -78, 54, fill=(107, 154, 198, 27), width=1)
    d.arc((950, -285, 1430, 185), 37, 153, fill=(122, 145, 199, 25), width=1)
    d.arc((960, 95, 1330, 455), 184, 300, fill=(117, 172, 210, 23), width=1)
    rnd = random.Random(28)
    for _ in range(92):
        x = rnd.choice((rnd.randrange(14, 310), rnd.randrange(892, 1185)))
        y = rnd.randrange(28, 324)
        d.ellipse((x, y, x + 1.4, y + 1.4),
                  fill=(131, 182, 220, rnd.randint(13, 42)))
    for x in range(28, 1180, 19):
        if 320 < x < 880:
            continue
        y = 324 + 3 * math.sin(x * .027)
        d.ellipse((x, y, x + 1.1, y + 1.1), fill=(105, 156, 202, 40))
    image.alpha_composite(art)
    return image

def points(t: float, side: int) -> list[tuple[float, float]]:
    centers = (
        [(52, 182), (125, 155), (191, 186), (245, 143), (310, 174)]
        if side == 0 else
        [(888, 171), (952, 143), (1014, 185), (1083, 154), (1150, 178)]
    )
    return [
        (x + math.sin(t * .24 + i * 1.2 + side) * 3.5,
         y + math.cos(t * .29 + i * .9 + side) * 4)
        for i, (x, y) in enumerate(centers)
    ]

def draw_network(frame: Image.Image, t: float) -> None:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")
    for side in (0, 1):
        p = points(t, side)
        for i in range(len(p) - 1):
            d.line([p[i], p[i + 1]], fill=(115, 178, 217, 39), width=1)
        d.line([p[0], p[2]], fill=(135, 145, 219, 19), width=1)
        d.line([p[1], p[3]], fill=(97, 183, 196, 20), width=1)
        for i, (x, y) in enumerate(p):
            rad = 2.3 if i in (1, 3) else 1.5
            v = .5 + .5 * math.sin(t * .85 + i * 1.8 + side)
            d.ellipse((x-rad, y-rad, x+rad, y+rad),
                      fill=(147, 204, 231, round(75 + v * 82)))
        phase = ((t * .13) + side * .31) % 1 * (len(p) - 1)
        k = min(int(phase), len(p) - 2)
        f = phase - k
        x = lerp(p[k][0], p[k+1][0], f)
        y = lerp(p[k][1], p[k+1][1], f)
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow, "RGBA").ellipse(
            (x-8, y-8, x+8, y+8), fill=(80, 161, 209, 130))
        layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(9)))
        d = ImageDraw.Draw(layer, "RGBA")
        d.ellipse((x-2.2, y-2.2, x+2.2, y+2.2),
                  fill=(179, 224, 255, 185))
    frame.alpha_composite(layer)

def centered(d, text, y, ff, fill):
    bounds = d.textbbox((0, 0), text, font=ff)
    x = (W - (bounds[2] - bounds[0])) / 2
    d.text((x, y), text, font=ff, fill=fill)

def draw_title(frame: Image.Image, t: float) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    advances = [draw.textlength(ch, font=NAME_FONT) for ch in NAME]
    x = (W - sum(advances)) / 2
    name_y = 84
    for i, char in enumerate(NAME):
        cycle = t if t < 11.1 else -1
        bright = smooth((cycle - .2 - i * .14) / .38) if cycle >= 0 else 1
        highlight = (
            math.exp(-(((cycle - .32 - i * .14) / .34) ** 2))
            if cycle >= 0 else 0
        )
        if char != " ":
            r = round(190 + bright * 53 + highlight * 8)
            g = round(203 + bright * 45 + highlight * 6)
            b = round(219 + bright * 32 + highlight * 3)
            if highlight > .14:
                glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(glow, "RGBA").text(
                    (x, name_y), char, font=NAME_FONT,
                    fill=(110, 181, 255, round(highlight * 112)))
                frame.alpha_composite(glow.filter(ImageFilter.GaussianBlur(9)))
            draw = ImageDraw.Draw(frame, "RGBA")
            draw.text((x, name_y), char, font=NAME_FONT,
                      fill=(min(255, r), min(255, g), min(255, b), 255))
        x += advances[i]
    d = ImageDraw.Draw(frame, "RGBA")
    centered(d, "Product & Systems Architect", 174, ROLE_FONT,
             (192, 211, 226, 241))
    d.line((521, 222, 578, 222), fill=(128, 184, 222, 60), width=1)
    d.ellipse((597, 220, 601, 224), fill=(140, 193, 231, 165))
    d.line((620, 222, 677, 222), fill=(128, 184, 222, 60), width=1)
    for i, phrase in enumerate(PHRASES):
        op = phrase_opacity(i, t)
        if op < .015:
            continue
        shift = round((1 - op) * 5)
        centered(d, phrase, 256 + shift, TAG_FONT,
                 (197, 220, 235, round(240 * op)))
    for i in range(3):
        op = phrase_opacity(i, t)
        xx = 585 + i * 15
        d.ellipse((xx, 303, xx + 3, 306),
                  fill=(126, 184, 219, round(48 + op * 125)))

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    base = base_layer()
    frames = []
    for i in range(N):
        t = i / FPS
        frame = base.copy()
        draw_network(frame, t)
        draw_title(frame, t)
        frames.append(
            frame.convert("RGB").quantize(
                colors=64,
                method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.NONE
            )
        )
    frames[0].save(
        OUT, save_all=True, append_images=frames[1:],
        duration=round(1000 / FPS), loop=0, optimize=True, disposal=2
    )
    print(f"output={OUT} bytes={OUT.stat().st_size} frames={N} dimensions={W}x{H}")

if __name__ == "__main__":
    main()
