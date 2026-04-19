"""
Generate PNG variations of the Free To Build logo for social media.
Draws primitives with Pillow so no SVG renderer is required.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import os

OUT = Path(__file__).resolve().parents[1] / "assets"
OUT.mkdir(exist_ok=True)

# Supersample factor for smooth anti-aliased edges
SSAA = 2


def save_png(img: Image.Image, filename: str, final_size):
    """Downsample from supersampled canvas and save as PNG."""
    if isinstance(final_size, int):
        final_size = (final_size, final_size)
    out = img.resize(final_size, Image.LANCZOS)
    if out.mode == "RGBA":
        out = out.convert("RGB")
    out.save(OUT / filename, "PNG", optimize=True)
    print(f"  wrote {filename} ({final_size[0]}x{final_size[1]})")

# Brand colors
BG_DARK = (10, 10, 10)
BG_CREAM = (245, 242, 234)
ACCENT = (255, 87, 34)
ACCENT_2 = (255, 183, 3)
FG = (245, 242, 234)
FG_DIM = (168, 161, 150)

# -------------------- font loading --------------------
def load_font(candidates, size):
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()

# Windows-friendly fallbacks (bold/black sans)
DISPLAY_FONTS = [
    "ArchivoBlack-Regular.ttf",
    "Archivo Black",
    "Impact.ttf",
    "impact.ttf",
    "AntonRegular.ttf",
    "arialbd.ttf",
    "arial.ttf",
]
BODY_FONTS = [
    "Inter-Bold.ttf",
    "seguisb.ttf",
    "segoeuib.ttf",
    "arialbd.ttf",
    "arial.ttf",
]

# -------------------- primitives --------------------
def draw_hashtag(draw: ImageDraw.ImageDraw, cx, y_top, font,
                  accent=None, to_color=None, build_color=None):
    """
    Draw '#FREETOBUILD' on one line centered at cx, with three parts:
      '#FREE'  -> accent
      'TO'     -> to_color (highlight)
      'BUILD'  -> build_color
    Returns (height, y_bottom).
    Defaults: #FREE and BUILD in accent (orange), TO in white.
    """
    accent = accent or ACCENT
    to_color = to_color or (255, 255, 255)
    build_color = build_color or accent

    parts = [("#FREE", accent), ("TO", to_color), ("BUILD", build_color)]
    full = "".join(p[0] for p in parts)
    b = draw.textbbox((0, 0), full, font=font)
    full_w = b[2] - b[0]
    full_h = b[3] - b[1]

    part_widths = [draw.textbbox((0, 0), t, font=font)[2] for t, _ in parts]

    x = cx - full_w // 2 - b[0]
    for (text, color), pw in zip(parts, part_widths):
        draw.text((x, y_top - b[1]), text, fill=color, font=font)
        x += pw

    return full_h, y_top + full_h


def draw_mark(draw: ImageDraw.ImageDraw, cx, cy, size, color, stroke_ratio=None):
    """
    Render the Free to Build mark, matching favicon.svg exactly.
    SVG viewBox is 40x40; mark uses these paths:
      triangle: M4 34 L20 6 L36 34 Z
      door:     M14 34 V22 H26 V34
      stroke-width=3, stroke-linejoin=round
    `size` maps to the full 40-unit SVG viewBox (so the visual logo fits in ~size*0.8).
    """
    # Scale factor: 1 SVG unit = (size/40) pixels.
    u = size / 40.0
    x0 = cx - size / 2
    y0 = cy - size / 2

    def P(sx, sy):
        return (x0 + sx * u, y0 + sy * u)

    stroke = max(2, int(round(3 * u)))

    # Triangle — closed path. Use Pillow's multi-point line with curve joints, and
    # repeat the first segment at the end so every vertex gets a rounded join.
    tri = [P(4, 34), P(20, 6), P(36, 34), P(4, 34), P(20, 6)]
    draw.line(tri, fill=color, width=stroke, joint="curve")

    # Door — open path with rounded joins at the two top corners; bottom ends
    # meet the triangle's baseline with plain butt caps (no nubs).
    door = [P(14, 34), P(14, 22), P(26, 22), P(26, 34)]
    draw.line(door, fill=color, width=stroke, joint="curve")


def rounded_square(size, bg, radius_ratio=0.18):
    # Plain square background (no rounded corners).
    return Image.new("RGBA", (size, size), bg + (255,))


def add_glow(img, cx, cy, radius, color, alpha=110):
    """Soft radial glow layered under the logo."""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    steps = 24
    for i in range(steps, 0, -1):
        a = int(alpha * (i / steps) ** 2 / 3)
        rr = int(radius * (i / steps))
        gd.ellipse(
            [cx - rr, cy - rr, cx + rr, cy + rr],
            fill=(color[0], color[1], color[2], a),
        )
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.08))
    img.alpha_composite(glow)


# -------------------- variations --------------------

def mark_only(size, bg, fg, filename, square=True, glow_color=None):
    S = size * SSAA
    if square:
        img = rounded_square(S, bg).convert("RGBA")
    else:
        img = Image.new("RGBA", (S, S), bg + (255,))
    # Optical center: lift mark slightly because the triangle's wide base is visually heavy.
    cx = S // 2
    cy = S // 2 - int(S * 0.03)
    if glow_color:
        # Keep glow inside the inscribed circle so profile pic crops don't clip it oddly.
        add_glow(img, cx, cy, int(S * 0.42), glow_color, alpha=140)
    d = ImageDraw.Draw(img)
    draw_mark(d, cx, cy, int(S * 0.62), fg)
    save_png(img, filename, size)


def profile_with_wordmark(size, bg, mark_color, text_color, filename, accent_color=None):
    S = size * SSAA
    img = rounded_square(S, bg).convert("RGBA")
    if accent_color:
        add_glow(img, int(S * 0.25), int(S * 0.25), int(S * 0.6), accent_color, alpha=120)

    d = ImageDraw.Draw(img)

    # Compose mark + stacked wordmark as a single block, vertically centered
    # so there's equal padding top and bottom.
    mark_size = int(S * 0.48)
    font_big = load_font(DISPLAY_FONTS, int(S * 0.12))
    lines = ["FREE", "TO", "BUILD"]
    line_gap = int(S * 0.012)

    # Measure total block height: mark + gap + 3 lines
    line_bboxes = [d.textbbox((0, 0), ln, font=font_big) for ln in lines]
    line_heights = [b[3] - b[1] for b in line_bboxes]
    text_block_h = sum(line_heights) + line_gap * (len(lines) - 1)

    mark_to_text_gap = int(S * 0.03)
    block_h = mark_size + mark_to_text_gap + text_block_h
    block_top = (S - block_h) // 2

    mark_cy = block_top + mark_size // 2
    draw_mark(d, S // 2, mark_cy, mark_size, mark_color)

    y = block_top + mark_size + mark_to_text_gap
    for ln, bbox, h in zip(lines, line_bboxes, line_heights):
        w = bbox[2] - bbox[0]
        x = (S - w) // 2 - bbox[0]
        color = accent_color if accent_color and ln == "TO" else text_color
        d.text((x, y - bbox[1]), ln, fill=color, font=font_big)
        y += h + line_gap

    save_png(img, filename, size)


def hashtag_badge(size, filename):
    S = size * SSAA
    img = rounded_square(S, BG_DARK).convert("RGBA")
    add_glow(img, int(S * 0.85), int(S * 0.15), int(S * 0.7), ACCENT, alpha=150)
    add_glow(img, int(S * 0.1), int(S * 0.9), int(S * 0.6), ACCENT_2, alpha=90)

    d = ImageDraw.Draw(img)

    # Two-line hashtag with three colors so "TO" stands out:
    #   line 1: "#FREE" (orange)
    #   line 2: "TO" (yellow) + "BUILD" (cream), rendered as one baseline
    mark_size = int(S * 0.26)
    font = load_font(DISPLAY_FONTS, int(S * 0.18))
    line_gap = int(S * 0.02)
    mark_to_text_gap = int(S * 0.04)

    line1 = "#FREE"
    line2_parts = [("TO", (255, 255, 255)), ("BUILD", FG)]

    b1 = d.textbbox((0, 0), line1, font=font)
    h1 = b1[3] - b1[1]
    w1 = b1[2] - b1[0]

    # Measure line 2 as concatenation for correct width and baseline alignment.
    full2 = "".join(p[0] for p in line2_parts)
    b2 = d.textbbox((0, 0), full2, font=font)
    h2 = b2[3] - b2[1]
    w2 = b2[2] - b2[0]
    # Per-part widths for placement
    part_widths = [d.textbbox((0, 0), p[0], font=font)[2] for p in line2_parts]

    text_h = h1 + line_gap + h2
    block_h = mark_size + mark_to_text_gap + text_h
    block_top = (S - block_h) // 2

    draw_mark(d, S // 2, block_top + mark_size // 2, mark_size, ACCENT)

    # Line 1
    y = block_top + mark_size + mark_to_text_gap
    x = (S - w1) // 2 - b1[0]
    d.text((x, y - b1[1]), line1, fill=ACCENT, font=font)

    # Line 2 — draw each part at its own x, sharing baseline
    y += h1 + line_gap
    x = (S - w2) // 2 - b2[0]
    for (text, color), pw in zip(line2_parts, part_widths):
        d.text((x, y - b2[1]), text, fill=color, font=font)
        x += pw

    save_png(img, filename, size)


def banner(width, height, filename, pad_ratio=0.06):
    """Horizontal banner (X / LinkedIn): mark left, headline stack right."""
    W = width * SSAA
    H = height * SSAA
    img = Image.new("RGBA", (W, H), BG_DARK + (255,))

    # Grid overlay
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    step = max(40 * SSAA, H // 14)
    line_col = (245, 242, 234, 16)
    for x in range(0, W, step):
        gd.line([(x, 0), (x, H)], fill=line_col, width=1 * SSAA)
    for y in range(0, H, step):
        gd.line([(0, y), (W, y)], fill=line_col, width=1 * SSAA)
    img.alpha_composite(grid)

    # Glows
    add_glow(img, int(W * 0.18), int(H * 0.3), int(H * 1.4), ACCENT, alpha=170)
    add_glow(img, int(W * 0.95), int(H * 1.0), int(H * 1.2), ACCENT_2, alpha=80)

    d = ImageDraw.Draw(img)

    pad_x = int(W * pad_ratio)

    # Mark block (left), vertically centered
    mark_size = int(H * 0.58)
    mark_cx = pad_x + mark_size // 2
    mark_cy = H // 2
    draw_mark(d, mark_cx, mark_cy, mark_size, ACCENT)

    # Text block starts after mark + gap
    text_x = mark_cx + mark_size // 2 + int(W * 0.04)
    available_w = W - text_x - pad_x

    headline = "BUILD WHERE YOU STAND."
    sub_line = "No permits. No fees. Just build."
    tag_line = "#FREETOBUILD"

    # Fit headline to available width
    fit_size = int(H * 0.32)
    headline_font = load_font(DISPLAY_FONTS, fit_size)
    while fit_size > 20:
        f = load_font(DISPLAY_FONTS, fit_size)
        b = d.textbbox((0, 0), headline, font=f)
        if (b[2] - b[0]) <= available_w:
            headline_font = f
            break
        fit_size -= 4 * SSAA

    sub_font = load_font(BODY_FONTS, max(14, int(H * 0.075)))
    tag_font = load_font(DISPLAY_FONTS, max(16, int(H * 0.09)))

    b1 = d.textbbox((0, 0), headline, font=headline_font)
    b2 = d.textbbox((0, 0), sub_line, font=sub_font)
    b3 = d.textbbox((0, 0), tag_line, font=tag_font)

    h1 = b1[3] - b1[1]
    h2 = b2[3] - b2[1]
    h3 = b3[3] - b3[1]

    gap1 = int(H * 0.045)
    gap2 = int(H * 0.035)
    total = h1 + h2 + h3 + gap1 + gap2
    y = (H - total) // 2

    d.text((text_x, y - b1[1]), headline, fill=FG, font=headline_font)
    y += h1 + gap1
    d.text((text_x, y - b2[1]), sub_line, fill=FG_DIM, font=sub_font)
    y += h2 + gap2
    # Tag: draw three-color hashtag aligned left to text_x.
    # draw_hashtag centers on cx; compute cx so the left edge lands at text_x.
    tag_full_w = d.textbbox((0, 0), tag_line, font=tag_font)[2]
    tag_cx = text_x + tag_full_w // 2
    draw_hashtag(d, tag_cx, y, tag_font)

    save_png(img, filename, (width, height))


def youtube_banner(filename):
    """
    YouTube channel banner: 2560x1440.
    Content must fit the TV/mobile-safe center zone (~1546x423 centered).
    Design: centered vertical stack — mark, giant headline, tagline, hashtag.
    """
    width, height = 2560, 1440
    W = width * SSAA
    H = height * SSAA
    img = Image.new("RGBA", (W, H), BG_DARK + (255,))

    # Grid
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    step = int(80 * SSAA)
    line_col = (245, 242, 234, 14)
    for x in range(0, W, step):
        gd.line([(x, 0), (x, H)], fill=line_col, width=1 * SSAA)
    for y in range(0, H, step):
        gd.line([(0, y), (W, y)], fill=line_col, width=1 * SSAA)
    img.alpha_composite(grid)

    # Big dramatic glows
    add_glow(img, int(W * 0.3), int(H * 0.5), int(W * 0.35), ACCENT, alpha=200)
    add_glow(img, int(W * 0.75), int(H * 0.5), int(W * 0.25), ACCENT_2, alpha=90)

    d = ImageDraw.Draw(img)

    # Safe-zone: centered box ~1546x423. Design content to fit here.
    safe_w = 1546 * SSAA
    safe_h = 423 * SSAA
    safe_cx = W // 2
    safe_cy = H // 2

    # Headline, hashtag, mark stacked horizontally within safe zone.
    headline = "BUILD WHERE YOU STAND."
    tag_line = "#FREETOBUILD"

    headline_font = load_font(DISPLAY_FONTS, int(safe_h * 0.32))
    tag_font = load_font(DISPLAY_FONTS, int(safe_h * 0.14))

    b1 = d.textbbox((0, 0), headline, font=headline_font)
    b2 = d.textbbox((0, 0), tag_line, font=tag_font)
    h1 = b1[3] - b1[1]
    h2 = b2[3] - b2[1]

    mark_size = int(safe_h * 0.5)
    gap_mark_text = int(safe_h * 0.06)
    gap_head_tag = int(safe_h * 0.06)

    # Total stack: mark + gap + headline + gap + tag
    stack_h = mark_size + gap_mark_text + h1 + gap_head_tag + h2
    top = safe_cy - stack_h // 2

    # Mark
    draw_mark(d, safe_cx, top + mark_size // 2, mark_size, ACCENT)

    # Headline
    y = top + mark_size + gap_mark_text
    w1 = b1[2] - b1[0]
    d.text((safe_cx - w1 // 2 - b1[0], y - b1[1]), headline, fill=FG, font=headline_font)

    # Hashtag
    y += h1 + gap_head_tag
    draw_hashtag(d, safe_cx, y, tag_font)

    save_png(img, filename, (width, height))


# -------------------- run --------------------
if __name__ == "__main__":
    print("Generating logo variations...")

    # 1) Mark only, dark background — classic profile pic
    for s in (1024, 512, 400, 200):
        mark_only(s, BG_DARK, ACCENT, f"mark-dark-{s}.png", glow_color=ACCENT)

    # 1b) Mark only, dark background, NO glow — matches the raw SVG exactly
    for s in (1024, 512, 400, 200):
        mark_only(s, BG_DARK, ACCENT, f"mark-dark-plain-{s}.png", glow_color=None)

    # 2) Mark only, orange background — high-impact alternate
    for s in (1024, 512):
        mark_only(s, ACCENT, BG_DARK, f"mark-orange-{s}.png")

    # 3) Mark only, cream background — light-mode alternate
    for s in (1024, 512):
        mark_only(s, BG_CREAM, BG_DARK, f"mark-cream-{s}.png")

    # 4) Profile with stacked wordmark
    for s in (1024, 512):
        profile_with_wordmark(
            s, BG_DARK, ACCENT, FG,
            f"profile-wordmark-dark-{s}.png",
            accent_color=ACCENT,
        )

    # 5) Hashtag badge — for story avatars, sticker-style posts
    for s in (1024, 512):
        hashtag_badge(s, f"hashtag-{s}.png")

    # 6) Banners (X/Twitter, LinkedIn-ish, YouTube-safe)
    banner(1500, 500, "banner-x-1500x500.png", pad_ratio=0.07)
    banner(1584, 396, "banner-linkedin-1584x396.png", pad_ratio=0.06)
    youtube_banner("banner-youtube-2560x1440.png")

    print("\nDone. Files in:", OUT)
