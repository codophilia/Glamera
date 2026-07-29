"""Streamlit UI for Glamera — Personal Styling Agent."""
from __future__ import annotations

import base64
import io
import json
import os
from pathlib import Path

import google.generativeai as genai
import PIL.Image
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from styling_agent import StylingAgent, StylingRequest
from styling_agent.schema import WardrobeItem

load_dotenv()
genai.configure(api_key=os.getenv("STYLIST_AI_KEY"))

# ============================================================================
# LOGO LOADER (script-relative — robust to how you launch streamlit)
# ============================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
LOGO_CANDIDATES = [
    SCRIPT_DIR / "assets" / "glamera_g.png",
    SCRIPT_DIR / "assets" / "glamera_g.PNG",
    SCRIPT_DIR / "assets" / "glamera.png",
    Path.cwd() / "assets" / "glamera_g.png",
]
_LOGO_DATA_URI = ""
_FAVICON = "👗"        # fallback if logo not found
_LOGO_FOUND_AT = None
for _p in LOGO_CANDIDATES:
    try:
        if _p.exists():
            _bytes = _p.read_bytes()
            _LOGO_DATA_URI = f"data:image/png;base64,{base64.b64encode(_bytes).decode()}"
            _FAVICON = PIL.Image.open(io.BytesIO(_bytes))
            _LOGO_FOUND_AT = _p
            break
    except Exception:
        pass

# ============================================================================
# PAGE CONFIG (must be called exactly ONCE, before any other st.* call)
# ============================================================================
st.set_page_config(page_title="Glamera", page_icon=_FAVICON, layout="centered")

# ============================================================================
# GLOBAL CSS
# ============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap');
:root {
  --violet:  #380525;
  --custard: #F8F0B4;
  --thistle: #D4CAE3;
  --navy: #380525;
  --navy-light: #D4CAE3;
  --text: #380525;
  --muted: #6b5b6e;
  --border: rgba(56, 5, 37, 0.20);
}

/* Kill Streamlit's default top bar */
header[data-testid="stHeader"] { display: none !important; height: 0 !important; }
[data-testid="stToolbar"]      { display: none !important; }
[data-testid="stDecoration"]   { display: none !important; }
#MainMenu, footer              { display: none !important; }

/* App background */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stAppViewBlockContainer"],
.main, .block-container {
  background: var(--custard) !important;
  color: var(--violet);
}
.block-container {
  max-width: 560px;
  padding-top: 1.2rem !important;
  padding-bottom: 6rem;
}

/* ---- Title ------------------------------------------------------------- */
.glamera-lamera {
  font-family: 'Dancing Script', cursive;
  font-size: 4rem;
  font-weight: 700;
  line-height: 1;
  color: var(--violet);
  text-align: left;
  padding: 0;
  margin: 0;
  display: flex;
  align-items: center;
  height: 100%;
}
.glamera-sub {
  font-size: 0.85rem; color: var(--muted);
  margin-top: 4px; margin-bottom: 24px; text-align: center;
}
/* Make the G image sit tight next to 'lamera' */
[data-testid="stImage"] img { display: block; }

/* ---- Cards / item rows ------------------------------------------------- */
.card {
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px 20px;
  margin-top: 12px;
  background: var(--thistle);
}
.item-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0; border-bottom: 1px solid var(--border);
}
.item-row:last-child { border-bottom: none; }
.item-name { font-size: 0.9rem; font-weight: 500; text-transform: capitalize; color: var(--violet); }
.item-notes { font-size: 0.75rem; color: var(--muted); }

.pill {
  display: inline-block; padding: 2px 10px; border-radius: 999px;
  background: var(--custard); color: var(--violet);
  font-size: 0.7rem; margin-right: 4px;
  border: 1px solid var(--border);
}
.harmony-badge {
  display: inline-block; padding: 3px 14px; border-radius: 999px;
  background: var(--violet); color: var(--custard);
  font-size: 0.78rem; font-weight: 600;
}
.section-title { font-size: 1.05rem; font-weight: 600; margin: 14px 0 6px; color: var(--violet); }
.weather-strip { font-size: 0.85rem; color: var(--muted); margin-bottom: 8px; }
.rationale { font-size: 0.9rem; line-height: 1.6; color: var(--violet); }
.relaxed-box {
  border: 1px solid rgba(245,158,11,0.4); background: rgba(245,158,11,0.10);
  border-radius: 10px; padding: 8px 14px; font-size: 0.8rem; color: #7a3d00; margin-top: 10px;
}

/* ---- Chat -------------------------------------------------------------- */
.chat-window {
  border: 1px solid var(--border);
  border-radius: 16px; overflow: hidden;
  margin-top: 12px;
  background: var(--thistle);
}
.chat-header {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; border-bottom: 1px solid var(--border);
  background: var(--thistle);
}
.chat-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--violet); color: var(--custard);
  display: flex; align-items: center; justify-content: center; font-size: 0.85rem;
}
.chat-name { font-size: 0.85rem; font-weight: 600; color: var(--violet); }
.chat-status { font-size: 0.7rem; color: var(--muted); }
.chat-messages { padding: 16px; background: var(--custard); max-height: 340px; overflow-y: auto; }
.msg-ai-wrap { display: flex; justify-content: flex-start; margin-bottom: 10px; }
.msg-user-wrap { display: flex; justify-content: flex-end; margin-bottom: 10px; }
.msg-ai-bubble {
  background: var(--thistle); border: 1px solid var(--border);
  border-radius: 18px 18px 18px 4px;
  padding: 10px 14px; font-size: 0.85rem; max-width: 82%; line-height: 1.5; color: var(--violet);
}
.msg-user-bubble {
  background: var(--violet); color: var(--custard);
  border-radius: 18px 18px 4px 18px;
  padding: 10px 14px; font-size: 0.85rem; max-width: 82%; line-height: 1.5;
}

/* ---- Streamlit buttons ------------------------------------------------- */
div.stButton > button {
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--thistle);
  color: var(--violet);
  font-size: 0.85rem; padding: 6px 16px; font-weight: 500;
}
div.stButton > button:hover {
  background: var(--violet);
  color: var(--custard);
  border-color: var(--violet);
}
div.stButton > button[kind="primary"] {
  background: var(--custard) !important;
  color: var(--violet) !important;
  border: 1.5px solid var(--violet) !important;
  font-size: 0.95rem; padding: 10px; font-weight: 600;
}
div.stButton > button[kind="primary"]:hover {
  background: var(--thistle) !important;
  color: var(--violet) !important;
}
/* Fix FAB buttons to bottom right corner */
div[data-testid="stHorizontalBlock"]:has(button[key="fab_gallery_btn"]) {
    position: fixed !important;
    bottom: 24px !important;
    right: 24px !important;
    z-index: 9999 !important;
    width: auto !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 10px !important;
    pointer-events: auto !important;
}
div[data-testid="stHorizontalBlock"]:has(button[key="fab_gallery_btn"]) button {
    pointer-events: auto !important;
    opacity: 1 !important;
}

/* ---- Inputs / selects / text areas ------------------------------------- */
input, textarea,
.stTextInput input,
.stTextArea textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
  background: var(--thistle) !important;
  color: var(--violet) !important;
  border-color: var(--border) !important;
  border-radius: 10px !important;
}
input::placeholder, textarea::placeholder { color: var(--muted) !important; opacity: 0.85; }

div[data-baseweb="select"] > div {
  background: var(--thistle) !important;
  color: var(--violet) !important;
  border-color: var(--border) !important;
  border-radius: 10px !important;
}
div[data-baseweb="select"] * { color: var(--violet) !important; }

/* Expander */
[data-testid="stExpander"] {
  background: var(--thistle);
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] p,
[data-testid="stExpander"] label,
[data-testid="stExpander"] div { color: var(--violet) !important; }

/* File uploader */
[data-testid="stFileUploader"] section {
  background: var(--thistle) !important;
  border: 1.5px dashed var(--violet) !important;
  border-radius: 12px;
}
[data-testid="stFileUploader"] * { color: var(--violet) !important; }

label, .stTextInput label, .stSelectbox label, .stTextArea label {
  color: var(--violet) !important;
  font-weight: 500;
}
hr { border-color: var(--border) !important; }

.gallery-label {
  font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--muted); margin: 12px 0 6px;
}
.gallery-caption { font-size: 0.72rem; color: var(--muted); margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================
for key, default in {
    "style_profile": "",
    "constraints": [],
    "preferences": ["minimal", "earth tones"],
    "extra_wardrobe": [],
    "gallery_images": [],
    "chat_open": False,
    "gallery_open": False,
    "chat_history": [],
    "last_outfit": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

if not st.session_state.chat_history:
    st.session_state.chat_history.append({
        "role": "ai",
        "text": "Hi! ✨ I'm your Glamera stylist — so glad you're here! What mood are you in today, and what kind of look are you reaching for?"
    })

# ============================================================================
# HEADER — G logo (via st.image) + "lamera" text, centered
# ============================================================================
# ---- Title: G logo (bg removed, embedded) + "lamera" in cursive ----------

def _get_g_logo_b64() -> str:
    """Load G logo, strip grey/white background, return base64 PNG data URI."""
    for p in LOGO_CANDIDATES:
        try:
            if not p.exists():
                continue
            img = Image.open(p).convert("RGBA")
            data = img.getdata()
            new_data = []
            for r, g, b, a in data:
                brightness = (r + g + b) / 3
                is_grey = abs(r - g) < 25 and abs(g - b) < 25 and abs(r - b) < 25
                if is_grey and brightness > 140:
                    new_data.append((r, g, b, 0))   # transparent
                else:
                    new_data.append((r, g, b, a))
            img.putdata(new_data)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            return f"data:image/png;base64,{b64}"
        except Exception:
            pass
    return ""

_G_DATA_URI = _get_g_logo_b64()

if _G_DATA_URI:
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:center; gap:0px; margin-bottom:4px;">
      <img src="{_G_DATA_URI}"
           style="height:150px; width:auto; object-fit:contain; display:block; margin:0; padding:0;
                  image-rendering:crisp-edges;" />
      <span style="font-family:'Dancing Script',cursive; font-size:4rem; font-weight:700;
                   color:#380525; line-height:1; margin:0; padding:0; display:block;">lamera</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(
        "<h1 style='text-align:center; font-family:Dancing Script,cursive; "
        "color:#380525; font-size:12rem; margin:0;'>Glamera</h1>",
        unsafe_allow_html=True,
    )

st.markdown("<div class='glamera-sub'>Snap · Sync · Glam</div>", unsafe_allow_html=True)

# ============================================================================
# NAV — Gallery / Chat toggles
# ============================================================================
st.markdown("""
<style>
/* Icon-only round FAB buttons */
div[data-testid="stHorizontalBlock"]:has(button[key="fab_gallery_btn"]) {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin: 8px 0;
}
button[key="fab_gallery_btn"], button[key="fab_chat_btn"] {
    width: 52px !important;
    height: 52px !important;
    border-radius: 50% !important;
    padding: 0 !important;
    font-size: 1.3rem !important;
    min-width: 0 !important;
}
</style>
""", unsafe_allow_html=True)

col_g, col_c = st.columns(2)
with col_g:
    if st.button("🖼️", key="fab_gallery_btn"):
        st.session_state.gallery_open = not st.session_state.gallery_open
        st.session_state.chat_open = False
with col_c:
    if st.button("💬", key="fab_chat_btn"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.session_state.gallery_open = False

st.markdown("---")

# ============================================================================
# CHAT PANEL
# ============================================================================
if st.session_state.chat_open:
    msgs_html = ""
    for msg in st.session_state.chat_history:
        cls = "msg-ai-wrap" if msg["role"] == "ai" else "msg-user-wrap"
        bcls = "msg-ai-bubble" if msg["role"] == "ai" else "msg-user-bubble"
        msgs_html += f"<div class='{cls}'><div class='{bcls}'>{msg['text']}</div></div>"

    st.markdown(f"""
<div class='chat-window'>
  <div class='chat-header'>
    <div class='chat-avatar'>✨</div>
    <div>
      <div class='chat-name'>Glamera Stylist</div>
      <div class='chat-status'>online · your personal stylist</div>
    </div>
  </div>
  <div class='chat-messages'>{msgs_html}</div>
</div>
""", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        c1, c2 = st.columns([5, 1])
        with c1:
            user_msg = st.text_input(
                "chat_input", placeholder="Tell your stylist anything…",
                label_visibility="collapsed",
            )
        with c2:
            send = st.form_submit_button("Send")

        if send and user_msg.strip():
            st.session_state.chat_history.append({"role": "user", "text": user_msg})
            history_text = "\n".join(
                f"{'User' if m['role'] == 'user' else 'Glamera'}: {m['text']}"
                for m in st.session_state.chat_history[:-1]
            )
            prompt = f"""You are Glamera, a warm personal AI fashion stylist.
Style profile: {st.session_state.style_profile or 'not set yet'}
Conversation: {history_text}
User: {user_msg}
Reply in 2-3 sentences. Warm, specific, fashion-forward."""
            model = genai.GenerativeModel("gemini-2.5-flash")
            with st.spinner(""):
                response = model.generate_content(prompt)
            st.session_state.chat_history.append({"role": "ai", "text": response.text.strip()})
            st.rerun()

    if st.button("🗑️ Reset chat"):
        st.session_state.chat_history = []
        st.rerun()
    st.markdown("---")

# ============================================================================
# GALLERY PANEL
# ============================================================================
if st.session_state.gallery_open:
    with st.sidebar:
        st.markdown("### 🖼️ Wardrobe Gallery")
        uploaded = st.file_uploader(
            "Upload clothing photos — Gemini auto-extracts metadata",
            type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True,
        )
        if uploaded:
            for folder in ["tops", "bottoms", "outerwear", "shoes", "accessories", "other"]:
                Path(f"gallery/{folder}").mkdir(parents=True, exist_ok=True)
            for file in uploaded:
                if any(g["filename"] == file.name for g in st.session_state.gallery_images):
                    continue
                img_bytes = file.read()
                with st.spinner(f"Analyzing {file.name}..."):
                    try:
                        import PIL.Image, io
                        img = PIL.Image.open(io.BytesIO(img_bytes))
                        model = genai.GenerativeModel("gemini-2.5-flash")
                        prompt = """Analyze this clothing item. Return STRICT JSON only:
{
  "item_type": "top|bottom|outerwear|shoes|dress|accessory",
  "color": "primary color lowercase",
  "warmth_rating": 1-5,
  "style_tag": ["up to 4 tags"],
  "occasion_suitability": ["work","date","gym","formal","casual"],
  "notes": "max 10 word description"
}"""
                        resp = model.generate_content([prompt, img])
                        raw = resp.text.strip()
                        meta = json.loads(raw[raw.find("{"):raw.rfind("}")+1])
                    except Exception as e:
                        st.warning(f"Could not analyze {file.name}: {e}")
                        meta = {"item_type": "top", "color": "unknown", "warmth_rating": 3,
                                "style_tag": ["casual"], "occasion_suitability": ["casual"],
                                "notes": file.name}
                folder_map = {"top": "tops", "bottom": "bottoms", "outerwear": "outerwear",
                              "shoes": "shoes", "dress": "accessories", "accessory": "accessories"}
                folder = folder_map.get(meta.get("item_type", "top"), "other")
                save_path = Path("gallery") / folder / file.name
                with open(save_path, "wb") as f:
                    f.write(img_bytes)
                st.session_state.extra_wardrobe.append(
                    WardrobeItem.from_upload(file.name, meta)
                )
                st.session_state.gallery_images.append({
                    "filename": file.name, "bytes": img_bytes,
                    "meta": meta, "folder": folder,
                })
        if st.session_state.gallery_images:
            folder_groups: dict = {}
            for g in st.session_state.gallery_images:
                folder_groups.setdefault(g["folder"], []).append(g)
            for folder, items in folder_groups.items():
                st.markdown(f"**{folder.title()}**")
                for item in items:
                    st.image(item["bytes"], use_container_width=True)
                    m = item["meta"]
                    st.caption(f"{m.get('color','')} · {m.get('item_type','')} · {m.get('notes','')}")
            if st.button("🗑️ Clear gallery", key="clear_gallery"):
                st.session_state.gallery_images = []
                st.session_state.extra_wardrobe = []
                st.rerun()
        else:
            st.caption("No items yet — upload some photos above.")

# ============================================================================
# STYLE PROFILE
# ============================================================================
with st.expander("👤 Style profile", expanded=not st.session_state.style_profile):
    st.session_state.style_profile = st.text_area(
        "Describe yourself", value=st.session_state.style_profile,
        placeholder="e.g. I'm petite, I love minimalism, I avoid bold prints",
        height=80, label_visibility="collapsed",
    )

# ============================================================================
# TAG INPUT
# ============================================================================
def _add_tag(session_key: str) -> None:
    v = st.session_state[f"_inp_{session_key}"].strip().lower()
    if v and v not in st.session_state[session_key]:
        st.session_state[session_key].append(v)

def tag_input(label: str, session_key: str, placeholder: str) -> None:
    st.markdown(f"**{label}**")
    st.text_input(
        label, label_visibility="collapsed",
        placeholder=placeholder,
        key=f"_inp_{session_key}",
        on_change=_add_tag,
        args=(session_key,),
    )
    tags = st.session_state[session_key]
    if tags:
        cols = st.columns(len(tags))
        for i, tag in enumerate(tags):
            with cols[i]:
                if st.button(f"{tag} ×", key=f"_rm_{session_key}_{tag}"):
                    st.session_state[session_key].remove(tag)
                    st.rerun()
        if st.button("Clear all", key=f"_clr_{session_key}"):
            st.session_state[session_key] = []
            st.rerun()

# ============================================================================
# MAIN FORM
# ============================================================================
region = st.text_input("Region / City", value="Lisbon")
event_type = st.selectbox("Event", ["casual", "work", "date", "formal", "gym"])
tag_input("Style constraints", "constraints",
          "Press Enter to add — e.g. monochromatic, no denim")
tag_input("Preferences", "preferences",
          "Press Enter to add — e.g. minimal, earth tones")

style_me = st.button("Style me ✨", use_container_width=True, type="primary")

# ============================================================================
# RECOMMENDATION
# ============================================================================
if style_me:
    request = StylingRequest(
        region=region, event_type=event_type,
        constraints=st.session_state.constraints,
        preferences=st.session_state.preferences,
        style_profile=st.session_state.style_profile,
    )
    if st.session_state.extra_wardrobe:
        agent = StylingAgent(wardrobe=st.session_state.extra_wardrobe)
    else:
        agent = StylingAgent()
    with st.spinner("Styling…"):
        outfit = agent.recommend(request)
    st.session_state.last_outfit = outfit

    if outfit.weather:
        w = outfit.weather
        st.markdown(
            f"<div class='weather-strip'>🌤 {w.region} · {round(w.temperature_c)}°C "
            f"· {w.condition}" + (" (mock)" if w.is_mock else "") + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='section-title'>Today's outfit</div>", unsafe_allow_html=True)
    rows = ""
    for it in outfit.items:
        tags = "".join(f"<span class='pill'>{t}</span>" for t in it.style_tag[:2])
        rows += (
            f"<div class='item-row'>"
            f"<div><div class='item-name'>{it.item_type} · {it.color}</div>"
            f"<div class='item-notes'>{it.notes or ''}</div></div>"
            f"<div>{tags}</div>"
            f"</div>"
        )
    st.markdown(f"<div class='card'>{rows}</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        deep_btn = st.button("💡 Why this?", use_container_width=True)
    with col2:
        love_btn = st.button("👍 Love it", use_container_width=True)
    with col3:
        again_btn = st.button("👎 Try again", use_container_width=True)

    if deep_btn:
        item_desc = "\n".join(
            f"- {it.item_type}: {it.color} ({', '.join(it.style_tag)})"
            for it in outfit.items
        )
        prompt = f"""You are Glamera, expert AI fashion stylist.
Deep dive this outfit: {item_desc}
Event: {event_type} | Weather: {outfit.weather.temperature_c if outfit.weather else '?'}°C
Style profile: {st.session_state.style_profile or 'not provided'}
Cover: 1) color theory 2) body type 3) trend context 4) one tip. 4-5 sentences."""
        model = genai.GenerativeModel("gemini-2.5-flash")
        with st.spinner("Deep diving..."):
            deep = model.generate_content(prompt)
        st.markdown("<div class='section-title'>Why this outfit?</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='rationale'>{deep.text}</div>", unsafe_allow_html=True)

    if love_btn:
        st.success("Glad you love it! 💖")

    if again_btn:
        item_desc = "\n".join(f"- {it.item_type}: {it.color}" for it in outfit.items)
        prompt = f"""User didn't like: {item_desc}
Event: {event_type}, Preferences: {st.session_state.preferences}
Suggest ONE specific change. Brief and friendly."""
        model = genai.GenerativeModel("gemini-2.5-flash")
        with st.spinner("Rethinking..."):
            suggestion = model.generate_content(prompt)
        st.info(f"💡 {suggestion.text.strip()}")

    if outfit.color_harmony_score is not None:
        st.markdown(
            f"<div class='section-title'>Color harmony "
            f"<span class='harmony-badge'>{outfit.color_harmony_score}/10</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='rationale'>{outfit.color_rationale}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='section-title'>Stylist rationale</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='rationale'>{outfit.rationale}</div>", unsafe_allow_html=True)

    if outfit.relaxed_constraints:
        st.markdown(
            f"<div class='relaxed-box'>⚠️ Relaxed to find a viable outfit: "
            f"{', '.join(outfit.relaxed_constraints)}</div>",
            unsafe_allow_html=True,
        )