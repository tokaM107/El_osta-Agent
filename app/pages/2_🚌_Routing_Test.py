import streamlit as st
import sys
import os

# Path setup
_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.dirname(_APP_DIR)
for p in (_REPO_ROOT, _APP_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

st.set_page_config(
    page_title="Routing Test • El Osta",
    page_icon="🚌",
    layout="centered"
)

# Theme Init
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

with st.sidebar:
    st.markdown('<span class="eo-pill">🎨 Theme</span>', unsafe_allow_html=True)
    st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, on_change=toggle_theme)

from ui.theme import inject_theme, render_header
from services.routing_client import find_route

inject_theme(st.session_state.dark_mode)
render_header()

st.markdown("""
    <div class="eo-card eo-card-green">
        <div class="section-header">
            <span class="section-icon" style="font-size:1.5rem; margin-right:10px;">🚌</span>
            <div>
                <h3 class="section-title" style="margin:0;">Direct API Test</h3>
                <div class="eo-muted">Test routing server with coordinates</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

with st.form("raw_server_form"):
    st.markdown("**📍 Locations**")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Start Lat/Lon")
        slat = st.number_input("Lat", 31.229688, format="%.6f", key="s_lat")
        slon = st.number_input("Lon", 29.961393, format="%.6f", key="s_lon")
    with c2:
        st.caption("End Lat/Lon")
        elat = st.number_input("Lat", 31.207759, format="%.6f", key="e_lat")
        elon = st.number_input("Lon", 29.941941, format="%.6f", key="e_lon")
    
    st.markdown("---")
    st.markdown("**⚙️ Configuration**")
    
    col_w, col_t = st.columns(2)
    with col_w:
        w_cut = st.number_input("Walk Cutoff (m)", 1000, step=100)
    with col_t:
        max_t = st.number_input("Max Transfers", 2)

    st.caption("Weights (Time / Cost / Walk / Transfer)")
    wc1, wc2, wc3, wc4 = st.columns(4)
    w_time = wc1.number_input("T", 0.5, step=0.1)
    w_cost = wc2.number_input("C", 0.3, step=0.1)
    w_walk = wc3.number_input("W", 0.1, step=0.1)
    w_tran = wc4.number_input("Tr", 0.1, step=0.1)
    
    st.markdown("")
    if st.form_submit_button("🔍 Test Server", use_container_width=True):
        with st.spinner(" querying..."):
            try:
                res = find_route(
                    slat, slon, elat, elon,
                    int(max_t), float(w_cut), [],
                    {"time":w_time, "cost":w_cost, "walk":w_walk, "transfer":w_tran}
                )
                cnt = len(res.get('journeys', []))
                st.success(f"✅ Found {cnt} routes")
                st.json(res)
            except Exception as e:
                st.error(f"Error: {e}")