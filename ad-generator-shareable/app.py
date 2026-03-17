"""
Meta Ad Generator - Web UI
Run: python app.py
Then open: http://localhost:5000
"""

import base64
import io
import os
import tempfile
import webbrowser
from threading import Timer

from flask import Flask, jsonify, request
from PIL import Image

import generate_ad as gen

app = Flask(__name__)

# -- Helpers ---------------------------------------------------------------

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def b64_to_image(b64_str):
    data = base64.b64decode(b64_str.split(",")[-1])
    return Image.open(io.BytesIO(data))

def render_to_b64(headline, hook, w, h, **kwargs):
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()
    try:
        gen.render_ad(headline, hook, w, h, tmp.name, **kwargs)
        with open(tmp.name, "rb") as f:
            return base64.b64encode(f.read()).decode()
    finally:
        os.unlink(tmp.name)

def kwargs_from_card(card):
    """Extract render_ad kwargs from a card dict sent by the frontend."""
    kw = {}
    if card.get("bg_color"):
        kw["bg_color"] = hex_to_rgb(card["bg_color"])
    if card.get("highlight_color"):
        kw["highlight_color"] = hex_to_rgb(card["highlight_color"])
    kw["show_logo"]       = card.get("show_logo", True)
    kw["logo_offset_x"]   = int(card.get("logo_offset_x", 0))
    kw["logo_offset_y"]   = int(card.get("logo_offset_y", 0))
    kw["overlay_opacity"]  = int(card.get("overlay_opacity", 12))
    if card.get("image_b64") and card.get("image_mode", "none") != "none":
        kw["overlay_image"] = b64_to_image(card["image_b64"])
        kw["overlay_mode"]  = card["image_mode"]
    return kw

def kwargs_for_format(card, fmt_name):
    kw = kwargs_from_card(card)
    size_key = f"hook_font_size_{fmt_name}"
    if card.get(size_key):
        kw["hook_font_size_override"] = int(card[size_key])
    return kw


# -- HTML ------------------------------------------------------------------

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ad Generator</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #1a1f1a; color: #e8f0e8;
    min-height: 100vh; padding: 32px 24px;
  }
  .top-bar {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 32px; padding-bottom: 20px; border-bottom: 1px solid #2e3a2e;
  }
  .top-bar h1 { font-size: 22px; font-weight: 700; color: #b5d97a; }
  .top-bar span { font-size: 13px; color: #6b806b; }
  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(580px, 1fr));
    gap: 24px; margin-bottom: 32px;
  }
  .card {
    background: #232b23; border: 1px solid #2e3a2e;
    border-radius: 12px; padding: 24px;
  }
  .card-title {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; color: #6b806b; margin-bottom: 16px;
  }
  .field { margin-bottom: 14px; }
  .field label {
    display: block; font-size: 12px; font-weight: 600; color: #9ab89a;
    margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px;
  }
  .field textarea, .field input[type=number], .field input[type=text] {
    width: 100%; background: #1a1f1a; border: 1px solid #2e3a2e;
    border-radius: 6px; color: #e8f0e8; font-size: 14px; padding: 10px 12px;
    resize: vertical; font-family: 'SF Mono','Cascadia Code',monospace;
    transition: border-color 0.15s; line-height: 1.5;
  }
  .field textarea:focus, .field input:focus {
    outline: none; border-color: #b5d97a;
  }
  .field textarea { min-height: 72px; }
  .hint { font-size: 11px; color: #4a5e4a; margin-top: 4px; }
  .hint b { color: #b5d97a; }
  .row { display: flex; gap: 14px; }
  .row .field { flex: 1; }
  .section-label {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; color: #4a5e4a; margin: 18px 0 12px;
    padding-top: 16px; border-top: 1px solid #2a342a;
  }
  .color-row { display: flex; gap: 14px; }
  .color-field { flex: 1; }
  .color-field label {
    display: block; font-size: 12px; font-weight: 600; color: #9ab89a;
    margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px;
  }
  .color-wrap {
    display: flex; align-items: center; gap: 10px;
    background: #1a1f1a; border: 1px solid #2e3a2e;
    border-radius: 6px; padding: 6px 10px;
  }
  .color-wrap input[type=color] {
    width: 32px; height: 32px; border: none; background: none;
    cursor: pointer; padding: 0; border-radius: 4px;
  }
  .color-wrap .hex-val {
    font-size: 13px; font-family: monospace; color: #9ab89a;
  }
  .logo-row { display: flex; gap: 14px; align-items: flex-end; }
  .logo-row .field { flex: 1; }
  .checkbox-row {
    display: flex; align-items: center; gap: 8px; margin-bottom: 14px;
  }
  .checkbox-row input[type=checkbox] {
    width: 16px; height: 16px; accent-color: #b5d97a; cursor: pointer;
  }
  .checkbox-row label {
    font-size: 13px; color: #9ab89a; cursor: pointer;
  }
  .upload-area {
    border: 1px dashed #3e4e3e; border-radius: 8px; padding: 16px;
    text-align: center; cursor: pointer; transition: border-color 0.15s;
    color: #6b806b; font-size: 13px; position: relative;
  }
  .upload-area:hover { border-color: #b5d97a; color: #b5d97a; }
  .upload-area input[type=file] {
    position: absolute; inset: 0; opacity: 0; cursor: pointer;
  }
  .upload-thumb {
    width: 100%; max-height: 120px; object-fit: cover;
    border-radius: 6px; margin-top: 10px; display: none;
  }
  .img-mode-row {
    display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap;
  }
  .img-mode-btn {
    flex: 1; min-width: 80px; padding: 7px 10px;
    background: #1a1f1a; border: 1px solid #2e3a2e;
    border-radius: 6px; color: #6b806b; font-size: 12px;
    font-weight: 600; cursor: pointer; text-align: center;
    transition: all 0.15s;
  }
  .img-mode-btn.active { border-color: #b5d97a; color: #b5d97a; background: #1e2b1e; }
  .opacity-row { margin-top: 10px; }
  .opacity-row label { font-size: 12px; color: #6b806b; display: flex; justify-content: space-between; }
  .opacity-row input[type=range] { width: 100%; accent-color: #b5d97a; margin-top: 4px; }
  .btn-generate {
    width: 100%; padding: 12px; background: #b5d97a; color: #1a1f1a;
    border: none; border-radius: 8px; font-size: 14px; font-weight: 700;
    cursor: pointer; margin-top: 6px; transition: background 0.15s, transform 0.1s;
  }
  .btn-generate:hover { background: #c8e896; }
  .btn-generate:active { transform: scale(0.98); }
  .btn-generate:disabled { background: #3a4a3a; color: #6b806b; cursor: not-allowed; }
  .spinner { display: none; }
  .btn-generate.loading .spinner { display: inline; }
  .status { font-size: 12px; color: #6b806b; margin-top: 8px; min-height: 16px; }
  .status.ok  { color: #b5d97a; }
  .status.err { color: #e07070; }
  .previews { display: flex; gap: 16px; margin-top: 20px; align-items: flex-start; }
  .preview-wrap { flex: 1; }
  .preview-label {
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.5px; color: #6b806b; margin-bottom: 8px;
  }
  .preview-img { width: 100%; border-radius: 6px; border: 1px solid #2e3a2e; display: block; }
  .btn-download {
    display: block; text-align: center; margin-top: 8px; padding: 8px;
    background: #1a1f1a; border: 1px solid #2e3a2e; border-radius: 6px;
    color: #9ab89a; font-size: 12px; font-weight: 600; text-decoration: none;
    cursor: pointer; transition: border-color 0.15s, color 0.15s;
  }
  .btn-download:hover { border-color: #b5d97a; color: #b5d97a; }
  .bottom-bar {
    display: flex; justify-content: flex-end; gap: 12px;
    padding-top: 20px; border-top: 1px solid #2e3a2e;
  }
  .btn-all {
    padding: 12px 28px; background: #2e3a2e; border: 1px solid #3e4e3e;
    border-radius: 8px; color: #b5d97a; font-size: 14px; font-weight: 700;
    cursor: pointer; transition: background 0.15s;
  }
  .btn-all:hover { background: #3a4a3a; }
  .all-status { font-size: 12px; color: #6b806b; align-self: center; }
  .all-status.ok  { color: #b5d97a; }
  .all-status.err { color: #e07070; }
</style>
</head>
<body>

<div class="top-bar">
  <h1>Ad Generator</h1>
  <span>Use *word* to highlight &nbsp;&middot;&nbsp; \n for line breaks &nbsp;&middot;&nbsp; $30K auto-highlights</span>
</div>

<div class="cards" id="cards"></div>

<div class="bottom-bar">
  <span class="all-status" id="all-status"></span>
  <button class="btn-all" onclick="generateAll()">Generate All &amp; Save</button>
</div>

<script>
const HOOKS = HOOKS_JSON_PLACEHOLDER;

const cardImages = {};

function makeCard(data, index) {
  const slug  = data.slug || ('ad_' + (index+1));
  const vSize = data.hook_font_size_vertical || 82;
  const sSize = data.hook_font_size_square   || 72;
  const hl    = (data.headline || '');
  const hk    = (data.hook     || '');

  return `
  <div class="card" id="card-${index}">
    <div class="card-title">Ad ${index+1} &nbsp;&middot;&nbsp; ${slug}</div>

    <div class="field">
      <label>Headline</label>
      <textarea id="hl-${index}" rows="3">${hl}</textarea>
      <div class="hint">Use <b>\\n</b> for line breaks &nbsp;&middot;&nbsp; <b>$30K</b> auto-highlights</div>
    </div>
    <div class="field">
      <label>Hook</label>
      <textarea id="hk-${index}" rows="3">${hk}</textarea>
      <div class="hint">Wrap with <b>*asterisks*</b> for custom highlight</div>
    </div>
    <div class="row">
      <div class="field">
        <label>Hook Font - Vertical</label>
        <input type="number" id="vs-${index}" value="${vSize}" min="30" max="200">
      </div>
      <div class="field">
        <label>Hook Font - Square</label>
        <input type="number" id="ss-${index}" value="${sSize}" min="30" max="200">
      </div>
    </div>

    <div class="section-label">Colors</div>
    <div class="color-row">
      <div class="color-field">
        <label>Background</label>
        <div class="color-wrap">
          <input type="color" id="bg-${index}" value="#7d8f75"
            oninput="document.getElementById('bg-hex-${index}').textContent=this.value">
          <span class="hex-val" id="bg-hex-${index}">#7d8f75</span>
        </div>
      </div>
      <div class="color-field">
        <label>Highlight / Callout</label>
        <div class="color-wrap">
          <input type="color" id="hl-col-${index}" value="#b5d97a"
            oninput="document.getElementById('hl-hex-${index}').textContent=this.value">
          <span class="hex-val" id="hl-hex-${index}">#b5d97a</span>
        </div>
      </div>
    </div>

    <div class="section-label">Logo</div>
    <div class="checkbox-row">
      <input type="checkbox" id="logo-show-${index}" checked
        onchange="toggleLogoOffsets(${index})">
      <label for="logo-show-${index}">Show logo</label>
    </div>
    <div id="logo-offsets-${index}">
      <div class="logo-row">
        <div class="field">
          <label>X Offset (px)</label>
          <input type="number" id="lox-${index}" value="0" min="-400" max="400">
        </div>
        <div class="field">
          <label>Y Offset (px)</label>
          <input type="number" id="loy-${index}" value="0" min="-200" max="200">
        </div>
      </div>
    </div>

    <div class="section-label">Image</div>
    <div class="upload-area" id="upload-area-${index}">
      <input type="file" accept="image/*" onchange="handleImageUpload(event, ${index})">
      <span id="upload-label-${index}">Click or drag an image here</span>
      <img class="upload-thumb" id="upload-thumb-${index}">
    </div>
    <div class="img-mode-row" id="img-modes-${index}">
      <div class="img-mode-btn active" id="mode-none-${index}"
        onclick="setMode(${index},'none')">None</div>
      <div class="img-mode-btn" id="mode-background-${index}"
        onclick="setMode(${index},'background')">Background</div>
      <div class="img-mode-btn" id="mode-card-${index}"
        onclick="setMode(${index},'card')">Photo Card</div>
      <div class="img-mode-btn" id="mode-both-${index}"
        onclick="setMode(${index},'both')">Both</div>
    </div>
    <div class="opacity-row" id="opacity-wrap-${index}" style="display:none">
      <label>
        Background opacity
        <span id="opacity-val-${index}">12%</span>
      </label>
      <input type="range" id="opacity-${index}" min="5" max="40" value="12"
        oninput="document.getElementById('opacity-val-${index}').textContent=this.value+'%'">
    </div>

    <button class="btn-generate" id="btn-${index}" onclick="generate(${index}, '${slug}')">
      <span class="spinner">&#x23F3; </span>Generate Preview
    </button>
    <div class="status" id="status-${index}"></div>
    <div class="previews" id="previews-${index}" style="display:none">
      <div class="preview-wrap">
        <div class="preview-label">Vertical (1080x1920)</div>
        <img class="preview-img" id="prev-v-${index}">
        <a class="btn-download" id="dl-v-${index}" download>&#x2193; Download Vertical</a>
      </div>
      <div class="preview-wrap">
        <div class="preview-label">Square (1080x1080)</div>
        <img class="preview-img" id="prev-s-${index}">
        <a class="btn-download" id="dl-s-${index}" download>&#x2193; Download Square</a>
      </div>
    </div>
  </div>`;
}

function toggleLogoOffsets(index) {
  const show = document.getElementById('logo-show-' + index).checked;
  document.getElementById('logo-offsets-' + index).style.display = show ? '' : 'none';
}

function handleImageUpload(event, index) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    cardImages[index] = e.target.result;
    const thumb = document.getElementById('upload-thumb-' + index);
    thumb.src = e.target.result;
    thumb.style.display = 'block';
    document.getElementById('upload-label-' + index).textContent = file.name;
  };
  reader.readAsDataURL(file);
}

function setMode(index, mode) {
  ['none','background','card','both'].forEach(m => {
    document.getElementById('mode-' + m + '-' + index)
      .classList.toggle('active', m === mode);
  });
  document.getElementById('opacity-wrap-' + index).style.display =
    (mode === 'background' || mode === 'both') ? '' : 'none';
}

function getCardData(index) {
  const slug = HOOKS[index] ? (HOOKS[index].slug || ('ad_' + (index+1))) : ('ad_' + (index+1));
  const activeMode = ['none','background','card','both'].find(m =>
    document.getElementById('mode-' + m + '-' + index)?.classList.contains('active')
  ) || 'none';

  return {
    slug,
    headline: document.getElementById('hl-' + index).value,
    hook:     document.getElementById('hk-' + index).value,
    hook_font_size_vertical: parseInt(document.getElementById('vs-' + index).value),
    hook_font_size_square:   parseInt(document.getElementById('ss-' + index).value),
    bg_color:        document.getElementById('bg-' + index).value,
    highlight_color: document.getElementById('hl-col-' + index).value,
    show_logo:       document.getElementById('logo-show-' + index).checked,
    logo_offset_x:   parseInt(document.getElementById('lox-' + index).value) || 0,
    logo_offset_y:   parseInt(document.getElementById('loy-' + index).value) || 0,
    image_b64:       cardImages[index] || null,
    image_mode:      activeMode,
    overlay_opacity: parseInt(document.getElementById('opacity-' + index)?.value) || 12,
  };
}

async function generate(index, slug) {
  const btn    = document.getElementById('btn-' + index);
  const status = document.getElementById('status-' + index);
  const card   = getCardData(index);

  btn.disabled = true;
  btn.classList.add('loading');
  status.textContent = 'Rendering...';
  status.className = 'status';

  try {
    const res = await fetch('/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(card)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Server error');

    document.getElementById('prev-v-' + index).src = 'data:image/png;base64,' + data.vertical;
    document.getElementById('prev-s-' + index).src = 'data:image/png;base64,' + data.square;
    const dlV = document.getElementById('dl-v-' + index);
    const dlS = document.getElementById('dl-s-' + index);
    dlV.href = 'data:image/png;base64,' + data.vertical;
    dlV.download = slug + '_vertical.png';
    dlS.href = 'data:image/png;base64,' + data.square;
    dlS.download = slug + '_square.png';

    document.getElementById('previews-' + index).style.display = 'flex';
    status.textContent = 'Done!';
    status.className = 'status ok';
  } catch(e) {
    status.textContent = 'Error: ' + e.message;
    status.className = 'status err';
  } finally {
    btn.disabled = false;
    btn.classList.remove('loading');
  }
}

async function generateAll() {
  const statusEl = document.getElementById('all-status');
  statusEl.textContent = 'Saving all ads...';
  statusEl.className = 'all-status';
  const cards = HOOKS.map((_, i) => getCardData(i));
  try {
    const res  = await fetch('/generate_all', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({cards})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Server error');
    statusEl.textContent = data.message;
    statusEl.className = 'all-status ok';
  } catch(e) {
    statusEl.textContent = 'Error: ' + e.message;
    statusEl.className = 'all-status err';
  }
}

document.getElementById('cards').innerHTML = HOOKS.map((h, i) => makeCard(h, i)).join('');
</script>
</body>
</html>
"""


# -- Routes ----------------------------------------------------------------

@app.route("/")
def index():
    import json
    return HTML.replace("HOOKS_JSON_PLACEHOLDER", json.dumps(gen.HOOKS))


@app.route("/generate", methods=["POST"])
def generate():
    card = request.get_json()
    headline = card.get("headline", "")
    hook     = card.get("hook", "")
    try:
        v_kw = kwargs_for_format(card, "vertical")
        s_kw = kwargs_for_format(card, "square")
        vertical = render_to_b64(headline, hook, 1080, 1920, **v_kw)
        square   = render_to_b64(headline, hook, 1080, 1080, **s_kw)
        return jsonify({"vertical": vertical, "square": square})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/generate_all", methods=["POST"])
def generate_all():
    cards = request.get_json().get("cards", [])
    saved = []
    try:
        for card in cards:
            slug     = card["slug"]
            headline = card["headline"]
            hook     = card["hook"]
            for fmt_name, dims in gen.FORMATS.items():
                kw = kwargs_for_format(card, fmt_name)
                out_path = os.path.join(gen.OUTPUT_DIR, f"{slug}_{fmt_name}.png")
                gen.render_ad(headline, hook, dims["w"], dims["h"], out_path, **kw)
                saved.append(os.path.basename(out_path))
        return jsonify({"message": f"Saved {len(saved)} images to ad-outputs/"})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    gen.download_fonts()
    print("\nStarting Ad Generator...")
    print("Open: http://127.0.0.1:5000\n")
    Timer(1.2, open_browser).start()
    app.run(debug=False, port=5000)
