"""
Meta Ad Generator
Generates static ad images in vertical (1080x1920) and square (1080x1080) formats.

Usage:
    python generate_ad.py

Requirements:
    pip install pillow requests

Output:
    ad-outputs/
"""

import os
import re
import sys
import requests
from PIL import Image, ImageDraw, ImageFont

# -- Paths -----------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH  = os.path.normpath(os.path.join(SCRIPT_DIR, "logo.png"))
FONT_DIR   = os.path.join(SCRIPT_DIR, "fonts")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "ad-outputs")

os.makedirs(FONT_DIR,   exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -- Brand colors (CUSTOMIZE THESE) ----------------------------------------
BG_COLOR      = (125, 143, 117)   # background color  - change to your brand
WHITE         = (255, 255, 255)   # body text
HIGHLIGHT     = (181, 217, 122)   # highlight for $amounts and *asterisk* text
DIVIDER_COLOR = (255, 255, 255, 80)

# -- Hooks (YOUR AD COPY GOES HERE) ----------------------------------------
# Edit these with your own headlines and hooks.
# Use \n for line breaks, $amounts auto-highlight, *asterisks* for custom highlights.
HOOKS = [
    {
        "slug":     "hook1_pain",
        "headline": "$5M COMPANY.\nYOUR HEADLINE HERE.",
        "hook":     "YOUR HOOK GOES HERE.\nWHAT PAIN POINT\nDOES YOUR AUDIENCE FEEL?",
    },
    {
        "slug":     "hook2_desire",
        "headline": "$4M BUSINESS\nOWNER",
        "hook":     "WHAT IF YOU COULD\nGET THE OUTCOME\nTHEY *ACTUALLY* WANT?",
    },
    {
        "slug":          "hook3_case_study",
        "headline":      "WE HELPED A CLIENT\nGO FROM $2M TO $4M",
        "hook":          "WANT TO BE\n*NEXT?*",
        "hook_font_size_vertical": 130,
        "hook_font_size_square":   110,
    },
]

# -- Canvas sizes ----------------------------------------------------------
FORMATS = {
    "vertical": {"w": 1080, "h": 1920},
    "square":   {"w": 1080, "h": 1080},
}

# -- Font download ---------------------------------------------------------
FONTS = {
    "headline": {
        "api":  "https://fonts.googleapis.com/css2?family=Oswald:wght@700",
        "file": "Oswald-Bold.ttf",
    },
    "bold": {
        "api":  "https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700",
        "file": "BarlowCondensed-Bold.ttf",
    },
}

def download_fonts():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for key, info in FONTS.items():
        dest = os.path.join(FONT_DIR, info["file"])
        if not os.path.exists(dest):
            print(f"Downloading {info['file']}...")
            css = requests.get(info["api"], headers=headers, timeout=15).text
            match = re.search(r'src: url\((https://[^)]+\.ttf)\)', css)
            if not match:
                sys.exit(f"Could not parse font URL for {key}.\n{css[:500]}")
            r = requests.get(match.group(1), headers=headers, timeout=15)
            r.raise_for_status()
            with open(dest, "wb") as f:
                f.write(r.content)
            print(f"  Saved to {dest}")
        else:
            print(f"Font ready: {info['file']}")

def get_font(key, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, FONTS[key]["file"]), size)


# -- Text helpers ----------------------------------------------------------

def colorize_tokens(text, highlight_color=None):
    """Split text into (token, color) pairs. Dollar amounts and *asterisk* text get highlighted."""
    hl = highlight_color or HIGHLIGHT
    tokens = re.split(r'(\$[\w.]+|\*[^*]+\*)', text)
    result = []
    for t in tokens:
        if re.match(r'\$[\w.]+', t):
            result.append((t, hl))
        elif t.startswith('*') and t.endswith('*'):
            result.append((t[1:-1], hl))
        else:
            result.append((t, WHITE))
    return result

def draw_colored_text_centered(draw, text, font, y_center, canvas_w,
                                line_spacing=1.1, highlight_color=None):
    lines = text.split("\n")
    line_h = int(font.size * line_spacing)
    total_h = line_h * len(lines)
    y = y_center - total_h // 2
    for line in lines:
        tokens = colorize_tokens(line, highlight_color)
        total_w = sum(draw.textlength(t, font=font) for t, _ in tokens)
        x = (canvas_w - total_w) / 2
        for tok, color in tokens:
            draw.text((x, y), tok, font=font, fill=color)
            x += draw.textlength(tok, font=font)
        y += line_h
    return total_h


# -- Image overlay helpers -------------------------------------------------

def cover_fit(img, w, h):
    """Resize image to cover (w, h), cropping excess."""
    src_ratio = img.width / img.height
    dst_ratio = w / h
    if src_ratio > dst_ratio:
        new_h = h
        new_w = int(h * src_ratio)
    else:
        new_w = w
        new_h = int(w / src_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    x = (new_w - w) // 2
    y = (new_h - h) // 2
    return img.crop((x, y, x + w, y + h))

def contain_fit(img, w, h):
    """Resize image to fit inside (w, h), preserving aspect ratio."""
    src_ratio = img.width / img.height
    dst_ratio = w / h
    if src_ratio > dst_ratio:
        new_w = w
        new_h = int(w / src_ratio)
    else:
        new_h = h
        new_w = int(h * src_ratio)
    return img.resize((new_w, new_h), Image.LANCZOS)


# -- Main render -----------------------------------------------------------

def render_ad(
    headline, hook, w, h, output_path,
    hook_font_size_override=None,
    bg_color=None,
    highlight_color=None,
    show_logo=True,
    logo_offset_x=0,
    logo_offset_y=0,
    overlay_image=None,
    overlay_mode=None,
    overlay_opacity=12,
):
    actual_bg = bg_color or BG_COLOR

    img  = Image.new("RGB", (w, h), actual_bg)
    draw = ImageDraw.Draw(img, "RGBA")

    is_square = (h == 1080)
    scale = h / 1920

    # -- Background image --------------------------------------------------
    if overlay_image and overlay_mode in ("background", "both"):
        bg_img = cover_fit(overlay_image.convert("RGB"), w, h)
        alpha = int(overlay_opacity / 100 * 255)
        bg_rgba = bg_img.convert("RGBA")
        bg_rgba.putalpha(alpha)
        img.paste(bg_img, (0, 0))
        overlay_layer = Image.new("RGBA", (w, h), actual_bg + (255 - alpha,))
        img = Image.alpha_composite(img.convert("RGBA"), overlay_layer).convert("RGB")
        draw = ImageDraw.Draw(img, "RGBA")

    # -- Logo --------------------------------------------------------------
    logo_bottom = int(245 * scale)
    if show_logo and os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_h = int(155 * scale)
        logo_w = int(logo.width * (logo_h / logo.height))
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        logo_x = (w - logo_w) // 2 + int(logo_offset_x)
        logo_y = int(90 * scale) + int(logo_offset_y)
        img.paste(logo, (logo_x, logo_y), logo)
        logo_bottom = logo_y + logo_h

    # -- Layout zones ------------------------------------------------------
    if is_square:
        headline_font_size = 110
        hook_font_size     = hook_font_size_override if hook_font_size_override else 90
        usable_top    = logo_bottom + 30
        usable_bottom = h - 50
        mid           = usable_top + int((usable_bottom - usable_top) * 0.48)
        headline_y    = usable_top + (mid - usable_top) // 2
        divider_y     = mid
        hook_y        = mid + (usable_bottom - mid) // 2
    else:
        headline_font_size = 138
        hook_font_size     = hook_font_size_override if hook_font_size_override else 82
        headline_y = 700
        divider_y  = 980
        hook_y     = 1260

    # -- Card image (centered photo) ---------------------------------------
    if overlay_image and overlay_mode in ("card", "both"):
        card_pad   = int(60 * scale)
        card_w     = w - card_pad * 2
        card_h     = int(card_w * 0.6)
        card_x     = card_pad
        card_y     = logo_bottom + int(20 * scale)
        card_img   = contain_fit(overlay_image.convert("RGB"), card_w, card_h)
        cx = card_x + (card_w - card_img.width) // 2
        cy = card_y + (card_h - card_img.height) // 2
        img.paste(card_img, (cx, cy))
        draw.rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            outline=(255, 255, 255, 60), width=2
        )
        card_bottom   = card_y + card_h + int(30 * scale)
        remaining     = h - card_bottom - int(40 * scale)
        divider_y     = card_bottom + int(remaining * 0.45)
        headline_y    = card_bottom + int(remaining * 0.20)
        hook_y        = divider_y  + int(remaining * 0.35)
        headline_font_size = int(headline_font_size * 0.72)
        hook_font_size     = int(hook_font_size     * 0.72)

    # -- Headline (auto-shrink if overflow) --------------------------------
    pad_inner     = 60
    headline_font = get_font("headline", headline_font_size)
    tmp_draw      = ImageDraw.Draw(Image.new("RGB", (w, h)))
    while headline_font_size > 40:
        max_line_w = max(
            sum(tmp_draw.textlength(tok, font=headline_font)
                for tok, _ in colorize_tokens(line, highlight_color))
            for line in headline.split("\n")
        )
        if max_line_w <= w - pad_inner * 2:
            break
        headline_font_size -= 4
        headline_font = get_font("headline", headline_font_size)
    draw_colored_text_centered(draw, headline, headline_font, headline_y, w,
                                line_spacing=1.05, highlight_color=highlight_color)

    # -- Divider -----------------------------------------------------------
    draw.line([(60, divider_y), (w - 60, divider_y)], fill=DIVIDER_COLOR, width=2)

    # -- Hook --------------------------------------------------------------
    hook_font = get_font("bold", hook_font_size)
    draw_colored_text_centered(draw, hook, hook_font, hook_y, w,
                                line_spacing=1.15, highlight_color=highlight_color)

    img.save(output_path, "PNG")
    print(f"  Saved: {os.path.relpath(output_path, SCRIPT_DIR)}")


# -- Entry point -----------------------------------------------------------

if __name__ == "__main__":
    print("Meta Ad Generator")
    print("Downloading fonts if needed...")
    download_fonts()
    print()

    total = 0
    for hook_data in HOOKS:
        print(f"Rendering: {hook_data['slug']}")
        for fmt_name, dims in FORMATS.items():
            filename = f"{hook_data['slug']}_{fmt_name}.png"
            out_path = os.path.join(OUTPUT_DIR, filename)
            override_key = f"hook_font_size_{fmt_name}"
            render_ad(
                hook_data["headline"],
                hook_data["hook"],
                dims["w"],
                dims["h"],
                out_path,
                hook_font_size_override=hook_data.get(override_key),
            )
            total += 1

    print(f"\nDone. {total} images saved to:\n  {OUTPUT_DIR}")
