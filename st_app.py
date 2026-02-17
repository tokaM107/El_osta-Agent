import streamlit as st
import sys
import os
import base64
from typing import Any

# Ensure both the script directory and repo root are on PYTHONPATH.
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_APP_DIR)
for p in (_REPO_ROOT, _APP_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from graph.graph import build_graph
from services.routing_client import find_route
from services.geocoding_serv import geocode_address

# --- Page Config ---
st.set_page_config(page_title="El Osta • RouteAI", page_icon="🧭", layout="wide")


def _init_state() -> None:
    st.session_state.setdefault("query_text", "")
    st.session_state.setdefault("last_state", {})
    st.session_state.setdefault("last_query", "")
    st.session_state.setdefault("dark_mode", False)


_init_state()


@st.cache_data
def _load_bg_data_url() -> str | None:
    bg_path = os.path.join(_APP_DIR, "elostabackground.png")
    if not os.path.exists(bg_path):
        return None
    try:
        with open(bg_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        return f"data:image/png;base64,{encoded}"
    except Exception:
        return None


_BG_DATA_URL = _load_bg_data_url()

# Theme variables based on mode
if st.session_state.get("dark_mode", False):
    theme_vars = """
        :root {
            --bg0: #0F172A;
            --bg1: #1E293B;
            --card: rgba(30, 41, 59, 0.95);
            --border: rgba(255, 255, 255, 0.12);
            --text: rgba(248, 250, 252, 0.95);
            --muted: rgba(148, 163, 184, 0.85);
            --accent: #FBBF24;
            --accent2: #34D399;
            --accent3: #818CF8;
            --input-bg: rgba(51, 65, 85, 0.8);
            --input-border: rgba(100, 116, 139, 0.5);
            --success-bg: rgba(34, 197, 94, 0.15);
            --error-bg: rgba(239, 68, 68, 0.15);
        }
    """
    bg_opacity = "0.15"
else:
    theme_vars = """
        :root {
            --bg0: #F8FAFF;
            --bg1: #EEF3FF;
            --card: rgba(255, 255, 255, 0.92);
            --border: rgba(15, 23, 42, 0.10);
            --text: rgba(15, 23, 42, 0.92);
            --muted: rgba(15, 23, 42, 0.62);
            --accent: #FFB020;
            --accent2: #00B89F;
            --accent3: #6366F1;
            --input-bg: rgba(255, 255, 255, 0.9);
            --input-border: rgba(15, 23, 42, 0.15);
            --success-bg: rgba(34, 197, 94, 0.1);
            --error-bg: rgba(239, 68, 68, 0.1);
        }
    """
    bg_opacity = "0.35"

_bg_css = ""
if _BG_DATA_URL:
    _bg_css = f"""
      .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("{_BG_DATA_URL}");
        background-repeat: no-repeat;
        background-position: center center;
        background-size: cover;
        opacity: {bg_opacity};
        filter: saturate(1.1) contrast(1.05);
        z-index: -1;
        pointer-events: none;
      }}
    """

st.markdown(
    theme_vars
    + """
    <style>
        /* Base App Styling */
        .stApp {
            color: var(--text);
            background:
                radial-gradient(1200px 600px at 10% 0%, rgba(255,176,32,0.12), transparent 60%),
                radial-gradient(1200px 600px at 90% 0%, rgba(0,184,159,0.10), transparent 60%),
                linear-gradient(180deg, var(--bg0), var(--bg1));
        }

    """
    + _bg_css
    + """

        /* Typography - Bilingual Support */
        html, body, [class*="css"] {
            font-family: "Inter", "Segoe UI", "Noto Sans Arabic", "Noto Sans", "Cairo", Tahoma, sans-serif;
        }

        /* Bilingual text container */
        .bilingual {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .bilingual .en {
            direction: ltr;
            text-align: left;
            font-size: 1rem;
        }
        .bilingual .ar {
            direction: rtl;
            text-align: right;
            font-size: 1rem;
            font-family: "Noto Sans Arabic", "Cairo", Tahoma, sans-serif;
        }
        
        /* Auto-direction for mixed content */
        .auto-dir {
            unicode-bidi: plaintext;
            direction: auto;
        }

        /* Layout */
        .block-container { 
            padding-top: 1.5rem; 
            padding-bottom: 2rem; 
            max-width: 1400px; 
        }
        header[data-testid="stHeader"] { background: transparent; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }

        /* Card Components */
        .eo-card { 
            background: var(--card); 
            border: 1px solid var(--border); 
            border-radius: 16px; 
            padding: 24px; 
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08); 
            margin-bottom: 20px; 
            backdrop-filter: blur(12px);
            transition: all 0.3s ease;
        }
        .eo-card:hover {
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            transform: translateY(-2px);
        }
        .eo-card-green { border-left: 4px solid var(--accent2); }
        .eo-card-orange { border-left: 4px solid var(--accent); }
        .eo-card-purple { border-left: 4px solid var(--accent3); }
        
        .eo-muted { 
            color: var(--muted); 
            font-size: 0.9rem;
            margin-top: 4px;
        }
        
        .eo-pill { 
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px; 
            border: 1px solid var(--border); 
            border-radius: 999px; 
            background: var(--card); 
            font-size: 0.9rem;
            font-weight: 500;
        }

        /* Form Styling */
        div[data-testid="stForm"] { 
            background: var(--card); 
            border: 1px solid var(--border); 
            border-radius: 16px; 
            padding: 20px; 
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06); 
            backdrop-filter: blur(8px); 
        }
        
        /* Input Fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input {
            background: var(--input-bg) !important;
            border: 1px solid var(--input-border) !important;
            border-radius: 10px !important;
            color: var(--text) !important;
            font-family: inherit !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px rgba(255, 176, 32, 0.2) !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] { 
            background: var(--card); 
            border-right: 1px solid var(--border); 
        }
        section[data-testid="stSidebar"] .block-container { 
            padding-top: 1.5rem; 
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: var(--text);
        }

        /* Result Styling */
        .eo-suggestion { 
            border-left: 4px solid var(--accent); 
            background: linear-gradient(135deg, var(--card), rgba(255, 176, 32, 0.05));
        }
        .eo-answer { 
            white-space: pre-wrap; 
            line-height: 1.75; 
            font-size: 1.05rem; 
            unicode-bidi: plaintext; 
            direction: auto;
            padding: 12px 0;
        }
        
        /* Section Headers */
        .section-header { 
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
        }
        .section-title { 
            font-size: 1.25rem; 
            font-weight: 600; 
            margin: 0;
            color: var(--text);
        }
        .section-icon {
            font-size: 1.5rem;
        }
        
        /* Journey Card */
        .journey-card {
            background: var(--input-bg);
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
            border: 1px solid var(--border);
        }
        
        /* Theme Toggle */
        .theme-toggle {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px;
            background: var(--input-bg);
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 16px;
        }
        
        /* Buttons */
        .stButton > button {
            border-radius: 10px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button:hover {
            transform: translateY(-1px) !important;
        }
        
        /* Status Widget */
        div[data-testid="stStatusWidget"] { 
            border-radius: 12px; 
            background: var(--card);
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: var(--input-bg) !important;
            border-radius: 10px !important;
        }
        
        /* Success/Error States */
        .stSuccess {
            background: var(--success-bg) !important;
            border-radius: 10px;
        }
        .stError {
            background: var(--error-bg) !important;
            border-radius: 10px;
        }
        
        /* Slider */
        .stSlider > div > div > div {
            background: var(--accent) !important;
        }
        
        /* Checkbox */
        .stCheckbox label span {
            color: var(--text) !important;
        }
        
        /* Divider */
        hr {
            border-color: var(--border) !important;
            opacity: 0.5;
        }
        
        /* Labels */
        .stTextInput label, .stTextArea label, .stNumberInput label, 
        .stSlider label, .stCheckbox label, .stMultiSelect label {
            color: var(--text) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize the graph
@st.cache_resource
def get_graph():
    return build_graph()

graph = get_graph()


# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    # Theme Toggle
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <span class="eo-pill">🎨 Theme</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    col_theme1, col_theme2 = st.columns([3, 1])
    with col_theme1:
        mode_label = "🌙 Dark Mode" if st.session_state.dark_mode else "☀️ Light Mode"
        st.markdown(f"**{mode_label}**")
    with col_theme2:
        if st.button("🔄", key="theme_toggle", help="Toggle theme"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("<span class='eo-pill'>⚙️ Settings</span>", unsafe_allow_html=True)
    st.markdown("")
    
    st.markdown("**🚶 Trip Configuration**")
    walking_cutoff = st.slider(
        "Walking Distance (meters)", 
        min_value=0, 
        max_value=4000, 
        value=1000, 
        step=50,
        help="Maximum walking distance between stops"
    )
    max_transfers = st.slider(
        "Maximum Transfers", 
        min_value=0, 
        max_value=6, 
        value=2, 
        step=1,
        help="Maximum number of vehicle changes"
    )

    st.markdown("---")
    st.markdown("**👁️ Display Options**")
    show_steps = st.checkbox("Show agent steps", value=True, help="Display AI processing steps")
    show_raw_state = st.checkbox("Show raw state", value=False, help="Show technical details")
    show_map = st.checkbox("Show map", value=True, help="Display route map")
    
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 16px 0;">
            <div style="font-size: 0.85rem; color: var(--muted);">
                <div>El Osta • RouteAI</div>
                <div style="margin-top: 4px;">v1.0.0</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# HEADER
# ============================================================================
st.markdown(
    """
    <div style="padding: 20px 0 30px 0;">
        <h1 style="font-size: 3.5rem; text-align: center; font-weight: 700; margin: 0; background: linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            🧭 El Osta
        </h1>
        <div class="bilingual" style="margin-top: 8px; text-align: center;">
            <span class="en" style="color: var(--muted); font-size: 1.1rem; text-align: center;">Your Smart Transit Companion</span>
            <span class="ar" style="color: var(--muted); font-size: 1.1rem; text-align: center;">رفيقك الذكي للمواصلات</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# MAIN LAYOUT: Two columns
# ============================================================================
col1, col2 = st.columns([1, 1], gap="large")


# ============================================================================
# COLUMN 1: AI-Powered (Full Pipeline with LLM)
# ============================================================================
with col1:
    st.markdown(
        """
        <div class="eo-card eo-card-orange">
            <div class="section-header">
                <span class="section-icon">🤖</span>
                <div>
                    <h3 class="section-title">AI Trip Planner</h3>
                    <div class="bilingual eo-muted">
                        <span class="en">Describe your trip in plain language</span>
                        <span class="ar">اكتب طلبك بالعربي أو الإنجليزي</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    with st.form("ai_query_form"):
        ai_query = st.text_area(
            "Your request",
            placeholder="Examples:\n• عايز اروح من سيدي جابر لمحطة مصر\n• I want to go from Sidi Gaber to Misr Station\n• من المنشية للمعمورة",
            height=120,
            label_visibility="collapsed",
        )
        
        st.markdown("")
        ai_submit = st.form_submit_button("🚀 Plan My Trip | خطط رحلتي", use_container_width=True)

    # AI Results
    if ai_submit and ai_query.strip():
        initial_state = {
            "query": ai_query,
            "walking_cutoff": float(walking_cutoff),
            "max_transfers": int(max_transfers)
        }

        with st.status("🤔 El Osta is thinking... | الأُسطى بيفكر...", expanded=True) as status:
            final_state: dict[str, Any] = {}
            try:
                for event in graph.stream(initial_state):
                    for node_name, state_update in event.items():
                        if show_steps:
                            st.write(f"✅ {node_name}")
                        final_state.update(state_update)
            except Exception as e:
                final_state["error"] = str(e)

            if final_state.get("error"):
                status.update(label="❌ Error occurred", state="error", expanded=True)
            else:
                status.update(label="✅ Route found!", state="complete", expanded=False)

        st.session_state["last_state"] = final_state

        if final_state.get("final_answer"):
            answer_text = str(final_state["final_answer"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(
                f"""
                <div class="eo-card eo-suggestion">
                    <div class="section-header">
                        <span class="section-icon">🗣️</span>
                        <div class="bilingual">
                            <span class="en section-title">El Osta Says</span>
                            <span class="ar section-title">الأُسطى بيقول</span>
                        </div>
                    </div>
                    <div class="eo-answer">{answer_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if final_state.get("error"):
            st.error(f"⚠️ Error: {final_state['error']}")

    if show_raw_state and st.session_state.get("last_state"):
        with st.expander("🔍 Technical Details (Raw State)"):
            st.json(st.session_state["last_state"])


# ============================================================================
# COLUMN 2: Raw Server Test (Coordinates Only - No AI)
# ============================================================================
with col2:
    st.markdown(
        """
        <div class="eo-card eo-card-green">
            <div class="section-header">
                <span class="section-icon">🔧</span>
                <div>
                    <h3 class="section-title">Direct API Test</h3>
                    <div class="eo-muted">Test routing server with coordinates</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    with st.form("raw_server_form"):
        st.markdown("**📍 Start Location**")
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            start_lat = st.number_input("Latitude", value=31.22968895248673, format="%.8f", key="start_lat")
        with r_col2:
            start_lon = st.number_input("Longitude", value=29.96139328537071, format="%.8f", key="start_lon")
        
        st.markdown("**📍 End Location**")
        r_col3, r_col4 = st.columns(2)
        with r_col3:
            end_lat = st.number_input("Latitude", value=31.20775934404925, format="%.8f", key="end_lat")
        with r_col4:
            end_lon = st.number_input("Longitude", value=29.94194179397711, format="%.8f", key="end_lon")
        
        st.markdown("**⚖️ Route Weights**")
        w_col1, w_col2, w_col3, w_col4 = st.columns(4)
        with w_col1:
            w_time = st.number_input("Time", value=0.5, min_value=0.0, max_value=1.0, step=0.1)
        with w_col2:
            w_cost = st.number_input("Cost", value=0.3, min_value=0.0, max_value=1.0, step=0.1)
        with w_col3:
            w_walk = st.number_input("Walk", value=0.1, min_value=0.0, max_value=1.0, step=0.1)
        with w_col4:
            w_transfer = st.number_input("Transfer", value=0.1, min_value=0.0, max_value=1.0, step=0.1)
        
        st.markdown("**🚫 Restricted Modes**")
        restricted_modes = st.multiselect(
            "Select modes to exclude",
            options=["Bus", "Minibus", "Microbus", "Tram", "Metro"],
            default=[],
            label_visibility="collapsed"
        )
        
        st.markdown("")
        raw_submit = st.form_submit_button("🔍 Test Server", use_container_width=True)

    if raw_submit:
        with st.spinner("📡 Connecting to routing server..."):
            try:
                weights = {
                    "time": w_time,
                    "cost": w_cost,
                    "walk": w_walk,
                    "transfer": w_transfer
                }
                raw_result = find_route(
                    start_lat=start_lat,
                    start_lon=start_lon,
                    end_lat=end_lat,
                    end_lon=end_lon,
                    max_transfers=max_transfers,
                    walking_cutoff=walking_cutoff,
                    restricted_modes=restricted_modes,
                    weights=weights
                )
                
                journey_count = len(raw_result.get('journeys', []))
                st.success(f"✅ Found {journey_count} route{'s' if journey_count != 1 else ''}")
                
                for i, journey in enumerate(raw_result.get("journeys", [])):
                    with st.expander(f"🚌 Route Option {i+1}", expanded=(i == 0)):
                        st.json(journey)
                        
            except Exception as e:
                st.error(f"❌ Server Error: {e}")


# ============================================================================
# SECTION 3: Geocoding & Parsing Test
# ============================================================================
st.markdown("---")
st.markdown(
    """
    <div class="eo-card eo-card-purple">
        <div class="section-header">
            <span class="section-icon">📍</span>
            <div>
                <h3 class="section-title">Geocoding Test</h3>
                <div class="bilingual eo-muted">
                    <span class="en">Convert location names to coordinates</span>
                    <span class="ar">تحويل أسماء الأماكن لإحداثيات</span>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

stop_col1, stop_col2 = st.columns([1, 1])

with stop_col1:
    with st.form("stop_names_form"):
        st.markdown("**🚏 Enter Stop Names**")
        from_stop = st.text_input(
            "From (من)", 
            value="محطة مصر", 
            placeholder="e.g., محطة مصر / Misr Station"
        )
        to_stop = st.text_input(
            "To (إلى)", 
            value="سيدي بشر", 
            placeholder="e.g., سيدي بشر / Sidi Bishr"
        )
        st.markdown("")
        stop_submit = st.form_submit_button("🔍 Geocode Locations", use_container_width=True)

with stop_col2:
    st.markdown("**📊 Results**")
    geocode_placeholder = st.empty()

if stop_submit and from_stop.strip() and to_stop.strip():
    with geocode_placeholder.container():
        with st.spinner("🔄 Geocoding locations..."):
            try:
                from_geo = geocode_address(from_stop)
                to_geo = geocode_address(to_stop)
                
                st.success("✅ Locations geocoded successfully!")
                
                st.markdown("**📍 From Location:**")
                st.json({"input": from_stop, "coordinates": from_geo})
                
                st.markdown("**📍 To Location:**")
                st.json({"input": to_stop, "coordinates": to_geo})
                
            except Exception as e:
                st.error(f"❌ Geocoding Error: {e}")
