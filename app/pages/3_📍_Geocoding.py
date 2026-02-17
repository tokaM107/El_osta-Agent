import streamlit as st
import sys
import os

_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(_APP_DIR)
for p in (_REPO_ROOT, _APP_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

st.set_page_config(page_title="Geocoding", page_icon="📍", layout="centered")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def toggle():
    st.session_state.dark_mode = not st.session_state.dark_mode

with st.sidebar:
    st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, on_change=toggle)

from ui.theme import inject_theme, render_header
from services.geocoding_serv import geocode_address

inject_theme(st.session_state.dark_mode)
render_header()

st.markdown("""
    <div class="eo-card eo-card-purple">
        <div class="section-header">
            <span class="section-icon" style="font-size:1.5rem; margin-right:10px;">📍</span>
            <div>
                <h3 class="section-title" style="margin:0;">Geocoding Test</h3>
                <div class="eo-muted">Address to Coordinates</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

with st.form("geo"):
    f_txt = st.text_input("From", "محطة مصر")
    t_txt = st.text_input("To", "سيدي بشر")
    
    if st.form_submit_button("🔍 Lookup", use_container_width=True):
        try:
            r1 = geocode_address(f_txt)
            r2 = geocode_address(t_txt)
            st.success("Done")
            c1, c2 = st.columns(2)
            c1.json(r1)
            c2.json(r2)
        except Exception as e:
            st.error(str(e))