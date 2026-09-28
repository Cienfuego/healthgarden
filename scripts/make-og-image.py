#!/usr/bin/env python3
"""
Generate public/og-image.jpg (1200x630) for Healthgarden link previews.

Run from the repo root:
    python3 scripts/make-og-image.py

It uses the Cormorant Garamond files that Fontsource already installed into
node_modules, so the wordmark matches the site. If those are missing it falls
back to any serif it can find and prints a warning.
"""

from PIL import Image, ImageDraw, ImageFont
import os, sys

# --- paths -----------------------------------------------------------------

SRC = "src/assets/garden-hero.jpg"        # change to whichever photo you want
OUT = "public/og-image.jpg"

FONT_DIR = "node_modules/@fontsource/cormorant-garamond/files"
SERIF_REGULAR = f"{FONT_DIR}/cormorant-garamond-latin-400-normal.woff2"
SERIF_ITALIC  = f"{FONT_DIR}/cormorant-garamond-latin-400-italic.woff2"
SANS_DIR = "node_modules/@fontsource/inter/files"
SANS_REGULAR = f"{SANS_DIR}/inter-latin-500-normal.woff2"

FALLBACK_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FALLBACK_SERIF_ITALIC = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"
FALLBACK_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# --- brand -----------------------------------------------------------------

TEAL_DEEP  = (15, 110, 124)
SAGE       = (122, 155, 118)
WARM_WHITE = (250, 250, 247)

W, H = 1200, 630
SCRIM_OPACITY = 210          # 0-255; higher = more washed out, more readable
TEXT_CX_RATIO = 0.5

def load_font(primary, fallback, size):
    """PIL can't read woff2, so prefer a .ttf/.otf next to it, else fallback."""
    for candidate in (primary.replace(".woff2", ".ttf"),
                      primary.replace(".woff2", ".otf"),
                      primary):
        if os.path.exists(candidate):
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    if os.path.exists(fallback):
        print(f"  note: falling back to {os.path.basename(fallback)}")
        return ImageFont.truetype(fallback, size)
    return ImageFont.load_default()


def draw_tracked(draw, text, font, fill, center_x, y, tracking):
    """Draw letterspaced text centered on center_x."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = center_x - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking


def main():
    if not os.path.exists(SRC):
        sys.exit(f"Source photo not found: {SRC}")

    src = Image.open(SRC).convert("RGB")
    sw, sh = src.size

    # centre-crop to 1200x630 proportions, then resize
    target = W / H
    if sw / sh > target:
        ch = sh
        cw = int(sh * target)
    else:
        cw = sw
        ch = int(sw / target)
    left = (sw - cw) // 2
    top = int((sh - ch) * 0.85)        # bias low so the chair and beds are in frame
    img = src.crop((left, top, left + cw, top + ch)).resize((W, H), Image.LANCZOS)

    # warm-white scrim so the teal type stays readable at thumbnail size
    scrim = Image.new("RGBA", (W, H), WARM_WHITE + (SCRIM_OPACITY,))
    img = Image.alpha_composite(img.convert("RGBA"), scrim).convert("RGB")

    draw = ImageDraw.Draw(img)
    eyebrow_font  = load_font(SANS_REGULAR, FALLBACK_SANS, 22)
    wordmark_font = load_font(SERIF_REGULAR, FALLBACK_SERIF, 118)
    tagline_font  = load_font(SERIF_ITALIC, FALLBACK_SERIF_ITALIC, 52)

    cx = int(W * TEXT_CX_RATIO)
    draw_tracked(draw, "CLINICAL PATIENT ADVOCACY", eyebrow_font, SAGE, cx, 210, 4)

    wm = "Healthgarden"
    wm_w = draw.textlength(wm, font=wordmark_font)
    draw.text((cx - wm_w / 2, 255), wm, font=wordmark_font, fill=TEAL_DEEP)

    tag = "Cultivating thoughtful care."
    tag_w = draw.textlength(tag, font=tagline_font)
    draw.text((cx - tag_w / 2, 400), tag, font=tagline_font, fill=TEAL_DEEP)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, quality=88, optimize=True)
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
