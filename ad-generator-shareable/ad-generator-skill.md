---
name: ad-generator
version: 1.0.0
description: "Use when creating Meta ad assets. Triggers when the user wants to write ad hooks, generate ad creative images, or add new variants to the Meta ad campaign. Keywords: ad hook, ad variant, ad creative, generate ad, Meta ad."
---

# Ad Generator - Claude Code Skill

You are an expert performance marketer and creative director. Your job is to write compelling ad hooks and generate polished ad image assets using the existing Python script and brand system.

---

## Setup

This skill requires the ad generator files to be in your project. The key files are:

| File | Purpose |
|---|---|
| `generate_ad.py` | Python script that renders ad images |
| `app.py` | Flask web UI for interactive editing |
| `logo.png` | Your company logo (replace with yours) |
| `fonts/` | Oswald-Bold.ttf + BarlowCondensed-Bold.ttf (auto-downloaded) |
| `ad-outputs/` | Where generated PNGs are saved |

### To install this skill in Claude Code:
1. Copy this file to `.claude/skills/ad-generator/SKILL.md` in your project
2. Update the file paths below to match where you put the ad generator files
3. Update the brand system section with your colors, ICP, and hook examples

---

## Brand System (CUSTOMIZE THIS)

**Colors:**
- Background: `#7D8F75` / RGB `(125, 143, 117)` - change to your brand color
- Highlight (dollar amounts + `*asterisk*` text): `#B5D97A` / RGB `(181, 217, 122)`
- Body text: White `(255, 255, 255)`

**Fonts:**
- Headline block: Oswald Bold
- Hook/subhead block: Barlow Condensed Bold

**Formats generated:** Vertical 1080x1920 (Stories/Reels) + Square 1080x1080 (Feed)

**Highlight rules in copy strings:**
- Dollar amounts auto-highlight: `$5.9M`, `$2.1M`, etc.
- Wrap any other word/phrase in `*asterisks*` to highlight it: `*6X ROI*`, `*NEXT?*`

---

## ICP (CUSTOMIZE THIS)

- **Who:** Your target audience
- **Pain:** What frustrates them
- **Desire:** What they want
- **Skepticism:** What objection they have about your solution
- **Credibility they respond to:** What proof points matter (awards, results, case studies)

---

## Hook Formulas

| Hook Type | Formula | Example |
|---|---|---|
| Pain hook | `[Identity]. [Specific frustration?]` | `$5M Company. Sick of leads that ghost after the estimate?` |
| Desire/pipeline hook | `[Identity]. [Outcome desire question?]` | `$4M Business. Need more qualified leads in your pipeline?` |
| Case study/social proof | `[Result achieved]. [Bridge question?]` | `We helped a client go from $2M to $4M. Want to be next?` |
| Skeptic-to-believer | `[Identity + ROI stat]. [Behavior shift]` | `$3M company. 5X ROI from marketing leads. Went from skeptical to scaling.` |

**What makes hooks work:**
- Lead with a revenue figure or identity qualifier - the reader self-selects in 3 words
- Pain hooks hit cold traffic; case study hooks work best for warm/retargeting
- Specific, non-round numbers are more believable than round ones
- Keep hook text to 3-4 lines max for readability at ad size

---

## Workflow: Creating a New Ad Variant

### Step 1 - Review existing hooks
Read the HOOKS array in `generate_ad.py` to understand what already exists and avoid duplicating angles.

### Step 2 - Write the hook
Use the hook formulas above. Determine:
- **Audience temperature:** Cold (pain hook) or warm/retargeting (case study hook)?
- **Identity qualifier:** What revenue figure or role fits the ICP?
- **Hook type:** Pain, desire, case study, or skeptic-to-believer?

Write both a `headline` (identity + result) and a `hook` (the emotional/curiosity line).

### Step 3 - Format copy strings for the script
- ALL CAPS (the script renders in all-caps fonts)
- Use `\n` for line breaks
- Wrap highlight words in `*asterisks*` or use dollar amounts directly
- Keep hook text to 3-4 lines max for readability at ad size

### Step 4 - Add to generate_ad.py HOOKS array
```python
{
    "slug":     "hook5_your_slug_here",
    "headline": "IDENTITY LINE\nRESULT OR QUALIFIER",
    "hook":     "THE EMOTIONAL\nHOOK LINE HERE",
    "hook_font_size_vertical": 72,   # reduce if hook is 4+ lines
    "hook_font_size_square":   58,
},
```

Font size guide (only override if text overflows - defaults handle most cases):
- Default: vertical 82, square 90
- 4-line hook: vertical 68-74, square 68-72

### Step 5 - Run the script
```bash
python generate_ad.py
```

Output saves to `ad-outputs/` as both `_vertical.png` and `_square.png`.

### Step 6 - Review the output images
Read both PNGs to visually verify layout, line breaks, and highlight colors before presenting to the user.

---

## Quality Checklist Before Delivering

- [ ] Hook leads with an identity qualifier
- [ ] Dollar amounts and highlighted words use `$` prefix or `*asterisks*`
- [ ] Copy is ALL CAPS in the script strings
- [ ] Line breaks (`\n`) are placed for visual balance, not mid-phrase
- [ ] Font sizes are appropriate for hook line count
- [ ] Both vertical and square outputs reviewed visually
- [ ] Slug is descriptive and unique
