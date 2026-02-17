import streamlit as st

st.set_page_config(
    page_title="El Osta • رفيقك الذكي في المواصلات",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state for consistent theme across pages
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# --- Theme Toggle Logic ---
# Logic: We use a callback to sync the toggle state with session state
def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

with st.sidebar:
    st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, on_change=toggle_theme)

from ui.theme import inject_theme, render_header

# Inject the theme based on the current session state
inject_theme(st.session_state.dark_mode)

# Render main UI
render_header()

st.markdown("""
    <div class="eo-card" style="text-align: center;">
        <h2 style="margin-bottom: 16px;">Welcome to El Osta | أهلاً بك</h2>
        <p class="eo-muted" style="font-size: 1.1rem; line-height: 1.7; margin-bottom: 24px;">
            Navigate Alexandria's public transit with AI assistance.<br>
            تنقل في مواصلات الإسكندرية بسهولة باستخدام الذكاء الاصطناعي
        </p>
        <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
            <span class="eo-pill">🤖 AI Trip Planner</span>
            <span class="eo-pill">🚌 Route Testing</span>
            <span class="eo-pill">📍 Geocoding</span>
        </div>
        <br>
        <p class="eo-muted" style="font-size: 0.9rem;">
            👈 Choose a tool from the sidebar to get started<br>
            اختر أداة من القائمة الجانبية للبدء
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="text-align: center; padding: 32px 0; font-size: 0.8rem;" class="eo-muted">
        El Osta • v1.0.0
    </div>
""", unsafe_allow_html=True)
