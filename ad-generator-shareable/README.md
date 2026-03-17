# Meta Ad Generator

A Python tool that generates polished Meta ad images in two formats:
- **Vertical** (1080x1920) - Stories/Reels
- **Square** (1080x1080) - Feed

Includes a web UI for live editing and preview.

---

## Quick Start

### 1. Install dependencies
```
pip install pillow requests flask
```

### 2. Run the web UI
```
python app.py
```
Then open http://localhost:5000 in your browser.

### 3. Or run the script directly (generates all hooks as PNGs)
```
python generate_ad.py
```
Output saves to `ad-outputs/`

---

## Customize for Your Brand

Open `generate_ad.py` and update these sections:

### Colors (line ~30)
```python
BG_COLOR      = (125, 143, 117)   # your background color (RGB)
WHITE         = (255, 255, 255)   # body text color
LIME_GREEN    = (181, 217, 122)   # highlight color for dollar amounts + *asterisk* text
```

### Logo
Replace `logo.png` with your own logo file (transparent PNG or WebP works best). If you don't want a logo, set `show_logo=False` in the HOOKS or toggle it off in the web UI.

### Hooks (your ad copy)
Edit the `HOOKS` array in `generate_ad.py`. Each hook has:
```python
{
    "slug":     "unique_name_here",          # used for filenames
    "headline": "LINE ONE\nLINE TWO",        # identity/qualifier text
    "hook":     "THE HOOK\nGOES HERE",        # emotional/curiosity line
}
```

**Formatting rules:**
- Use ALL CAPS (the fonts render best this way)
- Use `\n` for line breaks
- Dollar amounts like `$30K` auto-highlight in your highlight color
- Wrap any word in `*asterisks*` to highlight it: `*FREE*`, `*6X ROI*`

**Optional font size overrides** (only needed if text overflows):
```python
{
    "slug": "long_hook",
    "headline": "...",
    "hook": "...",
    "hook_font_size_vertical": 72,   # default is 82
    "hook_font_size_square":   68,   # default is 90
}
```

### Fonts
The tool uses Google Fonts (auto-downloaded on first run):
- **Oswald Bold** - headlines
- **Barlow Condensed Bold** - hooks

To use different fonts, replace the entries in the `FONTS` dict with your preferred Google Fonts, or drop `.ttf` files directly into the `fonts/` folder and update the file references.

---

## Web UI Features

- Edit headline, hook, and font sizes per ad
- Custom background and highlight colors (color pickers)
- Toggle logo on/off with position offsets
- Upload a photo as a background overlay or centered card
- Live preview of both vertical and square formats
- Download individual images or batch-generate all

---

## How the Hook Formula Works

The best-performing Meta ad hooks follow this pattern:

| Hook Type | Formula | Example |
|---|---|---|
| Pain hook | `[Identity]. [Specific frustration?]` | `$5M Company. Tired of leads that ghost after the first call?` |
| Desire hook | `[Identity]. [Outcome they want?]` | `$4M Agency. Need a predictable pipeline of qualified leads?` |
| Case study | `[Result achieved]. [Bridge question?]` | `We helped a client go from $2M to $4M. Want to be next?` |
| Skeptic-to-believer | `[Identity + ROI]. [Behavior shift]` | `$3M business. 5X ROI from paid ads. Went from skeptical to scaling.` |

**Tips:**
- Lead with a revenue figure or identity qualifier - the reader self-selects
- Pain hooks work best for cold traffic; case study hooks for warm/retargeting
- Specific, non-round numbers feel more believable
- Keep hook text to 3-4 lines max for readability at ad size

---

## File Structure

```
├── README.md           # this file
├── generate_ad.py      # core rendering script
├── app.py              # Flask web UI
├── logo.png            # your logo (replace with yours)
├── fonts/              # auto-downloaded on first run
│   ├── Oswald-Bold.ttf
│   └── BarlowCondensed-Bold.ttf
└── ad-outputs/         # generated PNGs go here
```
