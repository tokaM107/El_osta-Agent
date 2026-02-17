import streamlit as st
import sys
import os
from typing import Any

# Path setup
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(_APP_DIR)
for p in (_REPO_ROOT, _APP_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

st.set_page_config(
    page_title="El Osta AI • Trip Planner",
    page_icon="🤖",
    layout="centered"
)

# Initialize Session State
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "last_state" not in st.session_state:
    st.session_state.last_state = {}

from ui.theme import inject_theme, render_header
from graph.graph import build_graph

# Inject Theme
inject_theme(st.session_state.dark_mode)

# ============================================================================
# SIDEBAR
# ============================================================================
def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

with st.sidebar:
    st.markdown('<span class="eo-pill" style="margin-bottom:10px; display:inline-block;">🎨 Appearance</span>', unsafe_allow_html=True)
    st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, on_change=toggle_theme)
    
    st.markdown("---")
    st.markdown('<span class="eo-pill" style="margin-bottom:10px; display:inline-block;">⚙️ Settings</span>', unsafe_allow_html=True)
    
    st.caption("**🚶 Trip Configuration**")
    walking_cutoff = st.slider(
        "Walking Distance (m)", 
        0, 4000, 1000, 50,
        help="Max walking distance"
    )
    max_transfers = st.slider(
        "Max Transfers", 
        0, 6, 2, 1
    )

    st.markdown("---")
    st.caption("**👁️ Debug**")
    show_steps = st.checkbox("Show steps", value=True)
    show_raw_state = st.checkbox("Show raw JSON", value=False)


# ============================================================================
# MAIN CONTENT
# ============================================================================
render_header()

st.markdown("""
    <div class="eo-card eo-card-orange">
        <div class="section-header">
            <span class="section-icon" style="font-size: 1.5rem; margin-right: 10px;">🤖</span>
            <div>
                <h3 class="section-title" style="margin:0;">AI Trip Planner</h3>
                <div class="eo-muted">
                    Describe your trip in plain language <br>
                    <span style="font-family:'Cairo';">اشرح مشوارك ببساطة</span>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Graph Init
@st.cache_resource
def get_graph():
    return build_graph()
graph = get_graph()

# Form
with st.form("ai_query_form"):
    ai_query = st.text_area(
        "Your request",
        placeholder="Examples:\n• عايز اروح من سيدي جابر لمحطة مصر\n• I want to go from Sidi Gaber to Misr Station",
        height=140,
        label_visibility="collapsed",
    )
    st.markdown("")
    ai_submit = st.form_submit_button("🚀 Plan My Trip | خطط رحلتي", use_container_width=True)

# Results
if ai_submit and ai_query.strip():
    initial_state = {
        "query": ai_query,
        "walking_cutoff": float(walking_cutoff),
        "max_transfers": int(max_transfers)
    }

    with st.status("🤔 El Osta is thinking...", expanded=True) as status:
        final_state: dict[str, Any] = {}
        try:
            for event in graph.stream(initial_state):
                for node_name, state_update in event.items():
                    if show_steps:
                        st.write(f"✅ {node_name}")
                    final_state.update(state_update)
            status.update(label="✅ Route found!", state="complete", expanded=False)
        except Exception as e:
            final_state["error"] = str(e)
            status.update(label="❌ Error occurred", state="error", expanded=True)

    st.session_state["last_state"] = final_state

    if final_state.get("error"):
        st.error(f"⚠️ Error: {final_state['error']}")
    
    # Display Answer
    # Display Answer
    if final_state.get("final_answer"):
        import markdown
        raw_answer = str(final_state["final_answer"])
        
        # نستخدم markdown لتنسيق Markdown في النص
        safe_answer_html = markdown.markdown(raw_answer, extensions=['extra'])

        st.markdown(f"""
            <div class="eo-card eo-card-green" style="margin-top:20px;">
                <h4 style="margin-bottom:12px;">🗣️ El Osta Says:</h4>
                <div style="
                    line-height: 1.8;
                    font-size: 1.05rem;
                    text-align: right;
                    direction: rtl;
                    unicode-bidi: plaintext;
                ">
                    {safe_answer_html}
                </div>
            </div>
        """, unsafe_allow_html=True)


# Debug
if show_raw_state and st.session_state.get("last_state"):
    with st.expander("🔍 Raw State"):
        st.json(st.session_state["last_state"])